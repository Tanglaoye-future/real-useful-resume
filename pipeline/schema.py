"""Unified Job schema (v1).

Single source of truth for what a 'job' looks like after normalization.
Every adapter in `pipeline/normalize.py` MUST produce instances of `Job`.
Every downstream consumer (matcher, recommender) reads ONLY this schema.

Design notes:
- Keep the field set MINIMAL but matchable: title, company, city, jd_text,
  job_type, seniority, salary, requirements. Anything more goes into `extra`.
- All optional fields default to None / "" so partial sources don't crash.
- Salary is stored as min/max numeric + unit; raw string preserved for audit.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


SCHEMA_VERSION = "v1"


class JobType(str, Enum):
    INTERNSHIP = "internship"
    CAMPUS = "campus"
    FULLTIME = "fulltime"
    FREELANCE = "freelance"
    UNKNOWN = "unknown"


class Seniority(str, Enum):
    INTERN = "intern"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    UNKNOWN = "unknown"


class SalaryUnit(str, Enum):
    MONTH = "month"
    DAY = "day"
    HOUR = "hour"
    YEAR = "year"
    UNKNOWN = "unknown"


class Job(BaseModel):
    """Unified job record. v1.

    Primary key: (platform, source_job_id). Tested in dedupe.
    """

    job_id: str = Field(..., description="Globally unique. Built as f'{platform}:{source_job_id}'.")
    platform: str = Field(..., description="Source platform name. Lowercase ascii.")
    source_job_id: str = Field(..., description="Per-platform id (or url-derived if missing).")
    url: str = Field("", description="Canonical job page URL.")

    title: str = Field("", description="Job title, cleaned (no city prefix, no company suffix).")
    company: str = Field("", description="Hiring company name.")

    city: str = Field("", description="Primary city, normalized (e.g. 上海, 北京).")
    district: str = Field("", description="District / area within city, optional.")

    job_type: JobType = JobType.UNKNOWN
    seniority: Seniority = Seniority.UNKNOWN

    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_unit: SalaryUnit = SalaryUnit.UNKNOWN
    salary_raw: str = Field("", description="Original salary string, kept for audit.")

    education_req: str = Field("", description="Education requirement, e.g. 本科.")
    experience_req: str = Field("", description="Experience requirement, free-form.")
    industry: str = Field("", description="Company industry, free-form.")
    language_req: list[str] = Field(default_factory=list)

    jd_text: str = Field(
        "",
        description="Cleaned plain text of responsibilities + requirements. "
                    "This is the field used by embedding/matching downstream.",
    )
    skills: list[str] = Field(default_factory=list)

    raw_path: str = Field("", description="Source file this record came from (relative to project root).")
    ingest_time: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds") + "Z"
    )
    schema_version: str = Field(default=SCHEMA_VERSION)

    @field_validator("platform")
    @classmethod
    def _platform_lower(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("city")
    @classmethod
    def _city_strip(cls, v: str) -> str:
        return (v or "").strip()

    def parquet_dict(self) -> dict:
        """Flat dict ready for pandas/pyarrow. Enums -> str, lists kept."""
        d = self.model_dump()
        for k in ("job_type", "seniority", "salary_unit"):
            d[k] = d[k].value if hasattr(d[k], "value") else d[k]
        return d


def make_job_id(platform: str, source_job_id: str) -> str:
    """Canonical job_id constructor. Use everywhere instead of f-string by hand."""
    return f"{platform.strip().lower()}:{source_job_id.strip()}"
