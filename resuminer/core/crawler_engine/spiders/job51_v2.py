import logging
import os
import json
import random
import re
import time
from datetime import datetime, timedelta
from resuminer.core.crawler_engine.base_spider import BaseSpider
from resuminer.core.crypto_engine.platforms.job51 import Job51Crypto

logger = logging.getLogger(__name__)

class Job51SpiderV2(BaseSpider):
    def __init__(self, scheduler, base_cookie: str = ""):
        super().__init__("前程无忧", scheduler, base_cookie)
        self.crypto = Job51Crypto()
        self.job_area = os.getenv("JOB51_JOB_AREA", "020000")
        self.primary_keywords = self.split_words(os.getenv("JOB51_CAMPUS_KEYWORDS", "实习,日常实习,暑期实习"))
        self.intern_keywords = self.split_words(os.getenv("JOB51_INTERN_KEYWORDS", "实习,日常实习,暑期实习"))
        self.fallback_keywords = self.split_words(os.getenv("JOB51_FALLBACK_KEYWORDS", "实习"))
        self.max_safety_pages = int(os.getenv("JOB51_MAX_SAFETY_PAGES", "300"))
        self.page_size = int(os.getenv("JOB51_PAGE_SIZE", "20"))
        self.empty_streak_limit = int(os.getenv("JOB51_EMPTY_STREAK_LIMIT", "3"))
        self.throttle_min_seconds = float(os.getenv("JOB51_THROTTLE_MIN_SECONDS", "3"))
        self.throttle_max_seconds = float(os.getenv("JOB51_THROTTLE_MAX_SECONDS", "12"))
        self.enable_detail_fetch = os.getenv("JOB51_FETCH_JD_DETAIL", "1") == "1"
        self.detail_throttle_min_seconds = float(os.getenv("JOB51_DETAIL_THROTTLE_MIN_SECONDS", "3"))
        self.detail_throttle_max_seconds = float(os.getenv("JOB51_DETAIL_THROTTLE_MAX_SECONDS", "8"))
        self.max_retry = int(os.getenv("JOB51_MAX_RETRY", "3"))
        self.target_min_count = int(os.getenv("JOB51_TARGET_MIN_COUNT", "3000"))
        self.require_scope_filter = os.getenv("JOB51_SCOPE_FILTER_ENABLED", "1") == "1"
        self.require_recent_days_first = int(os.getenv("JOB51_RECENT_DAYS_FIRST", "0"))
        self.require_recent_days_fallback = int(os.getenv("JOB51_RECENT_DAYS_FALLBACK", "0"))
        self.intern_terms = self.split_words(os.getenv("JOB51_INTERN_TERMS", "实习,日常实习,暑期实习,在校"))
        self.remote_exclude_terms = self.split_words(os.getenv("JOB51_REMOTE_EXCLUDE_TERMS", "纯远程,远程办公,全国轮岗,异地办公,居家办公"))
        self.active_status_terms = self.split_words(os.getenv("JOB51_ACTIVE_STATUS_TERMS", "招聘中,正在招聘,急聘,热招"))
        self.inactive_status_terms = self.split_words(os.getenv("JOB51_INACTIVE_STATUS_TERMS", "已下线,停止招聘,已结束,过期,暂停招聘"))
        self.checkpoint_path = os.getenv("JOB51_CHECKPOINT_PATH", os.path.join("output", "job51_checkpoint.json"))
        self.resume_from_checkpoint = os.getenv("JOB51_RESUME_FROM_CHECKPOINT", "1") == "1"

    def run(self):
        logger.info("Starting Job51Spider V2 (Shanghai IT campus/intern mode)...")
        return self.run_with_day_window(self.require_recent_days_first)

    def run_with_day_window(self, recent_days: int):
        all_jobs = []
        entry_groups = [
            ("intern", self.intern_keywords),
            ("fallback", self.fallback_keywords)
        ]
        checkpoint = self.load_checkpoint()
        for entry_name, keywords in entry_groups:
            for keyword in keywords:
                ck_key = self.build_checkpoint_key(entry_name, keyword, recent_days)
                start_page = 1
                request_id = ""
                if self.resume_from_checkpoint and ck_key in checkpoint:
                    saved = checkpoint.get(ck_key) or {}
                    saved_page = int(saved.get("page", 0) or 0)
                    if saved_page > 0:
                        start_page = saved_page + 1
                    request_id = str(saved.get("request_id", "") or "")
                    logger.info(f"Job51 resume checkpoint key={ck_key} start_page={start_page} request_id={request_id}")
                logger.info(f"Start 51job crawl entry={entry_name}, keyword={keyword}, days={recent_days}")
                empty_streak = 0
                page = start_page
                page_guard = 0
                while True:
                    page_guard += 1
                    if page_guard > self.max_safety_pages:
                        logger.info(f"Stop by max safety pages for keyword={keyword}")
                        break
                    self.scheduler.throttle("we.51job.com", random.uniform(self.throttle_min_seconds, self.throttle_max_seconds))
                    retry_count = 0
                    data = None
                    while retry_count < self.max_retry:
                        try:
                            data = self.crypto.search_jobs(
                                keyword=keyword,
                                page_num=page,
                                cookie_str=self.base_cookie,
                                job_area=self.job_area,
                                page_size=self.page_size,
                                request_id=request_id
                            )
                            if isinstance(data, dict) and data.get("blocked"):
                                retry_count += 1
                                time.sleep(random.uniform(self.throttle_min_seconds, self.throttle_max_seconds))
                                continue
                            break
                        except Exception as e:
                            retry_count += 1
                            logger.error(f"51job request failed keyword={keyword} page={page} retry={retry_count}: {e}")
                            time.sleep(random.uniform(self.throttle_min_seconds, self.throttle_max_seconds))
                    if data is None:
                        break
                    if isinstance(data, dict) and data.get("blocked"):
                        logger.error(f"51job blocked after retry keyword={keyword} page={page}")
                        break
                    jobs, current_request_id = self.parse_json(
                        data=data,
                        keyword=keyword,
                        recent_days=recent_days,
                        entry_name=entry_name
                    )
                    if current_request_id:
                        request_id = current_request_id
                    if jobs:
                        all_jobs.extend(jobs)
                        empty_streak = 0
                    else:
                        empty_streak += 1
                    self.save_checkpoint(
                        checkpoint,
                        ck_key=ck_key,
                        page=page,
                        request_id=request_id
                    )
                    if empty_streak >= self.empty_streak_limit:
                        logger.info(f"51job stop by empty streak keyword={keyword}, page={page}")
                        break
                    page += 1
        logger.info(f"Job51 day window result days={recent_days} count={len(all_jobs)}")
        return all_jobs

    def build_checkpoint_key(self, entry_name: str, keyword: str, recent_days: int):
        return f"{entry_name}|{keyword}|{recent_days}"

    def load_checkpoint(self):
        if not self.resume_from_checkpoint:
            return {}
        try:
            if os.path.exists(self.checkpoint_path):
                with open(self.checkpoint_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
        except Exception as e:
            logger.warning(f"Job51 checkpoint load failed: {e}")
        return {}

    def save_checkpoint(self, checkpoint: dict, ck_key: str, page: int, request_id: str):
        if not self.resume_from_checkpoint:
            return
        checkpoint[ck_key] = {
            "page": page,
            "request_id": request_id,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        try:
            os.makedirs(os.path.dirname(self.checkpoint_path), exist_ok=True)
            with open(self.checkpoint_path, "w", encoding="utf-8") as f:
                json.dump(checkpoint, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Job51 checkpoint save failed: {e}")

    def parse_json(self, data, keyword: str = "", recent_days: int = 90, entry_name: str = ""):
        jobs = []
        request_id = ""
        try:
            if not isinstance(data, dict):
                return jobs, request_id
            body = data.get("resultbody", {})
            request_id = body.get("requestId", "")
            job_container = body.get("job", {})
            items = job_container.get("items") or []
            empty_streak = 0
            filtered_count = 0
            for item in items:
                job_name = item.get("jobName", "")
                company_name = item.get("fullCompanyName", "") or item.get("companyName", "")
                location = item.get("jobAreaString", "")
                salary = item.get("provideSalaryString", "") or item.get("salaryDesc", "")
                jd_url = item.get("jobHref", "")
                jd_content = self.extract_fallback_jd(item)
                company_industry = item.get("industryType1Str", "") or item.get("industryType2Str", "")
                publish_date = item.get("issueDateString", "") or item.get("issueDate", "")
                refresh_time = item.get("updateTime", "") or item.get("refreshTime", "") or publish_date
                if not self.within_days(publish_date, refresh_time, recent_days):
                    filtered_count += 1
                    continue
                if self.enable_detail_fetch:
                    detail_jd = self.fetch_jd_content(
                        jd_url=jd_url,
                        referer="https://we.51job.com/",
                        throttle_host="we.51job.com",
                        throttle_seconds=random.uniform(self.detail_throttle_min_seconds, self.detail_throttle_max_seconds)
                    )
                    if detail_jd:
                        jd_content = detail_jd
                job_description, job_requirement = self.split_jd_sections(jd_content)
                tags = item.get("jobTags") or item.get("tags") or []
                all_text = "\n".join([
                    str(job_name),
                    str(company_name),
                    str(location),
                    str(tags),
                    str(jd_content),
                    str(keyword),
                    str(item.get("jobType", "")),
                    str(item.get("workYearString", "") or item.get("workYear", "")),
                    str(item.get("jobStatusDesc", "") or item.get("jobStatus", ""))
                ]).lower()
                scope_keep = self.should_keep_scope(
                    item=item,
                    all_text=all_text,
                    location=location,
                    job_name=job_name
                )
                if self.require_scope_filter and not scope_keep:
                    filtered_count += 1
                    continue
                company_property = item.get("companyTypeDesc", "") or item.get("companyType", "")
                welfare_tags = item.get("welfareTagList") or tags
                jobs.append(self.format_data(
                    job_name=job_name,
                    company_name=company_name,
                    location=location,
                    salary=salary,
                    job_type=self.infer_job_type(all_text),
                    jd_url=jd_url,
                    jd_content=jd_content,
                    publish_date=publish_date,
                    job_description=job_description,
                    job_requirement=job_requirement,
                    employment_type=item.get("jobType", "") or self.infer_job_type(all_text),
                    experience_requirement=item.get("workYearString", "") or item.get("workYear", ""),
                    education_requirement=item.get("degreeString", "") or item.get("degree", ""),
                    source_job_id=item.get("jobId", ""),
                    source_keyword=keyword,
                    source_entry=entry_name,
                    job_tags=tags,
                    skill_tags=tags,
                    company_industry=company_industry,
                    company_stage=item.get("financingStage", ""),
                    company_size=item.get("companySizeString", ""),
                    welfare_tags=welfare_tags,
                    refresh_time=refresh_time,
                    recruitment_count=item.get("needNumString", "") or item.get("needNum", ""),
                    detail_address=item.get("jobAddress", "") or item.get("jobAreaString", ""),
                    arrival_time_requirement=item.get("arrivalTime", ""),
                    internship_duration=item.get("internshipDuration", "") or item.get("internDuration", ""),
                    direct_apply_url=jd_url,
                    application_email=item.get("email", "") or item.get("contactEmail", ""),
                    company_id=item.get("companyId", ""),
                    company_property=company_property,
                    company_location=item.get("companyAddress", "") or item.get("cityString", ""),
                    company_description=item.get("companyDetail", "") or item.get("companyShortName", ""),
                    job_status=item.get("jobStatusDesc", "") or item.get("jobStatus", ""),
                    is_accept_fresh_graduate=self.bool_by_terms(all_text, ["应届", "校招", "毕业生", "2026届", "2027届"]),
                    is_accept_intern=self.bool_by_terms(all_text, ["实习", "在校", "暑期实习", "日常实习"]),
                    has_shanghai_hukou_quota=self.bool_by_terms(all_text, ["落户", "上海户口", "户口指标", "居转户"]),
                    can_issue_internship_certificate=self.bool_by_terms(all_text, ["实习证明", "开具证明", "可开证明"]),
                    has_return_offer=self.bool_by_terms(all_text, ["转正机会", "留用机会", "可转正"]),
                    provide_food_or_housing=self.bool_by_terms(all_text, ["包食宿", "提供住宿", "餐补", "住房补贴"]),
                    social_insurance=self.bool_by_terms(all_text, ["五险一金", "社保", "公积金"])
                ))
            logger.info(f"Parsed {len(jobs)} jobs from 51job page, filtered={filtered_count}")

            # 字段完整率校验与补齐
            if jobs:
                self._validate_and_enhance_fields(jobs)

        except Exception as e:
            logger.error(f"51job parse error: {e}")
        return jobs, request_id

    def _validate_and_enhance_fields(self, jobs: list):
        """校验并补齐字段，确保任职要求等核心字段完整"""
        if not jobs:
            return

        total = len(jobs)
        req_missing = sum(1 for j in jobs if not j.get("job_requirement"))
        desc_missing = sum(1 for j in jobs if not j.get("job_description"))
        jd_missing = sum(1 for j in jobs if not j.get("jd_content"))

        req_rate = (total - req_missing) / total * 100
        desc_rate = (total - desc_missing) / total * 100
        jd_rate = (total - jd_missing) / total * 100

        logger.info(f"Field validation: total={total}, req_rate={req_rate:.1f}%, desc_rate={desc_rate:.1f}%, jd_rate={jd_rate:.1f}%")

        # 如果任职要求缺失率过高，尝试从 jd_content 重新提取
        if req_missing > 0:
            enhanced_count = 0
            for job in jobs:
                if not job.get("job_requirement") and job.get("jd_content"):
                    jd_content = job["jd_content"]
                    # 重新尝试分割
                    desc, req = self.split_jd_sections(jd_content)
                    
                    # 更新岗位职责
                    if desc and len(desc) > 10:
                        job["job_description"] = desc
                    
                    # 更新任职要求
                    if req and len(req) > 10:
                        job["job_requirement"] = req
                        enhanced_count += 1
                    else:
                        # 兜底策略：将 jd_content 后半部分作为任职要求
                        paragraphs = [p.strip() for p in jd_content.split("\n") if p.strip()]
                        if len(paragraphs) > 1:
                            mid = len(paragraphs) // 2
                            fallback_req = "\n".join(paragraphs[mid:])
                            if len(fallback_req) > 20:
                                job["job_requirement"] = self.normalize_jd_text(fallback_req)
                                enhanced_count += 1
                                logger.debug(f"Applied fallback requirement for job {job.get('source_job_id', 'unknown')}")
                        else:
                            # 如果段落太少，将后半字符作为任职要求
                            mid_char = len(jd_content) // 2
                            if len(jd_content) > 40:
                                job["job_requirement"] = self.normalize_jd_text(jd_content[mid_char:])
                                enhanced_count += 1

            if enhanced_count > 0:
                logger.info(f"Enhanced {enhanced_count} jobs with missing requirements")

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
                        logger.debug(f"Applied fallback requirement for job {job.get('source_job_id', 'unknown')}")

        if fallback_count > 0:
            logger.info(f"Applied fallback strategy to {fallback_count} jobs")

    def extract_fallback_jd(self, item):
        candidate_parts = []
        for key in ("jobDescribe", "jobDescribeText", "jobTags", "jobDescribeJson"):
            value = item.get(key, "")
            if isinstance(value, list):
                value = "；".join([str(x) for x in value if x])
            if value:
                candidate_parts.append(str(value))
        return self.normalize_jd_text("\n".join(candidate_parts))

    def split_words(self, text: str):
        return [x.strip().lower() for x in re.split(r"[,，|/\s]+", str(text)) if x.strip()]

    def contains_any(self, text: str, words):
        if not text:
            return False
        text = str(text).lower()
        for w in words:
            if w and w in text:
                return True
        return False

    def infer_job_type(self, all_text: str):
        if self.contains_any(all_text, ["实习", "暑期实习", "日常实习", "在校"]):
            return "实习生"
        if self.contains_any(all_text, ["应届", "校招", "毕业生", "春招", "秋招", "补录", "2026届", "2027届"]):
            return "应届生校招"
        return "实习生"

    def bool_by_terms(self, all_text: str, words):
        return "1" if self.contains_any(all_text, words) else "0"

    def parse_date_text(self, text: str):
        raw = str(text or "").strip()
        if not raw:
            return None
        now = datetime.now()
        normalized = raw.replace("发布", "").replace("更新", "").replace("/", "-").strip()
        if "今天" in normalized:
            return now
        if "昨天" in normalized:
            return now - timedelta(days=1)
        rel_day = re.search(r"(\d+)\s*天前", normalized)
        if rel_day:
            return now - timedelta(days=int(rel_day.group(1)))
        rel_hour = re.search(r"(\d+)\s*小时前", normalized)
        if rel_hour:
            return now - timedelta(hours=int(rel_hour.group(1)))
        rel_min = re.search(r"(\d+)\s*分钟前", normalized)
        if rel_min:
            return now - timedelta(minutes=int(rel_min.group(1)))
        mmdd = re.search(r"^(\d{1,2})-(\d{1,2})$", normalized)
        if mmdd:
            month = int(mmdd.group(1))
            day = int(mmdd.group(2))
            year = now.year
            try:
                dt = datetime(year, month, day)
                if dt > now + timedelta(days=1):
                    dt = datetime(year - 1, month, day)
                return dt
            except ValueError:
                return None
        for fmt in ("%Y-%m-%d", "%Y.%m.%d", "%Y%m%d"):
            try:
                return datetime.strptime(normalized, fmt)
            except ValueError:
                pass
        return None

    def within_days(self, publish_date: str, refresh_time: str, day_limit: int):
        if day_limit <= 0:
            return True
        now = datetime.now()
        candidates = [self.parse_date_text(publish_date), self.parse_date_text(refresh_time)]
        candidates = [x for x in candidates if x is not None]
        if not candidates:
            return True
        latest = max(candidates)
        return (now - latest).days <= day_limit

    def experience_ok(self, item, all_text: str):
        exp = str(item.get("workYearString", "") or item.get("workYear", "") or "").lower()
        if not exp:
            return True
        allow_terms = ["经验不限", "应届", "在校", "无经验", "1年", "一年", "1年及以下"]
        if any(x in exp for x in allow_terms):
            return True
        reject_patterns = [
            r"[2-9]\s*年",
            r"\d+\s*-\s*\d+\s*年",
            r"\d+\s*年以上"
        ]
        for pattern in reject_patterns:
            if re.search(pattern, exp):
                return False
        if "年" in exp and "1年" not in exp and "一年" not in exp:
            return False
        if self.contains_any(all_text, ["2年以上", "3年以上", "资深", "高级", "专家"]):
            return False
        return True

    def location_ok(self, location: str, all_text: str):
        if "上海" not in str(location) and "上海" not in all_text:
            return False
        if self.contains_any(all_text, self.remote_exclude_terms):
            return False
        if self.contains_any(all_text, ["杭州", "苏州", "南京", "无锡", "昆山", "全国"]):
            if "上海" not in str(location):
                return False
        return True

    def status_ok(self, item, all_text: str):
        status = str(item.get("jobStatusDesc", "") or item.get("jobStatus", "")).lower()
        if status:
            if self.contains_any(status, self.inactive_status_terms):
                return False
            if self.active_status_terms and self.contains_any(status, self.active_status_terms):
                return True
        return not self.contains_any(all_text, self.inactive_status_terms)

    def should_keep_scope(self, item, all_text: str, location: str, job_name: str):
        if not self.location_ok(location, all_text):
            return False
        if not self.contains_any(all_text, self.intern_terms):
            return False
        if not self.status_ok(item, all_text):
            return False
        return True
