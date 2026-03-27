from __future__ import annotations

# 该文件为唯一需要修改的配置入口：企业梯队、平台开关、抓取规则、增量与输出格式都在这里调整。
# 核心代码不建议直接改动，便于后续升级与复用。

import os
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class CompanyConfig:
    name: str
    level: str
    aliases: List[str]
    campus_url: Optional[str] = None
    social_url: Optional[str] = None


@dataclass(frozen=True)
class TierConfig:
    level: str
    companies: List[CompanyConfig]


TIERS: List[TierConfig] = [
    TierConfig(
        level="S",
        companies=[
            CompanyConfig("腾讯", "S", ["腾讯", "Tencent"], None, None),
            CompanyConfig("阿里巴巴", "S", ["阿里", "阿里巴巴", "Alibaba"], None, None),
            CompanyConfig("百度", "S", ["百度", "Baidu"], None, None),
            CompanyConfig("字节跳动", "S", ["字节", "字节跳动", "ByteDance"], "https://jobs.bytedance.com/campus/position", "https://jobs.bytedance.com/experienced/position"),
        ],
    ),
    TierConfig(
        level="A",
        companies=[
            CompanyConfig("美团", "A", ["美团", "Meituan"], None, None),
            CompanyConfig("拼多多", "A", ["拼多多", "PDD", "Pinduoduo"], None, None),
            CompanyConfig("京东", "A", ["京东", "JD", "JD.com"], None, None),
            CompanyConfig("网易", "A", ["网易", "NetEase"], None, None),
            CompanyConfig("快手", "A", ["快手", "Kuaishou"], None, None),
            CompanyConfig("滴滴出行", "A", ["滴滴", "滴滴出行", "DiDi"], None, None),
        ],
    ),
    TierConfig(
        level="B",
        companies=[
            CompanyConfig("B站", "B", ["B站", "哔哩哔哩", "Bilibili"], None, None),
            CompanyConfig("小红书", "B", ["小红书", "XHS"], None, None),
            CompanyConfig("小米", "B", ["小米", "Xiaomi"], None, None),
            CompanyConfig("携程", "B", ["携程", "Ctrip"], None, None),
            CompanyConfig("金山软件", "B", ["金山", "金山软件", "Kingsoft"], None, None),
            CompanyConfig("360", "B", ["360", "奇虎360", "Qihoo"], None, None),
            CompanyConfig("蚂蚁集团", "B", ["蚂蚁", "蚂蚁集团", "Ant Group"], None, None),
            CompanyConfig("阿里云", "B", ["阿里云", "Alibaba Cloud"], None, None),
            CompanyConfig("腾讯云", "B", ["腾讯云", "Tencent Cloud"], None, None),
            CompanyConfig("华为云", "B", ["华为云", "Huawei Cloud"], None, None),
        ],
    ),
    TierConfig(
        level="C",
        companies=[
            CompanyConfig("米哈游", "C", ["米哈游", "miHoYo"], None, None),
            CompanyConfig("Shein", "C", ["Shein", "SHEIN"], None, None),
            CompanyConfig("得物", "C", ["得物", "Poizon"], None, None),
            CompanyConfig("知乎", "C", ["知乎", "Zhihu"], None, None),
            CompanyConfig("喜马拉雅", "C", ["喜马拉雅", "Ximalaya"], None, None),
            CompanyConfig("货拉拉", "C", ["货拉拉", "Lalamove"], None, None),
            CompanyConfig("完美世界", "C", ["完美世界", "Perfect World"], None, None),
            CompanyConfig("三七互娱", "C", ["三七互娱", "37互娱", "37 Interactive"], None, None),
        ],
    ),
]


PLATFORMS: Dict[str, bool] = {
    "official": False,
    "nowcoder": True,
    "boss_zhipin": False,
    "shixiseng": True,
    "lagou": False,
    "liepin": True,
    "51job": False,
    "zhaopin": False,
}


NOWCODER_ENTERPRISE_URLS: Dict[str, str] = {
    "腾讯": "https://www.nowcoder.com/enterprise/138",
    "阿里巴巴": "https://www.nowcoder.com/enterprise/134",
    "百度": "https://www.nowcoder.com/enterprise/139",
    "字节跳动": "https://www.nowcoder.com/enterprise/665",
    "美团": "https://www.nowcoder.com/enterprise/256",
    "拼多多": "https://www.nowcoder.com/enterprise/323",
    "京东": "https://www.nowcoder.com/enterprise/155",
    "网易": "https://www.nowcoder.com/enterprise/147",
    "快手": "https://www.nowcoder.com/enterprise/1061",
    "滴滴出行": "https://www.nowcoder.com/enterprise/235",
    "B站": "https://www.nowcoder.com/enterprise/318",
    "哔哩哔哩": "https://www.nowcoder.com/enterprise/318",
    "小红书": "https://www.nowcoder.com/enterprise/1193",
    "小米": "https://www.nowcoder.com/enterprise/159",
    "携程": "https://www.nowcoder.com/enterprise/263",
    "金山软件": "https://www.nowcoder.com/enterprise/215",
    "360": "https://www.nowcoder.com/enterprise/201",
    "奇虎360": "https://www.nowcoder.com/enterprise/201",
    "蚂蚁集团": "https://www.nowcoder.com/enterprise/1447",
    "阿里云": "https://www.nowcoder.com/enterprise/134",
    "腾讯云": "https://www.nowcoder.com/enterprise/138",
    "华为云": "https://www.nowcoder.com/enterprise/1077",
    "米哈游": "https://www.nowcoder.com/enterprise/836",
    "Shein": "https://www.nowcoder.com/enterprise/1713",
    "得物": "https://www.nowcoder.com/enterprise/1110",
    "知乎": "https://www.nowcoder.com/enterprise/400",
    "喜马拉雅": "https://www.nowcoder.com/enterprise/414",
    "货拉拉": "https://www.nowcoder.com/enterprise/1040",
    "完美世界": "https://www.nowcoder.com/enterprise/193",
    "三七互娱": "https://www.nowcoder.com/enterprise/422",
}


CRAWL_RULES: Dict[str, object] = {
    "headless": os.getenv("HEADLESS", "0") == "1",
    "request_delay_range_s": (1.5, 3.5),
    "retry_times": 2,
    "max_pages_per_source": 5,
    "max_jobs_per_source": 1000,
    "location_whitelist": ["上海"],
    "recruit_types_enabled": ["校招", "社招", "实习", "暑期实习"],
}

THIRD_PARTY_MODE = "whitelist_first"

BLACKLIST_COMPANIES = {
    "字节跳动",
    "腾讯",
    "阿里巴巴",
    "百度",
    "美团",
    "拼多多",
    "京东",
    "网易",
    "快手",
    "滴滴出行",
    "蚂蚁集团",
    "阿里云",
    "腾讯云",
}

WHITELIST_FOREIGN = {
    "西门子",
    "博世",
    "施耐德电气",
    "英伟达",
    "亚马逊",
    "SAP",
    "微软",
    "英特尔",
}

WHITELIST_UNICORN = {
    "米哈游",
    "小红书",
    "得物",
    "商汤科技",
    "沐瞳科技",
    "UCloud",
    "壁仞科技",
}

WHITELIST_SOE_TECH = {
    "上海电气",
    "上海联和",
    "上海仪电",
}

LIEPIN_SEARCH_KEYWORDS = [
    "27届校招 上海",
    "2027届校招 上海",
    "27届秋招 上海",
    "2027届秋招 上海",
    "27届实习 上海",
    "2027届实习 上海",
    "27届暑期实习 上海",
    "2027届暑期实习 上海",
    "26届校招补录 上海",
    "2026届校招补录 上海",
    "应届毕业生 上海",
    "2027毕业 上海",
    "2026毕业 上海",
    "校招 上海",
    "秋招 上海",
    "实习 上海",
    "后端开发 校招 上海",
    "Go开发 校招 上海",
    "产品经理 校招 上海",
    "产品运营 校招 上海",
    "数据分析师 校招 上海",
    "数据工程师 校招 上海",
    "算法工程师 校招 上海",
]

LIEPIN_PAGES_PER_KEYWORD = 3

LIEPIN_REQUEST_INTERVAL = {"min": 3, "max": 5}

LIEPIN_RUN_MODE = "connect_cdp"

LIEPIN_CDP_ADDRESS = "http://localhost:9222"

LIEPIN_HEADLESS = False

LIEPIN_PAGES_PER_URL = 3

LIEPIN_SCROLL_TIMES_PER_PAGE = 3

LIEPIN_PAGE_STAY_SECONDS = {"min": 2, "max": 4}

LIEPIN_DETAIL_FETCH_LIMIT = 50

LIEPIN_JOB_API_KEYWORDS = ["liepin.com/zhaopin/position", "api-c.liepin.com", "searchfront4c", "jobList"]

LIEPIN_FILTER_PRESETS = [
    {"label": "应届默认", "workYearCode": "1", "recruitTime": "", "salary": "", "compNature": "", "financing": "", "compScale": ""},
    {"label": "实习默认", "workYearCode": "2", "recruitTime": "", "salary": "", "compNature": "", "financing": "", "compScale": ""},
    {"label": "近一月应届", "workYearCode": "1", "recruitTime": "30", "salary": "", "compNature": "", "financing": "", "compScale": ""},
    {"label": "外资合资应届", "workYearCode": "1", "recruitTime": "", "salary": "", "compNature": "010|020", "financing": "", "compScale": ""},
    {"label": "独角兽上市", "workYearCode": "1", "recruitTime": "", "salary": "", "compNature": "", "financing": "080|090|100", "compScale": ""},
    {"label": "中大型企业", "workYearCode": "1", "recruitTime": "", "salary": "", "compNature": "", "financing": "", "compScale": "2000|5000|10000"},
]

LIEPIN_PAGES_PER_PRESET = 3

LIEPIN_DETAIL_ENRICH_LIMIT = 80

LIEPIN_MAX_LINKS_PER_PAGE = 220

LIEPIN_ALLOWED_RECRUIT_TYPES = ["校招", "秋招", "提前批", "实习"]

PLATFORM_SEARCH_RULES: Dict[str, dict] = {
    "shixiseng": {
        "entry_urls": [
            "https://www.shixiseng.com/interns",
            "https://www.shixiseng.com/jobs",
        ],
        "city": "上海",
        "graduate_years": ["2027", "2026"],
        "recruit_keywords": ["实习", "秋招", "提前批", "校招", "补录", "应届"],
        "publish_days": 180,
        "industries": ["互联网", "科技", "金融", "硬科技", "企业服务"],
        "pages": 40,
        "request_interval_seconds": 2.0,
        "api_candidates": [
            "https://www.shixiseng.com/interns/search",
            "https://www.shixiseng.com/api/v1/interns",
            "https://www.shixiseng.com/api/v2/interns",
            "https://www.shixiseng.com/api/interns",
        ],
    },
    "liepin": {
        "entry_urls": [
            "https://www.liepin.com/zhaopin/",
            "https://www.liepin.com/campus/",
        ],
        "city": "上海",
        "graduate_years": ["2027", "2026"],
        "recruit_keywords": ["应届", "校招", "实习", "管培", "提前批", "秋招"],
        "publish_days": 180,
        "industries": ["互联网", "科技", "金融", "硬科技"],
        "company_nature": ["外资", "合资", "民营"],
        "pages": 40,
        "request_interval_seconds": 3.0,
        "run_mode": LIEPIN_RUN_MODE,
        "cdp_address": LIEPIN_CDP_ADDRESS,
        "headless": LIEPIN_HEADLESS,
        "pages_per_url": LIEPIN_PAGES_PER_URL,
        "scroll_times_per_page": LIEPIN_SCROLL_TIMES_PER_PAGE,
        "page_stay_seconds": LIEPIN_PAGE_STAY_SECONDS,
        "search_keywords": LIEPIN_SEARCH_KEYWORDS,
        "pages_per_keyword": LIEPIN_PAGES_PER_KEYWORD,
        "request_interval": LIEPIN_REQUEST_INTERVAL,
        "filter_presets": LIEPIN_FILTER_PRESETS,
        "pages_per_preset": LIEPIN_PAGES_PER_PRESET,
        "detail_limit": LIEPIN_DETAIL_FETCH_LIMIT,
        "max_links_per_page": LIEPIN_MAX_LINKS_PER_PAGE,
        "allowed_recruit_types": LIEPIN_ALLOWED_RECRUIT_TYPES,
        "job_api_keywords": LIEPIN_JOB_API_KEYWORDS,
        "api_candidates": [
            "https://api-c.liepin.com/api/com.liepin.searchfront4c.pc-search-job",
            "https://www.liepin.com/api/com.liepin.searchfront4c.pc-search-job",
            "https://www.liepin.com/api/job/search",
        ],
    },
}

# ====================== 第三方平台登录态配置 ======================
# 实习僧Cookie：浏览器登录实习僧后，F12开发者工具→Network→任意请求→复制Request Headers里的Cookie完整内容
SHIXISENG_COOKIE = "__jsluid_s=e54253aae59efd9d04018f4576c5ce6b; utm_source_first=PC; utm_source=PC; utm_campaign=PC; position=pc_default; Hm_lvt_03465902f492a43ee3eb3543d81eba55=1773847704; Hm_lpvt_03465902f492a43ee3eb3543d81eba55=1773847704; HMACCOUNT=CAEDB54954793AAA"
# 猎聘Cookie：浏览器登录猎聘后，同上操作复制完整Cookie
LIEPIN_COOKIE = "inited_user=66dfbc382ab19a7e5346c6a285bcc743; XSRF-TOKEN=pgG6UPHVQXKa-q5Q-90O1g; __uuid=1773901243763.46; __sessionId=1773901243775.48; acw_tc=7b3975b817739012444566879e53fd7f615fa7c298ce7af9b5dcf1d41f758b; __gc_id=2962bae08254434dbf7400d63981b1a7; UniqueKey=986a21b6ef39fa4a7ecd4408bb1e9b04; liepin_login_valid=0; lt_auth=uO8JO3BUzg387XWI3DZbsq9Fh96rVWTBon9e0BoDgd67WfXm4PziRg%2BOrrUA%2FCoIq05zcfkzMLf5NuH%2ByHBI6UMR%2FFGnlJeuv%2Fm9z30DSvpnLsW2vezHg%2FXUQp4hk0AA8nJbpEIL%2BVzO; access_system=C; hpo_role-sec_project=sec_project_liepin; hpo_sec_tenant=0; Hm_lvt_a2647413544f5a04f00da7eee0d5e200=1773901324; HMACCOUNT=34C687B2BBBE45E9; user_roles=0; need_bind_tel=false; new_user=true; c_flag=bb37a295995fdc3a63eb2e4d3048eeae; user_photo=5f8fa3a9dfb13a7dee343d4808u.png; user_name=%E5%94%90%E5%9C%A3%E6%98%95; Hm_lpvt_a2647413544f5a04f00da7eee0d5e200=1773901696; __session_seq=9; __tlg_event_seq=112"
# 平台请求间隔配置（严格遵守反爬要求）
REQUEST_INTERVAL = {
    "shixiseng": 2.0,
    "liepin": 3.0,
}


INCREMENTAL: Dict[str, object] = {
    "enabled": True,
    "state_file": "output/state.json",
    "default_since_days": 30,
    "apply_publish_time_filter_sources": ["bytedance_official", "shixiseng", "liepin"],
}


OUTPUT: Dict[str, object] = {
    "dir": "output",
    "latest_excel": "output/jobs_latest.xlsx",
    "latest_csv": "output/jobs_latest.csv",
    "latest_json": "output/jobs_latest.json",
    "excel_by_tier_sheet": True,
    "keep_history": os.getenv("KEEP_HISTORY", "0") == "1",
}
