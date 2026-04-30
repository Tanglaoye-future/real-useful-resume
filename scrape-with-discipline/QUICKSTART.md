# Quickstart — Crawl 实习僧 in 30 minutes

This is the runbook for someone seeing this skill for the first time. Follow steps in order. Each step has an **expected output** — if yours doesn't match, the step *itself* tells you what's wrong. Don't skip ahead.

If you just want to understand the *why* before running anything, read `SKILL.md` first. If you just want data, follow this file end-to-end.

## Prerequisites

- Python 3.9+
- A network that can reach `https://www.shixiseng.com` (test in a browser first)
- ~30 minutes total

## Step 1 — Install dependencies (1 min)

```bash
cd ~/.claude/skills/scrape-with-discipline/reference
pip install -r requirements.txt
```

**Expected**: `Successfully installed requests-... beautifulsoup4-... pandas-... fonttools-... Pillow-...`

If pip is slow, try `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`.

## Step 2 — Verify your setup (1 min)

```bash
python verify_setup.py
```

**Expected** (last lines):
```
[3] Checking list-page selector still matches...
   OK    '.intern-wrap'                            -> 12 matches
[4] Looking for font anti-bot signal...
   FOUND 1 .woff reference(s). ...
All core checks passed.
```

What this checks: deps installed, network reaches the site, the CSS selector in the adapter still matches at least 5 job cards (websites change — this catches it before you waste time), and whether font anti-bot is active.

**If you see `STALE` instead of `OK`**: the site changed its HTML class names. Open the page in browser, inspect a job card, find the new wrapping class, edit `shixiseng_adapter.py:list_selector`, re-run verify.

**If you see `non-200 status`**: you may be rate-limited or blocked. Wait 10 min, try again from a different network if possible.

## Step 3 — Extract the font map (5 min)

```bash
python extract_font_map.py
```

**Expected** (last lines):
```
[4/4] Rendering each glyph to PNG ...
   OK    font_extract/font_map.json written with 27 empty slots

MANUAL STEP — about 5 minutes:
  1. Open folder:  .../font_extract/glyphs
  2. Open file:    .../font_extract/font_map.json
  ...
```

Now do the manual step:
- Open `font_extract/glyphs/` — you'll see ~30 small PNG files like `U+E001.png`, each showing one digit or character
- Open `font_extract/font_map.json` in any editor — keys are escaped codepoints, values are empty
- For each entry, look at the matching PNG and type the character you see:

```json
{
  "": "0",
  "": "1",
  "": "2",
  "": "招",
  ...
}
```

Save the file. Most entries are digits 0–9 plus a handful of common chars (招、聘、急、面). Takes 5 min if you focus.

**Why manual**: the font rotates daily and glyph names are obfuscated, so OCR is overkill. Eye + 5 min is faster and more reliable.

## Step 4 — Dry run on 3 pages (2 min)

```bash
python shixiseng_adapter.py --pages 3 --dry-run
```

**Expected**:
```
Loaded font map: 27 entries from font_extract/font_map.json
DRY RUN: fetching page 1, parsing first 3 cards, no writes

Got 12 cards.

--- card 1 ---
  company_name: '某某科技有限公司'
  job_title: '数据分析实习生'
  salary_range: '200-300/天'
  location: '上海'
  url: 'https://www.shixiseng.com/intern/inn_xxxxxx'
...
```

**Sanity check** (this is the moment of truth):
- `salary_range` shows real numbers like `200-300/天`, NOT `□-□/天` or random unicode
- `company_name` and `job_title` look like normal Chinese, no `&#x` or boxes
- `url` starts with `https://www.shixiseng.com/intern/inn_`

If salaries are still garbled: your font_map is incomplete. Re-open the PNGs you weren't sure about, fill in more entries, re-run.

If everything looks clean: you're done with setup. Move to Step 5.

## Step 5 — Real run (~20 min for 200 pages)

```bash
python shixiseng_adapter.py --pages 200
```

**Expected**:
```
[shixiseng] Fetching list page 1
Page 1: 12 parsed, 8 would pass filter
[shixiseng] Fetching list page 2
...
```

Progress is saved after every page (`logs/shixiseng_ckpt.txt`). If your laptop sleeps or network drops, just re-run the same command — it picks up where it stopped.

Output is at `raw/shixiseng_dryrun.csv` (raw, no filter) and you can apply filters separately. To run the filter pass:

```python
from template_crawler import filter_raw_to_clean
from shixiseng_adapter import ShixisengAdapter
filter_raw_to_clean("raw/shixiseng_dryrun.csv", "clean/shixiseng_clean.csv", ShixisengAdapter())
```

## QC — Before you trust the data

```python
import pandas as pd
df = pd.read_csv("raw/shixiseng_dryrun.csv")
print(df.shape)                                    # rows, cols
print(df.isna().mean().round(2))                  # null rate per column
print(df.sample(10)[["company_name", "job_title", "salary_range"]])
print(df.astype(str).apply(lambda c: c.str.contains(r"[-]|□|&#x", regex=True).sum()))
```

The last line counts decoding artifacts per column. **All zeros** = data is clean. **Anything > 0** = your font_map is missing entries; go back to Step 3 and add them.

## Adapting to a different site (BOSS, 拉勾, 58同城...)

Once 实习僧 works, copy `shixiseng_adapter.py` to e.g. `boss_adapter.py` and change five things:

1. Class name + `name` field
2. `base_url` and `list_query`
3. `list_selector` and field selectors in `parse_list_card()`
4. `parse_detail()` selectors
5. `font_map` (extract with a tweaked `extract_font_map.py` — change `LIST_URL`)

The 5 disciplines (schema, list+detail, decoding, retry+checkpoint, raw-then-filter) are inside `template_crawler.py` and don't move. See `SKILL.md` § "How to Adapt to a New Site" for the full checklist.

JS-rendered sites (BOSS, 拉勾) need Playwright instead of `requests` — see `reference/encoding_recipes.md` §4.
