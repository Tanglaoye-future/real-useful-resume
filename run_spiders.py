import concurrent.futures
import pandas as pd
import threading
import logging
import time
import requests
import os
import sys
import subprocess
import atexit
import json
import glob
from datetime import datetime
from urllib.parse import urlparse
from crawler_engine.scheduler import RedisScheduler
from crawler_engine.base_spider import BaseSpider
from crawler_engine.spiders.boss_v2 import BossSpiderV2
from crawler_engine.spiders.lagou_v2 import LagouSpiderV2
from crawler_engine.spiders.job51_v2 import Job51SpiderV2
from crawler_engine.spiders.shixiseng_v2 import ShixisengSpiderV2
from crawler_engine.spiders.yingjiesheng_v2 import YingjieshengSpiderV2
from crawler_engine.spiders.liepin_v2 import LiepinSpiderV2
from crawler_engine.spiders.linkedin_v2 import LinkedInSpiderV2
from crawler_engine.spiders.zhilian_v2 import ZhilianSpiderV2
from crawler_engine.auto_monitor import auto_monitor
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# from spiders.job51_spider import Job51Spider
# from spiders.zhaopin_spider import ZhaopinSpider
# from spiders.yingjiesheng_spider import YingjieshengSpider
# from spiders.linkedin_spider import LinkedInSpider
# from spiders.liepin_spider import LiepinSpider

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MainScheduler")

# 全局锁，用于写入 CSV 或收集数据
data_lock = threading.Lock()
all_results = []
spider_reports = []
rpc_process = None

def summarize_spider_quality(platform_name, jobs):
    total = len(jobs) if isinstance(jobs, list) else 0
    if total == 0:
        return {
            "platform": platform_name,
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_jobs": 0,
            "quality_score": 0.0,
            "jd_nonempty_rate": 0.0,
            "desc_nonempty_rate": 0.0,
            "req_nonempty_rate": 0.0,
            "salary_nonempty_rate": 0.0,
            "location_nonempty_rate": 0.0,
            "url_valid_rate": 0.0,
            "avg_jd_length": 0.0,
            "note": "本轮该平台无数据"
        }
    jd_nonempty = 0
    desc_nonempty = 0
    req_nonempty = 0
    salary_nonempty = 0
    location_nonempty = 0
    url_valid = 0
    jd_len_sum = 0
    for row in jobs:
        jd = str(row.get("jd_content", "") or "").strip()
        desc = str(row.get("job_description", "") or "").strip()
        req = str(row.get("job_requirement", "") or "").strip()
        salary = str(row.get("salary", "") or "").strip()
        location = str(row.get("location", "") or "").strip()
        jd_url = str(row.get("jd_url", "") or "").strip()
        if len(jd) > 20:
            jd_nonempty += 1
        if len(desc) > 20:
            desc_nonempty += 1
        if len(req) > 10:
            req_nonempty += 1
        if salary:
            salary_nonempty += 1
        if location:
            location_nonempty += 1
        if jd_url.startswith("http"):
            url_valid += 1
        jd_len_sum += len(jd)
    jd_rate = round(jd_nonempty / total, 4)
    desc_rate = round(desc_nonempty / total, 4)
    req_rate = round(req_nonempty / total, 4)
    salary_rate = round(salary_nonempty / total, 4)
    location_rate = round(location_nonempty / total, 4)
    url_rate = round(url_valid / total, 4)
    avg_jd_len = round(jd_len_sum / total, 2)
    quality_score = round(
        jd_rate * 0.35 + desc_rate * 0.2 + req_rate * 0.15 + salary_rate * 0.1 + location_rate * 0.1 + url_rate * 0.1,
        4
    )
    return {
        "platform": platform_name,
        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_jobs": total,
        "quality_score": quality_score,
        "jd_nonempty_rate": jd_rate,
        "desc_nonempty_rate": desc_rate,
        "req_nonempty_rate": req_rate,
        "salary_nonempty_rate": salary_rate,
        "location_nonempty_rate": location_rate,
        "url_valid_rate": url_rate,
        "avg_jd_length": avg_jd_len
    }

def write_spider_quality_report(report):
    output_dir = os.path.join("output", "monitoring")
    os.makedirs(output_dir, exist_ok=True)
    platform_slug = str(report.get("platform", "unknown")).replace("/", "_")
    history_files = sorted(glob.glob(os.path.join(output_dir, f"{platform_slug}_quality_*.json")))
    prev_report = None
    if history_files:
        latest_file = history_files[-1]
        try:
            with open(latest_file, "r", encoding="utf-8") as f:
                prev_report = json.load(f)
        except Exception:
            prev_report = None
    if prev_report:
        compare = {}
        for key in [
            "total_jobs",
            "quality_score",
            "jd_nonempty_rate",
            "desc_nonempty_rate",
            "req_nonempty_rate",
            "salary_nonempty_rate",
            "location_nonempty_rate",
            "url_valid_rate",
            "avg_jd_length"
        ]:
            current_v = float(report.get(key, 0) or 0)
            prev_v = float(prev_report.get(key, 0) or 0)
            compare[f"{key}_prev"] = prev_v
            compare[f"{key}_delta"] = round(current_v - prev_v, 4)
        report["compare_with_previous"] = compare
        report["previous_report_time"] = prev_report.get("crawl_time", "")
    else:
        report["compare_with_previous"] = None
        report["previous_report_time"] = ""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = os.path.join(output_dir, f"{platform_slug}_quality_{ts}.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    score_delta = ""
    if report.get("compare_with_previous"):
        score_delta = report["compare_with_previous"].get("quality_score_delta", 0)
    logger.info(
        f"[监测报告] {report.get('platform')} total={report.get('total_jobs')} "
        f"score={report.get('quality_score')} delta={score_delta} "
        f"jd_rate={report.get('jd_nonempty_rate')} file={json_file}"
    )
    return json_file

def write_overall_quality_summary(reports):
    if not reports:
        return
    output_dir = os.path.join("output", "monitoring")
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = os.path.join(output_dir, f"quality_summary_{ts}.md")

    # 计算整体统计
    total_jobs = sum(x.get('total_jobs', 0) for x in reports)
    avg_quality_score = sum(x.get('quality_score', 0) for x in reports) / len(reports) if reports else 0
    avg_req_rate = sum(x.get('req_nonempty_rate', 0) for x in reports) / len(reports) if reports else 0

    lines = [
        "# 本次爬虫质量总览",
        "",
        f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**总采集数**: {total_jobs}",
        f"**平均质量分**: {avg_quality_score:.4f}",
        f"**任职要求平均完整率**: {avg_req_rate:.2%}",
        "",
        "## 各平台详细数据",
        "",
        "| 平台 | 总数 | 质量分 | 对比上次 | JD完整率 | 描述完整率 | 要求完整率 | 平均JD长度 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for x in reports:
        compare = x.get("compare_with_previous") or {}
        score_delta = compare.get("quality_score_delta")
        score_delta_text = f"{score_delta:+.4f}" if isinstance(score_delta, (int, float)) else "首次"
        lines.append(
            f"| {x.get('platform','')} | {x.get('total_jobs',0)} | {x.get('quality_score',0)} | "
            f"{score_delta_text} | {x.get('jd_nonempty_rate',0)} | {x.get('desc_nonempty_rate',0)} | "
            f"{x.get('req_nonempty_rate',0)} | {x.get('avg_jd_length',0)} |"
        )

    # 添加质量告警
    lines.extend([
        "",
        "## 质量告警",
        ""
    ])

    low_req_rate_platforms = [x for x in reports if x.get('req_nonempty_rate', 0) < 0.95]
    if low_req_rate_platforms:
        lines.append("### ⚠️ 任职要求完整率低于 95% 的平台")
        lines.append("")
        lines.append("| 平台 | 任职要求完整率 | 状态 |")
        lines.append("|---|---|---|")
        for x in low_req_rate_platforms:
            rate = x.get('req_nonempty_rate', 0)
            status = "🔴 严重" if rate < 0.5 else "🟡 警告"
            lines.append(f"| {x.get('platform','')} | {rate:.2%} | {status} |")
        lines.append("")
        lines.append("**建议**: 检查详情页解析逻辑，或增加字段补齐机制。")
    else:
        lines.append("✅ 所有平台任职要求完整率均达到 95% 以上")

    lines.extend([
        "",
        "## 优化建议",
        "",
        "1. **任职要求提取**: 如完整率低于 95%，建议检查 `split_jd_sections()` 方法",
        "2. **详情页获取**: 确保 `fetch_jd_content()` 能正确获取详情页内容",
        "3. **字段校验**: 在最小采集单元后增加字段完整率校验",
        ""
    ])

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info(f"[监测报告] 总览已生成: {summary_file}")

    # 如果任职要求完整率过低，输出告警日志
    if avg_req_rate < 0.95:
        logger.warning(f"[质量告警] 任职要求平均完整率 {avg_req_rate:.2%} 低于 95%，建议检查字段提取逻辑")

def run_spider(spider_instance):
    """
    运行单个爬虫实例的包装函数 - 集成自动监控
    """
    platform_name = spider_instance.platform_name
    
    # 记录平台开始
    auto_monitor.record_platform_start(platform_name)
    
    try:
        logger.info(f"Starting {platform_name} spider in a new thread...")
        jobs = spider_instance.run()
        
        with data_lock:
            all_results.extend(jobs)
            logger.info(f"Collected {len(jobs)} jobs from {platform_name}")
            report = summarize_spider_quality(platform_name, jobs)
            write_spider_quality_report(report)
            spider_reports.append(report)
        
        # 记录平台完成
        auto_monitor.record_platform_complete(platform_name, jobs)
        
    except Exception as e:
        logger.error(f"Spider {platform_name} failed: {e}")
        # 记录平台错误
        auto_monitor.record_platform_error(platform_name, str(e))

def ensure_rpc_ready(rpc_url: str = "http://localhost:5600", timeout_seconds: int = 30):
    deadline = time.time() + timeout_seconds
    last_error = ""
    while time.time() < deadline:
        try:
            resp = requests.get(f"{rpc_url}/health", timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                initialized = data.get("initialized_platforms", [])
                if data.get("ready") and ("job51" in initialized or "lagou" in initialized):
                    logger.info("RPC service is ready and required page initialized.")
                    return
                last_error = f"RPC not ready: {data}"
            else:
                last_error = f"RPC health HTTP {resp.status_code}: {resp.text}"
        except Exception as e:
            last_error = f"RPC health check failed: {e}"
        time.sleep(1)
    raise RuntimeError(f"RPC service unavailable within {timeout_seconds}s. {last_error}")

def start_rpc_background_if_needed():
    global rpc_process
    if rpc_process is not None:
        return
    try:
        requests.get("http://localhost:5600/health", timeout=2)
        return
    except Exception:
        pass
    rpc_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "crawler_engine.rpc.server:app", "--host", "127.0.0.1", "--port", "5600"],
        cwd=os.getcwd(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)

def stop_rpc_background():
    global rpc_process
    if rpc_process is not None and rpc_process.poll() is None:
        try:
            rpc_process.terminate()
        except Exception:
            pass
    rpc_process = None

def enrich_jd_for_all_platforms(results, scheduler):
    if not results:
        return results
    if os.getenv("JD_ENRICH_ENABLED", "1") != "1":
        return results
    max_rows = int(os.getenv("JD_ENRICH_MAX_ROWS", "600"))
    enricher = BaseSpider("JD补全器", scheduler, "")
    platform_referer = {
        "BOSS直聘": "https://www.zhipin.com/",
        "拉勾网": "https://www.lagou.com/",
        "前程无忧": "https://we.51job.com/",
        "猎聘": "https://www.liepin.com/",
        "LinkedIn": "https://www.linkedin.com/jobs/",
        "智联招聘": "https://www.zhaopin.com/",
        "实习僧": "https://www.shixiseng.com/interns",
        "应届生": "https://www.yingjiesheng.com/"
    }
    fixed = 0
    for idx, row in enumerate(results):
        if idx >= max_rows:
            break
        if not isinstance(row, dict):
            continue
        jd_url = str(row.get("jd_url", "") or "").strip()
        if not jd_url:
            continue
        jd_content = str(row.get("jd_content", "") or "").strip()
        parsed = urlparse(jd_url)
        host = parsed.netloc.replace("www.", "")
        if "linkedin.com" in host or "seed=" in jd_url:
            need_fetch = False
        else:
            need_fetch = (len(jd_content) < 80) or ("详情需" in jd_content)
        if need_fetch:
            try:
                referer = platform_referer.get(str(row.get("platform", "")), "")
                detail = enricher.fetch_jd_content(
                    jd_url=jd_url,
                    referer=referer,
                    throttle_host=host,
                    throttle_seconds=0.35
                )
                if detail and len(detail.strip()) >= 40:
                    row["jd_content"] = detail
                    jd_content = detail
                    fixed += 1
            except Exception as e:
                logger.warning(f"JD enrich fetch failed for {jd_url}: {e}")
        if len(str(jd_content).strip()) < 20:
            fallback_text = "\n".join([
                f"岗位名称: {row.get('job_name', '')}",
                f"公司: {row.get('company_name', '')}",
                f"地点: {row.get('location', '')}",
                f"薪资: {row.get('salary', '')}",
                f"关键词: {row.get('source_keyword', '')}",
                f"岗位链接: {jd_url}"
            ]).strip()
            row["jd_content"] = fallback_text
            jd_content = fallback_text
        desc = str(row.get("job_description", "") or "").strip()
        req = str(row.get("job_requirement", "") or "").strip()
        if not desc or not req:
            split_desc, split_req = enricher.split_jd_sections(jd_content)
            if not desc:
                row["job_description"] = split_desc or jd_content
            if not req:
                row["job_requirement"] = split_req
    logger.info(f"JD enrichment finished. fetched_detail_count={fixed}")
    return results

def apply_target_scope_filter(results):
    if not results:
        return results
    if os.getenv("TARGET_SCOPE_FILTER_ENABLED", "1") != "1":
        return results
    intern_terms = ["实习", "应届", "校招", "管培生", "2026届", "2027届", "graduate", "intern"]
    bachelor_terms = ["本科", "学士", "bachelor", "985", "211", "双一流", "硕士", "博士", "master", "phd", "一本"]
    low_edu_terms = ["大专", "中专", "高中", "职高", "中技"]
    elite_terms = ["双一流", "985", "211", "c9", "重点高校", "名校"]
    captcha_terms = ["滑动滑块", "访问验证", "别离开", "验证码", "captcha", "verify"]
    require_elite = os.getenv("TARGET_REQUIRE_ELITE", "1") == "1"
    require_student = os.getenv("TARGET_REQUIRE_STUDENT", "0") == "1"
    keep_inferred = os.getenv("TARGET_KEEP_INFERRED_EDU", "1") == "1"
    keep_review = os.getenv("TARGET_KEEP_REVIEW_EDU", "1") == "1"
    filtered = []
    dropped = 0
    level_counter = {"明确本科及以上": 0, "推断本科及以上": 0, "待人工复核": 0}
    def has_any(text: str, words):
        return any(x in text for x in words)
    for row in results:
        if not isinstance(row, dict):
            continue
        location = str(row.get("location", "") or "")
        city = str(row.get("city", "") or "")
        job_name = str(row.get("job_name", "") or "")
        job_type = str(row.get("job_type", "") or "")
        source_keyword = str(row.get("source_keyword", "") or "")
        edu = str(row.get("education_requirement", "") or "")
        jd = str(row.get("jd_content", "") or "")
        jd_url = str(row.get("jd_url", "") or "")
        blob = "\n".join([location, city, job_name, job_type, source_keyword, edu, jd]).lower()
        if ("nan" == edu.strip().lower()) or ("none" == edu.strip().lower()):
            edu = ""
        if not jd_url.startswith("http"):
            dropped += 1
            continue
        captcha_hit = has_any(blob, [x.lower() for x in captcha_terms])
        if captcha_hit:
            row["jd_content"] = ""
            row["job_description"] = ""
            row["job_requirement"] = ""
            row["jd_quality_tag"] = "待补JD"
        in_shanghai = ("上海" in location) or ("上海" in city) or ("shanghai" in blob)
        is_student = has_any(blob, [x.lower() for x in intern_terms])
        edu_text = str(edu).lower()
        req_text = str(row.get("job_requirement", "") or "").lower()
        has_low_edu = False
        req_low_only = False
        if has_any(edu_text, [x.lower() for x in low_edu_terms]) and (not has_any(edu_text, [x.lower() for x in bachelor_terms])):
            has_low_edu = True
        if (not edu_text) and has_any(req_text, [x.lower() for x in low_edu_terms]) and (not has_any(req_text, [x.lower() for x in bachelor_terms])):
            req_low_only = True
        explicit_bachelor = has_any(edu_text, [x.lower() for x in bachelor_terms])
        explicit_from_jd = has_any(req_text, [x.lower() for x in bachelor_terms])
        if has_low_edu:
            dropped += 1
            continue
        if explicit_bachelor or explicit_from_jd:
            edu_scope_tag = "明确本科及以上"
        else:
            if req_low_only:
                edu_scope_tag = "待人工复核"
            elif len(str(jd).strip()) < 80:
                edu_scope_tag = "待人工复核"
            else:
                edu_scope_tag = "推断本科及以上"
        if edu_scope_tag == "推断本科及以上" and (not keep_inferred):
            dropped += 1
            continue
        if edu_scope_tag == "待人工复核" and (not keep_review):
            dropped += 1
            continue
        elite_school = has_any(blob, [x.lower() for x in elite_terms])
        elite_ok = elite_school if require_elite else True
        student_ok = is_student if require_student else True
        if in_shanghai and student_ok and elite_ok:
            row["education_scope_tag"] = edu_scope_tag
            level_counter[edu_scope_tag] = level_counter.get(edu_scope_tag, 0) + 1
            filtered.append(row)
        else:
            dropped += 1
    logger.info(f"Target scope filter kept={len(filtered)} dropped={dropped} levels={level_counter}")
    return filtered

def validate_job51_basic_completeness(results):
    core_fields = [
        "job_name", "source_job_id", "publish_date", "refresh_time", "job_type",
        "salary", "location", "job_description", "job_requirement", "jd_url", "company_name"
    ]
    kept = []
    rejected = 0
    reason_stats = {}
    for row in results:
        if not isinstance(row, dict):
            rejected += 1
            reason_stats["invalid_row"] = reason_stats.get("invalid_row", 0) + 1
            continue
        missing = 0
        for field in core_fields:
            value = str(row.get(field, "") or "").strip()
            if not value:
                missing += 1
        row["core_missing_count"] = missing
        if missing >= 2:
            rejected += 1
            reason_stats["core_missing_ge_2"] = reason_stats.get("core_missing_ge_2", 0) + 1
            continue
        kept.append(row)
    return kept, {"rejected": rejected, "kept": len(kept), "reason_stats": reason_stats}

def deduplicate_job51_dataframe(df: pd.DataFrame):
    if df.empty:
        return df, 0
    for col in ["company_name", "job_name", "location", "core_complete_rate", "refresh_time", "publish_date"]:
        if col not in df.columns:
            df[col] = ""
    raw_count = len(df)
    df = df[df["company_name"].astype(str).str.strip().astype(bool)]
    df = df[df["job_name"].astype(str).str.strip().astype(bool)]
    df = df[df["location"].astype(str).str.strip().astype(bool)]
    df["refresh_sort"] = pd.to_datetime(df["refresh_time"], errors="coerce")
    df["publish_sort"] = pd.to_datetime(df["publish_date"], errors="coerce")
    df["core_complete_rate"] = pd.to_numeric(df["core_complete_rate"], errors="coerce").fillna(0.0)
    df = df.sort_values(
        by=["company_name", "job_name", "location", "core_complete_rate", "refresh_sort", "publish_sort"],
        ascending=[True, True, True, False, False, False]
    )
    df = df.drop_duplicates(subset=["company_name", "job_name", "location"], keep="first")
    dedup_removed = raw_count - len(df)
    df.drop(columns=["refresh_sort", "publish_sort"], inplace=True, errors="ignore")
    return df, dedup_removed

def write_job51_delivery_outputs(df: pd.DataFrame, stats: dict):
    output_dir = "output"
    monitor_dir = os.path.join(output_dir, "monitoring")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(monitor_dir, exist_ok=True)
    csv_file = os.path.join(output_dir, "job51_shanghai_intern_all_latest.csv")
    json_file = os.path.join(output_dir, "job51_shanghai_intern_all_latest.json")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_json = os.path.join(monitor_dir, f"job51_shanghai_it_run_summary_{ts}.json")
    delivery_md = os.path.join(monitor_dir, f"job51_shanghai_it_delivery_{ts}.md")
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")
    df.to_json(json_file, orient="records", force_ascii=False, indent=2)
    payload = dict(stats)
    payload["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload["final_valid_count"] = int(len(df))
    payload["csv_file"] = csv_file
    payload["json_file"] = json_file
    with open(summary_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    lines = [
        "# 前程无忧上海IT应届生/实习生交付报告",
        "",
        f"- 生成时间: {payload['generated_at']}",
        f"- 总抓取条数: {stats.get('total_collected', 0)}",
        f"- 规则过滤后: {stats.get('valid_after_scope', 0)}",
        f"- 去重后有效条数: {len(df)}",
        "",
        "## 过滤原因分布",
        json.dumps(stats.get("reason_stats", {}), ensure_ascii=False, indent=2)
    ]
    with open(delivery_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return csv_file, json_file, summary_json, delivery_md

def main():
    # 启动自动监控
    auto_monitor.start_monitoring()
    
    # 1. 初始化 Cookie Manager 并获取动态 Cookie
    # (如果当前没有隧道代理，跳过强风控网站的动态 Cookie 获取以节省时间)
    logger.info("Initializing runtime mode...")
    
    # 定义全局变量保存获取到的 Cookie
    dynamic_51job_cookie = ""
    dynamic_lagou_cookie = ""
    dynamic_sxs_cookie = ""

    cookies = {
        "boss": "YOUR_BOSS_COOKIE_HERE",
        "lagou": "tfstk=gDUKaXwd_OXnzA71HejgreD2m0CGjGVexJPXrYDHVReTGSJnV8jee8FmIyD3t2OUb-VX-yjErU3Ez46cnZbDTWurPsrcoapefbGAreiIF2u6g8355Zb0TWOnOsV1ok2X3pcSF4iIVFgsQbdIPDi56AG-g39QF41O6bcBFYtINVtswX3SF8g565MZN4GQF41T1AlSM21KQBGpylZIXFkhcVYWPPhKfGVICs4L7XeZnWa9PUOj9DHbOABKmwxsf7o8zQ8-cWZ4UjwBdTHzW5aQc-6MxvZxwSq8OwTs-yPQc0afU3wxJ8nbRcdWJVutdVh_l_xqIPH3Fyn1iEno5rmjRljNK00KM8aUpQL7h5V08czRHdMzxjuswz5X2Yn54gz0k0SWnxhkA1C943oI_mfdz27D6dFt6xfIA3-rqfltn1CM43oI1fHcO3xy40LA.; sajssdk_2015_cross_new_user=1; sensorsdata2015session=%7B%7D; JSESSIONID=ABAACDGAADHAAHF38DB4325451250DDD5C649A707036956; ssxmod_itna=1-iqGxuDBD27i=GQ6KYQPY5DO3BDWIPijKDXDULqe7tQGcD8gx0Pw7PDk0KaDUOsGy9qqKji0RYdNnxGX=wDA5DnCx7YDt=RcDeenOk5hKkWnl2td3KP2KhIq3B9ikKhH80/Rcusytbwx=pG=dcFHKQ4DHxi8DBIx3h0YDemaDCeDQxirDD4DADibQ4D11DDkD0RIhb8E14GWDmRIDWPDYxDrkFoDR=xD0Pp_DQF3zbDDBrGRKxGiVYM63Uk54dfxyfG4k4G1ED0H=B=xkSMyhTifyz190UWpDl9MDCFE1A3w45wvL83jwlA1WbHzim8iGWD4jixQG=KGtzGPGD7CBtQD4kG=GiHbuK5rHDDWSGDErx1EdV0KwDzuLzydswYbkOoqG=BgxeSsMBxjxwYBQwGel05Do4nnKEExF04=Wvi0wf244D; ssxmod_itna2=1-iqGxuDBD27i=GQ6KYQPY5DO3BDWIPijKDXDULqe7tQGcD8gx0Pw7PDk0KaDUOsGy9qqKji0RYdNKxD31MQiiv_5eDjRwxadQPDsNffAfPdCu8Ph=U3KlpHq0Lr0ccUyURUrULkahP92CNjTsTpcTCOczaO0tx8TsKlYFRZD4KjA=h6q4NQHqN80H9nYQqcHe7fDHXOp4eAyGMOPrzcyGqeeHNtBICxP7s=DGq_ia=i0fifpNfOxhuf3NZaQWCgjdXa1FUCOAou1aMGC73IG8a=kqc8p=YVpaFn7LGPmCuHZlAr8789E_F=D2=5/6AKjNnoKqQie9Daxqe8wxj05FGD130eN5tpvZpf2656vr6Ymh662ELmo1h2Pov0Dia66VA3iSfPcoR6Ir_AdFAgQA=eUnAAt9oL7P2hjg6xfQ0yDhPo2N3IxOD5Uw9WcPOcjQK6SovPmfnUg7q0/5hSfjipL7EPI6ARGLmPqt5K1Pv3n50XjrRCSQqecd2N4B0XeQP/0tbI5/5cxUOrbFhES_iNzoLnDZlt6B7RcrBzrX1EeuYs=S=RKXWQOgcQsfym8PiUjeoLrYX8I4zt9rKOLQx/vM_7v8ugQGyj9Bay5gjxe7xMaUPu_qwL1deLGaT=5X8iPB/nCapYf9ETwOmoj/eiXIa7BWnqRsa6Kj65lHmxxCIEPacrmDeGDSiLQPFhi0bDA80NeBaY7e0BQG7x7AFOvegkRFeITjrdxhBr27xxr87hP47WQYGSWTOIAjF44GBkEA76FMiX1Wtv27qH4Zcb8b=/oHR=t4wiWYmwDo0q/DiexBbIemQooi4eGDD; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2219d15250b1c88-07894c8d8c7f318-26061f51-3686400-19d15250b1e322%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24os%22%3A%22Windows%22%2C%22%24browser%22%3A%22Chrome%22%2C%22%24browser_version%22%3A%22146.0.0.0%22%7D%2C%22%24device_id%22%3A%2219d15250b1c88-07894c8d8c7f318-26061f51-3686400-19d15250b1e322%22%7D; user_trace_token=20260322184427-02d80ada-073b-4e65-93cc-78bc6e665b7d; LGSID=20260322184427-6307b3b9-d28c-43af-bdda-c23828f06f81; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Faccount.lagou.com%2Fv2%2Faccount%2FbindMainAccount.html%3Fcallback%3Dhttps%253A%252F%252Fwww.lagou.com%26token%3Da3ae57774f5f244717027bb39d5aa47a41e0b08e30777d918ec7db83008b3d2172705c53f0a931a09289cdee9d0923c2a2ec96a3afd3f754cb6f51ae96464a72b82289816c9a363f%26oauthType%3DAUTH%5FTYPE%5FWEIXIN%5FUNIONID; LGUID=20260322184427-e992fd49-6f70-4043-9eb4-55eb894fcd1f; _ga=GA1.3.1868136473.1774176268; _gat=1; _ga=GA1.2.1868136473.1774176268; _gid=GA1.2.41025998.1774176268; LGRID=20260322184428-20b29c05-0946-46b2-a9f8-4a36ba8446d4; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1774176268; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1774176268; HMACCOUNT=34C687B2BBBE45E9; _ga_DDLTLJDLHH=GS2.2.s1774176269$o1$g0$t1774176269$j60$l0$h0; ticketGrantingTicketId=_CAS_TGT_TGT-438489f2276047c98008dcefa458b595-20260322184751-_CAS_TGT_; gate_login_token=v1####fbdd9aba07d8824872ae477df6e872a42282756c437beb3b661a3cd59adb65b9; LG_HAS_LOGIN=1",
        "job51": "_c_i_p=020000; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2219d152ab2a31-05f5890664270cc-26061f51-3686400-19d152ab2a44a%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.google.com%2F%22%2C%22%24latest_landing_page%22%3A%22https%3A%2F%2Fwww.51job.com%2F%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTlkMTUyYWIyYTMxLTA1ZjU4OTA2NjQyNzBjYy0yNjA2MWY1MS0zNjg2NDAwLTE5ZDE1MmFiMmE0NGEifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%7D; guid=e50d9d5e6456e2cbaf5067f8da029f52; partner=www_google_com; seo_refer_info_2023=%7B%22referUrl%22%3A%22https%3A%5C%2F%5C%2Fwww.google.com%5C%2F%22%2C%22referHost%22%3A%22www.google.com%22%2C%22landUrl%22%3A%22https%3A%5C%2F%5C%2Fwww.51job.com%5C%2F%22%2C%22landHost%22%3A%22www.51job.com%22%2C%22partner%22%3A%22www_google_com%22%7D; Hm_lvt_1370a11171bd6f2d9b1fe98951541941=1774176615; Hm_lpvt_1370a11171bd6f2d9b1fe98951541941=1774176615; HMACCOUNT=34C687B2BBBE45E9; slife=lastlogindate%3D20260322%26%7C%26; ps=needv%3D0; 51job=cuid%3D270490607%26%7C%26cusername%3Dm5AOY6O6NDJLrji4Tr%252BI3r4yi3Xha5AWZb4rd1DIZ34%253D%26%7C%26cpassword%3D%26%7C%26cname%3DUj8Q2848g57agSoEMTHB0Q%253D%253D%26%7C%26cemail%3Dt%252Bu%252FS03DV9jbSq5%252B%252BMq3wjlB9AipxwoChMphp1VHxEo%253D%26%7C%26cemailstatus%3D0%26%7C%26cnickname%3D%26%7C%26ccry%3D.00Z0EoLldSIs%26%7C%26cconfirmkey%3D10VgsdmAeF0Z6%26%7C%26cautologin%3D1%26%7C%26cenglish%3D0%26%7C%26sex%3D0%26%7C%26cnamekey%3D10AOm9ZEZqX%252FQ%26%7C%26to%3D7af170802bcae3c2786d36d5f4f2156969bfc977%26%7C%26; sensor=createDate%3D2025-12-30%26%7C%26identityType%3D2",
        "zhaopin": "ab_jid=fdcf801a39d83bf7203051e6c40d211d7a89; ab_jid_BFESS=fdcf801a39d83bf7203051e6c40d211d7a89; BAIDUID_BFESS=2056EE0D8601489DC534E49600C067AF:FG=1; ZFY=tkBhhtfqNC:Ao5IvvBDwk3qFlydKv:BbGCOPlKojcejVM:C; H_WISE_SIDS_BFESS=65312_66212_66222_66192_66276_66257_66547_66589_66583_66593_66642_66655_66675_66679_66668_66698_66599_66741; BDUSS_BFESS=npOckgzZUR0OEoyUXlqcXRxemhwTnBFbDRXelVaZ0EwNkRWNi10M0VYcEhBODFwSVFBQUFBJCQAAAAAAAAAAAEAAAA2lXWlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEd2pWlHdqVpa; ab_bid=0d211d7a8a875909a3c361c580a9b9db704d; ab_sr=1.0.1_MDlkZTI4ZjgyYmJjNTk0ODc1NDY1YTViZDg4MjQ5NDRmMWI0MGM5M2I3M2JmMDU5NmY2OTI0ZDg4MjRhMmI3YzAyNGQ0MDdmZTM1ZDNlZjk2MmQxOTkxOWY2M2ZjZjVjMmRiMGQzZDYxNTQwZWU1YTE2ZjEzMzBjMTVkMWQ5NTE3YmM5MTU5YjEzYTBkMTFiYjk2MzFhNGE0ZjNkN2YxYmJhZTI2YzlhMDk0M2JmOWQ5Y2Q3YzBiYjMwNmI0ZjI2",
        "yingjiesheng": "acw_tc=781bad4917741770441283465e2247db69ebd844f8b729a4312e20b6bde1c9; uid=wKhK7mm/yxSxA12hB86vAg==; Hm_lvt_6465b7e5e0e872fc416968a53d4fb422=1774177061; HMACCOUNT=34C687B2BBBE45E9; acw_sc__v2=69bfcb172b78db9b90aaa9c12a20844ed59030db; sajssdk_2015_cross_new_user=1; CookieUuid=16fd78cbfeb958f135525b58719417a3; Yjs_logindata={%22is51jobUserMobile%22:%221%22%2C%22isShowBind51job%22:false%2C%22isNewYJS%22:%220%22}; Yjs_Partner=; YSSN=h8aocqib976ttin1u4fk4ealk6jrudct; Yjs_UAccountId=270490933; Yjs_UToken=b0187ae7edbff63e3634b1a4a3c99784; Yjs_Udate=2025%2F12%2F30; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22270490933%22%2C%22first_id%22%3A%2219d15318b0c21d-0b3a033b10ed1b8-26061f51-3686400-19d15318b0d351%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.google.com%2F%22%2C%22%24latest_landing_page%22%3A%22https%3A%2F%2Fwww.yingjiesheng.com%2F%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTlkMTUzMThiMGMyMWQtMGIzYTAzM2IxMGVkMWI4LTI2MDYxZjUxLTM2ODY0MDAtMTlkMTUzMThiMGQzNTEiLCIkaWRlbnRpdHlfbG9naW5faWQiOiIyNzA0OTA5MzMifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22270490933%22%7D%2C%22%24device_id%22%3A%2219d15318b0c21d-0b3a033b10ed1b8-26061f51-3686400-19d15318b0d351%22%7D; ssxmod_itna=eqUxnDuGex0DcDl4Yq0pF1Kd5/7D7qit+8qkDl=YxA5D8D6DQeGTr0KDBnicQZDgx3GYAlDWqaKQmCDfmYiaeWeDHxY=DUhiTUYD4+KGwD0eG+DD4DWDmWFDnxAQDjxGPnUpNH=DEDm48DWPDYxDrAoKDRxi7DDvdHx07DQy8=DDz=AOq+DGiKQDGPza+2PgkYWB5AxG1T40HNl8qAcYjR901PIS5/h+7DlK0DC9C2hHFrF28grvsr0pW80uezonDYQit+0e4G70KTYRqTBDBem1t5rtNvnze=DDWlnUDD==; ssxmod_itna2=eqUxnDuGex0DcDl4Yq0pF1Kd5/7D7qit+8qD619D0yo07jDLxYFwD===; Hm_lpvt_6465b7e5e0e872fc416968a53d4fb422=1774177117",
        "linkedin": 'bcookie="v=2&96ac5cac-1737-41bc-8fae-b2f301c9f536"; li_sugr=51efd83e-d4bd-41b0-9a00-5d1294225b3b; bscookie="v=1&20251018142238a63edf4b-e118-4f24-8a37-0885a6ed1038AQEmfSjnTka448kT_Xtes-_ZHO2upPcS"; lang=v=2&lang=zh-cn; li_rm=AQEqqYBubBUWYQAAAZ0VMyP7NwF6KieZvkYpJkeeO1yYpzGx_ddVY1j4p9nmIhRTqMbKDvMVn3mLPFxOgDzdJaVQpyd0Tk8EO-RrT2S9S7KNVJ5GRwIWRv1g; JSESSIONID="ajax:5066774426378795507"; __cf_bm=b7ktNWfaCnYimLuKE.fGoxINsC1RsyLucJtjNPbM0FE-1774177166-1.0.1.1-FEoGN.6VKghPR.f.OdttzC508cYqjbYWLIL7Haws_3Gj6pan84F5hGo8gzPIN4DiPlEHTeLyNII32nyKb9S3P942uTvdcKC4JwHle.ckj3Q; AMCVS_14215E3D5995C57C0A495C55%40AdobeOrg=1; AMCV_14215E3D5995C57C0A495C55%40AdobeOrg=-637568504%7CMCIDTS%7C20535%7CMCMID%7C80292257814091341850624917281459253211%7CMCAAMLH-1774781976%7C3%7CMCAAMB-1774781976%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1774184376s%7CNONE%7CvVersion%7C5.1.1; aam_uuid=80441737935951149140604337531266489360; g_state={"i_p":1774184417361,"i_l":1}; liap=true; li_at=AQEDAVzEI1cE8pb6AAABnRU2vzEAAAGdOUNDMVYASTmVp4NqqZVHJkFh6SFO-7nQFx7637zZMDHW4H4vV26Z9JVErjgFRdz9Y-XX8w7Pk_WJQG44UMPNLfkiHMPiC_N8p9ULXx1RybSXsLn4BVdm0m2R; timezone=Asia/Shanghai; li_theme=light; li_theme_set=app; UserMatchHistory=AQJw_iliaoirHgAAAZ0VNvmPt0Iuw-rFBmoy_Awdhz9TDu54j0_Nru8Cx_PlB546DcRVUE-HUzvXU_FeHn5Hj6htSw9KesR3s5HCVLJpJdiqvnN5TVfI_pMTaCok23pP6SIttY224vZEW0_ld2EByuV0_TxXZ3awOJnoRFuW1PI8imW8MJ9CUD_C6eXJA1PJXpz3B-pKnY_uoUcJVD2kmMQF6CwlwRq_SpYrmhJlc5xRXNJctXJYzIh5VPqkMWCMkbNxBoRjOoOuRodfqf3au-ar4kHyuV1qY9bNAuyi4KU6XCPq-yRAK3I6LyJeXOSQi-t9czemVi5uuB4yk3ELw34ld_CT33sqV1xwXrxku3-E2prs8w; AnalyticsSyncHistory=AQIm3e_1johfnAAAAZ0VNvmPRTopmQPXqsDwjaJxDkbtq1ymiUGn2G-Ft2ZRhreiIEl5wnBoVzdXoTn8iCQ3_g; _guid=da30ac99-baf0-4480-86ea-430df01d70de; lms_ads=AQHsR1q0Fwn65wAAAZ0VNvyBr71TDTozXaejLYZ6TZwwLfaYNJYldVP4r4h4EkwYqZsrwTcLsbbktZ6mBF-jjfZ_8xhcFLJi; lms_analytics=AQHsR1q0Fwn65wAAAZ0VNvyBr71TDTozXaejLYZ6TZwwLfaYNJYldVP4r4h4EkwYqZsrwTcLsbbktZ6mBF-jjfZ_8xhcFLJi; lidc="b=OB75:s=O:r=O:a=O:p=O:g=4316:u=12:x=1:i=1774177420:t=1774255846:v=2:sig=AQGOhyXjNaA930ty6QEaqfNmYncqeOPH"; _pxvid=355ca7ae-25de-11f1-8efd-59739475471b; _px3=a964a41b3330179ab7b4c8a6b0102edb93b1a012f57b6e1d176835aee5d605d9:fRV5ysV5mRIaC+qX8qKQGdXi8KP2LShYPc6EPvrsYhCeSU1oSRAKzTEN7nFn2Zuxo3rPWI8+Q16+4cSTAbgFnQ==:1000:5+38NmE8ewnJQuD5qKBpOKeBakwpzENchlv20Nqgfl5h5NfBLl01HmYZhh1uvkvHtQ9XLsFtWthKWTygl04fXxmnTMJTtROCx3pZBbhQ0W0IGiHlLlZ2k52t/AXxOPCn2uwd9yhQmSrm12j0e9qE7ahGQERov8zLMXw+Aw9m9pddnH62ljtTw2QXtnffH7YZEg2F6x4sh87iymiHq3Ea5s8qEjL+hAWsLQ1z1qF/cHkpVDmwwAQR2sSKw15WXRGVHXcczq2ZMTFGesvuWx22Gms9bjpxiDRpgPcz+bgj/KMeW3WZiIVz4LEJXmRqjPGhlysL1dau+BAfh6tkpU497E2jISM+UD8UHpstt4wuB79iL9/h7zFY0d4wqXXudB+ESA73Zb78WegZ59Au6X3V8sfCJX22X2EuxWmzt5Elpqbr+En7XDEs3f5bHE4x3r9mxi7krfLC5Qya0H0HBI9p/TtinMvAc7oSKWG7qWZrGr002bQZ5MEgy9vnWLwNlGN',
        "shixiseng": "utm_source_first=PC; utm_source=PC; utm_campaign=PC; position=pc_default; SXS_XSESSION_ID=2|1:0|10:1774177521|15:SXS_XSESSION_ID|88:NTg5ZTVhNjE3NWNlN2UyYTA0NmVhNGUwYmI5MWY4MzRhNzQ2NGQzMTE1YWYyNWQ2MWVjNjg0NjE2NjViMzBhOQ==|af0e0f73556da3ea79574bffe1c4d0132c77d055c3d60d4fd5120244a8112f3a; SXS_XSESSION_ID_EXP=2|1:0|10:1774177521|19:SXS_XSESSION_ID_EXP|16:MTc3Njc2OTUyMQ==|bf6fec595b754b4329689a563b322cbd63de53e47594ae88011428d0bf5e0b87; affefdgx=usr_ftcwnwllpuat; sxs_usr=2|1:0|10:1774177521|7:sxs_usr|24:dXNyX2Z0Y3dud2xscHVhdA==|47530ce17e92cb3c5563eccbdd850f6aaaa5f9c44a52106a9dd2b14d55e4c2ef; xyz_usr=2|1:0|10:1774177521|7:xyz_usr|40:bzhSbncwRE4zVUVnYkNlRlIwRXJiaXM5VElqUQ==|ee022c98277eaa1c5313d5c36df8d96135bb1d779ed2f4a7b028004f92a96305; userflag=user",
        "liepin": "inited_user=66dfbc382ab19a7e5346c6a285bcc743; __uuid=1773901243763.46; __gc_id=2962bae08254434dbf7400d63981b1a7; need_bind_tel=false; c_flag=bb37a295995fdc3a63eb2e4d3048eeae; imId_0=e547f6fe8234ccaf04e9a2edda78d687; imClientId_0=e547f6fe8234ccaf9d6a977ec539a9af; _ga=GA1.1.1485473.1773905929; _ga_54YTJKWN86=GS2.1.s1773911506$o2$g0$t1773911506$j60$l0$h0; XSRF-TOKEN=5HkUBj23QhmgksyWm7hxVw; acw_tc=7b3975b417741776691994548ec63beeebf9e694916793431d239dad088e74; __sessionId=1774177671491.82; hpo_role-sec_project=sec_project_liepin; hpo_sec_tenant=0; Hm_lvt_a2647413544f5a04f00da7eee0d5e200=1773901324,1774177691; Hm_lpvt_a2647413544f5a04f00da7eee0d5e200=1774177691; HMACCOUNT=34C687B2BBBE45E9; UniqueKey=986a21b6ef39fa4a7ecd4408bb1e9b04; liepin_login_valid=0; lt_auth=u%2BcLaHBUzg387XWI3DZbsq9Fh96rVWTBon9e0BoDgd67WfXm4PziRg%2BOrrUA%2FCoIqxkkI%2FszMLf5Men5znRJ6UQb%2BFGnlJeuv%2Fm9z30DSvpnLsW2vezHg%2FXUQp0lkkAA8nJbpEIL%2BVzO; user_roles=0; user_photo=5f8fa3a9dfb13a7dee343d4808u.png; user_name=%E5%94%90%E5%9C%A3%E6%98%95; new_user=false; inited_user=66dfbc382ab19a7e5346c6a285bcc743; __session_seq=6; __tlg_event_seq=14"
    }
    enable_dynamic_cookie = os.getenv("ENABLE_DYNAMIC_COOKIE", "1") == "1"
    if enable_dynamic_cookie:
        from crawler_engine.services.cookie_manager import CookieManager
        cm = CookieManager()
        try:
            cm.start_browser(headless=True)
            if os.getenv("RUN_LAGOU", "1") == "1":
                ck = cm.get_lagou_cookie()
                if ck:
                    cookies["lagou"] = ck
            if os.getenv("RUN_JOB51", "1") == "1":
                ck = cm.get_51job_cookie()
                if ck:
                    cookies["job51"] = ck
            if os.getenv("RUN_SHIXISENG", "1") == "1":
                ck = cm.get_shixiseng_cookie()
                if ck:
                    cookies["shixiseng"] = ck
        except Exception as e:
            logger.warning(f"Dynamic cookie fetch failed: {e}")
        finally:
            try:
                cm.close_browser()
            except Exception:
                pass

    # 初始化 Redis 调度器
    scheduler = RedisScheduler()

    logger.info("Running in RPC + curl_cffi mode.")
    spiders = []
    # 配置要启用的爬虫平台
    # 只保留：前程无忧(51job)、Boss直聘、猎聘(liepin)
    job51_only_mode = os.getenv("JOB51_ONLY_MODE", "0") == "1"
    run_job51 = os.getenv("RUN_JOB51", "1") == "1"      # 前程无忧 - 启用
    run_boss = os.getenv("RUN_BOSS", "1") == "1"        # Boss直聘 - 启用
    run_liepin = os.getenv("RUN_LIEPIN", "1") == "1"    # 猎聘 - 启用
    # 禁用其他平台
    run_lagou = os.getenv("RUN_LAGOU", "0") == "1"      # 拉勾 - 禁用
    run_linkedin = os.getenv("RUN_LINKEDIN", "0") == "1" # 领英 - 禁用
    run_zhilian = os.getenv("RUN_ZHILIAN", "0") == "1"  # 智联 - 禁用
    run_shixiseng = os.getenv("RUN_SHIXISENG", "0") == "1" # 实习僧 - 禁用
    run_yingjiesheng = os.getenv("RUN_YINGJIESHENG", "0") == "1" # 应届生 - 禁用

    if run_lagou or run_job51:
        try:
            start_rpc_background_if_needed()
            atexit.register(stop_rpc_background)
            ensure_rpc_ready()
        except Exception as e:
            logger.warning(f"RPC unavailable, skip lagou/job51 this round: {e}")
            run_lagou = False
            run_job51 = False

    if run_boss:
        spiders.append(BossSpiderV2(scheduler=scheduler, base_cookie=cookies["boss"]))
    if run_lagou:
        spiders.append(LagouSpiderV2(scheduler=scheduler, base_cookie=cookies["lagou"]))
    if run_job51:
        spiders.append(Job51SpiderV2(scheduler=scheduler, base_cookie=cookies["job51"]))
    if run_liepin:
        spiders.append(LiepinSpiderV2(scheduler=scheduler, base_cookie=cookies["liepin"]))
    if run_linkedin:
        spiders.append(LinkedInSpiderV2(scheduler=scheduler, base_cookie=cookies["linkedin"]))
    if run_zhilian:
        spiders.append(ZhilianSpiderV2(scheduler=scheduler, base_cookie=cookies["zhaopin"]))
    if run_shixiseng:
        spiders.append(ShixisengSpiderV2(scheduler=scheduler, base_cookie=cookies["shixiseng"]))
    if run_yingjiesheng:
        spiders.append(YingjieshengSpiderV2(scheduler=scheduler, base_cookie=cookies["yingjiesheng"]))
    if not spiders:
        logger.warning("No enabled spiders.")
        return

    logger.info("Initializing ThreadPoolExecutor...")
    # 使用 ThreadPoolExecutor 实现平台级并发
    # max_workers 设置为爬虫的数量
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(spiders)) as executor:
        # 提交所有爬虫任务到线程池
        futures = [executor.submit(run_spider, spider) for spider in spiders]
        
        # 等待所有任务完成
        concurrent.futures.wait(futures)

    logger.info(f"All spiders finished. Total jobs collected: {len(all_results)}")
    write_overall_quality_summary(spider_reports)
    enrich_jd_for_all_platforms(all_results, scheduler)
    if job51_only_mode:
        filtered_results = [x for x in all_results if isinstance(x, dict) and x.get("platform") == "前程无忧"]
    else:
        filtered_results = apply_target_scope_filter(all_results)

    # 数据处理与去重
    if filtered_results:
        logger.info("Processing and saving data to CSV...")
        stats = {
            "total_collected": len(filtered_results),
            "valid_after_scope": len(filtered_results),
            "reason_stats": {}
        }
        if job51_only_mode:
            filtered_results, scope_stats = validate_job51_basic_completeness(filtered_results)
            stats["valid_after_scope"] = scope_stats.get("kept", 0)
            stats["reason_stats"] = scope_stats.get("reason_stats", {})
        df = pd.DataFrame(filtered_results)
        for col in BaseSpider.STANDARD_FIELDS:
            if col not in df.columns:
                df[col] = ""
        ordered_cols = BaseSpider.STANDARD_FIELDS + [c for c in df.columns if c not in BaseSpider.STANDARD_FIELDS]
        df = df[ordered_cols]
        
        disable_dedup = os.getenv("OUTPUT_DISABLE_DEDUP", "0") == "1"
        if not disable_dedup:
            initial_count = len(df)
            df = df[df['jd_url'].astype(bool)]
            df.drop_duplicates(subset=['jd_url'], keep='first', inplace=True)
            final_count = len(df)
            logger.info(f"Removed {initial_count - final_count} duplicates.")
        else:
            logger.info("Skipping dedup by OUTPUT_DISABLE_DEDUP=1")
        
        # 保存到 CSV
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'shanghai_intern_jobs.csv')
        append_mode = os.getenv("OUTPUT_APPEND", "0") == "1"
        if append_mode and os.path.exists(output_file):
            old_df = pd.read_csv(output_file, encoding='utf-8-sig')
            df = pd.concat([old_df, df], ignore_index=True)
        try:
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            logger.info(f"Data successfully saved to {output_file}")
        except PermissionError:
            fallback_file = os.path.join(output_dir, f"shanghai_intern_jobs_{int(time.time())}.csv")
            df.to_csv(fallback_file, index=False, encoding='utf-8-sig')
            logger.warning(f"Primary CSV is locked, saved to fallback file: {fallback_file}")
        if job51_only_mode:
            stats["final_after_dedup"] = len(df)
            csv_file, json_file, summary_json, delivery_md = write_job51_delivery_outputs(df, stats)
            logger.info(f"Job51 delivery files generated: {csv_file}, {json_file}, {summary_json}, {delivery_md}")
        if os.getenv("RUN_HIGH_VALUE_REPORT", "1") == "1":
            try:
                from etl.high_value_report import run as run_high_value_report
                report_rc = run_high_value_report()
                if report_rc == 0:
                    logger.info("High value report generated.")
                else:
                    logger.warning(f"High value report returned non-zero code: {report_rc}")
            except Exception as e:
                logger.error(f"High value report failed: {e}")
    else:
        logger.warning("No data collected to save after target scope filter.")
    
    # 完成监控并生成报告
    report_file = auto_monitor.finish_monitoring()
    if report_file:
        logger.info(f"[AutoMonitor] 监控报告已生成: {report_file}")

if __name__ == "__main__":
    main()
