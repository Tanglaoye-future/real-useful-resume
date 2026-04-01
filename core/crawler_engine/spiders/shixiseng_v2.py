import json
import logging
import os
from resuminer.core.crawler_engine.base_spider import BaseSpider
from resuminer.core.crypto_engine.platforms.shixiseng import ShixisengCrypto
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

class ShixisengSpiderV2(BaseSpider):
    def __init__(self, scheduler, base_cookie: str = ""):
        super().__init__("实习僧", scheduler, base_cookie)
        self.crypto = ShixisengCrypto()
        self.api_url = "https://www.shixiseng.com/api/interns/search"
        self.page_count = int(os.getenv("SHIXISENG_MAX_PAGES", "2"))
        self.keyword = os.getenv("SHIXISENG_KEYWORD", "实习")
        self.city_query = os.getenv("SHIXISENG_CITY_QUERY", "上海")
        self.use_playwright = os.getenv("SHIXISENG_USE_PLAYWRIGHT", "1") == "1"

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

    def run_with_playwright(self):
        logger.info("Starting ShixisengSpider V2 (Playwright Mode)...")
        all_jobs = []
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
            page = context.new_page()
            for page_num in range(1, self.page_count + 1):
                self.scheduler.throttle("shixiseng.com", 2.0)
                url = f"https://www.shixiseng.com/interns?keyword={self.keyword}&city={self.city_query}&page={page_num}"
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=45000)
                    page.wait_for_timeout(2000)
                    cards = page.eval_on_selector_all(
                        "a[href*='/intern/inn_']",
                        """els => els.map(a => {
                            const card = a.closest('.intern-wrap, .intern-item, li, .intern-item-wrap') || a.parentElement;
                            const text = (card ? card.innerText : a.innerText) || '';
                            return {href: a.href, text};
                        })"""
                    )
                    for card in cards:
                        jd_url = (card or {}).get("href", "")
                        if not jd_url:
                            continue
                        text = (card or {}).get("text", "")
                        lines = [x.strip() for x in text.split("\n") if x and x.strip()]
                        job_name = lines[0] if lines else ""
                        company_name = lines[1] if len(lines) > 1 else ""
                        salary = ""
                        location = "上海"
                        for ln in lines:
                            if "/天" in ln or "/月" in ln:
                                salary = ln
                            if "上海" in ln:
                                location = ln
                        parsed = self.format_data(
                            job_name=job_name,
                            company_name=company_name,
                            location=location,
                            salary=salary,
                            job_type="实习",
                            jd_url=jd_url,
                            jd_content="",
                            publish_date="",
                            employment_type="实习",
                            source_job_id=jd_url.split("/")[-1].split("?")[0],
                            source_keyword=self.keyword
                        )
                        all_jobs.append(parsed)
                except Exception as e:
                    logger.error(f"Shixiseng Playwright page={page_num} failed: {e}")
            browser.close()
        dedup = {}
        for row in all_jobs:
            key = row.get("jd_url", "")
            if key and key not in dedup:
                dedup[key] = row
        jobs = list(dedup.values())
        logger.info(f"Shixiseng Playwright collected {len(jobs)} jobs")
        return jobs

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
