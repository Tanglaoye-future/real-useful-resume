"""
ShixisengAdapter — 实习僧 (shixiseng.com) RpcSiteAdapter for RpcCrawler.

Architecture
------------
shixiseng.com runs a JS anti-bot stack (font-glyph swap + behaviour fingerprint)
that plain `requests` cannot handle.  All page fetches therefore go through a
local Playwright RPC server (crawlers/rpc/server.py) via ShixisengClient,
which reuses the server's generic `/invoke/{platform}/fetch_detail` endpoint
for both list and detail pages.

The adapter slots into RpcCrawler (Disciplines 1, 4, 5) and implements
Discipline 2 (list+detail layering) via RPC.  Discipline 3 (font decode)
is applied here in `clean_text(..., self.font_map)`.

Prerequisites
-------------
1. RPC server running:
       python -m crawlers.rpc.server
2. Font map at logs/shixiseng_font_map.json (rotates ~daily).
   Without it salaries / digits will render as □ — re-extract with:
       python scrape-with-discipline/reference/extract_font_map.py
   then copy font_extract/font_map.json → logs/shixiseng_font_map.json.

Usage
-----
    from crawlers.adapters.shixiseng import ShixisengAdapter, load_font_map, KEYWORDS
    from crawlers.base.rpc_crawler import RpcCrawler

    adapter = ShixisengAdapter(font_map=load_font_map())
    crawler = RpcCrawler(
        adapter=adapter,
        raw_path="data/raw/shixiseng/shixiseng_20260430.jsonl",
        checkpoint_path="logs/shixiseng_ckpt.json",
    )
    rows = crawler.run(keywords=KEYWORDS)
"""
from __future__ import annotations

import datetime
import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from crawlers.base.rpc_crawler import RpcSiteAdapter
from crawlers.base.template_crawler import clean_text
from crawlers.rpc.shixiseng_client import ShixisengClient

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Default keyword list — broad sweep first, then targeted categories
# ---------------------------------------------------------------------------

KEYWORDS: list[str] = [
    "",  # broad — all Shanghai internships
    "数据分析", "数据", "算法",
    "产品", "运营", "市场", "增长",
    "金融", "咨询", "战略",
    "前端", "后端",
]


# ---------------------------------------------------------------------------
# Font map loader
# ---------------------------------------------------------------------------

def load_font_map(path: str = "logs/shixiseng_font_map.json") -> dict:
    """Load the shixiseng glyph→char map.  Returns {} if file absent."""
    if not os.path.exists(path):
        logger.warning(
            "Font map not found at %s. Salaries/digits may be garbled. "
            "Run scrape-with-discipline/reference/extract_font_map.py "
            "and copy font_extract/font_map.json → %s.",
            path, path,
        )
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        filled = {k: v for k, v in raw.items() if v}
        empty = len(raw) - len(filled)
        logger.info("Font map loaded: %d filled, %d empty slots from %s",
                    len(filled), empty, path)
        if empty:
            logger.warning(
                "%d font-map slots still empty — those glyphs will render as □", empty,
            )
        return filled
    except Exception as e:
        logger.error("Failed to load font map from %s: %s", path, e)
        return {}


# ---------------------------------------------------------------------------
# URL helpers
# ---------------------------------------------------------------------------

_INTERN_ID_RE = re.compile(r"/intern/(inn_[A-Za-z0-9]+)")


def _extract_job_id(url: str) -> str:
    """Extract `inn_xxx` from a shixiseng intern URL."""
    if not url:
        return ""
    m = _INTERN_ID_RE.search(url)
    return m.group(1) if m else ""


# ---------------------------------------------------------------------------
# ShixisengAdapter
# ---------------------------------------------------------------------------

@dataclass
class ShixisengAdapter(RpcSiteAdapter):
    """RpcSiteAdapter for shixiseng.com.

    `parse_list_card` / `parse_detail` / `filter_row` keep the legacy
    field names (job_title, salary_range, responsibilities, publish_time)
    so the existing test fixtures remain valid; `fetch_page` and
    `fetch_detail` map those into the rpc_crawler.SCHEMA shape
    (job_name, salary, job_description, publish_date, …).
    """

    name: str = "shixiseng"
    base_url: str = "https://www.shixiseng.com/interns"
    city: str = "上海"
    keyword: str = ""  # optional fallback when RpcCrawler passes ""
    require_undergrad: bool = True

    list_selector: str = ".intern-wrap"
    detail_link_selector: str = "a.intern-detail__title"

    font_map: dict = field(default_factory=dict)
    rpc_url: str = field(
        default_factory=lambda: os.getenv("SHIXISENG_RPC_URL", "http://127.0.0.1:5600")
    )
    rate_limit_seconds: tuple = field(
        default_factory=lambda: (
            float(os.getenv("SHIXISENG_THROTTLE_MIN", "5")),
            float(os.getenv("SHIXISENG_THROTTLE_MAX", "8")),
        )
    )
    fetch_detail_enabled: bool = True

    _client: ShixisengClient = field(init=False, repr=False, default=None)

    def __post_init__(self):
        self._client = ShixisengClient(rpc_url=self.rpc_url)

    # ------------------------------------------------------------------
    # Discipline 2 — list page
    # ------------------------------------------------------------------

    def parse_list_card(self, card) -> dict:
        """Extract fields from a single list-page job card.

        Return shape (legacy keys preserved for tests):
            {company_name, job_title, salary_range, location, url}
        """
        company = ""
        cdiv = card.select_one(".intern-detail__company")
        if cdiv:
            link = cdiv.select_one("a[title]")
            company = link.get("title", "") if link else cdiv.get_text(strip=True)

        name_el = card.select_one(".intern-detail__job, .job_name, .name, .title")
        salary_el = card.select_one(".day_money, .day, .job_money")
        loc_el = card.select_one(".city, .job_city")
        link_el = (
            card.select_one(self.detail_link_selector)
            or card.select_one("a.job_name, a.name, a.title")
        )

        url = ""
        if link_el and link_el.get("href"):
            href = link_el["href"]
            url = href if href.startswith("http") else f"https://www.shixiseng.com{href}"

        return {
            "company_name": clean_text(company, self.font_map),
            "job_title":    clean_text(name_el.get_text() if name_el else "", self.font_map),
            "salary_range": clean_text(salary_el.get_text() if salary_el else "", self.font_map),
            "location":     clean_text(loc_el.get_text() if loc_el else "", self.font_map),
            "url":          url,
        }

    # ------------------------------------------------------------------
    # Discipline 2 — detail page
    # ------------------------------------------------------------------

    def parse_detail(self, soup: BeautifulSoup) -> dict:
        """Extract detail-page fields.  Legacy keys preserved for tests."""
        out: dict = {}

        addr = soup.select_one(".job_address, .address, .com_position")
        if addr:
            out["location"] = clean_text(addr.get_text(), self.font_map)

        detail = soup.select_one(".job_detail, .job-detail, .detail")
        if detail:
            content = detail.get_text("\n")
            for marker in ("任职要求", "职位要求"):
                if marker in content:
                    parts = content.split(marker, 1)
                    out["responsibilities"] = clean_text(
                        parts[0].replace("岗位职责", ""), self.font_map
                    )
                    out["requirements"] = clean_text(parts[1], self.font_map)
                    break
            else:
                out["responsibilities"] = clean_text(content, self.font_map)

        welfare_els = soup.select(".job_welfare .welfare_item")
        if welfare_els:
            out["benefits"] = " ".join(
                clean_text(w.get_text(strip=True), self.font_map) for w in welfare_els
            )

        pub_el = soup.select_one(
            ".job-header__time, .job_date .cutom_font, .job_update_time, .time, .pub_time"
        )
        if pub_el:
            pub_text = clean_text(pub_el.get_text(), self.font_map)
            m = re.search(r"(20\d{2}-\d{1,2}-\d{1,2})", pub_text)
            if m:
                out["publish_time"] = m.group(1)
            elif "天前" in pub_text:
                match = re.search(r"(\d+)天前", pub_text)
                if match:
                    days = int(match.group(1))
                    out["publish_time"] = (
                        datetime.date.today() - datetime.timedelta(days=days)
                    ).isoformat()
            elif "小时前" in pub_text or "分钟前" in pub_text:
                out["publish_time"] = datetime.date.today().isoformat()

        body_text = soup.get_text()
        dm = re.search(r"截止日期[：:]\s*(20\d{2}-\d{1,2}-\d{1,2})", body_text)
        if dm:
            out["deadline"] = dm.group(1)

        return out

    # ------------------------------------------------------------------
    # Schema mappers — legacy keys → rpc_crawler.SCHEMA keys
    # ------------------------------------------------------------------

    def _list_card_to_rpc(self, card_dict: dict, keyword: str) -> Optional[dict]:
        url = card_dict.get("url", "")
        job_id = _extract_job_id(url)
        if not job_id and not url:
            return None
        return {
            "source_job_id":  job_id or url,
            "job_name":       card_dict.get("job_title", ""),
            "company_name":   card_dict.get("company_name", ""),
            "location":       card_dict.get("location", ""),
            "salary":         card_dict.get("salary_range", ""),
            "url":            url,
            "source_keyword": keyword,
        }

    @staticmethod
    def _detail_to_rpc(detail_dict: dict) -> dict:
        out: dict = {}
        # Combine responsibilities + requirements into job_description for matcher.
        resp = detail_dict.get("responsibilities", "")
        req  = detail_dict.get("requirements", "")
        if resp or req:
            parts = []
            if resp:
                parts.append(resp)
            if req:
                parts.append("任职要求\n" + req)
            out["job_description"] = "\n\n".join(parts)
            if req:
                out["job_requirement"] = req
        if detail_dict.get("location"):
            out["location"] = detail_dict["location"]
        if detail_dict.get("benefits"):
            out["job_tags"] = detail_dict["benefits"]
        if detail_dict.get("publish_time"):
            out["publish_date"] = detail_dict["publish_time"]
        return out

    # ------------------------------------------------------------------
    # RpcSiteAdapter overrides
    # ------------------------------------------------------------------

    def fetch_page(self, keyword: str, page_num: int) -> tuple[list[dict], bool]:
        """Fetch one search-results page via RPC. Returns (jobs, has_next)."""
        # If caller passes empty keyword and adapter has a default, use the default.
        kw = keyword if keyword is not None else ""
        if not kw and self.keyword:
            kw = self.keyword

        result = self._client.fetch_list_html(
            page_num=page_num, city=self.city, keyword=kw,
        )

        if result.get("blocked"):
            logger.warning("[Shixiseng] blocked: %s", result.get("title", ""))
            return [], False

        if result.get("error"):
            logger.error("[Shixiseng] fetch error: %s", result.get("error"))
            return [], True  # transient — let crawler retry next page

        html = result.get("html", "") or ""
        if not html:
            return [], False

        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(self.list_selector)
        logger.info(
            "[Shixiseng] page=%d keyword=%r: %d card(s) matched %r",
            page_num, kw, len(cards), self.list_selector,
        )

        jobs: list[dict] = []
        for card in cards:
            try:
                card_dict = self.parse_list_card(card)
            except Exception as e:
                logger.warning("[Shixiseng] parse_list_card failed: %s", e)
                continue
            mapped = self._list_card_to_rpc(card_dict, kw)
            if mapped:
                jobs.append(mapped)

        # Heuristic: if list page returned a normal-sized batch we assume
        # there is a next page; an underfilled page is taken as the tail.
        has_next = len(cards) >= 10
        return jobs, has_next

    def fetch_detail(self, job: dict) -> dict:
        """Enrich job with detail-page fields.  Returns rpc-schema keys."""
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
            logger.warning("[Shixiseng] parse_detail failed for %s: %s", url, e)
            return {}
        return self._detail_to_rpc(detail_dict)

    # ------------------------------------------------------------------
    # Filter (Discipline 5 part 2)
    # ------------------------------------------------------------------

    def filter_row(self, row: dict) -> bool:
        """Keep Shanghai internships; drop graduate-only roles if configured."""
        loc = str(row.get("location", ""))
        if self.city and self.city not in loc:
            return False
        if self.require_undergrad:
            req = str(row.get("requirements", "")) or str(row.get("job_requirement", ""))
            if any(b in req for b in ("仅硕士", "仅博士", "仅研究生")):
                return False
        return True
