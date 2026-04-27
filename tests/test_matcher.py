"""Stage 2 unit tests: hard filter, scoring components, resume loader, render.

These tests don't load the bge model — semantic similarity is tested with
synthetic vectors so the suite stays fast (< 2s) and offline.
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import pytest

from matcher import resume_loader, score, render


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

def _meta_df() -> pd.DataFrame:
    return pd.DataFrame([
        {"job_id": "a1", "platform": "yj", "title": "数据分析师",
         "company": "字节", "city": "上海", "job_type": "fulltime",
         "seniority": "junior", "salary_raw": "20-30k",
         "url": "https://e/1",
         "jd_text": "负责用 Python 和 SQL 处理日志数据，搭建数据看板。" * 10},
        {"job_id": "a2", "platform": "ss", "title": "电话销售",
         "company": "X 公司", "city": "上海", "job_type": "fulltime",
         "seniority": "junior", "salary_raw": "5-8k", "url": "https://e/2",
         "jd_text": "电话销售岗位，负责拓客户。"},
        {"job_id": "a3", "platform": "ss", "title": "Algorithm Engineer",
         "company": "Y", "city": "北京", "job_type": "fulltime",
         "seniority": "senior", "salary_raw": "", "url": "https://e/3",
         "jd_text": "Build ML models with PyTorch and Python." * 5},
        {"job_id": "a4", "platform": "yj", "title": "数据科学家实习生",
         "company": "Z", "city": "上海", "job_type": "internship",
         "seniority": "intern", "salary_raw": "300/d", "url": "https://e/4",
         "jd_text": "用 Python 和机器学习处理用户数据。" * 8},
    ])


def _prefs() -> dict:
    return {
        "filters": {
            "target_cities": ["上海"],
            "target_job_types": ["fulltime", "internship"],
            "exclude_keywords": ["销售"],
            "min_jd_chars": 50,
        },
        "scoring": {
            "weights": {"semantic": 0.6, "keyword": 0.2, "title": 0.1,
                        "location": 0.05, "job_type": 0.05},
            "target_titles": ["数据分析", "数据科学"],
            "must_have_keywords": ["Python"],
            "nice_to_have_keywords": ["机器学习", "PyTorch"],
        },
        "output": {"top_n": 5, "formats": ["csv", "markdown", "html"]},
    }


# ---------------------------------------------------------------------------
# hard filter
# ---------------------------------------------------------------------------

def test_apply_filters_drops_wrong_city():
    df, stats = score.apply_filters(_meta_df(), _prefs())
    assert "a3" not in df["job_id"].tolist()
    assert stats["dropped_city"] >= 1


def test_apply_filters_drops_excluded_keyword():
    df, _ = score.apply_filters(_meta_df(), _prefs())
    assert "a2" not in df["job_id"].tolist()


def test_apply_filters_keeps_valid_rows():
    df, _ = score.apply_filters(_meta_df(), _prefs())
    assert {"a1", "a4"}.issubset(set(df["job_id"].tolist()))


def test_apply_filters_min_jd_chars():
    p = _prefs()
    p["filters"]["min_jd_chars"] = 5000
    df, _ = score.apply_filters(_meta_df(), p)
    assert len(df) == 0


def test_apply_filters_no_constraints_keeps_all():
    df, _ = score.apply_filters(_meta_df(), {"filters": {}})
    assert len(df) == 4


# ---------------------------------------------------------------------------
# scoring components
# ---------------------------------------------------------------------------

def test_keyword_score_must_and_nice():
    df = _meta_df()
    s = score.keyword_score(df, _prefs())
    assert s.shape == (4,)
    assert s[0] > 0  # mentions Python and 机器学习
    assert s[2] > 0  # mentions Python and PyTorch
    assert 0 <= s.min() and s.max() <= 1


def test_keyword_score_no_keywords_returns_zero():
    df = _meta_df()
    s = score.keyword_score(df, {"scoring": {}})
    assert (s == 0).all()


def test_title_score_hits_target_titles():
    s = score.title_score(_meta_df(), _prefs())
    assert s[0] == 1.0
    assert s[3] == 1.0
    assert s[2] == 0.0


def test_title_score_short_ascii_keyword_uses_word_boundary():
    """'AI' must not match 'Associate' or 'trainee' (real bug we hit)."""
    df = pd.DataFrame([
        {"job_id": "x1", "title": "Associate Cloud Consultant",
         "company": "Amzn", "city": "上海", "job_type": "fulltime",
         "jd_text": "x" * 200},
        {"job_id": "x2", "title": "AI Researcher",
         "company": "Lab", "city": "上海", "job_type": "fulltime",
         "jd_text": "x" * 200},
        {"job_id": "x3", "title": "Marketing Trainee",
         "company": "Co", "city": "上海", "job_type": "fulltime",
         "jd_text": "x" * 200},
    ])
    p = {"scoring": {"target_titles": ["AI"]}}
    s = score.title_score(df, p)
    assert s.tolist() == [0.0, 1.0, 0.0]


def test_keyword_score_short_ascii_uses_word_boundary():
    """Keyword 'R' must not match 'Researcher' or 'Python'."""
    df = pd.DataFrame([
        {"job_id": "k1", "title": "Researcher",
         "company": "X", "city": "上海", "job_type": "fulltime",
         "jd_text": "uses Python and Pandas"},
        {"job_id": "k2", "title": "Data Analyst",
         "company": "Y", "city": "上海", "job_type": "fulltime",
         "jd_text": "uses R and SAS"},
    ])
    p = {"scoring": {"must_have_keywords": ["R"]}}
    s = score.keyword_score(df, p)
    assert s[0] == 0.0
    assert s[1] == 1.0


def test_exclude_keyword_short_ascii_uses_word_boundary():
    df = pd.DataFrame([
        {"job_id": "e1", "title": "AI Engineer", "company": "X",
         "city": "上海", "job_type": "fulltime", "jd_text": "x" * 300},
        {"job_id": "e2", "title": "Associate Consultant", "company": "Y",
         "city": "上海", "job_type": "fulltime", "jd_text": "x" * 300},
    ])
    prefs = {"filters": {"exclude_keywords": ["AI"], "min_jd_chars": 0}}
    out, _ = score.apply_filters(df, prefs)
    assert "e1" not in out["job_id"].tolist()
    assert "e2" in out["job_id"].tolist()


def test_location_score_target_cities():
    s = score.location_score(_meta_df(), _prefs())
    assert s.tolist() == [1.0, 1.0, 0.0, 1.0]


def test_job_type_score():
    s = score.job_type_score(_meta_df(), _prefs())
    assert s.tolist() == [1.0, 1.0, 1.0, 1.0]
    p = _prefs()
    p["filters"]["target_job_types"] = ["internship"]
    s2 = score.job_type_score(_meta_df(), p)
    assert s2.tolist() == [0.0, 0.0, 0.0, 1.0]


def test_semantic_similarity_with_synthetic_vectors():
    rng = np.random.default_rng(0)
    resume = rng.normal(size=8).astype("float32")
    resume /= np.linalg.norm(resume)
    perfect = resume.copy()
    opposite = -resume
    middle = np.zeros(8, dtype="float32"); middle[0] = 1.0
    if abs(np.dot(resume, middle)) > 0.99:
        middle[0] = 0; middle[1] = 1.0
    vecs = np.stack([perfect, opposite, middle / np.linalg.norm(middle)])
    s = score.semantic_similarity(resume, vecs)
    assert s[0] > 0.99
    assert s[1] < 0.01
    assert 0 <= s[2] <= 1


def test_normalized_weights_sum_to_one():
    w = score.normalized_weights({"scoring": {"weights":
        {"semantic": 6, "keyword": 2, "title": 1, "location": 0.5, "job_type": 0.5}}})
    assert abs(sum(w.values()) - 1.0) < 1e-6


def test_normalized_weights_fallback_on_zero():
    w = score.normalized_weights({"scoring": {"weights":
        {"semantic": 0, "keyword": 0, "title": 0, "location": 0, "job_type": 0}}})
    assert abs(sum(w.values()) - 1.0) < 1e-6


def test_final_score_alignment():
    df, _ = score.apply_filters(_meta_df(), _prefs())
    rng = np.random.default_rng(0)
    vecs = rng.normal(size=(len(df), 8)).astype("float32")
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
    resume = rng.normal(size=8).astype("float32")
    resume /= np.linalg.norm(resume)
    finals, comp = score.final_score(df, vecs, resume, _prefs())
    assert finals.shape == (len(df),)
    assert 0 <= finals.min() and finals.max() <= 1
    for k in ("semantic", "keyword", "title", "location", "job_type"):
        assert comp[k].shape == (len(df),)


def test_final_score_misalignment_raises():
    df, _ = score.apply_filters(_meta_df(), _prefs())
    bad_vecs = np.zeros((len(df) + 1, 8), dtype="float32")
    with pytest.raises(ValueError):
        score.final_score(df, bad_vecs, np.zeros(8, dtype="float32"), _prefs())


# ---------------------------------------------------------------------------
# big-tech soft-deprioritization
# ---------------------------------------------------------------------------

def test_is_big_tech_substring_matches_alias():
    df = pd.DataFrame([
        {"company": "字节跳动"},
        {"company": "腾讯科技 (上海) 有限公司"},
        {"company": "上海某中小企"},
        {"company": ""},
    ])
    p = {"scoring": {"big_tech_companies": ["字节跳动", "腾讯"]}}
    flags = score.is_big_tech(df, p)
    assert flags.tolist() == [True, True, False, False]


def test_is_big_tech_empty_alias_list_marks_none():
    df = pd.DataFrame([{"company": "字节跳动"}, {"company": "腾讯"}])
    flags = score.is_big_tech(df, {"scoring": {}})
    assert flags.tolist() == [False, False]


def test_final_score_applies_penalty_to_big_tech_only():
    """When big_tech_penalty < 1, only rows whose company matches an alias
    have their final score multiplied. Other rows are unchanged."""
    df, _ = score.apply_filters(_meta_df(), _prefs())  # keeps a1, a4
    # a1 company='字节', a4 company='Z'
    rng = np.random.default_rng(7)
    vecs = rng.normal(size=(len(df), 8)).astype("float32")
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
    resume = rng.normal(size=8).astype("float32")
    resume /= np.linalg.norm(resume)

    p = _prefs()
    p["scoring"]["big_tech_companies"] = ["字节"]
    p["scoring"]["big_tech_penalty"] = 0.3

    finals, comp = score.final_score(df, vecs, resume, p)
    base = comp["base"]
    flag = comp["is_big_tech"]
    assert flag.tolist() == [True, False]  # a1 is big tech, a4 isn't
    np.testing.assert_allclose(finals[flag], base[flag] * 0.3, rtol=1e-5)
    np.testing.assert_allclose(finals[~flag], base[~flag], rtol=1e-5)
    assert comp["big_tech_penalty"] == 0.3


def test_final_score_penalty_one_is_no_op():
    df, _ = score.apply_filters(_meta_df(), _prefs())
    rng = np.random.default_rng(1)
    vecs = rng.normal(size=(len(df), 8)).astype("float32")
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
    resume = rng.normal(size=8).astype("float32")
    resume /= np.linalg.norm(resume)
    p = _prefs()
    p["scoring"]["big_tech_companies"] = ["字节"]
    p["scoring"]["big_tech_penalty"] = 1.0
    finals, comp = score.final_score(df, vecs, resume, p)
    np.testing.assert_allclose(finals, comp["base"], rtol=1e-6)


def test_short_jd_big_tech_passes_filter_then_gets_penalty():
    """Regression: liepin 列表页 JD 通常 80~150 字符。如果 hard filter
    把它们刷掉，penalty 就没机会作用，相当于对短 JD 大厂"硬过滤"。

    这条测试钉住的契约：当 min_jd_chars <= 实际 JD 长度时，大厂行必须能进
    池子，并最终被 penalty 推下去（而不是 base 排名）。"""
    df = pd.DataFrame([
        # ~120 字符 — 模拟 liepin "腾讯科技 · 嵌入式开发" 真实数据形态
        # （列表页 JD 通常 100~150 字符；早于现实的 200 阈值就会被刷掉）
        {"job_id": "lp1", "platform": "liepin", "title": "嵌入式开发",
         "company": "腾讯科技", "city": "上海", "job_type": "campus",
         "seniority": "intern", "salary_raw": "300/d",
         "url": "https://liepin/1",
         "jd_text": "负责嵌入式系统开发；与硬件团队协作完成驱动调试；"
                    "编写高质量代码；参与产品验证与上线。\n\n"
                    "计算机相关专业本科及以上；C/C++ 基础扎实；"
                    "有 Linux 内核或驱动开发经验者优先；良好的沟通能力"},
        # 普通中小企长 JD
        {"job_id": "lp2", "platform": "liepin", "title": "数据分析实习",
         "company": "上海某中小企", "city": "上海", "job_type": "internship",
         "seniority": "intern", "salary_raw": "200/d",
         "url": "https://liepin/2",
         "jd_text": "用 Python 和 SQL 处理用户行为数据，搭建看板。" * 8},
    ])
    p = {
        "filters": {
            "target_cities": ["上海"],
            "target_job_types": ["campus", "internship"],
            # 用 80 而不是 100，确保该测试钉住的契约不依赖 fixture 的精确长度。
            # 现实 prod 值 = 100；只要 prod 值 ≤ 96（fixture 长度），契约就成立。
            "min_jd_chars": 80,
        },
        "scoring": {
            "weights": {"semantic": 0.6, "keyword": 0.2, "title": 0.1,
                        "location": 0.05, "job_type": 0.05},
            "big_tech_companies": ["腾讯"],
            "big_tech_penalty": 0.3,
        },
    }
    kept, _ = score.apply_filters(df, p)
    assert "lp1" in kept["job_id"].tolist(), \
        "短 JD 大厂被 hard filter 刷掉了 — penalty 失去作用空间"

    rng = np.random.default_rng(42)
    vecs = rng.normal(size=(len(kept), 8)).astype("float32")
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
    resume = vecs[0].copy()  # 让大厂行的 semantic 接近满分

    finals, comp = score.final_score(kept, vecs, resume, p)
    flags = comp["is_big_tech"]
    base = comp["base"]
    assert flags.tolist() == [True, False]
    assert finals[0] == pytest.approx(base[0] * 0.3, rel=1e-5)
    assert finals[0] < base[0], "penalty 应当让大厂 final < base"


def test_final_score_penalty_clamped_to_unit_range():
    df, _ = score.apply_filters(_meta_df(), _prefs())
    rng = np.random.default_rng(2)
    vecs = rng.normal(size=(len(df), 8)).astype("float32")
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
    resume = rng.normal(size=8).astype("float32")
    resume /= np.linalg.norm(resume)
    p = _prefs()
    p["scoring"]["big_tech_companies"] = ["字节"]
    p["scoring"]["big_tech_penalty"] = -0.5  # nonsense -> clamped to 0
    finals, comp = score.final_score(df, vecs, resume, p)
    flag = comp["is_big_tech"]
    np.testing.assert_allclose(finals[flag], 0.0, atol=1e-6)
    np.testing.assert_allclose(finals[~flag], comp["base"][~flag], rtol=1e-6)


# ---------------------------------------------------------------------------
# resume loader
# ---------------------------------------------------------------------------

def test_resume_loader_markdown(tmp_path: Path):
    p = tmp_path / "r.md"
    p.write_text("# Me\n\nI know Python and SQL." * 5, encoding="utf-8")
    text = resume_loader.load_resume(p, min_chars=10)
    assert "Python" in text
    assert "<" not in text


def test_resume_loader_too_short(tmp_path: Path):
    p = tmp_path / "r.md"
    p.write_text("hi", encoding="utf-8")
    with pytest.raises(resume_loader.ResumeLoadError):
        resume_loader.load_resume(p, min_chars=50)


def test_resume_loader_unsupported(tmp_path: Path):
    p = tmp_path / "r.xyz"
    p.write_text("foo", encoding="utf-8")
    with pytest.raises(resume_loader.ResumeLoadError):
        resume_loader.load_resume(p)


def test_resume_loader_strips_html(tmp_path: Path):
    p = tmp_path / "r.md"
    p.write_text("<p>hello <b>world</b></p>" * 10, encoding="utf-8")
    text = resume_loader.load_resume(p, min_chars=10)
    assert "<" not in text
    assert "hello" in text


# ---------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------

def _scored_df() -> pd.DataFrame:
    df = _meta_df().head(2).copy()
    df["semantic"] = [0.8, 0.4]
    df["keyword"] = [0.7, 0.3]
    df["title_score"] = [1.0, 0.0]
    df["location_score"] = [1.0, 1.0]
    df["job_type_score"] = [1.0, 1.0]
    df["final"] = [0.85, 0.30]
    df["jd_excerpt"] = df["jd_text"].str.slice(0, 200)
    df.insert(0, "rank", [1, 2])
    return df


def test_render_all_writes_three_files(tmp_path: Path):
    out = tmp_path / "rec"
    paths = render.render_all(_scored_df(), out, meta_info={
        "timestamp": "20260101T000000Z", "resume_path": "x.md",
        "model": "test", "total": 4, "after_filter": 2,
        "filter_stats": {"input": 4, "output": 2},
        "weights": {"semantic": 0.6, "keyword": 0.2, "title": 0.1,
                    "location": 0.05, "job_type": 0.05},
    }, formats=["csv", "markdown", "html"])
    assert len(paths) == 3
    for p in paths:
        assert p.exists() and p.stat().st_size > 0


def test_render_csv_has_rank_and_url(tmp_path: Path):
    out = tmp_path / "rec"
    render.render_all(_scored_df(), out, meta_info={"weights": {}, "filter_stats": {}},
                      formats=["csv"])
    txt = (out / "recommendations.csv").read_text(encoding="utf-8-sig")
    assert "rank" in txt
    assert "https://e/1" in txt


def test_render_markdown_has_top_picks_header(tmp_path: Path):
    out = tmp_path / "rec"
    render.render_all(_scored_df(), out, meta_info={
        "timestamp": "ts", "resume_path": "r", "model": "m",
        "total": 1, "after_filter": 1, "filter_stats": {},
        "weights": {"semantic": 1.0},
    }, formats=["markdown"])
    txt = (out / "recommendations.md").read_text(encoding="utf-8")
    assert "Top picks" in txt
    assert "数据分析师" in txt


def test_render_markdown_marks_big_tech_when_penalty_lt_one(tmp_path: Path):
    df = _scored_df()
    df["base"] = [1.0, 0.5]
    df["is_big_tech"] = [True, False]
    out = tmp_path / "rec"
    render.render_all(df, out, meta_info={
        "timestamp": "ts", "resume_path": "r", "model": "m",
        "total": 2, "after_filter": 2, "filter_stats": {},
        "weights": {"semantic": 1.0},
        "big_tech_penalty": 0.3,
        "big_tech_count_in_top": 1,
    }, formats=["markdown"])
    txt = (out / "recommendations.md").read_text(encoding="utf-8")
    assert "大厂·已软降" in txt
    assert "×0.30" in txt
    # second row has is_big_tech=False -> no soft-deprioritization tag on it
    assert txt.count("大厂·已软降") == 1


def test_render_markdown_no_big_tech_marker_when_penalty_one(tmp_path: Path):
    df = _scored_df()
    df["base"] = [1.0, 0.5]
    df["is_big_tech"] = [True, False]
    out = tmp_path / "rec"
    render.render_all(df, out, meta_info={
        "timestamp": "ts", "resume_path": "r", "model": "m",
        "total": 2, "after_filter": 2, "filter_stats": {},
        "weights": {"semantic": 1.0},
        "big_tech_penalty": 1.0,
    }, formats=["markdown"])
    txt = (out / "recommendations.md").read_text(encoding="utf-8")
    assert "大厂·已软降" not in txt


def test_render_html_escapes_html(tmp_path: Path):
    df = _scored_df()
    df.loc[df.index[0], "title"] = "<script>alert(1)</script>"
    out = tmp_path / "rec"
    render.render_all(df, out, meta_info={
        "timestamp": "ts", "resume_path": "r", "model": "m",
        "total": 1, "after_filter": 1, "filter_stats": {},
        "weights": {"semantic": 1.0},
    }, formats=["html"])
    txt = (out / "recommendations.html").read_text(encoding="utf-8")
    assert "<script>alert(1)</script>" not in txt
    assert "&lt;script&gt;" in txt
