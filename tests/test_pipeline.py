"""Pipeline unit tests.

Run from project root:
  py -3.11 -m pytest tests/test_pipeline.py -v

Each test uses a tiny synthetic record copied from real raw output, NOT
real files — keeps tests fast and CI-friendly.
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest  # noqa: E402

from pipeline.clean_jd import clean_jd, join_sections, normalize_whitespace, strip_html
from pipeline.dedupe import dedupe
from pipeline.normalize import (
    adapter_foreign_official,
    adapter_liepin,
    adapter_shixiseng,
    adapter_smartshanghai,
    adapter_yingjiesheng,
    detect_source,
    extract_title_from_jd,
    parse_salary,
)
from pipeline.schema import Job, JobType, SalaryUnit, Seniority, make_job_id


# ---------------------------------------------------------------------------
# clean_jd
# ---------------------------------------------------------------------------

def test_strip_html_decodes_entities_and_removes_tags():
    raw = "Bachelor&rsquo;s degree <a href='x'>here</a> &nbsp;required"
    out = strip_html(raw)
    assert "&rsquo;" not in out
    assert "<a" not in out
    assert "Bachelor" in out and "required" in out


def test_clean_jd_strips_smartshanghai_footer():
    raw = (
        "Description\nDo cool stuff.\nRead More\n"
        "SmartShanghai.com is the longest-running English online magazine "
        "in Shanghai. NAVIGATE About Us Contact Us Advertise FAQ"
    )
    out = clean_jd(raw)
    assert "Do cool stuff" in out
    assert "longest-running" not in out
    assert "Read More" not in out
    assert "NAVIGATE" not in out


def test_clean_jd_idempotent():
    raw = "Hello&nbsp;world<br/> Read More\n\n\n\nfoo"
    once = clean_jd(raw)
    twice = clean_jd(once)
    assert once == twice


def test_normalize_whitespace_collapses_blank_lines():
    raw = "a\n\n\n\nb\n   \nc"
    assert normalize_whitespace(raw) == "a\n\nb\n\nc"


def test_join_sections_drops_empty():
    assert join_sections(["a", "", None, "b"]) == "a\n\nb"


# ---------------------------------------------------------------------------
# salary parsing
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw,expected", [
    ("5k-8k",       (5000.0, 8000.0, SalaryUnit.MONTH)),
    ("5K-8K",       (5000.0, 8000.0, SalaryUnit.MONTH)),
    ("150-180/天",   (150.0, 180.0, SalaryUnit.DAY)),
    ("302-568元/天", (302.0, 568.0, SalaryUnit.DAY)),
    ("",            (None, None, SalaryUnit.UNKNOWN)),
])
def test_parse_salary(raw, expected):
    smin, smax, sunit = parse_salary(raw)
    assert smin == expected[0]
    assert smax == expected[1]
    assert sunit == expected[2]


# ---------------------------------------------------------------------------
# adapters
# ---------------------------------------------------------------------------

def test_adapter_yingjiesheng_falls_back_to_jd_first_line():
    """When raw title == company (yingjiesheng's known limitation), the
    adapter must extract the real position name from the JD body."""
    rec = {
        "job_name": "[上海]上海募艺文化传播有限公司",
        "company_name": "上海募艺文化传播有限公司",
        "location": "上海", "city": "上海",
        "salary": "5k-8k",
        "job_type": "校招/应届",
        "education_requirement": "本科及以上",
        "platform": "应届生",
        "source_job_id": "job-007-958-717",
        "jd_url": "https://www.yingjiesheng.com/job-007-958-717.html",
        "jd_content": "市场BD\n岗位职责\n做事\n任职要求\n本科以上",
    }
    job = adapter_yingjiesheng(rec, "data/raw/yingjiesheng/test.jsonl")
    assert job is not None
    assert job.job_id == "yingjiesheng:job-007-958-717"
    assert job.title == "市场BD"  # extracted from JD's first line
    assert job.city == "上海"
    assert job.job_type == JobType.CAMPUS
    assert job.salary_min == 5000 and job.salary_max == 8000
    assert "市场BD" in job.jd_text


def test_adapter_yingjiesheng_keeps_existing_title_when_not_company():
    """If raw title is already a real position name, don't overwrite it."""
    rec = {
        "job_name": "[上海]Java 开发工程师",
        "company_name": "上海某公司",
        "city": "上海",
        "source_job_id": "j1",
        "jd_url": "https://www.yingjiesheng.com/x.html",
        "jd_content": "公司介绍\n这是一段很长的公司介绍文字" * 10,
    }
    job = adapter_yingjiesheng(rec, "data/raw/yingjiesheng/test.jsonl")
    assert job is not None
    assert job.title == "Java 开发工程师"


def test_extract_title_from_jd_uses_first_short_line():
    assert extract_title_from_jd("市场BD\n下文很长") == "市场BD"


def test_extract_title_from_jd_uses_explicit_label_when_first_line_too_long():
    body = (
        "本招聘启示由复旦大学某学院某课题组发布，"
        "面向2026届毕业生与博士后研究人员，欢迎符合条件的有志青年报名应聘。\n"
        "岗位名称：信息化专员\n岗位职责...\n"
    )
    assert extract_title_from_jd(body) == "信息化专员"


def test_extract_title_from_jd_returns_empty_on_no_signal():
    # No first-line short title and no labelled pattern.
    body = "x" * 1000
    assert extract_title_from_jd(body) == ""


def test_adapter_shixiseng_joins_jd_and_requirement():
    rec = {
        "platform": "shixiseng",
        "job_id": "inn_jxenjxcezvtk",
        "job_name": "文员实习",
        "company_name": "睿民科技",
        "location": "上海",
        "salary_text": "150-180/天",
        "url": "https://www.shixiseng.com/intern/inn_jxenjxcezvtk",
        "job_description": "数据收集校验",
        "job_requirement": "本科及以上学历",
    }
    job = adapter_shixiseng(rec, "data/raw/shixiseng/test.jsonl")
    assert job is not None
    assert job.job_type == JobType.INTERNSHIP
    assert job.seniority == Seniority.INTERN
    assert "数据收集校验" in job.jd_text and "本科" in job.jd_text
    assert job.salary_unit == SalaryUnit.DAY


def test_adapter_smartshanghai_strips_footer():
    rec = {
        "platform": "smartshanghai",
        "url": "https://www.smartshanghai.com/jobs/x/123",
        "job_name": "Designer",
        "company_name": "X",
        "city": "上海",
        "job_description": (
            "Description\nMake stuff. Read More\n"
            "SmartShanghai.com is the longest-running... NAVIGATE About Us"
        ),
        "job_type": "Full time",
        "seniority": "Junior",
        "category": "arts-design-music",
        "source_job_id": "123",
    }
    job = adapter_smartshanghai(rec, "data/raw/smartshanghai/test.jsonl")
    assert job is not None
    assert "longest-running" not in job.jd_text
    assert "Read More" not in job.jd_text
    assert "Make stuff" in job.jd_text
    assert job.job_type == JobType.FULLTIME
    assert job.seniority == Seniority.JUNIOR


def test_adapter_liepin_basic():
    rec = {
        "job_id": "liepin_1775046301_0",
        "source": "liepin",
        "company_name": "阿里巴巴",
        "position_name": "算法工程师",
        "salary_min": 249,
        "salary_max": 358,
        "salary_text": "249-358元/天",
        "location": "上海",
        "experience": "在校/应届",
        "education": "本科",
        "job_description": "负责公司核心产品的开发和维护",
        "job_requirements": "熟悉Linux操作系统",
        "publish_date": "2026-03-21",
        "url": "https://www.liepin.com/job/1775046301.shtml",
    }
    job = adapter_liepin(rec, "data/raw/liepin/jobs_liepin_test.json")
    assert job is not None
    # 'liepin_' prefix is stripped from source_job_id to avoid 'liepin:liepin_'.
    assert job.job_id == "liepin:1775046301_0"
    assert job.platform == "liepin"
    assert job.title == "算法工程师"
    assert job.company == "阿里巴巴"
    assert job.city == "上海"
    assert job.salary_min == 249 and job.salary_max == 358
    assert job.salary_unit == SalaryUnit.DAY
    assert "Linux" in job.jd_text and "核心产品" in job.jd_text


def test_adapter_liepin_handles_missing_url_falls_back_to_job_id():
    rec = {
        "job_id": "liepin_x_42",
        "company_name": "Acme",
        "position_name": "Intern",
        "location": "上海",
    }
    job = adapter_liepin(rec, "data/raw/liepin/jobs_liepin_test.json")
    assert job is not None
    assert job.source_job_id == "x_42"


def test_adapter_foreign_official_basic():
    rec = {
        "url": "https://amazon.jobs/en/jobs/10397862/marketing-intern",
        "company": "Amazon / AWS",
        "name": "Marketing Intern",
        "city": "上海",
        "jd_raw": "Amazon strives to be...",
        "salary": "",
        "academic": "Bachelor",
        "source": "amazon_aws",
        "recruit_type": "实习",
        "external_job_id": "10397862",
    }
    job = adapter_foreign_official(rec, "outputs/raw/foreign_amazon_aws_official_raw.csv")
    assert job is not None
    assert job.platform == "amazon_aws"
    assert job.job_id == "amazon_aws:10397862"
    assert job.job_type == JobType.INTERNSHIP


# ---------------------------------------------------------------------------
# detect_source routing
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path,expected", [
    ("data/raw/yingjiesheng/yingjiesheng_latest.jsonl", "yingjiesheng"),
    ("data/raw/shixiseng/shixiseng_latest.jsonl", "shixiseng"),
    ("data/raw/smartshanghai/smartshanghai_latest.jsonl", "smartshanghai"),
    ("data/raw/liepin/jobs_liepin_20260401.json", "liepin"),
    ("outputs/raw/foreign_amazon_aws_official_raw.csv", "foreign_official"),
    ("data/raw/merged/foreign_candidate_raw_x.json", None),
    ("release_data/foreign_master_database_v2.csv", None),
])
def test_detect_source(path, expected):
    assert detect_source(path) == expected


# ---------------------------------------------------------------------------
# dedupe
# ---------------------------------------------------------------------------

def _mk(job_id: str, jd_text: str = "", url: str = "", company: str = "x") -> Job:
    plat, sjid = job_id.split(":", 1)
    return Job(
        job_id=job_id, platform=plat, source_job_id=sjid,
        url=url, title="x", company=company, city="x",
        jd_text=jd_text,
    )


def test_dedupe_keeps_longer_jd_on_pk_collision():
    a = _mk("p:1", jd_text="short")
    b = _mk("p:1", jd_text="much much longer description here")
    out, stats = dedupe([a, b])
    assert len(out) == 1
    assert out[0].jd_text == b.jd_text
    assert stats.dropped_pk_collision == 1


def test_dedupe_collapses_url_collision_across_platforms():
    a = _mk("p1:1", jd_text="aaa", url="https://x.com/job/1")
    b = _mk("p2:2", jd_text="bbbbbbbbbbbbb", url="https://www.x.com/job/1/")
    out, stats = dedupe([a, b])
    assert len(out) == 1
    assert stats.dropped_url_collision == 1


def test_dedupe_preserves_unique_records():
    a = _mk("p:1", url="https://x.com/1")
    b = _mk("p:2", url="https://x.com/2")
    out, _ = dedupe([a, b])
    assert {j.job_id for j in out} == {"p:1", "p:2"}


def test_dedupe_collapses_same_company_same_jd_amazon_pattern():
    """Amazon AWS publishes the SAME JD body under different jobIds, with no
    public URL. PK+URL dedupe doesn't catch them. Content-key does."""
    body = (
        "Amazon strives to be Earth's most customer-centric company. "
        "We are seeking a passionate intern to join the AWS Marketing team. "
        "Responsibilities include market research, campaign analytics, and "
        "supporting senior marketers across multiple verticals. The role is "
        "ideal for students pursuing a marketing or business degree."
    )
    a = _mk("amazon:101", jd_text=body, url="", company="Amazon / AWS")
    b = _mk("amazon:202", jd_text=body, url="", company="Amazon / AWS")
    out, stats = dedupe([a, b])
    assert len(out) == 1
    assert stats.dropped_content_collision == 1


def test_dedupe_does_not_collapse_same_jd_across_unrelated_companies():
    """Two distinct companies with templated identical JDs (e.g. mock data)
    must NOT merge — content key is namespaced by company."""
    body = "负责公司核心产品的开发和维护；与产品、设计团队紧密合作；编写高质量代码。" * 3
    a = _mk("liepin:1", jd_text=body, company="阿里巴巴")
    b = _mk("liepin:2", jd_text=body, company="美团")
    out, stats = dedupe([a, b])
    assert len(out) == 2
    assert stats.dropped_content_collision == 0


def test_dedupe_skips_content_key_for_short_jd():
    """Below the min-length threshold we don't trust the content fingerprint."""
    a = _mk("p:1", jd_text="too short", company="A")
    b = _mk("p:2", jd_text="too short", company="A")
    out, stats = dedupe([a, b])
    assert len(out) == 2
    assert stats.dropped_content_collision == 0


# ---------------------------------------------------------------------------
# schema sanity
# ---------------------------------------------------------------------------

def test_make_job_id_lowercases_platform():
    assert make_job_id("YingJieSheng", "abc") == "yingjiesheng:abc"


def test_job_parquet_dict_serializes_enums():
    j = _mk("p:1")
    d = j.parquet_dict()
    assert isinstance(d["job_type"], str)
    assert isinstance(d["seniority"], str)
    assert isinstance(d["salary_unit"], str)
