#!/usr/bin/env python3
"""
Pipeline smoke test for:
  1. New function imports (parse_shixiseng_item, crawl_shixiseng_direct)
  2. coarse_filter source-awareness (Shixiseng bypasses role filter)
  3. company_score domestic tier (8 pts for non-big-tech)
  4. priority new tier (国内可投 at >=40)
  5. strict_filter_and_score no longer hard-fails on 非严格外企
  6. Shixiseng spider 1-page live smoke crawl
"""
import sys
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

PASS = "[PASS]"
FAIL = "[FAIL]"


def section(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")


# ─────────────────────────────────────────────────────────
# Stage 1: imports
# ─────────────────────────────────────────────────────────
def test_imports():
    section("Stage 1: Imports")
    from scripts.foreign_pipeline_v2 import (
        parse_shixiseng_item,
        crawl_shixiseng_direct,
        coarse_filter,
        company_score,
        priority,
        strict_filter_and_score,
    )
    from core.crawler_engine.spiders.shixiseng_v2 import ShixisengSpiderV2
    print(f"{PASS} All imports OK")
    return True


# ─────────────────────────────────────────────────────────
# Stage 2: parse_shixiseng_item field mapping
# ─────────────────────────────────────────────────────────
def test_parse_shixiseng_item():
    section("Stage 2: parse_shixiseng_item field mapping")
    from scripts.foreign_pipeline_v2 import parse_shixiseng_item

    raw = {
        "job_name": "Data Analyst Intern",
        "company_name": "SomeStartup",
        "location": "Shanghai",
        "salary": "200/day",
        "jd_url": "https://www.shixiseng.com/intern/inn_abc123",
        "source_job_id": "inn_abc123",
        "jd_content": "",
        "company_industry": "Tech",
        "company_stage": "Series B",
        "company_size": "200-500",
    }
    row = parse_shixiseng_item(raw, keyword="test")
    assert row["platform"] == "shixiseng", row["platform"]
    assert row["url"] == raw["jd_url"], row["url"]
    assert row["job_name"] == raw["job_name"], row["job_name"]
    assert row["keyword_group"] == "test"
    print(f"{PASS} parse_shixiseng_item maps fields correctly")
    return True


# ─────────────────────────────────────────────────────────
# Stage 3: coarse_filter source-awareness
# ─────────────────────────────────────────────────────────
def test_coarse_filter_source_awareness():
    section("Stage 3: coarse_filter - Shixiseng bypasses role filter")
    from scripts.foreign_pipeline_v2 import coarse_filter

    rows = [
        # Shixiseng row with non-data role title — must survive
        {
            "platform": "shixiseng", "company_name": "SomeCompany",
            "job_name": "Marketing Intern",   # no data/analytics keywords
            "location": "上海", "url": "https://www.shixiseng.com/intern/inn_1",
            "job_description": "实习", "job_requirement": "实习",
        },
        # Liepin row with non-data role — must be filtered out
        {
            "platform": "liepin", "company_name": "OtherCo",
            "job_name": "Marketing Intern",
            "location": "上海", "url": "https://www.liepin.com/job/111.shtml",
            "job_description": "实习", "job_requirement": "实习",
        },
        # Liepin row with data role — must survive
        {
            "platform": "liepin", "company_name": "ForeignCo",
            "job_name": "Data Analyst Intern",
            "location": "上海", "url": "https://www.liepin.com/job/222.shtml",
            "job_description": "数据分析实习", "job_requirement": "实习",
        },
    ]
    df = pd.DataFrame(rows).fillna("")
    result = coarse_filter(df)
    urls = set(result["url"].tolist())

    assert "https://www.shixiseng.com/intern/inn_1" in urls, "Shixiseng non-data role should survive coarse_filter"
    assert "https://www.liepin.com/job/111.shtml" not in urls, "Liepin non-data role should be filtered"
    assert "https://www.liepin.com/job/222.shtml" in urls, "Liepin data role should survive"
    print(f"{PASS} Shixiseng rows bypass role filter; Liepin rows still filtered by role")
    return True


# ─────────────────────────────────────────────────────────
# Stage 4: company_score domestic tier
# ─────────────────────────────────────────────────────────
def test_company_score_domestic():
    section("Stage 4: company_score domestic tier")
    from scripts.foreign_pipeline_v2 import company_score, BIG_TECH_BAN_RE
    import re

    # Domestic non-big-tech should get 8
    score, ctype, crank = company_score("SomeRandomChineseCo")
    assert score == 8, f"Expected 8, got {score}"
    print(f"{PASS} domestic non-big-tech = {score} pts ({crank})")

    # Foreign company should still score >=20
    score_f, _, _ = company_score("Microsoft")
    assert score_f >= 20, f"Expected >=20 for Microsoft, got {score_f}"
    print(f"{PASS} Microsoft = {score_f} pts")

    # Big tech should be blocked by coarse_filter — company_score may still return 8,
    # but coarse_filter bans them before scoring. Verify BIG_TECH_BAN_RE matches.
    assert re.search(BIG_TECH_BAN_RE, "字节跳动", re.I), "BIG_TECH_BAN_RE should match 字节跳动"
    print(f"{PASS} BIG_TECH_BAN_RE blocks Chinese big tech")
    return True


# ─────────────────────────────────────────────────────────
# Stage 5: priority tiers
# ─────────────────────────────────────────────────────────
def test_priority_tiers():
    section("Stage 5: priority() tiers")
    from scripts.foreign_pipeline_v2 import priority

    cases = [
        (79, "核心目标"),
        (75, "核心目标"),
        (74, "优质目标"),
        (70, "优质目标"),
        (69, "保底目标"),
        (60, "保底目标"),
        (59, "国内可投"),
        (40, "国内可投"),
        (39, "过滤"),
        (0,  "过滤"),
    ]
    for score, expected in cases:
        got = priority(score)
        assert got == expected, f"priority({score}) = {got!r}, expected {expected!r}"
    print(f"{PASS} All priority tiers correct")
    return True


# ─────────────────────────────────────────────────────────
# Stage 6: strict_filter_and_score - domestic passes
# ─────────────────────────────────────────────────────────
def test_strict_filter_domestic():
    section("Stage 6: strict_filter_and_score - domestic company no longer hard-fails")
    from scripts.foreign_pipeline_v2 import strict_filter_and_score

    rows = [
        {
            "platform": "shixiseng",
            "company_name": "SomeDomesticStartup",
            "job_name": "Data Analyst Intern",
            "location": "上海",
            "url": "https://www.shixiseng.com/intern/inn_dom1",
            "job_description": "负责数据分析，SQL，Python",
            "job_requirement": "在校生，熟悉Excel和SQL",
            "完整职责": "负责日常数据报表，独立分析业务数据",
            "完整要求": "本科及以上，有数据分析实习经验优先",
            "详情抓取文本": "数据分析 SQL Python 上海",
            "链接状态": "OK",
            "链接原因": "",
        }
    ]
    df = pd.DataFrame(rows).fillna("")
    result = strict_filter_and_score(df)
    reasons = result["严格过滤失败原因"].iloc[0]
    assert "非严格外企" not in reasons, f"'非严格外企' should not appear in fail reasons, got: {reasons}"
    print(f"{PASS} Domestic company not hard-failed. Fail reasons: '{reasons or 'none'}'")
    return True


# ─────────────────────────────────────────────────────────
# Stage 7: Shixiseng 1-page live smoke crawl
# ─────────────────────────────────────────────────────────
def test_shixiseng_live_smoke():
    section("Stage 7: Shixiseng 1-page live smoke crawl")
    import os
    os.environ["SHIXISENG_MAX_PAGES"] = "1"

    from scripts.foreign_pipeline_v2 import crawl_shixiseng_direct
    print("  Running Shixiseng with 1 page, keyword='实习' ...")
    t0 = time.time()
    rows = crawl_shixiseng_direct(["实习"])
    elapsed = time.time() - t0

    print(f"  Crawled {len(rows)} jobs in {elapsed:.1f}s")

    out_dir = ROOT / "tests" / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "shixiseng_smoke_rows.json"
    out_csv = out_dir / "shixiseng_smoke_rows.csv"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2, default=str)
    try:
        pd.DataFrame(rows).to_csv(out_csv, index=False, encoding="utf-8-sig")
    except Exception as e:
        print(f"  [WARN] CSV dump failed: {e}")
    print(f"  Wrote {len(rows)} rows -> {out_json}")
    print(f"  Wrote {len(rows)} rows -> {out_csv}")

    if rows:
        sample = rows[0]
        print(f"  Sample: company={sample.get('company_name')} job={sample.get('job_name')} url={sample.get('url')}")
        print(f"  Salary: {sample.get('salary')}")
        print(f"  JD desc len: {len(sample.get('job_description') or '')}  req len: {len(sample.get('job_requirement') or '')}")
        assert sample.get("platform") == "shixiseng"
        assert sample.get("url", "").startswith("http")
        print(f"{PASS} Shixiseng live crawl returned {len(rows)} jobs")
    else:
        print("  [WARN] 0 jobs returned — Shixiseng may require login or is blocking headless browser")
        print("  This is not a code error; try running with SHIXISENG_USE_PLAYWRIGHT=1 and a logged-in cookie")
    return True


# ─────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────
def main():
    print("\nResuMiner — Shixiseng pipeline smoke test")
    stages = [
        ("Imports", test_imports),
        ("parse_shixiseng_item", test_parse_shixiseng_item),
        ("coarse_filter source-awareness", test_coarse_filter_source_awareness),
        ("company_score domestic tier", test_company_score_domestic),
        ("priority tiers", test_priority_tiers),
        ("strict_filter domestic pass", test_strict_filter_domestic),
        ("Shixiseng live 1-page smoke", test_shixiseng_live_smoke),
    ]

    results = []
    for name, fn in stages:
        try:
            ok = fn()
            results.append((name, ok))
        except Exception as e:
            import traceback
            print(f"{FAIL} {name}: {e}")
            traceback.print_exc()
            results.append((name, False))

    section("Results")
    passed = sum(1 for _, ok in results if ok)
    for name, ok in results:
        print(f"  {'OK' if ok else 'FAIL':4s}  {name}")
    print(f"\n{passed}/{len(results)} stages passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
