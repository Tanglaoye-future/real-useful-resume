"""Shixiseng time-boxed crawl — thin wrapper around the unified CLI.

The original time-budget + ShixisengSpiderV2 logic has been superseded by
scripts/crawl.py.  Use that directly:

    py scripts/crawl.py --site shixiseng --pages 200

The --pages flag controls how many list pages are fetched per keyword.
Checkpoint is written to logs/shixiseng_ckpt.txt after each page.
Raw output goes to data/raw/shixiseng/shixiseng_YYYYMMDD.csv.

Env vars still honoured (passed through to crawl.py):
  SHIXISENG_MAX_PAGES   — overrides --pages
  PYTHONUTF8=1          — set on Windows to avoid GBK crashes
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.crawl import main

if __name__ == "__main__":
    pages = os.getenv("SHIXISENG_MAX_PAGES", "200")
    raise SystemExit(main(["--site", "shixiseng", "--pages", pages]))
