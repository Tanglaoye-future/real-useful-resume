"""
Worked example: 实习僧 (shixiseng.com) adapter.

This is the entire site-specific code needed once template_crawler.py is in place.
Read this side-by-side with template_crawler.py to see how the 5 disciplines stay
universal while only the SiteAdapter changes per site.

Run:
    python -m logging.basicConfig
    from template_crawler import Crawler
    from shixiseng_adapter import ShixisengAdapter
    Crawler(ShixisengAdapter(city="上海"), "raw/shixiseng.csv", "logs/ckpt.txt").run(max_pages=200)
"""
from __future__ import annotations

import re
import datetime
from dataclasses import dataclass, field

from bs4 import BeautifulSoup

from template_crawler import SiteAdapter, clean_text


# === Font-glyph map for 实习僧 ================================================
# Extracted from the live WOFF the site loads. The map rotates ~daily; if you
# see □ in salaries or 公司名 again after a few days, re-extract:
#   1. Open https://www.shixiseng.com/interns in DevTools
#   2. Network tab → filter "woff" → copy the .woff URL
#   3. Use fontTools to dump glyph -> unicode mapping, then map private-use
#      codepoints (U+E000..U+F8FF range) to the digits / chars they render as
SHIXISENG_FONT_MAP = {
    # Examples — replace with extracted values for current font:
    # "": "0", "": "1", ..., "": "9",
    # "": "招", "": "聘", ...
    # Leave empty if the current font doesn't substitute, but check first.
}


@dataclass
class ShixisengAdapter(SiteAdapter):
    name: str = "shixiseng"
    base_url: str = "https://www.shixiseng.com/interns"
    city: str = "上海"
    keyword: str = ""
    require_undergrad: bool = True
    list_query: dict = field(default_factory=dict)
    list_selector: str = ".intern-wrap"
    detail_link_selector: str = "a.intern-detail__title"
    font_map: dict = field(default_factory=lambda: dict(SHIXISENG_FONT_MAP))
    rate_limit_seconds: tuple = (5.0, 8.0)

    def __post_init__(self):
        self.list_query = {"page": "{page}", "city": self.city, "keyword": self.keyword}

    # --- list page ----------------------------------------------------------
    def parse_list_card(self, card) -> dict:
        company = ""
        cdiv = card.select_one(".intern-detail__company")
        if cdiv:
            link = cdiv.select_one("a[title]")
            company = link.get("title", "") if link else cdiv.get_text(strip=True)

        name_el = card.select_one(".intern-detail__job, .job_name, .name, .title")
        salary_el = card.select_one(".day_money, .day, .job_money")
        loc_el = card.select_one(".city, .job_city")
        link_el = card.select_one(self.detail_link_selector) or card.select_one("a.job_name, a.name, a.title")

        url = ""
        if link_el and link_el.get("href"):
            href = link_el["href"]
            url = href if href.startswith("http") else f"https://www.shixiseng.com{href}"

        return {
            "company_name": clean_text(company, self.font_map),
            "job_title":    clean_text(name_el.get_text() if name_el else "", self.font_map),
            "salary_range": clean_text(salary_el.get_text() if salary_el else "", self.font_map),
            "location":     clean_text(loc_el.get_text() if loc_el else "", self.font_map),
            "url":          url,
        }

    # --- detail page --------------------------------------------------------
    def parse_detail(self, soup: BeautifulSoup) -> dict:
        out = {}

        addr = soup.select_one(".job_address, .address, .com_position")
        if addr:
            out["location"] = clean_text(addr.get_text(), self.font_map)

        detail = soup.select_one(".job_detail, .job-detail, .detail")
        if detail:
            content = detail.get_text("\n")
            for marker in ("任职要求", "职位要求"):
                if marker in content:
                    parts = content.split(marker, 1)
                    out["responsibilities"] = clean_text(parts[0].replace("岗位职责", ""), self.font_map)
                    out["requirements"] = clean_text(parts[1], self.font_map)
                    break
            else:
                out["responsibilities"] = clean_text(content, self.font_map)

        welfare_els = soup.select(".job_welfare .welfare_item")
        if welfare_els:
            out["benefits"] = " ".join(clean_text(w.get_text(strip=True), self.font_map) for w in welfare_els)

        # Publish time: handles "2025-12-05" and "3天前" / "2小时前"
        pub_el = soup.select_one(".job-header__time, .job_date .cutom_font, .job_update_time, .time, .pub_time")
        if pub_el:
            pub_text = clean_text(pub_el.get_text(), self.font_map)
            m = re.search(r"(20\d{2}-\d{1,2}-\d{1,2})", pub_text)
            if m:
                out["publish_time"] = m.group(1)
            elif "天前" in pub_text:
                d = int(re.search(r"(\d+)天前", pub_text).group(1))
                out["publish_time"] = (datetime.date.today() - datetime.timedelta(days=d)).isoformat()
            elif "小时前" in pub_text or "分钟前" in pub_text:
                out["publish_time"] = datetime.date.today().isoformat()

        body_text = soup.get_text()
        dm = re.search(r"截止日期[：:]\s*(20\d{2}-\d{1,2}-\d{1,2})", body_text)
        if dm:
            out["deadline"] = dm.group(1)

        return out

    # --- filter (raw saved first; this only affects the cleaned output) -----
    def filter_row(self, row: dict) -> bool:
        loc = f"{row.get('location','')}"
        if self.city and self.city not in loc:
            return False
        if self.require_undergrad:
            req = str(row.get("requirements", ""))
            blacklist = ("仅硕士", "仅博士", "仅研究生")
            if any(b in req for b in blacklist):
                return False
        return True


# === CLI entry point ========================================================

if __name__ == "__main__":
    import argparse
    import json
    import logging
    import os
    import sys

    # Force UTF-8 stdout so Chinese chars don't get mangled by Windows GBK console
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    # Make sibling imports work regardless of where the user runs from
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)

    from template_crawler import Crawler, request_with_retry  # noqa: E402

    parser = argparse.ArgumentParser(description="实习僧 crawler (worked example for scrape-with-discipline skill)")
    parser.add_argument("--pages", type=int, default=3, help="Max list pages to crawl (default: 3)")
    parser.add_argument("--city", default="上海")
    parser.add_argument("--keyword", default="")
    parser.add_argument("--dry-run", action="store_true",
                        help="Fetch page 1, parse first 3 cards, print to stdout, do NOT write CSV.")
    parser.add_argument("--font-map", default="font_extract/font_map.json",
                        help="Path to font_map.json (run extract_font_map.py to create it)")
    parser.add_argument("--output", default="raw/shixiseng.csv")
    parser.add_argument("--checkpoint", default="logs/shixiseng_ckpt.txt")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    font_map = {}
    if os.path.exists(args.font_map):
        with open(args.font_map, "r", encoding="utf-8") as f:
            raw = json.load(f)
        font_map = {k: v for k, v in raw.items() if v}
        print(f"Loaded font map: {len(font_map)} filled entries from {args.font_map}")
        if len(raw) > 0 and len(font_map) < len(raw):
            print(f"  WARN: {len(raw) - len(font_map)} slots still empty — fill them in to remove garbled chars")
    else:
        print(f"WARN: {args.font_map} not found.")
        print(f"      Salaries / digits will likely show as garbled chars.")
        print(f"      Run:  python extract_font_map.py")
        print()

    adapter = ShixisengAdapter(city=args.city, keyword=args.keyword)
    adapter.font_map = font_map

    if args.dry_run:
        import requests
        from bs4 import BeautifulSoup
        print(f"\n=== DRY RUN: page 1, first 3 cards, no writes ===\n")
        sess = requests.Session()
        url, params = adapter.build_list_url(1)
        r = request_with_retry(sess, url, params=params, referer=url)
        if not r:
            print("FAIL: list page didn't load. Run verify_setup.py.")
            sys.exit(1)
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select(adapter.list_selector)
        print(f"Selector {adapter.list_selector!r} matched {len(cards)} cards.\n")
        if not cards:
            print("FAIL: 0 cards. Selector is stale. Run verify_setup.py for diagnosis.")
            sys.exit(1)
        for i, card in enumerate(cards[:3]):
            try:
                row = adapter.parse_list_card(card)
                print(f"--- card {i+1} ---")
                for k in ("company_name", "job_title", "salary_range", "location", "url"):
                    print(f"  {k:14s}= {row.get(k, '')!r}")
                print()
            except Exception as e:
                print(f"  PARSE ERROR on card {i+1}: {e}")
        print("Inspect output above:")
        print("  - salary_range numeric and clean? if '□' or weird unicode → fill more font_map slots")
        print("  - company_name / job_title look like normal Chinese? if no → font_map missing 汉字 slots")
        print("  - url starts with https://www.shixiseng.com/intern/inn_ ?")
        print("\nIf all three look good:  python shixiseng_adapter.py --pages 200")
    else:
        Crawler(adapter, args.output, args.checkpoint).run(max_pages=args.pages)
