from __future__ import annotations

import argparse
from typing import List

from playwright.sync_api import sync_playwright

import config as cfg
from crawler.common import parse_since_days
from crawler.dispatcher import dispatch
from crawler.logger import setup_logger
from crawler.state import CrawlState
from crawler.storage import filter_rows_by_location, load_history_json, merge_by_unique_id, save_csv, save_excel, save_json
from crawler.sources.bytedance_official import crawl_bytedance_official
from crawler.sources.liepin import crawl_liepin
from crawler.sources.nowcoder import crawl_nowcoder
from crawler.sources.shixiseng import crawl_shixiseng


def build_cfg_dict() -> dict:
    return {
        "TIERS": cfg.TIERS,
        "PLATFORMS": cfg.PLATFORMS,
        "CRAWL_RULES": cfg.CRAWL_RULES,
        "INCREMENTAL": cfg.INCREMENTAL,
        "OUTPUT": cfg.OUTPUT,
        "NOWCODER_ENTERPRISE_URLS": cfg.NOWCODER_ENTERPRISE_URLS,
        "THIRD_PARTY_MODE": cfg.THIRD_PARTY_MODE,
        "BLACKLIST_COMPANIES": cfg.BLACKLIST_COMPANIES,
        "WHITELIST_FOREIGN": cfg.WHITELIST_FOREIGN,
        "WHITELIST_UNICORN": cfg.WHITELIST_UNICORN,
        "WHITELIST_SOE_TECH": cfg.WHITELIST_SOE_TECH,
        "PLATFORM_SEARCH_RULES": cfg.PLATFORM_SEARCH_RULES,
        "SHIXISENG_COOKIE": cfg.SHIXISENG_COOKIE,
        "LIEPIN_COOKIE": cfg.LIEPIN_COOKIE,
        "REQUEST_INTERVAL": cfg.REQUEST_INTERVAL,
    }


def run() -> int:
    logger = setup_logger()
    c = build_cfg_dict()

    # 增量模式：默认用“最近N天”的发布时间过滤（仅对配置允许的平台生效），并在输出时做 unique_id 覆盖合并。
    state_path = str(c["INCREMENTAL"]["state_file"])
    state = CrawlState.load(state_path) if c["INCREMENTAL"]["enabled"] else CrawlState()

    since_dt = None
    if c["INCREMENTAL"]["enabled"]:
        since_dt = parse_since_days(int(c["INCREMENTAL"]["default_since_days"]))

    sources_official = {
        "bytedance_official": crawl_bytedance_official,
    }
    sources_third_party = {
        "nowcoder": crawl_nowcoder,
        "shixiseng": crawl_shixiseng,
        "liepin": crawl_liepin,
    }

    all_rows: List[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=bool(c["CRAWL_RULES"]["headless"]), args=["--disable-blink-features=AutomationControlled", "--no-sandbox"])
        context = browser.new_context(locale="zh-CN", timezone_id="Asia/Shanghai")
        try:
            rows, stats = dispatch(
                context=context,
                tiers=c["TIERS"],
                sources_official=sources_official,
                sources_third_party=sources_third_party,
                config_obj=c,
                logger=logger,
                since_dt=since_dt,
            )
            all_rows.extend(rows)
            logger.info("调度完成：companies=%s sources=%s ok=%s fail=%s rows=%s", stats.planned_companies, stats.planned_sources, stats.succeeded_sources, stats.failed_sources, stats.collected_rows)
        finally:
            try:
                browser.close()
            except Exception:
                pass

    latest_json = str(c["OUTPUT"]["latest_json"])
    old_rows = load_history_json(latest_json) if c["INCREMENTAL"]["enabled"] else []
    merged = merge_by_unique_id(old_rows, all_rows)
    merged = filter_rows_by_location(merged, list(c["CRAWL_RULES"].get("location_whitelist", []) or []))
    merged = [r for r in merged if (str(r.get("publish_time", "")).startswith("2026") or str(r.get("publish_time", "")).startswith("2027") or str(r.get("publish_time", "")).startswith("2028") or str(r.get("publish_time", "")).startswith("2029") or str(r.get("publish_time", "")).startswith("203"))]

    save_json(latest_json, merged)
    save_csv(str(c["OUTPUT"]["latest_csv"]), merged)
    save_excel(str(c["OUTPUT"]["latest_excel"]), merged, bool(c["OUTPUT"]["excel_by_tier_sheet"]))

    if c["INCREMENTAL"]["enabled"]:
        state.touch()
        state.save(state_path)

    logger.info("输出完成：json=%s csv=%s excel=%s", c["OUTPUT"]["latest_json"], c["OUTPUT"]["latest_csv"], c["OUTPUT"]["latest_excel"])
    return 0


def run_test_source(source_name: str) -> int:
    logger = setup_logger()
    c = build_cfg_dict()
    if source_name not in {"shixiseng", "liepin"}:
        print(f"unsupported test source: {source_name}")
        return 1

    if source_name == "shixiseng":
        c["PLATFORM_SEARCH_RULES"]["shixiseng"]["pages"] = 2
    if source_name == "liepin":
        c["PLATFORM_SEARCH_RULES"]["liepin"]["pages"] = 2

    fn_map = {
        "shixiseng": crawl_shixiseng,
        "liepin": crawl_liepin,
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=bool(c["CRAWL_RULES"]["headless"]), args=["--disable-blink-features=AutomationControlled", "--no-sandbox"])
        context = browser.new_context(locale="zh-CN", timezone_id="Asia/Shanghai")
        try:
            rows = fn_map[source_name](context, None, c) if source_name in {"shixiseng", "liepin"} else []
            total = len(rows)
            loc_kept = sum(1 for r in rows if "上海" in str(r.get("work_location", "")))
            core_ok = sum(
                1
                for r in rows
                if all(
                    str(r.get(k, "")).strip()
                    for k in ["unique_id", "company_name", "job_name", "recruit_type", "work_location", "delivery_link", "source_platform", "crawl_time", "original_url"]
                )
            )
            print(f"[test:{source_name}] rows={total} location_shanghai={loc_kept} core_fields_ok={core_ok}")
            if rows:
                sample = rows[:5]
                for i, r in enumerate(sample, start=1):
                    print(
                        f"[sample {i}] {r.get('company_name')} | {r.get('job_name')} | {r.get('work_location')} | {r.get('publish_time')} | {r.get('salary_range')} | {r.get('delivery_link')}"
                    )
            else:
                print(f"[test:{source_name}] 暂未抓到数据，请检查Cookie配置、网络状态与平台页面结构。")
        finally:
            try:
                browser.close()
            except Exception:
                pass
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-source", choices=["shixiseng", "liepin"], default="")
    args = parser.parse_args()
    if args.test_source:
        raise SystemExit(run_test_source(args.test_source))
    raise SystemExit(run())
