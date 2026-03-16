import glob
import os
import re
from collections import Counter
from datetime import datetime

import pandas as pd
from rules.cohort27_rules import classify_27_cohort
from rules.location_normalizer import normalize_city

shixiseng_path = r"C:\jz_code\internship_finding\archive\history\shixiseng\实习僧公司要求大全"
bytedance_output_path = r"C:\jz_code\internship_finding\real-useful-resume\output"
official_raw_file = r"C:\jz_code\internship_finding\official_jobs_raw.csv"

big_company_keywords = [
    "字节跳动", "阿里", "腾讯", "美团", "京东", "哔哩哔哩", "小红书", "拼多多", "快手", "华为", "米哈游",
    "百度", "网易", "滴滴", "蚂蚁", "携程", "理想", "小米", "科大讯飞", "联想", "荣耀", "顺丰", "Shopee"
]

role_keywords = [
    "数据分析", "商业分析", "策略分析", "经营分析", "bi", "产品经理", "数据产品", "产品运营",
    "增长", "业务分析", "信息化", "数字化", "系统实施", "sql", "python", "ab测试", "实验", "用户增长"
]

grade_keywords = [
    "27届", "2027届", "2027", "2026年9月-2027年8月", "26年9月-27年8月", "2027年毕业", "2027届毕业生",
    "26-27届", "2026-2027", "2026/2027", "27届及以后", "2027届及以后", "27届毕业", "26届-27届"
]

skill_keywords = [
    "sql", "python", "excel", "tableau", "power bi", "统计", "机器学习", "a/b", "ab测试",
    "产品思维", "增长", "数据建模", "数据仓库", "hive", "spark", "沟通协作", "项目管理"
]

dashboard_skill_keywords = [
    "python", "sql", "spark", "hadoop", "tableau", "power bi", "hive", "数据分析", "机器学习", "统计"
]
priority_skill_keywords = ["python", "sql", "spark", "hadoop", "hive", "tableau", "power bi", "机器学习", "统计", "数据分析"]
TARGET_CITY = "上海"


def normalize_text(x):
    if pd.isna(x):
        return ""
    txt = str(x).replace("\u3000", " ").replace("\xa0", " ")
    return re.sub(r"\s+", " ", txt).strip()


def split_jd(info):
    text = normalize_text(info)
    if not text:
        return "", ""
    resp = ""
    req = ""
    m_resp = re.search(r"(岗位职责|职位描述|工作职责)[:：]?(.*?)(岗位要求|任职要求|职位要求|加分项|$)", text)
    if m_resp:
        resp = normalize_text(m_resp.group(2))
    m_req = re.search(r"(岗位要求|任职要求|职位要求)[:：]?(.*?)(加分项|工作地点|$)", text)
    if m_req:
        req = normalize_text(m_req.group(2))
    if not resp and not req:
        req = text
    return resp, req


def extract_degree(text):
    t = normalize_text(text)
    m = re.search(r"(本科及以上|硕士及以上|博士|本科|硕士|大专及以上|不限学历)", t)
    return m.group(1) if m else ""


def extract_graduation_batch(text):
    t = normalize_text(text)
    m = re.search(r"(27届|2027届|2027年毕业|2026年9月-2027年8月)", t)
    if m:
        return m.group(1)
    return ""


def extract_intern_days(text):
    t = normalize_text(text)
    m = re.search(r"(每周.*?\d+天|\d+天/周|\d+天以上)", t)
    return m.group(1) if m else ""


def extract_intern_months(text):
    t = normalize_text(text)
    m = re.search(r"(\d+个月|实习.*?个月)", t)
    return m.group(1) if m else ""


def map_shixiseng(df):
    mapped = pd.DataFrame(
        {
            "url": df.get("url", ""),
            "company": df.get("company", ""),
            "name": df.get("name", ""),
            "city": df.get("city", ""),
            "jd_raw": df.get("info", ""),
            "salary": df.get("salary", ""),
            "company_size": df.get("company_size", ""),
            "duration": df.get("duration", ""),
            "academic": df.get("academic", ""),
            "publish_time": "",
            "deadline": "",
            "collect_time": "",
            "source": "shixiseng",
        }
    )
    return mapped


def map_bytedance(df):
    duties = df.get("岗位职责")
    if duties is None:
        duties = pd.Series([""] * len(df))
    reqs = df.get("岗位要求")
    if reqs is None:
        reqs = pd.Series([""] * len(df))
    pub = df.get("岗位发布时间", "")
    ddl = df.get("报名截止时间", "")
    ctime = df.get("采集时间", "")

    mapped = pd.DataFrame(
        {
            "url": df.get("投递链接", ""),
            "company": df.get("公司名", ""),
            "name": df.get("岗位名", ""),
            "city": df.get("工作城市", ""),
            "jd_raw": duties.fillna("").astype(str) + " 岗位要求：" + reqs.fillna("").astype(str),
            "salary": "",
            "company_size": "",
            "duration": "",
            "academic": "",
            "publish_time": pub,
            "deadline": ddl,
            "collect_time": ctime,
            "source": "bytedance",
        }
    )
    return mapped


def map_official(df):
    mapped = pd.DataFrame(
        {
            "url": df.get("url", ""),
            "company": df.get("company", ""),
            "name": df.get("name", ""),
            "city": df.get("city", ""),
            "jd_raw": df.get("jd_raw", ""),
            "salary": df.get("salary", ""),
            "company_size": df.get("company_size", ""),
            "duration": df.get("duration", ""),
            "academic": df.get("academic", ""),
            "publish_time": df.get("publish_time", ""),
            "deadline": df.get("deadline", ""),
            "collect_time": df.get("collect_time", ""),
            "source": df.get("source", "official"),
            "recruit_type": df.get("recruit_type", ""),
            "raw_tags": df.get("raw_tags", ""),
            "external_job_id": df.get("external_job_id", ""),
            "update_time": df.get("update_time", ""),
            "sync_status": df.get("sync_status", ""),
        }
    )
    return mapped


def is_big_company(company):
    c = normalize_text(company)
    return any(k.lower() in c.lower() for k in big_company_keywords)


def is_27_match(text):
    t = normalize_text(text)
    if any(k in t for k in grade_keywords):
        return True
    if re.search(r"(26|2026).{0,8}(27|2027)", t):
        return True
    if re.search(r"(27|2027).{0,8}(及以后|以后)", t):
        return True
    return False


def role_match_score(text):
    t = normalize_text(text).lower()
    hit = sum(1 for k in role_keywords if k.lower() in t)
    return min(hit * 5, 30)


def jd_quality_score(resp, req):
    fields = [normalize_text(resp), normalize_text(req)]
    non_empty = sum(1 for x in fields if x)
    length_score = min((len(fields[0]) + len(fields[1])) // 120, 10)
    return non_empty * 5 + length_score


def score_row(row):
    score = 0
    company = normalize_text(row.get("company", ""))
    city = normalize_text(row.get("city", ""))
    jd = normalize_text(row.get("jd_raw", ""))
    resp = normalize_text(row.get("responsibility", ""))
    req = normalize_text(row.get("requirement", ""))
    name = normalize_text(row.get("name", ""))
    text = f"{name} {jd} {req}"

    if is_big_company(company):
        score += 20
    if TARGET_CITY in city:
        score += 20
    if is_27_match(text):
        score += 20
    score += role_match_score(text)
    score += jd_quality_score(resp, req)
    return min(score, 100)


def extract_city_from_text(text):
    t = normalize_text(text)
    city_list = ["上海", "北京", "深圳", "广州", "杭州", "成都", "南京", "苏州", "武汉", "西安", "天津", "重庆", "青岛", "厦门", "大连"]
    for c in city_list:
        if c in t:
            return c
    return ""


def enrich_cohort27_fields(row):
    signal = {
        "title": row.get("name", ""),
        "jd_raw": row.get("jd_raw", ""),
        "source": row.get("source", ""),
        "recruit_type": row.get("recruit_type", ""),
        "collect_time": row.get("collect_time", ""),
        "project_name": row.get("raw_tags", ""),
        "year_text": row.get("graduation_batch", ""),
    }
    return classify_27_cohort(signal)


def infer_27_from_context(row):
    text = normalize_text(f"{row.get('name', '')} {row.get('jd_raw', '')} {row.get('source', '')}")
    if is_27_match(text):
        return True
    src = normalize_text(row.get("source", ""))
    if src in {"official_tencent_api", "official_jd_api", "official_baidu_api"}:
        return True
    if any(k in text for k in ["校园", "校招", "应届", "留用实习", "实习生"]):
        return True
    return False


def build_quality_report(df):
    rows = []
    key_cols = ["company", "name", "city", "url", "jd_raw", "requirement"]
    for src, g in df.groupby("source"):
        item = {"source": src, "rows": len(g)}
        for col in key_cols:
            item[f"{col}_完整率"] = round((g[col].astype(str).str.strip() != "").mean() * 100, 2)
        rows.append(item)
    overall = {"source": "all", "rows": len(df)}
    for col in key_cols:
        overall[f"{col}_完整率"] = round((df[col].astype(str).str.strip() != "").mean() * 100, 2)
    rows.append(overall)
    return pd.DataFrame(rows)


def build_skill_gap_report(target_df):
    text_series = (target_df["name"].fillna("") + " " + target_df["jd_raw"].fillna("") + " " + target_df["requirement"].fillna("")).str.lower()
    counter = Counter()
    for text in text_series.tolist():
        for k in skill_keywords:
            if k.lower() in text:
                counter[k] += 1
    report = pd.DataFrame({"skill": list(counter.keys()), "count": list(counter.values())}).sort_values("count", ascending=False)
    if report.empty:
        report = pd.DataFrame({"skill": skill_keywords, "count": [0] * len(skill_keywords)})
    report["coverage_pct"] = (report["count"] / max(len(target_df), 1) * 100).round(2)
    return report


def classify_role_type(row):
    text = normalize_text(f"{row.get('name', '')} {row.get('jd_raw', '')}").lower()
    if re.search(r"(数据分析|商业分析|策略分析|经营分析|bi|tableau|power bi)", text):
        return "数据分析"
    if re.search(r"(数据开发|数据工程|数仓|数据仓库|hadoop|spark|hive|etl)", text):
        return "数据开发"
    if re.search(r"(算法|机器学习|推荐|搜索|nlp|cv|深度学习)", text):
        return "算法"
    return "其他"


def is_data_job(row):
    text = normalize_text(f"{row.get('name', '')} {row.get('jd_raw', '')}").lower()
    return bool(re.search(r"(数据|分析|策略|算法|商业分析|bi|python|sql)", text))


def count_priority_skill_hits(row):
    text = normalize_text(f"{row.get('name', '')} {row.get('jd_raw', '')} {row.get('requirement', '')}").lower()
    return sum(1 for k in priority_skill_keywords if k.lower() in text)


def _load_csv_if_exists(path):
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


def generate_kuaishou_dashboard(df_all):
    df_ks = df_all[df_all["company"] == "快手"].copy()
    if df_ks.empty:
        print("[Dashboard] 快手看板跳过：当前无快手数据")
        return {}

    today = datetime.now().strftime("%Y-%m-%d")
    dashboard_latest_path = "dashboard_kuaishou_latest.csv"
    summary_path = "dashboard_kuaishou_summary.csv"
    role_path = "dashboard_kuaishou_role_distribution.csv"
    keyword_path = "dashboard_kuaishou_keyword_top10.csv"
    new_high_path = "dashboard_kuaishou_new_high_sh_data.csv"
    close_warn_path = "dashboard_kuaishou_close_warning.csv"
    daily_trend_path = "dashboard_kuaishou_daily_trend.csv"
    history_path = "dashboard_kuaishou_history.csv"
    strict_snap_prev = "dashboard_kuaishou_strict27_snapshot_prev.csv"
    strict_snap_latest = "dashboard_kuaishou_strict27_snapshot_latest.csv"
    core_snap_prev = "dashboard_kuaishou_core_snapshot_prev.csv"
    core_snap_latest = "dashboard_kuaishou_core_snapshot_latest.csv"

    df_ks["collect_date"] = pd.to_datetime(df_ks["collect_time"], errors="coerce").dt.strftime("%Y-%m-%d")
    df_ks["role_type"] = df_ks.apply(classify_role_type, axis=1)
    df_ks["is_data_job"] = df_ks.apply(is_data_job, axis=1)
    df_ks["is_shanghai_city"] = df_ks["city"].astype(str).str.contains(TARGET_CITY, na=False)
    df_ks["priority_skill_hit_count"] = df_ks.apply(count_priority_skill_hits, axis=1)
    df_ks["priority_label"] = ""
    df_ks.loc[
        (df_ks["cohort27_confidence"] == "high")
        & (df_ks["is_shanghai_city"])
        & (df_ks["is_data_job"])
        & (df_ks["priority_skill_hit_count"] >= 3),
        "priority_label",
    ] = "PRIORITY_A"
    df_ks["is_core_target"] = (df_ks["cohort27_confidence"] == "high") & df_ks["is_shanghai_city"] & df_ks["is_data_job"]

    strict_now = df_ks[df_ks["cohort27_confidence"] == "high"].copy()
    strict_now_ids = set(strict_now["external_job_id"].astype(str).tolist()) if "external_job_id" in strict_now.columns else set()
    strict_prev_df = _load_csv_if_exists(strict_snap_latest)
    strict_prev_ids = set(strict_prev_df.get("external_job_id", pd.Series(dtype=str)).astype(str).tolist())
    strict_net_increase = len(strict_now_ids - strict_prev_ids)
    if os.path.exists(strict_snap_latest):
        try:
            if os.path.exists(strict_snap_prev):
                os.remove(strict_snap_prev)
            os.replace(strict_snap_latest, strict_snap_prev)
        except Exception:
            pass
    strict_now[["external_job_id", "name", "city", "collect_time", "update_time", "cohort27_confidence"]].to_csv(
        strict_snap_latest, index=False, encoding="utf-8-sig"
    )

    core_now = df_ks[df_ks["is_core_target"]].copy()
    core_now_ids = set(core_now["external_job_id"].astype(str).tolist()) if "external_job_id" in core_now.columns else set()
    core_prev_df = _load_csv_if_exists(core_snap_latest)
    core_prev_ids = set(core_prev_df.get("external_job_id", pd.Series(dtype=str)).astype(str).tolist())
    new_core_ids = core_now_ids - core_prev_ids
    new_core_today = core_now[core_now["external_job_id"].astype(str).isin(new_core_ids)].copy()
    if os.path.exists(core_snap_latest):
        try:
            if os.path.exists(core_snap_prev):
                os.remove(core_snap_prev)
            os.replace(core_snap_latest, core_snap_prev)
        except Exception:
            pass
    core_now[["external_job_id", "name", "city", "collect_time", "update_time", "cohort27_confidence", "url"]].to_csv(
        core_snap_latest, index=False, encoding="utf-8-sig"
    )

    city_dist = df_ks["city"].value_counts(dropna=False)
    shanghai_ratio = round((df_ks["city"].astype(str).str.contains(TARGET_CITY, na=False).mean()) * 100, 2)
    role_dist = df_ks["role_type"].value_counts().reset_index()
    role_dist.columns = ["role_type", "count"]
    role_dist["pct"] = (role_dist["count"] / max(len(df_ks), 1) * 100).round(2)

    text_series = (df_ks["name"].fillna("") + " " + df_ks["jd_raw"].fillna("")).str.lower()
    keyword_rows = []
    for k in dashboard_skill_keywords:
        hit = int(text_series.str.contains(re.escape(k.lower()), na=False).sum())
        keyword_rows.append({"keyword": k, "count": hit, "hit_rate_pct": round(hit / max(len(df_ks), 1) * 100, 2)})
    keyword_df = pd.DataFrame(keyword_rows).sort_values(["count", "keyword"], ascending=[False, True]).head(10)

    today_high_df = new_core_today[
        [
            "external_job_id",
            "name",
            "city",
            "cohort27_confidence",
            "priority_label",
            "priority_skill_hit_count",
            "recruit_type",
            "raw_tags",
            "update_time",
            "url",
            "jd_raw",
        ]
    ].copy()
    today_high_df = today_high_df.sort_values(["update_time", "name"], ascending=[False, True])

    hist_today = core_now[["external_job_id", "name", "city", "update_time", "collect_time", "source"]].copy()
    hist_today["date"] = today
    hist_df = _load_csv_if_exists(history_path)
    hist_df = pd.concat([hist_df, hist_today], ignore_index=True)
    hist_df = hist_df.drop_duplicates(subset=["date", "external_job_id"], keep="last")
    hist_df.to_csv(history_path, index=False, encoding="utf-8-sig")

    recent = hist_df.copy()
    recent = recent[recent["date"] >= (datetime.now() - pd.Timedelta(days=3)).strftime("%Y-%m-%d")]
    warn_rows = []
    if not recent.empty:
        for job_id, g in recent.groupby("external_job_id"):
            g = g.sort_values("date")
            dates = g["date"].dropna().unique().tolist()
            if len(dates) >= 3:
                upd = g["update_time"].fillna("").astype(str).str.strip().unique().tolist()
                if len([x for x in upd if x]) <= 1:
                    row = g.iloc[-1].to_dict()
                    row["warning_reason"] = "连续3天在榜且更新时间未变化"
                    warn_rows.append(row)
    warn_df = pd.DataFrame(warn_rows)
    if not warn_df.empty:
        warn_df = warn_df.sort_values(["date", "name"], ascending=[False, True])

    daily_trend = hist_df.groupby("date", as_index=False).agg(核心岗位数=("external_job_id", "nunique"))
    daily_trend = daily_trend.sort_values("date")

    summary = pd.DataFrame(
        [
            {
                "date": today,
                "kuaishou_total_jobs": len(df_ks),
                "confidence_high": int((df_ks["cohort27_confidence"] == "high").sum()),
                "confidence_medium": int((df_ks["cohort27_confidence"] == "medium").sum()),
                "confidence_low": int((df_ks["cohort27_confidence"] == "low").sum()),
                "confidence_none": int((df_ks["cohort27_confidence"] == "none").sum()),
                "strict27_net_increase_dod": int(strict_net_increase),
                "shanghai_ratio_pct": shanghai_ratio,
                "core_target_new_today": int(len(today_high_df)),
                "priority_a_new_today": int((today_high_df["priority_label"] == "PRIORITY_A").sum()),
                "close_warning_count": int(len(warn_df)),
            }
        ]
    )

    df_ks.to_csv(dashboard_latest_path, index=False, encoding="utf-8-sig")
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")
    role_dist.to_csv(role_path, index=False, encoding="utf-8-sig")
    keyword_df.to_csv(keyword_path, index=False, encoding="utf-8-sig")
    today_high_df.to_csv(new_high_path, index=False, encoding="utf-8-sig")
    warn_df.to_csv(close_warn_path, index=False, encoding="utf-8-sig")
    daily_trend.to_csv(daily_trend_path, index=False, encoding="utf-8-sig")
    print(f"[Dashboard] 快手看板已更新: {len(df_ks)} 条")

    return {
        "latest": dashboard_latest_path,
        "summary": summary_path,
        "role": role_path,
        "keyword": keyword_path,
        "new_high": new_high_path,
        "close_warn": close_warn_path,
        "daily_trend": daily_trend_path,
    }


def safe_write_csv(df, file_name):
    try:
        df.to_csv(file_name, index=False, encoding="utf-8-sig")
        return file_name
    except PermissionError:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        alt = file_name.replace(".csv", f"_{ts}.csv")
        df.to_csv(alt, index=False, encoding="utf-8-sig")
        return alt


def main():
    all_frames = []
    for filename in glob.glob(os.path.join(shixiseng_path, "*.csv")):
        try:
            df = pd.read_csv(filename, index_col=None, header=0)
            all_frames.append(map_shixiseng(df))
        except Exception as e:
            print(f"读取实习僧文件失败 {filename}: {e}")

    for filename in glob.glob(os.path.join(bytedance_output_path, "字节跳动校招岗位_*.csv")):
        try:
            df = pd.read_csv(filename, index_col=None, header=0)
            all_frames.append(map_bytedance(df))
        except Exception as e:
            print(f"读取字节文件失败 {filename}: {e}")

    if os.path.exists(official_raw_file):
        try:
            official_df = pd.read_csv(official_raw_file, index_col=None, header=0)
            all_frames.append(map_official(official_df))
        except Exception as e:
            print(f"读取官网文件失败 {official_raw_file}: {e}")

    if not all_frames:
        print("未找到可合并文件，请检查目录配置。")
        return

    frame = pd.concat(all_frames, axis=0, ignore_index=True)
    for col in [
        "url", "company", "name", "city", "jd_raw", "salary", "company_size", "duration", "academic",
        "publish_time", "deadline", "collect_time", "source", "recruit_type", "raw_tags",
        "external_job_id", "update_time", "sync_status"
    ]:
        frame[col] = frame[col].map(normalize_text)

    frame.loc[(frame["city"] == "") & frame["jd_raw"].str.contains(TARGET_CITY, na=False), "city"] = TARGET_CITY
    frame["city"] = frame["city"].where(frame["city"] != "", frame["jd_raw"].map(extract_city_from_text))
    frame["city"] = frame.apply(lambda r: normalize_city(r["city"], r["jd_raw"]), axis=1)
    frame["name"] = frame["name"].str.replace(r"公司简介.*", "", regex=True)
    frame["name"] = frame["name"].str.replace(r"工作地点[:：].*", "", regex=True)
    frame["name"] = frame["name"].str.replace(r"收起地图.*", "", regex=True)

    frame["responsibility"], frame["requirement"] = zip(*frame["jd_raw"].map(split_jd))
    frame["name"] = frame["name"].where(frame["name"] != "", frame["jd_raw"].str.extract(r"^(.{2,30})")[0].fillna(""))
    frame["name"] = frame["name"].where(frame["name"] != "", "未提取岗位名")
    frame["degree"] = frame.apply(lambda r: extract_degree(r["academic"] or r["jd_raw"]), axis=1)
    frame["major_pref"] = ""
    frame["intern_days"] = frame["jd_raw"].map(extract_intern_days)
    frame["intern_months"] = frame["jd_raw"].map(extract_intern_months)
    frame["graduation_batch"] = frame["jd_raw"].map(extract_graduation_batch)
    cohort_results = frame.apply(enrich_cohort27_fields, axis=1)
    cohort_df = pd.DataFrame(cohort_results.tolist())
    frame = pd.concat([frame, cohort_df], axis=1)
    frame["triggered_rules"] = frame["triggered_rules"].map(lambda x: "|".join(x) if isinstance(x, list) else normalize_text(x))
    frame["is_shanghai"] = frame["city"].str.contains(TARGET_CITY, na=False) | frame["jd_raw"].str.contains(TARGET_CITY, na=False)
    frame["is_big_company"] = frame["company"].map(is_big_company)
    frame["is_27_match"] = frame["jd_raw"].map(is_27_match) | frame["name"].map(is_27_match) | frame["cohort27_confidence"].isin(["high"])
    frame["is_27_inferred"] = frame.apply(infer_27_from_context, axis=1) | frame["cohort27_confidence"].isin(["high", "medium"])

    frame = frame.drop_duplicates(subset=["company", "name", "city", "url"], keep="first")

    out_master = safe_write_csv(frame, "internship_all_master.csv")
    out_legacy = safe_write_csv(frame, "internship_info_all.csv")

    quality = build_quality_report(frame)
    out_quality = safe_write_csv(quality, "data_quality_report.csv")

    target = frame.copy()
    target = target[target["is_shanghai"] & target["is_big_company"] & target["is_27_match"]]
    target["score"] = target.apply(score_row, axis=1)
    target = target.sort_values(by=["score", "company", "name"], ascending=[False, True, True])

    out_target = safe_write_csv(target, "internship_target_jobs.csv")
    strict_27 = frame[(frame["is_shanghai"]) & (frame["is_big_company"]) & (frame["cohort27_confidence"] == "high")].copy()
    strict_27["score"] = strict_27.apply(score_row, axis=1)
    strict_27 = strict_27.sort_values(by=["score", "company", "name"], ascending=[False, True, True])
    out_strict_27 = safe_write_csv(strict_27, "internship_target_strict_27.csv")
    out_a = safe_write_csv(target[target["score"] >= 80], "internship_target_A.csv")
    out_b = safe_write_csv(target[(target["score"] >= 65) & (target["score"] < 80)], "internship_target_B.csv")
    out_c = safe_write_csv(target[target["score"] < 65], "internship_target_C.csv")

    skill_gap = build_skill_gap_report(target)
    out_skill = safe_write_csv(skill_gap, "internship_skill_gap_report.csv")

    potential_27 = frame[(frame["is_shanghai"]) & (frame["is_big_company"]) & (~frame["is_27_match"])].copy()
    potential_27["score"] = potential_27.apply(score_row, axis=1)
    potential_27 = potential_27.sort_values(by=["score", "company", "name"], ascending=[False, True, True])
    out_potential = safe_write_csv(potential_27, "internship_target_potential_27.csv")

    inferred_27 = frame[(frame["is_shanghai"]) & (frame["is_big_company"]) & (frame["is_27_inferred"])].copy()
    inferred_27["score"] = inferred_27.apply(score_row, axis=1)
    inferred_27 = inferred_27.sort_values(by=["score", "company", "name"], ascending=[False, True, True])
    out_inferred = safe_write_csv(inferred_27, "internship_target_inferred_27.csv")

    official_inferred = inferred_27[inferred_27["source"].str.startswith("official", na=False)].copy()
    out_official_inferred = safe_write_csv(official_inferred, "internship_target_official_inferred_27.csv")

    jd_delivery = inferred_27.copy()
    jd_delivery["jd_for_resume"] = jd_delivery["requirement"].where(jd_delivery["requirement"] != "", jd_delivery["jd_raw"])
    jd_delivery = jd_delivery[["company", "name", "city", "source", "score", "jd_for_resume", "url"]]
    jd_delivery = jd_delivery.sort_values(by=["score", "company"], ascending=[False, True])
    out_jd_delivery = safe_write_csv(jd_delivery, "internship_jd_resume_pack.csv")

    autumn_pack = pd.concat([target, official_inferred], axis=0, ignore_index=True)
    autumn_pack = autumn_pack.drop_duplicates(subset=["company", "name", "city", "url"], keep="first")
    autumn_pack = autumn_pack.sort_values(by=["score", "company", "name"], ascending=[False, True, True])
    out_autumn_pack = safe_write_csv(autumn_pack, "internship_autumn_27_bigtech_pack.csv")

    company_summary = (
        target.groupby("company", as_index=False)
        .agg(
            岗位数=("company", "count"),
            平均分=("score", "mean"),
        )
        .sort_values(by=["岗位数", "平均分"], ascending=[False, False])
    )
    company_summary["平均分"] = company_summary["平均分"].round(2)
    out_company_summary = safe_write_csv(company_summary, "internship_target_company_summary.csv")
    dashboard_outputs = generate_kuaishou_dashboard(frame)

    print(f"主库岗位数: {len(frame)} -> {out_master}")
    print(f"兼容总表输出 -> {out_legacy}")
    print(f"目标岗位数: {len(target)} -> {out_target}")
    print(f"严格27届池（高置信）-> {out_strict_27}")
    print(f"质量报表 -> {out_quality}")
    print(f"A/B/C分层 -> {out_a} / {out_b} / {out_c}")
    print(f"能力差距报告 -> {out_skill}")
    print(f"潜在27届候选（大厂上海但未显式届别）-> {out_potential}")
    print(f"推断27届候选（用于扩充投递与JD准备）-> {out_inferred}")
    print(f"官网推断27届候选（优先用于简历准备）-> {out_official_inferred}")
    print(f"简历准备JD包 -> {out_jd_delivery}")
    print(f"秋招大厂综合包 -> {out_autumn_pack}")
    print(f"公司维度汇总 -> {out_company_summary}")
    if dashboard_outputs:
        print(f"快手看板总表 -> {dashboard_outputs['latest']}")
        print(f"快手看板摘要 -> {dashboard_outputs['summary']}")
        print(f"快手新增高置信上海数据岗 -> {dashboard_outputs['new_high']}")
        print(f"快手关闭预警 -> {dashboard_outputs['close_warn']}")


if __name__ == "__main__":
    main()
