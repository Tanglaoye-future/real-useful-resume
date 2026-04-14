import asyncio
import datetime as dt
import glob
import json
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "release_data"
RAW_DIR = ROOT / "data" / "raw"
RPC_BASE = "http://127.0.0.1:5600/invoke"

# Reuse existing URL checker
import sys

sys.path.insert(0, str(ROOT.parent))
from utils.link_checker import check_links_batch  # type: ignore


# 用短关键词提高平台召回，行业和外企属性在过滤与评分阶段识别
KEYWORDS = [
    "实习",
    "数据分析",
    "商业分析",
    "数据科学",
    "BI",
    "Data Analyst",
    "Business Analyst",
    "巴斯夫 实习",
    "西门子 实习",
    "博世 实习",
    "壳牌 实习",
    "辉瑞 实习",
    "罗氏 实习",
]

BIG_TECH_BAN_RE = (
    "字节|腾讯|快手|小红书|美团|阿里|京东|哔哩|"
    "bilibili|bytedance|tencent|kuaishou|xiaohongshu|meituan|alibaba|jingdong|jd\\.com"
)
OUTSOURCE_RE = "外包|驻场|中介|代招|人力资源|劳务派遣|服务外包|猎头"
EN_RE = "english|英语|英文|cet-6|tem-4|fluent"
DATA_ROLE_RE = "数据分析|商业分析|数据科学|bi|data analyst|business analyst|data scientist"
SKILL_RE = "sql|python|tableau|power\\s?bi|pbi|spark|hadoop|sas|r语言|r "
FOREIGN_INCLUDE_RE = (
    "microsoft|google|amazon|apple|oracle|ibm|sap|salesforce|adobe|nvidia|intel|amd|qualcomm|cisco|"
    "linkedin|uber|airbnb|paypal|stripe|shopee|shein|tesla|siemens|bosch|unilever|p&g|jpmorgan|goldman|"
    "morgan stanley|deloitte|pwc|ey|kpmg|accenture|nestle|pepsi|hsbc|standard chartered|"
    "谷歌|微软|亚马逊|苹果|甲骨文|英伟达|英特尔|高通|思科|领英|优步|爱彼迎|贝宝|西门子|博世|联合利华|宝洁|摩根|高盛|德勤|普华永道|安永|毕马威|"
    "巴斯夫|淡水河谷|陶氏|杜邦|必和必拓|力拓|辉瑞|罗氏|诺华|abb|壳牌|bp|埃克森|泰科电子|喜利得|普立万|麦格纳|凯士比|"
    "依必安派特|麦当劳|勘讯|analyt(ic|ic) partners|ebm-papst|"
    "阿斯利康|礼来|诺和诺德|赛默飞|丹纳赫|拜耳|飞利浦|霍尼韦尔|施耐德|3m|"
    "merck|sanofi|gsk|abbott|boehringer|novo nordisk|astrazeneca|lilly|thermo fisher|danaher|"
    "philips|honeywell|schneider|siemens healthineers|bosch rexroth|byk|evonik|basf|roche|pfizer"
)

WHITELIST_40 = [
    "巴斯夫",
    "淡水河谷",
    "陶氏",
    "杜邦",
    "必和必拓",
    "力拓",
    "辉瑞",
    "罗氏",
    "诺华",
    "西门子",
    "abb",
    "博世",
    "壳牌",
    "bp",
    "埃克森",
]
TIER_38 = ["联合利华", "雀巢", "百事", "可口可乐", "强生", "默沙东", "施耐德"]
TIER_35 = ["shein", "openai", "anthropic", "shopee"]
TIER_30 = ["微软", "谷歌", "亚马逊", "苹果", "meta", "特斯拉", "麦肯锡", "bcg", "贝恩", "高盛", "摩根士丹利"]
TIER_25 = ["ibm", "sap", "英特尔", "德勤", "毕马威", "埃森哲", "欧莱雅", "汇丰", "渣打", "普华永道", "安永"]


def norm(v) -> str:
    return re.sub(r"\s+", " ", str(v or "")).strip()


def now_str() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def company_score(company_name: str) -> Tuple[int, str, str]:
    name = norm(company_name).lower()
    if any(k.lower() in name for k in WHITELIST_40):
        return 40, "全球行业绝对龙头", "全球Top3/白名单"
    if any(k.lower() in name for k in TIER_38):
        return 38, "全球行业前10龙头", "全球Top10"
    if any(k.lower() in name for k in TIER_35):
        return 35, "外资高成长独角兽", "估值>=10亿美元"
    if any(k.lower() in name for k in TIER_30):
        return 30, "一线大厂/咨询/投行", "冲刺档"
    if any(k.lower() in name for k in TIER_25):
        return 25, "二线外企/四大", "保底档"
    if re.search(FOREIGN_INCLUDE_RE, name, re.I):
        return 20, "其他正规外资", "基础档"
    return 0, "非目标公司", "剔除"


def role_score(job_name: str) -> int:
    t = norm(job_name).lower()
    if re.search("数据科学|机器学习|算法|数据挖掘|data scientist|ml|algorithm", t, re.I):
        return 30
    if re.search("商业分析|数据分析|bi|business analyst|data analyst|analytics", t, re.I):
        return 25
    if re.search("数据运营|市场分析|用户分析|增长分析|growth|marketing analyst", t, re.I):
        return 20
    if re.search("产品运营|战略分析|财务分析|strategy|finance analyst", t, re.I):
        return 10
    return 0


def english_score(text: str) -> int:
    t = norm(text).lower()
    if re.search("fluent in english|english as working language|native english", t, re.I):
        return 20
    if re.search("good english|english report|英文汇报|英语沟通|英文沟通", t, re.I):
        return 14
    if re.search("cet-6|tem-4|英语读写|英文阅读", t, re.I):
        return 8
    if re.search(r"[a-zA-Z]{8,}", t):
        return 8
    return 0


def growth_score(text: str) -> int:
    t = norm(text).lower()
    if re.search("独立负责|主导|分析并提出建议|优化|提升|owner|lead", t, re.I):
        return 10
    if re.search("参与|协助|支持|制作报表|分析数据|参与项目", t, re.I):
        return 6
    if re.search("整理|录入|维护|协助团队", t, re.I):
        return 3
    return 0


def priority(total: int) -> str:
    if total >= 75:
        return "核心目标"
    if total >= 70:
        return "优质目标"
    if total >= 60:
        return "保底目标"
    return "过滤"


def split_sentences(text: str) -> List[str]:
    parts = re.split(r"[。；;\n.!?]|\\d+[、.)）]", norm(text))
    return [x.strip() for x in parts if len(x.strip()) >= 6]


def parse_jd_fields(text: str) -> Tuple[str, str]:
    t = norm(text)
    if not t:
        return "", ""
    duties = extract_section(
        t,
        ["岗位职责", "工作职责", "职位描述", "职位职责", "工作内容", "Responsibilities", "Responsibility"],
        ["任职要求", "岗位要求", "职位要求", "任职资格", "Minimum Experience", "Qualifications", "Requirements"],
    )
    reqs = extract_section(
        t,
        ["任职要求", "岗位要求", "职位要求", "任职资格", "Minimum Experience", "Qualifications", "Requirements"],
        ["投递方式", "工作地点", "薪资", "公司介绍", "岗位职责", "Responsibilities", "Responsibility"],
    )
    if not duties and not reqs:
        lines = [x for x in re.split(r"[\n；;。]", t) if len(x.strip()) >= 8]
        # fallback split: front as duties, latter as requirements
        if len(lines) >= 6:
            mid = len(lines) // 2
            duties = "；".join(lines[:mid])
            reqs = "；".join(lines[mid:])
    return norm(duties), norm(reqs)


def infer_intern_type(text: str) -> str:
    t = norm(text)
    if re.search("可转正", t):
        return "可转正实习"
    if re.search("日常实习|长期实习|off-cycle", t, re.I):
        return "日常实习"
    if re.search("校招", t):
        return "校招实习"
    if re.search("暑期|寒假|summer|winter", t, re.I):
        return "季节实习"
    return "实习"


def extract_duration(text: str) -> str:
    t = norm(text)
    m = re.search(r"(每周.{0,8}[天日]|.{0,8}个月|实习.{0,8}月|.{0,8}周以上)", t)
    return m.group(1) if m else ""


def extract_deadline(text: str) -> str:
    t = norm(text)
    m = re.search(r"(20\d{2}[./-]\d{1,2}[./-]\d{1,2}(?:\s*\d{1,2}:\d{2})?)", t)
    return m.group(1) if m else ""


def extract_retention(text: str) -> str:
    t = norm(text)
    m = re.search(r"(.{0,8}(留用|转正).{0,20})", t)
    return m.group(1) if m else ""


def html_to_text(html: str) -> str:
    no_script = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    no_style = re.sub(r"<style[\s\S]*?</style>", " ", no_script, flags=re.I)
    plain = re.sub(r"<[^>]+>", " ", no_style)
    plain = re.sub(r"&nbsp;|&amp;|&lt;|&gt;|&#\d+;", " ", plain)
    return norm(plain)


def extract_section(text: str, starts: List[str], ends: List[str]) -> str:
    lower = text.lower()
    for s in starts:
        i = lower.find(s.lower())
        if i >= 0:
            sub = text[i : i + 1800]
            end_idx = len(sub)
            for e in ends:
                j = sub.lower().find(e.lower())
                if j > 20:
                    end_idx = min(end_idx, j)
            return norm(sub[:end_idx])
    return ""


def fetch_detail(url: str, max_retries: int = 2) -> Tuple[Dict[str, str], str]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    reason = ""
    for attempt in range(max_retries + 1):
        try:
            r = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            html = r.text
            text = html_to_text(html)
            if re.search("验证码|captcha|访问受限|请验证|人机验证", text, re.I):
                reason = "blocked_or_captcha"
                time.sleep(15)
                continue
            if r.status_code >= 400:
                reason = f"http_{r.status_code}"
                time.sleep(1)
                continue
            duties = extract_section(
                text,
                ["岗位职责", "工作职责", "职位描述", "职位职责", "工作内容", "岗位描述"],
                ["任职要求", "岗位要求", "职位要求", "我们希望", "任职资格"],
            )
            reqs = extract_section(
                text,
                ["任职要求", "岗位要求", "职位要求", "任职资格"],
                ["投递方式", "工作地点", "薪资", "公司介绍", "岗位职责"],
            )
            skills = " ".join(sorted(set(re.findall(r"SQL|Python|Tableau|Power BI|SAS|R|Spark|Hadoop", text, flags=re.I))))
            return (
                {
                    "完整职责": duties,
                    "完整要求": reqs,
                    "完整技能": skills,
                    "截止日期": extract_deadline(text),
                    "实习时长": extract_duration(text),
                    "留用机会": extract_retention(text),
                    "详情抓取文本": text[:3000],
                },
                "ok",
            )
        except Exception as e:
            reason = f"exception_{type(e).__name__}"
            time.sleep(1.5)
    return ({}, reason or "unknown_error")


def get_latest_seed_candidates() -> pd.DataFrame:
    # P0 input priority: strict file; fallback to provisional
    strict = OUT_DIR / "foreign_strict_shanghai_opportunities_latest.csv"
    prov = OUT_DIR / "foreign_strict_provisional_candidates_latest.csv"
    if strict.exists():
        df = pd.read_csv(strict).fillna("")
        if len(df) > 0:
            return df
    if prov.exists():
        return pd.read_csv(prov).fillna("")
    return pd.DataFrame()


def p0_detail_enrich() -> pd.DataFrame:
    df = get_latest_seed_candidates()
    if df.empty:
        return df
    if "url" not in df.columns:
        return pd.DataFrame()

    # ensure at most 11 for P0 audit delivery
    df = df.head(11).copy()

    details = []
    failed = []
    for _, row in df.iterrows():
        d, status = fetch_detail(norm(row.get("url", "")), max_retries=2)
        if status != "ok":
            failed.append((row.get("url", ""), status))
        details.append(d)

    det_df = pd.DataFrame(details)
    merged = pd.concat([df.reset_index(drop=True), det_df.reset_index(drop=True)], axis=1).fillna("")

    # score by full detail
    rows = []
    for _, row in merged.iterrows():
        company = norm(row.get("company_name", row.get("公司全称", "")))
        name = norm(row.get("job_name", row.get("岗位名称", "")))
        location = norm(row.get("location", row.get("工作地点", "")))
        duties = norm(row.get("完整职责", ""))
        reqs = norm(row.get("完整要求", ""))
        parsed_duties, parsed_reqs = parse_jd_fields(
            f"{norm(row.get('详情抓取文本',''))} {norm(row.get('job_description',''))} {norm(row.get('job_requirement',''))}"
        )
        if len(duties) < 20 and parsed_duties:
            duties = parsed_duties
        if len(reqs) < 20 and parsed_reqs:
            reqs = parsed_reqs
        # 详情抽取失败时回填列表页描述，避免空值直接清零
        if len(duties) < 20:
            duties = norm(row.get("job_description", ""))
        if len(reqs) < 20:
            reqs = norm(row.get("job_requirement", ""))
        text_full = f"{name} {duties} {reqs} {norm(row.get('完整技能', ''))}"
        c_score, c_type, c_rank = company_score(company)
        r_score = role_score(name)
        e_score = english_score(text_full)
        g_score = growth_score(text_full)
        total = c_score + r_score + e_score + g_score
        rows.append(
            {
                "公司全称": company,
                "法定主体名称": company,
                "岗位名称": name,
                "薪资范围": norm(row.get("salary_text", row.get("salary", ""))),
                "工作地点": location,
                "实习类型": infer_intern_type(text_full),
                "实习时长": norm(row.get("实习时长", "")),
                "留用机会": norm(row.get("留用机会", "")),
                "投递链接": norm(row.get("url", "")),
                "完整职责": duties,
                "完整要求": reqs,
                "完整技能": norm(row.get("完整技能", "")),
                "抓取日期": now_str(),
                "截止日期": norm(row.get("截止日期", "")),
                "公司类型": c_type,
                "公司行业排名": c_rank,
                "总分": total,
                "投递优先级": priority(total),
                "核验状态": "详情已补抓",
                "平台": norm(row.get("platform", row.get("source", ""))),
                "source_job_id": norm(row.get("job_id", "")),
            }
        )
    out = pd.DataFrame(rows)

    # link accessibility
    if len(out) > 0:
        checks = asyncio.run(check_links_batch(out["投递链接"].tolist(), max_concurrent=8, timeout=12))
        m = {x["url"]: x for x in checks}
        out["链接状态"] = out["投递链接"].map(lambda u: (m.get(u) or {}).get("status", "UNKNOWN"))
        out["链接原因"] = out["投递链接"].map(lambda u: (m.get(u) or {}).get("reason", ""))

    out_path = OUT_DIR / "foreign_strict_shanghai_11_detailed_v2.csv"
    out.to_csv(out_path, index=False, encoding="utf-8-sig")
    return out


def parse_job51_item(it: Dict, keyword: str, page: int) -> Dict:
    job_id = it.get("jobId")
    return {
        "platform": "51job",
        "source": "51job",
        "keyword_group": keyword,
        "page": page,
        "job_id": job_id,
        "job_name": it.get("jobName"),
        "company_name": it.get("fullCompanyName") or it.get("customerName"),
        "location": it.get("jobAreaString"),
        "salary_text": it.get("provideSalaryString"),
        "education": it.get("degreeString"),
        "experience": it.get("workYearString"),
        "url": it.get("jobHref") or (f"https://jobs.51job.com/shanghai/{job_id}.html" if job_id else ""),
        "publish_date": it.get("issueDateString"),
        "job_description": it.get("jobDescribe") or it.get("jobDescribeText") or "",
        "job_requirement": it.get("jobRequirements") or "",
    }


def parse_liepin_item(it: Dict, keyword: str, page: int) -> Dict:
    comp = it.get("comp") if isinstance(it.get("comp"), dict) else {}
    job = it.get("job") if isinstance(it.get("job"), dict) else {}
    dq = job.get("dq") if isinstance(job.get("dq"), dict) else {}
    job_id = job.get("jobId") or it.get("jobId")
    return {
        "platform": "liepin",
        "source": "liepin",
        "keyword_group": keyword,
        "page": page,
        "job_id": job_id,
        "job_name": job.get("title") or it.get("title"),
        "company_name": comp.get("compName") or comp.get("name") or it.get("compName"),
        "location": dq.get("name") if isinstance(dq, dict) else "",
        "salary_text": job.get("salary") or "",
        "education": job.get("requireEduLevel") or "",
        "experience": job.get("requireWorkYears") or "",
        "url": f"https://www.liepin.com/job/{job_id}.shtml" if job_id else "",
        "publish_date": job.get("refreshTime") or "",
        "job_description": job.get("description") or it.get("description") or "",
        "job_requirement": job.get("require") or job.get("requireText") or "",
    }


def coarse_filter(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    work = df.copy().fillna("")
    # hard keep
    work = work[~work["company_name"].astype(str).str.contains(BIG_TECH_BAN_RE, regex=True, na=False, case=False)]
    work = work[~work["company_name"].astype(str).str.contains(OUTSOURCE_RE, regex=True, na=False, case=False)]
    # 粗过滤阶段不再强依赖外企名录，先做高召回；外企主体在严格阶段判定
    work = work[work["location"].astype(str).str.contains("上海|shanghai", regex=True, na=False, case=False)]
    full_text = (
        work["job_name"].astype(str)
        + " "
        + work["job_description"].astype(str)
        + " "
        + work["job_requirement"].astype(str)
    )
    work = work[
        work["job_name"].astype(str).str.contains("实习|intern|校招", regex=True, na=False, case=False)
        | full_text.str.contains("实习|intern|校招", regex=True, na=False, case=False)
    ]
    # 召回优先：岗位关键词放宽，英语要求下沉到严格过滤评分阶段
    broad_role_re = r"数据|分析|bi|ai|analytics|analyst|strategy|商业智能|数字化"
    work = work[work["job_name"].astype(str).str.contains(broad_role_re, regex=True, na=False, case=False)]
    work = work.drop_duplicates(subset=["url"], keep="first")
    return work


def strict_filter_and_score(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    rows = []
    for _, row in df.iterrows():
        company = norm(row.get("company_name", ""))
        name = norm(row.get("job_name", ""))
        detail = norm(row.get("详情抓取文本", ""))
        duties = norm(row.get("完整职责", ""))
        reqs = norm(row.get("完整要求", ""))
        if not duties or not reqs:
            d, r = parse_jd_fields(f"{detail} {norm(row.get('job_description',''))} {norm(row.get('job_requirement',''))}")
            duties = duties or d
            reqs = reqs or r
        skills = norm(row.get("完整技能", ""))
        text = f"{name} {duties} {reqs} {skills} {detail}"

        # strict detail filters
        fail = []
        duty_sent_cnt = len(split_sentences(duties))
        req_sent_cnt = len(split_sentences(reqs))
        if duty_sent_cnt < 3 and len(duties) < 120:
            fail.append("职责不足3条")
        if req_sent_cnt < 3 and len(reqs) < 120:
            fail.append("要求不足3条")
        if not re.search(SKILL_RE, text, re.I):
            fail.append("无硬技能关键词")
        if not re.search(FOREIGN_INCLUDE_RE, company, re.I):
            fail.append("非严格外企")
        if re.search(OUTSOURCE_RE, company, re.I):
            fail.append("外包中介")
        if row.get("链接状态", "") != "OK":
            fail.append("链接不可访问")

        c_score, c_type, c_rank = company_score(company)
        r_score = role_score(name)
        e_score = english_score(text)
        g_score = growth_score(text)
        total = c_score + r_score + e_score + g_score
        rows.append(
            {
                **row.to_dict(),
                "公司类型": c_type,
                "公司行业排名": c_rank,
                "公司梯队分": c_score,
                "岗位核心度分": r_score,
                "英语使用度分": e_score,
                "成长潜力分": g_score,
                "总分": total,
                "投递优先级": priority(total),
                "严格过滤失败原因": "|".join(fail),
                "严格过滤通过": len(fail) == 0,
            }
        )
    out = pd.DataFrame(rows)
    out = out.sort_values(["严格过滤通过", "总分"], ascending=[False, False])
    return out


def crawl_keyword_pages(max_pages_per_source: int = 50) -> pd.DataFrame:
    rows: List[Dict] = []
    job51_timeout = int(os.getenv("JOB51_RPC_TIMEOUT", "8"))
    liepin_timeout = int(os.getenv("LIEPIN_RPC_TIMEOUT", "20"))
    fail_stats = []
    for kw in KEYWORDS:
        print(f"[crawl] keyword={kw}")
        job51_consecutive_fail = 0
        liepin_consecutive_fail = 0
        for page in range(1, max_pages_per_source + 1):
            if job51_consecutive_fail >= 5 and liepin_consecutive_fail >= 8:
                break
            # 51job
            if job51_consecutive_fail < 5:
                p1 = {"keyword": kw, "pageNum": page, "jobArea": "020000", "pageSize": 20, "requestId": f"p1_{page}_{int(time.time())}"}
                try:
                    obj = requests.post(f"{RPC_BASE}/job51/search_jobs", json=p1, timeout=job51_timeout).json()
                    rb = (obj.get("result") or {}).get("resultbody") or {}
                    items = ((rb.get("job") or {}).get("items") or [])
                    rows.extend([parse_job51_item(x, kw, page) for x in items])
                    job51_consecutive_fail = 0
                except Exception as e:
                    job51_consecutive_fail += 1
                    fail_stats.append({"platform": "51job", "keyword": kw, "page": page, "reason": f"rpc_fail_{type(e).__name__}"})
            # liepin
            if liepin_consecutive_fail < 8:
                p2 = {"keyword": kw, "pageNum": page, "city": "020", "pageSize": 20}
                try:
                    obj = requests.post(f"{RPC_BASE}/liepin/search_jobs", json=p2, timeout=liepin_timeout).json()
                    res = obj.get("result") or {}
                    data = res.get("data") or {}
                    items = data.get("jobCardList") or []
                    rows.extend([parse_liepin_item(x, kw, page) for x in items])
                    liepin_consecutive_fail = 0
                except Exception as e:
                    liepin_consecutive_fail += 1
                    fail_stats.append({"platform": "liepin", "keyword": kw, "page": page, "reason": f"rpc_fail_{type(e).__name__}"})
            if page % 10 == 0:
                print(f"[crawl] keyword={kw} page={page} rows={len(rows)}")
            time.sleep(0.08)
        if job51_consecutive_fail >= 5:
            print(f"[crawl] keyword={kw} job51 circuit-breaker triggered, skipped remaining timeout-prone pages.")
        if liepin_consecutive_fail >= 8:
            print(f"[crawl] keyword={kw} liepin circuit-breaker triggered, skipped remaining timeout-prone pages.")
    raw = pd.DataFrame(rows).fillna("")
    if fail_stats:
        pd.DataFrame(fail_stats).to_csv(OUT_DIR / "rpc_page_failures_v2.csv", index=False, encoding="utf-8-sig")
    return raw


def enrich_details_with_retry(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    ok_rows = []
    fail_rows = []
    for _, row in df.iterrows():
        url = norm(row.get("url", ""))
        detail, status = fetch_detail(url, max_retries=2)
        if status == "ok":
            merged = {**row.to_dict(), **detail, "详情抓取状态": "成功"}
            d, r = parse_jd_fields(f"{norm(merged.get('详情抓取文本',''))} {norm(merged.get('job_description',''))} {norm(merged.get('job_requirement',''))}")
            if not norm(merged.get("完整职责", "")):
                merged["完整职责"] = d
            if not norm(merged.get("完整要求", "")):
                merged["完整要求"] = r
            duty_cnt = len(split_sentences(norm(merged.get("完整职责", ""))))
            req_cnt = len(split_sentences(norm(merged.get("完整要求", ""))))
            jd_visible = (duty_cnt >= 3 or len(norm(merged.get("完整职责", ""))) >= 120) and (
                req_cnt >= 3 or len(norm(merged.get("完整要求", ""))) >= 120
            )
            merged["JD可见性"] = "清晰可见" if jd_visible else "不清晰"
            merged["JD可见性原因"] = "" if jd_visible else f"duty_cnt={duty_cnt},req_cnt={req_cnt}"
            ok_rows.append(merged)
        else:
            # fallback with list JD so pipeline does not lose JD candidates
            d, r = parse_jd_fields(f"{norm(row.get('job_description',''))} {norm(row.get('job_requirement',''))}")
            if d or r:
                ok_rows.append(
                    {
                        **row.to_dict(),
                        "详情抓取状态": "失败-列表回填",
                        "失败原因": status,
                        "完整职责": d if d else norm(row.get("job_description", "")),
                        "完整要求": r if r else norm(row.get("job_requirement", "")),
                        "完整技能": " ".join(
                            sorted(set(re.findall(r"SQL|Python|Tableau|Power BI|SAS|R|Spark|Hadoop", f"{d} {r}", flags=re.I)))
                        ),
                        "详情抓取文本": norm(row.get("job_description", ""))[:3000],
                        "JD可见性": "不清晰",
                        "JD可见性原因": f"detail_fetch_failed:{status}",
                    }
                )
            else:
                fail_rows.append({**row.to_dict(), "详情抓取状态": "失败", "失败原因": status})
    return pd.DataFrame(ok_rows).fillna(""), pd.DataFrame(fail_rows).fillna("")


def generate_quality_report(
    raw_total: int,
    coarse_count: int,
    ok_count: int,
    fail_df: pd.DataFrame,
    strict_df: pd.DataFrame,
    raw_df: pd.DataFrame,
    jd_clear_count: int,
    jd_unclear_count: int,
):
    fail_reasons = {}
    if not fail_df.empty and "失败原因" in fail_df.columns:
        for x in fail_df["失败原因"].astype(str):
            fail_reasons[x] = fail_reasons.get(x, 0) + 1

    strict_pass = strict_df[strict_df.get("严格过滤通过", False) == True] if not strict_df.empty else pd.DataFrame()
    score_bins = {
        ">=75": int((strict_pass["总分"] >= 75).sum()) if not strict_pass.empty else 0,
        "70-74": int(((strict_pass["总分"] >= 70) & (strict_pass["总分"] <= 74)).sum()) if not strict_pass.empty else 0,
        "60-69": int(((strict_pass["总分"] >= 60) & (strict_pass["总分"] <= 69)).sum()) if not strict_pass.empty else 0,
        "<60": int((strict_pass["总分"] < 60).sum()) if not strict_pass.empty else 0,
    }
    industry_bins = {
        "化工": int(strict_pass["company_name"].astype(str).str.contains("巴斯夫|陶氏|杜邦|化工", regex=True, na=False).sum()) if not strict_pass.empty else 0,
        "制造": int(strict_pass["company_name"].astype(str).str.contains("西门子|博世|abb|制造|麦格纳|凯士比", regex=True, na=False).sum()) if not strict_pass.empty else 0,
        "医药": int(strict_pass["company_name"].astype(str).str.contains("辉瑞|罗氏|诺华|医药|强生|默沙东", regex=True, na=False).sum()) if not strict_pass.empty else 0,
        "能源": int(strict_pass["company_name"].astype(str).str.contains("壳牌|bp|埃克森|能源|油气", regex=True, na=False).sum()) if not strict_pass.empty else 0,
        "其他": int(len(strict_pass)) - sum(
            [
                int(strict_pass["company_name"].astype(str).str.contains("巴斯夫|陶氏|杜邦|化工", regex=True, na=False).sum()) if not strict_pass.empty else 0,
                int(strict_pass["company_name"].astype(str).str.contains("西门子|博世|abb|制造|麦格纳|凯士比", regex=True, na=False).sum()) if not strict_pass.empty else 0,
                int(strict_pass["company_name"].astype(str).str.contains("辉瑞|罗氏|诺华|医药|强生|默沙东", regex=True, na=False).sum()) if not strict_pass.empty else 0,
                int(strict_pass["company_name"].astype(str).str.contains("壳牌|bp|埃克森|能源|油气", regex=True, na=False).sum()) if not strict_pass.empty else 0,
            ]
        ),
    }

    md = []
    md.append("# quality_report_v2")
    md.append("")
    md.append(f"- 总抓取列表页条数: {raw_total}")
    md.append(f"- 粗过滤后剩余条数: {coarse_count}")
    md.append(f"- 详情页补抓成功条数: {ok_count}")
    md.append(f"- JD清晰可见条数: {jd_clear_count}")
    md.append(f"- JD不清晰条数: {jd_unclear_count}")
    md.append(f"- 详情页补抓失败条数: {len(fail_df)}")
    md.append("- 详情页补抓失败原因:")
    if fail_reasons:
        for k, v in sorted(fail_reasons.items(), key=lambda x: x[1], reverse=True):
            md.append(f"  - {k}: {v}")
    else:
        md.append("  - 无")
    md.append(f"- 严格过滤后剩余条数: {int((strict_df.get('严格过滤通过', pd.Series([], dtype=bool)) == True).sum()) if not strict_df.empty else 0}")
    md.append("- 各分数段条数分布:")
    for k, v in score_bins.items():
        md.append(f"  - {k}: {v}")
    md.append("- 各行业条数分布:")
    for k, v in industry_bins.items():
        md.append(f"  - {k}: {v}")
    md.append("- 每关键词召回条数:")
    if not raw_df.empty and "keyword_group" in raw_df.columns:
        for k, v in raw_df["keyword_group"].value_counts().items():
            md.append(f"  - {k}: {int(v)}")
    else:
        md.append("  - 无")
    md.append("- 每平台超时/熔断次数:")
    fail_csv = OUT_DIR / "rpc_page_failures_v2.csv"
    if fail_csv.exists():
        fdf = pd.read_csv(fail_csv)
        if not fdf.empty and "platform" in fdf.columns:
            for k, v in fdf["platform"].value_counts().items():
                md.append(f"  - {k}: {int(v)}")
        else:
            md.append("  - 无")
    else:
        md.append("  - 无")
    (OUT_DIR / "quality_report_v2.md").write_text("\n".join(md), encoding="utf-8")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / "51job").mkdir(parents=True, exist_ok=True)
    (RAW_DIR / "liepin").mkdir(parents=True, exist_ok=True)

    # P0: 11 details + re-score
    p0_df = p0_detail_enrich()
    print(f"P0 detailed rows={len(p0_df)}")

    # P1: 50 pages/source * keyword groups
    max_pages = int(os.getenv("PAGES_PER_SOURCE", "50"))
    use_existing_raw = os.getenv("USE_EXISTING_RAW", "0") == "1"
    use_all_local_raw = os.getenv("USE_ALL_LOCAL_RAW", "1") == "1"
    use_merged_pool = os.getenv("USE_MERGED_POOL", "1") == "1"
    if use_existing_raw:
        if use_all_local_raw:
            rows = []
            # aggregate historical third-party snapshots to improve sample size
            f51 = sorted(glob.glob(str(RAW_DIR / "51job" / "jobs_51job_*.json")))
            flp = sorted(glob.glob(str(RAW_DIR / "liepin" / "jobs_liepin_*.json")))
            for f in f51 + flp:
                try:
                    data = json.load(open(f, "r", encoding="utf-8"))
                    if isinstance(data, list):
                        rows.extend(data)
                except Exception:
                    continue
            raw_df = pd.DataFrame(rows).fillna("")
            print(f"use_existing_raw=1 use_all_local_raw=1 files={len(f51)+len(flp)} rows={len(raw_df)}")
        else:
            latest = sorted(glob.glob(str(RAW_DIR / "foreign_candidate_raw_*.json")), key=os.path.getmtime, reverse=True)
            if latest:
                raw_df = pd.DataFrame(json.load(open(latest[0], "r", encoding="utf-8"))).fillna("")
                print(f"use_existing_raw=1 source={latest[0]} rows={len(raw_df)}")
            else:
                raw_df = pd.DataFrame()
    else:
        raw_df = crawl_keyword_pages(max_pages_per_source=max_pages)
        ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        f_all = RAW_DIR / f"foreign_candidate_raw_{ts}.json"
        f_all.write_text(raw_df.to_json(orient="records", force_ascii=False), encoding="utf-8")

    if use_merged_pool:
        merged_pool = OUT_DIR / "foreign_strict_shanghai_candidate_pool_merged_v2.csv"
        if merged_pool.exists():
            mdf = pd.read_csv(merged_pool).fillna("")
            for c in ["platform", "source", "company_name", "job_name", "location", "salary_text", "education", "experience", "url", "publish_date", "job_description", "job_requirement"]:
                if c not in raw_df.columns:
                    raw_df[c] = ""
                if c not in mdf.columns:
                    mdf[c] = ""
            raw_df = pd.concat([raw_df, mdf[raw_df.columns.intersection(mdf.columns)]], ignore_index=True).fillna("")
            raw_df = raw_df.drop_duplicates(subset=["url"], keep="first")
            print(f"use_merged_pool=1 merged_rows={len(mdf)} total_rows={len(raw_df)}")

    coarse_df = coarse_filter(raw_df)
    coarse_path = OUT_DIR / "foreign_strict_shanghai_candidate_pool_v2.csv"
    coarse_df.to_csv(coarse_path, index=False, encoding="utf-8-sig")

    ok_df, fail_df = enrich_details_with_retry(coarse_df)
    # link check
    if not ok_df.empty:
        checks = asyncio.run(check_links_batch(ok_df["url"].astype(str).tolist(), max_concurrent=12, timeout=12))
        m = {x["url"]: x for x in checks}
        ok_df["链接状态"] = ok_df["url"].map(lambda u: (m.get(u) or {}).get("status", "UNKNOWN"))
        ok_df["链接原因"] = ok_df["url"].map(lambda u: (m.get(u) or {}).get("reason", ""))
    else:
        ok_df["链接状态"] = []
        ok_df["链接原因"] = []

    # 强制 JD 可见性门槛：不清晰JD进入隔离池，不参与严格筛选
    if "JD可见性" not in ok_df.columns:
        ok_df["JD可见性"] = "不清晰"
        ok_df["JD可见性原因"] = "missing_visibility_flag"
    jd_clear_df = ok_df[ok_df["JD可见性"] == "清晰可见"].copy()
    jd_unclear_df = ok_df[ok_df["JD可见性"] != "清晰可见"].copy()
    jd_unclear_path = OUT_DIR / "foreign_jd_unclear_quarantine_v2.csv"
    jd_unclear_df.to_csv(jd_unclear_path, index=False, encoding="utf-8-sig")

    strict_df = strict_filter_and_score(jd_clear_df)
    strict_path = OUT_DIR / "foreign_strict_shanghai_filtered_v2.csv"
    strict_df.to_csv(strict_path, index=False, encoding="utf-8-sig")

    top50 = strict_df[(strict_df["严格过滤通过"] == True) & (strict_df["总分"] >= 70)].head(50).copy()
    top50_path = OUT_DIR / "foreign_strict_top50_actionable_v2.csv"
    top50.to_csv(top50_path, index=False, encoding="utf-8-sig")

    generate_quality_report(
        raw_total=len(raw_df),
        coarse_count=len(coarse_df),
        ok_count=len(ok_df),
        fail_df=fail_df,
        strict_df=strict_df,
        raw_df=raw_df,
        jd_clear_count=len(jd_clear_df),
        jd_unclear_count=len(jd_unclear_df),
    )

    print(f"saved {coarse_path} rows={len(coarse_df)}")
    print(f"saved {strict_path} rows={len(strict_df)}")
    print(f"saved {top50_path} rows={len(top50)}")
    print(f"saved {jd_unclear_path} rows={len(jd_unclear_df)}")
    print(f"saved {(OUT_DIR / 'quality_report_v2.md')}")


if __name__ == "__main__":
    main()
