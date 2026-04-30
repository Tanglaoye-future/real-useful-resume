"""Overnight sequential full crawl + ingest.

Run with:
    python scripts/run_overnight.py

Sequence (each step must pass before the next starts):
    1. shixiseng  — default 15 pages × 13 keywords
    2. yingjiesheng — 10 pages
    3. liepin     — default 15 pages
    4. ingest_all — normalise + dedup → jobs.parquet

All stdout/stderr are tee'd to logs/overnight_<timestamp>.log so you can
review in the morning.
"""
from __future__ import annotations

import datetime
import json
import logging
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = LOGS / f"overnight_full_{ts}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
    datefmt="%H:%M:%S",
)
log = logging.getLogger("overnight")


def _reset_checkpoint(name: str):
    """Delete a checkpoint file so the crawler starts from scratch."""
    ckpt = LOGS / f"{name}_ckpt.json"
    if ckpt.exists():
        ckpt.unlink()
        log.info("Cleared checkpoint: %s", ckpt.name)
    else:
        log.info("No checkpoint to clear for %s", name)


def run_step(label: str, cmd: list[str], timeout_hours: float = 8.0) -> bool:
    """Run a subprocess step.  Returns True on success."""
    log.info("=" * 60)
    log.info("STEP: %s", label)
    log.info("CMD : %s", " ".join(cmd))
    log.info("=" * 60)
    t0 = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=str(ROOT),
            timeout=timeout_hours * 3600,
            check=False,
        )
        elapsed = time.time() - t0
        if result.returncode == 0:
            log.info("PASS (%s) in %.1f min", label, elapsed / 60)
            return True
        else:
            log.error("FAIL (%s) rc=%d after %.1f min", label, result.returncode, elapsed / 60)
            return False
    except subprocess.TimeoutExpired:
        log.error("TIMEOUT (%s) after %.1fh", label, timeout_hours)
        return False
    except Exception as e:
        log.error("ERROR (%s): %s", label, e)
        return False


def main():
    log.info("Overnight full crawl started — log: %s", LOG_FILE.name)
    log.info("Python: %s", sys.executable)
    log.info("CWD: %s", ROOT)

    results: dict[str, bool] = {}

    # ── 1. Shixiseng ─────────────────────────────────────────────────────
    _reset_checkpoint("shixiseng")
    results["shixiseng"] = run_step(
        "shixiseng full (15 pages × 13 keywords)",
        [sys.executable, "scripts/crawl.py", "--site", "shixiseng"],
        timeout_hours=7,
    )

    # ── 2. Yingjiesheng ──────────────────────────────────────────────────
    _reset_checkpoint("yingjiesheng")
    results["yingjiesheng"] = run_step(
        "yingjiesheng full (10 pages)",
        [sys.executable, "scripts/crawl.py", "--site", "yingjiesheng", "--pages", "10"],
        timeout_hours=3,
    )

    # ── 3. Liepin ─────────────────────────────────────────────────────────
    results["liepin"] = run_step(
        "liepin full (15 pages, no checkpoint reset — incremental)",
        [sys.executable, "scripts/crawl.py", "--site", "liepin"],
        timeout_hours=4,
    )

    # ── 4. Ingest pipeline ────────────────────────────────────────────────
    any_crawl_ok = any(results.values())
    if any_crawl_ok:
        results["ingest"] = run_step(
            "ingest_all (normalise + dedup → jobs.parquet)",
            [sys.executable, "scripts/ingest_all.py"],
            timeout_hours=1,
        )
    else:
        log.error("All crawlers failed — skipping ingest.")
        results["ingest"] = False

    # ── Final summary ─────────────────────────────────────────────────────
    log.info("")
    log.info("=" * 60)
    log.info("OVERNIGHT SUMMARY")
    log.info("=" * 60)
    for step, ok in results.items():
        status = "PASS" if ok else "FAIL"
        log.info("  %-20s %s", step, status)

    # Count rows produced today
    today = datetime.date.today().strftime("%Y%m%d")
    for site in ("shixiseng", "yingjiesheng", "liepin"):
        raw_dir = ROOT / "data" / "raw" / site
        total = 0
        files = []
        for pat in ("*.jsonl", "*.json"):
            for f in raw_dir.glob(pat):
                if today in f.name or site in f.name:
                    lines = f.read_text("utf-8", errors="replace").strip().splitlines()
                    n = sum(1 for l in lines if l.strip() and not l.startswith("//"))
                    total += n
                    files.append(f"{f.name}({n})")
        log.info("  %-20s raw rows today: %d  [%s]", site, total, ", ".join(files[-3:]))

    # Check jobs.parquet
    unified = ROOT / "data" / "unified" / "jobs.parquet"
    if unified.exists():
        size_kb = unified.stat().st_size // 1024
        log.info("  %-20s jobs.parquet: %d KB", "unified", size_kb)
    else:
        log.info("  %-20s jobs.parquet: NOT FOUND", "unified")

    log.info("")
    log.info("Full log: %s", LOG_FILE)
    all_ok = all(results.values())
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
