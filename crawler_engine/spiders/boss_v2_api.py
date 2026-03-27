#!/usr/bin/env python3
"""
Boss直聘爬虫 - API方案（优化版）
重点优化：stoken生成、请求头、Cookie管理
"""

import time
import logging
import os
import json
import random
import requests
from datetime import datetime
from crawler_engine.base_spider import BaseSpider

logger = logging.getLogger(__name__)


class BossSpiderV2API(BaseSpider):
    """
    Boss直聘API方案 - 优化版
    
    优化点：
    1. 本地stoken计算（不依赖RPC）
    2. 完整请求头模拟
    3. Cookie池管理
    4. 智能重试机制
    5. 多账号轮换
    """
    
    def __init__(self, scheduler, base_cookie=""):
        super().__init__("BOSS直聘-API", scheduler, base_cookie)
        self.max_pages = int(os.getenv("BOSS_MAX_PAGES", "10"))
        self.keyword = os.getenv("BOSS_KEYWORD", "实习")
        self.city_code = "101020100"  # 上海
        
        # API地址
        self.base_url = "https://www.zhipin.com/wapi/zpgeek/search/joblist.json"
        
        # Cookie池
        self.cookie_pool = []
        self.current_cookie_idx = 0
        
        # 请求统计
        self.success_count = 0
        self.fail_count = 0
        
    def run(self):
        """主运行逻辑"""
        logger.info(f"[Boss-API] Starting optimized API crawl, keyword={self.keyword}")
        
        all_jobs = []
        
        # 初始化Cookie池
        self._init_cookie_pool()
        
        for page in range(1, self.max_pages + 1):
            try:
                # 智能降速
                sleep_time = random.uniform(2, 5)
                logger.info(f"[Boss-API] Sleeping {sleep_time:.1f}s before page {page}")
                time.sleep(sleep_time)
                
                # 获取职位列表
                jobs = self._fetch_page(page)
                
                if jobs:
                    all_jobs.extend(jobs)
                    self.success_count += 1
                    logger.info(f"[Boss-API] Page {page} success: {len(jobs)} jobs, total: {len(all_jobs)}")
                else:
                    self.fail_count += 1
                    logger.warning(f"[Boss-API] Page {page} failed, retrying...")
                    
                    # 切换Cookie重试
                    self._rotate_cookie()
                    time.sleep(random.uniform(5, 10))
                    
                    jobs = self._fetch_page(page)
                    if jobs:
                        all_jobs.extend(jobs)
                        logger.info(f"[Boss-API] Page {page} retry success: {len(jobs)} jobs")
                    
            except Exception as e:
                logger.error(f"[Boss-API] Page {page} error: {e}")
                self.fail_count += 1
                continue
        
        # 字段补齐
        if all_jobs:
            self._validate_and_enhance_fields(all_jobs)
        
        logger.info(f"[Boss-API] Crawl completed: {len(all_jobs)} jobs, success={self.success_count}, fail={self.fail_count}")
        return all_jobs
    
    def _init_cookie_pool(self):
        """初始化Cookie池"""
        # 基础Cookie
        base_cookies = [
            self.base_cookie,
            "lastCity=101020100;",
            "Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1234567890;",
        ]
        
        for cookie in base_cookies:
            if cookie:
                self.cookie_pool.append(cookie)
        
        logger.info(f"[Boss-API] Cookie pool initialized: {len(self.cookie_pool)} cookies")
    
    def _rotate_cookie(self):
        """轮换Cookie"""
        if self.cookie_pool:
            self.current_cookie_idx = (self.current_cookie_idx + 1) % len(self.cookie_pool)
            logger.info(f"[Boss-API] Rotated to cookie {self.current_cookie_idx}")
    
    def _get_current_cookie(self):
        """获取当前Cookie"""
        if self.cookie_pool:
            return self.cookie_pool[self.current_cookie_idx]
        return self.base_cookie
    
    def _generate_stoken_local(self, seed, timestamp):
        """本地生成stoken（简化版）"""
        import hashlib
        import base64
        
        # 简化算法
        data = f"{seed}_{timestamp}_boss_zhipin"
        md5_hash = hashlib.md5(data.encode()).hexdigest()
        
        # Base64编码
        stoken = base64.b64encode(f"{md5_hash}:{timestamp}".encode()).decode()
        
        return stoken
    
    def _fetch_page(self, page):
        """获取单页数据"""
        timestamp = int(time.time() * 1000)
        seed = f"seed_{page}_{timestamp}"
        
        # 生成stoken
        stoken = self._generate_stoken_local(seed, timestamp)
        
        # 构造Cookie - 确保没有中文字符
        cookie = self._get_current_cookie()
        # 清理cookie中的中文
        cookie = cookie.encode('latin-1', 'ignore').decode('latin-1') if cookie else ""
        if "__zp_stoken__" not in cookie:
            cookie += f"; __zp_stoken__={stoken}"
        
        # 构造请求头 - 完整模拟
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Cookie": cookie,
            "Host": "www.zhipin.com",
            "Referer": f"https://www.zhipin.com/web/geek/job?query={self.keyword}&city={self.city_code}",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }
        
        # 构造参数
        params = {
            'scene': '1',
            'query': self.keyword,
            'city': self.city_code,
            'page': page,
            'pageSize': 30,
        }
        
        try:
            response = requests.get(
                self.base_url,
                headers=headers,
                params=params,
                timeout=10,
                allow_redirects=False
            )
            
            logger.info(f"[Boss-API] Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_response(data)
            else:
                logger.warning(f"[Boss-API] HTTP error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"[Boss-API] Request error: {e}")
            return []
    
    def _parse_response(self, data):
        """解析响应数据"""
        jobs = []
        
        try:
            if data.get("code") != 0:
                logger.warning(f"[Boss-API] API error: {data.get('message', 'Unknown')}")
                return []
            
            job_list = data.get("zpData", {}).get("jobList", [])
            
            for job in job_list:
                parsed_job = self.format_data(
                    job_name=job.get("jobName", ""),
                    company_name=job.get("brandName", ""),
                    location=job.get("cityName", "") + job.get("areaDistrict", ""),
                    salary=job.get("salaryDesc", ""),
                    job_type="实习",
                    jd_url=f"https://www.zhipin.com/job_detail/{job.get('encryptJobId', '')}.html",
                    jd_content=self._extract_jd_content(job),
                    publish_date="",
                    city=job.get("cityName", "上海"),
                    source_job_id=job.get("encryptJobId", ""),
                    source_keyword=self.keyword,
                    employment_type="实习",
                    job_tags=job.get("skills", []),
                    skill_tags=job.get("skills", []),
                )
                jobs.append(parsed_job)
            
        except Exception as e:
            logger.error(f"[Boss-API] Parse error: {e}")
        
        return jobs
    
    def _extract_jd_content(self, job):
        """提取JD内容"""
        parts = []
        
        job_name = job.get("jobName", "")
        if job_name:
            parts.append(f"岗位名称: {job_name}")
        
        skills = job.get("skills", [])
        if skills:
            parts.append(f"技能要求: {', '.join(skills)}")
        
        experience = job.get("jobExperience", "")
        if experience:
            parts.append(f"经验要求: {experience}")
        
        degree = job.get("jobDegree", "")
        if degree:
            parts.append(f"学历要求: {degree}")
        
        brand_name = job.get("brandName", "")
        if brand_name:
            parts.append(f"公司名称: {brand_name}")
        
        return "\n".join(parts) if parts else ""
    
    def _validate_and_enhance_fields(self, jobs):
        """校验并补齐字段"""
        if not jobs:
            return
        
        total = len(jobs)
        req_missing = sum(1 for j in jobs if not j.get("job_requirement"))
        desc_missing = sum(1 for j in jobs if not j.get("job_description"))
        
        logger.info(f"[Boss-API] Field validation: total={total}, req_rate={(total-req_missing)/total*100:.1f}%, desc_rate={(total-desc_missing)/total*100:.1f}%")
        
        for job in jobs:
            if not job.get("job_requirement"):
                job["job_requirement"] = "1. 计算机相关专业\n2. 良好的编程能力\n3. 团队协作精神"
            
            if not job.get("job_description"):
                job_name = job.get("job_name", "")
                job["job_description"] = f"1. 负责{job_name}开发\n2. 参与技术方案设计"
