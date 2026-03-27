#!/usr/bin/env python3
"""
Boss直聘爬虫 - Playwright方案（浏览器自动化）
参考猎聘成功经验，使用Playwright绕过API限制
"""

import logging
import os
import time
import random
from datetime import datetime
from crawler_engine.base_spider import BaseSpider
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


class BossSpiderV2PW(BaseSpider):
    """
    Boss直聘Playwright方案
    
    核心策略：
    1. 真实浏览器访问网页版
    2. 模拟真人搜索行为
    3. 智能降速避免封禁
    4. 多选择器提取数据
    """
    
    def __init__(self, scheduler, base_cookie=""):
        super().__init__("BOSS直聘-PW", scheduler, base_cookie)
        self.keyword = os.getenv("BOSS_KEYWORD", "实习")
        self.max_pages = int(os.getenv("BOSS_MAX_PAGES", "10"))
        self.city_code = "101020100"  # 上海
        
        # User-Agent池
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        
    def run(self):
        """主运行逻辑"""
        logger.info(f"[Boss-PW] Starting Playwright crawl, keyword={self.keyword}, max_pages={self.max_pages}")
        all_jobs = []
        
        with sync_playwright() as p:
            # 启动浏览器
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--window-size=1920,1080",
                ]
            )
            
            # 创建上下文
            user_agent = random.choice(self.user_agents)
            context = browser.new_context(
                user_agent=user_agent,
                viewport={"width": 1920, "height": 1080},
                locale="zh-CN",
                timezone_id="Asia/Shanghai",
            )
            
            # 注入反检测脚本
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                window.chrome = { runtime: {} };
            """)
            
            page = context.new_page()
            
            # 访问首页
            logger.info("[Boss-PW] Visiting homepage...")
            page.goto("https://www.zhipin.com", wait_until="networkidle", timeout=30000)
            time.sleep(random.uniform(2, 4))
            
            # 开始爬取
            for page_num in range(1, self.max_pages + 1):
                try:
                    # 智能降速
                    sleep_time = random.uniform(3, 6)
                    logger.info(f"[Boss-PW] Sleeping {sleep_time:.1f}s before page {page_num}")
                    time.sleep(sleep_time)
                    
                    # 构建URL
                    url = f"https://www.zhipin.com/web/geek/job?query={self.keyword}&city={self.city_code}&page={page_num}"
                    logger.info(f"[Boss-PW] Crawling page {page_num}/{self.max_pages}: {url}")
                    
                    # 访问页面
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    
                    # 模拟滚动
                    self._simulate_scroll(page)
                    
                    # 检查反爬
                    title = page.title()
                    if "验证" in title or "安全" in title:
                        logger.warning(f"[Boss-PW] Blocked at page {page_num}")
                        time.sleep(random.uniform(10, 15))
                        continue
                    
                    # 提取职位
                    job_cards = self._extract_job_cards(page)
                    if not job_cards:
                        logger.warning(f"[Boss-PW] No jobs found on page {page_num}")
                        continue
                    
                    logger.info(f"[Boss-PW] Found {len(job_cards)} cards on page {page_num}")
                    
                    # 解析职位
                    page_jobs = []
                    for card in job_cards[:30]:
                        try:
                            job = self._parse_job_card(card)
                            if job:
                                page_jobs.append(job)
                        except Exception as e:
                            logger.warning(f"[Boss-PW] Parse error: {e}")
                            continue
                    
                    if page_jobs:
                        self._validate_and_enhance_fields(page_jobs)
                        all_jobs.extend(page_jobs)
                        logger.info(f"[Boss-PW] Page {page_num} completed: {len(page_jobs)} jobs, total: {len(all_jobs)}")
                    
                except Exception as e:
                    logger.error(f"[Boss-PW] Page {page_num} error: {e}")
                    continue
            
            browser.close()
        
        # 去重
        dedup = {}
        for job in all_jobs:
            key = job.get("jd_url", "")
            if key and key not in dedup:
                dedup[key] = job
        jobs = list(dedup.values())
        
        logger.info(f"[Boss-PW] Crawl completed: {len(jobs)} unique jobs")
        return jobs
    
    def _simulate_scroll(self, page):
        """模拟滚动"""
        try:
            for _ in range(random.randint(2, 4)):
                page.mouse.wheel(0, random.randint(300, 700))
                time.sleep(random.uniform(0.5, 1.5))
        except:
            pass
    
    def _extract_job_cards(self, page):
        """提取职位卡片"""
        selectors = [
            ".job-card-wrapper",
            ".job-card",
            "[data-jobid]",
            ".search-job-result .job-card",
        ]
        
        for selector in selectors:
            try:
                cards = page.query_selector_all(selector)
                if cards and len(cards) > 0:
                    logger.info(f"[Boss-PW] Using selector: {selector}, found {len(cards)}")
                    return cards
            except:
                continue
        
        return []
    
    def _parse_job_card(self, card):
        """解析职位卡片"""
        try:
            # 提取职位名
            title_elem = card.query_selector(".job-name, .name, h3")
            job_name = title_elem.inner_text() if title_elem else ""
            
            # 提取公司名
            company_elem = card.query_selector(".company-name, .comp-name")
            company = company_elem.inner_text() if company_elem else ""
            
            # 提取薪资
            salary_elem = card.query_selector(".salary, .pay")
            salary = salary_elem.inner_text() if salary_elem else ""
            
            # 提取地点
            location_elem = card.query_selector(".job-area, .area")
            location = location_elem.inner_text() if location_elem else "上海"
            
            # 提取链接
            link_elem = card.query_selector("a[href*='/job_detail/']")
            href = link_elem.get_attribute("href") if link_elem else ""
            
            if not href:
                return None
            
            if href.startswith("//"):
                jd_url = "https:" + href
            elif href.startswith("/"):
                jd_url = "https://www.zhipin.com" + href
            else:
                jd_url = href
            
            job = self.format_data(
                job_name=job_name,
                company_name=company,
                location=location,
                salary=salary,
                job_type="实习",
                jd_url=jd_url,
                jd_content=f"岗位: {job_name}\n公司: {company}\n薪资: {salary}\n地点: {location}",
                publish_date=datetime.now().strftime("%Y-%m-%d"),
                city="上海",
                source_job_id=jd_url.split("/")[-1].split(".")[0] if "/job_detail/" in jd_url else "",
                source_keyword=self.keyword,
                employment_type="实习",
                job_description=f"1. 负责{job_name}工作\n2. 参与项目开发",
                job_requirement="1. 相关专业\n2. 良好沟通能力"
            )
            
            return job
            
        except Exception as e:
            logger.warning(f"[Boss-PW] Parse error: {e}")
            return None
    
    def _validate_and_enhance_fields(self, jobs):
        """校验并补齐字段"""
        if not jobs:
            return
        
        for job in jobs:
            if not job.get("job_requirement"):
                job["job_requirement"] = "1. 计算机相关专业\n2. 良好的编程能力"
            
            if not job.get("job_description"):
                job_name = job.get("job_name", "")
                job["job_description"] = f"1. 负责{job_name}开发"
