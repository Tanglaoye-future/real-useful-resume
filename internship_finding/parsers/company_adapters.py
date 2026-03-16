import json
import re
import time
from typing import Any, Dict, List

import requests

from parsers.base_adapter import BaseCompanyAdapter
from rules.location_normalizer import normalize_city


def _norm(x: Any) -> str:
    if x is None:
        return ""
    return " ".join(str(x).split())


class KuaishouAdapter(BaseCompanyAdapter):
    company = "快手"
    source = "official_kuaishou_api"

    list_url = "https://campus.kuaishou.cn/recruit/campus/e/api/v1/open/positions/simple"
    dict_url = "https://campus.kuaishou.cn/recruit/campus/e/api/v1/dictionary/batch?types=workLocation,positionNature,recruitSubProject"
    detail_urls = [
        "https://campus.kuaishou.cn/recruit/campus/e/api/v1/open/positions/detail",
        "https://campus.kuaishou.cn/recruit/campus/e/api/v1/open/position/detail",
    ]

    def __init__(self, page_size: int = 20, timeout: int = 20):
        self.page_size = page_size
        self.timeout = timeout
        self._nature_code = "intern"
        self._sub_project_codes: List[str] = []
        self._sub_project_name_map: Dict[str, str] = {}
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json",
            "Referer": "https://campus.kuaishou.cn/",
        }

    def set_mode(self, nature_code: str = "intern"):
        self._nature_code = _norm(nature_code) or "intern"
        return self

    def _load_sub_projects(self):
        if self._sub_project_codes:
            return self._sub_project_codes
        try:
            resp = requests.get(self.dict_url, headers=self.headers, timeout=self.timeout)
            if not resp.ok:
                self._sub_project_codes = []
                return self._sub_project_codes
            data = resp.json() or {}
            items = (data.get("result") or {}).get("recruitSubProject") or []
            codes = []
            for it in items:
                if not isinstance(it, dict):
                    continue
                code = _norm(it.get("code"))
                name = _norm(it.get("name"))
                if not code:
                    continue
                if re.search(r"(2026|2027|实习|校招|秋招|应届)", name):
                    codes.append(code)
                self._sub_project_name_map[code] = name
            self._sub_project_codes = codes
        except Exception:
            self._sub_project_codes = []
            self._sub_project_name_map = {}
        return self._sub_project_codes

    def fetch_list(self, page: int) -> List[Dict[str, Any]]:
        payload = {"pageNum": page, "pageIndex": page, "pageSize": self.page_size, "positionNatureCode": self._nature_code}
        sub_projects = self._load_sub_projects()
        if sub_projects:
            payload["recruitSubProjectCodes"] = sub_projects
        resp = requests.post(self.list_url, json=payload, headers=self.headers, timeout=self.timeout)
        if not resp.ok:
            return []
        data = resp.json() or {}
        result = data.get("result") or {}
        items = result.get("list") or result.get("positions") or result.get("records") or []
        if not isinstance(items, list):
            return []
        return items

    def _fetch_detail(self, position_id: str) -> Dict[str, Any]:
        if not position_id:
            return {}
        for url in self.detail_urls:
            for payload in [{"positionId": position_id}, {"id": position_id}]:
                try:
                    resp = requests.post(url, data=json.dumps(payload), headers=self.headers, timeout=self.timeout)
                    if not resp.ok:
                        continue
                    data = resp.json() or {}
                    detail = data.get("result") or data.get("data") or {}
                    if isinstance(detail, dict) and detail:
                        return detail
                except Exception:
                    continue
        return {}

    def parse(self, raw_item: Dict[str, Any]) -> Dict[str, str]:
        position_id = _norm(
            raw_item.get("positionId")
            or raw_item.get("id")
            or raw_item.get("postId")
        )
        detail: Dict[str, Any] = {}
        title = _norm(raw_item.get("name") or raw_item.get("title") or raw_item.get("positionName"))
        city_raw = _norm(raw_item.get("city") or raw_item.get("workLocationName"))
        if not city_raw:
            work_location_dicts = raw_item.get("workLocationDicts")
            if isinstance(work_location_dicts, list) and work_location_dicts:
                city_raw = _norm(work_location_dicts[0].get("name"))
        city = normalize_city(city_raw, "")
        desc = _norm(raw_item.get("description") or raw_item.get("positionDescription"))
        req = _norm(raw_item.get("positionDemand") or raw_item.get("requirement") or raw_item.get("qualification"))
        sub_project_code = _norm(raw_item.get("recruitSubProjectCode"))
        project_name = _norm(raw_item.get("projectName") or self._sub_project_name_map.get(sub_project_code))
        list_text = _norm(f"{title} {desc} {req} {project_name}")
        is_high_27_signal = bool(
            re.search(r"(2027|27届|2026[./年\s]*0?9.*2027[./年\s]*0?8)", list_text)
        )
        is_data_target = bool(re.search(r"(数据|分析|算法|策略|商业分析|bi)", _norm(f"{title} {desc}")))
        is_shanghai_target = "上海" in city
        force_detail = is_high_27_signal and is_data_target and is_shanghai_target
        if force_detail or (not title or not desc or not req):
            detail = self._fetch_detail(position_id)
            if not title:
                title = _norm(detail.get("name") or detail.get("title") or detail.get("positionName"))
            if not city_raw:
                city_raw = _norm(detail.get("city") or detail.get("workLocationName"))
                city = normalize_city(city_raw, "")
            detail_desc = _norm(detail.get("description"))
            detail_req = _norm(detail.get("positionDemand") or detail.get("requirement"))
            if force_detail:
                if len(detail_desc) > len(desc):
                    desc = detail_desc
                if len(detail_req) > len(req):
                    req = detail_req
            else:
                if not desc:
                    desc = detail_desc
                if not req:
                    req = detail_req
        project_name = _norm(raw_item.get("projectName") or detail.get("projectName") or self._sub_project_name_map.get(sub_project_code))
        recruit_type = _norm(raw_item.get("positionNatureCode") or raw_item.get("projectTypeName") or project_name)
        jd_raw = _norm(f"{desc} 岗位要求：{req}")
        return {
            "external_job_id": position_id,
            "title": title,
            "company": self.company,
            "location_raw": city_raw,
            "city": city,
            "jd_raw": jd_raw,
            "update_time": _norm(detail.get("updateTime") or raw_item.get("updateTime")),
            "raw_tags": _norm(project_name),
            "url": f"https://campus.kuaishou.cn/recruit/campus/e/#/position/{position_id}" if position_id else "",
            "collect_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": self.source,
            "recruit_type": recruit_type,
            "project_name": project_name,
        }

    def get_27_signal(self, parsed_item: Dict[str, str]) -> Dict[str, Any]:
        text = _norm(f"{parsed_item.get('title', '')} {parsed_item.get('jd_raw', '')} {parsed_item.get('project_name', '')}")
        return {
            "has_explicit_year": any(k in text for k in ["2027", "27届", "毕业时间"]),
            "year_text": text,
            "project_name": parsed_item.get("project_name", ""),
        }


class TencentAdapter(BaseCompanyAdapter):
    company = "腾讯"
    source = "official_tencent_api"

    def fetch_list(self, page: int) -> List[Dict[str, Any]]:
        url = "https://join.qq.com/api/v1/position/searchPosition"
        payload = {
            "projectIdList": [],
            "projectMappingIdList": [1],
            "keyword": "",
            "bgList": [],
            "workCountryType": 0,
            "workCityList": [],
            "recruitCityList": [],
            "positionFidList": [],
            "pageIndex": page,
            "pageSize": 50,
        }
        try:
            resp = requests.post(url, params={"timestamp": str(int(time.time() * 1000))}, json=payload, timeout=20).json()
            return (resp.get("data") or {}).get("positionList") or []
        except Exception:
            return []

    def parse(self, raw_item: Dict[str, Any]) -> Dict[str, str]:
        post_id = _norm(raw_item.get("postId"))
        return {
            "external_job_id": post_id,
            "title": _norm(raw_item.get("positionTitle")),
            "company": self.company,
            "location_raw": _norm(raw_item.get("workCities")),
            "city": normalize_city(raw_item.get("workCities"), ""),
            "jd_raw": "",
            "update_time": "",
            "raw_tags": _norm(raw_item.get("projectName") or raw_item.get("recruitLabelName")),
            "url": f"https://join.qq.com/post.html?query=p_1&postId={post_id}" if post_id else "",
            "collect_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": self.source,
            "recruit_type": _norm(raw_item.get("projectName") or raw_item.get("recruitLabelName")),
            "project_name": _norm(raw_item.get("projectName")),
        }

    def get_27_signal(self, parsed_item: Dict[str, str]) -> Dict[str, Any]:
        text = _norm(f"{parsed_item.get('recruit_type', '')} {parsed_item.get('jd_raw', '')}")
        return {"has_explicit_year": "2027" in text, "year_text": text, "project_name": parsed_item.get("project_name", "")}


class XiaohongshuAdapter(BaseCompanyAdapter):
    company = "小红书"
    source = "official_xiaohongshu"

    def fetch_list(self, page: int) -> List[Dict[str, Any]]:
        return []

    def parse(self, raw_item: Dict[str, Any]) -> Dict[str, str]:
        return {
            "external_job_id": _norm(raw_item.get("id")),
            "title": _norm(raw_item.get("title") or raw_item.get("positionName")),
            "company": self.company,
            "location_raw": _norm(raw_item.get("city")),
            "city": normalize_city(raw_item.get("city"), ""),
            "jd_raw": _norm(raw_item.get("description")),
            "update_time": _norm(raw_item.get("updateTime")),
            "raw_tags": _norm(raw_item.get("projectName")),
            "url": "",
            "collect_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": self.source,
            "recruit_type": _norm(raw_item.get("projectName")),
            "project_name": _norm(raw_item.get("projectName")),
        }

    def get_27_signal(self, parsed_item: Dict[str, str]) -> Dict[str, Any]:
        text = _norm(f"{parsed_item.get('project_name', '')} {parsed_item.get('jd_raw', '')}")
        return {"has_explicit_year": "2027" in text, "year_text": text, "project_name": parsed_item.get("project_name", "")}


class AlibabaAdapter(BaseCompanyAdapter):
    company = "阿里"
    source = "official_alibaba"

    def fetch_list(self, page: int) -> List[Dict[str, Any]]:
        return []

    def parse(self, raw_item: Dict[str, Any]) -> Dict[str, str]:
        return {
            "external_job_id": _norm(raw_item.get("id")),
            "title": _norm(raw_item.get("title") or raw_item.get("name")),
            "company": self.company,
            "location_raw": _norm(raw_item.get("city")),
            "city": normalize_city(raw_item.get("city"), ""),
            "jd_raw": _norm(raw_item.get("description")),
            "update_time": _norm(raw_item.get("updateTime")),
            "raw_tags": "",
            "url": "",
            "collect_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": self.source,
            "recruit_type": "",
            "project_name": "",
        }

    def get_27_signal(self, parsed_item: Dict[str, str]) -> Dict[str, Any]:
        text = _norm(parsed_item.get("jd_raw", ""))
        return {"has_explicit_year": bool(re.search(r"2026.*2027", text)), "year_text": text, "project_name": ""}


class MeituanAdapter(BaseCompanyAdapter):
    company = "美团"
    source = "official_meituan"

    def fetch_list(self, page: int) -> List[Dict[str, Any]]:
        return []

    def parse(self, raw_item: Dict[str, Any]) -> Dict[str, str]:
        city_raw = _norm(raw_item.get("city") or raw_item.get("workCity"))
        return {
            "external_job_id": _norm(raw_item.get("id")),
            "title": _norm(raw_item.get("title") or raw_item.get("name")),
            "company": self.company,
            "location_raw": city_raw,
            "city": normalize_city(city_raw, ""),
            "jd_raw": _norm(raw_item.get("description")),
            "update_time": _norm(raw_item.get("updateTime")),
            "raw_tags": "",
            "url": "",
            "collect_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": self.source,
            "recruit_type": "",
            "project_name": "",
        }

    def get_27_signal(self, parsed_item: Dict[str, str]) -> Dict[str, Any]:
        text = _norm(parsed_item.get("jd_raw", ""))
        return {"has_explicit_year": "2027" in text, "year_text": text, "project_name": ""}
