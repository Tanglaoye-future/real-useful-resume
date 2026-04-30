#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _utc_ts() -> str:
    return dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _date_tag() -> str:
    return dt.date.today().strftime("%Y%m%d")


def _safe_str(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Selectors:
    job_card: str
    job_card_link: str
    job_card_title: str
    job_card_company: str
    job_card_location: str
    detail_panel: str
    detail_title: str
    detail_company: str
    detail_location: str
    detail_posted_at: str
    detail_description: str
    see_more_button: str

    @staticmethod
    def from_yaml(path: Path) -> "Selectors":
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return Selectors(**data)


def _load_selectors() -> Selectors:
    local = Path(__file__).resolve().parent / "selectors.yaml"
    if local.exists():
        return Selectors.from_yaml(local)
    return Selectors.from_yaml(Path(__file__).resolve().parent / "selectors.example.yaml")


def _jsonl_append(path: Path, rec: dict) -> None:
    _ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _extract_job_id_from_url(url: str) -> str:
    # LinkedIn job view URLs often contain "currentJobId=<id>" or "/view/<id>/"
    if not url:
        return ""
    for key in ("currentJobId=", "jobId="):
        if key in url:
            tail = url.split(key, 1)[1]
            jid = "".join(ch for ch in tail if ch.isdigit())
            if jid:
                return jid
    parts = [p for p in url.split("/") if p]
    for i, p in enumerate(parts):
        if p.lower() == "view" and i + 1 < len(parts):
            cand = "".join(ch for ch in parts[i + 1] if ch.isdigit())
            if cand:
                return cand
    return ""


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="LinkedIn authenticated capture (DOM text + screenshots).")
    ap.add_argument("--start-url", default="https://www.linkedin.com/jobs/", help="Where to open first.")
    ap.add_argument("--interval", type=float, default=4.0, help="Seconds between capture ticks.")
    ap.add_argument("--max-seconds", type=int, default=0, help="Stop after N seconds (0 = run until Ctrl-C).")
    ap.add_argument("--headless", action="store_true", help="Run headless (not recommended for manual browsing).")
    ap.add_argument("--list-only", action="store_true",
                    help="Only parse left-side job cards (title/company/location/url). Don't click open details.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print a few captured rows and exit. No files written.")
    ap.add_argument("--dry-run-n", type=int, default=10,
                    help="How many rows to print in --dry-run mode (default: 10).")
    args = ap.parse_args(argv)

    selectors = _load_selectors()

    out_raw = PROJECT_ROOT / "data" / "raw" / "linkedin" / f"linkedin_{_date_tag()}.jsonl"
    run_id = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_shots = PROJECT_ROOT / "outputs" / "linkedin" / "screenshots" / run_id
    if not args.dry_run:
        _ensure_dir(out_shots)

    # Reusable browser profile so you only login once
    profile_dir = PROJECT_ROOT / "logs" / "linkedin_profile"
    _ensure_dir(profile_dir)

    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout
    except Exception as e:
        print("[!] playwright not installed. Run: pip install -r linkedin/requirements.txt", file=sys.stderr)
        print(f"    import error: {type(e).__name__}: {e}", file=sys.stderr)
        return 2

    seen: set[str] = set()
    started = time.time()

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=args.headless,
            viewport={"width": 1280, "height": 900},
        )
        page = browser.new_page()
        page.goto(args.start_url, wait_until="domcontentloaded")

        print("\n[LinkedIn capture]")
        print("- Login if needed, then navigate to Jobs search results.")
        print("- Scroll/browse at human pace. This script captures every few seconds.")
        print("- Press Ctrl-C to stop.\n")

        tick = 0
        printed = 0
        try:
            while True:
                if args.max_seconds and (time.time() - started) >= args.max_seconds:
                    break

                tick += 1
                ts = _utc_ts()

                # Screenshot (audit trail)
                shot_path: Optional[Path] = None
                if not args.dry_run:
                    shot_path = out_shots / f"{tick:06d}.png"
                    try:
                        page.screenshot(path=str(shot_path), full_page=False)
                    except Exception:
                        # Don't fail capture if screenshots are blocked
                        shot_path = None

                # Extract currently visible job cards
                try:
                    cards = page.locator(selectors.job_card)
                    n = cards.count()
                except Exception:
                    n = 0

                for i in range(min(n, 30)):  # cap per tick; user scroll drives coverage
                    card = cards.nth(i)
                    try:
                        link_el = card.locator(selectors.job_card_link).first
                        href = _safe_str(link_el.get_attribute("href"))
                        if href and href.startswith("/"):
                            href = "https://www.linkedin.com" + href
                    except Exception:
                        href = ""

                    if not href or href in seen:
                        continue

                    # Always extract from the card first (robust for list-only tests)
                    try:
                        title = _safe_str(card.locator(selectors.job_card_title).first.inner_text(timeout=800))
                    except Exception:
                        title = ""
                    try:
                        company = _safe_str(card.locator(selectors.job_card_company).first.inner_text(timeout=800))
                    except Exception:
                        company = ""
                    try:
                        location = _safe_str(card.locator(selectors.job_card_location).first.inner_text(timeout=800))
                    except Exception:
                        location = ""

                    posted_at = ""
                    jd_text = ""

                    if not args.list_only:
                        # Click to load details panel (best-effort)
                        try:
                            link_el.click(timeout=1500)
                        except Exception:
                            pass

                        # Expand "see more" if present (best-effort)
                        try:
                            page.locator(selectors.see_more_button).first.click(timeout=800)
                        except Exception:
                            pass

                        def g(sel: str) -> str:
                            try:
                                return _safe_str(page.locator(sel).first.inner_text(timeout=1200))
                            except Exception:
                                return ""

                        title = g(selectors.detail_title) or title
                        company = g(selectors.detail_company) or company
                        location = g(selectors.detail_location) or location
                        posted_at = g(selectors.detail_posted_at)
                        jd_text = g(selectors.detail_description)

                    rec = {
                        "url": href,
                        "source_job_id": _extract_job_id_from_url(href),
                        "title": title,
                        "company": company,
                        "location": location,
                        "publish_date": posted_at,
                        "jd_text": jd_text,
                        "captured_at": ts,
                        "screenshot_path": (
                            str(shot_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
                            if shot_path else ""
                        ),
                    }

                    if args.dry_run:
                        print(json.dumps(rec, ensure_ascii=False))
                        printed += 1
                        if printed >= max(1, args.dry_run_n):
                            return 0
                    else:
                        _jsonl_append(out_raw, rec)
                    seen.add(href)

                time.sleep(max(1.0, args.interval))
        except KeyboardInterrupt:
            pass
        finally:
            try:
                browser.close()
            except Exception:
                pass

    if not args.dry_run:
        print(f"\nWrote raw records: {out_raw}")
        print(f"Screenshots: {out_shots}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

