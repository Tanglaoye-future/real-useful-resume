import json
import os
import re
from datetime import datetime

import requests


UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
SITE_JS_DIR = os.path.join(os.path.dirname(__file__), "site_main_js")


def safe_get(url, headers=None, params=None, timeout=15):
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=timeout)
        return resp, ""
    except Exception as e:
        return None, str(e)


def safe_post(url, headers=None, json_body=None, timeout=15):
    try:
        resp = requests.post(url, headers=headers, json=json_body, timeout=timeout)
        return resp, ""
    except Exception as e:
        return None, str(e)


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def js_signals(filename, patterns):
    path = os.path.join(SITE_JS_DIR, filename)
    text = read_text(path)
    hits = {}
    for p in patterns:
        matches = re.findall(p, text, flags=re.IGNORECASE)
        hits[p] = len(matches)
    return {
        "file": path,
        "size_kb": round(os.path.getsize(path) / 1024, 1),
        "hits": hits,
    }


def parse_json_body(resp):
    try:
        return resp.json(), ""
    except Exception as e:
        return None, str(e)


def extract_jsessionid(cookie_text):
    m = re.search(r'JSESSIONID="?([^";]+)"?', cookie_text or "")
    return m.group(1) if m else ""


def result_template(site, endpoint, method, js_info):
    return {
        "site": site,
        "endpoint": endpoint,
        "method": method,
        "js_info": js_info,
        "status_code": 0,
        "ok": False,
        "evidence": "",
        "error": "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def test_liepin():
    js_info = js_signals(
        "liepin.main.js",
        [r"x-fscp", r"pc-search-job", r"liepin", r"trace-id", r"x-requested-with"],
    )
    endpoint = "https://www.liepin.com/api/com.liepin.searchfront4c.pc-search-job"
    data = {
        "mainSearchPcConditionForm": {
            "city": "020",
            "key": "实习",
            "currentPage": 0,
        },
        "passThroughForm": {"scene": "input"},
    }
    headers = {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.liepin.com/zhaopin/",
    }
    cookie = os.getenv("LIEPIN_COOKIE", "")
    if cookie:
        headers["Cookie"] = cookie
    out = result_template("liepin", endpoint, "POST", js_info)
    resp, err = safe_post(endpoint, headers=headers, json_body=data)
    if err:
        out["error"] = err
        return out
    out["status_code"] = resp.status_code
    body, jerr = parse_json_body(resp)
    if not jerr and isinstance(body, dict):
        out["evidence"] = str(body.get("flag") or body.get("code") or body.get("msg") or "")[:240]
        out["ok"] = resp.status_code == 200 and body.get("flag") is not None
    else:
        out["evidence"] = (resp.text or "")[:240]
        out["ok"] = resp.status_code == 200 and "job" in (resp.text or "").lower()
    return out


def test_linkedin():
    js_info = js_signals(
        "linkedin.main.js",
        [r"x-li-track", r"csrf-token", r"x-restli-protocol-version", r"jobs-guest", r"seeMoreJobPostings"],
    )
    endpoint = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    params = {"keywords": "Intern", "location": "Shanghai", "start": "0"}
    headers = {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.linkedin.com/jobs/search/?keywords=Intern&location=Shanghai",
    }
    cookie = os.getenv("LINKEDIN_COOKIE", "")
    if cookie:
        headers["Cookie"] = cookie
        jsession = extract_jsessionid(cookie)
        if jsession:
            headers["csrf-token"] = jsession
    out = result_template("linkedin", endpoint, "GET", js_info)
    resp, err = safe_get(endpoint, headers=headers, params=params)
    if err:
        out["error"] = err
        return out
    out["status_code"] = resp.status_code
    html = resp.text or ""
    out["evidence"] = html[:240]
    out["ok"] = resp.status_code == 200 and ("base-card" in html or "job-search-card" in html or "<li" in html)
    return out


def test_maimai():
    js_info = js_signals(
        "maimai.main.js",
        [r"maimai", r"/api/", r"cookie", r"token", r"authorization", r"x-"],
    )
    endpoint = "https://maimai.cn"
    headers = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
    cookie = os.getenv("MAIMAI_COOKIE", "")
    if cookie:
        headers["Cookie"] = cookie
    out = result_template("maimai", endpoint, "GET", js_info)
    resp, err = safe_get(endpoint, headers=headers)
    if err:
        out["error"] = err
        return out
    out["status_code"] = resp.status_code
    html = resp.text or ""
    out["evidence"] = html[:240]
    out["ok"] = resp.status_code == 200 and ("maimai" in html.lower() or "脉脉" in html)
    return out


def test_shixiseng():
    js_info = js_signals(
        "shixiseng.main.js",
        [r"apigateway\.shixiseng\.com", r"api/interns/search", r"cookie", r"newApiHost", r"login"],
    )
    endpoint = "https://www.shixiseng.com/api/interns/search"
    params = {"k": "实习", "c": "310000", "p": "1"}
    headers = {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.shixiseng.com/interns",
    }
    cookie = os.getenv("SHIXISENG_COOKIE", "")
    if cookie:
        headers["Cookie"] = cookie
    out = result_template("shixiseng", endpoint, "GET", js_info)
    resp, err = safe_get(endpoint, headers=headers, params=params)
    if err:
        out["error"] = err
        return out
    out["status_code"] = resp.status_code
    body, jerr = parse_json_body(resp)
    if not jerr and isinstance(body, dict):
        msg = body.get("msg")
        count = len(msg) if isinstance(msg, list) else 0
        out["evidence"] = f"code={body.get('code')} count={count}"
        out["ok"] = resp.status_code == 200 and body.get("code") in {200, "200"}
    else:
        out["evidence"] = (resp.text or "")[:240]
        out["ok"] = False
    return out


def test_yingjiesheng():
    js_info = js_signals(
        "yingjiesheng.main.js",
        [r"cookie", r"u_asession", r"yingjiesheng", r"jobsearch", r"php"],
    )
    endpoint = "http://my.yingjiesheng.com/index.php/personal/jobsearch"
    headers = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
    cookie = os.getenv("YINGJIESHENG_COOKIE", "")
    if cookie:
        headers["Cookie"] = cookie
    out = result_template("yingjiesheng", endpoint, "GET", js_info)
    resp, err = safe_get(endpoint, headers=headers)
    if err:
        out["error"] = err
        return out
    out["status_code"] = resp.status_code
    html = resp.text or ""
    out["evidence"] = html[:240]
    out["ok"] = resp.status_code in {200, 302} and ("yingjiesheng" in html.lower() or "应届生" in html or "jobsearch" in html.lower())
    return out


def test_zhilian():
    js_info = js_signals(
        "zhilian.main.js",
        [r"x-zp-token", r"x-zp-client-id", r"zhaopin", r"fe-api", r"sign"],
    )
    endpoint = "https://fe-api.zhaopin.com/c/i/sou"
    params = {"pageSize": "20", "cityId": "538", "kw": "实习", "kt": "3", "p": "1"}
    headers = {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://sou.zhaopin.com/",
    }
    cookie = os.getenv("ZHILIAN_COOKIE", "") or os.getenv("ZHAOPIN_COOKIE", "")
    if cookie:
        headers["Cookie"] = cookie
    out = result_template("zhilian", endpoint, "GET", js_info)
    resp, err = safe_get(endpoint, headers=headers, params=params)
    if err:
        out["error"] = err
        return out
    out["status_code"] = resp.status_code
    body, jerr = parse_json_body(resp)
    if not jerr and isinstance(body, dict):
        out["evidence"] = str(body.get("code") or body.get("message") or body.get("msg") or "")[:240]
        out["ok"] = resp.status_code == 200 and body.get("data") is not None
    else:
        out["evidence"] = (resp.text or "")[:240]
        out["ok"] = resp.status_code == 200 and ("职位" in (resp.text or "") or "job" in (resp.text or "").lower())
    return out


def main():
    tests = [
        test_liepin,
        test_linkedin,
        test_maimai,
        test_shixiseng,
        test_yingjiesheng,
        test_zhilian,
    ]
    results = [fn() for fn in tests]
    ok_count = sum(1 for r in results if r.get("ok"))
    payload = {
        "summary": {"total": len(results), "ok": ok_count, "failed": len(results) - ok_count},
        "results": results,
    }
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "mvp_reverse_test.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(json.dumps(payload, ensure_ascii=False))
    print(output_file)


if __name__ == "__main__":
    main()
