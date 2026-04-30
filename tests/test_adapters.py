"""
Crawler-layer regression tests for the new adapter architecture.

Tests cover:
1.  ShixisengAdapter.parse_list_card() — against a minimal HTML fixture
2.  ShixisengAdapter.filter_row()      — city and grad-only filters
3.  LiepinAdapter._parse_job_card()   — both flat and nested API shapes
4.  RpcCrawler checkpoint read/write   — round-trip correctness
5.  rpc_crawler.normalize()            — SCHEMA completeness guarantee
6.  ShixisengAdapter.parse_detail()    — HTML fragment with JD + pub date
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Make project root importable
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# 1. ShixisengAdapter.parse_list_card()
# ---------------------------------------------------------------------------

SHIXISENG_LIST_HTML = """
<div class="intern-wrap">
  <div class="intern-detail__company">
    <a title="测试科技">测试科技</a>
  </div>
  <a class="intern-detail__title" href="/intern/inn_test123?pcm=pc_SearchList">
    <span class="intern-detail__job">算法实习生</span>
  </a>
  <span class="day_money">120元/天</span>
  <span class="city">上海</span>
</div>
"""


def test_shixiseng_parse_list_card_basic():
    from bs4 import BeautifulSoup
    from crawlers.adapters.shixiseng import ShixisengAdapter

    adapter = ShixisengAdapter()
    soup = BeautifulSoup(SHIXISENG_LIST_HTML, "html.parser")
    card = soup.select_one(".intern-wrap")
    result = adapter.parse_list_card(card)

    assert result["company_name"] == "测试科技"
    assert result["job_title"] == "算法实习生"
    assert result["salary_range"] == "120元/天"
    assert result["location"] == "上海"
    assert result["url"] == "https://www.shixiseng.com/intern/inn_test123?pcm=pc_SearchList"


def test_shixiseng_parse_list_card_returns_all_keys():
    from bs4 import BeautifulSoup
    from crawlers.adapters.shixiseng import ShixisengAdapter

    adapter = ShixisengAdapter()
    soup = BeautifulSoup(SHIXISENG_LIST_HTML, "html.parser")
    card = soup.select_one(".intern-wrap")
    result = adapter.parse_list_card(card)

    for key in ("company_name", "job_title", "salary_range", "location", "url"):
        assert key in result, f"Missing key: {key}"


# ---------------------------------------------------------------------------
# 2. ShixisengAdapter.filter_row()
# ---------------------------------------------------------------------------

def test_shixiseng_filter_row_keeps_shanghai():
    from crawlers.adapters.shixiseng import ShixisengAdapter
    adapter = ShixisengAdapter(city="上海")
    row = {"location": "上海-浦东新区", "requirements": "本科及以上"}
    assert adapter.filter_row(row) is True


def test_shixiseng_filter_row_drops_non_shanghai():
    from crawlers.adapters.shixiseng import ShixisengAdapter
    adapter = ShixisengAdapter(city="上海")
    row = {"location": "北京-朝阳区", "requirements": ""}
    assert adapter.filter_row(row) is False


def test_shixiseng_filter_row_drops_graduate_only():
    from crawlers.adapters.shixiseng import ShixisengAdapter
    adapter = ShixisengAdapter(city="上海", require_undergrad=True)
    row = {"location": "上海", "requirements": "仅硕士以上学历"}
    assert adapter.filter_row(row) is False


def test_shixiseng_filter_row_keeps_normal_grad_req():
    from crawlers.adapters.shixiseng import ShixisengAdapter
    adapter = ShixisengAdapter(city="上海", require_undergrad=True)
    row = {"location": "上海", "requirements": "本科在读，大三大四均可"}
    assert adapter.filter_row(row) is True


# ---------------------------------------------------------------------------
# 3. LiepinAdapter._parse_job_card() — flat and nested shapes
# ---------------------------------------------------------------------------

def test_liepin_parse_flat_card():
    from crawlers.adapters.liepin import _parse_job_card

    flat = {
        "jobId": "12345",
        "jobName": "数据分析实习",
        "compName": "ABC科技",
        "dq": "上海",
        "salary": "200元/天",
        "industryName": "互联网",
        "publishTime": "2026-04-01",
    }
    result = _parse_job_card(flat, "数据")

    assert result is not None
    assert result["source_job_id"] == "12345"
    assert result["job_name"] == "数据分析实习"
    assert result["company_name"] == "ABC科技"
    assert result["location"] == "上海"
    assert result["salary"] == "200元/天"
    assert result["source_keyword"] == "数据"
    assert "liepin.com/job/12345" in result["url"]


def test_liepin_parse_nested_card():
    from crawlers.adapters.liepin import _parse_job_card

    nested = {
        "job": {
            "jobId": "99999",
            "title": "产品实习生",
            "salary": "面议",
            "dq": "上海-徐汇区",
            "link": "https://www.liepin.com/job/99999.shtml",
        },
        "comp": {
            "compName": "XYZ集团",
            "compIndustry": "快消",
            "compScale": "10000人以上",
        },
    }
    result = _parse_job_card(nested, "产品")

    assert result is not None
    assert result["source_job_id"] == "99999"
    assert result["job_name"] == "产品实习生"
    assert result["company_name"] == "XYZ集团"
    assert result["company_industry"] == "快消"
    assert result["url"] == "https://www.liepin.com/job/99999.shtml"


def test_liepin_parse_card_missing_id_returns_none():
    from crawlers.adapters.liepin import _parse_job_card
    assert _parse_job_card({"jobName": "orphan"}, "") is None
    assert _parse_job_card({"job": {"title": "nested_orphan"}, "comp": {}}, "") is None


# ---------------------------------------------------------------------------
# 4. RpcCrawler checkpoint round-trip
# ---------------------------------------------------------------------------

def test_rpc_crawler_checkpoint_roundtrip():
    from crawlers.base.rpc_crawler import load_checkpoint, save_checkpoint

    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = os.path.join(tmpdir, "test_ckpt.json")
        data = {"keyword_idx": 7, "seen_ids": ["a1", "b2", "c3"]}
        save_checkpoint(ckpt_path, data)

        loaded = load_checkpoint(ckpt_path)
        assert loaded["keyword_idx"] == 7
        assert set(loaded["seen_ids"]) == {"a1", "b2", "c3"}


def test_rpc_crawler_checkpoint_absent():
    from crawlers.base.rpc_crawler import load_checkpoint
    result = load_checkpoint("/nonexistent/path/ckpt.json")
    assert result == {}


def test_rpc_crawler_checkpoint_corrupt():
    from crawlers.base.rpc_crawler import load_checkpoint
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("not json {{{")
        tmp = f.name
    try:
        result = load_checkpoint(tmp)
        assert result == {}
    finally:
        os.unlink(tmp)


# ---------------------------------------------------------------------------
# 5. rpc_crawler.normalize() — SCHEMA completeness
# ---------------------------------------------------------------------------

def test_rpc_crawler_normalize_all_schema_keys():
    from crawlers.base.rpc_crawler import normalize, SCHEMA

    raw = {
        "source_job_id": "X1",
        "job_name": "测试岗位",
        "company_name": "测试公司",
        "url": "https://example.com/job/X1",
        "location": "上海",
    }
    row = normalize(raw, "test_site")

    for key in SCHEMA:
        assert key in row, f"SCHEMA key missing from normalized row: {key}"
    assert row["platform"] == "test_site"
    assert row["source_job_id"] == "X1"
    assert row["crawled_at"]  # not empty


def test_rpc_crawler_normalize_fills_missing_with_empty():
    from crawlers.base.rpc_crawler import normalize, SCHEMA

    row = normalize({}, "site")
    for key in SCHEMA:
        assert key in row


# ---------------------------------------------------------------------------
# 6. ShixisengAdapter.parse_detail() — JD content + publish date
# ---------------------------------------------------------------------------

DETAIL_HTML = """
<html><body>
  <div class="job_detail">
    <h3>岗位职责</h3>
    <p>负责数据分析工作</p>
    <p>任职要求</p>
    <p>统计学相关专业在读</p>
  </div>
  <span class="job-header__time">发布时间：2026-04-15</span>
</body></html>
"""


def test_shixiseng_parse_detail_extracts_jd():
    from bs4 import BeautifulSoup
    from crawlers.adapters.shixiseng import ShixisengAdapter

    adapter = ShixisengAdapter()
    soup = BeautifulSoup(DETAIL_HTML, "html.parser")
    result = adapter.parse_detail(soup)

    assert "responsibilities" in result or "requirements" in result, (
        "Expected at least one of responsibilities/requirements"
    )


def test_shixiseng_parse_detail_extracts_date():
    from bs4 import BeautifulSoup
    from crawlers.adapters.shixiseng import ShixisengAdapter

    adapter = ShixisengAdapter()
    soup = BeautifulSoup(DETAIL_HTML, "html.parser")
    result = adapter.parse_detail(soup)

    assert result.get("publish_time") == "2026-04-15"


# ---------------------------------------------------------------------------
# 7. LiepinAdapter._clean_jd() — strips boilerplate
# ---------------------------------------------------------------------------

def test_clean_jd_strips_boilerplate():
    from crawlers.adapters.liepin import _clean_jd

    raw = "负责后端开发\n使用Python和Go\n猎聘-中高端职业发展平台\n下载App"
    cleaned = _clean_jd(raw)

    assert "后端开发" in cleaned
    assert "猎聘" not in cleaned
    assert "下载App" not in cleaned


def test_clean_jd_handles_empty():
    from crawlers.adapters.liepin import _clean_jd
    assert _clean_jd("") == ""
    assert _clean_jd(None) == ""


def test_clean_jd_extracts_from_html():
    from crawlers.adapters.liepin import _clean_jd

    html = """
    <html><body>
      <div class="job-detail-content">负责前端开发，React技能。</div>
      <script>var x=1;</script>
    </body></html>
    """
    cleaned = _clean_jd(html)
    assert "前端开发" in cleaned


# ---------------------------------------------------------------------------
# 8. YingjieshengAdapter — list anchors, detail prefix+sections, filter
# ---------------------------------------------------------------------------

YINGJIESHENG_LIST_HTML = """
<html><body>
  <ul>
    <li><a href="/job-007-958-717.html">[上海]上海募艺文化传播有限公司</a></li>
    <li><a href="https://www.yingjiesheng.com/job-007-958-718.html">[上海]校拓主管</a></li>
    <li><a href="/about/contact.html">联系我们</a></li>
    <li><a href="/shanghai-morejob-2.html">下一页</a></li>
  </ul>
</body></html>
"""


def test_yingjiesheng_parse_list_card_picks_job_links():
    from bs4 import BeautifulSoup
    from crawlers.adapters.yingjiesheng import YingjieshengAdapter

    adapter = YingjieshengAdapter()
    soup = BeautifulSoup(YINGJIESHENG_LIST_HTML, "html.parser")

    parsed = [adapter.parse_list_card(a) for a in soup.select("a[href]")]
    job_cards = [p for p in parsed if p]

    assert len(job_cards) == 2
    ids = {c["source_job_id"] for c in job_cards}
    assert ids == {"job-007-958-717", "job-007-958-718"}
    assert all(c["url"].startswith("https://www.yingjiesheng.com/") for c in job_cards)


def test_yingjiesheng_parse_list_card_rejects_non_job_link():
    from bs4 import BeautifulSoup
    from crawlers.adapters.yingjiesheng import YingjieshengAdapter

    adapter = YingjieshengAdapter()
    soup = BeautifulSoup('<a href="/about/contact.html">联系我们</a>', "html.parser")
    assert adapter.parse_list_card(soup.select_one("a")) is None


YINGJIESHENG_DETAIL_HTML = """
<html><body>
  <h1>市场BD</h1>
  <div class="job-detail-content">
市场BD
招聘单位：上海募艺文化传播有限公司
职位类别：市场/营销/拓展专员
学历要求：本科及以上
工作地点：上海市
薪资待遇：5k-8k
发布日期：2026-04-25
专业要求：市场营销,工商管理
岗位职责
1.异业合作与渠道统筹
2.方案优化与全域关系维护
任职要求
1.具备市场推广经验
2.善于沟通
福利待遇
节日福利、带薪休假
联系方式
联系电话：18917272220
公司地址：上海市普陀区
  </div>
</body></html>
"""


def test_yingjiesheng_parse_detail_extracts_prefix():
    from bs4 import BeautifulSoup
    from crawlers.adapters.yingjiesheng import YingjieshengAdapter

    adapter = YingjieshengAdapter()
    soup = BeautifulSoup(YINGJIESHENG_DETAIL_HTML, "html.parser")
    result = adapter.parse_detail(soup)

    assert result.get("job_name") == "市场BD"
    assert result.get("company_name") == "上海募艺文化传播有限公司"
    assert result.get("education_requirement") == "本科及以上"
    assert result.get("location") == "上海市"
    assert result.get("salary") == "5k-8k"
    assert result.get("publish_date") == "2026-04-25"


def test_yingjiesheng_parse_detail_splits_sections():
    from bs4 import BeautifulSoup
    from crawlers.adapters.yingjiesheng import YingjieshengAdapter

    adapter = YingjieshengAdapter()
    soup = BeautifulSoup(YINGJIESHENG_DETAIL_HTML, "html.parser")
    result = adapter.parse_detail(soup)

    assert "异业合作" in result.get("job_description", "")
    assert "市场推广" in result.get("job_requirement", "")
    assert "节日福利" in result.get("benefits", "")
    # Boilerplate must be stripped from jd_content
    assert "18917272220" not in result.get("jd_content", "")


def test_yingjiesheng_filter_row_keeps_shanghai():
    from crawlers.adapters.yingjiesheng import YingjieshengAdapter
    adapter = YingjieshengAdapter()
    assert adapter.filter_row({"location": "上海-浦东", "city": ""}) is True
    assert adapter.filter_row({"location": "", "city": "上海"}) is True


def test_yingjiesheng_filter_row_drops_non_shanghai():
    from crawlers.adapters.yingjiesheng import YingjieshengAdapter
    adapter = YingjieshengAdapter()
    assert adapter.filter_row({"location": "北京-朝阳", "city": "北京"}) is False


def test_yingjiesheng_list_card_to_rpc_schema():
    from crawlers.adapters.yingjiesheng import YingjieshengAdapter
    adapter = YingjieshengAdapter()
    card = {
        "job_name":      "[上海]募艺文化",
        "company_name":  "募艺文化",
        "url":           "https://www.yingjiesheng.com/job-007-958-717.html",
        "source_job_id": "job-007-958-717",
        "location":      "上海",
    }
    rpc = adapter._list_card_to_rpc(card, "应届生")
    assert rpc is not None
    assert rpc["source_job_id"] == "job-007-958-717"
    assert rpc["job_name"] == "[上海]募艺文化"
    assert rpc["city"] == "上海"
    assert rpc["source_keyword"] == "应届生"
