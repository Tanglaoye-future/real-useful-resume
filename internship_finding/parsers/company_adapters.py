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
        publish_time = _norm(
            raw_item.get("publishTime")
            or raw_item.get("createTime")
            or detail.get("publishTime")
            or detail.get("createTime")
        )
        deadline = _norm(
            raw_item.get("deadline")
            or raw_item.get("endTime")
            or detail.get("deadline")
            or detail.get("endTime")
            or detail.get("deliveryEndTime")
        )
        return {
            "external_job_id": position_id,
            "title": title,
            "company": self.company,
            "location_raw": city_raw,
            "city": city,
            "jd_raw": jd_raw,
            "update_time": _norm(detail.get("updateTime") or raw_item.get("updateTime")),
            "publish_time": publish_time,
            "deadline": deadline,
            "raw_tags": _norm(project_name),
            "url": f"https://campus.kuaishou.cn/recruit/campus/e/#/campus/jobs?positionId={position_id}" if position_id else "",
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
    list_url = "https://join.qq.com/api/v1/position/searchPosition"
    detail_url = "https://join.qq.com/api/v1/jobDetails/getJobDetailsByPostId"

    def fetch_list(self, page: int) -> List[Dict[str, Any]]:
        payload = {
            "projectIdList": [],
            "projectMappingIdList": [],
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
            resp = requests.post(self.list_url, params={"timestamp": str(int(time.time() * 1000))}, json=payload, timeout=20).json()
            return (resp.get("data") or {}).get("positionList") or []
        except Exception:
            return []

    def _fetch_detail(self, post_id: str) -> Dict[str, Any]:
        if not post_id:
            return {}
        try:
            resp = requests.get(
                self.detail_url,
                params={"postId": post_id, "timestamp": str(int(time.time() * 1000))},
                timeout=20,
            ).json()
            return (resp.get("data") or {}) if isinstance(resp, dict) else {}
        except Exception:
            return {}

    def parse(self, raw_item: Dict[str, Any]) -> Dict[str, str]:
        post_id = _norm(raw_item.get("postId"))
        detail = self._fetch_detail(post_id)
        desc = _norm(detail.get("desc") or detail.get("topicDetail") or detail.get("introduction"))
        req = _norm(detail.get("request") or detail.get("require") or detail.get("topicRequirement"))
        jd_raw = _norm(f"{desc} 岗位要求：{req}")
        raw_tags = _norm(
            f"{raw_item.get('projectName') or ''} {raw_item.get('recruitLabelName') or ''} {raw_item.get('groupTag') or ''} {raw_item.get('positionFamily') or ''}"
        )
        publish_time = _norm(
            raw_item.get("publishTime")
            or raw_item.get("createTime")
            or detail.get("publishTime")
            or detail.get("createTime")
            or detail.get("postTime")
        )
        deadline = _norm(
            raw_item.get("deadline")
            or raw_item.get("endTime")
            or detail.get("deadline")
            or detail.get("endTime")
            or detail.get("finishTime")
        )
        return {
            "external_job_id": post_id,
            "title": _norm(raw_item.get("positionTitle")),
            "company": self.company,
            "location_raw": _norm(raw_item.get("workCities")),
            "city": normalize_city(raw_item.get("workCities"), ""),
            "jd_raw": jd_raw,
            "update_time": "",
            "publish_time": publish_time,
            "deadline": deadline,
            "raw_tags": raw_tags,
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
    list_url = "https://job.xiaohongshu.com/websiterecruit/position/pageQueryPosition"

    def __init__(self, page_size: int = 20, timeout: int = 20):
        self.page_size = page_size
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://job.xiaohongshu.com/campus/position",
            "Origin": "https://job.xiaohongshu.com",
            "Content-Type": "application/json",
        }

    def fetch_list(self, page: int) -> List[Dict[str, Any]]:
        payload = {"recruitType": "campus", "positionName": "", "pageNum": page, "pageSize": self.page_size}
        try:
            resp = requests.post(self.list_url, json=payload, headers=self.headers, timeout=self.timeout).json()
            data = resp.get("data") or {}
            items = data.get("list") or data.get("records") or []
            return items if isinstance(items, list) else []
        except Exception:
            return []

    def parse(self, raw_item: Dict[str, Any]) -> Dict[str, str]:
        position_id = _norm(raw_item.get("positionId") or raw_item.get("id"))
        title = _norm(raw_item.get("positionName") or raw_item.get("title"))
        city_raw = _norm(raw_item.get("workplace") or raw_item.get("city"))
        duty = _norm(raw_item.get("duty") or raw_item.get("description"))
        qualification = _norm(raw_item.get("qualification") or raw_item.get("requirement"))
        job_project_name = _norm(raw_item.get("jobProjectName"))
        job_type = _norm(raw_item.get("jobType"))
        labels = raw_item.get("labels")
        if isinstance(labels, list):
            label_text = " ".join(_norm(x) for x in labels if _norm(x))
        else:
            label_text = _norm(labels)
        raw_tags = _norm(f"{job_project_name} {job_type} {label_text}")
        jd_raw = _norm(f"{duty} 岗位要求：{qualification}")
        publish_time = _norm(raw_item.get("publishTime") or raw_item.get("updateTime") or raw_item.get("createTime"))
        deadline = _norm(raw_item.get("deadline") or raw_item.get("endTime") or raw_item.get("deliveryEndTime"))
        return {
            "external_job_id": position_id,
            "title": title,
            "company": self.company,
            "location_raw": city_raw,
            "city": normalize_city(city_raw, ""),
            "jd_raw": jd_raw,
            "update_time": _norm(raw_item.get("publishTime") or raw_item.get("updateTime")),
            "publish_time": publish_time,
            "deadline": deadline,
            "raw_tags": raw_tags,
            "url": f"https://job.xiaohongshu.com/campus/position?positionId={position_id}" if position_id else "",
            "collect_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": self.source,
            "recruit_type": _norm(job_project_name or job_type),
            "project_name": job_project_name,
        }

    def get_27_signal(self, parsed_item: Dict[str, str]) -> Dict[str, Any]:
        text = _norm(f"{parsed_item.get('project_name', '')} {parsed_item.get('jd_raw', '')}")
        return {"has_explicit_year": "2027" in text, "year_text": text, "project_name": parsed_item.get("project_name", "")}


class AlibabaAdapter(BaseCompanyAdapter):
    company = "阿里"
    source = "official_alibaba"
    list_url = "https://talent.alibaba.com/position/search"
    list_page_url = "https://talent.alibaba.com/campus/position-list?campusType=freshman"

    def __init__(self, page_size: int = 20, timeout: int = 20):
        self.page_size = page_size
        self.timeout = timeout
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": self.list_page_url,
            "Content-Type": "application/json",
        }

    def _get_csrf(self) -> str:
        try:
            self.session.get(self.list_page_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=self.timeout)
        except Exception:
            pass
        return _norm(self.session.cookies.get("XSRF-TOKEN"))

    def fetch_list(self, page: int) -> List[Dict[str, Any]]:
        csrf = self._get_csrf()
        if not csrf:
            return []
        payload = {
            "channel": "campus_group_official_site",
            "language": "zh",
            "pageSize": self.page_size,
            "batchId": "",
            "subCategories": "",
            "regions": "",
            "customDeptCode": "",
            "corpCode": "",
            "pageIndex": page,
            "key": "",
            "categoryType": "freshman",
        }
        try:
            url = f"{self.list_url}?_csrf={csrf}"
            resp = self.session.post(url, json=payload, headers=self.headers, timeout=self.timeout).json()
            content = resp.get("content") or {}
            items = content.get("datas") or content.get("list") or []
            return items if isinstance(items, list) else []
        except Exception:
            return []

    def parse(self, raw_item: Dict[str, Any]) -> Dict[str, str]:
        pos_id = _norm(raw_item.get("id"))
        work_locations = raw_item.get("workLocations")
        if isinstance(work_locations, list):
            city_raw = _norm(" ".join(_norm(x) for x in work_locations if _norm(x)))
        else:
            city_raw = _norm(raw_item.get("workLocation") or raw_item.get("city"))
        desc = _norm(raw_item.get("description"))
        req = _norm(raw_item.get("requirement"))
        graduation = raw_item.get("graduationTime") or {}
        if isinstance(graduation, dict):
            grad_from = _norm(graduation.get("from"))
            grad_to = _norm(graduation.get("to"))
        else:
            grad_from = ""
            grad_to = ""
        raw_tags = _norm(
            f"{raw_item.get('batchName') or ''} {raw_item.get('categoryName') or ''} {raw_item.get('project') or ''} 毕业时间:{grad_from}-{grad_to}"
        )
        return {
            "external_job_id": pos_id,
            "title": _norm(raw_item.get("name") or raw_item.get("title")),
            "company": self.company,
            "location_raw": city_raw,
            "city": normalize_city(city_raw, ""),
            "jd_raw": _norm(f"{desc} 岗位要求：{req}"),
            "update_time": _norm(raw_item.get("modifyTime")),
            "publish_time": _norm(raw_item.get("publishTime")),
            "deadline": "",
            "raw_tags": raw_tags,
            "url": _norm(raw_item.get("positionUrl")) or (f"https://talent.alibaba.com/campus/position-detail?positionId={pos_id}" if pos_id else ""),
            "collect_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": self.source,
            "recruit_type": _norm(raw_item.get("batchName") or raw_item.get("categoryName") or raw_item.get("categoryType")),
            "project_name": _norm(raw_item.get("batchName") or raw_item.get("project")),
        }

    def get_27_signal(self, parsed_item: Dict[str, str]) -> Dict[str, Any]:
        text = _norm(f"{parsed_item.get('recruit_type', '')} {parsed_item.get('raw_tags', '')} {parsed_item.get('jd_raw', '')}")
        return {"has_explicit_year": bool(re.search(r"2026.*2027", text)), "year_text": text, "project_name": ""}


class MeituanAdapter(BaseCompanyAdapter):
    company = "美团"
    source = "official_meituan"
    list_url = "https://zhaopin.meituan.com/api/official/job/getJobList"
    detail_url = "https://zhaopin.meituan.com/api/official/job/getJobDetail"

    def __init__(self, page_size: int = 20, timeout: int = 20):
        self.page_size = page_size
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://zhaopin.meituan.com/web/campus",
            "Content-Type": "application/json",
        }

    def fetch_list(self, page: int) -> List[Dict[str, Any]]:
        payload = {
            "page": {"pageNo": page, "pageSize": self.page_size},
            "jobShareType": "1",
            "keywords": "",
            "cityList": [],
            "department": [],
            "jfJgList": [],
            "jobType": [{"code": "1", "subCode": []}, {"code": "2", "subCode": []}],
            "typeCode": [],
            "specialCode": [],
            "u_query_id": f"meituan_{int(time.time() * 1000)}",
            "r_query_id": str(int(time.time() * 1000)),
        }
        try:
            resp = requests.post(self.list_url, json=payload, headers=self.headers, timeout=self.timeout).json()
            data = resp.get("data") or {}
            items = data.get("list") or data.get("jobList") or []
            return items if isinstance(items, list) else []
        except Exception:
            return []

    def _fetch_detail(self, job_union_id: str) -> Dict[str, Any]:
        if not job_union_id:
            return {}
        try:
            resp = requests.post(
                self.detail_url,
                json={"jobUnionId": job_union_id},
                headers=self.headers,
                timeout=self.timeout,
            ).json()
            data = resp.get("data") or {}
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def parse(self, raw_item: Dict[str, Any]) -> Dict[str, str]:
        job_union_id = _norm(raw_item.get("jobUnionId") or raw_item.get("id"))
        detail = self._fetch_detail(job_union_id)
        city_list = raw_item.get("cityList")
        if isinstance(city_list, list):
            city_raw = _norm(" ".join(_norm(x.get("name")) for x in city_list if isinstance(x, dict)))
        else:
            city_raw = _norm(raw_item.get("city") or raw_item.get("workCity"))
        dept_list = raw_item.get("department")
        if isinstance(dept_list, list):
            dept_text = _norm(" ".join(_norm(x.get("name")) for x in dept_list if isinstance(x, dict)))
        else:
            dept_text = _norm(raw_item.get("department"))
        duty = _norm(detail.get("jobDuty") or raw_item.get("jobDuty") or raw_item.get("desc"))
        req = _norm(detail.get("jobRequirement") or raw_item.get("jobRequirement"))
        high_light = _norm(detail.get("highLight") or raw_item.get("highLight"))
        jd_raw = _norm(f"{duty} 岗位要求：{req} 亮点：{high_light}")
        raw_tags = _norm(f"{raw_item.get('jobFamily') or ''} {raw_item.get('jobFamilyGroup') or ''} {raw_item.get('projectName') or ''} {raw_item.get('jobType') or ''}")
        publish_time = _norm(detail.get("firstPostTime") or raw_item.get("firstPostTime") or raw_item.get("refreshTime"))
        deadline = _norm(detail.get("expiredTime") or raw_item.get("expiredTime"))
        return {
            "external_job_id": job_union_id,
            "title": _norm(raw_item.get("name") or detail.get("name") or raw_item.get("title")),
            "company": self.company,
            "location_raw": city_raw,
            "city": normalize_city(city_raw, ""),
            "jd_raw": jd_raw,
            "update_time": _norm(detail.get("refreshTime") or raw_item.get("refreshTime")),
            "publish_time": publish_time,
            "deadline": deadline,
            "raw_tags": raw_tags,
            "url": f"https://zhaopin.meituan.com/web/job/{job_union_id}" if job_union_id else "",
            "collect_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": self.source,
            "recruit_type": _norm(raw_item.get("projectName") or raw_item.get("jobType")),
            "project_name": _norm(raw_item.get("projectName")),
            "department": dept_text,
        }

    def get_27_signal(self, parsed_item: Dict[str, str]) -> Dict[str, Any]:
        text = _norm(parsed_item.get("jd_raw", ""))
        return {"has_explicit_year": "2027" in text, "year_text": text, "project_name": ""}
