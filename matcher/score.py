"""Hard filter + multi-dimensional scoring.

Keyword matching note:
  Some keywords are short ASCII strings (e.g. 'AI', 'R', 'C'). Plain
  substring matching would mis-hit 'Associate', 'PyTorch' etc. So we
  use word-boundary regex for any keyword that is fully ASCII; for
  CJK / mixed keywords we keep plain `str.contains` since CJK has no
  word boundary concept and substring is what users mean.

Pipeline:
  1. apply_filters(meta, prefs)      -> drop rows that fail hard constraints
  2. semantic_similarity(...)        -> cosine sim between resume vec and each jd vec
  3. keyword_score(...)              -> fraction of must/nice keywords appearing in jd
  4. title_score(...)                -> 1.0 if any target_title is in title, else partial / 0
  5. location_score(...)             -> 1.0 if city in target_cities, else 0
  6. job_type_score(...)             -> 1.0 if type in target list, else 0
  7. final_score = sum(weights[i] * score[i])

All scores normalized to [0, 1]. Weights live in preferences.yaml.

Design rule (CLAUDE.md): every score component is independently testable
and has a clear meaning ("did this dimension match?"). Don't bundle them.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
import pandas as pd


def _is_ascii(s: str) -> bool:
    return s.isascii()


def _kw_hit_series(haystack: pd.Series, kw: str) -> pd.Series:
    """Return a boolean Series for whether `kw` is in each row of `haystack`.

    ASCII keywords use word boundaries to avoid sub-token matches
    ('AI' shouldn't match 'Associate'). CJK keywords use plain substring
    matching (Chinese has no word boundary).
    """
    if _is_ascii(kw):
        pattern = r"(?:^|[^A-Za-z0-9_])" + re.escape(kw) + r"(?:$|[^A-Za-z0-9_])"
        return haystack.str.contains(pattern, regex=True, na=False)
    return haystack.str.contains(kw, regex=False, na=False)


# ---------------------------------------------------------------------------
# hard filters
# ---------------------------------------------------------------------------

def apply_filters(meta: pd.DataFrame, prefs: dict) -> tuple[pd.DataFrame, dict]:
    """Apply hard constraints from preferences.yaml. Returns (kept_df, stats).

    The original index of `meta` is preserved (we use `.loc` semantics in
    the caller to align with embeddings).
    """
    f = prefs.get("filters", {}) or {}
    keep = pd.Series(True, index=meta.index)
    stats = {"input": int(len(meta))}

    target_cities = [c.strip() for c in (f.get("target_cities") or []) if c]
    if target_cities:
        m = meta["city"].astype(str).str.strip().isin(target_cities)
        stats["dropped_city"] = int((~m & keep).sum())
        keep &= m

    target_types = [t.strip().lower() for t in (f.get("target_job_types") or []) if t]
    if target_types:
        m = meta["job_type"].astype(str).str.strip().str.lower().isin(target_types)
        stats["dropped_job_type"] = int((~m & keep).sum())
        keep &= m

    min_chars = int(f.get("min_jd_chars") or 0)
    if min_chars > 0:
        m = meta["jd_text"].astype(str).str.len() >= min_chars
        stats["dropped_short_jd"] = int((~m & keep).sum())
        keep &= m

    excluded_kw = [k for k in (f.get("exclude_keywords") or []) if k]
    if excluded_kw:
        haystack = (meta["title"].astype(str).str.lower()
                    + " " + meta["jd_text"].astype(str).str.lower())
        m = pd.Series(True, index=meta.index)
        for kw in excluded_kw:
            m &= ~_kw_hit_series(haystack, kw.lower())
        stats["dropped_excluded_kw"] = int((~m & keep).sum())
        keep &= m

    excluded_co = [c.strip() for c in (f.get("exclude_companies") or []) if c]
    if excluded_co:
        m = ~meta["company"].astype(str).str.strip().isin(excluded_co)
        stats["dropped_excluded_company"] = int((~m & keep).sum())
        keep &= m

    stats["output"] = int(keep.sum())
    return meta[keep].copy(), stats


# ---------------------------------------------------------------------------
# scoring components — each in [0, 1]
# ---------------------------------------------------------------------------

def semantic_similarity(resume_vec: np.ndarray, jd_vecs: np.ndarray) -> np.ndarray:
    """Cosine sim assuming both are L2-normalized (bge default)."""
    sims = jd_vecs @ resume_vec
    return np.clip((sims + 1) / 2, 0, 1).astype("float32")


def keyword_score(meta: pd.DataFrame, prefs: dict) -> np.ndarray:
    """Two-tier keyword overlap.

    must_have_keywords contribute weight 1.0 each.
    nice_to_have_keywords contribute weight 0.5 each.
    Score = sum(weighted_hits) / max_possible. In [0, 1].
    Empty config -> score 0 (no signal).
    """
    sc = prefs.get("scoring", {}) or {}
    must = [k.lower() for k in (sc.get("must_have_keywords") or []) if k]
    nice = [k.lower() for k in (sc.get("nice_to_have_keywords") or []) if k]
    if not must and not nice:
        return np.zeros(len(meta), dtype="float32")

    max_score = len(must) * 1.0 + len(nice) * 0.5
    haystack = (meta["title"].astype(str).str.lower()
                + " " + meta["jd_text"].astype(str).str.lower())

    hits = pd.Series(0.0, index=meta.index)
    for kw in must:
        hits += _kw_hit_series(haystack, kw).astype(float) * 1.0
    for kw in nice:
        hits += _kw_hit_series(haystack, kw).astype(float) * 0.5

    return (hits / max_score).clip(0, 1).to_numpy().astype("float32")


def title_score(meta: pd.DataFrame, prefs: dict) -> np.ndarray:
    """Boost when one of target_titles appears in job title (case-insensitive)."""
    targets = [t.lower() for t in
               (prefs.get("scoring", {}).get("target_titles") or []) if t]
    if not targets:
        return np.zeros(len(meta), dtype="float32")
    titles = meta["title"].astype(str).str.lower()
    hits = pd.Series(False, index=meta.index)
    for t in targets:
        hits |= _kw_hit_series(titles, t)
    return hits.astype("float32").to_numpy()


def location_score(meta: pd.DataFrame, prefs: dict) -> np.ndarray:
    cities = [c.strip() for c in
              (prefs.get("filters", {}).get("target_cities") or []) if c]
    if not cities:
        return np.ones(len(meta), dtype="float32")
    m = meta["city"].astype(str).str.strip().isin(cities)
    return m.astype("float32").to_numpy()


def job_type_score(meta: pd.DataFrame, prefs: dict) -> np.ndarray:
    types = [t.strip().lower() for t in
             (prefs.get("filters", {}).get("target_job_types") or []) if t]
    if not types:
        return np.ones(len(meta), dtype="float32")
    m = meta["job_type"].astype(str).str.strip().str.lower().isin(types)
    return m.astype("float32").to_numpy()


# ---------------------------------------------------------------------------
# big-tech soft-deprioritization
# ---------------------------------------------------------------------------

def is_big_tech(meta: pd.DataFrame, prefs: dict) -> np.ndarray:
    """Return a boolean array marking rows whose company matches any alias in
    `scoring.big_tech_companies`. Matching is case-insensitive substring on
    the company field — e.g. alias '腾讯' matches '腾讯科技'.

    Empty alias list -> all-False (penalty becomes a no-op).
    """
    sc = prefs.get("scoring", {}) or {}
    aliases = [a.strip() for a in (sc.get("big_tech_companies") or []) if a]
    if not aliases:
        return np.zeros(len(meta), dtype=bool)
    company = meta["company"].astype(str).str.lower()
    flag = pd.Series(False, index=meta.index)
    for a in aliases:
        flag |= company.str.contains(a.lower(), regex=False, na=False)
    return flag.to_numpy()


# ---------------------------------------------------------------------------
# final aggregation
# ---------------------------------------------------------------------------

@dataclass
class ScoreBreakdown:
    """Per-row breakdown for transparency in the recommendation report."""
    semantic: float
    keyword: float
    title: float
    location: float
    job_type: float
    final: float


DEFAULT_WEIGHTS = {
    "semantic": 0.60,
    "keyword": 0.20,
    "title": 0.10,
    "location": 0.05,
    "job_type": 0.05,
}


def normalized_weights(prefs: dict) -> dict[str, float]:
    """Read weights from prefs and renormalize so they sum to 1.0."""
    raw = (prefs.get("scoring", {}) or {}).get("weights", {}) or {}
    w = {k: float(raw.get(k, DEFAULT_WEIGHTS[k])) for k in DEFAULT_WEIGHTS}
    s = sum(w.values())
    if s <= 0:
        return DEFAULT_WEIGHTS.copy()
    return {k: v / s for k, v in w.items()}


def final_score(meta: pd.DataFrame, jd_vecs: np.ndarray,
                resume_vec: np.ndarray, prefs: dict) -> tuple[np.ndarray, dict]:
    """Compute final score per row. Returns (scores, components_dict).

    components_dict maps name -> per-row np.ndarray, useful for the renderer
    so it can show why a job ranked where it did.
    """
    if len(meta) != jd_vecs.shape[0]:
        raise ValueError(
            f"meta rows ({len(meta)}) != jd_vecs rows ({jd_vecs.shape[0]}). "
            f"They must be aligned (same row order)."
        )

    w = normalized_weights(prefs)
    s_sem = semantic_similarity(resume_vec, jd_vecs)
    s_kw = keyword_score(meta, prefs)
    s_ti = title_score(meta, prefs)
    s_lo = location_score(meta, prefs)
    s_jt = job_type_score(meta, prefs)

    base = (w["semantic"] * s_sem
            + w["keyword"] * s_kw
            + w["title"] * s_ti
            + w["location"] * s_lo
            + w["job_type"] * s_jt).astype("float32")

    big_tech = is_big_tech(meta, prefs)
    penalty = float((prefs.get("scoring", {}) or {}).get("big_tech_penalty", 1.0))
    penalty = max(0.0, min(1.0, penalty))
    multiplier = np.where(big_tech, penalty, 1.0).astype("float32")
    final = (base * multiplier).astype("float32")

    components = {
        "semantic": s_sem,
        "keyword": s_kw,
        "title": s_ti,
        "location": s_lo,
        "job_type": s_jt,
        "is_big_tech": big_tech,
        "big_tech_penalty": penalty,
        "base": base,
        "final": final,
        "weights": w,
    }
    return final, components
