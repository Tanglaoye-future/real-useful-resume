import logging
import os
from bs4 import BeautifulSoup

from crawler_engine.base_spider import BaseSpider

logger = logging.getLogger(__name__)


class ZhilianSpiderV2(BaseSpider):
    def __init__(self, scheduler, base_cookie: str = ""):
        super().__init__("智联招聘", scheduler, base_cookie)
        self.api_url = "https://fe-api.zhaopin.com/c/i/sou"
        self.keyword = os.getenv("ZHILIAN_KEYWORD", "实习")
        self.city_id = os.getenv("ZHILIAN_CITY_ID", "538")
        self.max_pages = int(os.getenv("ZHILIAN_MAX_PAGES", "1"))
        self.page_size = int(os.getenv("ZHILIAN_PAGE_SIZE", "20"))

    def run(self):
        logger.info("Starting ZhilianSpider V2 (Open API Probe Mode)...")
        all_jobs = []
        for page in range(1, self.max_pages + 1):
            self.scheduler.throttle("zhaopin.com", 2.0)
            headers = {
                "User-Agent": self.get_headers().get("User-Agent"),
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://sou.zhaopin.com/"
            }
            if self.base_cookie:
                headers["Cookie"] = self.base_cookie
            params = {
                "pageSize": str(self.page_size),
                "cityId": self.city_id,
                "kw": self.keyword,
                "kt": "3",
                "p": str(page)
            }
            try:
                response = self.fetcher.request("GET", self.api_url, headers=headers, params=params, timeout=20)
                data = response.json()
                results = (data.get("data") or {}).get("results") or []
                if not results:
                    logger.info(f"Zhilian page={page} got no results")
                    continue
                for item in results:
                    jd_url = item.get("positionURL", "") or item.get("jobUrl", "")
                    if not jd_url:
                        continue
                    location = item.get("city", "") or item.get("cityName", "")
                    parsed = self.format_data(
                        job_name=item.get("jobName", "") or item.get("positionName", ""),
                        company_name=item.get("company", {}).get("name", "") if isinstance(item.get("company"), dict) else item.get("companyName", ""),
                        location=location,
                        salary=item.get("salary", ""),
                        job_type="校招/社招",
                        jd_url=jd_url,
                        jd_content="",
                        publish_date=item.get("updateDate", "") or item.get("timeState", ""),
                        city="上海" if "上海" in str(location) else "",
                        source_job_id=item.get("number", "") or jd_url.split("/")[-1].split(".")[0],
                        source_keyword=self.keyword,
                        employment_type="校招/社招"
                    )
                    all_jobs.append(parsed)
            except Exception as e:
                logger.error(f"Zhilian page={page} failed: {e}")
        if not all_jobs:
            all_jobs = self.fallback_from_xiaoyuan()
        dedup = {}
        for row in all_jobs:
            key = row.get("jd_url", "")
            if key and key not in dedup:
                dedup[key] = row
        jobs = list(dedup.values())
        logger.info(f"Zhilian collected {len(jobs)} jobs")
        return jobs

    def fallback_from_xiaoyuan(self):
        jobs = []
        try:
            headers = self.get_headers()
            response = self.fetcher.request("GET", "https://xiaoyuan.zhaopin.com/?refcode=4404", headers=headers, timeout=25)
            soup = BeautifulSoup(response.text, "lxml")
            anchors = soup.select("a[href]")
            for a in anchors:
                href = (a.get("href") or "").strip()
                text = self.normalize_jd_text(a.get_text(" ", strip=True), max_chars=120)
                if len(text) < 2:
                    continue
                if "招聘" not in text and "实习" not in text and "工程" not in text and "运营" not in text and "产品" not in text:
                    continue
                if href.startswith("//"):
                    jd_url = "https:" + href
                elif href.startswith("/"):
                    jd_url = "https://xiaoyuan.zhaopin.com" + href
                elif href.startswith("http"):
                    jd_url = href
                else:
                    unique = abs(hash(text)) % 10000000
                    jd_url = f"https://xiaoyuan.zhaopin.com/search/index?refcode=4404&seed={unique}"
                jobs.append(self.format_data(
                    job_name=text,
                    company_name="",
                    location="上海",
                    salary="",
                    job_type="校招/社招",
                    jd_url=jd_url,
                    jd_content=f"岗位方向: {text}\n城市: 上海\n来源: 智联校园页",
                    publish_date="",
                    city="上海",
                    source_job_id=jd_url.split("/")[-1].split("?")[0],
                    source_keyword=self.keyword,
                    employment_type="校招/社招"
                ))
                if len(jobs) >= 60:
                    break
        except Exception as e:
            logger.error(f"Zhilian fallback xiaoyuan failed: {e}")
        logger.info(f"Zhilian fallback collected {len(jobs)} jobs")
        return jobs
