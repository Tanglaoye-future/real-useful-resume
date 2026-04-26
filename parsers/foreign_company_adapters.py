"""Foreign-company official-site adapters.

Phase 1: GenericInhouseAdapter only. Per-company adapters land in Phase 2.
Schema-compatible with outputs/raw/<co>_official_raw.csv (20 cols).
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import time
import unicodedata
from datetime import datetime
from typing import Any, Dict, List, Optional, Set


CITY_KEYWORDS = ("上海", "Shanghai", "shanghai", "SH")
# Word-boundary regex for English to avoid false matches ("International" → intern).
# Chinese tokens don't need boundaries.
INTERN_PATTERN = re.compile(
    r"(?i)\b(?:intern|internship|graduate|trainee|new\s+grad|management\s+trainee|"
    r"university\s+(?:hire|grad|graduate))\b|"
    r"实习|校招|校园招聘|应届|校园|暑期"
)
DETAIL_URL_PATTERNS = re.compile(
    r"(?i)(/jobs?/|/job/|/position/|/career/|/role/|/openings?/|/opportunit|"
    r"\?jobid=|\?positionid=|\?reqid=|\?id=\d|/p/|/req/|/posting/)"
)
TITLE_SELECTORS = [
    "h1",
    "h2.job-title",
    "[class*='job-title']",
    "[class*='JobTitle']",
    "[class*='position-title']",
    "[data-automation-id*='jobPostingHeader']",
    "h2",
]
BODY_SELECTORS = [
    "[data-automation-id='jobPostingDescription']",  # workday
    "main [class*='description']",
    "main [class*='Description']",
    "main article",
    "article",
    "main",
    "[role='main']",
]


def make_slug(company: str) -> str:
    folded = unicodedata.normalize("NFKD", company)
    folded = folded.encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^A-Za-z0-9]+", "_", folded.lower()).strip("_")
    return re.sub(r"_+", "_", s) or "unknown"


def md5_text(t: str) -> str:
    return hashlib.md5(t.encode("utf-8")).hexdigest()


def _norm_ws(text: Optional[str]) -> str:
    if not text:
        return ""
    return re.sub(r"[ \t\f\v]+", " ", text).strip()


def _contains_any(haystack: str, needles) -> bool:
    h = haystack or ""
    return any(n in h for n in needles)


def _looks_like_detail_url(url: str, allow_domains: List[str]) -> bool:
    if not url or not url.startswith("http"):
        return False
    if not any(d in url for d in allow_domains):
        return False
    return bool(DETAIL_URL_PATTERNS.search(url))


class BaseForeignAdapter:
    """Common behavior shared by Generic + per-company adapters."""

    def __init__(self, seed: Dict[str, Any]):
        self.seed = seed
        self.company: str = seed["company"]
        self.industry: str = seed.get("industry", "")
        self.priority: str = seed.get("priority", "P2")
        self.slug: str = make_slug(self.company)
        self.start_urls: List[str] = seed.get("start_urls", [])
        self.allow_domains: List[str] = seed.get("allow_domains", [])

    @property
    def source(self) -> str:
        return f"official_{self.slug}"

    def crawl(self, page, *, max_detail: int = 200) -> List[Dict[str, str]]:
        raise NotImplementedError

    def normalize(self, raw: Dict[str, Any]) -> Dict[str, str]:
        """Map a raw dict into the 20-column standard row."""
        url = _norm_ws(raw.get("url", ""))
        name = _norm_ws(raw.get("name", ""))
        city_raw = _norm_ws(raw.get("city", ""))
        city = "上海" if _contains_any(city_raw, CITY_KEYWORDS) else city_raw
        jd_raw = raw.get("jd_raw", "") or ""

        ext_id = _norm_ws(raw.get("external_job_id", ""))
        if not ext_id:
            ext_id = md5_text(f"{self.company}|{name}|{city}|{url}")

        publish_time = _norm_ws(raw.get("publish_time", "")) or "不知道发布时间"
        publish_time_source = "page" if raw.get("publish_time") else "unknown"
        deadline = _norm_ws(raw.get("deadline", "")) or "未知截止时间"
        deadline_source = "page" if raw.get("deadline") else "unknown"

        recruit_type = ""
        if _contains_any(name + jd_raw, ("实习", "intern", "Intern")):
            recruit_type = "实习"
        elif _contains_any(name + jd_raw, ("校招", "校园招聘", "graduate", "trainee", "应届")):
            recruit_type = "校招"

        return {
            "url": url,
            "company": self.company,
            "name": name,
            "city": city,
            "jd_raw": jd_raw,
            "salary": "",
            "company_size": "",
            "duration": "",
            "academic": "",
            "publish_time": publish_time,
            "deadline": deadline,
            "collect_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": self.source,
            "recruit_type": recruit_type,
            "raw_tags": _norm_ws(raw.get("raw_tags", "")),
            "external_job_id": ext_id,
            "update_time": _norm_ws(raw.get("update_time", "")),
            "publish_time_source": publish_time_source,
            "deadline_source": deadline_source,
            "sync_status": "",
        }

    @staticmethod
    def passes_filter(row: Dict[str, str]) -> bool:
        if not row.get("name") or not row.get("url"):
            return False
        if not _contains_any(row.get("city", ""), CITY_KEYWORDS):
            return False
        haystack = (row.get("name", "") or "") + " " + (row.get("jd_raw", "") or "")
        if not INTERN_PATTERN.search(haystack):
            return False
        if len(row.get("jd_raw", "")) < 50:
            return False
        return True


class GenericInhouseAdapter(BaseForeignAdapter):
    """One adapter for all `ats_type=inhouse` (and as fallback for others).

    Strategy:
      1. For each start_url: open in Playwright, scroll until no new detail
         links appear for two consecutive cycles, or until 50 cycles.
      2. Heuristically pick detail links by URL pattern + allow_domains.
      3. Visit each detail page, pull title/body/city heuristically.
      4. Normalize to 20-col schema; filter by city + recruit-type keywords.
    """

    SCROLL_STABLE_THRESHOLD = 2
    SCROLL_MAX_CYCLES = 50
    SCROLL_PAUSE_MS = 2500
    DETAIL_GOTO_TIMEOUT_MS = 30000
    LIST_GOTO_TIMEOUT_MS = 60000

    def crawl(self, page, *, max_detail: int = 200) -> List[Dict[str, str]]:
        seen_links: Set[str] = set()
        for url in self.start_urls:
            try:
                links = self._scroll_collect_links(page, url)
            except Exception as e:
                print(f"[{self.slug}] list-crawl failed for {url}: {e}")
                continue
            for ln in links:
                if ln not in seen_links and len(seen_links) < max_detail:
                    seen_links.add(ln)

        rows: List[Dict[str, str]] = []
        for i, link in enumerate(sorted(seen_links)):
            if i and i % 10 == 0:
                print(f"[{self.slug}] detail {i}/{len(seen_links)} kept={len(rows)}")
            try:
                raw = self._fetch_detail(page, link)
            except Exception as e:
                print(f"[{self.slug}] detail failed url={link}: {e}")
                continue
            if not raw:
                continue
            row = self.normalize(raw)
            if self.passes_filter(row):
                rows.append(row)
            time.sleep(random.uniform(1.0, 2.0))
        return rows

    def _scroll_collect_links(self, page, list_url: str) -> List[str]:
        try:
            page.goto(list_url, timeout=self.LIST_GOTO_TIMEOUT_MS, wait_until="domcontentloaded")
        except Exception as e:
            # Many SPAs never fire 'domcontentloaded' cleanly within the budget.
            # Give the page whatever it managed to render and continue.
            print(f"[{self.slug}] list-goto soft-fail (continuing): {e}")
        page.wait_for_timeout(3000)

        seen: Set[str] = set()
        stable = 0
        for cycle in range(self.SCROLL_MAX_CYCLES):
            try:
                hrefs = page.eval_on_selector_all(
                    "a",
                    "els => els.map(a => a.href).filter(h => !!h)",
                )
            except Exception:
                hrefs = []
            new = 0
            for h in hrefs:
                if _looks_like_detail_url(h, self.allow_domains) and h not in seen:
                    seen.add(h)
                    new += 1
            if new == 0:
                stable += 1
                if stable >= self.SCROLL_STABLE_THRESHOLD:
                    break
            else:
                stable = 0
            try:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            except Exception:
                pass
            page.wait_for_timeout(self.SCROLL_PAUSE_MS)

        return list(seen)

    def _fetch_detail(self, page, url: str) -> Optional[Dict[str, Any]]:
        page.goto(url, timeout=self.DETAIL_GOTO_TIMEOUT_MS, wait_until="domcontentloaded")
        page.wait_for_timeout(random.randint(800, 1500))

        title = ""
        for sel in TITLE_SELECTORS:
            try:
                el = page.query_selector(sel)
                if el:
                    t = (el.inner_text() or "").strip()
                    if 2 <= len(t) <= 200:
                        title = t
                        break
            except Exception:
                continue

        body = ""
        for sel in BODY_SELECTORS:
            try:
                el = page.query_selector(sel)
                if el:
                    b = (el.inner_text() or "").strip()
                    if len(b) >= 50:
                        body = b
                        break
            except Exception:
                continue
        if not body:
            try:
                body = page.eval_on_selector("body", "el => el.innerText || ''")
            except Exception:
                body = ""

        body = _norm_ws_multiline(body)

        city = ""
        if _contains_any(body, CITY_KEYWORDS) or _contains_any(title, CITY_KEYWORDS):
            city = "上海"

        publish_time = _extract_date(body)

        return {
            "url": url,
            "name": title,
            "city": city,
            "jd_raw": body,
            "publish_time": publish_time,
            "external_job_id": _extract_job_id_from_url(url),
        }


def _norm_ws_multiline(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_date(text: str) -> str:
    if not text:
        return ""
    m = re.search(r"(20\d{2}[./-]\d{1,2}[./-]\d{1,2})", text)
    if m:
        return m.group(1).replace("/", "-").replace(".", "-")
    return ""


def _extract_job_id_from_url(url: str) -> str:
    for pat in (
        r"jobid=([A-Za-z0-9_-]+)",
        r"positionId=([A-Za-z0-9_-]+)",
        r"reqid=([A-Za-z0-9_-]+)",
        r"/(\d{6,})",
        r"/([A-Z0-9]{6,}-[A-Z0-9]+)",
    ):
        m = re.search(pat, url, re.I)
        if m:
            return m.group(1)
    return ""


def _strip_html(html: str) -> str:
    if not html:
        return ""
    text = re.sub(r"<\s*br\s*/?>", "\n", html, flags=re.I)
    text = re.sub(r"</\s*(p|div|li|h[1-6])\s*>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = (
        text.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&#39;", "'")
        .replace("&quot;", '"')
    )
    return _norm_ws_multiline(text)


def _ts_to_str(ts) -> str:
    try:
        return datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# P0 — Google (careers.google.com)
# ---------------------------------------------------------------------------
class GoogleAdapter(BaseForeignAdapter):
    """Google careers — DOM-based crawl.

    Job cards are <li>/[role=listitem] elements containing the title text
    + a 'place' line + an anchor with /jobs/results/<id>-<slug>?location=...
    """

    SEARCH_URL = (
        "https://www.google.com/about/careers/applications/jobs/results?"
        "location=Shanghai%2C%20China"
    )

    def crawl(self, page, *, max_detail: int = 200) -> List[Dict[str, str]]:
        try:
            page.goto(self.SEARCH_URL, wait_until="networkidle", timeout=60000)
        except Exception as e:
            print(f"[{self.slug}] list-goto soft-fail: {e}")
        page.wait_for_timeout(5000)

        # Scroll to surface paginated cards (Google uses Load-more or auto-paginate).
        prev = -1
        for _ in range(15):
            try:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            except Exception:
                pass
            page.wait_for_timeout(1800)
            try:
                cur = page.eval_on_selector_all("li, [role='listitem']", "els => els.length")
            except Exception:
                cur = 0
            if cur == prev:
                break
            prev = cur

        cards = page.eval_on_selector_all(
            "li, [role='listitem']",
            """els => els.map(e => {
                const txt = e.innerText || '';
                const links = Array.from(e.querySelectorAll('a')).map(a => a.href).filter(h => !!h);
                const jobLink = links.find(h => h.indexOf('/jobs/results/') !== -1) || '';
                return {text: txt, href: jobLink};
            }).filter(c => c.href && (c.text.indexOf('Shanghai') !== -1 || c.text.indexOf('上海') !== -1))""",
        )

        seen: set = set()
        rows: List[Dict[str, str]] = []
        for card in cards:
            href = card.get("href") or ""
            if not href or href in seen:
                continue
            seen.add(href)
            txt = card.get("text") or ""
            title = txt.split("\n", 1)[0].strip()
            if not title:
                continue
            try:
                page.goto(href, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(1200)
                jd_raw = page.eval_on_selector(
                    "main, [role='main'], article, body",
                    "el => el.innerText || ''",
                ) or ""
            except Exception as e:
                print(f"[{self.slug}] detail err {href}: {e}")
                continue

            jd_raw = _norm_ws_multiline(jd_raw)
            ext_id = _extract_job_id_from_url(href) or md5_text(href)
            row = self.normalize({
                "url": href,
                "name": title,
                "city": "Shanghai",
                "jd_raw": jd_raw,
                "external_job_id": ext_id,
            })
            if self.passes_filter(row):
                rows.append(row)
            if len(rows) >= max_detail:
                break
            time.sleep(random.uniform(0.5, 1.0))
        return rows


# ---------------------------------------------------------------------------
# P0 — Microsoft (apply.careers.microsoft.com/api/pcsx/*)
# ---------------------------------------------------------------------------
class MicrosoftAdapter(BaseForeignAdapter):
    SEARCH_URL = "https://apply.careers.microsoft.com/api/pcsx/search"
    DETAIL_URL = "https://apply.careers.microsoft.com/api/pcsx/position_details"
    JOB_PUBLIC_URL = "https://jobs.careers.microsoft.com/global/en/job/{id}"
    # MS API hardcodes ~10/page regardless of page-size params; paginate by start += batch len.
    MAX_PAGES = 60

    def crawl(self, page=None, *, max_detail: int = 200) -> List[Dict[str, str]]:
        try:
            import requests
        except ImportError:
            print(f"[{self.slug}] requests missing; cannot run MS adapter")
            return []

        sess = requests.Session()
        sess.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Referer": "https://jobs.careers.microsoft.com/",
        })

        positions: List[Dict[str, Any]] = []
        seen_ids: set = set()
        start = 0
        for _ in range(self.MAX_PAGES):
            params = {
                "domain": "microsoft.com",
                "query": "",
                "location": "Shanghai, China",
                "start": start,
            }
            try:
                r = sess.get(self.SEARCH_URL, params=params, timeout=30)
            except Exception as e:
                print(f"[{self.slug}] search err start={start}: {e}")
                break
            if r.status_code != 200:
                print(f"[{self.slug}] search status={r.status_code} start={start}")
                break
            batch = (r.json().get("data") or {}).get("positions") or []
            if not batch:
                break
            new = 0
            for p in batch:
                pid = p.get("id")
                if pid and pid not in seen_ids:
                    seen_ids.add(pid)
                    positions.append(p)
                    new += 1
            if new == 0 or len(positions) >= max_detail:
                break
            start += len(batch)
            time.sleep(random.uniform(0.5, 1.0))

        rows: List[Dict[str, str]] = []
        for pos in positions[:max_detail]:
            std = " ".join(pos.get("standardizedLocations") or [])
            if "Shanghai" not in std:
                continue
            pos_id = pos.get("id")
            if not pos_id:
                continue
            try:
                dr = sess.get(
                    self.DETAIL_URL,
                    params={"position_id": pos_id, "domain": "microsoft.com", "hl": "en"},
                    timeout=30,
                )
                detail = (dr.json().get("data") or {}).get("position") or {}
            except Exception as e:
                print(f"[{self.slug}] detail err id={pos_id}: {e}")
                detail = {}

            jd = _strip_html(detail.get("jobDescription") or "")
            row = self.normalize({
                "url": self.JOB_PUBLIC_URL.format(id=pos_id),
                "name": pos.get("name") or detail.get("name") or "",
                "city": "Shanghai",
                "jd_raw": jd,
                "publish_time": _ts_to_str(pos.get("postedTs")),
                "external_job_id": str(pos.get("atsJobId") or pos_id),
                "raw_tags": pos.get("department") or "",
            })
            if self.passes_filter(row):
                rows.append(row)
            time.sleep(random.uniform(0.3, 0.8))
        return rows


# ---------------------------------------------------------------------------
# P0 — P&G (pgcareers.com, phenompeople ATS — DOM-based)
# ---------------------------------------------------------------------------
class PgAdapter(BaseForeignAdapter):
    """P&G's job listings render to anchor tags in HTML (no XHR data path).

    Strategy: visit the China-specific entry + a Shanghai search URL, scroll,
    extract /global/en/job/<id>/<slug> anchors, then visit each detail to pull
    full JD and city.
    """

    LIST_URLS = [
        "https://www.pgcareers.com/global/en/search-results?country=china&city=shanghai",
        "https://www.pgcareers.com/global/en/greater-china",
    ]
    JOB_URL_RE = re.compile(r"/global/en/job/[^/]+/")

    def crawl(self, page, *, max_detail: int = 200) -> List[Dict[str, str]]:
        all_links: set = set()
        for url in self.LIST_URLS:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                print(f"[{self.slug}] list-goto soft-fail {url}: {e}")
            page.wait_for_timeout(5000)
            prev = -1
            for _ in range(15):
                try:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                except Exception:
                    pass
                page.wait_for_timeout(1500)
                try:
                    hrefs = page.eval_on_selector_all(
                        "a", "els => els.map(a => a.href).filter(h => !!h)"
                    )
                except Exception:
                    hrefs = []
                for h in hrefs:
                    if "pgcareers.com" in h and self.JOB_URL_RE.search(h):
                        all_links.add(h)
                if len(all_links) == prev:
                    break
                prev = len(all_links)
                if len(all_links) >= max_detail * 2:
                    break

        rows: List[Dict[str, str]] = []
        for url in sorted(all_links)[:max_detail * 2]:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(1500)
                title = ""
                for sel in TITLE_SELECTORS:
                    try:
                        el = page.query_selector(sel)
                        if el:
                            t = (el.inner_text() or "").strip()
                            if 2 <= len(t) <= 200:
                                title = t
                                break
                    except Exception:
                        continue
                body = page.eval_on_selector("main, article, body", "el => el.innerText || ''") or ""
            except Exception as e:
                print(f"[{self.slug}] detail err {url}: {e}")
                continue

            body = _norm_ws_multiline(body)
            # P&G P0 = Shanghai only — strict
            if not _contains_any(body + " " + title, CITY_KEYWORDS):
                continue

            ext_id = ""
            m = re.search(r"/job/([^/]+)/", url)
            if m:
                ext_id = m.group(1)

            row = self.normalize({
                "url": url,
                "name": title,
                "city": "Shanghai",
                "jd_raw": body,
                "external_job_id": ext_id or md5_text(url),
            })
            if self.passes_filter(row):
                rows.append(row)
            if len(rows) >= max_detail:
                break
            time.sleep(random.uniform(0.6, 1.2))
        return rows


# ---------------------------------------------------------------------------
# P0 — Unilever (careers.unilever.com)
# ---------------------------------------------------------------------------
class UnileverAdapter(BaseForeignAdapter):
    # Unilever has a location-specific aggregated page.
    # It uses a similar structure to a generic inhouse site but with a pre-filtered URL.
    # We'll reuse the GenericInhouseAdapter's crawl logic, but customize the start_urls
    # and potentially any specific selectors if needed.

    def crawl(self, page, *, max_detail: int = 200) -> List[Dict[str, str]]:
        # For Unilever, we can mostly rely on the GenericInhouseAdapter's logic,
        # as its Shanghai aggregated page behaves like a list page that needs scrolling
        # and link extraction.
        generic_adapter = GenericInhouseAdapter(self.seed)
        generic_adapter.company = self.company # Ensure correct company name for normalization
        generic_adapter.slug = self.slug
        generic_adapter.start_urls = self.start_urls
        generic_adapter.allow_domains = self.allow_domains
        
        return generic_adapter.crawl(page, max_detail=max_detail)


# ---------------------------------------------------------------------------
# P0 — Citadel (citadel.com, citadelsecurities.com)
# ---------------------------------------------------------------------------
class CitadelAdapter(BaseForeignAdapter):
    """Citadel — DOM-based, multi-page.

    Job detail pages live at /careers/details/<slug>/. The /careers/
    landing page only surfaces a few; the full list is at
    /careers/open-opportunities/ + pagination /page/2/, /page/3/, /page/4/.
    Filter to Shanghai by JD content (their slugs include region tags
    like '-asia' which is a hint, but JD verification is authoritative).
    """

    LIST_URLS = [
        "https://www.citadel.com/careers/open-opportunities/",
        "https://www.citadel.com/careers/open-opportunities/page/2/",
        "https://www.citadel.com/careers/open-opportunities/page/3/",
        "https://www.citadel.com/careers/open-opportunities/page/4/",
    ]
    DETAIL_RE = re.compile(r"/careers/details/[^/]+/?$")

    def crawl(self, page, *, max_detail: int = 200) -> List[Dict[str, str]]:
        all_links: set = set()
        for url in self.LIST_URLS:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                print(f"[{self.slug}] list-goto soft-fail {url}: {e}")
            page.wait_for_timeout(7000)
            for _ in range(4):
                try:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                except Exception:
                    pass
                page.wait_for_timeout(1500)
            try:
                hrefs = page.eval_on_selector_all(
                    "a", "els => els.map(a => a.href).filter(h => !!h)"
                )
            except Exception:
                hrefs = []
            for h in hrefs:
                if "citadel.com" in h and self.DETAIL_RE.search(h):
                    all_links.add(h)
            if len(all_links) >= max_detail * 2:
                break

        rows: List[Dict[str, str]] = []
        for url in sorted(all_links)[:max_detail * 2]:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(1500)
                title = ""
                for sel in ("h1", "h2", "[class*='title']"):
                    try:
                        el = page.query_selector(sel)
                        if el:
                            t = (el.inner_text() or "").strip()
                            if 2 <= len(t) <= 200:
                                title = t
                                break
                    except Exception:
                        continue
                body = page.eval_on_selector("main, article, body", "el => el.innerText || ''") or ""
            except Exception as e:
                print(f"[{self.slug}] detail err {url}: {e}")
                continue

            body = _norm_ws_multiline(body)
            if not _contains_any(body + " " + title, CITY_KEYWORDS):
                continue

            slug_m = re.search(r"/careers/details/([^/]+)/?$", url)
            ext_id = slug_m.group(1) if slug_m else md5_text(url)

            row = self.normalize({
                "url": url,
                "name": title,
                "city": "Shanghai",
                "jd_raw": body,
                "external_job_id": ext_id,
            })
            if self.passes_filter(row):
                rows.append(row)
            if len(rows) >= max_detail:
                break
            time.sleep(random.uniform(0.8, 1.5))
        return rows


# ---------------------------------------------------------------------------
# P0 — Amazon (amazon.jobs/en/search.json)
# ---------------------------------------------------------------------------
class AmazonAdapter(BaseForeignAdapter):
    SEARCH_URL = "https://www.amazon.jobs/en/search.json"
    JOB_PUBLIC_URL = "https://www.amazon.jobs{path}"
    PAGE_SIZE = 100
    MAX_PAGES = 20

    def crawl(self, page=None, *, max_detail: int = 200) -> List[Dict[str, str]]:
        try:
            import requests
        except ImportError:
            print(f"[{self.slug}] requests missing; cannot run Amazon adapter")
            return []

        sess = requests.Session()
        sess.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Referer": "https://www.amazon.jobs/",
        })

        all_jobs: List[Dict[str, Any]] = []
        for pg in range(self.MAX_PAGES):
            params = {
                "city": "Shanghai",  # exact, all CHN; loc_query is fuzzy and unusable
                "result_limit": self.PAGE_SIZE,
                "offset": pg * self.PAGE_SIZE,
                "sort": "recent",
            }
            try:
                r = sess.get(self.SEARCH_URL, params=params, timeout=30)
            except Exception as e:
                print(f"[{self.slug}] search err pg={pg}: {e}")
                break
            if r.status_code != 200:
                print(f"[{self.slug}] search status={r.status_code} pg={pg}")
                break
            batch = r.json().get("jobs") or []
            if not batch:
                break
            all_jobs.extend(batch)
            if len(batch) < self.PAGE_SIZE or len(all_jobs) >= max_detail * 4:
                break
            time.sleep(random.uniform(0.5, 1.0))

        rows: List[Dict[str, str]] = []
        for j in all_jobs:
            # Strict Shanghai post-filter — Amazon's loc_query is fuzzy
            city = (j.get("city") or "").strip()
            country = (j.get("country_code") or "").strip().upper()
            normloc = (j.get("normalized_location") or "").strip()
            if not (
                city in ("Shanghai", "上海")
                or "Shanghai" in normloc
                or (country in ("CHN", "CN") and "Shanghai" in (j.get("location") or ""))
            ):
                continue

            url = self.JOB_PUBLIC_URL.format(path=j.get("job_path") or "")
            jd_parts = [
                j.get("description") or "",
                j.get("basic_qualifications") or "",
                j.get("preferred_qualifications") or "",
            ]
            jd_raw = _strip_html("\n\n".join(p for p in jd_parts if p))

            posted = j.get("posted_date") or ""
            try:
                if posted:
                    posted = datetime.strptime(posted, "%B %d, %Y").strftime("%Y-%m-%d")
            except Exception:
                pass

            row = self.normalize({
                "url": url,
                "name": j.get("title") or "",
                "city": "Shanghai",
                "jd_raw": jd_raw,
                "publish_time": posted,
                "external_job_id": str(j.get("id_icims") or j.get("id") or ""),
                "raw_tags": j.get("job_category") or j.get("business_category") or "",
            })
            if self.passes_filter(row):
                rows.append(row)
            if len(rows) >= max_detail:
                break
        return rows
