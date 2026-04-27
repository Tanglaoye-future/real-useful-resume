"""Stage 4 (a): build job embeddings index.

Inputs:
  data/unified/jobs.parquet   (Stage 1-3 output, SSOT)

Outputs:
  index/jobs_embeddings.npz   {ids, vecs, model_name, fingerprint}
  index/jobs_meta.parquet     (slim copy: job_id, title, company, city, url, jd_text head)

Why a separate npz + meta:
  - npz holds float32 vectors only (fast load, no string overhead).
  - meta holds display fields used by the renderer (avoids re-reading the
    big jobs.parquet from a webserver / repeated CLI calls).

Reproducibility (per CLAUDE.md):
  - Each npz carries `model_name` (e.g. 'BAAI/bge-small-zh-v1.5') and
    `fingerprint` = sha1 of (sorted job_ids + sum of len(jd_text)).
  - At recommend time we verify the index matches the current jobs.parquet
    via the same fingerprint; mismatch -> tell user to rerun build_index.
  - The script is idempotent: same parquet + same model -> same npz.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd


DEFAULT_MODEL = "BAAI/bge-small-zh-v1.5"
DEFAULT_BATCH = 32


def fingerprint(job_ids: list[str], jd_lengths: list[int]) -> str:
    """Stable index fingerprint. Used to verify npz matches current parquet."""
    h = hashlib.sha1()
    for jid, ln in zip(job_ids, jd_lengths):
        h.update(jid.encode("utf-8"))
        h.update(b"|")
        h.update(str(ln).encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def build_text_for_embedding(row: pd.Series) -> str:
    """The exact string fed into the model.

    We prepend title + company so that JD body is contextualized by what role
    it's for. This is also what bge model authors recommend (concat short
    metadata + body separated by newlines).
    """
    parts = [
        str(row.get("title") or "").strip(),
        str(row.get("company") or "").strip(),
        str(row.get("jd_text") or "").strip(),
    ]
    return "\n".join(p for p in parts if p)


def encode(model, texts: list[str], batch: int = DEFAULT_BATCH) -> np.ndarray:
    """Run the bge model in batches. Returns L2-normalized float32 vectors."""
    vecs = model.encode(
        texts,
        batch_size=batch,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return vecs.astype("float32")


def main(jobs_parquet: Path, out_dir: Path, model_name: str, batch: int) -> None:
    if not jobs_parquet.exists():
        raise SystemExit(f"jobs.parquet not found at {jobs_parquet}. "
                         f"Run scripts/ingest_all.py first.")

    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(jobs_parquet)
    if len(df) == 0:
        raise SystemExit("jobs.parquet is empty.")

    print(f"Loaded {len(df)} jobs from {jobs_parquet.relative_to(PROJECT_ROOT)}")
    print(f"Loading model: {model_name}")
    print("(first run downloads ~100MB to your HuggingFace cache.)")

    from sentence_transformers import SentenceTransformer
    t0 = time.time()
    model = SentenceTransformer(model_name)
    print(f"Model loaded in {time.time() - t0:.1f}s")

    texts = [build_text_for_embedding(r) for _, r in df.iterrows()]
    job_ids = df["job_id"].astype(str).tolist()
    jd_lens = df["jd_text"].astype(str).map(len).tolist()
    fp = fingerprint(job_ids, jd_lens)

    print(f"Encoding {len(texts)} JDs (batch={batch})...")
    t0 = time.time()
    vecs = encode(model, texts, batch=batch)
    dt = time.time() - t0
    print(f"Encoded in {dt:.1f}s ({len(texts) / max(dt, 1e-6):.1f} jobs/s) "
          f"shape={vecs.shape} dtype={vecs.dtype}")

    npz_path = out_dir / "jobs_embeddings.npz"
    np.savez(
        npz_path,
        ids=np.array(job_ids, dtype=object),
        vecs=vecs,
        model_name=np.array(model_name),
        fingerprint=np.array(fp),
    )
    print(f"Wrote {npz_path}  ({npz_path.stat().st_size / 1024:.0f} KB)")

    meta_cols = ["job_id", "platform", "title", "company", "city",
                 "job_type", "seniority", "salary_raw", "url", "jd_text"]
    meta_cols = [c for c in meta_cols if c in df.columns]
    meta = df[meta_cols].copy()
    meta_path = out_dir / "jobs_meta.parquet"
    meta.to_parquet(meta_path, index=False)
    print(f"Wrote {meta_path}")

    print(f"\nfingerprint: {fp}")


def cli() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default="data/unified/jobs.parquet",
                    help="Path to Stage 1-3 unified jobs parquet.")
    ap.add_argument("--out", default="index",
                    help="Output dir for npz + meta.")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--batch", type=int, default=DEFAULT_BATCH)
    args = ap.parse_args()

    jobs_path = (PROJECT_ROOT / args.jobs).resolve()
    out_dir = (PROJECT_ROOT / args.out).resolve()
    main(jobs_path, out_dir, args.model, args.batch)
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
