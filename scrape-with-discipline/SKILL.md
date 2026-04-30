---
name: scrape-with-discipline
description: Build resilient web crawlers that produce usable, schema-complete data on the first run. Use when the user is writing a scraper from scratch, debugging a crawler whose output has missing fields / encoding garbage / partial data after long runs, or porting a working crawler to a new site (e.g. 实习僧, 58同城, BOSS直聘, 大众点评, 智联, 拉勾). Enforces 5 disciplines (schema-first, list+detail layering, decoding stack, retry+checkpoint, raw-then-filter) and provides a SiteAdapter template that isolates per-site knobs from universal infrastructure.
---

# Scrape With Discipline

> **TL;DR — if you only read 50 chars:** Crawled data is unusable because the crawler has no contract with itself. Sign one. (Schema, source-tag, decode, checkpoint, raw-first.)

**For someone running this for the first time**: skip this file, open `QUICKSTART.md`, follow the 5 steps. Come back here once the data is flowing — this file explains *why* the disciplines exist so you can adapt to other sites.

The reason "爬了半天数据不可用" is almost never that the website is too hard. It is that the crawler has no contract with itself — fields drop silently, decoding errors are caught and ignored, a network blip wipes 200 pages of progress, filters run before raw save. This skill encodes 5 disciplines that fix this, plus a `SiteAdapter` pattern so adapting to a new site takes ~30 minutes instead of starting over.

## When to Use

Trigger when the user is:
- Writing a new crawler from scratch (especially for jobs/listings sites)
- Debugging an existing crawler whose output has: missing fields, garbled Chinese, encoding errors, "ran for hours but data unusable"
- Porting a working crawler to a new site (the 5 disciplines stay; only the adapter changes)
- Reviewing a classmate's crawler code

Do NOT trigger for: API-only ingestion (no scraping), one-off scripts that don't need to run again, or anything that already uses Scrapy/Playwright with a working pipeline.

## The 5 Disciplines

These are non-negotiable. Skipping any one of them is what causes the "跑了很久数据不可用" outcome.

### 1. Schema-First — Every row has the same shape

Before writing the parser, declare the expected columns. Every record produced must have all keys, even if some values are empty strings. This makes "field missing" visible (warn in logs, fill with `''`) instead of invisible (`KeyError` deep in pandas later, or random `NaN` columns).

```python
SCHEMA = ["company_name", "job_title", "salary_range", "location",
          "url", "responsibilities", "requirements", "benefits",
          "publish_time", "deadline", "source", "crawled_at"]

def normalize(raw: dict) -> dict:
    row = {k: "" for k in SCHEMA}
    row.update({k: v for k, v in raw.items() if k in SCHEMA})
    missing = [k for k in SCHEMA if not row[k]]
    if missing and "url" not in missing:  # url is the minimum viable record
        logger.warning(f"Missing fields {missing} for {row['url']}")
    return row
```

**Anti-pattern**: building rows ad-hoc in the parser, then discovering at analysis time that 30% of rows are missing `requirements` because one selector silently broke 8 hours ago.

### 2. List + Detail Layering — Tag the source of every field

List pages have basic info (company, title, salary, link). Detail pages have everything else (full requirements, address, deadline). Always crawl both, and **mark which page each field came from**:

```python
row["address_source"] = "详情页" if detail_addr else "列表页"
```

Why: when you later notice "this field is wrong/missing", you instantly know whether the list selector or detail selector is the problem. Without this tag, you have to re-crawl to debug.

**Fallback rule**: if detail-page fetch fails, keep the list-page fields rather than dropping the whole record. Tag the row so you can re-fetch detail pages later.

### 3. Decoding Stack — Three layers, in this order

Encoding garbage is the #1 reason output is unusable. Apply these in order, never skip layers:

1. **HTTP response encoding**: `r.encoding = 'utf-8'` (or detect — `requests` defaults to ISO-8859-1 for many CN sites and silently mangles everything)
2. **Font-glyph anti-bot decode**: many CN sites (实习僧, 58同城, 大众点评, 猫眼) replace digits and key chars with private-use Unicode glyphs rendered by a custom WOFF font. You need a `font_map: dict[str, str]` to swap them back. See `reference/encoding_recipes.md`.
3. **Field-level cleanup**: strip `\r\n`, normalize whitespace, decode HTML entities (`&amp;`, `&#x6587;`). Always per-field with `try/except` so one broken record doesn't kill the page.

If you see `□` boxes, garbled digits in salaries, or `&#x` in output — you skipped a layer.

### 4. Retry + Checkpoint — Survive network blips and Ctrl-C

```python
def request_with_retry(session, url, attempts=3):
    for i in range(attempts):
        try:
            r = session.get(url, headers=rotate_ua(), timeout=15)
            r.encoding = "utf-8"
            return r
        except Exception:
            time.sleep(0.5 * (2 ** i))  # exponential backoff
    return None  # caller logs and continues — never raises
```

Plus a checkpoint file written after each page. On restart, read it and resume from `last_page + 1`. **Never** restart from page 1 because you "want a clean run" — that's how you lose 6 hours of work to a single timeout.

### 5. Raw-Then-Filter — Save before judging

Append every parsed record to a raw CSV **immediately**, before any filtering ("is 上海?", "是本科?"). Then run filters in a separate pass to produce the cleaned dataset.

Why: filter logic always changes (you'll realize "本科及以上" should also count, or you want to add 杭州). If filtering happens during crawl, every change means re-crawling. If filtering is a separate pass on the raw file, it's a 5-second pandas operation.

Format: `mode='a'`, `header=not os.path.exists(path)`, `encoding='utf-8-sig'` (the BOM keeps Excel from mangling Chinese).

## How to Adapt to a New Site

This is the question the user actually cares about. The 5 disciplines are universal. Per-site knobs go in a `SiteAdapter` (see `reference/template_crawler.py`). To port to a new site:

1. **Inspect the list page** in browser DevTools. Note the CSS selector for each card and for each field within a card. → fill in `list_selector`, `field_selectors`.
2. **Open one detail page**. Note selectors for the detail-only fields. → fill in `detail_selectors`.
3. **Check for font anti-bot**. View source and search for `@font-face` with a `.woff` URL, or look at salaries/numbers in the rendered page — if they show as `□` in `view-source` but render correctly, the site uses font swap. Build the `font_map` once (see `reference/encoding_recipes.md` § "Font glyph swap"); it usually rotates daily, so plan to refresh.
4. **Check rate limits**. Start with 2-second sleep + jitter. If you get 403/429 within 50 pages, slow down to 5–8 seconds and rotate UA. If still blocked, you need Playwright (browser context) instead of `requests`.
5. **Define the filter**. Site-specific predicates (location, education) go in `adapter.filter_row()`. Schema stays the same across sites.

That's it. The template and shixiseng adapter together are ~280 lines; a new site adapter is typically 60–100 lines.

## Common Sites — known traits

| Site | Anti-bot | Approach |
|---|---|---|
| 实习僧 shixiseng | Font glyph swap (digits + 部分汉字) | `requests` + font_map; map rotates ~daily. Worked example: `reference/shixiseng_adapter.py` |
| 58同城 / 赶集 | Font glyph swap (heavy) | Same pattern; map is bigger |
| 大众点评 | Font glyph + CSS sprite | Font map for text, sprite-position decode for some numbers |
| BOSS直聘 | JS-rendered + behavior detection | Playwright required; fingerprint matters |
| 拉勾 | API with token + JS-rendered | Playwright or reverse-engineer the token endpoint |
| 智联招聘 | Mostly JSON API | `requests` + cookie; minimal anti-bot |

## Files

- `QUICKSTART.md` — runbook for first-time users. Start here if you just want data.
- `reference/requirements.txt` — pinned deps (`pip install -r requirements.txt`).
- `reference/verify_setup.py` — pre-flight check: deps, network reach, list-page selectors still valid, font anti-bot detection.
- `reference/extract_font_map.py` — pulls current shixiseng .woff, renders each glyph to PNG, emits a `font_map.json` skeleton for ~5 min of manual labelling.
- `reference/template_crawler.py` — generic scaffold with `SiteAdapter` base class and all 5 disciplines wired in. **Don't edit this file** when porting to a new site — only subclass `SiteAdapter`.
- `reference/shixiseng_adapter.py` — worked example. Has a `__main__` block: `python shixiseng_adapter.py --dry-run` parses 3 cards and prints them. Use as the structural template when porting.
- `reference/encoding_recipes.md` — concrete patterns for the 5 most common decoding pitfalls (HTTP encoding, font swap, HTML entities, JS-rendered, base64 fields).

## Self-Check Before Declaring "Done"

Before saying a crawler is working, verify:

- [ ] Sample 10 random rows from output. **Every** row has all schema fields populated, or the empty ones are explained (e.g., "deadline" genuinely absent on this site).
- [ ] Salary/numeric fields contain real numbers, no `□` or `&#x`.
- [ ] Killing the process mid-run and restarting resumes from the right page (test this once, on purpose).
- [ ] Re-running on the same pages produces identical rows (idempotent — dedup by URL works).
- [ ] Total row count matches roughly what you see when scrolling the site by hand (within ±20%).

If any of these fail, the data is not usable yet — fix before moving to analysis.
