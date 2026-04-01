# Internship Finder -- Multi-Source Campus Recruitment Crawler

A Python-based web crawler and data pipeline that aggregates campus recruitment internship postings from 9 major Chinese technology companies. The system crawls official career portals, normalizes heterogeneous job data into a unified schema, applies rule-based filtering for target graduation cohorts, and produces ranked candidate-job match reports.

## Overview

Chinese tech companies each maintain distinct career portal architectures with varying APIs, page structures, and data formats. This project abstracts those differences behind a unified adapter pattern, enabling a single crawl command to collect, clean, deduplicate, and score thousands of internship listings across all target companies.

## Supported Companies

ByteDance, Tencent, Kuaishou, Xiaohongshu, Meituan, Alibaba, JD.com, Bilibili, Baidu

## Features

- **Multi-source crawling** -- Fetches job listings from 9 company career portals using both REST API calls (requests) and browser-rendered pages (Playwright).
- **Adapter pattern** -- Each company has a dedicated adapter class (extending `BaseCompanyAdapter`) that implements `fetch_list`, `parse`, and `get_27_signal`, isolating company-specific logic from the core pipeline.
- **Configurable company selection** -- Enable or disable individual company crawlers and set per-company strict mode via `config.py`.
- **Snapshot-based change detection** -- Maintains JSON snapshots (`snapshot_latest.json`, `snapshot_prev.json`) to detect new, updated, and removed listings between crawl runs.
- **Content-hash deduplication** -- Generates MD5 hashes from job title, city, JD text, and recruitment type to eliminate duplicate postings across sources.
- **Cohort classification engine** -- A rule-based classifier (`cohort27_rules.py`) assigns high/medium/low confidence scores to determine whether a listing targets the 2027 graduation cohort, using 12+ pattern rules covering explicit year mentions, special recruitment programs (X-Star, RedStar, etc.), and timing heuristics.
- **Location normalization** -- Maps varied city representations (district names, slash-separated multi-city strings, aliases) to canonical city names via a JSON alias mapping and fallback regex.
- **Data enrichment pipeline** (`merge_file.py`):
  - JD parsing: splits raw job descriptions into responsibility and requirement sections.
  - Structured field extraction: degree requirements, graduation batch, internship duration, days per week.
  - Salary normalization: converts K-range, K-plus, and daily-rate formats to a unified monthly range.
  - Experience extraction: parses year-range, year-plus, and zero-experience patterns.
  - Skill keyword matching against a configurable list (SQL, Python, Spark, Tableau, etc.).
  - Composite relevance scoring (0--100) combining company tier, target city, cohort match, role-keyword density, and JD quality.
- **Vectorized pandas operations** -- Performance-critical normalization and scoring functions have vectorized implementations for large datasets.
- **Link validation** -- Async batch link checking to flag dead application URLs.
- **Multi-format output** -- Generates CSV, Excel, and JSON reports, including filtered views (Shanghai-only, verified-only, new-this-update).

## Tech Stack

- **Language**: Python 3.10+
- **Web scraping**: Requests, Playwright (Chromium)
- **Data processing**: pandas, regex
- **Async**: asyncio (link validation)
- **Configuration**: Python dict-based config with environment variable overrides

## Project Structure

```
internship_finding/
  official_multi_crawler.py   # Core multi-source crawler orchestrator
  merge_file.py               # Data cleaning, enrichment, scoring pipeline
  config.py                   # Company enable/disable and crawl settings
  parsers/
    base_adapter.py           # Abstract adapter interface
    company_adapters.py       # Per-company adapter implementations
    company_registry.py       # Adapter registry and factory
  rules/
    cohort27_rules.py         # Graduation cohort classification rules
    location_normalizer.py    # City name normalization with alias mapping
  release_data/               # Output CSVs and Excel files
  archive/                    # Historical crawl snapshots
```

## How to Run

```bash
# Install dependencies
pip install pandas requests playwright apscheduler

# Install Playwright browsers (first time only)
playwright install chromium

# Run the multi-source crawler
python official_multi_crawler.py

# Run the merge and scoring pipeline
python merge_file.py
```

Environment variables (optional):

| Variable | Default | Description |
|---|---|---|
| `HEADLESS` | `1` | Run browser in headless mode |
| `MAX_SCROLL` | `10` | Maximum scroll iterations for infinite-scroll pages |
| `CITY_KEYWORD` | Shanghai | Target city filter |
| `GRAD_KEYWORDS` | `27届,2027届,2027` | Comma-separated graduation cohort keywords |
