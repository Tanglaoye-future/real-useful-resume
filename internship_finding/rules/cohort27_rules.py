import re
from typing import Any, Dict, List


RULE_VERSION = "v1.0_20260316"


def _norm(x: Any) -> str:
    if x is None:
        return ""
    return re.sub(r"\s+", " ", str(x)).strip()


def _contains_any(text: str, words: List[str]) -> bool:
    return any(w in text for w in words)


def classify_27_cohort(signals: Dict[str, Any]) -> Dict[str, Any]:
    text = _norm(
        f"{signals.get('title', '')} {signals.get('jd_raw', '')} {signals.get('year_text', '')} "
        f"{signals.get('project_name', '')} {signals.get('recruit_type', '')} {signals.get('source', '')}"
    )
    crawl_time = _norm(signals.get("collect_time", ""))
    source = _norm(signals.get("source", "")).lower()
    triggered_rules: List[str] = []
    confidence = "none"
    score = 0

    if _contains_any(text, ["2027届", "2027 校园招聘", "2027届秋季校园招聘", "2027毕业生", "2027年毕业", "2027应届生", "2027 应届生"]):
        triggered_rules.append("RULE_HIGH_TEXT_2027")
    if re.search(r"2027.{0,6}(实习生|实习|应届生|校招)", text):
        triggered_rules.append("RULE_HIGH_2027_PROJECT")
    if re.search(r"2026[./年\s]*0?9.*2027[./年\s]*0?8", text):
        triggered_rules.append("RULE_HIGH_RANGE_2026_09_2027_08")
    if source.startswith("official_bytedance") and _contains_any(text, ["campus", "校招", "实习"]):
        if _contains_any(text, ["2027", "27届"]):
            triggered_rules.append("RULE_HIGH_BYTEDANCE_DIRECT")

    if _contains_any(text, ["2026暑期实习", "summer intern"]) and _contains_any(text, ["留用", "转正", "return offer"]):
        triggered_rules.append("RULE_MED_SUMMER_RETURN")
    if _contains_any(text, ["2026暑期实习", "summer intern"]) and _contains_any(text, ["数据", "算法", "开发", "工程", "分析", "技术"]):
        triggered_rules.append("RULE_MED_SUMMER_TECH")
    if _contains_any(text, ["应届", "校园", "校招"]) and crawl_time.startswith(("2026-07", "2026-08", "2026-09", "2026-10", "2026-11", "2026-12")):
        triggered_rules.append("RULE_MED_FRESHMAN_TIMING")
    if _contains_any(text, ["应届", "校园", "校招"]) and source.startswith("official_"):
        triggered_rules.append("RULE_LOW_OFFICIAL_FRESH")

    if any(x.startswith("RULE_HIGH") for x in triggered_rules):
        confidence = "high"
        score = 90
    elif any(x.startswith("RULE_MED") for x in triggered_rules):
        confidence = "medium"
        score = 70
    elif any(x.startswith("RULE_LOW") for x in triggered_rules):
        confidence = "low"
        score = 50

    reason = ";".join(triggered_rules)
    return {
        "cohort27_confidence": confidence,
        "cohort27_reason": reason,
        "cohort27_score": score,
        "rule_version": RULE_VERSION,
        "triggered_rules": triggered_rules,
    }
