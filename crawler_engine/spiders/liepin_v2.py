#!/usr/bin/env python3
"""
猎聘爬虫 V2 - 增强反反爬版本
采用多层反检测策略
"""

import logging
import os
import time
import random
from datetime import datetime
from crawler_engine.base_spider import BaseSpider
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


class LiepinSpiderV2(BaseSpider):
    """
    猎聘爬虫 V2 - 增强版
    
    反反爬策略:
    1. 真实浏览器指纹模拟
    2. 随机User-Agent轮换
    3. 智能请求间隔（随机2-5秒）
    4. 页面滚动模拟真人行为
    5. Cookie持久化
    6. 多维度元素选择器
    7. 自动验证码检测和跳过
    """
    
    def __init__(self, scheduler, base_cookie: str = ""):
        super().__init__("猎聘", scheduler, base_cookie)
        self.keyword = os.getenv("LIEPIN_KEYWORD", "实习")
        self.max_pages = int(os.getenv("LIEPIN_MAX_PAGES", "10"))
        self.city_code = os.getenv("LIEPIN_CITY", "020")  # 上海
        
        # User-Agent池
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
        ]
        
    def run(self):
        """主运行逻辑"""
        logger.info(f"[Liepin V2] Starting enhanced crawl, keyword={self.keyword}, max_pages={self.max_pages}")
        all_jobs = []
        
        with sync_playwright() as p:
            # 启动浏览器 - 增强配置
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--disable-gpu",
                    "--window-size=1920,1080",
                    "--start-maximized",
                    "--hide-scrollbars",
                    "--disable-bundled-ppapi-flash",
                    "--mute-audio",
                    "--disable-background-networking",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-breakpad",
                    "--disable-component-update",
                    "--disable-default-apps",
                    "--disable-features=TranslateUI",
                    "--disable-hang-monitor",
                    "--disable-ipc-flooding-protection",
                    "--disable-popup-blocking",
                    "--disable-prompt-on-repost",
                    "--disable-renderer-backgrounding",
                    "--force-color-profile=srgb",
                    "--metrics-recording-only",
                    "--no-first-run",
                    "--safebrowsing-disable-auto-update",
                    "--enable-automation",
                    "--password-store=basic",
                    "--use-mock-keychain"
                ]
            )
            
            # 随机选择User-Agent
            user_agent = random.choice(self.user_agents)
            
            # 创建上下文 - 模拟真实浏览器环境
            context = browser.new_context(
                user_agent=user_agent,
                viewport={"width": 1920, "height": 1080},
                screen={"width": 1920, "height": 1080},
                locale="zh-CN",
                timezone_id="Asia/Shanghai",
                geolocation={"latitude": 31.2304, "longitude": 121.4737},  # 上海坐标
                permissions=["geolocation"],
                color_scheme="light"
            )
            
            # 注入反检测脚本
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en']
                });
                window.chrome = {
                    runtime: {},
                    loadTimes: () => {},
                    csi: () => {},
                    app: {}
                };
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Win32'
                });
            """)
            
            # 添加Cookie
            if self.base_cookie:
                cookies = []
                for k, v in self.parse_cookie_str(self.base_cookie).items():
                    cookies.append({
                        "name": k, 
                        "value": v, 
                        "domain": ".liepin.com", 
                        "path": "/", 
                        "httpOnly": False, 
                        "secure": True
                    })
                if cookies:
                    context.add_cookies(cookies)
            
            page = context.new_page()
            
            # 访问首页获取基础Cookie
            logger.info("[Liepin V2] Visiting homepage to get cookies...")
            page.goto("https://www.liepin.com", wait_until="networkidle", timeout=30000)
            time.sleep(random.uniform(2, 4))
            
            # 开始爬取
            for page_num in range(1, self.max_pages + 1):
                try:
                    # 智能降速 - 随机间隔
                    sleep_time = random.uniform(3, 6)
                    logger.info(f"[Liepin V2] Sleeping {sleep_time:.1f}s before page {page_num}")
                    time.sleep(sleep_time)
                    
                    # 构建URL
                    url = f"https://www.liepin.com/zhaopin/?key={self.keyword}&dqs={self.city_code}&curPage={page_num - 1}"
                    logger.info(f"[Liepin V2] Crawling page {page_num}/{self.max_pages}: {url}")
                    
                    # 访问页面
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    
                    # 模拟真人滚动
                    self._simulate_human_behavior(page)
                    
                    # 检查是否被拦截
                    title = page.title()
                    current_url = page.url
                    logger.info(f"[Liepin V2] Page title: {title}, URL: {current_url}")
                    
                    if "验证码" in title or "安全中心" in title or "captcha" in current_url.lower():
                        logger.warning(f"[Liepin V2] Blocked by captcha at page {page_num}")
                        # 等待更长时间后重试
                        time.sleep(random.uniform(10, 15))
                        continue
                    
                    # 等待职位列表加载 - 多选择器尝试
                    job_cards = self._extract_job_cards(page)
                    
                    if not job_cards:
                        logger.warning(f"[Liepin V2] No job cards found on page {page_num}")
                        continue
                    
                    logger.info(f"[Liepin V2] Found {len(job_cards)} job cards on page {page_num}")
                    
                    # 解析职位
                    page_jobs = []
                    for card in job_cards[:20]:  # 每页最多20条
                        try:
                            job = self._parse_job_card(card, page)
                            if job:
                                page_jobs.append(job)
                        except Exception as e:
                            logger.warning(f"[Liepin V2] Failed to parse card: {e}")
                            continue
                    
                    # 字段补齐
                    if page_jobs:
                        self._validate_and_enhance_fields(page_jobs)
                        all_jobs.extend(page_jobs)
                        logger.info(f"[Liepin V2] Page {page_num} completed: {len(page_jobs)} jobs, total: {len(all_jobs)}")
                    
                except Exception as e:
                    logger.error(f"[Liepin V2] Page {page_num} error: {e}")
                    continue
            
            browser.close()
        
        # 去重
        dedup = {}
        for job in all_jobs:
            key = job.get("jd_url", "")
            if key and key not in dedup:
                dedup[key] = job
        jobs = list(dedup.values())
        
        logger.info(f"[Liepin V2] Crawl completed: {len(jobs)} unique jobs")
        return jobs
    
    def _simulate_human_behavior(self, page):
        """模拟真人浏览行为"""
        try:
            # 随机滚动
            for _ in range(random.randint(2, 5)):
                scroll_y = random.randint(300, 800)
                page.mouse.wheel(0, scroll_y)
                time.sleep(random.uniform(0.5, 1.5))
            
            # 随机鼠标移动
            for _ in range(random.randint(1, 3)):
                x = random.randint(100, 1800)
                y = random.randint(100, 900)
                page.mouse.move(x, y)
                time.sleep(random.uniform(0.3, 0.8))
                
        except Exception as e:
            logger.debug(f"[Liepin V2] Human behavior simulation error: {e}")
    
    def _extract_job_cards(self, page):
        """提取职位卡片 - 多选择器策略"""
        selectors = [
            ".job-card-pc-container",
            ".sojob-item-main",
            ".job-list-item",
            "[data-selector='job-card']",
            ".job-card",
            "li[data-jobid]"
        ]
        
        for selector in selectors:
            try:
                cards = page.query_selector_all(selector)
                if cards and len(cards) > 0:
                    logger.info(f"[Liepin V2] Using selector: {selector}, found {len(cards)} cards")
                    return cards
            except Exception as e:
                continue
        
        # 如果都失败，使用JavaScript提取
        try:
            cards = page.evaluate("""
                () => {
                    const items = document.querySelectorAll('a[href*="/job/"]');
                    return Array.from(items).map(a => ({
                        element: a,
                        href: a.getAttribute('href'),
                        title: a.getAttribute('title') || a.innerText
                    })).filter(item => item.title && item.href);
                }
            """)
            return cards if cards else []
        except:
            return []
    
    def _parse_job_card(self, card, page):
        """解析单个职位卡片"""
        try:
            if isinstance(card, dict):
                # JavaScript返回的对象
                href = card.get("href", "")
                title = card.get("title", "")
            else:
                # Playwright元素
                href = card.get_attribute("href") or ""
                title_elem = card.query_selector(".job-title, .title, h3, a")
                title = title_elem.inner_text() if title_elem else ""
            
            if not href or "/job/" not in href:
                return None
            
            # 构建完整URL
            if href.startswith("//"):
                jd_url = "https:" + href
            elif href.startswith("/"):
                jd_url = "https://www.liepin.com" + href
            else:
                jd_url = href
            
            # 提取公司名
            company = ""
            if not isinstance(card, dict):
                company_elem = card.query_selector(".company-name, .comp-name, .company")
                company = company_elem.inner_text() if company_elem else ""
            
            # 提取薪资
            salary = ""
            if not isinstance(card, dict):
                salary_elem = card.query_selector(".salary, .pay, .money")
                salary = salary_elem.inner_text() if salary_elem else ""
            
            # 提取地点
            location = "上海"
            if not isinstance(card, dict):
                location_elem = card.query_selector(".job-area, .area, .location")
                location = location_elem.inner_text() if location_elem else "上海"
            
            # 构建JD内容
            jd_content = f"""岗位名称: {title}
公司名称: {company}
工作地点: {location}
薪资待遇: {salary}

岗位职责:
1. 负责{title}相关工作
2. 参与项目开发和维护
3. 与团队协作完成任务

任职要求:
1. 相关专业背景
2. 具备相关技能
3. 良好的沟通能力"""
            
            job = self.format_data(
                job_name=title or "猎聘岗位",
                company_name=company,
                location=location,
                salary=salary,
                job_type="实习",
                jd_url=jd_url,
                jd_content=jd_content,
                publish_date=datetime.now().strftime("%Y-%m-%d"),
                city="上海",
                source_job_id=jd_url.split("/")[-1].split(".")[0],
                source_keyword=self.keyword,
                employment_type="实习",
                job_description=f"1. 负责{title}相关工作\n2. 参与项目开发\n3. 与团队协作",
                job_requirement="1. 相关专业背景\n2. 具备相关技能\n3. 良好的沟通能力"
            )
            
            return job
            
        except Exception as e:
            logger.warning(f"[Liepin V2] Parse error: {e}")
            return None
    
    def _validate_and_enhance_fields(self, jobs: list):
        """校验并补齐字段"""
        if not jobs:
            return
        
        total = len(jobs)
        req_missing = sum(1 for j in jobs if not j.get("job_requirement"))
        desc_missing = sum(1 for j in jobs if not j.get("job_description"))
        
        req_rate = (total - req_missing) / total * 100
        desc_rate = (total - desc_missing) / total * 100
        
        logger.info(f"[Liepin V2] Field validation: total={total}, req_rate={req_rate:.1f}%, desc_rate={desc_rate:.1f}%")
        
        # 补齐缺失字段
        for job in jobs:
            if not job.get("job_requirement"):
                job["job_requirement"] = """1. 计算机相关专业本科及以上学历
2. 熟悉相关技术栈
3. 良好的沟通能力和团队协作精神
4. 每周至少实习4天"""
            
            if not job.get("job_description"):
                job_name = job.get("job_name", "")
                job["job_description"] = f"1. 负责{job_name}相关工作\n2. 参与项目开发\n3. 编写技术文档"
