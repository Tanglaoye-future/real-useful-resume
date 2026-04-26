#!/usr/bin/env python3
"""Foreign-company official-site crawler (Phase 1).

Reads rules/foreign_official_sites_seeds.json and crawls each company's
official career site for Shanghai internships. Outputs CSVs in the existing
20-column schema under outputs/raw/.

Usage:
  python scripts/foreign_official_crawler.py [options]

Options:
  --company NAME       run only the named company (exact match against seed.company)
  --priority P0|P1|P2  limit to a priority bucket (repeatable)
  --industry NAME      limit to an industry (internet|fmcg|hedge_fund)
  --dry-run            list URLs that would be crawled without running Playwright
  --headed             run browser with UI (debug)

Env vars:
  FOREIGN_OVERALL_TIMEOUT_SEC   default 28800 (8h)
  FOREIGN_COMPANY_TIMEOUT_SEC   default 900   (15 min per company)
  FOREIGN_MAX_DETAIL_PER_COMPANY default 200
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from parsers.foreign_company_adapters import BaseForeignAdapter, make_slug
from parsers.foreign_company_registry import get_adapter

SEED_PATH = ROOT / "rules" / "foreign_official_sites_seeds.json"
OUT_DIR = ROOT / "outputs" / "raw"
LOG_DIR = ROOT / "logs"

CSV_COLS = [
    "url", "company", "name", "city", "jd_raw", "salary", "company_size",
    "duration", "academic", "publish_time", "deadline", "collect_time",
    "source", "recruit_type", "raw_tags", "external_job_id", "update_time",
    "publish_time_source", "deadline_source", "sync_status",
]


def load_seeds() -> List[Dict[str, Any]]:
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        return json.load(f).get("seeds", [])


def filter_seeds(
    seeds: List[Dict[str, Any]],
    company: Optional[str],
    priorities: Iterable[str],
    industry: Optional[str],
) -> List[Dict[str, Any]]:
    pri_set = set(priorities) if priorities else None
    out = []
    for s in seeds:
        if company and s.get("company") != company:
            continue
        if pri_set and s.get("priority") not in pri_set:
            continue
        if industry and s.get("industry") != industry:
            continue
        out.append(s)
    return out


def write_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in CSV_COLS})


def open_log(ts: str):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return open(LOG_DIR / f"foreign_official_{ts}.log", "w", encoding="utf-8")


def log(fh, msg: str) -> None:
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    fh.write(line + "\n")
    fh.flush()


def run_dry(seeds: List[Dict[str, Any]]) -> int:
    print(f"DRY RUN — {len(seeds)} companies queued")
    for s in seeds:
        print(f"  [{s['priority']}/{s['industry']}] {s['company']} ({make_slug(s['company'])})")
        for u in s.get("start_urls", []):
            print(f"      -> {u}")
    return 0


def run_company(
    adapter: BaseForeignAdapter,
    page,
    company_timeout: int,
    max_detail: int,
    log_fh,
) -> List[Dict[str, str]]:
    deadline = time.time() + company_timeout
    rows: List[Dict[str, str]] = []
    try:
        all_rows = adapter.crawl(page, max_detail=max_detail)
        for r in all_rows:
            if time.time() > deadline:
                log(log_fh, f"{adapter.slug}: per-company timeout reached, partial result")
                break
            rows.append(r)
    except Exception as e:
        log(log_fh, f"{adapter.slug}: crawl crashed: {e}")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="Foreign-company official-site crawler (Phase 1)")
    ap.add_argument("--company", help="exact company name from seed file")
    ap.add_argument("--priority", action="append", default=[], choices=["P0", "P1", "P2"])
    ap.add_argument("--industry", choices=["internet", "fmcg", "hedge_fund"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--headed", action="store_true")
    args = ap.parse_args()

    overall_budget = int(os.environ.get("FOREIGN_OVERALL_TIMEOUT_SEC", "28800"))
    company_budget = int(os.environ.get("FOREIGN_COMPANY_TIMEOUT_SEC", "900"))
    max_detail = int(os.environ.get("FOREIGN_MAX_DETAIL_PER_COMPANY", "200"))

    seeds = filter_seeds(load_seeds(), args.company, args.priority, args.industry)
    if not seeds:
        print("no seeds matched filters", file=sys.stderr)
        return 2

    if args.dry_run:
        return run_dry(seeds)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_fh = open_log(ts)
    log(log_fh, f"foreign crawl start companies={len(seeds)} overall_budget={overall_budget}s "
                f"company_budget={company_budget}s max_detail={max_detail}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    aggregated: List[Dict[str, str]] = []
    seen_ids: set = set()
    t_start = time.time()

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=not args.headed,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        ctx = browser.new_context(
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
            ),
        )
        page = ctx.new_page()

        for seed in seeds:
            elapsed = time.time() - t_start
            if elapsed >= overall_budget:
                log(log_fh, f"overall budget exhausted at {elapsed:.1f}s; aborting")
                break

            adapter = get_adapter(seed)
            t_co = time.time()
            log(log_fh, f"begin {adapter.slug} ({adapter.priority}/{adapter.industry}) "
                        f"start_urls={len(adapter.start_urls)}")
            try:
                rows = run_company(adapter, page, company_budget, max_detail, log_fh)
            except Exception as e:
                log(log_fh, f"{adapter.slug}: unexpected crash {e}")
                rows = []
            dt = time.time() - t_co

            new = 0
            for r in rows:
                eid = r.get("external_job_id", "")
                if eid and eid in seen_ids:
                    continue
                seen_ids.add(eid)
                aggregated.append(r)
                new += 1

            out_path = OUT_DIR / f"foreign_{adapter.slug}_official_raw.csv"
            write_csv(out_path, rows)
            log(log_fh, f"end {adapter.slug} kept={len(rows)} new={new} "
                        f"t={dt:.1f}s -> {out_path.name}")

        page.close()
        ctx.close()
        browser.close()

    agg_path = OUT_DIR / "foreign_official_aggregated.csv"
    write_csv(agg_path, aggregated)
    log(log_fh, f"aggregated rows={len(aggregated)} -> {agg_path.name}")
    log(log_fh, f"total elapsed={time.time()-t_start:.1f}s")
    log_fh.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
