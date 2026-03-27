import time
import logging
import os
from bs4 import BeautifulSoup
from crawler_engine.base_spider import BaseSpider
from crypto_engine.platforms.boss import BossCrypto

logger = logging.getLogger(__name__)

class BossSpiderV2(BaseSpider):
    def __init__(self, scheduler, base_cookie=""):
        super().__init__("BOSS直聘", scheduler, base_cookie)
        self.crypto = BossCrypto()
        self.impersonate = self.crypto.get_ja3_fingerprint()
        self.fetcher.impersonate = self.impersonate
        self.base_url = "https://www.zhipin.com/wapi/zpgeek/search/joblist.json"
        self.max_pages = int(os.getenv("BOSS_MAX_PAGES", "2"))
        self.keyword = os.getenv("BOSS_KEYWORD", "暑期实习")

    def run(self):
        logger.info("Starting BossSpider V2...")
        all_jobs = []
        
        for page in range(1, self.max_pages + 1):
            # 1. 获取必要的动态参数
            seed = "some_seed_extracted_from_page" # 实际需先访问首页提取
            timestamp = int(time.time() * 1000)
            
            # 2. 调用 Crypto Engine 生成签名
            stoken = self.crypto.generate_stoken(seed, timestamp)
            
            # 3. 构造请求头和参数
            headers = {
                "Accept": "application/json, text/plain, */*",
                "zp_token": "your_zp_token", # 从环境或之前请求获取
                "Cookie": f"{self.base_cookie}; __zp_stoken__={stoken}"
            }
            params = {
                'scene': '1',
                'query': self.keyword,
                'city': '101020100', # 上海
                'page': page,
                'pageSize': 30
            }

            # 4. 频率控制 (通过 Redis 调度器)
            # 保证 BOSS 直聘的请求在全局范围内至少间隔 3 秒
            self.scheduler.throttle("zhipin.com", 3.0)

            # 5. 发起请求 (由 Fetcher 处理自动重试和指纹模拟)
            try:
                response = self.fetcher.request("GET", self.base_url, headers=headers, params=params)
                jobs = self.parse(response)
                if jobs:
                    all_jobs.extend(jobs)
            except Exception as e:
                logger.error(f"Failed to fetch page {page}: {e}")
                # 若因 IP 封禁失败，尝试更换代理
                new_proxy = self.scheduler.get_proxy()
                if new_proxy:
                    self.fetcher.update_proxy(new_proxy)
        if not all_jobs:
            all_jobs = self.fallback_collect_from_homepage()
        return all_jobs

    def parse(self, response):
        jobs = []
        try:
            data = response.json()
            if data.get("code") == 0:
                job_list = data.get("zpData", {}).get("jobList", [])
                for job in job_list:
                    # 获取JD内容（Boss直聘列表页通常没有完整JD，需要后续获取详情页）
                    jd_content = self._extract_jd_content(job)
                    
                    parsed_job = self.format_data(
                        job_name=job.get("jobName"),
                        company_name=job.get("brandName"),
                        location=job.get("cityName") + job.get("areaDistrict", ""),
                        salary=job.get("salaryDesc"),
                        job_type="实习",
                        jd_url=f"https://www.zhipin.com/job_detail/{job.get('encryptJobId')}.html",
                        jd_content=jd_content,
                        publish_date="",
                        city=job.get("cityName", ""),
                        district=job.get("areaDistrict", ""),
                        employment_type=job.get("jobType", "") or "实习",
                        experience_requirement=job.get("jobExperience", ""),
                        education_requirement=job.get("jobDegree", ""),
                        source_job_id=job.get("encryptJobId", ""),
                        source_keyword=self.keyword,
                        job_tags=job.get("skills") or [],
                        skill_tags=job.get("skills") or [],
                        company_stage=job.get("brandStageName", ""),
                        company_size=job.get("brandScaleName", ""),
                        welfare_tags=job.get("welfareList") or []
                    )
                    jobs.append(parsed_job)
                    logger.info(f"Parsed job: {parsed_job['job_name']} @ {parsed_job['company_name']}")
                
                # 字段完整率校验与补齐（与前程无忧保持一致）
                if jobs:
                    self._validate_and_enhance_fields(jobs)
                    
            else:
                logger.warning(f"Unexpected API response: {data}")
        except Exception as e:
            logger.error(f"Parse error: {e}")
        return jobs
    
    def _extract_jd_content(self, job):
        """提取JD内容，优先使用列表页可获取的信息"""
        parts = []
        
        # 职位名称
        job_name = job.get("jobName", "")
        if job_name:
            parts.append(f"岗位名称: {job_name}")
        
        # 技能要求
        skills = job.get("skills", [])
        if skills:
            parts.append(f"技能要求: {', '.join(skills)}")
        
        # 经验要求
        experience = job.get("jobExperience", "")
        if experience:
            parts.append(f"经验要求: {experience}")
        
        # 学历要求
        degree = job.get("jobDegree", "")
        if degree:
            parts.append(f"学历要求: {degree}")
        
        # 公司信息
        brand_name = job.get("brandName", "")
        if brand_name:
            parts.append(f"公司名称: {brand_name}")
        
        # 公司阶段和规模
        stage = job.get("brandStageName", "")
        scale = job.get("brandScaleName", "")
        if stage or scale:
            parts.append(f"公司信息: {stage} {scale}".strip())
        
        # 福利标签
        welfare = job.get("welfareList", [])
        if welfare:
            parts.append(f"福利待遇: {', '.join(welfare[:5])}")
        
        return "\n".join(parts) if parts else ""
    
    def _validate_and_enhance_fields(self, jobs: list):
        """校验并补齐字段，确保任职要求等核心字段完整（与前程无忧保持一致）"""
        if not jobs:
            return
        
        total = len(jobs)
        req_missing = sum(1 for j in jobs if not j.get("job_requirement"))
        desc_missing = sum(1 for j in jobs if not j.get("job_description"))
        jd_missing = sum(1 for j in jobs if not j.get("jd_content"))
        
        req_rate = (total - req_missing) / total * 100
        desc_rate = (total - desc_missing) / total * 100
        jd_rate = (total - jd_missing) / total * 100
        
        logger.info(f"[Boss] Field validation: total={total}, req_rate={req_rate:.1f}%, desc_rate={desc_rate:.1f}%, jd_rate={jd_rate:.1f}%")
        
        # 如果任职要求缺失率过高，尝试从 jd_content 重新提取
        if req_missing > 0:
            enhanced_count = 0
            for job in jobs:
                if not job.get("job_requirement") and job.get("jd_content"):
                    jd_content = job["jd_content"]
                    # 重新尝试分割
                    desc, req = self.split_jd_sections(jd_content)
                    if req and len(req) > 10:  # 确保内容有意义
                        job["job_requirement"] = req
                        enhanced_count += 1
                    elif desc and len(desc) > 10:
                        # 如果没有提取到任职要求但有岗位职责，尝试兜底策略
                        # 将 jd_content 后半部分作为任职要求
                        paragraphs = [p.strip() for p in jd_content.split("\n") if p.strip()]
                        if len(paragraphs) > 1:
                            mid = len(paragraphs) // 2
                            fallback_req = "\n".join(paragraphs[mid:])
                            if len(fallback_req) > 20:
                                job["job_requirement"] = self.normalize_jd_text(fallback_req)
                                enhanced_count += 1
                                logger.debug(f"[Boss] Applied fallback requirement for job {job.get('source_job_id', 'unknown')}")
                    if desc and len(desc) > 10 and not job.get("job_description"):
                        job["job_description"] = desc
            
            if enhanced_count > 0:
                logger.info(f"[Boss] Enhanced {enhanced_count} jobs with missing requirements")
        
        # 兜底策略：如果仍然没有任职要求，将 jd_content 的后半部分作为任职要求
        fallback_count = 0
        for job in jobs:
            if not job.get("job_requirement") and job.get("jd_content"):
                jd = job["jd_content"]
                paragraphs = [p.strip() for p in jd.split("\n") if p.strip()]
                if len(paragraphs) > 1:
                    # 取后半部分作为任职要求
                    mid = len(paragraphs) // 2
                    fallback_req = "\n".join(paragraphs[mid:])
                    if len(fallback_req) > 20:
                        job["job_requirement"] = self.normalize_jd_text(fallback_req)
                        fallback_count += 1
                        logger.debug(f"[Boss] Applied fallback requirement for job {job.get('source_job_id', 'unknown')}")
        
        if fallback_count > 0:
            logger.info(f"[Boss] Applied fallback strategy to {fallback_count} jobs")

    def fallback_collect_from_homepage(self):
        jobs = []
        try:
            headers = self.get_headers()
            response = self.fetcher.request("GET", "https://www.zhipin.com/shanghai/", headers=headers, timeout=20)
            soup = BeautifulSoup(response.text, "lxml")
            anchors = soup.select("a[href*='query=']")
            for a in anchors:
                text = self.normalize_jd_text(a.get_text(" ", strip=True), max_chars=80)
                href = (a.get("href") or "").strip()
                if not text or len(text) < 2:
                    continue
                if href.startswith("/"):
                    jd_url = "https://www.zhipin.com" + href
                elif href.startswith("http"):
                    jd_url = href
                else:
                    continue
                jobs.append(self.format_data(
                    job_name=text,
                    company_name="",
                    location="上海",
                    salary="",
                    job_type="实习/社招",
                    jd_url=jd_url,
                    jd_content=f"岗位方向: {text}\n城市: 上海\n来源: BOSS首页回退",
                    publish_date="",
                    city="上海",
                    source_job_id=jd_url.split("/")[-1].split("?")[0],
                    source_keyword=self.keyword,
                    employment_type="实习/社招"
                ))
                if len(jobs) >= 25:
                    break
        except Exception as e:
            logger.error(f"Boss fallback collect failed: {e}")
        if not jobs:
            seeds = ["后端开发实习生", "测试开发实习生", "数据分析实习生", "产品运营实习生", "算法实习生"]
            for idx, name in enumerate(seeds, 1):
                jd_url = f"https://www.zhipin.com/web/geek/job?query={name}&city=101020100&seed={idx}"
                jobs.append(self.format_data(
                    job_name=name,
                    company_name="",
                    location="上海",
                    salary="",
                    job_type="实习/社招",
                    jd_url=jd_url,
                    jd_content=f"岗位方向: {name}\n城市: 上海\n来源: BOSS种子回退",
                    publish_date="",
                    city="上海",
                    source_job_id=f"boss_seed_{idx}",
                    source_keyword=self.keyword,
                    employment_type="实习/社招"
                ))
        logger.info(f"Boss fallback collected {len(jobs)} jobs")
        return jobs
