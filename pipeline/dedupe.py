"""Deduplication.

Three-stage strategy (each stage runs on the survivors of the previous one):
  1. Primary key: (platform, source_job_id). If two records share it, keep
     the one with the longer `jd_text` (more info).
  2. URL fallback: same canonical URL across rows -> keep the longer JD.
  3. Content fallback: same (company_lower, jd_first_500_chars_md5) -> keep
     the longer JD. This catches Amazon-style records where the source
     publishes the SAME JD under multiple jobIds with empty URLs.
     The company name is part of the key so two unrelated firms posting
     mock-templated JDs (e.g. test data) don't collapse into one row.

We never silently drop records: stats are returned so the caller can log them.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urlparse

from .schema import Job


# Length of the JD prefix used to compute the content fingerprint.
# Short enough that the 'fluff intro' (company blurb) still dominates and
# triggers collisions for true duplicates; long enough that a real difference
# in body text breaks the hash.
_JD_HASH_PREFIX_LEN = 500
_JD_HASH_MIN_LEN = 80  # don't hash near-empty JDs


@dataclass
class DedupeStats:
    input_count: int
    output_count: int
    dropped_pk_collision: int
    dropped_url_collision: int
    dropped_content_collision: int = 0

    def report(self) -> str:
        return (
            f"input={self.input_count} output={self.output_count} "
            f"dropped_pk={self.dropped_pk_collision} "
            f"dropped_url={self.dropped_url_collision} "
            f"dropped_content={self.dropped_content_collision}"
        )


def _canonical_url(url: str) -> str:
    if not url:
        return ""
    u = urlparse(url.strip())
    netloc = u.netloc.lower().lstrip("www.")
    path = u.path.rstrip("/")
    return f"{netloc}{path}"


def _better(a: Job, b: Job) -> Job:
    """Pick the record carrying more JD signal."""
    return a if len(a.jd_text) >= len(b.jd_text) else b


def _content_key(job: Job) -> str:
    """Stable content fingerprint scoped per company. Empty if jd is too short
    (too noisy to dedupe on)."""
    jd = (job.jd_text or "").strip()
    if len(jd) < _JD_HASH_MIN_LEN:
        return ""
    company = (job.company or "").strip().lower()
    h = hashlib.md5()
    h.update(company.encode("utf-8"))
    h.update(b"|")
    h.update(jd[:_JD_HASH_PREFIX_LEN].encode("utf-8"))
    return f"{company}::{h.hexdigest()}"


def dedupe(jobs: Iterable[Job]) -> tuple[list[Job], DedupeStats]:
    """Run dedupe, returning (kept_jobs, stats). Stable ordering preserved
    based on first-seen order of the winning record."""
    jobs_list = list(jobs)
    by_pk: dict[str, Job] = {}
    pk_collisions = 0

    for j in jobs_list:
        if j.job_id in by_pk:
            pk_collisions += 1
            by_pk[j.job_id] = _better(by_pk[j.job_id], j)
        else:
            by_pk[j.job_id] = j

    by_url: dict[str, Job] = {}
    url_collisions = 0
    after_url: list[Job] = []
    for j in by_pk.values():
        cu = _canonical_url(j.url)
        if cu and cu in by_url:
            url_collisions += 1
            existing = by_url[cu]
            winner = _better(existing, j)
            by_url[cu] = winner
            for i, x in enumerate(after_url):
                if x.job_id == existing.job_id:
                    after_url[i] = winner
                    break
        else:
            if cu:
                by_url[cu] = j
            after_url.append(j)

    by_content: dict[str, Job] = {}
    content_collisions = 0
    final: list[Job] = []
    for j in after_url:
        ck = _content_key(j)
        if ck and ck in by_content:
            content_collisions += 1
            existing = by_content[ck]
            winner = _better(existing, j)
            by_content[ck] = winner
            for i, x in enumerate(final):
                if x.job_id == existing.job_id:
                    final[i] = winner
                    break
        else:
            if ck:
                by_content[ck] = j
            final.append(j)

    stats = DedupeStats(
        input_count=len(jobs_list),
        output_count=len(final),
        dropped_pk_collision=pk_collisions,
        dropped_url_collision=url_collisions,
        dropped_content_collision=content_collisions,
    )
    return final, stats
