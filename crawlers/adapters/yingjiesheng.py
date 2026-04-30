"""
YingjieshengAdapter — 应届生 (yingjiesheng.com) RpcSiteAdapter for RpcCrawler.

Architecture
------------
yingjiesheng.com Shanghai listings live at /shanghai/ (page 1) and
/shanghai-morejob-N.html (page 2+). Pages are JS-rendered enough that
plain `requests` is unreliable, so all fetches go through the local
Playwright RPC server (crawlers/rpc/server.py). The server's
`fetch_detail_html` lazily creates a Playwright page for "yingjiesheng"
on first call — no init script or cookie setup needed.

The site is location-based, not keyword-based: each list page exposes
all Shanghai openings. Keyword arg from RpcCrawler is recorded only as
`source_keyword` for tagging.

The list page yields very thin records (job_name, jd_url) — the bulk of
useful data lives in the detail page, which has a structured prefix
(招聘单位/学历要求/工作地点/薪资待遇/发布日期/...) plus content sections
(岗位职责/任职要求/福利待遇).

Prerequisites
-------------
RPC server running:  python -m crawlers.rpc.server

Usage
-----
    from crawlers.adapters.yingjiesheng import YingjieshengAdapter, KEYWORDS
    from crawlers.base.rpc_crawler import RpcCrawler

    crawler = RpcCrawler(
        adapter=YingjieshengAdapter(),
        raw_path="data/raw/yingjiesheng/yingjiesheng_20260430.jsonl",
        checkpoint_path="logs/yingjiesheng_ckpt.json",
        max_pages_per_keyword=15,
    )
    crawler.run(keywords=KEYWORDS)
"""
from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from typing import Optional

from bs4 import BeautifulSoup

from crawlers.base.rpc_crawler import RpcSiteAdapter
from crawlers.rpc.yingjiesheng_client import YingjieshengClient

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Keyword list — yingjiesheng is location-driven, so keywords are tag-only.
# ---------------------------------------------------------------------------

KEYWORDS: list[str] = ["应届生"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_JOB_LINK_RE = re.compile(r"/job-[\w\-]+\.html")
_JOB_ID_RE = re.compile(r"/(job-[\w\-]+)\.html")

# Boilerplate markers we never want in JD output
_BOILERPLATE_MARKERS = (
    "联系方式", "联系电话", "公司地址", "招聘专员", "应聘电话",
    "更多职位", "举报职位", "应届生求职网", "yingjiesheng",
)

# Structured prefix markers in detail JD text
_PREFIX_FIELDS = {
    "招聘单位": "company_name",
    "职位类别": "job_category",
    "学历要求": "education_requirement",
    "工作地点": "location",
    "薪资待遇": "salary",
    "发布日期": "publish_date",
    "专业要求": "majors",
    "工作经验": "experience_requirement",
    "工作年限": "experience_requirement",
}


def _absolutize(href: str) -> str:
    """Turn a relative yingjiesheng href into an absolute URL."""
    if not href:
        return ""
    if href.startswith("http"):
        return href
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        return "https://www.yingjiesheng.com" + href
    return "https://www.yingjiesheng.com/" + href.lstrip("./")


def _extract_job_id(url: str) -> str:
    """Pull `job-007-958-717` out of a yingjiesheng detail URL."""
    if not url:
        return ""
    m = _JOB_ID_RE.search(url)
    return m.group(1) if m else ""


def _guess_company_from_title(text: str) -> str:
    """Many yingjiesheng anchor texts are `[上海]公司名` — peel the prefix."""
    t = (text or "").strip()
    if not t:
        return ""
    if t.startswith("[") and "]" in t:
        return t.split("]", 1)[1].strip()
    return ""


def _strip_boilerplate(text: str) -> str:
    """Drop tail boilerplate sections (contact info etc.)."""
    if not text:
        return ""
    out_lines: list[str] = []
    skip_until_blank = False
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            skip_until_blank = False
            out_lines.append("")
            continue
        if any(m in stripped for m in _BOILERPLATE_MARKERS):
            skip_until_blank = True
            continue
        if skip_until_blank:
            continue
        out_lines.append(stripped)
    return "\n".join(out_lines).strip()


def _extract_jd_text(soup: BeautifulSoup) -> str:
    """Pull the largest JD-shaped text block from the detail page.

    Mirrors the strategy used in core.crawler_engine.base_spider:
    walk a list of likely selectors, return the first ≥40-char block.
    """
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    for selector in (
        "[class*='job-detail']", "[class*='jobdetail']",
        "[class*='job_description']", "[class*='description']",
        "[class*='content']", "[id*='job-detail']",
        "[id*='description']", "[id*='detail']",
        "main", "article",
    ):
        for block in soup.select(selector):
            text = block.get_text("\n", strip=True)
            if len(text) >= 40:
                return text
    return soup.get_text("\n", strip=True)


def _parse_prefix(jd_text: str) -> dict:
    """Extract structured `key：value` pairs from the JD prefix lines."""
    out: dict = {}
    for line in jd_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Accept both fullwidth ：and halfwidth :
        m = re.match(r"^([一-龥]{2,6})[：:]\s*(.+?)\s*$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if key in _PREFIX_FIELDS and value:
            out[_PREFIX_FIELDS[key]] = value
    return out


def _split_sections(jd_text: str) -> dict:
    """Split JD body into responsibilities / requirements / benefits.

    Matches the section headers `岗位职责`, `任职要求`, `福利待遇`
    (with common synonyms) when they appear on their own line.
    """
    if not jd_text:
        return {}
    desc_markers = ("岗位职责", "工作职责", "职位描述", "工作内容", "职责描述")
    req_markers = ("任职要求", "岗位要求", "职位要求", "任职资格", "招聘要求")
    perk_markers = ("福利待遇", "薪资福利", "公司福利", "我们提供")

    lines = jd_text.split("\n")
    section = None
    buckets: dict[str, list[str]] = {"desc": [], "req": [], "perk": []}
    for raw in lines:
        line = raw.strip()
        if any(line.startswith(m) for m in desc_markers):
            section = "desc"
            continue
        if any(line.startswith(m) for m in req_markers):
            section = "req"
            continue
        if any(line.startswith(m) for m in perk_markers):
            section = "perk"
            continue
        if section and line:
            buckets[section].append(line)

    out: dict = {}
    if buckets["desc"]:
        out["job_description"] = "\n".join(buckets["desc"]).strip()
    if buckets["req"]:
        out["job_requirement"] = "\n".join(buckets["req"]).strip()
    if buckets["perk"]:
        out["benefits"] = "\n".join(buckets["perk"]).strip()
    return out


# ---------------------------------------------------------------------------
# YingjieshengAdapter
# ---------------------------------------------------------------------------

@dataclass
class YingjieshengAdapter(RpcSiteAdapter):
    """RpcSiteAdapter for yingjiesheng.com (Shanghai)."""

    name: str = "yingjiesheng"
    city: str = "上海"
    rpc_url: str = field(
        default_factory=lambda: os.getenv("YINGJIESHENG_RPC_URL", "http://127.0.0.1:5600")
    )
    rate_limit_seconds: tuple = field(
        default_factory=lambda: (
            float(os.getenv("YINGJIESHENG_THROTTLE_MIN", "3")),
            float(os.getenv("YINGJIESHENG_THROTTLE_MAX", "6")),
        )
    )
    fetch_detail_enabled: bool = True

    _client: YingjieshengClient = field(init=False, repr=False, default=None)

    def __post_init__(self):
        self._client = YingjieshengClient(rpc_url=self.rpc_url)

    # ------------------------------------------------------------------
    # Discipline 2 — list page
    # ------------------------------------------------------------------

    def parse_list_card(self, anchor) -> Optional[dict]:
        """Extract list-card fields from a single `<a>` element.

        Return shape:
            {job_name, company_name, url, source_job_id, location}
        Returns None if the anchor isn't a job link.
        """
        href = (anchor.get("href") or "").strip()
        if not href or not _JOB_LINK_RE.search(href):
            return None
        url = _absolutize(href)
        text = (anchor.get_text() or "").strip()
        job_name = text if len(text) >= 2 else "应届生岗位"
        return {
            "job_name":      job_name,
            "company_name":  _guess_company_from_title(text),
            "url":           url,
            "source_job_id": _extract_job_id(url),
            "location":      "上海",
        }

    # ------------------------------------------------------------------
    # Discipline 2 — detail page
    # ------------------------------------------------------------------

    def parse_detail(self, soup: BeautifulSoup) -> dict:
        """Extract structured detail-page fields.

        Return keys (a subset of):
            job_name, company_name, education_requirement, location,
            salary, publish_date, experience_requirement, job_category,
            majors, job_description, job_requirement, benefits, jd_content
        """
        out: dict = {}

        # Title — prefer <h1>, fall back to first non-marker line of JD body
        h1 = soup.select_one("h1")
        if h1:
            title = (h1.get_text() or "").strip()
            if title and len(title) >= 2:
                out["job_name"] = title

        jd_raw = _extract_jd_text(soup)
        if not jd_raw:
            return out

        out.update(_parse_prefix(jd_raw))
        out.update(_split_sections(jd_raw))

        # Title fallback: first non-empty, non-marker line
        if "job_name" not in out:
            for line in jd_raw.split("\n"):
                line = line.strip()
                if not line or "：" in line[:6] or ":" in line[:6]:
                    continue
                if any(line.startswith(m) for m in ("岗位职责", "任职要求", "福利待遇")):
                    break
                out["job_name"] = line
                break

        out["jd_content"] = _strip_boilerplate(jd_raw)
        return out

    # ------------------------------------------------------------------
    # Schema mappers — adapter dict → rpc_crawler.SCHEMA
    # ------------------------------------------------------------------

    @staticmethod
    def _list_card_to_rpc(card_dict: dict, keyword: str) -> Optional[dict]:
        url = card_dict.get("url", "")
        job_id = card_dict.get("source_job_id") or _extract_job_id(url)
        if not job_id and not url:
            return None
        return {
            "source_job_id":   job_id or url,
            "job_name":        card_dict.get("job_name", ""),
            "company_name":    card_dict.get("company_name", ""),
            "location":        card_dict.get("location", "上海"),
            "city":            "上海",
            "url":             url,
            "source_keyword":  keyword or "应届生",
        }

    @staticmethod
    def _detail_to_rpc(detail_dict: dict) -> dict:
        out: dict = {}
        # Direct rpc-schema fields
        for src, dst in (
            ("job_name", "job_name"),
            ("company_name", "company_name"),
            ("location", "location"),
            ("salary", "salary"),
            ("publish_date", "publish_date"),
            ("education_requirement", "education_requirement"),
            ("experience_requirement", "experience_requirement"),
            ("job_category", "company_industry"),  # closest match
        ):
            v = detail_dict.get(src)
            if v:
                out[dst] = v

        # Job description: prefer the structured slice; fall back to full content.
        if detail_dict.get("job_description"):
            out["job_description"] = detail_dict["job_description"]
        elif detail_dict.get("jd_content"):
            out["job_description"] = detail_dict["jd_content"]
        if detail_dict.get("job_requirement"):
            out["job_requirement"] = detail_dict["job_requirement"]

        # Benefits + majors → job_tags (rpc schema lacks dedicated fields)
        tag_parts = []
        if detail_dict.get("benefits"):
            tag_parts.append(detail_dict["benefits"][:200])
        if detail_dict.get("majors"):
            tag_parts.append(detail_dict["majors"][:200])
        if tag_parts:
            out["job_tags"] = " | ".join(tag_parts)
        return out

    # ------------------------------------------------------------------
    # RpcSiteAdapter overrides
    # ------------------------------------------------------------------

    def fetch_page(self, keyword: str, page_num: int) -> tuple[list[dict], bool]:
        """Fetch one Shanghai list page via RPC. Returns (jobs, has_next)."""
        result = self._client.fetch_list_html(page_num=page_num)

        if result.get("blocked"):
            logger.warning("[Yingjiesheng] blocked: %s", result.get("title", ""))
            return [], False
        if result.get("error"):
            logger.error("[Yingjiesheng] fetch error: %s", result.get("error"))
            return [], True
        html = result.get("html", "") or ""
        if not html:
            return [], False

        soup = BeautifulSoup(html, "html.parser")
        anchors = soup.select("a[href]")
        jobs: list[dict] = []
        seen_ids: set = set()
        for a in anchors:
            try:
                card = self.parse_list_card(a)
            except Exception as e:
                logger.warning("[Yingjiesheng] parse_list_card error: %s", e)
                continue
            if not card:
                continue
            if card["source_job_id"] in seen_ids:
                continue
            seen_ids.add(card["source_job_id"])
            mapped = self._list_card_to_rpc(card, keyword)
            if mapped:
                jobs.append(mapped)

        logger.info(
            "[Yingjiesheng] page=%d: %d unique job links extracted from %d anchors",
            page_num, len(jobs), len(anchors),
        )
        # Heuristic: a normal Shanghai list page has 30+ jobs; <5 means tail.
        has_next = len(jobs) >= 5
        return jobs, has_next

    def fetch_detail(self, job: dict) -> dict:
        if not self.fetch_detail_enabled:
            return {}
        url = job.get("url", "")
        if not url:
            return {}
        result = self._client.fetch_detail_html(url)
        if not isinstance(result, dict) or result.get("blocked"):
            return {}
        html = result.get("html", "") or ""
        if not html:
            return {}
        try:
            soup = BeautifulSoup(html, "html.parser")
            detail_dict = self.parse_detail(soup)
        except Exception as e:
            logger.warning("[Yingjiesheng] parse_detail failed for %s: %s", url, e)
            return {}
        return self._detail_to_rpc(detail_dict)

    # ------------------------------------------------------------------
    # Filter
    # ------------------------------------------------------------------

    def filter_row(self, row: dict) -> bool:
        """Defensive: keep Shanghai rows. Site URL already filters by city."""
        loc = str(row.get("location", "")) + " " + str(row.get("city", ""))
        return ("上海" in loc) or ("shanghai" in loc.lower())
