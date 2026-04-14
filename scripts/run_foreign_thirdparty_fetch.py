import datetime as dt
import json
import re
import time
from pathlib import Path

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[1]
OUT_RAW = ROOT / "data" / "raw"
OUT_RAW_51 = OUT_RAW / "51job"
OUT_RAW_LP = OUT_RAW / "liepin"
OUT_RELEASE = ROOT / "release_data"
RPC_BASE = "http://127.0.0.1:5600/invoke"


def fetch_job51(max_pages: int = 15):
    rows = []
    for page in range(1, max_pages + 1):
        payload = {
            "keyword": "实习",
            "pageNum": page,
            "jobArea": "020000",
            "pageSize": 20,
            "requestId": f"audit51_{page}",
        }
        try:
            obj = requests.post(
                f"{RPC_BASE}/job51/search_jobs",
                json=payload,
                timeout=90,
            ).json()
            result = obj.get("result") or {}
            result_body = result.get("resultbody") or {}
            items = ((result_body.get("job") or {}).get("items") or [])
            for it in items:
                job_id = it.get("jobId")
                rows.append(
                    {
                        "platform": "51job",
                        "job_id": job_id,
                        "job_name": it.get("jobName"),
                        "company_name": it.get("fullCompanyName") or it.get("customerName"),
                        "location": it.get("jobAreaString"),
                        "salary_text": it.get("provideSalaryString"),
                        "education": it.get("degreeString"),
                        "experience": it.get("workYearString"),
                        "url": it.get("jobHref")
                        or (f"https://jobs.51job.com/shanghai/{job_id}.html" if job_id else ""),
                        "publish_date": it.get("issueDateString"),
                        "source": "51job",
                        "raw": it,
                    }
                )
            print(f"job51_page={page} items={len(items)}")
        except Exception as e:
            print(f"job51_page={page} ERR={e}")
        time.sleep(0.8)
    return rows


def fetch_liepin(max_pages: int = 15):
    rows = []
    for page in range(1, max_pages + 1):
        payload = {"keyword": "实习", "pageNum": page, "city": "020", "pageSize": 20}
        try:
            obj = requests.post(
                f"{RPC_BASE}/liepin/search_jobs",
                json=payload,
                timeout=120,
            ).json()
            result = obj.get("result") or {}
            data = result.get("data") or {}
            items = data.get("jobCardList") or []
            for it in items:
                comp = it.get("comp") if isinstance(it.get("comp"), dict) else {}
                job = it.get("job") if isinstance(it.get("job"), dict) else {}
                dq = job.get("dq") if isinstance(job.get("dq"), dict) else {}
                job_id = job.get("jobId") or it.get("jobId")
                rows.append(
                    {
                        "platform": "liepin",
                        "job_id": job_id,
                        "job_name": job.get("title") or it.get("title"),
                        "company_name": comp.get("compName") or comp.get("name") or it.get("compName"),
                        "location": dq.get("name") if isinstance(dq, dict) else "",
                        "salary_text": job.get("salary") or "",
                        "education": job.get("requireEduLevel") or "",
                        "experience": job.get("requireWorkYears") or "",
                        "url": f"https://www.liepin.com/job/{job_id}.shtml" if job_id else "",
                        "publish_date": job.get("refreshTime") or "",
                        "source": "liepin",
                        "raw": it,
                    }
                )
            print(f"liepin_page={page} items={len(items)} method={result.get('method')}")
        except Exception as e:
            print(f"liepin_page={page} ERR={e}")
        time.sleep(1.2)
    return rows


def strict_foreign_filter(df: pd.DataFrame) -> pd.DataFrame:
    ban = (
        "字节|腾讯|快手|小红书|美团|阿里|京东|哔哩|"
        "bilibili|bytedance|tencent|kuaishou|xiaohongshu|meituan|alibaba|jingdong|jd\\.com"
    )
    df = df[~df["company_name"].astype(str).str.lower().str.contains(ban, regex=True, na=False)]
    loc = df["location"].astype(str).str.lower()
    title = df["job_name"].astype(str).str.lower()
    mask_sh = loc.str.contains("上海|shanghai", regex=True, na=False)
    mask_intern = title.str.contains(r"实习|intern", regex=True, na=False)
    df = df[mask_sh & mask_intern]

    foreign_names = [
        "microsoft",
        "google",
        "amazon",
        "apple",
        "oracle",
        "ibm",
        "sap",
        "salesforce",
        "adobe",
        "nvidia",
        "intel",
        "amd",
        "qualcomm",
        "cisco",
        "linkedin",
        "uber",
        "airbnb",
        "paypal",
        "stripe",
        "shopee",
        "shein",
        "tesla",
        "siemens",
        "bosch",
        "unilever",
        "p&g",
        "jpmorgan",
        "goldman",
        "morgan stanley",
        "deloitte",
        "pwc",
        "ey",
        "kpmg",
        "谷歌",
        "微软",
        "亚马逊",
        "苹果",
        "甲骨文",
        "英伟达",
        "英特尔",
        "高通",
        "思科",
        "领英",
        "优步",
        "爱彼迎",
        "贝宝",
        "西门子",
        "博世",
        "联合利华",
        "宝洁",
        "摩根",
        "高盛",
        "德勤",
        "普华永道",
        "安永",
        "毕马威",
        "泰科电子",
        "喜利得",
        "普立万",
        "麦格纳",
        "凯士比",
        "俄远东船务",
    ]
    pat = "|".join([re.escape(x) for x in foreign_names])
    fd = df[df["company_name"].astype(str).str.lower().str.contains(pat, regex=True, na=False)].copy()

    high = [
        "data analyst",
        "business analyst",
        "bi",
        "strategy",
        "analytics",
        "python",
        "sql",
        "machine learning",
        "数据分析",
        "商业分析",
        "策略",
        "算法",
    ]
    fd["jd_value_score"] = fd["job_name"].astype(str).str.lower().apply(
        lambda t: sum(8 for k in high if k in t)
    )
    return fd.sort_values("jd_value_score", ascending=False)


def main():
    OUT_RAW_51.mkdir(parents=True, exist_ok=True)
    OUT_RAW_LP.mkdir(parents=True, exist_ok=True)
    OUT_RELEASE.mkdir(parents=True, exist_ok=True)

    rows_51 = fetch_job51(max_pages=15)
    rows_lp = fetch_liepin(max_pages=15)
    all_rows = rows_51 + rows_lp

    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    f51 = OUT_RAW_51 / f"jobs_51job_{ts}.json"
    flp = OUT_RAW_LP / f"jobs_liepin_{ts}.json"
    with open(f51, "w", encoding="utf-8") as f:
        json.dump(rows_51, f, ensure_ascii=False)
    with open(flp, "w", encoding="utf-8") as f:
        json.dump(rows_lp, f, ensure_ascii=False)
    print(f"saved {f51} rows={len(rows_51)}")
    print(f"saved {flp} rows={len(rows_lp)}")

    df = pd.DataFrame(all_rows).fillna("")
    strict = strict_foreign_filter(df)
    out = OUT_RELEASE / "foreign_strict_shanghai_opportunities_latest.csv"
    strict.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"strict_foreign_count={len(strict)}")
    print(f"saved {out}")
    if not strict.empty:
        print(strict[["company_name", "job_name", "location", "platform"]].head(20).to_string(index=False))


if __name__ == "__main__":
    main()
