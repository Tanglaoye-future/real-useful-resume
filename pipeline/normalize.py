"""Source -> unified Job adapters.

One adapter per crawler output format. Each adapter:
  - takes a single raw record (dict) + the file path it came from
  - returns a `Job` instance (or None to skip)
  - is pure: no I/O, no global state

Adapters are registered in ADAPTERS so `scripts/ingest_all.py` can route
files based on path conventions. New sources only need: a new adapter
function + an entry in ADAPTERS.
"""
from __future__ import annotations

import re
from typing import Callable, Optional
from urllib.parse import urlparse

from .clean_jd import clean_jd, join_sections
from .schema import Job, JobType, SalaryUnit, Seniority, make_job_id


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

_SALARY_RE = re.compile(
    r"(?P<min>\d+(?:\.\d+)?)\s*[kK]?\s*[-~–]\s*(?P<max>\d+(?:\.\d+)?)\s*(?P<unit>[kK]|元/天|/天|元/月|/月|元/小时|/小时|/year|/yr)?",
)
_SINGLE_SALARY_RE = re.compile(r"(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>[kK]|元/天|/天|元/月|/月)?")

_K_FACTOR = 1000


def parse_salary(raw: str) -> tuple[Optional[float], Optional[float], SalaryUnit]:
    """Best-effort parse of salary strings.

    Examples it must handle:
      '5k-8k'              -> (5000, 8000, MONTH)
      '5K-8K'              -> (5000, 8000, MONTH)
      '150-180/天'         -> (150, 180, DAY)
      '302-568元/天'       -> (302, 568, DAY)
      '350-400 RMB per hour' -> (350, 400, HOUR)  [via 'hour' keyword fallback]
      ''                   -> (None, None, UNKNOWN)
    """
    if not raw:
        return None, None, SalaryUnit.UNKNOWN
    s = raw.strip()
    s_lc = s.lower()

    unit = SalaryUnit.UNKNOWN
    if "天" in s or "/day" in s_lc or "per day" in s_lc:
        unit = SalaryUnit.DAY
    elif "小时" in s or "hour" in s_lc:
        unit = SalaryUnit.HOUR
    elif "year" in s_lc or "/yr" in s_lc or "annual" in s_lc:
        unit = SalaryUnit.YEAR
    elif "月" in s or "/mo" in s_lc or "month" in s_lc:
        unit = SalaryUnit.MONTH

    m = _SALARY_RE.search(s)
    if m:
        lo = float(m.group("min"))
        hi = float(m.group("max"))
        unit_token = (m.group("unit") or "").lower()
        if "k" in unit_token or ("k" in s_lc and unit == SalaryUnit.UNKNOWN):
            lo *= _K_FACTOR
            hi *= _K_FACTOR
            if unit == SalaryUnit.UNKNOWN:
                unit = SalaryUnit.MONTH
        return lo, hi, unit

    m2 = _SINGLE_SALARY_RE.search(s)
    if m2:
        v = float(m2.group("val"))
        if "k" in (m2.group("unit") or "").lower() or "k" in s_lc:
            v *= _K_FACTOR
            if unit == SalaryUnit.UNKNOWN:
                unit = SalaryUnit.MONTH
        return v, v, unit

    return None, None, unit


def map_seniority(raw: str) -> Seniority:
    if not raw:
        return Seniority.UNKNOWN
    s = raw.strip().lower()
    if s in {"intern", "internship", "实习"}:
        return Seniority.INTERN
    if s in {"junior", "no prior experience required", "初级"}:
        return Seniority.JUNIOR
    if s in {"mid", "middle", "中级"}:
        return Seniority.MID
    if s in {"senior", "高级", "executive"}:
        return Seniority.SENIOR
    if s in {"lead", "principal", "manager", "主管"}:
        return Seniority.LEAD
    return Seniority.UNKNOWN


def map_job_type(raw: str) -> JobType:
    if not raw:
        return JobType.UNKNOWN
    s = raw.strip().lower()
    if "intern" in s or "实习" in s:
        return JobType.INTERNSHIP
    if "校招" in s or "应届" in s or "campus" in s:
        return JobType.CAMPUS
    if "freelance" in s or "兼职" in s or "part" in s:
        return JobType.FREELANCE
    if "full" in s or "全职" in s:
        return JobType.FULLTIME
    return JobType.UNKNOWN


def _safe(rec: dict, key: str, default: str = "") -> str:
    v = rec.get(key, default)
    if v is None:
        return default
    return str(v).strip()


def _id_from_url(url: str) -> str:
    """Fallback: derive a stable id from URL path basename."""
    if not url:
        return ""
    path = urlparse(url).path
    base = path.rstrip("/").split("/")[-1]
    return base or url


_TITLE_FALLBACK_RE = re.compile(
    r"(?:岗位\s*名?\s*称|招聘\s*岗位|职位\s*名?\s*称|Position)\s*[:：]\s*([^\n\r。]+)",
    re.IGNORECASE,
)
_TITLE_PREFIX_STRIP = re.compile(r"^\s*\[[^\]]+\]\s*")


def extract_title_from_jd(jd_text: str, max_first_line_len: int = 40) -> str:
    """Best-effort extract a real job title from a JD body.

    Strategy (in order):
      1. If first non-empty line is short (<= max_first_line_len chars),
         use it as the title.
      2. Otherwise look for explicit '岗位名称: X' / '招聘岗位: X' patterns.
      3. Otherwise return ''.
    """
    if not jd_text:
        return ""
    lines = [ln.strip() for ln in jd_text.splitlines() if ln.strip()]
    if lines:
        first = lines[0]
        if 1 <= len(first) <= max_first_line_len:
            return first
    m = _TITLE_FALLBACK_RE.search(jd_text)
    if m:
        cand = m.group(1).strip()
        if cand and len(cand) <= 60:
            return cand
    return ""


# ---------------------------------------------------------------------------
# adapters
# ---------------------------------------------------------------------------

def adapter_yingjiesheng(rec: dict, raw_path: str) -> Optional[Job]:
    """应届生 (yingjiesheng) — JD body is in `jd_content`.

    Title in raw is shaped '[城市]<company>' (e.g. '[上海]上海募艺...'). After
    stripping the city prefix it equals the company name — useless for matching.
    We fall back to the JD's first short line, which on yingjiesheng is the
    real position name (verified across multiple samples).
    """
    url = _safe(rec, "jd_url") or _safe(rec, "url")
    sjid = _safe(rec, "source_job_id") or _id_from_url(url)
    if not sjid:
        return None

    raw_title = _safe(rec, "job_name")
    title = _TITLE_PREFIX_STRIP.sub("", raw_title).strip()
    company = _safe(rec, "company_name")

    jd = clean_jd(_safe(rec, "jd_content")) or clean_jd(_safe(rec, "job_description"))

    if title and company and (title == company or company in title):
        better = extract_title_from_jd(jd)
        if better:
            title = better

    salary_raw = _safe(rec, "salary")
    smin, smax, sunit = parse_salary(salary_raw)
    if rec.get("salary_min") and rec.get("salary_max"):
        try:
            smin = float(rec["salary_min"])
            smax = float(rec["salary_max"])
        except (TypeError, ValueError):
            pass

    return Job(
        job_id=make_job_id("yingjiesheng", sjid),
        platform="yingjiesheng",
        source_job_id=sjid,
        url=url,
        title=title,
        company=company,
        city=_safe(rec, "city") or _safe(rec, "location"),
        district=_safe(rec, "district"),
        job_type=map_job_type(_safe(rec, "job_type") or _safe(rec, "employment_type")),
        seniority=Seniority.UNKNOWN,
        salary_min=smin,
        salary_max=smax,
        salary_unit=sunit,
        salary_raw=salary_raw,
        education_req=_safe(rec, "education_requirement"),
        experience_req=_safe(rec, "experience_requirement"),
        industry=_safe(rec, "company_industry"),
        publish_date=_safe(rec, "publish_date") or _safe(rec, "crawled_at"),
        jd_text=jd,
        skills=[],
        raw_path=raw_path,
    )


def adapter_shixiseng(rec: dict, raw_path: str) -> Optional[Job]:
    """实习僧 (shixiseng) — JD split across job_description + job_requirement."""
    sjid = _safe(rec, "job_id") or _id_from_url(_safe(rec, "url"))
    if not sjid:
        return None

    jd = clean_jd(join_sections([_safe(rec, "job_description"), _safe(rec, "job_requirement")]))
    salary_raw = _safe(rec, "salary_text")
    smin, smax, sunit = parse_salary(salary_raw)

    return Job(
        job_id=make_job_id("shixiseng", sjid),
        platform="shixiseng",
        source_job_id=sjid,
        url=_safe(rec, "url"),
        title=_safe(rec, "job_name"),
        company=_safe(rec, "company_name"),
        city=_safe(rec, "location"),
        district="",
        job_type=JobType.INTERNSHIP,
        seniority=Seniority.INTERN,
        salary_min=smin,
        salary_max=smax,
        salary_unit=sunit,
        salary_raw=salary_raw,
        education_req=_safe(rec, "education"),
        experience_req=_safe(rec, "experience"),
        industry=_safe(rec, "company_industry"),
        publish_date=_safe(rec, "publish_date") or _safe(rec, "crawled_at"),
        jd_text=jd,
        skills=[],
        raw_path=raw_path,
    )


def adapter_smartshanghai(rec: dict, raw_path: str) -> Optional[Job]:
    """SmartShanghai — JD body has heavy site-footer pollution; clean_jd handles it."""
    sjid = _safe(rec, "source_job_id") or _id_from_url(_safe(rec, "url"))
    if not sjid:
        return None

    jd = clean_jd(_safe(rec, "job_description"))

    return Job(
        job_id=make_job_id("smartshanghai", sjid),
        platform="smartshanghai",
        source_job_id=sjid,
        url=_safe(rec, "url"),
        title=_safe(rec, "job_name"),
        company=_safe(rec, "company_name"),
        city=_safe(rec, "city"),
        district="",
        job_type=map_job_type(_safe(rec, "job_type")),
        seniority=map_seniority(_safe(rec, "seniority")),
        salary_min=None,
        salary_max=None,
        salary_unit=SalaryUnit.UNKNOWN,
        salary_raw="",
        education_req="",
        experience_req="",
        industry=_safe(rec, "category"),
        publish_date=_safe(rec, "publish_date") or _safe(rec, "crawled_at"),
        jd_text=jd,
        skills=[],
        raw_path=raw_path,
    )


_LIEPIN_BOILERPLATE_RE = re.compile(
    r"(?:猎聘|liepin\.com|ICP|Copyright|举报|津ICP|经营许可证|企业服务热线|jubao@)",
    re.IGNORECASE,
)

def adapter_liepin(rec: dict, raw_path: str) -> Optional[Job]:
    """猎聘 (liepin).

    Supports two raw schemas:
      A. Old spider (jobs_liepin_*.json):
         job_id, url, position_name, salary_text, job_description, job_requirements
      B. New spider (liepin_full_*.json, produced by LiepinSpiderV6):
         source_job_id, jd_url, job_name, salary, jd_content, job_description,
         job_requirement, salary_min/max, city, location

    When the captured JD is detected as Liepin boilerplate (footer/copyright
    text) it is discarded so we fall back to a minimal structured summary built
    from title + company + salary.  This keeps the record searchable even when
    the detail-page scrape failed.
    """
    # ── ID ─────────────────────────────────────────────────────────────────
    raw_jid = _safe(rec, "source_job_id") or _safe(rec, "job_id")
    sjid = raw_jid[len("liepin_"):] if raw_jid.startswith("liepin_") else raw_jid
    url = _safe(rec, "jd_url") or _safe(rec, "url")
    sjid = sjid or _id_from_url(url)
    if not sjid:
        return None

    # ── title / company ────────────────────────────────────────────────────
    title   = _safe(rec, "job_name") or _safe(rec, "position_name")
    company = _safe(rec, "company_name")

    # ── JD text ────────────────────────────────────────────────────────────
    raw_jd = join_sections([
        _safe(rec, "jd_content"),
        _safe(rec, "job_description"),
        _safe(rec, "job_requirement") or _safe(rec, "job_requirements"),
    ])
    jd = clean_jd(raw_jd)

    # If jd is purely Liepin boilerplate, discard it
    if jd and _LIEPIN_BOILERPLATE_RE.search(jd):
        # Keep only lines that don't look like footer / copyright
        clean_lines = [
            ln for ln in jd.splitlines()
            if ln.strip() and not _LIEPIN_BOILERPLATE_RE.search(ln)
        ]
        jd = "\n".join(clean_lines).strip()

    # Fallback: synthesise a minimal JD so the record is still matchable
    if not jd:
        parts = [p for p in [title, company, _safe(rec, "company_industry")] if p]
        jd = " | ".join(parts)

    if not jd:
        return None

    # ── salary ─────────────────────────────────────────────────────────────
    salary_raw = _safe(rec, "salary") or _safe(rec, "salary_text")
    smin, smax, sunit = parse_salary(salary_raw)
    # New spider writes pre-parsed salary_min/max
    if not smin and rec.get("salary_min"):
        try:
            smin = float(rec["salary_min"])
            smax = float(rec.get("salary_max") or smin)
            unit_str = _safe(rec, "salary_unit").lower()
            if unit_str in ("k", "月"):
                sunit = SalaryUnit.MONTH
                smin *= 1000
                smax *= 1000
            elif unit_str in ("天", "day"):
                sunit = SalaryUnit.DAY
        except (TypeError, ValueError):
            pass

    job_type_raw = _safe(rec, "job_type") or _safe(rec, "employment_type") or _safe(rec, "experience")

    return Job(
        job_id=make_job_id("liepin", sjid),
        platform="liepin",
        source_job_id=sjid,
        url=url,
        title=title,
        company=company,
        city=_safe(rec, "city") or _safe(rec, "location", "").split("-")[0].split("·")[0].strip(),
        district=_safe(rec, "district"),
        job_type=map_job_type(job_type_raw) if job_type_raw else JobType.INTERNSHIP,
        seniority=map_seniority(_safe(rec, "experience")),
        salary_min=smin,
        salary_max=smax,
        salary_unit=sunit,
        salary_raw=salary_raw,
        education_req=_safe(rec, "education_requirement") or _safe(rec, "education"),
        experience_req=_safe(rec, "experience_requirement") or _safe(rec, "experience"),
        industry=_safe(rec, "company_industry"),
        publish_date=_safe(rec, "publish_date") or _safe(rec, "crawled_at") or _safe(rec, "crawl_time"),
        jd_text=jd,
        skills=[t for t in _safe(rec, "job_tags").split("|") if t]
               or [t for t in _safe(rec, "skill_tags").split("|") if t],
        raw_path=raw_path,
    )


def adapter_foreign_official(rec: dict, raw_path: str) -> Optional[Job]:
    """Foreign company official sites — schema:
    url, company, name, city, jd_raw, salary, company_size, duration, academic,
    publish_time, deadline, collect_time, source, recruit_type, raw_tags,
    external_job_id, ...
    """
    sjid = _safe(rec, "external_job_id") or _id_from_url(_safe(rec, "url"))
    if not sjid:
        return None

    platform = _safe(rec, "source") or "foreign_official"
    jd = clean_jd(_safe(rec, "jd_raw"))
    salary_raw = _safe(rec, "salary")
    smin, smax, sunit = parse_salary(salary_raw)

    return Job(
        job_id=make_job_id(platform, sjid),
        platform=platform,
        source_job_id=sjid,
        url=_safe(rec, "url"),
        title=_safe(rec, "name"),
        company=_safe(rec, "company"),
        city=_safe(rec, "city"),
        district="",
        job_type=map_job_type(_safe(rec, "recruit_type")),
        seniority=Seniority.UNKNOWN,
        salary_min=smin,
        salary_max=smax,
        salary_unit=sunit,
        salary_raw=salary_raw,
        education_req=_safe(rec, "academic"),
        experience_req="",
        industry="",
        publish_date=_safe(rec, "publish_time") or _safe(rec, "collect_time"),
        jd_text=jd,
        skills=[],
        raw_path=raw_path,
    )


def adapter_integrated_jobs(rec: dict, raw_path: str) -> Optional[Job]:
    """integrated_jobs_*.json — consolidated snapshot produced by foreign_pipeline_v2.

    Covers platforms: 51job, bytedance, bytedance_crawler, official_xiaohongshu,
    official_xiaohongshu_raw, official_meituan, official_tencent_api,
    official_kuaishou_api, cdp_alibaba, cdp_bilibili, cdp_jd, cdp_kuaishou,
    cdp_meituan, cdp_tencent, official_jd_api, official_alibaba, liepin.

    Schema fields used:
      source_job_id, job_name, company_name, location, city, salary,
      job_description, job_requirement, jd_content, experience_requirement,
      education_requirement, source, platform, crawled_at, publish_date,
      company_industry, job_type, employment_type, jd_url, url.
    """
    platform_raw = _safe(rec, "platform") or _safe(rec, "source") or "integrated"
    platform = platform_raw.lower().replace(" ", "_")

    sjid = _safe(rec, "source_job_id") or _safe(rec, "job_id")
    url  = _safe(rec, "jd_url") or _safe(rec, "url") or _safe(rec, "direct_apply_url")
    # bytedance uses the detail URL as source_job_id
    if not sjid and url:
        sjid = _id_from_url(url)
    if not sjid:
        return None

    title   = _safe(rec, "job_name")
    company = _safe(rec, "company_name")

    jd = clean_jd(
        join_sections([
            _safe(rec, "jd_content"),
            _safe(rec, "job_description"),
            _safe(rec, "job_requirement"),
        ])
    )
    if not jd:
        return None  # skip records with no JD content

    city = _safe(rec, "city") or _safe(rec, "location", "").split("·")[0].split("—")[0].strip()

    salary_raw = _safe(rec, "salary")
    smin, smax, sunit = parse_salary(salary_raw)
    if not smin and rec.get("salary_min"):
        try:
            smin = float(rec["salary_min"])
            smax = float(rec.get("salary_max") or smin)
        except (TypeError, ValueError):
            pass

    publish_date = _safe(rec, "publish_date") or _safe(rec, "crawled_at") or _safe(rec, "crawl_time")

    return Job(
        job_id=make_job_id(platform, sjid),
        platform=platform,
        source_job_id=sjid,
        url=url,
        title=title,
        company=company,
        city=city,
        district=_safe(rec, "district"),
        job_type=map_job_type(_safe(rec, "job_type") or _safe(rec, "employment_type")),
        seniority=Seniority.INTERN,
        salary_min=smin,
        salary_max=smax,
        salary_unit=sunit,
        salary_raw=salary_raw,
        education_req=_safe(rec, "education_requirement"),
        experience_req=_safe(rec, "experience_requirement"),
        industry=_safe(rec, "company_industry"),
        publish_date=publish_date,
        jd_text=jd,
        skills=[t for t in _safe(rec, "job_tags").split("|") if t]
               or [t for t in _safe(rec, "skill_tags").split("|") if t],
        raw_path=raw_path,
    )


def adapter_linkedin(rec: dict, raw_path: str) -> Optional[Job]:
    """LinkedIn (authenticated, browser-assisted capture).

    Expected raw schema (jsonl), produced by linkedin pipeline:
      url, source_job_id?, title, company, location/city, jd_text, publish_date,
      seniority?, job_type?, skills?

    Notes:
    - Salary is usually absent on LinkedIn; we keep it empty.
    - `source_job_id` falls back to URL-derived basename.
    """
    url = _safe(rec, "url")
    sjid = _safe(rec, "source_job_id") or _id_from_url(url)
    if not sjid:
        return None

    title = _safe(rec, "title") or _safe(rec, "job_title") or _safe(rec, "job_name")
    company = _safe(rec, "company") or _safe(rec, "company_name")
    city = _safe(rec, "city") or _safe(rec, "location")
    publish_date = _safe(rec, "publish_date") or _safe(rec, "posted_at")

    jd = clean_jd(_safe(rec, "jd_text") or _safe(rec, "description") or _safe(rec, "job_description"))
    if not jd:
        # Minimal fallback so list-only captures can be ingested and deduped.
        parts = [p for p in (title, company, city) if p]
        jd = " | ".join(parts)
    if not jd:
        return None

    skills = rec.get("skills") if isinstance(rec.get("skills"), list) else []
    if not skills:
        skills = [t for t in str(_safe(rec, "skills_raw")).split("|") if t]

    return Job(
        job_id=make_job_id("linkedin", sjid),
        platform="linkedin",
        source_job_id=sjid,
        url=url,
        title=title,
        company=company,
        city=city,
        district="",
        job_type=map_job_type(_safe(rec, "job_type")),
        seniority=map_seniority(_safe(rec, "seniority")),
        salary_min=None,
        salary_max=None,
        salary_unit=SalaryUnit.UNKNOWN,
        salary_raw="",
        education_req=_safe(rec, "education_req"),
        experience_req=_safe(rec, "experience_req"),
        industry=_safe(rec, "industry"),
        publish_date=publish_date,
        jd_text=jd,
        skills=skills,
        raw_path=raw_path,
    )


# ---------------------------------------------------------------------------
# router
# ---------------------------------------------------------------------------

AdapterFn = Callable[[dict, str], Optional[Job]]

ADAPTERS: dict[str, AdapterFn] = {
    "yingjiesheng": adapter_yingjiesheng,
    "shixiseng": adapter_shixiseng,
    "smartshanghai": adapter_smartshanghai,
    "liepin": adapter_liepin,
    "foreign_official": adapter_foreign_official,
    "integrated_jobs": adapter_integrated_jobs,
    "linkedin": adapter_linkedin,
}


def detect_source(path: str) -> Optional[str]:
    """Pick adapter key based on file path. Conventions:
      data/raw/yingjiesheng/*              -> yingjiesheng
      data/raw/shixiseng/*                 -> shixiseng
      data/raw/smartshanghai/*             -> smartshanghai
      data/raw/liepin/*                    -> liepin
      data/raw/merged/integrated_jobs_*    -> integrated_jobs
      outputs/raw/foreign_*_official_raw.csv -> foreign_official
    """
    p = path.replace("\\", "/").lower()
    if "data/raw/yingjiesheng/" in p:
        return "yingjiesheng"
    if "data/raw/shixiseng/" in p:
        return "shixiseng"
    if "data/raw/smartshanghai/" in p:
        return "smartshanghai"
    if "data/raw/liepin/" in p:
        return "liepin"
    if "data/raw/linkedin/" in p:
        return "linkedin"
    if "data/raw/merged/integrated_jobs_" in p:
        return "integrated_jobs"
    if "outputs/raw/foreign_" in p and "_official_raw.csv" in p:
        return "foreign_official"
    return None
