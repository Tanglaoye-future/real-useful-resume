#!/usr/bin/env python3
"""SmartShanghai jobs crawler — Shanghai internships.

SmartShanghai is a small English-language Shanghai expat board (~28 listings
total). Plain HTTP works — no Playwright, no anti-bot. We walk pagination,
fetch each detail page, parse title/type/JD from HTML, and filter for
internships only.

Output: data/raw/smartshanghai/smartshanghai_latest.{jsonl,csv,log,summary}
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "raw" / "smartshanghai"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE = "https://www.smartshanghai.com"
LIST_URL = f"{BASE}/jobs/list/"
DETAIL_LINK_RE = re.compile(r"/jobs/[a-z-]+/\d+")
INTERN_PATTERN = re.compile(
    r"(?i)\b(?:intern|internship|interns|graduate|trainee|management\s+trainee|new\s+grad)\b|"
    r"实习|校招|校园招聘|应届|校园|暑期"
)
H2_RE = re.compile(r"<h2[^>]*>(.*?)</h2>", re.S)
H3_RE = re.compile(r"<h3[^>]*>(.*?)</h3>", re.S)
TYPE_RE = re.compile(r"Type:\s*([A-Za-z][\w\s/-]*?)(?:\s*Seniority|\s*<)", re.S)
SENIOR_RE = re.compile(r"Seniority:\s*([A-Za-z][\w\s/-]*?)(?:\s*Description|\s*<)", re.S)
DESC_RE = re.compile(r"Description\s*<div[^>]*>(.*?)</div>\s*</div>", re.S)


def strip_html(html: str) -> str:
    text = re.sub(r"<\s*br\s*/?>", "\n", html, flags=re.I)
    text = re.sub(r"</\s*(p|div|li|h[1-6])\s*>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = (
        text.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&#39;", "'")
        .replace("&quot;", '"')
    )
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def collect_listing_links(sess: requests.Session, log_fh) -> List[str]:
    seen: Set[str] = set()
    for page in range(1, 30):
        url = f"{LIST_URL}?page={page}"
        try:
            r = sess.get(url, timeout=20)
        except Exception as e:
            log(log_fh, f"page={page} err: {e}")
            break
        if r.status_code != 200:
            log(log_fh, f"page={page} status={r.status_code}, stop")
            break
        found = set(DETAIL_LINK_RE.findall(r.text))
        new = found - seen
        seen |= found
        log(log_fh, f"list page={page} found={len(found)} new={len(new)} total={len(seen)}")
        if not new:
            break
        time.sleep(0.4)
    return [BASE + p for p in sorted(seen)]


def fetch_detail(sess: requests.Session, url: str) -> Optional[Dict[str, str]]:
    try:
        r = sess.get(url, timeout=20)
    except Exception as e:
        return {"_err": str(e)}
    if r.status_code != 200:
        return {"_err": f"status={r.status_code}"}

    html = r.text

    title = ""
    m = H2_RE.search(html)
    if m:
        title = strip_html(m.group(1))

    company = ""
    for h3 in H3_RE.findall(html):
        clean = strip_html(h3)
        if " at " in clean and len(clean) < 250:
            company = clean.split(" at ", 1)[1].strip()
            break

    job_type = ""
    m = TYPE_RE.search(html)
    if m:
        job_type = m.group(1).strip()

    seniority = ""
    m = SENIOR_RE.search(html)
    if m:
        seniority = m.group(1).strip()

    jd_body = ""
    m = DESC_RE.search(html)
    if m:
        jd_body = strip_html(m.group(1))
    if not jd_body:
        # fallback: grab generous chunk after "Description" keyword
        pos = html.find("Description")
        if pos > 0:
            jd_body = strip_html(html[pos:pos + 6000])

    cat_match = re.search(r"/jobs/([a-z-]+)/(\d+)", url)
    category = cat_match.group(1) if cat_match else ""
    job_id = cat_match.group(2) if cat_match else ""

    return {
        "platform": "smartshanghai",
        "url": url,
        "job_name": title,
        "company_name": company,
        "city": "上海",
        "job_description": jd_body,
        "job_type": job_type,
        "seniority": seniority,
        "category": category,
        "source_job_id": job_id,
        "collect_time": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def is_intern_row(row: Dict[str, str]) -> bool:
    if (row.get("job_type") or "").strip().lower() == "internship":
        return True
    haystack = (row.get("job_name", "") or "") + " " + (row.get("job_description", "") or "")
    return bool(INTERN_PATTERN.search(haystack))


def log(fh, msg: str) -> None:
    line = f"[{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    fh.write(line + "\n")
    fh.flush()


def main() -> int:
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    jsonl_path = OUT_DIR / "smartshanghai_latest.jsonl"
    csv_path = OUT_DIR / "smartshanghai_latest.csv"
    log_path = OUT_DIR / "smartshanghai_latest.log"
    summary_path = OUT_DIR / "smartshanghai_latest_summary.txt"

    log_fh = open(log_path, "w", encoding="utf-8")
    log(log_fh, f"start; jsonl -> {jsonl_path}")

    sess = requests.Session()
    sess.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8",
    })

    links = collect_listing_links(sess, log_fh)
    log(log_fh, f"detail link count: {len(links)}")

    rows: List[Dict[str, str]] = []
    intern_rows: List[Dict[str, str]] = []
    type_dist: Dict[str, int] = {}
    with open(jsonl_path, "w", encoding="utf-8") as fh:
        for i, url in enumerate(links):
            row = fetch_detail(sess, url)
            if not row or row.get("_err"):
                log(log_fh, f"detail err {url}: {row.get('_err') if row else 'no row'}")
                time.sleep(0.5)
                continue
            t = row.get("job_type", "") or "?"
            type_dist[t] = type_dist.get(t, 0) + 1
            rows.append(row)
            fh.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
            fh.flush()
            if is_intern_row(row):
                intern_rows.append(row)
                marker = "INTERN"
            else:
                marker = "      "
            log(log_fh, f"[{i+1}/{len(links)}] {marker} {row.get('job_type'):>11s}  {row.get('job_name','')[:65]}")
            time.sleep(0.4)

    # CSV
    try:
        import pandas as pd
        pd.DataFrame(rows).to_csv(csv_path, index=False, encoding="utf-8-sig")
    except Exception as e:
        log(log_fh, f"csv export failed: {e}")

    summary = [
        f"SmartShanghai crawl @ {ts}",
        f"total listings crawled: {len(rows)}",
        f"internships (filtered): {len(intern_rows)}",
        "",
        "type distribution:",
    ]
    for t, n in sorted(type_dist.items(), key=lambda x: -x[1]):
        summary.append(f"  {t:>15s}: {n}")
    summary.append("")
    summary.append("internship listings:")
    for r in intern_rows:
        summary.append(f"  - {r['job_name']!r} ({r['job_type']}) -> {r['url']}")
    text = "\n".join(summary)
    summary_path.write_text(text, encoding="utf-8")

    log(log_fh, "---- summary ----")
    for ln in summary:
        log(log_fh, ln)
    log(log_fh, f"artifacts: jsonl={jsonl_path}")
    log(log_fh, f"artifacts: csv={csv_path}")
    log(log_fh, f"artifacts: summary={summary_path}")
    log_fh.close()

    # Keep only latest artifacts for this source
    try:
        from scripts.output_latest import prune_directory
        prune_directory(
            OUT_DIR,
            keep_paths=[jsonl_path, csv_path, log_path, summary_path],
            allow_globs=[
                "smartshanghai_*.jsonl",
                "smartshanghai_*.csv",
                "smartshanghai_*.log",
                "smartshanghai_*_summary.txt",
            ],
        )
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
