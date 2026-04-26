#!/usr/bin/env python3
"""Time-boxed Shixiseng Shanghai crawl (sweep mode).

Runs a multi-keyword Shanghai crawl until either all keywords complete or the
wall-clock budget is exhausted. Dumps all unique rows to JSONL + CSV under
data/raw/shixiseng/.

Env vars:
  SHIXISENG_TIME_BUDGET_SEC   total wall-clock budget in seconds (default 36000 = 10h)
  SHIXISENG_MAX_PAGES         pages per keyword (default 50; spider auto-stops on exhaustion)
  SHIXISENG_KEYWORDS          comma-separated override of the keyword list
  SHIXISENG_BLOCK_SLEEP_SEC   sleep this long if blocking is suspected (default 300)
"""
import json
import os
import sys
import time
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

# 39-keyword sweep targeting the full Shanghai internship inventory:
# generalist roles + tech + major industries (incl. FMCG).
DEFAULT_KEYWORDS = [
    # Generalist roles
    "实习", "运营", "产品", "设计", "研发", "销售", "市场",
    "财务", "人力", "行政", "法务", "编辑", "翻译", "客服",
    "采购", "教育", "咨询",
    # Tech-specific
    "数据分析", "商业分析", "算法", "前端", "后端", "AI", "测试", "产品经理",
    # Industries
    "投资", "投行", "互联网", "金融", "文娱", "影视", "传媒",
    "游戏", "电商", "新媒体",
    # FMCG
    "快消", "消费品", "零售", "食品", "美妆",
]
_kw_override = os.environ.get("SHIXISENG_KEYWORDS", "").strip()
KEYWORDS = [k.strip() for k in _kw_override.split(",") if k.strip()] if _kw_override else DEFAULT_KEYWORDS

BUDGET_SEC = int(os.environ.get("SHIXISENG_TIME_BUDGET_SEC", "36000"))
BLOCK_SLEEP_SEC = int(os.environ.get("SHIXISENG_BLOCK_SLEEP_SEC", "300"))
os.environ.setdefault("SHIXISENG_MAX_PAGES", "50")

OUT_DIR = ROOT / "data" / "raw" / "shixiseng"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TS = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
JSONL_PATH = OUT_DIR / f"shixiseng_overnight_{TS}.jsonl"
CSV_PATH = OUT_DIR / f"shixiseng_overnight_{TS}.csv"
SUMMARY_PATH = OUT_DIR / f"shixiseng_overnight_{TS}_summary.txt"
LOG_PATH = OUT_DIR / f"shixiseng_overnight_{TS}.log"


def _log(msg: str, log_fh) -> None:
    line = f"[{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    log_fh.write(line + "\n")
    log_fh.flush()


def main() -> int:
    from scripts.foreign_pipeline_v2 import parse_shixiseng_item
    from core.crawler_engine.spiders.shixiseng_v2 import ShixisengSpiderV2

    class _Sched:
        def throttle(self, domain, delay): time.sleep(delay)
        def get_proxy(self): return None

    log_fh = open(LOG_PATH, "w", encoding="utf-8")

    _log(f"keywords ({len(KEYWORDS)}) = {KEYWORDS}", log_fh)
    _log(f"budget={BUDGET_SEC}s  pages_per_kw={os.environ['SHIXISENG_MAX_PAGES']}  "
         f"block_sleep={BLOCK_SLEEP_SEC}s", log_fh)
    _log(f"jsonl -> {JSONL_PATH}", log_fh)

    t_start = time.time()
    seen_urls: set = set()
    per_kw: list[tuple[str, int, float]] = []  # (kw, kept, elapsed)
    total_kept = 0
    consecutive_blocks = 0

    with open(JSONL_PATH, "w", encoding="utf-8") as fh:
        for kw in KEYWORDS:
            elapsed = time.time() - t_start
            if elapsed >= BUDGET_SEC:
                _log(f"budget exhausted at {elapsed:.1f}s before keyword={kw}; stopping", log_fh)
                per_kw.append((kw, 0, 0.0))
                continue

            t_kw = time.time()
            try:
                spider = ShixisengSpiderV2(scheduler=_Sched())
                spider.keyword = kw
                spider.city_query = "上海"
                jobs = spider.run_with_playwright() or []
            except Exception as e:
                _log(f"keyword={kw} crashed: {e}", log_fh)
                per_kw.append((kw, 0, time.time() - t_kw))
                continue

            kept = 0
            for j in jobs:
                row = parse_shixiseng_item(j, keyword=kw)
                u = row.get("url", "")
                if not u or u in seen_urls:
                    continue
                seen_urls.add(u)
                fh.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
                kept += 1
            fh.flush()
            total_kept += kept
            dt_kw = time.time() - t_kw
            per_kw.append((kw, kept, dt_kw))
            _log(f"keyword={kw} jobs={len(jobs)} kept={kept} t={dt_kw:.1f}s "
                 f"(running total={total_kept}, elapsed={time.time()-t_start:.1f}s)", log_fh)

            # Circuit breaker: 0 jobs returned in <10s strongly suggests blocking.
            # (Healthy 1-page crawl ≈ 80s. 0 jobs in <10s means either blocked
            # or keyword genuinely has no Shanghai results — sleep to be safe.)
            if len(jobs) == 0 and dt_kw < 10:
                consecutive_blocks += 1
                _log(f"suspected block (0 jobs in {dt_kw:.1f}s) consecutive={consecutive_blocks}; "
                     f"sleeping {BLOCK_SLEEP_SEC}s", log_fh)
                time.sleep(BLOCK_SLEEP_SEC)
                if consecutive_blocks >= 3:
                    _log("3 consecutive suspected blocks; aborting overnight run early", log_fh)
                    break
            else:
                consecutive_blocks = 0

    elapsed_total = time.time() - t_start

    # CSV view (best-effort — JD text can break CSV; JSONL is canonical)
    try:
        rows = [json.loads(l) for l in open(JSONL_PATH, "r", encoding="utf-8") if l.strip()]
        pd.DataFrame(rows).to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
        _log(f"csv -> {CSV_PATH}", log_fh)
    except Exception as e:
        _log(f"csv export failed: {e}", log_fh)

    lines = []
    lines.append(f"Shixiseng overnight crawl @ {TS}")
    lines.append(f"budget={BUDGET_SEC}s  elapsed={elapsed_total:.1f}s  pages_per_kw={os.environ['SHIXISENG_MAX_PAGES']}")
    lines.append(f"total unique jobs kept: {total_kept}")
    lines.append("")
    lines.append(f"{'keyword':<14} {'kept':>6} {'time_s':>8}")
    for kw, kept, dt_kw in per_kw:
        lines.append(f"{kw:<14} {kept:>6} {dt_kw:>8.1f}")
    summary = "\n".join(lines)
    SUMMARY_PATH.write_text(summary, encoding="utf-8")
    _log("---- summary ----", log_fh)
    for ln in lines:
        _log(ln, log_fh)
    _log(f"artifacts: jsonl={JSONL_PATH}", log_fh)
    _log(f"artifacts: csv={CSV_PATH}", log_fh)
    _log(f"artifacts: summary={SUMMARY_PATH}", log_fh)
    log_fh.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
