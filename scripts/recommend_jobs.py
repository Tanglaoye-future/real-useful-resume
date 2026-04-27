"""Stage 5 main entry: resume + index + preferences -> Top-N recommendations.

Reads:
  data/unified/jobs.parquet         (Stage 1-3, SSOT)
  index/jobs_embeddings.npz         (Stage 4, vectors)
  index/jobs_meta.parquet           (Stage 4, slim display fields)
  config/preferences.yaml           (Stage 5 input, user-curated)
  data/resumes/<your_resume>        (Stage 5 input, user-curated)

Writes:
  outputs/recommendations/<UTC_TS>/{recommendations.csv,.md,.html}
  outputs/recommendations/<UTC_TS>/run_meta.json
  outputs/recommendations/latest -> <UTC_TS>           (Windows-safe junction)

Reproducibility:
  Each run is its own folder. Re-running never overwrites past results.
  Per CLAUDE.md: append-only result storage.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import yaml

from matcher.render import render_all
from matcher.resume_loader import load_resume
from matcher.score import apply_filters, final_score, normalized_weights
from pipeline.build_index import build_text_for_embedding, fingerprint as fp_fn  # noqa: F401


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(
            f"Preferences file not found: {path}\n"
            f"Copy config/preferences.example.yaml to config/preferences.yaml "
            f"and edit it."
        )
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_index(index_dir: Path) -> tuple[np.ndarray, np.ndarray, str, str]:
    """Returns (ids, vecs, model_name, fingerprint)."""
    npz_path = index_dir / "jobs_embeddings.npz"
    if not npz_path.exists():
        raise SystemExit(
            f"Embedding index not found at {npz_path}.\n"
            f"Run: py -3.11 pipeline/build_index.py"
        )
    npz = np.load(npz_path, allow_pickle=True)
    ids = np.array(npz["ids"], dtype=str)
    vecs = np.array(npz["vecs"], dtype="float32")
    model_name = str(npz["model_name"])
    fp = str(npz["fingerprint"])
    return ids, vecs, model_name, fp


def _verify_index_matches_meta(ids: np.ndarray, meta: pd.DataFrame, fp: str) -> None:
    """Ensure index aligns with current jobs_meta.parquet by job_id set + fingerprint."""
    set_idx = set(ids.tolist())
    set_meta = set(meta["job_id"].astype(str).tolist())
    missing_in_meta = set_idx - set_meta
    missing_in_index = set_meta - set_idx
    if missing_in_meta or missing_in_index:
        raise SystemExit(
            "Index and jobs_meta.parquet are out of sync.\n"
            f"  ids in index but not in meta: {len(missing_in_meta)}\n"
            f"  ids in meta but not in index: {len(missing_in_index)}\n"
            f"Rerun: py -3.11 pipeline/build_index.py"
        )


def recommend(
    prefs: dict,
    resume_text: str,
    resume_path: str,
    project_root: Path,
    top_n: int | None = None,
) -> Path:
    index_dir = project_root / "index"
    ids, jd_vecs, model_name, fp = _load_index(index_dir)

    meta_path = index_dir / "jobs_meta.parquet"
    if not meta_path.exists():
        raise SystemExit(f"jobs_meta.parquet not found at {meta_path}. "
                         f"Run pipeline/build_index.py.")
    meta_full = pd.read_parquet(meta_path)
    _verify_index_matches_meta(ids, meta_full, fp)

    meta_full = meta_full.set_index("job_id").loc[ids].reset_index()

    print(f"Index: {len(ids)} jobs, model={model_name}")

    n_before = len(meta_full)
    kept_meta, fstats = apply_filters(meta_full, prefs)
    n_after = len(kept_meta)
    print(f"Hard filter: {n_before} -> {n_after}  ({fstats})")
    if n_after == 0:
        raise SystemExit(
            "No jobs survived the hard filter. Loosen "
            "filters.target_cities / target_job_types / exclude_keywords / "
            "min_jd_chars in config/preferences.yaml."
        )

    kept_indices = meta_full.index.get_indexer(kept_meta.index)
    kept_vecs = jd_vecs[kept_indices]

    print(f"Encoding resume ({len(resume_text)} chars)...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name)
    resume_vec = model.encode(
        [resume_text],
        normalize_embeddings=True,
        show_progress_bar=False,
    )[0].astype("float32")

    t0 = time.time()
    scores, comp = final_score(kept_meta, kept_vecs, resume_vec, prefs)
    print(f"Scored {len(scores)} jobs in {(time.time() - t0) * 1000:.0f} ms")

    out = kept_meta.copy()
    out["semantic"] = comp["semantic"]
    out["keyword"] = comp["keyword"]
    out["title_score"] = comp["title"]
    out["location_score"] = comp["location"]
    out["job_type_score"] = comp["job_type"]
    out["base"] = comp["base"]
    out["is_big_tech"] = comp["is_big_tech"]
    out["final"] = scores
    out["jd_excerpt"] = out["jd_text"].astype(str).str.slice(0, 600)

    out = out.sort_values("final", ascending=False).reset_index(drop=True)
    if top_n is None:
        top_n = int((prefs.get("output", {}) or {}).get("top_n", 20))
    top = out.head(top_n).copy()
    top.insert(0, "rank", np.arange(1, len(top) + 1))

    ts = _utc_stamp()
    run_dir = project_root / "outputs" / "recommendations" / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    formats = (prefs.get("output", {}) or {}).get("formats") or ["csv", "markdown", "html"]
    weights = normalized_weights(prefs)
    meta_info = {
        "timestamp": ts,
        "resume_path": resume_path,
        "model": model_name,
        "total": int(n_before),
        "after_filter": int(n_after),
        "filter_stats": fstats,
        "weights": weights,
        "fingerprint": fp,
        "big_tech_penalty": float(comp.get("big_tech_penalty", 1.0)),
        "big_tech_count_in_top": int(top["is_big_tech"].sum()) if "is_big_tech" in top else 0,
    }

    paths = render_all(top, run_dir, meta_info, formats)

    (run_dir / "run_meta.json").write_text(
        json.dumps(meta_info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\nWrote {len(paths)} files to {run_dir.relative_to(project_root)}/")
    for p in paths:
        print(f"  - {p.relative_to(project_root)}")
    print(f"  - {(run_dir / 'run_meta.json').relative_to(project_root)}")
    return run_dir


def cli() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefs", default="config/preferences.yaml",
                    help="Preferences YAML. Falls back to .example if missing.")
    ap.add_argument("--resume", default=None,
                    help="Override resume path (else read from prefs.resume.path).")
    ap.add_argument("--top", type=int, default=None,
                    help="Override prefs.output.top_n.")
    args = ap.parse_args()

    prefs_path = (PROJECT_ROOT / args.prefs).resolve()
    if not prefs_path.exists():
        example = PROJECT_ROOT / "config" / "preferences.example.yaml"
        if example.exists():
            print(f"[!] {prefs_path} not found, falling back to {example.name}")
            prefs_path = example
        else:
            raise SystemExit(f"Preferences file not found: {prefs_path}")
    prefs = _read_yaml(prefs_path)
    print(f"Loaded prefs from {prefs_path.relative_to(PROJECT_ROOT)}")

    resume_cfg = (prefs.get("resume", {}) or {})
    resume_path = args.resume or resume_cfg.get("path")
    if not resume_path:
        raise SystemExit("Resume path not set. Pass --resume or set resume.path in prefs.")
    resume_full = (PROJECT_ROOT / resume_path).resolve()
    min_chars = int(resume_cfg.get("parse_min_chars", 100))

    print(f"Loading resume: {resume_full.relative_to(PROJECT_ROOT)}")
    resume_text = load_resume(resume_full, min_chars=min_chars)
    print(f"Resume: {len(resume_text)} chars")

    recommend(prefs, resume_text, str(resume_full.relative_to(PROJECT_ROOT)),
              PROJECT_ROOT, top_n=args.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
