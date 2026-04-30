"""Yingjiesheng crawler — thin wrapper around the unified CLI.

The original YingjieshengSpiderV2 logic has been superseded by
scripts/crawl.py.  Use that directly:

    py scripts/crawl.py --site yingjiesheng [--pages 50]

Checkpoint: logs/yingjiesheng_ckpt.json (resumes on restart)
Raw output: data/raw/yingjiesheng/yingjiesheng_YYYYMMDD.jsonl

Env vars honoured:
  YINGJIESHENG_MAX_PAGES   — overrides --pages
  PYTHONUTF8=1             — set on Windows to avoid GBK crashes
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
    pages = os.getenv("YINGJIESHENG_MAX_PAGES", "50")
    raise SystemExit(main(["--site", "yingjiesheng", "--pages", pages]))
