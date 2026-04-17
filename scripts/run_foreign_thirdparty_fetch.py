import datetime as dt
import json
import os
import re
import time
from pathlib import Path

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[1]
OUT_RAW = ROOT / "data" / "raw"
OUT_RAW_51 = OUT_RAW / "51job"
OUT_RAW_LP = OUT_RAW / "liepin"
OUT_RELEASE = ROOT / "release_data"
RPC_BASE = "http://127.0.0.1:5600/invoke"

BIG_TECH_BAN_RE = (
    "字节|腾讯|快手|小红书|美团|阿里|京东|哔哩|"
    "bilibili|bytedance|tencent|kuaishou|xiaohongshu|meituan|alibaba|jingdong|jd\\.com"
)
OUTSOURCING_RE = "外包|驻场|中介|代招|人力资源|服务外包|劳务派遣"
ENGLISH_RE = (
    "fluent in english|english as working language|native english|"
    "good english|english report|cet-6|tem-4|英语|英文"
)
CORE_SKILL_RE = "sql|python|tableau|power bi|数据分析|商业分析|数据科学|bi"
ROLE_CORE_RE = "数据科学|机器学习|算法|数据挖掘|data scientist|ml|algorithm"
ROLE_ANALYST_RE = "商业分析|数据分析|bi|business analyst|data analyst|analytics"
ROLE_OPS_RE = "数据运营|市场分析|用户分析|增长分析|growth|marketing analyst"
ROLE_RELATED_RE = "产品运营|战略分析|财务分析|strategy|finance analyst"
ROLE_BAD_RE = "行政|销售|客服|纯运营|人力资源|hr"
SUMMER_WINTER_RE = "寒假|暑假|summer intern|winter intern"
DAILY_OR_CONVERT_RE = "日常实习|可转正|长期实习|off-cycle|长期"


COMPANY_TIER_RULES = [
    (40, r"google|microsoft|amazon|nvidia|mckinsey|bcg|goldman|morgan stanley|谷歌|微软|亚马逊|英伟达|麦肯锡|波士顿咨询|高盛|摩根士丹利"),
    (35, r"apple|meta|tesla|unilever|p&g|l'oreal|loreal|hsbc|standard chartered|苹果|特斯拉|联合利华|宝洁|欧莱雅|汇丰|渣打"),
    (30, r"ibm|sap|intel|deloitte|kpmg|accenture|nestle|pepsi|pwc|ey|英特尔|德勤|毕马威|埃森哲|雀巢|百事|普华永道|安永"),
    (20, r"siemens|bosch|schneider|bayer|pfizer|merck|sanofi|citi|ubs|jpmorgan|西门子|博世|施耐德|拜耳|辉瑞|默沙东|赛诺菲|花旗|瑞银|摩根大通"),
]

STRICT_FOREIGN_INCLUDE_RE = (
    "microsoft|google|amazon|apple|oracle|ibm|sap|salesforce|adobe|nvidia|intel|amd|qualcomm|cisco|"
    "linkedin|uber|airbnb|paypal|stripe|shopee|shein|tesla|siemens|bosch|unilever|p&g|jpmorgan|goldman|"
    "morgan stanley|deloitte|pwc|ey|kpmg|accenture|nestle|pepsi|hsbc|standard chartered|"
    "谷歌|微软|亚马逊|苹果|甲骨文|英伟达|英特尔|高通|思科|领英|优步|爱彼迎|贝宝|西门子|博世|联合利华|宝洁|摩根|高盛|德勤|普华永道|安永|毕马威|"
    "泰科电子|喜利得|普立万|麦格纳|凯士比|强生|欧莱雅|雀巢|花旗|汇丰|渣打"
)


def fetch_job51(max_pages: int = 15):
    rows = []
    for page in range(1, max_pages + 1):
        payload = {
            "keyword": "实习",
            "pageNum": page,
            "jobArea": "020000",
            "pageSize": 20,
            "requestId": f"audit51_{page}",
        }
        try:
            obj = requests.post(
                f"{RPC_BASE}/job51/search_jobs",
                json=payload,
                timeout=90,
            ).json()
            result = obj.get("result") or {}
            result_body = result.get("resultbody") or {}
            items = ((result_body.get("job") or {}).get("items") or [])
            for it in items:
                job_id = it.get("jobId")
                rows.append(
                    {
                        "platform": "51job",
                        "job_id": job_id,
                        "job_name": it.get("jobName"),
                        "company_name": it.get("fullCompanyName") or it.get("customerName"),
                        "location": it.get("jobAreaString"),
                        "salary_text": it.get("provideSalaryString"),
                        "education": it.get("degreeString"),
                        "experience": it.get("workYearString"),
                        "url": it.get("jobHref")
                        or (f"https://jobs.51job.com/shanghai/{job_id}.html" if job_id else ""),
                        "publish_date": it.get("issueDateString"),
                        "job_description": it.get("jobDescribe") or it.get("jobDescribeText") or "",
                        "job_requirement": it.get("jobRequirements") or "",
                        "source": "51job",
                        "raw": it,
                    }
                )
            print(f"job51_page={page} items={len(items)}")
        except Exception as e:
            print(f"job51_page={page} ERR={e}")
        time.sleep(0.8)
    return rows


def fetch_liepin(max_pages: int = 15):
    rows = []
    for page in range(1, max_pages + 1):
        payload = {"keyword": "实习", "pageNum": page, "city": "020", "pageSize": 20, "jobKind": "2"}
        try:
            obj = requests.post(
                f"{RPC_BASE}/liepin/search_jobs",
                json=payload,
                timeout=120,
            ).json()
            result = obj.get("result") or {}
            data = result.get("data") or {}
            items = data.get("jobCardList") or []
            for it in items:
                comp = it.get("comp") if isinstance(it.get("comp"), dict) else {}
                job = it.get("job") if isinstance(it.get("job"), dict) else {}
                dq = job.get("dq") if isinstance(job.get("dq"), dict) else {}
                job_id = job.get("jobId") or it.get("jobId")
                rows.append(
                    {
                        "platform": "liepin",
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
                        "source": "liepin",
                        "raw": it,
                    }
                )
            print(f"liepin_page={page} items={len(items)} method={result.get('method')}")
        except Exception as e:
            print(f"liepin_page={page} ERR={e}")
        time.sleep(1.2)
    return rows


def norm_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().lower()


def _count_requirements(jd_text: str) -> int:
    if not jd_text:
        return 0
    parts = re.split(r"[；;。.\n]|\\d+[、.)）]", jd_text)
    parts = [x.strip() for x in parts if x.strip()]
    return len(parts)


def _company_tier_score(company_name: str):
    name = norm_text(company_name)
    for score, pattern in COMPANY_TIER_RULES:
        if re.search(pattern, name, re.I):
            return score, "S/A/B_tier"
    if re.search(STRICT_FOREIGN_INCLUDE_RE, name, re.I):
        return 20, "B_tier_foreign"
    return 0, "unknown_or_non_foreign"


def _role_score(job_name: str):
    title = norm_text(job_name)
    if re.search(ROLE_BAD_RE, title, re.I):
        return 0, "non_data_role"
    if re.search(ROLE_CORE_RE, title, re.I):
        return 30, "core_data_algo"
    if re.search(ROLE_ANALYST_RE, title, re.I):
        return 25, "analyst_role"
    if re.search(ROLE_OPS_RE, title, re.I):
        return 20, "ops_analysis_role"
    if re.search(ROLE_RELATED_RE, title, re.I):
        return 10, "related_role"
    return 0, "non_data_role"


def _english_score(text: str):
    t = norm_text(text)
    if re.search(r"fluent in english|english as working language|native english", t, re.I):
        return 15, "full_english_env"
    if re.search(r"good english|english report|英文汇报|英语沟通|英文沟通", t, re.I):
        return 10, "daily_english"
    if re.search(r"cet-6|tem-4|英语读写|英文阅读", t, re.I):
        return 5, "basic_english"
    return 0, "no_english_requirement"


def _growth_score(text: str):
    t = norm_text(text)
    if re.search(r"独立负责|主导|分析并提出建议|优化|提升|owner|lead", t, re.I):
        return 15, "owner_level"
    if re.search(r"参与|协助|支持|制作报表|分析数据|参与项目", t, re.I):
        return 10, "project_participation"
    if re.search(r"整理|录入|维护|协助团队", t, re.I):
        return 5, "support_work"
    return 0, "generic_or_misc"


def evaluate_jobs(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    for col in [
        "platform",
        "job_id",
        "job_name",
        "company_name",
        "location",
        "salary_text",
        "education",
        "experience",
        "url",
        "publish_date",
        "job_description",
        "job_requirement",
        "source",
    ]:
        if col not in work.columns:
            work[col] = ""

    fail_reasons = []
    base_fail_reasons = []
    company_scores = []
    role_scores = []
    english_scores = []
    growth_scores = []
    total_scores = []
    levels = []

    for _, row in work.iterrows():
        name = str(row.get("job_name", ""))
        company = str(row.get("company_name", ""))
        loc = str(row.get("location", ""))
        desc = str(row.get("job_description", ""))
        req = str(row.get("job_requirement", ""))
        text_all = f"{name} {desc} {req}"

        reasons = []
        base_reasons = []
        if re.search(BIG_TECH_BAN_RE, company, re.I):
            reasons.append("ban_big_tech")
            base_reasons.append("ban_big_tech")
        if not re.search(r"上海|shanghai", loc, re.I):
            reasons.append("not_shanghai")
            base_reasons.append("not_shanghai")
        if not re.search(r"实习|intern|校招", name, re.I):
            reasons.append("not_intern_title")
            base_reasons.append("not_intern_title")
        if re.search(SUMMER_WINTER_RE, text_all, re.I) and not re.search(DAILY_OR_CONVERT_RE, text_all, re.I):
            reasons.append("seasonal_intern_only")
        if not re.search(STRICT_FOREIGN_INCLUDE_RE, company, re.I):
            reasons.append("not_strict_foreign")
            base_reasons.append("not_strict_foreign")
        if re.search(OUTSOURCING_RE, company, re.I):
            reasons.append("outsourcing_or_agency")
            base_reasons.append("outsourcing_or_agency")

        if not re.search(CORE_SKILL_RE + r"|data analyst|business analyst|analytics|ai|machine vision", text_all, re.I):
            reasons.append("no_core_skill_keyword")
        if not re.search(ENGLISH_RE, text_all, re.I):
            if re.search(r"[A-Za-z]{6,}", name):
                pass
            else:
                reasons.append("no_english_keyword")

        has_jd_detail = len(desc.strip()) >= 30 or len(req.strip()) >= 30
        if has_jd_detail:
            if _count_requirements(req) < 3:
                reasons.append("requirements_lt_3")
            if _count_requirements(desc) < 3:
                reasons.append("responsibilities_lt_3")
        else:
            reasons.append("jd_detail_missing")

        if not str(row.get("url", "")).strip():
            reasons.append("empty_url")
            base_reasons.append("empty_url")

        company_score, _ = _company_tier_score(company)
        role_score, _ = _role_score(name)
        english_score, _ = _english_score(text_all)
        growth_score, _ = _growth_score(text_all)
        total = company_score + role_score + english_score + growth_score

        if total >= 80:
            level = "顶级高价值"
        elif total >= 70:
            level = "优质高价值"
        elif total >= 60:
            level = "合格可投"
        else:
            level = "过滤"

        fail_reasons.append("|".join(reasons))
        base_fail_reasons.append("|".join(base_reasons))
        company_scores.append(company_score)
        role_scores.append(role_score)
        english_scores.append(english_score)
        growth_scores.append(growth_score)
        total_scores.append(total)
        levels.append(level)

    work["company_tier_score"] = company_scores
    work["role_core_score"] = role_scores
    work["english_score"] = english_scores
    work["growth_score"] = growth_scores
    work["total_score"] = total_scores
    work["value_level"] = levels
    work["hard_filter_fail_reasons"] = fail_reasons
    work["base_filter_fail_reasons"] = base_fail_reasons
    work["hard_filter_pass"] = work["hard_filter_fail_reasons"] == ""
    work["base_filter_pass"] = work["base_filter_fail_reasons"] == ""
    return work.sort_values(["hard_filter_pass", "total_score"], ascending=[False, False])


def main():
    OUT_RAW_51.mkdir(parents=True, exist_ok=True)
    OUT_RAW_LP.mkdir(parents=True, exist_ok=True)
    OUT_RELEASE.mkdir(parents=True, exist_ok=True)

    use_existing = os.getenv("USE_EXISTING_RAW", "0") == "1"
    if use_existing:
        latest_51 = sorted(OUT_RAW_51.glob("jobs_51job_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        latest_lp = sorted(OUT_RAW_LP.glob("jobs_liepin_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        rows_51 = json.load(open(latest_51[0], "r", encoding="utf-8")) if latest_51 else []
        rows_lp = json.load(open(latest_lp[0], "r", encoding="utf-8")) if latest_lp else []
        print(f"use_existing_raw=1 rows_51={len(rows_51)} rows_liepin={len(rows_lp)}")
    else:
        rows_51 = fetch_job51(max_pages=int(os.getenv("JOB51_PAGES", "15")))
        rows_lp = fetch_liepin(max_pages=int(os.getenv("LIEPIN_PAGES", "15")))
    all_rows = rows_51 + rows_lp

    if not use_existing:
        ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        f51 = OUT_RAW_51 / f"jobs_51job_{ts}.json"
        flp = OUT_RAW_LP / f"jobs_liepin_{ts}.json"
        with open(f51, "w", encoding="utf-8") as f:
            json.dump(rows_51, f, ensure_ascii=False)
        with open(flp, "w", encoding="utf-8") as f:
            json.dump(rows_lp, f, ensure_ascii=False)
        print(f"saved {f51} rows={len(rows_51)}")
        print(f"saved {flp} rows={len(rows_lp)}")

    df = pd.DataFrame(all_rows).fillna("")
    scored = evaluate_jobs(df)

    out_all = OUT_RELEASE / "foreign_strict_scored_all_latest.csv"
    out_pass = OUT_RELEASE / "foreign_strict_shanghai_opportunities_latest.csv"
    out_verified = OUT_RELEASE / "foreign_strict_shanghai_verified_only.csv"
    out_top50 = OUT_RELEASE / "foreign_strict_top50_actionable.csv"
    out_provisional = OUT_RELEASE / "foreign_strict_provisional_candidates_latest.csv"

    scored.to_csv(out_all, index=False, encoding="utf-8-sig")
    passed = scored[scored["hard_filter_pass"]].copy()
    passed.to_csv(out_pass, index=False, encoding="utf-8-sig")
    verified = passed[passed["total_score"] >= 60].copy()
    verified.to_csv(out_verified, index=False, encoding="utf-8-sig")
    top50 = passed[passed["total_score"] >= 70].head(50).copy()
    top50.to_csv(out_top50, index=False, encoding="utf-8-sig")
    provisional = scored[(scored["base_filter_pass"]) & (scored["total_score"] >= 20)].copy()
    provisional.to_csv(out_provisional, index=False, encoding="utf-8-sig")

    print(f"saved {out_all} rows={len(scored)}")
    print(f"saved {out_pass} rows={len(passed)}")
    print(f"saved {out_verified} rows={len(verified)}")
    print(f"saved {out_top50} rows={len(top50)}")
    print(f"saved {out_provisional} rows={len(provisional)}")
    if not passed.empty:
        print(passed[["company_name", "job_name", "total_score", "value_level"]].head(20).to_string(index=False))


if __name__ == "__main__":
    main()
