#!/usr/bin/env python3
"""
猎聘爬虫 V6 - RPC版本
通过RPC调用浏览器环境执行请求，绕过反爬机制
"""

import logging
import os
import random
import time
from datetime import datetime
from resuminer.crawler.base.base_spider import BaseSpider
from resuminer.core.crypto_engine.platforms.liepin import LiepinCrypto

logger = logging.getLogger(__name__)


class LiepinSpiderV6(BaseSpider):
    """
    猎聘爬虫 V6 - RPC版本
    
    特点:
    1. 使用RPC调用浏览器环境执行请求
    2. 支持重试、限流、断点续传
    3. 多关键词全量爬取
    """
    
    def __init__(self, scheduler, base_cookie: str = ""):
        super().__init__("猎聘", scheduler, base_cookie)
        self.crypto = LiepinCrypto()
        self.keyword = os.getenv("LIEPIN_KEYWORD", "实习")
        self.max_pages = int(os.getenv("LIEPIN_MAX_PAGES", "500"))
        self.city_code = os.getenv("LIEPIN_CITY", "020")
        self.page_size = int(os.getenv("LIEPIN_PAGE_SIZE", "20"))
        self.throttle_min = float(os.getenv("LIEPIN_THROTTLE_MIN", "5"))
        self.throttle_max = float(os.getenv("LIEPIN_THROTTLE_MAX", "10"))
        self.max_retry = int(os.getenv("LIEPIN_MAX_RETRY", "3"))
        self.empty_streak_limit = int(os.getenv("LIEPIN_EMPTY_STREAK_LIMIT", "5"))
        
    def run(self):
        """主运行逻辑"""
        logger.info(f"[Liepin V6] Starting RPC crawl, keyword={self.keyword}, max_pages={self.max_pages}")
        all_jobs = []
        empty_streak = 0
        
        for page_num in range(1, self.max_pages + 1):
            try:
                # 限流
                sleep_time = random.uniform(self.throttle_min, self.throttle_max)
                logger.info(f"[Liepin V6] Sleeping {sleep_time:.1f}s before page {page_num}")
                time.sleep(sleep_time)
                
                # 通过RPC获取数据
                jobs = self._fetch_page(page_num)
                
                if jobs:
                    all_jobs.extend(jobs)
                    empty_streak = 0
                    logger.info(f"[Liepin V6] Page {page_num}: {len(jobs)} jobs, total: {len(all_jobs)}")
                else:
                    empty_streak += 1
                    logger.warning(f"[Liepin V6] No jobs on page {page_num}, empty_streak={empty_streak}")
                    
                # 连续空页检测
                if empty_streak >= self.empty_streak_limit:
                    logger.info(f"[Liepin V6] Stopping due to {empty_streak} empty pages")
                    break
                    
            except Exception as e:
                logger.error(f"[Liepin V6] Page {page_num} error: {e}")
                continue
        
        # 去重并返回
        unique_jobs = self._dedup_jobs(all_jobs)
        logger.info(f"[Liepin V6] Crawl completed: {len(all_jobs)} raw, {len(unique_jobs)} unique jobs")
        return unique_jobs
    
    def _fetch_page(self, page_num: int):
        """获取单页数据"""
        retry_count = 0
        
        while retry_count < self.max_retry:
            try:
                logger.info(f"[Liepin V6] Fetching page {page_num} (attempt {retry_count + 1}/{self.max_retry})")
                
                # 调用RPC接口
                result = self.crypto.search_jobs(
                    keyword=self.keyword,
                    page_num=page_num,
                    city=self.city_code,
                    page_size=self.page_size
                )
                
                # 调试：打印返回结果
                logger.info(f"[Liepin V6] RPC result type: {type(result)}, keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
                
                # 检查是否被拦截
                if isinstance(result, dict):
                    if result.get("blocked"):
                        logger.warning(f"[Liepin V6] Blocked on page {page_num}: {result.get('message', 'Unknown')}")
                        retry_count += 1
                        time.sleep(random.uniform(self.throttle_min, self.throttle_max))
                        continue
                    
                    if result.get("error"):
                        logger.error(f"[Liepin V6] Error on page {page_num}: {result.get('error')}")
                        retry_count += 1
                        time.sleep(random.uniform(self.throttle_min, self.throttle_max))
                        continue
                
                # 解析职位数据
                jobs = self._parse_response(result)
                logger.info(f"[Liepin V6] Parsed {len(jobs)} jobs from response")
                return jobs
                
            except Exception as e:
                logger.error(f"[Liepin V6] Fetch page {page_num} failed (retry {retry_count + 1}): {e}")
                retry_count += 1
                time.sleep(random.uniform(self.throttle_min, self.throttle_max))
        
        logger.error(f"[Liepin V6] Failed to fetch page {page_num} after {self.max_retry} retries")
        return []
    
    def _parse_response(self, data):
        """解析API响应"""
        jobs = []
        
        try:
            if not isinstance(data, dict):
                logger.warning(f"[Liepin V6] Data is not dict: {type(data)}")
                return jobs
            
            logger.debug(f"[Liepin V6] Response data keys: {list(data.keys())}")
            
            # 获取职位列表 - 支持多种格式
            job_data = data.get("data", {})
            if not isinstance(job_data, dict):
                logger.warning(f"[Liepin V6] job_data is not dict: {type(job_data)}")
                return jobs
                
            job_list = job_data.get("jobCardList", []) or job_data.get("jobList", [])
            
            if not job_list:
                logger.debug(f"[Liepin V6] Empty job list in response. job_data keys: {list(job_data.keys())}")
                return jobs
            
            logger.info(f"[Liepin V6] Found {len(job_list)} jobs in response")
            
            for item in job_list:
                try:
                    job = self._format_job(item)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.warning(f"[Liepin V6] Parse item error: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"[Liepin V6] Parse response error: {e}")
        
        return jobs
    
    def _format_job(self, item):
        """格式化职位数据 - 支持API和DOM两种格式"""
        try:
            # 处理DOM解析格式
            if "title" in item:
                job_id = item.get("job_id", "")
                href = item.get("href", "")
                if not job_id and href:
                    import re
                    match = re.search(r'/job/(\d+)', href)
                    if match:
                        job_id = match.group(1)
                
                if not job_id:
                    # 生成临时ID
                    job_id = f"dom_{hash(item.get('title', '')) % 10000000}"
                
                return self.format_data(
                    job_name=item.get("title", ""),
                    company_name=item.get("company", ""),
                    location=item.get("location", "上海"),
                    salary=item.get("salary", ""),
                    job_type="实习",
                    jd_url=href or f"https://www.liepin.com/job/{job_id}.shtml",
                    jd_content="",
                    publish_date=datetime.now().strftime("%Y-%m-%d"),
                    city=item.get("location", "上海").split("-")[0] if "-" in item.get("location", "") else item.get("location", "上海"),
                    source_job_id=job_id,
                    source_keyword=self.keyword,
                    employment_type="实习",
                    experience_requirement=item.get("experience", ""),
                    education_requirement=item.get("education", ""),
                    job_tags=item.get("tags", []),
                    skill_tags=item.get("tags", []),
                    company_industry="",
                    company_stage="",
                    company_size="",
                    welfare_tags=[],
                    refresh_time=datetime.now().strftime("%Y-%m-%d"),
                    recruitment_count="",
                    detail_address="",
                    company_id="",
                    company_property="",
                    job_description="",
                    job_requirement=""
                )
            
            # 处理API格式
            job_id = item.get("jobId", "")
            if not job_id:
                return None
            
            # 解析薪资
            salary = item.get("salary", "")
            if not salary and item.get("salaryDesc"):
                salary = item.get("salaryDesc")
            
            # 解析地点
            location = item.get("city", "上海")
            if item.get("dq"):
                location = item.get("dq")
            
            # 解析发布时间
            publish_date = item.get("publishTime", "")
            if not publish_date:
                publish_date = datetime.now().strftime("%Y-%m-%d")
            
            # 解析公司阶段
            company_stage = item.get("compStage", "")
            if not company_stage and item.get("compStageName"):
                company_stage = item.get("compStageName")
            
            # 解析公司规模
            company_size = item.get("compScale", "")
            if not company_size and item.get("compScaleName"):
                company_size = item.get("compScaleName")
            
            # 构建福利标签
            welfare_tags = []
            if item.get("welfareTagList"):
                welfare_tags = item.get("welfareTagList")
            elif item.get("welfareTag"):
                welfare_tags = [item.get("welfareTag")]
            
            # 构建技能标签
            skill_tags = []
            if item.get("skillTagList"):
                skill_tags = item.get("skillTagList")
            elif item.get("labels"):
                skill_tags = item.get("labels")
            
            return self.format_data(
                job_name=item.get("jobName", ""),
                company_name=item.get("compName", ""),
                location=location,
                salary=salary,
                job_type=item.get("jobKind", "实习"),
                jd_url=f"https://www.liepin.com/job/{job_id}.shtml",
                jd_content=item.get("jobDesc", ""),
                publish_date=publish_date,
                city=location.split("-")[0] if "-" in location else location,
                source_job_id=job_id,
                source_keyword=self.keyword,
                employment_type=item.get("jobKind", "实习"),
                experience_requirement=item.get("requireWorkYears", ""),
                education_requirement=item.get("requireEduLevel", ""),
                job_tags=skill_tags,
                skill_tags=skill_tags,
                company_industry=item.get("industryName", ""),
                company_stage=company_stage,
                company_size=company_size,
                welfare_tags=welfare_tags,
                refresh_time=item.get("refreshTime", publish_date),
                recruitment_count=item.get("recruitCount", ""),
                detail_address=item.get("address", ""),
                company_id=item.get("compId", ""),
                company_property=item.get("compKindName", ""),
                job_description=item.get("jobDesc", ""),
                job_requirement=item.get("requirement", "")
            )
            
        except Exception as e:
            logger.warning(f"[Liepin V6] Format job error: {e}")
            return None
    
    def _dedup_jobs(self, jobs):
        """去重"""
        dedup = {}
        for job in jobs:
            key = job.get("jd_url", "") or f"{job.get('job_name', '')}_{job.get('company_name', '')}"
            if key and key not in dedup:
                dedup[key] = job
        
        return list(dedup.values())
