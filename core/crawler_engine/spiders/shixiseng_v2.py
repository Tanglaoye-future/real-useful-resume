import io
import json
import logging
import os
import random
import re
import time
from core.crawler_engine.base_spider import BaseSpider
from core.crypto_engine.platforms.shixiseng import ShixisengCrypto
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

# Shixiseng detail page selectors — ordered by specificity
_DETAIL_JD_SELECTORS = [
    ".intern_position_description",
    ".job_detail_content",
    ".intern_detail_content",
    ".job-detail-content",
    ".intern-wrap__content",
    ".intern_position_detail",
    ".detail-content",
    "[class*='job_detail']",
    "[class*='position_detail']",
    "[class*='intern_detail']",
    ".job_msg",
    "main .content",
]


class ShixisengSpiderV2(BaseSpider):
    def __init__(self, scheduler, base_cookie: str = ""):
        super().__init__("实习僧", scheduler, base_cookie)
        self.crypto = ShixisengCrypto()
        self.api_url = "https://www.shixiseng.com/api/interns/search"
        self.page_count = int(os.getenv("SHIXISENG_MAX_PAGES", "20"))
        self.keyword = os.getenv("SHIXISENG_KEYWORD", "实习")
        self.city_query = os.getenv("SHIXISENG_CITY_QUERY", "上海")
        self.use_playwright = os.getenv("SHIXISENG_USE_PLAYWRIGHT", "1") == "1"
        self.max_retries = int(os.getenv("SHIXISENG_MAX_RETRIES", "3"))
        self.fetch_jd_detail = os.getenv("SHIXISENG_FETCH_JD", "1") == "1"
        self.detail_timeout = int(os.getenv("SHIXISENG_DETAIL_TIMEOUT", "30000"))

    def run(self):
        if self.use_playwright:
            return self.run_with_playwright()
        logger.info("Starting ShixisengSpider V2 (Font Decrypt Mode)...")
        all_jobs = []

        for page in range(1, 3):
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Cookie": self.base_cookie,
                "Referer": "https://www.shixiseng.com/interns"
            }
            params = {
                'k': '实习',
                'c': '310000', # 上海
                'p': page
            }

            self.scheduler.throttle("shixiseng.com", 2.0)

            try:
                response = self.fetcher.request("GET", self.api_url, headers=headers, params=params)
                jobs = self.parse(response)
                if jobs:
                    all_jobs.extend(jobs)
            except Exception as e:
                logger.error(f"Failed to fetch Shixiseng page {page}: {e}")

        return all_jobs

    def _throttle_with_jitter(self, base_delay: float = 2.0):
        """Throttle with randomized jitter to avoid fingerprinting."""
        delay = random.uniform(base_delay * 0.75, base_delay * 1.5)
        self.scheduler.throttle("shixiseng.com", delay)

    @staticmethod
    def _build_font_map(font_bytes: bytes) -> dict:
        """Parse a WOFF/TTF font file and build a PUA→char mapping.

        Shixiseng encodes salary digits using a randomly-remapped custom font.
        Each page load fetches a new font where PUA codepoints (e.g. U+E042) map
        to actual digit characters (e.g. '0'). Glyph names follow the 'uniXXXX'
        convention, so 'uni30' → U+0030 → '0'.
        """
        try:
            from fontTools.ttLib import TTFont
            font = TTFont(io.BytesIO(font_bytes))
            cmap = font.getBestCmap() or {}
            mapping = {}
            for pua_cp, glyph_name in cmap.items():
                # glyph name format: uni30 / uni4E2A / x (skip non-uni names)
                if glyph_name.startswith("uni") and len(glyph_name) > 3:
                    try:
                        target_cp = int(glyph_name[3:], 16)
                        mapping[chr(pua_cp)] = chr(target_cp)
                    except ValueError:
                        pass
            return mapping
        except Exception as e:
            logger.debug(f"Font decode failed: {e}")
            return {}

    @staticmethod
    def _apply_font_map(text: str, font_map: dict) -> str:
        """Replace PUA characters in text using the decoded font mapping."""
        if not font_map or not text:
            return text
        return "".join(font_map.get(ch, ch) for ch in text)

    def _fetch_listing_page(self, page, page_num: int) -> list:
        """Fetch a single listing page with retry logic.

        Intercepts the Shixiseng custom font file to decode salary digits that are
        obfuscated with Unicode Private Use Area characters.
        Returns list of card dicts.
        """
        url = f"https://www.shixiseng.com/interns?keyword={self.keyword}&city={self.city_query}&page={page_num}"
        base_delay = 2.0
        for attempt in range(1, self.max_retries + 1):
            try:
                self._throttle_with_jitter()

                # Intercept the custom font file to build PUA→char decoding map
                font_map: dict = {}
                def _on_response(response):
                    try:
                        if "iconfonts/file" in response.url and response.status == 200:
                            font_bytes = response.body()
                            decoded = self._build_font_map(font_bytes)
                            if decoded:
                                font_map.update(decoded)
                                logger.debug(f"Font decoded: {len(decoded)} mappings")
                    except Exception:
                        pass

                page.on("response", _on_response)
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(random.randint(1500, 3000))
                page.remove_listener("response", _on_response)

                cards = page.eval_on_selector_all(
                    "a[href*='/intern/inn_']",
                    """els => {
                        const seen = new Set();
                        return els.flatMap(a => {
                            const card = a.closest('.intern-wrap') || a.parentElement;
                            if (!card) return [];
                            const id = card.getAttribute('data-intern-id') || a.href;
                            if (seen.has(id)) return [];
                            seen.add(id);
                            const jobDiv  = card.querySelector('.intern-detail__job');
                            const compDiv = card.querySelector('.intern-detail__company');
                            const get = (el, sel) => { const e = el && el.querySelector(sel); return e ? e.innerText.trim() : ''; };
                            return [{
                                href:         a.href,
                                job_name:     get(jobDiv,  'a.title') || a.innerText.trim(),
                                company_name: get(compDiv, 'a.title'),
                                salary:       get(jobDiv,  '.day'),
                                location:     get(jobDiv,  '.city'),
                                text:         card.innerText || ''
                            }];
                        });
                    }"""
                )

                # Decode salary PUA chars using the intercepted font map
                if font_map:
                    for card in cards:
                        raw_salary = card.get("salary", "")
                        if raw_salary:
                            card["salary"] = self._apply_font_map(raw_salary, font_map)
                else:
                    logger.warning(f"page={page_num}: no font map captured, salary will be obfuscated")
                return cards
            except Exception as e:
                logger.warning(f"Shixiseng page={page_num} attempt={attempt}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries:
                    backoff = base_delay * (2 ** (attempt - 1)) + random.uniform(0.5, 2.0)
                    time.sleep(backoff)
        return []

    def _fetch_detail_jd(self, page, url: str) -> str:
        """Navigate to a job detail page and extract JD content.
        Returns the extracted JD text, or empty string on failure."""
        try:
            self._throttle_with_jitter(base_delay=1.5)
            page.goto(url, wait_until="domcontentloaded", timeout=self.detail_timeout)
            page.wait_for_timeout(random.randint(1000, 2000))

            # Try each selector in order of specificity
            for selector in _DETAIL_JD_SELECTORS:
                try:
                    el = page.query_selector(selector)
                    if el:
                        text = el.inner_text().strip()
                        if len(text) >= 40:
                            return text
                except Exception:
                    continue

            # Fallback: grab all text from the page body, try to extract JD section
            body_text = page.eval_on_selector("body", "el => el.innerText || ''")
            if body_text and len(body_text) >= 100:
                return body_text[:4000]

            return ""
        except Exception as e:
            logger.warning(f"Shixiseng detail fetch failed url={url}: {e}")
            return ""

    def run_with_playwright(self):
        logger.info(f"Starting ShixisengSpider V2 (Playwright Mode) keyword={self.keyword} city={self.city_query} max_pages={self.page_count}")
        all_cards = []
        global_seen_urls = set()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled", "--no-sandbox"])
            context = browser.new_context(
                user_agent=self.get_headers().get("User-Agent"),
                locale="zh-CN",
                timezone_id="Asia/Shanghai"
            )
            if self.base_cookie:
                cookies = []
                for k, v in self.parse_cookie_str(self.base_cookie).items():
                    cookies.append(
                        {"name": k, "value": v, "domain": ".shixiseng.com", "path": "/", "httpOnly": False, "secure": True}
                    )
                if cookies:
                    context.add_cookies(cookies)

            listing_page = context.new_page()
            empty_streak = 0

            # --- Phase 1: Collect all listing cards ---
            for page_num in range(1, self.page_count + 1):
                cards = self._fetch_listing_page(listing_page, page_num)

                new_count = 0
                for card in cards:
                    href = (card or {}).get("href", "")
                    if href and href not in global_seen_urls:
                        global_seen_urls.add(href)
                        all_cards.append(card)
                        new_count += 1

                logger.info(f"Shixiseng page={page_num}/{self.page_count} cards={len(cards)} new={new_count} total={len(all_cards)}")

                # Pagination exhaustion: stop if no new results for consecutive pages
                if new_count == 0:
                    empty_streak += 1
                    if empty_streak >= 2:
                        logger.info(f"Shixiseng pagination exhausted at page={page_num} (no new results for {empty_streak} pages)")
                        break
                else:
                    empty_streak = 0

            # --- Phase 2: Parse cards and optionally fetch JD details ---
            all_jobs = []
            detail_page = context.new_page() if self.fetch_jd_detail else None
            detail_success = 0
            detail_fail = 0

            for i, card in enumerate(all_cards):
                jd_url = card.get("href", "")
                if not jd_url:
                    continue
                job_name     = (card.get("job_name") or "").strip()
                company_name = (card.get("company_name") or "").strip()
                salary       = (card.get("salary") or "").strip()
                location     = (card.get("location") or "").strip() or "上海"

                # Strip salary leaking into job_name (e.g. "岗位名称 200/天")
                job_name = re.sub(r"\s*\d*[-~]\d*/[天月].*$", "", job_name).strip()

                # Fetch JD detail content
                jd_content = ""
                if self.fetch_jd_detail and detail_page:
                    jd_content = self._fetch_detail_jd(detail_page, jd_url)
                    if jd_content:
                        detail_success += 1
                    else:
                        detail_fail += 1
                    if (i + 1) % 10 == 0:
                        logger.info(f"Shixiseng detail progress: {i+1}/{len(all_cards)} success={detail_success} fail={detail_fail}")

                parsed = self.format_data(
                    job_name=job_name,
                    company_name=company_name,
                    location=location,
                    salary=salary,
                    job_type="实习",
                    jd_url=jd_url,
                    jd_content=jd_content,
                    publish_date="",
                    employment_type="实习",
                    source_job_id=jd_url.split("/")[-1].split("?")[0],
                    source_keyword=self.keyword,
                )
                all_jobs.append(parsed)

            if detail_page:
                detail_page.close()
            listing_page.close()
            browser.close()

        logger.info(f"Shixiseng Playwright collected {len(all_jobs)} jobs (detail: {detail_success} ok, {detail_fail} fail)")
        return all_jobs

    def parse(self, response):
        jobs = []
        try:
            # 实习僧返回的是带有乱码的 JSON 字符串，我们需要先将其视为文本，或者解析后针对特定字段解密
            # 假设 crypto 引擎中已经预设好了当前的 font mapping
            # 真实环境中应该从页面的 DOM 中提取 font woff url 传给 update_font_mapping
            # self.crypto.update_font_mapping("https://www.shixiseng.com/interns/iconfonts/file?rand=xxx.woff")

            raw_text = response.text
            # 暴力全文替换字体乱码（在解析 JSON 之前）
            decrypted_text = self.crypto.decrypt_text(raw_text, woff_url="mock_woff_url")

            data = json.loads(decrypted_text)

            if data.get('code') == 200 and 'msg' in data and data['msg']:
                for item in data['msg']:
                    tags = item.get("tag_list") or item.get("tags") or []
                    parsed_job = self.format_data(
                        job_name=item.get('name', ''),
                        company_name=item.get('company_name', ''),
                        location=item.get('city', '上海'),
                        salary=f"{item.get('minsal', '')}-{item.get('maxsal', '')}/天",
                        job_type="实习",
                        jd_url=f"https://www.shixiseng.com/intern/{item.get('uuid')}",
                        jd_content="",
                        publish_date=item.get('refresh_time', ''),
                        employment_type="实习",
                        source_job_id=item.get("uuid", ""),
                        source_keyword="实习",
                        job_tags=tags,
                        skill_tags=tags,
                        company_industry=item.get("type", ""),
                        company_stage=item.get("stage", ""),
                        company_size=item.get("company_scale", ""),
                        welfare_tags=item.get("welfare", "") or tags
                    )
                    jobs.append(parsed_job)
                    logger.info(f"Parsed Shixiseng job: {parsed_job['job_name']} @ {parsed_job['company_name']} - Salary: {parsed_job['salary']}")
            else:
                logger.warning(f"Shixiseng API no data: {data}")
        except json.JSONDecodeError:
             logger.error("Failed to decode JSON from Shixiseng (possibly intercepted).")
        except Exception as e:
             logger.error(f"Shixiseng parse error: {e}")
        return jobs
