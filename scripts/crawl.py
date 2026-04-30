#!/usr/bin/env python3
"""
Unified crawler CLI entry point.

All sites require the RPC server:  `python -m crawlers.rpc.server`

Usage
-----
Shixiseng:
    py scripts/crawl.py --site shixiseng [--pages 15] [--city 上海]
    py scripts/crawl.py --site shixiseng --keywords "数据,产品" --pages 5
    py scripts/crawl.py --site shixiseng --dry-run

Liepin:
    py scripts/crawl.py --site liepin [--pages 15] [--resume]
    py scripts/crawl.py --site liepin --keywords "实习,产品,数据"

Yingjiesheng (location-driven; --keyword/--keywords act only as a tag):
    py scripts/crawl.py --site yingjiesheng [--pages 5]
    py scripts/crawl.py --site yingjiesheng --dry-run

Options
-------
--site        Required. One of: shixiseng, liepin, yingjiesheng
--pages       Max list pages per keyword (default: 15)
--city        City filter (default: 上海 for shixiseng, city code 020 for liepin)
--keyword     Single keyword override (shixiseng only — ignored if --keywords set)
--keywords    Comma-separated keyword list (overrides built-in list)
--resume      Resume from checkpoint (default behaviour; flag kept for clarity)
--dry-run     Fetch page 1 and print first 3 parsed cards; write nothing
--output      Override raw output path
--checkpoint  Override checkpoint path
"""
from __future__ import annotations

import argparse
import datetime
import logging
import os
import sys
from pathlib import Path

# Make project root importable regardless of cwd
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%H:%M:%S",
    )
    # Force UTF-8 so Chinese chars are not mangled on Windows GBK console
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Site runners
# ---------------------------------------------------------------------------

def run_shixiseng(args: argparse.Namespace) -> int:
    from crawlers.adapters.shixiseng import (
        ShixisengAdapter, load_font_map, KEYWORDS,
    )
    from crawlers.base.rpc_crawler import RpcCrawler
    from bs4 import BeautifulSoup

    date_tag = datetime.date.today().strftime("%Y%m%d")
    raw_path = args.output or f"data/raw/shixiseng/shixiseng_{date_tag}.jsonl"
    ckpt_path = args.checkpoint or "logs/shixiseng_ckpt.json"
    font_map_path = "logs/shixiseng_font_map.json"

    font_map = load_font_map(font_map_path)
    adapter = ShixisengAdapter(
        city=args.city or "上海",
        keyword=args.keyword or "",
        font_map=font_map,
    )

    logger = logging.getLogger("crawl.shixiseng")

    if args.dry_run:
        logger.info("=== DRY RUN: page 1, first 3 cards, no writes ===")
        # fetch_page goes through the RPC server (must be running).
        result = adapter._client.fetch_list_html(
            page_num=1, city=adapter.city, keyword=adapter.keyword,
        )
        if result.get("error"):
            logger.error("RPC fetch failed: %s", result.get("error"))
            logger.error("Make sure the RPC server is running: python -m crawlers.rpc.server")
            return 1
        if result.get("blocked"):
            logger.error("Blocked by site: %s", result.get("title", ""))
            return 1
        html = result.get("html", "") or ""
        if not html:
            logger.error("RPC returned empty HTML.")
            return 1
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(adapter.list_selector)
        logger.info("Selector %r matched %d cards.", adapter.list_selector, len(cards))
        if not cards:
            logger.error("0 cards — selector may be stale. Inspect the HTML.")
            return 1
        for i, card in enumerate(cards[:3]):
            try:
                row = adapter.parse_list_card(card)
                print(f"\n--- card {i + 1} ---")
                for k, v in row.items():
                    print(f"  {k:20s}= {v!r}")
            except Exception as e:
                print(f"  PARSE ERROR on card {i + 1}: {e}")
        print("\nIf salaries / numbers show □ → fill logs/shixiseng_font_map.json then retry.")
        return 0

    # Pick keywords: --keywords > --keyword > built-in KEYWORDS
    keywords: list[str]
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(",")]
    elif args.keyword:
        keywords = [args.keyword]
    else:
        keywords = KEYWORDS

    max_pages = args.pages or int(os.getenv("SHIXISENG_MAX_PAGES", "15"))

    crawler = RpcCrawler(
        adapter=adapter,
        raw_path=raw_path,
        checkpoint_path=ckpt_path,
        max_pages_per_keyword=max_pages,
    )
    logger.info(
        "Starting shixiseng crawl: %d keywords × up to %d pages each → %s",
        len(keywords), max_pages, raw_path,
    )
    rows = crawler.run(keywords=keywords)
    logger.info("Shixiseng crawl done. %d new unique rows. Raw: %s", len(rows), raw_path)
    return 0


def run_liepin(args: argparse.Namespace) -> int:
    from crawlers.adapters.liepin import LiepinAdapter, KEYWORDS
    from crawlers.base.rpc_crawler import RpcCrawler

    date_tag = datetime.date.today().strftime("%Y%m%d")
    raw_path = args.output or f"data/raw/liepin/liepin_{date_tag}.jsonl"
    ckpt_path = args.checkpoint or "logs/liepin_ckpt.json"

    # Keyword list: --keywords overrides built-in list
    keywords: list[str]
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(",")]
    else:
        keywords = KEYWORDS

    adapter = LiepinAdapter()
    max_pages = args.pages or int(os.getenv("LIEPIN_MAX_PAGES", "15"))

    crawler = RpcCrawler(
        adapter=adapter,
        raw_path=raw_path,
        checkpoint_path=ckpt_path,
        max_pages_per_keyword=max_pages,
    )

    logger = logging.getLogger("crawl.liepin")
    logger.info(
        "Starting liepin crawl: %d keywords × up to %d pages each → %s",
        len(keywords), max_pages, raw_path,
    )

    rows = crawler.run(keywords=keywords)
    logger.info("Liepin crawl done. %d new unique rows. Raw: %s", len(rows), raw_path)
    return 0


def run_yingjiesheng(args: argparse.Namespace) -> int:
    from crawlers.adapters.yingjiesheng import YingjieshengAdapter, KEYWORDS
    from crawlers.base.rpc_crawler import RpcCrawler
    from bs4 import BeautifulSoup

    date_tag = datetime.date.today().strftime("%Y%m%d")
    raw_path = args.output or f"data/raw/yingjiesheng/yingjiesheng_{date_tag}.jsonl"
    ckpt_path = args.checkpoint or "logs/yingjiesheng_ckpt.json"

    adapter = YingjieshengAdapter()
    logger = logging.getLogger("crawl.yingjiesheng")

    if args.dry_run:
        logger.info("=== DRY RUN: page 1, first 3 anchors, no writes ===")
        result = adapter._client.fetch_list_html(page_num=1)
        if result.get("error"):
            logger.error("RPC fetch failed: %s", result.get("error"))
            logger.error("Make sure the RPC server is running: python -m crawlers.rpc.server")
            return 1
        if result.get("blocked"):
            logger.error("Blocked by site: %s", result.get("title", ""))
            return 1
        html = result.get("html", "") or ""
        if not html:
            logger.error("RPC returned empty HTML.")
            return 1
        soup = BeautifulSoup(html, "html.parser")
        anchors = soup.select("a[href]")
        cards: list[dict] = []
        for a in anchors:
            card = adapter.parse_list_card(a)
            if card:
                cards.append(card)
        logger.info("Found %d job links among %d anchors.", len(cards), len(anchors))
        if not cards:
            logger.error("0 job links — list page format may have changed.")
            return 1
        for i, row in enumerate(cards[:3], start=1):
            print(f"\n--- card {i} ---")
            for k, v in row.items():
                print(f"  {k:20s}= {v!r}")
        return 0

    keywords: list[str]
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(",")]
    elif args.keyword:
        keywords = [args.keyword]
    else:
        keywords = KEYWORDS

    max_pages = args.pages or int(os.getenv("YINGJIESHENG_MAX_PAGES", "5"))

    crawler = RpcCrawler(
        adapter=adapter,
        raw_path=raw_path,
        checkpoint_path=ckpt_path,
        max_pages_per_keyword=max_pages,
    )
    logger.info(
        "Starting yingjiesheng crawl: %d keyword tag(s) × up to %d pages → %s",
        len(keywords), max_pages, raw_path,
    )
    rows = crawler.run(keywords=keywords)
    logger.info("Yingjiesheng crawl done. %d new unique rows. Raw: %s", len(rows), raw_path)
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

RUNNERS = {
    "shixiseng":    run_shixiseng,
    "liepin":       run_liepin,
    "yingjiesheng": run_yingjiesheng,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="crawl",
        description="ResuMiner unified crawler CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--site", required=True, choices=list(RUNNERS), metavar="SITE",
                        help=f"Site to crawl. Choices: {', '.join(RUNNERS)}")
    parser.add_argument("--pages",      type=int,  default=None,  help="Max pages per keyword")
    parser.add_argument("--city",       default=None,             help="City filter (shixiseng)")
    parser.add_argument("--keyword",    default=None,             help="Single keyword (shixiseng)")
    parser.add_argument("--keywords",   default=None,
                        help="Comma-separated keyword list (liepin; overrides built-in list)")
    parser.add_argument("--resume",     action="store_true",
                        help="Resume from checkpoint (liepin default; flag is informational)")
    parser.add_argument("--dry-run",    action="store_true",      help="Parse page 1, no writes")
    parser.add_argument("--output",     default=None,             help="Override raw output path")
    parser.add_argument("--checkpoint", default=None,             help="Override checkpoint path")
    parser.add_argument("--log-level",  default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        help="Logging verbosity (default: INFO)")

    args = parser.parse_args(argv)
    _setup_logging(args.log_level)

    runner = RUNNERS[args.site]
    return runner(args)


if __name__ == "__main__":
    raise SystemExit(main())
