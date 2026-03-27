from __future__ import annotations

from datetime import datetime
import re
from typing import Dict, Iterable, List, Tuple


def safe_text(v) -> str:
    if v is None:
        return ""
    return str(v).strip()

def normalize_space(s: str) -> str:
    return re.sub(r"\s+", " ", safe_text(s)).strip()

def normalize_date_text(s: str) -> str:
    t = safe_text(s)
    if not t:
        return ""
    t = t.replace("年", "-").replace("月", "-").replace("日", "")
    m = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", t)
    if m:
        y, mo, d = m.groups()
        return f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"
    m = re.search(r"(\d{1,2})[-/](\d{1,2})", t)
    if m:
        now = datetime.now()
        mo, d = m.groups()
        return f"{now.year:04d}-{int(mo):02d}-{int(d):02d}"
    return ""


LEVEL_BASE = {"S": 30, "A": 20, "B": 10, "C": 5}

RECRUIT_TYPE_BONUS = {
    "校招": 8,
    "社招": 10,
    "实习": 6,
    "暑期实习": 7,
}

SOURCE_BONUS = {
    "字节校招官网": 6,
    "牛客网": 3,
    "实习僧": 4,
    "猎聘": 5,
}


SIGNAL_KEYWORDS: List[Tuple[str, int]] = [
    ("大模型", 12),
    ("LLM", 10),
    ("AIGC", 10),
    ("算法", 10),
    ("推荐", 10),
    ("广告", 9),
    ("搜索", 9),
    ("风控", 9),
    ("安全", 8),
    ("数据科学", 10),
    ("数据平台", 8),
    ("基础架构", 9),
    ("平台", 6),
    ("分布式", 7),
    ("高并发", 7),
    ("稳定性", 6),
    ("SRE", 7),
    ("后端", 6),
    ("前端", 6),
    ("客户端", 6),
    ("测试开发", 6),
    ("DevOps", 6),
]


NEGATIVE_KEYWORDS: List[Tuple[str, int]] = [
    ("外包", -30),
    ("派遣", -20),
    ("劳务", -20),
    ("客服", -10),
    ("销售", -10),
    ("主播", -10),
]


def _contains_any(text: str, keywords: Iterable[str]) -> bool:
    t = normalize_space(text).lower()
    for k in keywords:
        if safe_text(k).lower() in t:
            return True
    return False


def _parse_date(s: str) -> datetime | None:
    d = normalize_date_text(s)
    if not d:
        return None
    try:
        return datetime.strptime(d, "%Y-%m-%d")
    except Exception:
        return None


def score_row(row: Dict[str, str]) -> Tuple[int, List[str]]:
    reasons: List[str] = []

    company_level = safe_text(row.get("company_level"))
    base = LEVEL_BASE.get(company_level, 0)
    score = base
    if base:
        reasons.append(f"梯队{company_level}+{base}")

    recruit_type = safe_text(row.get("recruit_type")) or safe_text(row.get("job_type"))
    rt = RECRUIT_TYPE_BONUS.get(recruit_type, 0)
    if rt:
        score += rt
        reasons.append(f"{recruit_type}+{rt}")

    source = safe_text(row.get("source_platform")) or safe_text(row.get("platform"))
    sb = SOURCE_BONUS.get(source, 0)
    if sb:
        score += sb
        reasons.append(f"来源{source}+{sb}")

    publish_time = safe_text(row.get("publish_time")) or safe_text(row.get("publish_date"))
    dt = _parse_date(publish_time)
    if dt:
        days = (datetime.now().date() - dt.date()).days
        if days <= 3:
            score += 10
            reasons.append("3天内发布+10")
        elif days <= 7:
            score += 6
            reasons.append("7天内发布+6")
        elif days <= 30:
            score += 2
            reasons.append("30天内发布+2")

    deadline = safe_text(row.get("deadline"))
    ddl = _parse_date(deadline)
    if ddl:
        if ddl.date() >= datetime.now().date():
            score += 6
            reasons.append("未过期+6")
        elif ddl.date() < datetime.now().date():
            score -= 30
            reasons.append("已过期-30")

    job_name = safe_text(row.get("job_name"))
    desc = safe_text(row.get("job_description")) or safe_text(row.get("jd_content"))
    req = safe_text(row.get("job_requirement"))
    tags = safe_text(row.get("job_tags")) + "\n" + safe_text(row.get("skill_tags"))
    blob = f"{job_name}\n{desc}\n{req}\n{tags}"

    for k, w in SIGNAL_KEYWORDS:
        if k and k in blob:
            score += w
            reasons.append(f"{k}+{w}")

    for k, w in NEGATIVE_KEYWORDS:
        if k and k in blob:
            score += w
            reasons.append(f"{k}{w}")

    company_nature = safe_text(row.get("company_nature"))
    if company_nature in {"外资", "合资"}:
        score += 8
        reasons.append(f"{company_nature}+8")
    elif company_nature in {"国企"}:
        score += 6
        reasons.append("国企+6")

    financing_round = safe_text(row.get("financing_round"))
    if financing_round in {"独角兽", "Pre-IPO", "已上市", "D轮"}:
        score += 8
        reasons.append(f"融资{financing_round}+8")
    elif financing_round in {"C轮", "B轮"}:
        score += 5
        reasons.append(f"融资{financing_round}+5")

    welfare_tag = safe_text(row.get("welfare_tag")) or safe_text(row.get("welfare_tags"))
    for k, v in [("落户", 6), ("期权", 5), ("六险一金", 4), ("五险一金", 2), ("年终奖", 2), ("租房补贴", 3)]:
        if k and k in welfare_tag:
            score += v
            reasons.append(f"{k}+{v}")

    if not safe_text(row.get("publish_time")):
        score -= 2
        reasons.append("缺发布时间-2")

    if (
        not safe_text(row.get("job_description"))
        and not safe_text(row.get("job_requirement"))
        and not safe_text(row.get("jd_content"))
    ):
        score -= 2
        reasons.append("缺描述/要求-2")

    if score < 0:
        score = 0
    if score > 100:
        score = 100

    return score, reasons
