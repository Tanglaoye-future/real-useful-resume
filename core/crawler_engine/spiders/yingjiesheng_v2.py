import logging
import os

from core.crawler_engine.base_spider import BaseSpider
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


class YingjieshengSpiderV2(BaseSpider):
    def __init__(self, scheduler, base_cookie: str = ""):
        super().__init__("应届生", scheduler, base_cookie)
        self.max_pages = int(os.getenv("YINGJIESHENG_MAX_PAGES", "2"))
        self.entry_urls = [
            "https://www.yingjiesheng.com/shanghai/",
            "http://my.yingjiesheng.com/index.php/personal/jobsearch",
            "https://www.yingjiesheng.com/"
        ]

    def run(self):
        logger.info("Starting YingjieshengSpider V2 (Playwright Mode)...")
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
                        {"name": k, "value": v, "domain": ".yingjiesheng.com", "path": "/", "httpOnly": False, "secure": False}
                    )
                if cookies:
                    context.add_cookies(cookies)
            page = context.new_page()
            target_url = self.entry_urls[0]
            for url in self.entry_urls:
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=45000)
                    page.wait_for_timeout(1800)
                    html = page.content()
                    if "Access Denied" not in html and "forbidden" not in html.lower():
                        target_url = url
                        break
                except Exception:
                    continue
            for page_num in range(1, self.max_pages + 1):
                self.scheduler.throttle("yingjiesheng.com", 2.5)
                url = target_url
                if "shanghai" in target_url and page_num > 1:
                    url = f"https://www.yingjiesheng.com/shanghai-morejob-{page_num}.html"
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=45000)
                    page.wait_for_timeout(2000)
                    links = page.eval_on_selector_all(
                        "a[href]",
                        """els => els.map(a => ({href: a.getAttribute('href') || '', text: (a.innerText || '').trim()}))"""
                    )
                    for item in links:
                        href = (item or {}).get("href", "")
                        text = (item or {}).get("text", "")
                        if not href or "/job-" not in href:
                            continue
                        if href.startswith("//"):
                            jd_url = "https:" + href
                        elif href.startswith("/"):
                            jd_url = "https://www.yingjiesheng.com" + href
                        elif href.startswith("http"):
                            jd_url = href
                        else:
                            jd_url = "https://www.yingjiesheng.com/" + href.lstrip("./")
                        job_name = text if len(text) > 2 else "应届生岗位"
                        parsed = self.format_data(
                            job_name=job_name,
                            company_name="",
                            location="上海",
                            salary="",
                            job_type="校招/应届",
                            jd_url=jd_url,
                            jd_content="",
                            publish_date="",
                            city="上海",
                            employment_type="校招/应届",
                            source_job_id=jd_url.split("/")[-1].split(".")[0],
                            source_keyword="应届生"
                        )
                        all_jobs.append(parsed)
                except Exception as e:
                    logger.error(f"Yingjiesheng page={page_num} failed: {e}")
            browser.close()
        dedup = {}
        for row in all_jobs:
            key = row.get("jd_url", "")
            if key and key not in dedup:
                dedup[key] = row
        jobs = list(dedup.values())
        logger.info(f"Yingjiesheng Playwright collected {len(jobs)} jobs")
        return jobs
