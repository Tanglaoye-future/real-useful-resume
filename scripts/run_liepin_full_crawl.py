"""Run Liepin full crawl via the new adapter architecture.

This script is kept for backward compatibility.
Prefer the unified CLI:
    py scripts/crawl.py --site liepin

Requirements
------------
* RPC server running: python crawlers/rpc/server.py
* Playwright browser launched by the server (headless=False for anti-bot)
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.crawl import main

if __name__ == "__main__":
    raise SystemExit(main(["--site", "liepin"]))
