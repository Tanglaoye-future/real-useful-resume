import json
import os
import re
from functools import lru_cache
from typing import Any


CITY_LIST = ["上海", "北京", "深圳", "广州", "杭州", "成都", "南京", "苏州", "武汉", "西安", "天津", "重庆", "青岛", "厦门", "大连"]


def _norm(x: Any) -> str:
    if x is None:
        return ""
    return re.sub(r"\s+", " ", str(x)).strip()


@lru_cache(maxsize=1)
def _load_mapping():
    path = os.path.join(os.path.dirname(__file__), "location_alias_city.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def normalize_city(city: Any, jd_raw: Any = "") -> str:
    city_text = _norm(city)
    mapping = _load_mapping()
    if city_text in mapping:
        return mapping[city_text]
    for key, value in mapping.items():
        if key and key in city_text:
            return value
    for c in CITY_LIST:
        if c in city_text:
            return c
    jd_text = _norm(jd_raw)
    for c in CITY_LIST:
        if c in jd_text:
            return c
    return city_text
