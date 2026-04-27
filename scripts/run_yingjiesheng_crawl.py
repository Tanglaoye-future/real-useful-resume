#!/usr/bin/env python3
"""Yingjiesheng (应届生) Shanghai jobs crawler — standalone runner.

The YingjieshengSpiderV2 class lives in core/crawler_engine/spiders/ but was
never wired to a runner (and had a broken import — fixed). This script
mirrors the Shixiseng pattern: simple scheduler stub, time-boxed crawl,
JSONL+CSV+log output to data/raw/yingjiesheng/.

Yingjiesheng is the dominant 校招/应届 board for Chinese fresh-grad/intern
audiences. The list pages emit /job-<id>.html style anchors that the spider
extracts. Volume varies by recruitment season.

Env vars:
  YINGJIESHENG_MAX_PAGES   pages per entry URL (default 5)
  YJS_TIME_BUDGET_SEC      total wall-clock budget (default 1800 = 30 min)
  YJS_ENRICH_DETAILS       run Phase2 detail enrichment (default 1)
  YJS_DETAIL_LIMIT         max detail pages to enrich (default 0 = all)
  YJS_DETAIL_DELAY_SEC     delay between detail pages (default 1.5)
  YJS_DETAIL_TIMEOUT_MS    playwright timeout per detail page (default 45000)
  YJS_INPUT_JSONL          skip Phase1; enrich existing jsonl instead
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

# Windows terminals may default to cp1252; ensure logs/prints don't crash on Chinese.
os.environ.setdefault("PYTHONUTF8", "1")
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

OUT_DIR = ROOT / "data" / "raw" / "yingjiesheng"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BUDGET_SEC = int(os.environ.get("YJS_TIME_BUDGET_SEC", "1800"))
os.environ.setdefault("YINGJIESHENG_MAX_PAGES", "5")

ENRICH_DETAILS = os.environ.get("YJS_ENRICH_DETAILS", "1").strip() != "0"
DETAIL_LIMIT = int(os.environ.get("YJS_DETAIL_LIMIT", "0"))
DETAIL_DELAY_SEC = float(os.environ.get("YJS_DETAIL_DELAY_SEC", "1.5"))
DETAIL_TIMEOUT_MS = int(os.environ.get("YJS_DETAIL_TIMEOUT_MS", "45000"))
INPUT_JSONL = os.environ.get("YJS_INPUT_JSONL", "").strip()


class _SimpleScheduler:
    """Minimal scheduler stub matching what YingjieshengSpiderV2 calls.
    The real RedisScheduler is overkill for a one-shot crawl.
    """
    def throttle(self, domain: str, delay: float) -> None:
        time.sleep(delay)

    def get_proxy(self):
        return None


def _log(fh, msg: str) -> None:
    line = f"[{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    fh.write(line + "\n")
    fh.flush()


def _guess_company_from_title(text: str) -> str:
    """Best-effort: many Yingjiesheng titles are like '[上海]某某公司'."""
    t = (text or "").strip()
    if not t:
        return ""
    if t.startswith("[") and "]" in t:
        after = t.split("]", 1)[1].strip()
        return after
    return ""


def _enrich_details_with_playwright(rows: List[Dict], log_fh) -> List[Dict]:
    """Phase2: visit each jd_url and extract title + JD body."""
    from playwright.sync_api import sync_playwright
    from core.crawler_engine.base_spider import BaseSpider

    # Use BaseSpider helpers (normalize/extract) without needing a full spider instance.
    extractor = BaseSpider(platform_name="应届生", scheduler=_SimpleScheduler())

    total = len(rows)
    target = rows if DETAIL_LIMIT <= 0 else rows[:DETAIL_LIMIT]
    _log(log_fh, f"phase2: enriching details; total={total} target={len(target)} delay={DETAIL_DELAY_SEC}s timeout={DETAIL_TIMEOUT_MS}ms")

    enriched: List[Dict] = []
    ok = 0
    fail = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = browser.new_context(locale="zh-CN", timezone_id="Asia/Shanghai")
        page = context.new_page()
        page.set_default_timeout(DETAIL_TIMEOUT_MS)

        for idx, row in enumerate(rows, start=1):
            if DETAIL_LIMIT > 0 and idx > DETAIL_LIMIT:
                enriched.append(row)
                continue

            url = (row or {}).get("jd_url") or ""
            if not url:
                fail += 1
                enriched.append(row)
                continue

            t0 = time.time()
            try:
                time.sleep(DETAIL_DELAY_SEC)
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(900)

                # Title (best-effort)
                title = ""
                try:
                    h1 = page.query_selector("h1")
                    if h1:
                        title = (h1.inner_text() or "").strip()
                except Exception:
                    title = ""

                # JD body
                html = page.content()
                jd = extractor.extract_jd_content_from_html(html)

                new_row = dict(row)
                if title and len(title) >= 2:
                    new_row["job_name"] = title
                if not new_row.get("company_name"):
                    new_row["company_name"] = _guess_company_from_title(new_row.get("job_name", ""))
                new_row["jd_content"] = jd

                ok += 1
                dt_s = time.time() - t0
                if idx % 10 == 0 or idx == 1:
                    _log(log_fh, f"phase2: {idx}/{len(target)} ok; jd_chars={len(jd)} t={dt_s:.1f}s url={url}")
                enriched.append(new_row)
            except Exception as e:
                fail += 1
                _log(log_fh, f"phase2: {idx}/{len(target)} failed: {e} url={url}")
                enriched.append(row)

        context.close()
        browser.close()

    _log(log_fh, f"phase2 done; ok={ok} fail={fail}")
    return enriched


def main() -> int:
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Always overwrite the latest artifacts (user preference: keep latest only).
    jsonl_path = OUT_DIR / "yingjiesheng_latest.jsonl"
    csv_path = OUT_DIR / "yingjiesheng_latest.csv"
    log_path = OUT_DIR / "yingjiesheng_latest.log"
    summary_path = OUT_DIR / "yingjiesheng_latest_summary.txt"

    enriched_jsonl_path = OUT_DIR / "yingjiesheng_latest_enriched.jsonl"
    enriched_csv_path = OUT_DIR / "yingjiesheng_latest_enriched.csv"
    enriched_summary_path = OUT_DIR / "yingjiesheng_latest_enriched_summary.txt"

    log_fh = open(log_path, "w", encoding="utf-8")
    _log(log_fh, f"start; max_pages={os.environ['YINGJIESHENG_MAX_PAGES']} budget={BUDGET_SEC}s")
    _log(log_fh, f"jsonl -> {jsonl_path}")
    _log(log_fh, f"enrich_details={ENRICH_DETAILS} detail_limit={DETAIL_LIMIT}")
    if INPUT_JSONL:
        _log(log_fh, f"input_jsonl -> {INPUT_JSONL} (skip Phase1 crawl)")

    t_start = time.time()
    jobs: List[Dict] = []

    if INPUT_JSONL:
        try:
            in_path = Path(INPUT_JSONL)
            if not in_path.is_absolute():
                in_path = (ROOT / INPUT_JSONL).resolve()
            for line in in_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    jobs.append(json.loads(line))
        except Exception as e:
            _log(log_fh, f"failed to read input_jsonl: {e}")
            jobs = []
    else:
        from core.crawler_engine.spiders.yingjiesheng_v2 import YingjieshengSpiderV2
        spider = YingjieshengSpiderV2(scheduler=_SimpleScheduler())
        try:
            jobs = spider.run() or []
        except Exception as e:
            _log(log_fh, f"spider.run() crashed: {e}")
            jobs = []

    elapsed = time.time() - t_start
    _log(log_fh, f"spider returned {len(jobs)} raw rows in {elapsed:.1f}s")

    # Dedup by jd_url just in case
    seen: set = set()
    unique: List[Dict] = []
    for j in jobs:
        u = (j or {}).get("jd_url") or (j or {}).get("url") or ""
        if u and u not in seen:
            seen.add(u)
            unique.append(j)

    with open(jsonl_path, "w", encoding="utf-8") as fh:
        for j in unique:
            fh.write(json.dumps(j, ensure_ascii=False, default=str) + "\n")

    try:
        pd.DataFrame(unique).to_csv(csv_path, index=False, encoding="utf-8-sig")
        _log(log_fh, f"csv -> {csv_path}")
    except Exception as e:
        _log(log_fh, f"csv export failed: {e}")

    enriched_rows = unique
    if ENRICH_DETAILS and unique:
        try:
            enriched_rows = _enrich_details_with_playwright(unique, log_fh)
            with open(enriched_jsonl_path, "w", encoding="utf-8") as fh:
                for j in enriched_rows:
                    fh.write(json.dumps(j, ensure_ascii=False, default=str) + "\n")
            _log(log_fh, f"enriched jsonl -> {enriched_jsonl_path}")
            try:
                pd.DataFrame(enriched_rows).to_csv(enriched_csv_path, index=False, encoding="utf-8-sig")
                _log(log_fh, f"enriched csv -> {enriched_csv_path}")
            except Exception as e:
                _log(log_fh, f"enriched csv export failed: {e}")
        except Exception as e:
            _log(log_fh, f"phase2 crashed: {e}")

    summary_lines = [
        f"Yingjiesheng crawl @ {ts}",
        f"max_pages={os.environ['YINGJIESHENG_MAX_PAGES']} budget={BUDGET_SEC}s elapsed={elapsed:.1f}s",
        f"raw rows: {len(jobs)}",
        f"unique by url: {len(unique)}",
        f"phase2 enabled: {ENRICH_DETAILS}  detail_limit={DETAIL_LIMIT}",
        "",
    ]
    if unique:
        summary_lines.append("sample (first 5):")
        for j in unique[:5]:
            summary_lines.append(
                f"  - {(j.get('job_name') or '')[:60]} | {(j.get('jd_url') or '')[:80]}"
            )
    text = "\n".join(summary_lines)
    summary_path.write_text(text, encoding="utf-8")

    # Enriched summary
    if ENRICH_DETAILS and enriched_rows is not unique:
        with_jd = sum(1 for r in enriched_rows if (r.get("jd_content") or "").strip())
        enriched_summary_lines = summary_lines + [
            "",
            f"enriched rows: {len(enriched_rows)}",
            f"rows with jd_content: {with_jd}/{len(enriched_rows)}",
            f"enriched_jsonl: {enriched_jsonl_path}",
            f"enriched_csv: {enriched_csv_path}",
        ]
        enriched_summary_path.write_text("\n".join(enriched_summary_lines), encoding="utf-8")
        _log(log_fh, f"enriched summary -> {enriched_summary_path}")

    _log(log_fh, "---- summary ----")
    for ln in summary_lines:
        _log(log_fh, ln)
    _log(log_fh, f"artifacts: jsonl={jsonl_path}")
    _log(log_fh, f"artifacts: csv={csv_path}")
    _log(log_fh, f"artifacts: summary={summary_path}")
    log_fh.close()

    # Prune older timestamped outputs in this directory.
    try:
        from scripts.output_latest import prune_directory
        prune_directory(
            OUT_DIR,
            keep_paths=[
                jsonl_path,
                csv_path,
                log_path,
                summary_path,
                enriched_jsonl_path,
                enriched_csv_path,
                enriched_summary_path,
            ],
            allow_globs=[
                "yingjiesheng_*.jsonl",
                "yingjiesheng_*.csv",
                "yingjiesheng_*.log",
                "yingjiesheng_*_summary.txt",
            ],
        )
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
