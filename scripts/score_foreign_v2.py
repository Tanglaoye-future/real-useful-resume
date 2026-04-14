import asyncio
import datetime as dt
import glob
import json
import os
import re
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_51_DIR = ROOT / "data" / "raw" / "51job"
RAW_LP_DIR = ROOT / "data" / "raw" / "liepin"
OUT_DIR = ROOT / "release_data"

# import shared link checker from parent project
sys.path.insert(0, str(ROOT.parent))
from utils.link_checker import check_links_batch  # type: ignore


BIG_TECH_BAN_RE = (
    "字节|腾讯|快手|小红书|美团|阿里|京东|哔哩|"
    "bilibili|bytedance|tencent|kuaishou|xiaohongshu|meituan|alibaba|jingdong|jd\\.com"
)
OUTSOURCING_RE = "外包|驻场|中介|代招|人力资源|服务外包|劳务派遣|猎头"
FOREIGN_INCLUDE_RE = (
    "microsoft|google|amazon|apple|oracle|ibm|sap|salesforce|adobe|nvidia|intel|amd|qualcomm|cisco|"
    "linkedin|uber|airbnb|paypal|stripe|shopee|shein|tesla|siemens|bosch|unilever|p&g|jpmorgan|goldman|"
    "morgan stanley|deloitte|pwc|ey|kpmg|accenture|nestle|pepsi|hsbc|standard chartered|"
    "谷歌|微软|亚马逊|苹果|甲骨文|英伟达|英特尔|高通|思科|领英|优步|爱彼迎|贝宝|西门子|博世|联合利华|宝洁|摩根|高盛|德勤|普华永道|安永|毕马威|"
    "泰科电子|喜利得|普立万|麦格纳|凯士比|强生|欧莱雅|雀巢|花旗|汇丰|渣打|巴斯夫|淡水河谷|陶氏|杜邦|必和必拓|力拓|辉瑞|罗氏|诺华|abb|壳牌|bp|埃克森"
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

TIER_38 = ["联合利华", "雀巢", "百事", "可口可乐", "强生", "默沙东", "施耐德", "壳牌", "bp", "埃克森"]
TIER_35 = ["shein", "openai", "anthropic", "shopee"]
TIER_30 = [
    "微软",
    "谷歌",
    "亚马逊",
    "苹果",
    "meta",
    "特斯拉",
    "麦肯锡",
    "bcg",
    "贝恩",
    "高盛",
    "摩根士丹利",
]
TIER_25 = ["ibm", "sap", "英特尔", "德勤", "毕马威", "埃森哲", "欧莱雅", "汇丰", "渣打", "普华永道", "安永"]


def norm(v) -> str:
    return re.sub(r"\s+", " ", str(v or "")).strip()


def load_latest_rows() -> pd.DataFrame:
    f51 = sorted(glob.glob(str(RAW_51_DIR / "jobs_51job_*.json")), key=os.path.getmtime, reverse=True)
    flp = sorted(glob.glob(str(RAW_LP_DIR / "jobs_liepin_*.json")), key=os.path.getmtime, reverse=True)
    rows = []
    if f51:
        rows += json.load(open(f51[0], "r", encoding="utf-8"))
    if flp:
        rows += json.load(open(flp[0], "r", encoding="utf-8"))
    df = pd.DataFrame(rows).fillna("")
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
        if col not in df.columns:
            df[col] = ""
    return df


def company_score(company_name: str):
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


def role_score(job_name: str):
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


def english_score(text: str):
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


def growth_score(text: str):
    t = norm(text).lower()
    if re.search("独立负责|主导|分析并提出建议|优化|提升|owner|lead", t, re.I):
        return 10
    if re.search("参与|协助|支持|制作报表|分析数据|参与项目", t, re.I):
        return 6
    if re.search("整理|录入|维护|协助团队", t, re.I):
        return 3
    return 0


def priority_label(total: int) -> str:
    if total >= 75:
        return "核心目标"
    if total >= 70:
        return "优质目标"
    if total >= 60:
        return "保底目标"
    return "过滤"


def hard_filter_base(row) -> list[str]:
    reasons = []
    company = norm(row.get("company_name", ""))
    name = norm(row.get("job_name", ""))
    location = norm(row.get("location", ""))
    jd_text = norm(row.get("job_description", "")) + " " + norm(row.get("job_requirement", ""))
    all_text = f"{name} {jd_text}"

    if re.search(BIG_TECH_BAN_RE, company, re.I):
        reasons.append("ban_big_tech")
    if re.search(OUTSOURCING_RE, company, re.I):
        reasons.append("outsourcing_or_agency")
    if not re.search("上海|shanghai", location, re.I):
        reasons.append("not_shanghai")
    if not re.search("实习|intern|校招", name, re.I):
        reasons.append("not_intern")
    if re.search("寒假|暑假|summer intern|winter intern", all_text, re.I) and not re.search(
        "日常实习|可转正|长期实习|off-cycle|长期", all_text, re.I
    ):
        reasons.append("seasonal_only")
    if not re.search(FOREIGN_INCLUDE_RE, company, re.I):
        reasons.append("not_strict_foreign")
    if not re.search("sql|python|tableau|power bi|数据分析|商业分析|数据科学|bi", all_text, re.I):
        reasons.append("no_core_skill")
    if not re.search("fluent in english|english|英语|英文|cet-6|tem-4", all_text, re.I):
        reasons.append("no_english")
    if not norm(row.get("url", "")):
        reasons.append("empty_url")
    return reasons


def build_scored(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for _, row in df.iterrows():
        company = norm(row.get("company_name", ""))
        name = norm(row.get("job_name", ""))
        jd_text = norm(row.get("job_description", "")) + " " + norm(row.get("job_requirement", ""))
        text_all = f"{name} {jd_text}"
        c_score, c_type, c_rank = company_score(company)
        r_score = role_score(name)
        e_score = english_score(text_all)
        g_score = growth_score(text_all)
        total = c_score + r_score + e_score + g_score
        fail = hard_filter_base(row)
        out.append(
            {
                **row.to_dict(),
                "公司类型": c_type,
                "公司行业排名": c_rank,
                "公司梯队分": c_score,
                "岗位核心度分": r_score,
                "英语使用度分": e_score,
                "成长潜力分": g_score,
                "总分": total,
                "投递优先级": priority_label(total),
                "硬过滤失败原因": "|".join(fail),
                "硬过滤通过": len(fail) == 0,
            }
        )
    return pd.DataFrame(out).sort_values(["硬过滤通过", "总分"], ascending=[False, False])


def mark_link_status(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        df["链接状态"] = []
        df["链接原因"] = []
        df["可投递性"] = []
        df["过期时间标注"] = []
        return df
    urls = df["url"].fillna("").astype(str).tolist()
    checks = asyncio.run(check_links_batch(urls, max_concurrent=12, timeout=12))
    m = {x["url"]: x for x in checks}
    status = []
    reason = []
    can_apply = []
    for u in urls:
        r = m.get(u, {})
        s = r.get("status", "UNKNOWN")
        status.append(s)
        reason.append(r.get("reason", ""))
        if s == "OK":
            can_apply.append("可投递")
        elif s == "BROKEN":
            can_apply.append("不可投递")
        else:
            can_apply.append("待人工复核")
    df["链接状态"] = status
    df["链接原因"] = reason
    df["可投递性"] = can_apply
    df["过期时间标注"] = "未提供"
    return df


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_latest_rows()
    scored = build_scored(df)

    strict_pool = scored[scored["硬过滤通过"]].copy()
    if strict_pool.empty:
        # audit fallback: keep base foreign/shanghai/intern pool for PM manual review
        strict_pool = scored[
            (~scored["硬过滤失败原因"].astype(str).str.contains("ban_big_tech|not_shanghai|not_intern|not_strict_foreign|outsourcing_or_agency"))
        ].copy()
        strict_pool["审核备注"] = "严格规则下为0，当前为人工复核候选池"
    strict_pool = mark_link_status(strict_pool)

    # deliverables required by PM
    out_11 = OUT_DIR / "foreign_strict_shanghai_11_verified_v2.csv"
    out_top50 = OUT_DIR / "foreign_strict_top50_actionable.csv"
    out_full = OUT_DIR / "foreign_strict_scored_all_latest.csv"

    # first deliverable: prioritize the first available strict pool (historically around 11 entries)
    strict_pool.head(11).to_csv(out_11, index=False, encoding="utf-8-sig")
    strict_pool[(strict_pool["总分"] >= 70) & (strict_pool["可投递性"] == "可投递")].head(50).to_csv(
        out_top50, index=False, encoding="utf-8-sig"
    )
    scored.to_csv(out_full, index=False, encoding="utf-8-sig")

    print(f"saved {out_11} rows={len(strict_pool.head(11))}")
    print(f"saved {out_top50} rows={len(strict_pool[(strict_pool['总分'] >= 70) & (strict_pool['可投递性'] == '可投递')].head(50))}")
    print(f"saved {out_full} rows={len(scored)}")
    if not strict_pool.empty:
        print(strict_pool[["company_name", "job_name", "总分", "投递优先级", "可投递性"]].head(20).to_string(index=False))
    else:
        print("strict_pool is empty under current hard filters.")


if __name__ == "__main__":
    main()
