"""Stage 1-3 main entry: raw crawler outputs -> data/unified/jobs.parquet.

What it does:
  1. Walk known raw locations (data/raw/yingjiesheng, data/raw/shixiseng,
     data/raw/smartshanghai, outputs/raw/foreign_*_official_raw.csv).
  2. Pick adapter via pipeline.normalize.detect_source.
  3. For each row -> normalize -> validate (pydantic) -> collect.
  4. Dedupe (platform, source_job_id) + URL fallback.
  5. Write data/unified/jobs.parquet (overwrite the unified file ONLY;
     raw inputs are never touched).
  6. Print a one-screen quality report.

Reproducibility: same raw inputs + same code = same parquet. The parquet
carries `ingest_time` and `raw_path` per row, so any recommendation can
trace back to the source file.

Usage:
  py -3.11 scripts/ingest_all.py
  py -3.11 scripts/ingest_all.py --jsonl-mirror   # also dump jobs.jsonl for human inspection
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import traceback
from collections import Counter
from pathlib import Path
from typing import Iterable, Iterator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from pipeline.dedupe import dedupe
from pipeline.normalize import ADAPTERS, detect_source
from pipeline.schema import Job


# ---------------------------------------------------------------------------
# discovery
# ---------------------------------------------------------------------------

def discover_raw_files(root: Path) -> list[Path]:
    """Return concrete files our adapters know how to read.

    Convention-based — see normalize.detect_source. We deliberately skip:
      - data/raw/merged/*.json     (legacy snapshots, superseded)
      - release_data/*.csv         (already-curated v2 workflow)
      - *.log, *.csv summary files
    """
    candidates: list[Path] = []
    raw_dir = root / "data" / "raw"
    for sub in ("yingjiesheng", "shixiseng", "smartshanghai"):
        d = raw_dir / sub
        if not d.exists():
            continue
        candidates.extend(p for p in d.glob("*.jsonl"))

    liepin_dir = raw_dir / "liepin"
    if liepin_dir.exists():
        candidates.extend(p for p in liepin_dir.glob("*.json")
                          if not p.name.startswith("."))

    foreign_dir = root / "outputs" / "raw"
    if foreign_dir.exists():
        candidates.extend(p for p in foreign_dir.glob("foreign_*_official_raw.csv"))

    return sorted(candidates)


# ---------------------------------------------------------------------------
# row iteration
# ---------------------------------------------------------------------------

def iter_jsonl(path: Path) -> Iterator[dict]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def iter_csv(path: Path) -> Iterator[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def iter_json(path: Path) -> Iterator[dict]:
    """Read a `.json` file containing either a top-level list of objects,
    or a dict with a 'jobs' / 'data' list inside.
    """
    with path.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return
    if isinstance(data, list):
        for row in data:
            if isinstance(row, dict):
                yield row
    elif isinstance(data, dict):
        for key in ("jobs", "data", "results"):
            if isinstance(data.get(key), list):
                for row in data[key]:
                    if isinstance(row, dict):
                        yield row
                return
        yield data


def iter_records(path: Path) -> Iterable[dict]:
    if path.suffix == ".jsonl":
        return iter_jsonl(path)
    if path.suffix == ".json":
        return iter_json(path)
    if path.suffix == ".csv":
        return iter_csv(path)
    return iter([])


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def ingest(root: Path, jsonl_mirror: bool = False) -> Path:
    files = discover_raw_files(root)
    if not files:
        print("No raw files discovered. Nothing to do.")
        return Path()

    jobs: list[Job] = []
    per_source: Counter = Counter()
    parse_errors: list[tuple[str, str]] = []

    for fp in files:
        rel = str(fp.relative_to(root)).replace("\\", "/")
        src = detect_source(rel)
        if src is None:
            print(f"  skip (no adapter): {rel}")
            continue
        adapter = ADAPTERS[src]
        n_in, n_out = 0, 0
        for rec in iter_records(fp):
            n_in += 1
            try:
                job = adapter(rec, rel)
            except Exception as e:
                parse_errors.append((rel, f"{type(e).__name__}: {e}"))
                continue
            if job is None:
                continue
            jobs.append(job)
            n_out += 1
        per_source[src] += n_out
        print(f"  {src:18s} {n_in:5d} -> {n_out:5d}   {rel}")

    print()
    print(f"Parsed {len(jobs)} job rows from {len(files)} files.")

    deduped, stats = dedupe(jobs)
    print(f"Dedupe: {stats.report()}")

    rows = [j.parquet_dict() for j in deduped]
    df = pd.DataFrame(rows)

    out_dir = root / "data" / "unified"
    out_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = out_dir / "jobs.parquet"
    df.to_parquet(parquet_path, index=False)
    print(f"\nWrote {parquet_path}  ({len(df)} rows, {len(df.columns)} cols)")

    if jsonl_mirror:
        jsonl_path = out_dir / "jobs.jsonl"
        with jsonl_path.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"Wrote {jsonl_path}")

    print("\n--- platform distribution ---")
    print(df["platform"].value_counts().to_string())

    print("\n--- empty-field rate (top fields) ---")
    for col in ["title", "company", "city", "jd_text", "salary_raw", "education_req"]:
        if col not in df.columns:
            continue
        empty = (df[col].astype(str).str.strip() == "").sum()
        rate = empty / len(df) if len(df) else 0
        print(f"  {col:14s}  empty={empty:5d}  rate={rate:.1%}")

    avg_jd = df["jd_text"].astype(str).str.len().mean() if len(df) else 0
    print(f"\nAvg jd_text length: {avg_jd:.0f} chars")

    if parse_errors:
        print(f"\n[!] {len(parse_errors)} parse errors. First 5:")
        for f, e in parse_errors[:5]:
            print(f"  {f}: {e}")

    return parquet_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl-mirror", action="store_true",
                    help="Also write data/unified/jobs.jsonl for human inspection.")
    args = ap.parse_args()
    try:
        ingest(PROJECT_ROOT, jsonl_mirror=args.jsonl_mirror)
    except Exception:
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
