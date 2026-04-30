"""RPC-backed crawler scaffold — Disciplines 1, 4, 5 for Playwright/RPC sites.

For sites that require a live browser (liepin, 51job) we cannot use
`requests.get`; instead a local Playwright RPC server fetches pages.
This module provides the same Discipline guarantees as template_crawler.py
for those sites:

  D1 Schema-first   — every row has all SCHEMA keys, warnings on missing.
  D4 Checkpoint     — JSON checkpoint written after every page/keyword.
  D5 Raw-then-filter — rows appended to JSONL immediately, filter is
                       a separate pass.

Discipline 2 (list+detail layering) is implemented inside each
RpcSiteAdapter subclass because the "list" and "detail" fetches both
go through the same RPC server.

Discipline 3 (decoding stack) is mostly handled by the RPC server
(Playwright already returns decoded UTF-8); adapters apply field-level
clean_text from template_crawler.

Usage
-----
    class LiepinAdapter(RpcSiteAdapter): ...

    RpcCrawler(LiepinAdapter(), "data/raw/liepin/liepin.jsonl",
               "logs/liepin_ckpt.json").run(keywords=KEYWORDS)
"""
from __future__ import annotations

import datetime
import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Universal schema — same contract as template_crawler.SCHEMA where possible
# ---------------------------------------------------------------------------

SCHEMA = [
    "source_job_id", "platform",
    "job_name", "company_name",
    "city", "location",
    "salary",
    "job_description", "job_requirement",
    "education_requirement", "experience_requirement",
    "company_industry", "company_size",
    "job_tags",
    "url",
    "publish_date",
    "source_keyword",
    "address_source",   # "列表页" | "详情页"  (D2 field-provenance tag)
    "crawled_at",
]


# ---------------------------------------------------------------------------
# D1: Schema-first normalizer
# ---------------------------------------------------------------------------

def normalize(raw: dict, source: str) -> dict:
    """Ensure every row has all SCHEMA keys.  Warns on critical missing fields."""
    row: dict = {k: "" for k in SCHEMA}
    row.update({k: v for k, v in raw.items() if k in SCHEMA})
    row["crawled_at"] = datetime.datetime.now().isoformat(timespec="seconds")
    row["platform"] = source

    missing = [k for k in ("source_job_id", "job_name", "company_name", "url")
               if not row.get(k)]
    if missing:
        logger.warning("Row missing critical fields %s: %s", missing, row.get("url") or row)
    return row


# ---------------------------------------------------------------------------
# RpcSiteAdapter — per-site knobs
# ---------------------------------------------------------------------------

@dataclass
class RpcSiteAdapter:
    """Subclass this for each RPC-backed site.

    The only required override is `fetch_page(keyword, page_num)`.
    Everything else has sensible defaults.
    """
    name: str = "rpc_site"
    rpc_url: str = "http://127.0.0.1:5600"
    rate_limit_seconds: tuple = (5.0, 10.0)

    def fetch_page(self, keyword: str, page_num: int) -> tuple[list[dict], bool]:
        """Fetch one search-results page via RPC.

        Returns:
            (jobs, has_next)
              jobs      — list of raw dicts from the site
              has_next  — True if there are more pages
        """
        raise NotImplementedError

    def fetch_detail(self, job: dict) -> dict:
        """Optionally enrich a job dict with detail-page fields.

        Return a (possibly empty) dict of extra fields.
        Default: no-op (returns {}).
        """
        return {}

    def filter_row(self, row: dict) -> bool:
        """Site/task-specific filter.  Default: keep everything."""
        return True


# ---------------------------------------------------------------------------
# D4: Checkpoint helpers
# ---------------------------------------------------------------------------

def load_checkpoint(path: str) -> dict:
    """Load checkpoint dict; returns {} if file absent or corrupt."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning("Checkpoint load failed (%s); starting fresh: %s", path, e)
        return {}


def save_checkpoint(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


# ---------------------------------------------------------------------------
# D5: Raw append
# ---------------------------------------------------------------------------

def append_raw(path: str, rows: list[dict]) -> None:
    """Append rows to a JSONL file immediately (raw-then-filter discipline)."""
    if not rows:
        return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# RpcCrawler — site-agnostic engine
# ---------------------------------------------------------------------------

class RpcCrawler:
    """Pagination engine for RPC-backed sites.

    Keyword-aware: can crawl a list of keywords sequentially, resuming
    from a saved checkpoint.  Within each keyword, pages are fetched until
    `has_next` is False or `no_new_streak_limit` consecutive pages yield
    no new unique job IDs.
    """

    def __init__(
        self,
        adapter: RpcSiteAdapter,
        raw_path: str,
        checkpoint_path: str,
        max_pages_per_keyword: int = 15,
        no_new_streak_limit: int = 3,
        empty_streak_limit: int = 3,
    ):
        self.adapter = adapter
        self.raw_path = raw_path
        self.checkpoint_path = checkpoint_path
        self.max_pages_per_keyword = max_pages_per_keyword
        self.no_new_streak_limit = no_new_streak_limit
        self.empty_streak_limit = empty_streak_limit

    # D1 ----------------------------------------------------------------------
    def _normalize(self, raw: dict) -> dict:
        return normalize(raw, self.adapter.name)

    # D5 ----------------------------------------------------------------------
    def _append_raw(self, rows: list[dict]) -> None:
        append_raw(self.raw_path, rows)

    # D4 ----------------------------------------------------------------------
    def _load_ckpt(self) -> dict:
        return load_checkpoint(self.checkpoint_path)

    def _save_ckpt(self, keyword_idx: int, seen_ids: set) -> None:
        save_checkpoint(self.checkpoint_path, {
            "keyword_idx": keyword_idx,
            "seen_ids": list(seen_ids),
        })

    # Main loop ---------------------------------------------------------------
    def run(self, keywords: list[str]) -> list[dict]:
        """Crawl all keywords sequentially.  Resumes from checkpoint.

        Returns list of all new normalized rows collected this run.
        """
        import random

        ckpt = self._load_ckpt()
        start_kw_idx: int = ckpt.get("keyword_idx", 0)
        seen_ids: set = set(ckpt.get("seen_ids", []))

        if start_kw_idx > 0:
            logger.info(
                "[%s] Resuming from keyword %d/%d, already_seen=%d",
                self.adapter.name, start_kw_idx, len(keywords), len(seen_ids),
            )

        all_new_rows: list[dict] = []

        for kw_idx, keyword in enumerate(keywords):
            if kw_idx < start_kw_idx:
                continue

            logger.info(
                "[%s] === keyword %d/%d: %r (global_seen=%d) ===",
                self.adapter.name, kw_idx + 1, len(keywords), keyword, len(seen_ids),
            )

            kw_new_rows: list[dict] = []
            empty_streak = 0
            no_new_streak = 0

            for page_num in range(1, self.max_pages_per_keyword + 1):
                sleep_s = random.uniform(*self.adapter.rate_limit_seconds)
                logger.info(
                    "[%s] sleeping %.1fs before page %d",
                    self.adapter.name, sleep_s, page_num,
                )
                time.sleep(sleep_s)

                try:
                    jobs, has_next = self.adapter.fetch_page(keyword, page_num)
                except Exception as e:
                    logger.error(
                        "[%s] fetch_page(%r, %d) failed: %s",
                        self.adapter.name, keyword, page_num, e,
                    )
                    empty_streak += 1
                    no_new_streak += 1
                    if empty_streak >= self.empty_streak_limit:
                        logger.info("[%s] empty_streak limit hit; stopping keyword", self.adapter.name)
                        break
                    continue

                if not jobs:
                    empty_streak += 1
                    no_new_streak += 1
                    logger.warning(
                        "[%s] page %d returned 0 jobs, empty_streak=%d",
                        self.adapter.name, page_num, empty_streak,
                    )
                else:
                    empty_streak = 0

                page_new: list[dict] = []
                for raw_job in jobs:
                    # D2: optionally enrich from detail page
                    detail = self.adapter.fetch_detail(raw_job)
                    if detail:
                        raw_job = {**raw_job, **detail}
                        raw_job["address_source"] = "详情页"
                    else:
                        raw_job.setdefault("address_source", "列表页")

                    row = self._normalize(raw_job)
                    jid = row.get("source_job_id") or row.get("url", "")
                    if jid and jid in seen_ids:
                        continue
                    if jid:
                        seen_ids.add(jid)
                    page_new.append(row)

                if page_new:
                    no_new_streak = 0
                    # D5: append raw immediately
                    self._append_raw(page_new)
                    kw_new_rows.extend(page_new)
                    logger.info(
                        "[%s] page %d: +%d new unique (kw_total=%d)",
                        self.adapter.name, page_num, len(page_new), len(kw_new_rows),
                    )
                else:
                    no_new_streak += 1
                    logger.info(
                        "[%s] page %d: 0 new unique (all dup), no_new_streak=%d",
                        self.adapter.name, page_num, no_new_streak,
                    )

                if empty_streak >= self.empty_streak_limit:
                    logger.info("[%s] empty_streak=%d; stopping", self.adapter.name, empty_streak)
                    break
                if no_new_streak >= self.no_new_streak_limit:
                    logger.info("[%s] no_new_streak=%d; stopping", self.adapter.name, no_new_streak)
                    break
                if not has_next:
                    logger.info("[%s] has_next=False; stopping", self.adapter.name)
                    break

            all_new_rows.extend(kw_new_rows)
            logger.info(
                "[%s] keyword %r done: +%d new unique (global_total=%d)",
                self.adapter.name, keyword, len(kw_new_rows), len(all_new_rows),
            )

            # D4: save checkpoint after every keyword
            self._save_ckpt(kw_idx + 1, seen_ids)

        logger.info("[%s] crawl complete: %d total new rows", self.adapter.name, len(all_new_rows))
        return all_new_rows


# ---------------------------------------------------------------------------
# Filter pass (D5 part 2)
# ---------------------------------------------------------------------------

def filter_raw_to_clean(raw_jsonl_path: str, clean_jsonl_path: str,
                         adapter: RpcSiteAdapter) -> list[dict]:
    """Apply adapter.filter_row() as a separate pass on the raw JSONL file."""
    if not os.path.exists(raw_jsonl_path):
        logger.warning("filter_raw_to_clean: %s not found", raw_jsonl_path)
        return []
    rows: list[dict] = []
    with open(raw_jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    kept = [r for r in rows if adapter.filter_row(r)]
    # dedup by url within clean output
    seen: set = set()
    deduped: list[dict] = []
    for r in kept:
        key = r.get("url") or r.get("source_job_id") or ""
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        deduped.append(r)
    os.makedirs(os.path.dirname(clean_jsonl_path) or ".", exist_ok=True)
    with open(clean_jsonl_path, "w", encoding="utf-8") as f:
        for r in deduped:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    logger.info("filter_raw_to_clean: %d -> %d rows; wrote %s",
                len(rows), len(deduped), clean_jsonl_path)
    return deduped
