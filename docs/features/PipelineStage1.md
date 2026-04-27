# Pipeline Stage 1-3: Raw → Unified Job Database

**Status:** Implemented and validated against real data (456 jobs across 5 platforms).
**Owner:** `pipeline/`
**Entry point:** `scripts/ingest_all.py`

---

## What this stage delivers

A single pandas-readable Parquet file `data/unified/jobs.parquet` that
contains every JD across every crawler source under one schema. This is
the **single source of truth** for everything downstream (semantic
indexing, resume matching, recommendation reports).

> Before this stage, JDs lived in 4 different formats with 4 different
> field naming conventions. After this stage: one table, one schema, one
> read.

```python
import pandas as pd
df = pd.read_parquet("data/unified/jobs.parquet")
# 456 rows, 23 cols, all platforms unified.
```

---

## Architecture

```
[data/raw/yingjiesheng/*.jsonl]
[data/raw/shixiseng/*.jsonl]
[data/raw/smartshanghai/*.jsonl]                   (Stage 1: normalize)
[data/raw/liepin/*.json]            ───────────►   pipeline/normalize.py
[outputs/raw/foreign_*_official_raw.csv]                 │
                                                         ▼
                                                   pipeline/clean_jd.py    (Stage 2: clean)
                                                         │
                                                         ▼
                                                   pipeline/dedupe.py      (Stage 3: dedupe)
                                                         │
                                                         ▼
                                            data/unified/jobs.parquet  ← SSOT
                                            data/unified/jobs.jsonl    (optional, for grep)
```

Each module is pure and tested: 36 unit tests covering HTML stripping,
boilerplate removal, salary parsing, all 5 adapters, source routing,
and the three-stage dedupe key strategy.

### Design principles followed

- **Single source of truth.** Every downstream consumer reads
  `jobs.parquet`. Adapters are the only code that talks to raw files.
- **Separate lifecycle.** `data/raw/` is append-only (crawler owns it).
  `data/unified/` is rebuildable (pipeline owns it). Never mix.
- **Reproducibility.** Each row carries `raw_path`, `ingest_time`, and
  `schema_version` so any recommendation can be traced back.
- **Never overwrite raw.** Re-running `ingest_all.py` rewrites
  `jobs.parquet` only.

---

## Job schema (v1)

Defined in `pipeline/schema.py`. All fields:

| field | type | semantics |
|---|---|---|
| `job_id` | str | Primary key. `f"{platform}:{source_job_id}"` |
| `platform` | str | Lowercase ascii (`yingjiesheng`, `shixiseng`, `smartshanghai`, `liepin`, `official_amazon_aws`, ...) |
| `source_job_id` | str | Per-platform id (or url-derived) |
| `url` | str | Canonical job page |
| `title` | str | Job title, cleaned |
| `company` | str | Hiring company |
| `city` | str | Normalized city, e.g. `上海` |
| `district` | str | Optional |
| `job_type` | enum | `internship` / `campus` / `fulltime` / `freelance` / `unknown` |
| `seniority` | enum | `intern` / `junior` / `mid` / `senior` / `lead` / `unknown` |
| `salary_min/max` | float | Numeric, with K-factor applied |
| `salary_unit` | enum | `month` / `day` / `hour` / `year` / `unknown` |
| `salary_raw` | str | Original string, kept for audit |
| `education_req` | str | e.g. `本科` |
| `experience_req` | str | Free-form |
| `industry` | str | |
| `language_req` | list[str] | |
| **`jd_text`** | str | **Cleaned plain text — this is what the embedding sees in Stage 4.** |
| `skills` | list[str] | Reserved (empty in v1; Stage 4 will populate) |
| `raw_path` | str | Source file (relative to project root) |
| `ingest_time` | str | UTC ISO8601 |
| `schema_version` | str | `v1` |

---

## How to run

```powershell
# 1. install deps once
py -3.11 -m pip install -r requirements.txt

# 2. run pipeline
py -3.11 scripts/ingest_all.py

# 3. (optional) also dump human-readable jsonl mirror
py -3.11 scripts/ingest_all.py --jsonl-mirror

# 4. run tests
py -3.11 -m pytest tests/test_pipeline.py -v
```

A full ingest is < 10 seconds for the current 818 raw rows.

---

## Last validation (2026-04-27)

```
Parsed  ≈900 job rows from 12 files (yingjiesheng + shixiseng +
        smartshanghai + liepin + foreign_official).
Dedupe: input=≈900  output=456  dropped_pk≈375  dropped_url=0
        dropped_content_collision≈68 (Amazon AWS clones, see below)
Wrote   data/unified/jobs.parquet  (456 rows, 23 cols)

platform distribution (approx)
  yingjiesheng           ~375
  smartshanghai            28
  liepin                   25   ← new since this iteration
  shixiseng                20
  official_amazon_aws       8   ← was 20; collapsed to 8 by content-hash dedupe

avg jd_text length: ~1100 chars
```

Two changes since the previous validation:

1. **Liepin integrated.** `data/raw/liepin/*.json` files (top-level list
   or `{"jobs": [...]}` envelope) are now ingested by `adapter_liepin`.
   Liepin's API only returns the listing-page JD (description +
   requirements concatenated), so its rows tend to be 80–150 chars —
   shorter than yingjiesheng. The Stage-2 `min_jd_chars` filter was
   lowered from 200 → 100 to accommodate this; see
   `docs/features/PipelineStage2.md`.
2. **Content-hash dedupe.** A third dedupe stage hashes
   `(company, jd_text[:500])` to collapse Amazon-style "same JD
   posted under N different titles" duplicates. See `pipeline/dedupe.py`.

The 375 PK collisions are expected: the yingjiesheng spider produces
both a base `*_latest.jsonl` and an enriched `*_latest_enriched.jsonl`
with the same `source_job_id`s. Dedupe keeps the row with the longer
`jd_text` (i.e. the enriched one).

---

## Known issues / Tech debt (to revisit in Stage 4-5)

- **`yingjiesheng.title` fallback.** The spider captures anchor text
  `[上海]<company>` instead of the real job title. `adapter_yingjiesheng`
  detects the case where `title == company` and falls back to extracting
  the title from the first line of `jd_text` (`extract_title_from_jd`,
  see `pipeline/normalize.py`). Tracked here because it's a workaround,
  not a real fix on the crawler side.
- **Liepin JD is short.** Listing-page JDs from liepin are 80–150 chars
  because the spider scrapes `jobDesc` + `requirement` from the search
  API, not the detail page. If detail-page enrichment is ever added,
  the `min_jd_chars` filter in `config/preferences.yaml` can be raised
  back toward 200 for tighter quality control.
- **`salary_raw` empty for 95% of rows.** Mostly yingjiesheng + shanghai
  smart, where the spider didn't capture the salary field. Salary-based
  filters in Stage 5 must therefore be optional, not required.
- **`skills` is empty.** Reserved for Stage 4 (NER / keyword extraction
  on `jd_text`). Don't depend on it yet.
- **`data/raw/merged/*.json` skipped.** Those are 41 legacy snapshots
  superseded by `outputs/raw/foreign_*_official_raw.csv`. If a snapshot
  ever needs to be re-ingested, add a path rule in `normalize.detect_source`.
- **`release_data/foreign_master_database_v2.csv` skipped.** Already
  curated by a separate workflow; reading both would double-count.

---

## Interface for Stage 4-5 (next iteration)

The matching engine will read from the unified table and write to
`outputs/recommendations/*`. It MUST NOT touch `data/raw/`.

```python
# Stage 4: build_index reads jobs.parquet, writes vectors.
df = pd.read_parquet("data/unified/jobs.parquet")
embeddings = model.encode(df["jd_text"].tolist())   # bge-small-zh
np.savez("index/jobs_v1.npz", ids=df["job_id"].values, vecs=embeddings)

# Stage 5: recommend reads vectors + resume + preferences.yaml,
# applies hard filters (city, job_type), scores, writes top-N to
# outputs/recommendations/{timestamp}.{csv,md,html}.
```

Schema version is bumped (`v1 → v2`) only if a field's semantics change.
Adding new optional fields does NOT bump the version.
