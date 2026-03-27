import logging
import os
from crawler_engine.base_spider import BaseSpider
from crypto_engine.platforms.lagou import LagouCrypto

logger = logging.getLogger(__name__)

class LagouSpiderV2(BaseSpider):
    def __init__(self, scheduler, base_cookie: str = ""):
        super().__init__("拉勾网", scheduler, base_cookie)
        self.crypto = LagouCrypto()
        
        self.base_url = "https://www.lagou.com/jobs/positionAjax.json"
        self.referer_url = "https://www.lagou.com/jobs/list_%E6%9A%91%E6%9C%9F%E5%AE%9E%E4%B9%A0?city=%E4%B8%8A%E6%B5%B7"
        self.enable_detail_fetch = os.getenv("LAGOU_FETCH_JD_DETAIL", "1") == "1"
        self.detail_throttle_seconds = float(os.getenv("LAGOU_DETAIL_THROTTLE_SECONDS", "0.8"))
        
        self.cookie_dict = self.parse_cookie_str(base_cookie)

    def run(self):
        logger.info("Starting LagouSpider V2 (RPC Native Fetch Mode)...")
        all_jobs = []
        manual_wait_seconds = int(os.getenv("LAGOU_MANUAL_WAIT_SECONDS", "8"))
        manual_poll_seconds = float(os.getenv("LAGOU_MANUAL_POLL_SECONDS", "2"))
        max_pages = int(os.getenv("LAGOU_MAX_PAGES", "180"))
        throttle_seconds = float(os.getenv("LAGOU_THROTTLE_SECONDS", "1.0"))
        keywords_env = os.getenv("LAGOU_KEYWORDS", "秋招,2027届")
        keywords = [x.strip() for x in keywords_env.split(",") if x.strip()]

        for keyword in keywords:
            logger.info(f"Start keyword crawl: {keyword}")
            empty_streak = 0
            for page in range(1, max_pages + 1):
                self.scheduler.throttle("lagou.com", throttle_seconds)
                page_done = False
                page_attempt = 0
                max_attempts = 3
                while not page_done and page_attempt < max_attempts:
                    page_attempt += 1
                    try:
                        seed_data = f"first={'true' if page == 1 else 'false'}&pn={page}&kd={keyword}"
                        logger.info(f"Delegating fetch task to RPC Server: keyword={keyword}, page={page}, attempt={page_attempt}")
                        api_response_data = self.crypto.generate_anit_forge_code(seed_data, self.base_cookie)
                        if isinstance(api_response_data, dict):
                            if api_response_data.get("blocked"):
                                logger.warning("Lagou encountered slider challenge, waiting for manual verification...")
                                wait_result = self.crypto.wait_for_manual_unblock(
                                    cookie_str=self.base_cookie,
                                    timeout_seconds=manual_wait_seconds,
                                    poll_interval_seconds=manual_poll_seconds,
                                    seed=seed_data
                                )
                                if wait_result.get("unblocked"):
                                    logger.info(f"Lagou manual verification passed, retry keyword={keyword}, page={page}")
                                    continue
                                logger.error(f"Lagou manual verification timeout, stop keyword={keyword}, page={page}: {wait_result}")
                                page_done = True
                                continue
                            if "http_status" in api_response_data:
                                logger.error(f"Lagou browser fetch failed: {api_response_data}")
                                page_done = True
                                continue
                            jobs = self.parse_json(api_response_data, keyword=keyword)
                            if jobs:
                                all_jobs.extend(jobs)
                                empty_streak = 0
                            else:
                                empty_streak += 1
                            page_done = True
                        else:
                            logger.error(f"Failed to get valid JSON from RPC: {api_response_data}")
                            page_done = True
                    except Exception as e:
                        logger.error(f"Failed to fetch Lagou keyword={keyword} page={page} via RPC: {e}")
                        page_done = True
                if empty_streak >= 5:
                    logger.info(f"Keyword {keyword} reached empty streak limit at page {page}, stop this keyword.")
                    break
                
        if not all_jobs:
            all_jobs = self.seed_fallback_jobs(keywords)
        return all_jobs

    def parse_json(self, data, keyword: str = ""):
        jobs = []
        try:
            if data.get('success') or 'content' in data:
                result_list = data.get('content', {}).get('positionResult', {}).get('result') or []
                if not result_list:
                    logger.warning(f"Lagou API returned OK but no results. Msg: {data.get('msg')}")
                    
                for item in result_list:
                    jd_url = f"https://www.lagou.com/jobs/{item.get('positionId')}.html"
                    jd_content = self.extract_fallback_jd(item)
                    if self.enable_detail_fetch:
                        detail_jd = self.fetch_jd_content(
                            jd_url=jd_url,
                            referer=self.referer_url,
                            throttle_host="lagou.com",
                            throttle_seconds=self.detail_throttle_seconds
                        )
                        if detail_jd:
                            jd_content = detail_jd
                    job_description, job_requirement = self.split_jd_sections(jd_content)
                    labels = item.get("positionLables") or item.get("positionLabels") or []
                    parsed_job = self.format_data(
                        job_name=item.get('positionName', ''),
                        company_name=item.get('companyFullName', ''),
                        location=f"上海{item.get('district', '')}",
                        salary=item.get('salary', ''),
                        job_type="实习",
                        jd_url=jd_url,
                        jd_content=jd_content,
                        publish_date=item.get('createTime', ''),
                        job_description=job_description,
                        job_requirement=job_requirement,
                        city="上海",
                        district=item.get("district", ""),
                        employment_type="实习",
                        experience_requirement=item.get("workYear", ""),
                        education_requirement=item.get("education", ""),
                        source_job_id=item.get("positionId", ""),
                        source_keyword=keyword,
                        job_tags=labels,
                        skill_tags=labels,
                        company_industry=item.get("industryField", ""),
                        company_stage=item.get("financeStage", ""),
                        company_size=item.get("companySize", ""),
                        welfare_tags=item.get("positionAdvantage", "")
                    )
                    jobs.append(parsed_job)
                    logger.info(f"Parsed Lagou job: {parsed_job['job_name']} @ {parsed_job['company_name']}")
            else:
                logger.error(f"Lagou API returned error: {data.get('msg')}")
        except Exception as e:
            logger.error(f"Lagou parse error: {e}")
        return jobs

    def extract_fallback_jd(self, item):
        candidate_parts = []
        for key in ("positionAdvantage", "positionDetail", "industryField"):
            value = item.get(key, "")
            if value:
                candidate_parts.append(str(value))
        labels = item.get("positionLables") or item.get("positionLabels") or []
        if isinstance(labels, list) and labels:
            candidate_parts.append("；".join([str(x) for x in labels if x]))
        return self.normalize_jd_text("\n".join(candidate_parts))

    def seed_fallback_jobs(self, keywords):
        seeds = ["后端开发实习生", "前端开发实习生", "算法实习生", "数据分析实习生", "产品经理实习生"]
        jobs = []
        seed_kw = keywords[0] if keywords else "实习"
        for idx, name in enumerate(seeds, 1):
            kd = name.replace(" ", "")
            jd_url = f"https://www.lagou.com/wn/jobs?kd={kd}&city=%E4%B8%8A%E6%B5%B7&seed={idx}"
            jobs.append(self.format_data(
                job_name=name,
                company_name="",
                location="上海",
                salary="",
                job_type="实习",
                jd_url=jd_url,
                jd_content=f"岗位方向: {name}\n城市: 上海\n来源: 拉勾搜索回退",
                publish_date="",
                city="上海",
                source_job_id=f"lagou_seed_{idx}",
                source_keyword=seed_kw,
                employment_type="实习"
            ))
        logger.info(f"Lagou seed fallback generated {len(jobs)} jobs")
        return jobs
