import json
import os
from datetime import datetime

from playwright.sync_api import sync_playwright


UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"


def parse_cookie_str(cookie_str):
    out = []
    if not cookie_str:
        return out
    for item in cookie_str.split(";"):
        if "=" not in item:
            continue
        k, v = item.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k:
            continue
        out.append((k, v))
    return out


def add_cookies_from_env(context, env_key, domain):
    raw = os.getenv(env_key, "")
    parsed = parse_cookie_str(raw)
    if not parsed:
        return 0
    cookies = []
    for name, value in parsed:
        cookies.append(
            {
                "name": name,
                "value": value,
                "domain": domain,
                "path": "/",
                "httpOnly": False,
                "secure": True,
            }
        )
    context.add_cookies(cookies)
    return len(cookies)


def test_shixiseng(page):
    result = {
        "site": "shixiseng",
        "ok": False,
        "status_code": 0,
        "title": "",
        "data_count": 0,
        "evidence": "",
        "error": "",
    }
    try:
        response = page.goto("https://www.shixiseng.com/interns", wait_until="domcontentloaded", timeout=45000)
        result["status_code"] = response.status if response else 0
        page.wait_for_timeout(2500)
        result["title"] = page.title()
        api_data = page.evaluate(
            """async () => {
                const u = "https://www.shixiseng.com/api/interns/search?k=%E5%AE%9E%E4%B9%A0&c=310000&p=1";
                const resp = await fetch(u, {method: "GET", credentials: "include"});
                const text = await resp.text();
                let parsed = null;
                try { parsed = JSON.parse(text); } catch(e) {}
                return {status: resp.status, text: text.slice(0, 300), parsed};
            }"""
        )
        parsed = api_data.get("parsed") if isinstance(api_data, dict) else None
        if isinstance(parsed, dict):
            msg = parsed.get("msg")
            count = len(msg) if isinstance(msg, list) else 0
            result["data_count"] = count
            result["evidence"] = f"api_status={api_data.get('status')} code={parsed.get('code')} count={count}"
            result["ok"] = api_data.get("status") == 200 and parsed.get("code") in {200, "200"} and count > 0
        else:
            result["evidence"] = (api_data.get("text") or "")[:300] if isinstance(api_data, dict) else ""
            html = page.content()
            result["ok"] = "实习岗位" in html or "intern-wrap" in html or "intern-item" in html
    except Exception as e:
        result["error"] = str(e)
    return result


def test_yingjiesheng(page):
    result = {
        "site": "yingjiesheng",
        "ok": False,
        "status_code": 0,
        "title": "",
        "data_count": 0,
        "evidence": "",
        "error": "",
    }
    try:
        candidates = [
            "http://my.yingjiesheng.com/index.php/personal/jobsearch",
            "https://www.yingjiesheng.com/shanghai/",
            "https://www.yingjiesheng.com/",
        ]
        last_html = ""
        for url in candidates:
            response = page.goto(url, wait_until="domcontentloaded", timeout=45000)
            result["status_code"] = response.status if response else 0
            page.wait_for_timeout(2500)
            result["title"] = page.title()
            html = page.content()
            last_html = html
            links = page.evaluate(
                """() => {
                    const arr = Array.from(document.querySelectorAll("a[href]")).map(a => a.href).filter(Boolean);
                    return arr.slice(0, 300);
                }"""
            )
            job_like = [x for x in links if "job" in x.lower() or "zhiwei" in x.lower() or "yingjiesheng" in x.lower()]
            blocked = "Access Denied" in html or "forbidden" in html.lower() or "验证" in html
            if (not blocked) and (len(job_like) > 5 or "职位" in html or "招聘" in html):
                result["ok"] = True
                result["data_count"] = len(job_like)
                result["evidence"] = f"url={url} " + html[:260]
                return result
        result["evidence"] = (last_html or "")[:300]
        result["data_count"] = 0
    except Exception as e:
        result["error"] = str(e)
    return result


def main():
    out = {
        "summary": {"total": 2, "ok": 0, "failed": 0},
        "results": [],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled", "--no-sandbox"])
        context = browser.new_context(user_agent=UA, locale="zh-CN", timezone_id="Asia/Shanghai")
        add_cookies_from_env(context, "SHIXISENG_COOKIE", ".shixiseng.com")
        add_cookies_from_env(context, "YINGJIESHENG_COOKIE", ".yingjiesheng.com")
        page = context.new_page()
        result_sxs = test_shixiseng(page)
        out["results"].append(result_sxs)
        page2 = context.new_page()
        result_yjs = test_yingjiesheng(page2)
        out["results"].append(result_yjs)
        browser.close()
    ok_count = sum(1 for x in out["results"] if x.get("ok"))
    out["summary"]["ok"] = ok_count
    out["summary"]["failed"] = out["summary"]["total"] - ok_count
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "mvp_playwright_access_test.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(json.dumps(out, ensure_ascii=False))
    print(output_file)


if __name__ == "__main__":
    main()
