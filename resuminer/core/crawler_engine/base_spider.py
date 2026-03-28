import time
import random
import logging
import re
from datetime import datetime
from bs4 import BeautifulSoup
from resuminer.core.crawler_engine.fetcher import Fetcher
from resuminer.core.crawler_engine.scheduler import RedisScheduler

logger = logging.getLogger(__name__)

class BaseSpider:
    STANDARD_FIELDS = [
        "job_name",
        "company_name",
        "location",
        "city",
        "district",
        "salary",
        "salary_min",
        "salary_max",
        "salary_unit",
        "salary_count",
        "job_type",
        "employment_type",
        "experience_requirement",
        "education_requirement",
        "platform",
        "source_job_id",
        "source_keyword",
        "jd_url",
        "jd_content",
        "job_description",
        "job_requirement",
        "job_tags",
        "skill_tags",
        "company_industry",
        "company_stage",
        "company_size",
        "welfare_tags",
        "publish_date",
        "crawl_time"
    ]

    def __init__(self, platform_name: str, scheduler: RedisScheduler, cookie: str = ""):
        self.platform_name = platform_name
        self.scheduler = scheduler
        self.base_cookie = cookie
        
        # 默认使用 chrome120 伪装 TLS
        self.impersonate = "chrome120"
        initial_proxy = self.scheduler.get_proxy()
        self.fetcher = Fetcher(proxy=initial_proxy, impersonate=self.impersonate)

    def get_headers(self):
        """生成基础请求头"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        if self.base_cookie:
            headers['Cookie'] = self.base_cookie
        return headers

    def format_data(
        self,
        job_name,
        company_name,
        location,
        salary,
        job_type,
        jd_url,
        jd_content,
        publish_date,
        job_description="",
        job_requirement="",
        **extra_fields
    ):
        record = {k: "" for k in self.STANDARD_FIELDS}
        normalized_jd = self.normalize_jd_text(jd_content)
        normalized_desc = self.normalize_jd_text(job_description)
        normalized_req = self.normalize_jd_text(job_requirement)
        if normalized_jd and (not normalized_desc and not normalized_req):
            normalized_desc, normalized_req = self.split_jd_sections(normalized_jd)
        if not normalized_jd:
            normalized_jd = self.normalize_jd_text(
                "\n".join([x for x in [normalized_desc, normalized_req] if x])
            )
        city, district = self.parse_location_fields(location)
        salary_min, salary_max, salary_unit, salary_count = self.parse_salary_fields(salary)
        record.update({
            "job_name": self.safe_value(job_name),
            "company_name": self.safe_value(company_name),
            "location": self.safe_value(location),
            "city": city,
            "district": district,
            "salary": self.safe_value(salary),
            "salary_min": salary_min,
            "salary_max": salary_max,
            "salary_unit": salary_unit,
            "salary_count": salary_count,
            "job_type": self.safe_value(job_type),
            "employment_type": self.safe_value(job_type),
            "platform": self.platform_name,
            "jd_url": self.safe_value(jd_url),
            "jd_content": normalized_jd,
            "job_description": normalized_desc,
            "job_requirement": normalized_req,
            "publish_date": self.safe_value(publish_date),
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        for key, value in extra_fields.items():
            if key in {"salary_min", "salary_max", "salary_unit", "salary_count"}:
                record[key] = self.safe_value(value)
                continue
            if isinstance(value, list):
                record[key] = "|".join([self.safe_value(x) for x in value if self.safe_value(x)])
                continue
            record[key] = self.safe_value(value)
        if not record.get("city"):
            record["city"] = city
        if not record.get("district"):
            record["district"] = district
        if not record.get("job_tags"):
            record["job_tags"] = self.safe_value(record.get("welfare_tags"))
        return record

    def parse_cookie_str(self, cookie_str):
        """将 Cookie 字符串转换为字典"""
        d = {}
        if not cookie_str:
            return d
        for item in cookie_str.split(';'):
            if '=' in item:
                k, v = item.split('=', 1)
                d[k.strip()] = v.strip()
        return d

    def normalize_jd_text(self, text: str, max_chars: int = 4000):
        if not text:
            return ""
        lines = []
        for line in text.replace("\r", "\n").split("\n"):
            cleaned = " ".join(line.split())
            if cleaned:
                lines.append(cleaned)
        if not lines:
            return ""
        merged = "\n".join(lines)
        return merged[:max_chars]

    def safe_value(self, value):
        if value is None:
            return ""
        return str(value).strip()

    def parse_location_fields(self, location: str):
        text = self.safe_value(location)
        if not text:
            return "", ""
        city = ""
        district = ""
        if "上海" in text:
            city = "上海"
        district_match = re.search(r"([\u4e00-\u9fa5]{1,10}区)", text)
        if district_match:
            district = district_match.group(1)
        if not city:
            m = re.search(r"([\u4e00-\u9fa5]{2,8})(?:市|[\-·/\s])", text)
            if m:
                city = m.group(1)
        return city, district

    def parse_salary_fields(self, salary: str):
        text = self.safe_value(salary).lower().replace(" ", "")
        if not text:
            return "", "", "", ""
        unit = ""
        for token in ["万/年", "万/月", "元/天", "元/月", "k/月", "k", "/天", "/月", "/年"]:
            if token in text:
                unit = token
                break
        range_match = re.search(r"(\d+(?:\.\d+)?)\s*[-~至]\s*(\d+(?:\.\d+)?)", text)
        if range_match:
            return range_match.group(1), range_match.group(2), unit, ""
        single_match = re.search(r"(\d+(?:\.\d+)?)", text)
        if single_match:
            return single_match.group(1), single_match.group(1), unit, ""
        return "", "", unit, ""

    def extract_jd_content_from_html(self, html_text: str):
        if not html_text:
            return ""
        soup = BeautifulSoup(html_text, "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        selectors = [
            "[class*='job-detail']",
            "[class*='jobdetail']",
            "[class*='job_description']",
            "[class*='description']",
            "[class*='content']",
            "[id*='job-detail']",
            "[id*='description']",
            "[id*='detail']",
            "main",
            "article"
        ]
        for selector in selectors:
            blocks = soup.select(selector)
            for block in blocks:
                text = self.normalize_jd_text(block.get_text("\n", strip=True))
                if len(text) >= 40:
                    return text
        return self.normalize_jd_text(soup.get_text("\n", strip=True))

    def fetch_jd_content(self, jd_url: str, referer: str = "", throttle_host: str = "", throttle_seconds: float = 1.0):
        if not jd_url:
            return ""
        try:
            if throttle_host:
                self.scheduler.throttle(throttle_host, throttle_seconds)
            headers = self.get_headers()
            headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            if referer:
                headers["Referer"] = referer
            response = self.fetcher.request("GET", jd_url, headers=headers, timeout=15, allow_redirects=True)
            if getattr(response, "status_code", 0) >= 400:
                return ""
            content_type = (response.headers.get("Content-Type") or "").lower()
            if "html" not in content_type and "text" not in content_type:
                return ""
            return self.extract_jd_content_from_html(response.text)
        except Exception as e:
            logger.warning(f"Failed to fetch JD detail url={jd_url}: {e}")
            return ""

    def split_jd_sections(self, jd_text: str):
        """增强版 JD 内容分割，提高任职要求提取率"""
        text = self.normalize_jd_text(jd_text)
        if not text:
            return "", ""

        compact_text = text.replace(" ", "")
        placeholder_tokens = ["详情需进入页面提取", "详情需访问链接", "官网未提供", "暂无"]
        if any(token in compact_text for token in placeholder_tokens):
            return "", ""

        desc_markers = [
            "岗位职责", "工作职责", "职位描述", "你将负责", "工作内容",
            "职责描述", "职责范围", "岗位描述", "工作描述", "职位介绍",
            "岗位介绍", "关于角色", "role description", "what you'll do",
            "工作说明", "职能描述", "role", "responsibilities",
            "职位职责", "工作职能", "职能范围", "岗位职能"
        ]
        req_markers = [
            "任职要求", "岗位要求", "职位要求", "我们希望你", "任职资格",
            "能力要求", "任职条件", "资格要求", "岗位资格", "招聘要求",
            "应聘条件", "必备条件", "希望你具备", "requirements", "who you are",
            "我们需要你", "期待你", "候选人要求", "人才要求", "应聘要求",
            "岗位需求", "职位需求", "技能要求", "专业要求",
            # 猎聘常见标记
            "任职资格", "优先条件", "必备技能", "技能要求",
            "学历要求", "经验要求", "工作年限", "优先",
            "希望你", "期待你", "需要你"
        ]

        normalized = text.replace("：", ":").replace("【", "").replace("】", "").replace("「", "").replace("」", "")
        lines = [line.strip() for line in normalized.split("\n") if line.strip()]

        desc_lines = []
        req_lines = []
        mode = None

        for line in lines:
            compact = line.replace(" ", "").replace(":", "").lower()

            if any(marker in compact for marker in [m.replace(" ", "").lower() for m in desc_markers]):
                mode = "desc"
                continue

            if any(marker in compact for marker in [m.replace(" ", "").lower() for m in req_markers]):
                mode = "req"
                continue

            if mode == "req":
                req_lines.append(line)
            elif mode == "desc":
                desc_lines.append(line)

        if not desc_lines and not req_lines:
            return self._smart_split_jd(text)

        desc = self.normalize_jd_text("\n".join(desc_lines))
        req = self.normalize_jd_text("\n".join(req_lines))

        if desc and not req:
            return desc, ""
        if req and not desc:
            return "", req

        return desc, req

    def _smart_split_jd(self, text: str):
        """智能分割：当没有明确标记时，基于段落特征分割"""
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        if len(paragraphs) <= 2:
            return text, ""

        mid = len(paragraphs) // 2
        desc = self.normalize_jd_text("\n".join(paragraphs[:mid]))
        req = self.normalize_jd_text("\n".join(paragraphs[mid:]))

        return desc, req

    def run(self):
        raise NotImplementedError("Subclasses must implement run method")

    def parse(self, response):
        raise NotImplementedError("Subclasses must implement parse method")
