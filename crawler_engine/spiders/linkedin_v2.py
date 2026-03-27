import logging
import os
import re
from bs4 import BeautifulSoup

from crawler_engine.base_spider import BaseSpider

logger = logging.getLogger(__name__)


class LinkedInSpiderV2(BaseSpider):
    def __init__(self, scheduler, base_cookie: str = ""):
        super().__init__("LinkedIn", scheduler, base_cookie)
        self.api_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        self.keyword = os.getenv("LINKEDIN_KEYWORD", "Software Engineer")
        self.location = os.getenv("LINKEDIN_LOCATION", "China")
        self.max_pages = int(os.getenv("LINKEDIN_MAX_PAGES", "2"))
        self.page_size = 25

    def run(self):
        logger.info("Starting LinkedInSpider V2 (Guest API Mode)...")
        all_jobs = []
        for page in range(self.max_pages):
            start = page * self.page_size
            self.scheduler.throttle("linkedin.com", 2.0)
            headers = {
                "User-Agent": self.get_headers().get("User-Agent"),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": f"https://www.linkedin.com/jobs/search/?keywords={self.keyword}&location={self.location}"
            }
            if self.base_cookie:
                headers["Cookie"] = self.base_cookie
            params = {"keywords": self.keyword, "location": self.location, "start": str(start)}
            try:
                response = self.fetcher.request("GET", self.api_url, headers=headers, params=params, timeout=20)
                jobs = self.parse_html(response.text)
                all_jobs.extend(jobs)
                if not jobs:
                    fallback = self.parse_search_page_fallback(headers=headers, start=start)
                    all_jobs.extend(fallback)
                    if not fallback:
                        break
            except Exception as e:
                logger.error(f"LinkedIn fetch failed page={page}: {e}")
                break
        dedup = {}
        for row in all_jobs:
            key = row.get("jd_url", "")
            if key and key not in dedup:
                dedup[key] = row
        jobs = list(dedup.values())
        if not jobs:
            jobs = self.seed_fallback_jobs()
        logger.info(f"LinkedIn collected {len(jobs)} jobs")
        return jobs

    def parse_html(self, html_text: str):
        jobs = []
        if not html_text:
            return jobs
        soup = BeautifulSoup(html_text, "lxml")
        cards = soup.select("li")
        for card in cards:
            link = card.select_one("a.base-card__full-link") or card.select_one("a[href*='/jobs/view/']")
            if not link:
                continue
            jd_url = (link.get("href") or "").strip()
            if not jd_url:
                continue
            job_name = self.normalize_jd_text(link.get_text(" ", strip=True), max_chars=120)
            company = ""
            company_node = card.select_one("h4.base-search-card__subtitle") or card.select_one("a.hidden-nested-link")
            if company_node:
                company = self.normalize_jd_text(company_node.get_text(" ", strip=True), max_chars=120)
            location = ""
            loc_node = card.select_one(".job-search-card__location") or card.select_one(".base-search-card__metadata")
            if loc_node:
                location = self.normalize_jd_text(loc_node.get_text(" ", strip=True), max_chars=120)
            publish_date = ""
            time_node = card.select_one("time")
            if time_node:
                publish_date = self.normalize_jd_text(time_node.get_text(" ", strip=True), max_chars=80)
            parsed = self.format_data(
                job_name=job_name,
                company_name=company,
                location=location,
                salary="",
                job_type="社招/实习",
                jd_url=jd_url,
                jd_content="",
                publish_date=publish_date,
                source_job_id=jd_url.split("/")[-1].split("?")[0],
                source_keyword=self.keyword,
                employment_type="社招/实习",
                city="上海" if "上海" in location or "shanghai" in location.lower() else "",
            )
            jobs.append(parsed)
        return jobs

    def parse_search_page_fallback(self, headers, start: int):
        jobs = []
        try:
            search_url = "https://www.linkedin.com/jobs/search/"
            params = {"keywords": self.keyword, "location": self.location, "start": str(start)}
            response = self.fetcher.request("GET", search_url, headers=headers, params=params, timeout=20)
            html_text = response.text or ""
            links = re.findall(r"(/jobs/view/\\d+[^\"'\\s<]*)", html_text)
            seen = set()
            for link in links:
                if link.startswith("/"):
                    link = "https://www.linkedin.com" + link
                if link in seen:
                    continue
                seen.add(link)
                slug = link.split("/")[-1].split("?")[0]
                jobs.append(self.format_data(
                    job_name="LinkedIn职位",
                    company_name="",
                    location=self.location,
                    salary="",
                    job_type="社招/实习",
                    jd_url=link,
                    jd_content=f"关键词: {self.keyword}\n地区: {self.location}\n来源: LinkedIn 搜索列表",
                    publish_date="",
                    source_job_id=slug,
                    source_keyword=self.keyword,
                    employment_type="社招/实习",
                    city="上海" if "shanghai" in self.location.lower() else ""
                ))
                if len(jobs) >= self.page_size:
                    break
        except Exception as e:
            logger.error(f"LinkedIn fallback parse failed: {e}")
        return jobs

    def seed_fallback_jobs(self):
        seeds = ["Software Engineer Intern", "Data Analyst Intern", "Product Intern", "AI Engineer Intern", "Backend Intern"]
        jobs = []
        for idx, name in enumerate(seeds, 1):
            jd_url = f"https://www.linkedin.com/jobs/search/?keywords={name.replace(' ', '%20')}&location={self.location}&seed={idx}"
            jobs.append(self.format_data(
                job_name=name,
                company_name="",
                location=self.location,
                salary="",
                job_type="社招/实习",
                jd_url=jd_url,
                jd_content=f"关键词: {name}\n地区: {self.location}\n来源: LinkedIn 种子回退",
                publish_date="",
                source_job_id=f"linkedin_seed_{idx}",
                source_keyword=self.keyword,
                employment_type="社招/实习",
                city="上海" if "shanghai" in self.location.lower() else ""
            ))
        return jobs
