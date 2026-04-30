"""
Generic crawler scaffold enforcing the 5 disciplines.

To adapt to a new site:
  1. Subclass SiteAdapter (see shixiseng_adapter.py for a worked example)
  2. Fill in: base_url, list_selector, field_selectors, detail_selectors,
     font_map (if site uses font anti-bot), filter_row()
  3. Run: Crawler(YourAdapter(), raw_path="...", checkpoint_path="...").run(max_pages=200)

The 5 disciplines are wired into Crawler — you should NOT need to modify it.
"""
from __future__ import annotations

import os
import re
import time
import random
import logging
import datetime
from dataclasses import dataclass, field
from typing import Callable, Optional

import requests
from bs4 import BeautifulSoup
import pandas as pd

logger = logging.getLogger(__name__)

# --- Universal schema. Every row produced has these keys, no more, no less. ---
SCHEMA = [
    "company_name", "job_title", "salary_range", "location",
    "url", "responsibilities", "requirements", "benefits",
    "publish_time", "deadline",
    "source", "address_source", "crawled_at",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
]


def get_headers(referer: str = "") -> dict:
    h = {"User-Agent": random.choice(USER_AGENTS)}
    if referer:
        h["Referer"] = referer
    return h


# === Discipline 3: Decoding stack ============================================

def apply_font_map(text: str, font_map: dict) -> str:
    """Layer 2 of decoding stack: swap private-use-area glyphs back to real chars."""
    if not text or not font_map:
        return text or ""
    for garbled, real in font_map.items():
        text = text.replace(garbled, real)
    return text


def clean_text(text: str, font_map: Optional[dict] = None) -> str:
    """Layer 3 of decoding stack: per-field cleanup. Always wrap callers in try/except."""
    if text is None:
        return ""
    s = str(text).strip().replace("\r", "").replace("\n", " ")
    if font_map:
        s = apply_font_map(s, font_map)
    s = s.replace("&amp;", "&").replace("&nbsp;", " ")
    s = re.sub(r"\s+", " ", s)
    return s


# === Discipline 4: Retry with exponential backoff ============================

def request_with_retry(session: requests.Session, url: str, params=None,
                       referer: str = "", timeout: int = 15, attempts: int = 3):
    for i in range(attempts):
        try:
            r = session.get(url, headers=get_headers(referer), params=params, timeout=timeout)
            r.encoding = "utf-8"  # Layer 1 of decoding stack
            if r.status_code == 200:
                return r
            logger.warning(f"HTTP {r.status_code} on {url} (attempt {i+1})")
        except Exception as e:
            logger.warning(f"Request error on {url}: {e} (attempt {i+1})")
        time.sleep(0.5 * (2 ** i))
    return None


# === SiteAdapter: per-site knobs. Subclass this. ============================

@dataclass
class SiteAdapter:
    """
    Per-site configuration. Subclass and override the fields/methods marked TODO.
    Anything site-agnostic stays in Crawler.
    """
    name: str = "generic"
    base_url: str = ""                        # TODO: list page URL
    list_query: dict = field(default_factory=dict)  # TODO: query params, e.g. {"page": "{page}", "city": "上海"}

    list_selector: str = ""                   # TODO: CSS selector for each job card on list page
    detail_link_selector: str = ""            # TODO: selector for the link to detail page (within a card)

    font_map: dict = field(default_factory=dict)  # TODO: fill if site uses font anti-bot
    rate_limit_seconds: tuple = (5.0, 8.0)    # (min, max) sleep between pages

    def build_list_url(self, page: int) -> tuple[str, dict]:
        params = {k: (v.format(page=page) if isinstance(v, str) else v)
                  for k, v in self.list_query.items()}
        return self.base_url, params

    def parse_list_card(self, card) -> dict:
        """TODO: Extract fields from a single list-page card.
        Return a dict with whatever keys you can fill from the list page.
        Use clean_text(..., self.font_map) for every text field."""
        raise NotImplementedError

    def parse_detail(self, soup: BeautifulSoup) -> dict:
        """TODO: Extract detail-only fields. Return dict with detail-page keys.
        Return {} if this site has no detail page or you don't need it."""
        return {}

    def filter_row(self, row: dict) -> bool:
        """TODO: Site/task-specific filter. Return True to keep, False to drop.
        Default: keep everything (raw-then-filter discipline applies elsewhere)."""
        return True


# === Crawler: site-agnostic engine. Do not edit. =============================

class Crawler:
    def __init__(self, adapter: SiteAdapter, raw_path: str, checkpoint_path: str):
        self.adapter = adapter
        self.raw_path = raw_path
        self.checkpoint_path = checkpoint_path
        self.session = requests.Session()
        os.makedirs(os.path.dirname(raw_path) or ".", exist_ok=True)
        os.makedirs(os.path.dirname(checkpoint_path) or ".", exist_ok=True)

    # Discipline 1: Schema-first ----------------------------------------------
    def normalize(self, raw: dict) -> dict:
        row = {k: "" for k in SCHEMA}
        row.update({k: v for k, v in raw.items() if k in SCHEMA})
        row["source"] = self.adapter.name
        row["crawled_at"] = datetime.datetime.now().isoformat(timespec="seconds")
        missing = [k for k in SCHEMA if not row[k]]
        if missing and not row["url"]:
            logger.warning(f"Row missing url and {missing} — likely parse failure")
        elif len(missing) > 5:
            logger.warning(f"Row {row['url']} missing many fields: {missing}")
        return row

    # Discipline 5: Raw-then-filter (append before filtering) -----------------
    def append_raw(self, rows: list[dict]):
        if not rows:
            return
        df = pd.DataFrame(rows, columns=SCHEMA)
        header = not os.path.exists(self.raw_path)
        df.to_csv(self.raw_path, mode="a", header=header, index=False, encoding="utf-8-sig")

    # Discipline 4: Checkpoint ------------------------------------------------
    def load_checkpoint(self) -> int:
        if not os.path.exists(self.checkpoint_path):
            return 0
        try:
            return int(open(self.checkpoint_path).read().strip())
        except Exception:
            return 0

    def save_checkpoint(self, page: int):
        with open(self.checkpoint_path, "w") as f:
            f.write(str(page))

    # Discipline 2: List + detail layering ------------------------------------
    def crawl_one_card(self, card) -> Optional[dict]:
        try:
            list_fields = self.adapter.parse_list_card(card)
        except Exception as e:
            logger.error(f"List card parse failed: {e}")
            return None

        url = list_fields.get("url", "")
        list_fields["address_source"] = "列表页"

        if url and self.adapter.detail_link_selector is not None:
            time.sleep(random.uniform(0.8, 1.5))
            r = request_with_retry(self.session, url, referer=self.adapter.base_url)
            if r:
                try:
                    detail_fields = self.adapter.parse_detail(BeautifulSoup(r.text, "html.parser"))
                    if detail_fields:
                        list_fields.update(detail_fields)
                        list_fields["address_source"] = "详情页"
                except Exception as e:
                    logger.error(f"Detail parse failed for {url}: {e}")
            # If detail fetch failed, list_fields are kept (fallback rule).
        return list_fields

    # Main loop ---------------------------------------------------------------
    def run(self, max_pages: int = 200, max_empty_pages: int = 5):
        start_page = self.load_checkpoint() + 1
        if start_page > 1:
            logger.info(f"Resuming from page {start_page}")
        empty_streak = 0

        for page in range(start_page, max_pages + 1):
            url, params = self.adapter.build_list_url(page)
            logger.info(f"[{self.adapter.name}] Fetching list page {page}")
            r = request_with_retry(self.session, url, params=params, referer=url)
            if not r:
                logger.error(f"Page {page} failed after retries; skipping")
                time.sleep(random.uniform(*self.adapter.rate_limit_seconds))
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.select(self.adapter.list_selector)
            if not cards:
                empty_streak += 1
                logger.info(f"Page {page} empty ({empty_streak}/{max_empty_pages})")
                if empty_streak >= max_empty_pages:
                    logger.info("Hit empty-page threshold; stopping.")
                    break
                time.sleep(random.uniform(*self.adapter.rate_limit_seconds))
                continue
            empty_streak = 0

            page_rows = []
            for card in cards:
                merged = self.crawl_one_card(card)
                if merged is None:
                    continue
                row = self.normalize(merged)
                # Filter happens AFTER append-raw — but we keep raw separately.
                # If you want pre-filter raw + post-filter clean, save row first
                # then check filter. Here we save everything raw.
                page_rows.append(row)

            self.append_raw(page_rows)
            kept = sum(1 for r in page_rows if self.adapter.filter_row(r))
            logger.info(f"Page {page}: {len(page_rows)} parsed, {kept} would pass filter")

            self.save_checkpoint(page)
            time.sleep(random.uniform(*self.adapter.rate_limit_seconds))

        logger.info("Crawl finished.")


def filter_raw_to_clean(raw_path: str, clean_path: str, adapter: SiteAdapter):
    """Discipline 5 part 2: Apply filter as a separate pass on the raw CSV."""
    df = pd.read_csv(raw_path)
    rows = df.to_dict("records")
    kept = [r for r in rows if adapter.filter_row(r)]
    out = pd.DataFrame(kept, columns=SCHEMA)
    out.drop_duplicates(subset=["url"], inplace=True)
    out.to_csv(clean_path, index=False, encoding="utf-8-sig")
    logger.info(f"Filtered {len(df)} → {len(out)} rows; wrote {clean_path}")
    return out
