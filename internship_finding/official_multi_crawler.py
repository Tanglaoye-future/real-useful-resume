import json
import hashlib
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import requests
from config import CRAWLER_CONFIG
from parsers.company_registry import get_adapter
from playwright.sync_api import sync_playwright


OUTPUT_FILE = r"c:\jz_code\internship_finding\official_jobs_raw.csv"
SNAPSHOT_LATEST = r"c:\jz_code\internship_finding\snapshot_latest.json"
SNAPSHOT_PREV = r"c:\jz_code\internship_finding\snapshot_prev.json"
HISTORY_DIR = r"c:\jz_code\internship_finding\archive\history\legacy_runs"
HEADLESS = os.getenv("HEADLESS", "1") == "1"
MAX_SCROLL = int(os.getenv("MAX_SCROLL", "10"))
CITY_KEYWORD = os.getenv("CITY_KEYWORD", "上海")
GRAD_KEYWORDS = [x.strip() for x in os.getenv("GRAD_KEYWORDS", "27届,2027届,2027").split(",") if x.strip()]
ENABLED_COMPANIES = set(CRAWLER_CONFIG.get("enabled_companies") or [])
REQUEST_DELAY_SECONDS = float(CRAWLER_CONFIG.get("request_delay_seconds", 0))

SOURCES = [
    {"company": "字节跳动", "source": "official_bytedance", "url_template": "https://jobs.bytedance.com/campus/position?current={page}&limit=40", "pages": 60},
    {"company": "小红书", "source": "official_xiaohongshu", "url_template": "https://job.xiaohongshu.com/campus/position?pageNo={page}", "pages": 120},
    {"company": "快手", "source": "official_kuaishou", "url_template": "https://campus.kuaishou.cn/recruit/campus/e/#/campus", "pages": 1},
    {"company": "腾讯", "source": "official_tencent", "url_template": "https://join.qq.com/campus.html", "pages": 1},
    {"company": "阿里", "source": "official_alibaba", "url_template": "https://talent.alibaba.com/campus/position-list", "pages": 1},
    {"company": "京东", "source": "official_jd", "url_template": "https://campus.jd.com/#/jobs", "pages": 1},
    {"company": "美团", "source": "official_meituan", "url_template": "https://zhaopin.meituan.com/web/campus", "pages": 1},
    {"company": "百度", "source": "official_baidu", "url_template": "https://talent.baidu.com/jobs/list?recruitType=2", "pages": 1},
]


def norm(x: Any) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""
    return re.sub(r"\s+", " ", str(x)).strip()


def source_key(source_name: str) -> str:
    s = norm(source_name).lower()
    return s.replace("official_", "").replace("_api", "")


def is_enabled(source_name: str) -> bool:
    if not ENABLED_COMPANIES:
        return True
    return source_key(source_name) in ENABLED_COMPANIES


def md5_text(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def build_external_job_id(row: Dict[str, Any]) -> str:
    ext = norm(row.get("external_job_id"))
    if ext:
        return ext
    seed = f"{norm(row.get('company'))}|{norm(row.get('name'))}|{norm(row.get('city'))}|{norm(row.get('url'))}"
    return md5_text(seed)


def build_content_hash(row: Dict[str, Any]) -> str:
    seed = f"{norm(row.get('name'))}|{norm(row.get('city'))}|{norm(row.get('jd_raw'))}|{norm(row.get('recruit_type'))}"
    return md5_text(seed)


def load_snapshot(path: str) -> List[Dict[str, str]]:
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except Exception:
        return []
    return []


def save_snapshot(path: str, records: List[Dict[str, str]]):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def walk(obj: Any):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for x in obj:
            yield from walk(x)


def get_str(d: Dict[str, Any], keys: List[str]) -> str:
    for k in keys:
        if k in d and d[k] is not None:
            return norm(d[k])
        for dk, dv in d.items():
            if dk.lower() == k.lower() and dv is not None:
                return norm(dv)
    return ""


def get_city(d: Dict[str, Any]) -> str:
    c = get_str(d, ["city", "work_city", "workCity", "location", "job_city", "city_name", "workplace", "workLocationName"])
    if c:
        return c
    for k in ["city_info", "cityInfo"]:
        val = d.get(k)
        if isinstance(val, dict):
            n = norm(val.get("name") or val.get("i18n_name") or val.get("en_name"))
            if n:
                return n
    txt = norm(
        f"{get_str(d, ['description', 'positionDemand', 'requirement', 'jd'])} "
        f"{get_str(d, ['workLocationName', 'work_location_name'])}"
    )
    if "上海" in txt:
        return "上海"
    return ""


def score_job_like(d: Dict[str, Any]) -> int:
    keys = set(x.lower() for x in d.keys())
    s = 0
    for k in ["title", "name", "positionname", "description", "duty", "requirement", "qualification", "positiondemand", "city", "location", "job_name", "post_url", "url", "id"]:
        if k in keys:
            s += 1
    return s


def is_valid_job_row(title: str, desc: str, req: str) -> bool:
    t = norm(title)
    d = norm(desc)
    r = norm(req)
    if len(t) < 2:
        return False
    if t in {"全部职位", "查看更多", "职位详情", "校招职位"}:
        return False
    if len(d) + len(r) < 20:
        return False
    if re.search(r"(登录|隐私|协议|关于我们|帮助中心|copyright)", t, re.I):
        return False
    return True


def extract_rows_from_payload(payload: Any, source: str, company: str, location_map: Dict[str, str]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for d in walk(payload):
        if not isinstance(d, dict):
            continue
        if score_job_like(d) < 3:
            continue
        title = get_str(d, ["title", "name", "positionName", "job_name", "position_name", "jobTitle"])
        desc = get_str(d, ["description", "duty", "jd", "job_desc", "responsibility", "positionDesc"])
        req = get_str(d, ["requirement", "qualification", "job_require", "qualifications", "positionDemand", "position_demand"])
        city = get_city(d)
        rid = get_str(d, ["id", "job_id", "post_id", "position_id", "positionId", "code"])
        work_location_code = get_str(d, ["workLocationCode", "work_location_code", "locationCode"])
        if not city and work_location_code and work_location_code in location_map:
            city = location_map.get(work_location_code, "")
        url = get_str(d, ["url", "post_url", "detail_url", "job_url", "link"])
        if not url and rid:
            if "bytedance" in source:
                url = f"https://jobs.bytedance.com/campus/position/{rid}/detail"
            if "xiaohongshu" in source:
                url = f"https://job.xiaohongshu.com/campus/position?jobId={rid}"
            if "kuaishou" in source:
                url = f"https://campus.kuaishou.cn/recruit/campus/e/#/position/{rid}"
        recruit_type = get_str(d, ["recruit_type", "job_type", "type"])
        if not is_valid_job_row(title, desc, req):
            continue
        rows.append(
            {
                "url": url,
                "company": company,
                "name": title,
                "city": city,
                "jd_raw": norm(f"{desc} 岗位要求：{req}"),
                "salary": "",
                "company_size": "",
                "duration": "",
                "academic": "",
                "publish_time": get_str(d, ["publish_time", "publishTime", "create_time"]),
                "deadline": get_str(d, ["deadline", "end_time", "expire_time"]),
                "collect_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "source": source,
                "recruit_type": recruit_type,
            }
        )
    return rows


def crawl_one_source(playwright, conf: Dict[str, Any]) -> List[Dict[str, str]]:
    browser = playwright.chromium.launch(channel="msedge", headless=HEADLESS)
    context = browser.new_context(locale="zh-CN")
    page = context.new_page()
    payloads: List[Any] = []
    api_tasks: List[Dict[str, Any]] = []
    location_map: Dict[str, str] = {}

    def on_response(resp):
        try:
            ct = resp.headers.get("content-type", "")
            if "application/json" not in ct:
                return
            data = resp.json()
            payloads.append(data)

            if "job.xiaohongshu.com/websiterecruit/position/pageQueryPosition" in resp.url:
                req = resp.request
                body = req.post_data
                if body:
                    try:
                        payload = json.loads(body)
                    except Exception:
                        payload = None
                    if isinstance(payload, dict):
                        total = 80
                        page_info = data.get("result") or data.get("data") or {}
                        if isinstance(page_info, dict):
                            total = int(page_info.get("pages") or page_info.get("totalPage") or total)
                        api_tasks.append({"url": resp.url, "payload": payload, "total": min(total, 200), "page_field": "pageNum"})

            if "campus.kuaishou.cn/recruit/campus/e/api/v1/open/positions/simple" in resp.url:
                req = resp.request
                body = req.post_data
                if body:
                    try:
                        payload = json.loads(body)
                    except Exception:
                        payload = None
                    if isinstance(payload, dict):
                        total = int((data.get("result") or {}).get("pages") or 1)
                        api_tasks.append({"url": resp.url, "payload": payload, "total": min(total, 120), "page_field": "pageNum"})

            if "campus.kuaishou.cn/recruit/campus/e/api/v1/open/dictionary/batch" in resp.url:
                result = data.get("result") or {}
                for key in ["workLocation", "work_location", "workLocationCode"]:
                    arr = result.get(key)
                    if isinstance(arr, list):
                        for it in arr:
                            if isinstance(it, dict):
                                code = norm(it.get("code") or it.get("value") or it.get("id"))
                                name = norm(it.get("name") or it.get("label"))
                                if code and name:
                                    location_map[code] = name
        except Exception:
            return

    page.on("response", on_response)
    for p in range(1, conf["pages"] + 1):
        url = conf["url_template"].format(page=p)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(1200)
            if conf["source"] == "official_kuaishou":
                for tab in ["实习招聘", "应届招聘"]:
                    try:
                        page.get_by_text(tab).first.click(timeout=3000)
                        page.wait_for_timeout(1200)
                    except Exception:
                        pass
            for _ in range(MAX_SCROLL):
                page.mouse.wheel(0, 1200)
                page.wait_for_timeout(250)
        except Exception:
            continue
        if REQUEST_DELAY_SECONDS > 0:
            time.sleep(REQUEST_DELAY_SECONDS)

    seen_api = set()
    for t in api_tasks:
        key = (t["url"], t["page_field"])
        if key in seen_api:
            continue
        seen_api.add(key)
        payload = dict(t["payload"])
        for page_no in range(2, int(t["total"]) + 1):
            payload[t["page_field"]] = page_no
            try:
                resp = context.request.post(
                    t["url"],
                    data=json.dumps(payload),
                    headers={"content-type": "application/json"},
                    timeout=30000,
                )
                if resp.ok:
                    payloads.append(resp.json())
            except Exception:
                continue

    rows: List[Dict[str, str]] = []
    for payload in payloads:
        rows.extend(extract_rows_from_payload(payload, conf["source"], conf["company"], location_map))

    seen = set()
    out = []
    for r in rows:
        key = (r["company"], r["name"], r["city"], r["url"], r["jd_raw"][:200])
        if key in seen:
            continue
        seen.add(key)
        out.append(r)

    context.close()
    browser.close()
    return out


def fetch_jd_jobs() -> List[Dict[str, str]]:
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://campus.jd.com/#/jobs",
        "Content-Type": "application/json",
    }
    list_url = "https://campus.jd.com/api/wx/position/page?type=present"
    rows: List[Dict[str, str]] = []
    page_size = 50
    page_index = 0
    total_pages = 1
    while page_index < total_pages:
        payload = {
            "pageSize": page_size,
            "pageIndex": page_index,
            "parameter": {
                "positionName": "",
                "planIdList": [],
                "jobDirectionCodeList": [],
                "workCityCodeList": [],
                "positionDeptList": [],
            },
        }
        try:
            data = requests.post(list_url, json=payload, headers=headers, timeout=30).json()
        except Exception:
            break
        body = data.get("body") or {}
        items = body.get("items") or []
        total_number = int(body.get("totalNumber") or 0)
        total_pages = max(1, (total_number + page_size - 1) // page_size)

        for it in items:
            title = norm(it.get("positionName"))
            city = norm(it.get("workCity"))
            city_set = []
            req_list = it.get("requirementVoList") or []
            if isinstance(req_list, list):
                for req in req_list:
                    if isinstance(req, dict):
                        wc = norm(req.get("workCity"))
                        if wc and wc not in city_set:
                            city_set.append(wc)
            if city_set:
                city = " ".join(city_set)
            work_content = norm(it.get("workContent"))
            qualification = norm(it.get("qualification"))
            if not title:
                continue
            rows.append(
                {
                    "url": "",
                    "company": "京东",
                    "name": title,
                    "city": city,
                    "jd_raw": norm(f"{work_content} 岗位要求：{qualification}"),
                    "salary": "",
                    "company_size": "",
                    "duration": "",
                    "academic": norm(it.get("education")),
                    "publish_time": norm(it.get("publishTime")),
                    "deadline": "",
                    "collect_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "source": "official_jd_api",
                    "recruit_type": "应届生",
                }
            )
        page_index += 1
        if REQUEST_DELAY_SECONDS > 0:
            time.sleep(REQUEST_DELAY_SECONDS)

    dedup = []
    seen = set()
    for r in rows:
        key = (r["company"], r["name"], r["city"], r["jd_raw"][:200])
        if key in seen:
            continue
        seen.add(key)
        dedup.append(r)
    return dedup


def fetch_tencent_jobs() -> List[Dict[str, str]]:
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://join.qq.com/post.html?query=p_1",
        "Content-Type": "application/json",
    }
    list_url = "https://join.qq.com/api/v1/position/searchPosition"
    detail_url = "https://join.qq.com/api/v1/jobDetails/getJobDetailsByPostId"

    rows: List[Dict[str, str]] = []
    page_size = 50
    page_index = 1
    total = 1
    while (page_index - 1) * page_size < total:
        payload = {
            "projectIdList": [],
            "projectMappingIdList": [1],
            "keyword": "",
            "bgList": [],
            "workCountryType": 0,
            "workCityList": [],
            "recruitCityList": [],
            "positionFidList": [],
            "pageIndex": page_index,
            "pageSize": page_size,
        }
        try:
            resp = requests.post(list_url, params={"timestamp": str(int(time.time() * 1000))}, json=payload, headers=headers, timeout=30).json()
        except Exception:
            break
        data = resp.get("data") or {}
        items = data.get("positionList") or []
        total = int(data.get("count") or 0)
        if not items:
            break

        for it in items:
            post_id = norm(it.get("postId"))
            title = norm(it.get("positionTitle"))
            city = norm(it.get("workCities"))
            recruit_type = norm(it.get("projectName") or it.get("recruitLabelName"))
            detail = {}
            if post_id:
                try:
                    detail = requests.get(
                        detail_url,
                        params={"postId": post_id, "timestamp": str(int(time.time() * 1000))},
                        headers=headers,
                        timeout=30,
                    ).json().get("data") or {}
                except Exception:
                    detail = {}
            desc = norm(detail.get("desc"))
            req = norm(detail.get("require"))
            link = f"https://join.qq.com/post.html?query=p_1&postId={post_id}" if post_id else ""

            if not title:
                continue
            rows.append(
                {
                    "url": link,
                    "company": "腾讯",
                    "name": title,
                    "city": city,
                    "jd_raw": norm(f"{desc} 岗位要求：{req}"),
                    "salary": "",
                    "company_size": "",
                    "duration": "",
                    "academic": "",
                    "publish_time": "",
                    "deadline": "",
                    "collect_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "source": "official_tencent_api",
                    "recruit_type": recruit_type,
                }
            )
        page_index += 1
        if REQUEST_DELAY_SECONDS > 0:
            time.sleep(REQUEST_DELAY_SECONDS)

    dedup = []
    seen = set()
    for r in rows:
        key = (r["company"], r["name"], r["city"], r["jd_raw"][:200])
        if key in seen:
            continue
        seen.add(key)
        dedup.append(r)
    return dedup


def fetch_kuaishou_jobs_api(max_pages: int = 120) -> List[Dict[str, str]]:
    adapter = get_adapter("kuaishou")
    if adapter is None:
        return []
    rows: List[Dict[str, str]] = []
    for nature_code in ["intern", "fulltime"]:
        if hasattr(adapter, "set_mode"):
            adapter.set_mode(nature_code)
        for page in range(1, max_pages + 1):
            try:
                items = adapter.fetch_list(page)
            except Exception:
                items = []
            if not items:
                break
            for it in items:
                parsed = adapter.parse(it)
                if not parsed.get("title"):
                    continue
                rows.append(
                    {
                        "url": parsed.get("url", ""),
                        "company": parsed.get("company", "快手"),
                        "name": parsed.get("title", ""),
                        "city": parsed.get("city", ""),
                        "jd_raw": parsed.get("jd_raw", ""),
                        "salary": "",
                        "company_size": "",
                        "duration": "",
                        "academic": "",
                        "publish_time": "",
                        "deadline": "",
                        "collect_time": parsed.get("collect_time", time.strftime("%Y-%m-%d %H:%M:%S")),
                        "source": parsed.get("source", "official_kuaishou_api"),
                        "recruit_type": parsed.get("recruit_type", ""),
                        "raw_tags": parsed.get("raw_tags", ""),
                        "external_job_id": parsed.get("external_job_id", ""),
                        "update_time": parsed.get("update_time", ""),
                    }
                )
            if REQUEST_DELAY_SECONDS > 0:
                time.sleep(REQUEST_DELAY_SECONDS)
    dedup = []
    seen = set()
    for r in rows:
        key = (r["company"], r["name"], r["city"], r["url"], r["jd_raw"][:200])
        if key in seen:
            continue
        seen.add(key)
        dedup.append(r)
    return dedup


def main():
    all_rows: List[Dict[str, str]] = []
    with sync_playwright() as p:
        for conf in SOURCES:
            if not is_enabled(conf["source"]):
                continue
            if conf["source"] == "official_kuaishou":
                continue
            rows = crawl_one_source(p, conf)
            print(conf["company"], conf["source"], len(rows))
            all_rows.extend(rows)

    if is_enabled("official_tencent_api"):
        tencent_rows = fetch_tencent_jobs()
        print("腾讯 official_tencent_api", len(tencent_rows))
        all_rows.extend(tencent_rows)

    if is_enabled("official_kuaishou_api"):
        kuaishou_rows = fetch_kuaishou_jobs_api()
        print("快手 official_kuaishou_api", len(kuaishou_rows))
        all_rows.extend(kuaishou_rows)

    if is_enabled("official_jd_api"):
        jd_rows = fetch_jd_jobs()
        print("京东 official_jd_api", len(jd_rows))
        all_rows.extend(jd_rows)

    if not all_rows:
        print("官方站未抓到可用数据")
        return

    df = pd.DataFrame(all_rows)
    df = df.fillna("")
    df["external_job_id"] = df.apply(lambda r: build_external_job_id(r.to_dict()), axis=1)
    df["content_hash"] = df.apply(lambda r: build_content_hash(r.to_dict()), axis=1)
    df["sync_key"] = df["source"].map(norm) + "|" + df["external_job_id"].map(norm)
    df = df.drop_duplicates(subset=["company", "name", "city", "url", "jd_raw"], keep="first")

    if os.path.exists(SNAPSHOT_LATEST):
        try:
            if os.path.exists(SNAPSHOT_PREV):
                os.remove(SNAPSHOT_PREV)
            os.replace(SNAPSHOT_LATEST, SNAPSHOT_PREV)
        except Exception:
            pass

    prev_records = load_snapshot(SNAPSHOT_PREV)
    prev_map = {f"{norm(r.get('source'))}|{norm(r.get('external_job_id'))}": norm(r.get("content_hash")) for r in prev_records}

    status_list = []
    change_rows = []
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for row in df.to_dict(orient="records"):
        key = row["sync_key"]
        new_hash = norm(row["content_hash"])
        old_hash = prev_map.get(key)
        if old_hash is None:
            status = "NEW"
        elif old_hash != new_hash:
            status = "UPDATED"
        else:
            status = "UNCHANGED"
        status_list.append(status)
        if status in {"NEW", "UPDATED"}:
            change_rows.append({"sync_key": key, "status": status, "collect_time": now_ts})
    df["sync_status"] = status_list

    current_keys = set(df["sync_key"].tolist())
    for key in prev_map.keys():
        if key not in current_keys:
            change_rows.append({"sync_key": key, "status": "CLOSED", "collect_time": now_ts})

    snapshot_rows = df[["source", "external_job_id", "content_hash"]].to_dict(orient="records")
    save_snapshot(SNAPSHOT_LATEST, snapshot_rows)

    os.makedirs(HISTORY_DIR, exist_ok=True)
    change_file_json = os.path.join(HISTORY_DIR, f"changes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(change_file_json, "w", encoding="utf-8") as f:
        json.dump(change_rows, f, ensure_ascii=False, indent=2)
    change_file_csv = change_file_json.replace(".json", ".csv")
    pd.DataFrame(change_rows).to_csv(change_file_csv, index=False, encoding="utf-8-sig")

    df = df.drop(columns=["sync_key"])
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print("official_rows", len(df), OUTPUT_FILE)
    print("changes_file", change_file_json)


if __name__ == "__main__":
    main()
