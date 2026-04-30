"""
LiepinAdapter — RpcSiteAdapter subclass for liepin.com (猎聘).

Architecture
------------
Liepin uses heavy anti-bot JS (encrypted tokens, TLS fingerprinting), so all
network requests go through a local Playwright RPC server instead of plain
requests.  This adapter slots into RpcCrawler (Disciplines 1, 4, 5) while
implementing Discipline 2 (list+detail layering) via RPC.

Prerequisites
-------------
1. RPC server running:
       python -m crawlers.rpc.server
   (or: python crawlers/rpc/server.py)
2. Playwright browser launched by the server (headless=False for anti-bot).

Checkpoint behaviour (Discipline 4)
-------------------------------------
After every keyword completes, RpcCrawler writes:
    logs/liepin_ckpt.json  →  {"keyword_idx": N, "seen_ids": [...]}

If the process is killed mid-crawl, restart with the same RpcCrawler instance
and it will resume from keyword N, skipping already-seen job IDs.

Usage
-----
    from crawlers.adapters.liepin import LiepinAdapter, KEYWORDS
    from crawlers.base.rpc_crawler import RpcCrawler
    import datetime

    adapter = LiepinAdapter()
    date_tag = datetime.date.today().strftime("%Y%m%d")
    crawler = RpcCrawler(
        adapter=adapter,
        raw_path=f"data/raw/liepin/liepin_{date_tag}.jsonl",
        checkpoint_path="logs/liepin_ckpt.json",
    )
    rows = crawler.run(keywords=KEYWORDS)
"""
from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from typing import Optional

from bs4 import BeautifulSoup

from crawlers.base.rpc_crawler import RpcSiteAdapter
from crawlers.rpc.liepin_client import LiepinCrypto

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default keyword list — covers major Shanghai internship categories
# ---------------------------------------------------------------------------

KEYWORDS: list[str] = [
    # Empty string → broad "all Shanghai internships" pool (largest; run first)
    "",
    "实习",
    # Product / operations
    "产品", "运营", "市场", "增长", "商业分析",
    # Data / engineering
    "数据分析", "数据", "算法", "前端", "后端", "测试",
    # Business / strategy
    "战略", "咨询", "BI", "财务", "人事", "供应链",
    # Industry-specific
    "金融", "医药", "医疗", "化工", "汽车", "机械",
    "半导体", "新能源", "快消", "零售",
    # Premium / international
    "外企", "500强",
]

# Big-tech company names — used for soft deprioritisation, not hard filter
_BIG_TECH = {
    "字节跳动", "tiktok", "bytedance",
    "阿里巴巴", "阿里", "淘宝", "天猫", "支付宝", "钉钉", "alibaba",
    "腾讯", "微信", "tencent",
    "百度", "baidu",
    "美团", "meituan",
    "京东", "jd.com",
    "快手", "kuaishou",
    "小红书", "rednote",
    "滴滴", "didi",
    "网易", "netease",
}

# Liepin boilerplate footer regex — stripped from JD text
_BOILERPLATE_RE = re.compile(
    r"(职位福利|工作地址|关于猎聘|猎聘网|版权所有|©|Copyright|\bwww\.liepin\.com\b"
    r"|如有疑问|请联系|加入我们|更多职位|关注公众号|下载猎聘|猎聘官方|使用猎聘APP"
    r"|手机号|联系电话|下载App|猎聘-中高端职业发展平台|猎聘App|分享职位|发送给朋友"
    r"|举报职位|我要投递|立即申请|在线申请|投递简历|收藏职位|在线沟通|猎聘|招聘职位)",
    re.IGNORECASE,
)


def _clean_jd(html_or_text: str) -> str:
    """Extract JD text from raw HTML or plain text, strip boilerplate."""
    if not html_or_text:
        return ""
    # If it looks like HTML, parse it
    if "<" in html_or_text and ">" in html_or_text:
        soup = BeautifulSoup(html_or_text, "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        for sel in (
            "[class*='job-detail']", "[class*='jobdetail']",
            "[class*='job_description']", "[class*='description']",
            "[class*='content']", "[id*='job-detail']",
            "[id*='description']", "main", "article",
        ):
            blocks = soup.select(sel)
            for block in blocks:
                text = block.get_text("\n", strip=True)
                if len(text) >= 40:
                    html_or_text = text
                    break
            else:
                continue
            break
        else:
            html_or_text = soup.get_text("\n", strip=True)

    lines = []
    for line in html_or_text.replace("\r", "\n").split("\n"):
        stripped = " ".join(line.split())
        if stripped and not _BOILERPLATE_RE.search(stripped):
            lines.append(stripped)
    return "\n".join(lines)


def _parse_job_card(item: dict, keyword: str) -> Optional[dict]:
    """Extract a SCHEMA-compatible dict from a single API card (any shape)."""
    try:
        # Nested card shape: {job: {...}, comp: {...}}
        job_card = item.get("job") if isinstance(item, dict) else None
        comp_card = item.get("comp") if isinstance(item, dict) else None
        if isinstance(job_card, dict):
            job_id = job_card.get("jobId", "") or ""
            if not job_id:
                return None
            company = (comp_card or {}).get("compName", "") if isinstance(comp_card, dict) else ""
            link = job_card.get("link", "") or f"https://www.liepin.com/job/{job_id}.shtml"
            return {
                "source_job_id":          job_id,
                "job_name":               job_card.get("title") or job_card.get("jobName", ""),
                "company_name":           company,
                "location":               job_card.get("dq") or job_card.get("city", ""),
                "salary":                 job_card.get("salary") or job_card.get("salaryDesc", ""),
                "company_industry":       (comp_card or {}).get("compIndustry", ""),
                "company_size":           (comp_card or {}).get("compScale", ""),
                "url":                    link,
                "publish_date":           job_card.get("refreshTime", ""),
                "source_keyword":         keyword,
            }

        # Flat shape: {jobId, jobName, compName, ...}
        job_id = item.get("jobId", "")
        if not job_id:
            return None
        tags = (
            item.get("skillTagList") or item.get("labels") or item.get("welfareTagList") or []
        )
        return {
            "source_job_id":          job_id,
            "job_name":               item.get("jobName", ""),
            "company_name":           item.get("compName", ""),
            "location":               item.get("dq") or item.get("city", ""),
            "salary":                 item.get("salary") or item.get("salaryDesc", ""),
            "experience_requirement": item.get("requireWorkYears", ""),
            "education_requirement":  item.get("requireEduLevel", ""),
            "company_industry":       item.get("industryName", ""),
            "company_size":           item.get("compScale") or item.get("compScaleName", ""),
            "job_tags":               "|".join(str(t) for t in tags if t),
            "job_description":        item.get("jobDesc", ""),
            "url":                    f"https://www.liepin.com/job/{job_id}.shtml",
            "publish_date":           item.get("publishTime") or item.get("refreshTime", ""),
            "source_keyword":         keyword,
        }
    except Exception as e:
        logger.warning("_parse_job_card error: %s | item=%s", e, str(item)[:200])
        return None


# ---------------------------------------------------------------------------
# LiepinAdapter
# ---------------------------------------------------------------------------

@dataclass
class LiepinAdapter(RpcSiteAdapter):
    """RpcSiteAdapter for liepin.com.

    All network IO goes through LiepinCrypto → RPC server → Playwright.
    """

    name: str = "liepin"
    city_code: str = field(default_factory=lambda: os.getenv("LIEPIN_CITY", "020"))
    page_size: int = field(default_factory=lambda: int(os.getenv("LIEPIN_PAGE_SIZE", "20")))
    max_retry: int = field(default_factory=lambda: int(os.getenv("LIEPIN_MAX_RETRY", "3")))
    rpc_url: str = field(
        default_factory=lambda: os.getenv("LIEPIN_RPC_URL", "http://127.0.0.1:5600")
    )
    rate_limit_seconds: tuple = field(
        default_factory=lambda: (
            float(os.getenv("LIEPIN_THROTTLE_MIN", "5")),
            float(os.getenv("LIEPIN_THROTTLE_MAX", "10")),
        )
    )

    # Internal RPC client — initialised in __post_init__
    _client: LiepinCrypto = field(init=False, repr=False, default=None)

    def __post_init__(self):
        self._client = LiepinCrypto(rpc_url=self.rpc_url)

    # ---- Discipline 2: list page --------------------------------------------

    def fetch_page(self, keyword: str, page_num: int) -> tuple[list[dict], bool]:
        """Fetch one search-results page.  Returns (jobs, has_next)."""
        import random, time

        for attempt in range(1, self.max_retry + 1):
            try:
                result = self._client.search_jobs(
                    keyword=keyword,
                    page_num=page_num,
                    city=self.city_code,
                    page_size=self.page_size,
                )
            except Exception as e:
                logger.error("[Liepin] search_jobs attempt %d failed: %s", attempt, e)
                time.sleep(random.uniform(*self.rate_limit_seconds))
                continue

            if not isinstance(result, dict):
                logger.warning("[Liepin] unexpected result type: %s", type(result))
                return [], True

            if result.get("blocked"):
                logger.warning("[Liepin] blocked: %s", result.get("message"))
                return [], True

            if result.get("error"):
                logger.error("[Liepin] RPC error: %s", result.get("error"))
                time.sleep(random.uniform(*self.rate_limit_seconds))
                continue

            # Parse pagination
            pagination = result.get("pagination") or {}
            has_next: bool = bool(pagination.get("hasNext", True))
            if pagination:
                logger.info(
                    "[Liepin] pagination: total=%s pages=%s hasNext=%s",
                    pagination.get("totalCounts"),
                    pagination.get("totalPage"),
                    has_next,
                )

            # Parse job cards
            data = result.get("data") or {}
            raw_list: list = (
                data.get("jobCardList") or data.get("jobList") or []
            )
            jobs: list[dict] = []
            for item in raw_list:
                parsed = _parse_job_card(item, keyword)
                if parsed:
                    jobs.append(parsed)

            logger.info(
                "[Liepin] page %d keyword=%r: %d jobs, has_next=%s",
                page_num, keyword, len(jobs), has_next,
            )
            return jobs, has_next

        logger.error("[Liepin] fetch_page exhausted retries for page %d", page_num)
        return [], True

    # ---- Discipline 2: detail page -----------------------------------------

    def fetch_detail(self, job: dict) -> dict:
        """Enrich job with full JD text from the detail page (best-effort)."""
        url = job.get("url", "")
        if not url:
            return {}
        try:
            result = self._client.fetch_detail_html(url)
        except Exception as e:
            logger.debug("[Liepin] fetch_detail failed for %s: %s", url, e)
            return {}

        if not isinstance(result, dict) or result.get("blocked"):
            return {}
        html = result.get("html", "")
        if not html:
            return {}
        jd_text = _clean_jd(html)
        if not jd_text:
            return {}
        return {"job_description": jd_text, "address_source": "详情页"}

    # ---- Discipline 5 filter ------------------------------------------------

    def filter_row(self, row: dict) -> bool:
        """Keep Shanghai internships.  Big-tech jobs are kept but flagged."""
        loc = str(row.get("location", "")).lower()
        if "上海" not in loc and "shanghai" not in loc:
            city = str(row.get("city", "")).lower()
            if "上海" not in city and "shanghai" not in city:
                return False
        # Soft deprioritisation: tag big-tech rather than drop
        company = str(row.get("company_name", "")).lower()
        is_big_tech = any(bt.lower() in company for bt in _BIG_TECH)
        if is_big_tech and "big_tech" not in str(row.get("job_tags", "")):
            existing = row.get("job_tags", "")
            row["job_tags"] = (existing + "|big_tech").lstrip("|") if existing else "big_tech"
        return True
