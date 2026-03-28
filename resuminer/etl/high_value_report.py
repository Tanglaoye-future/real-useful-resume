from __future__ import annotations

from pathlib import Path
import os

import pandas as pd

from etl.value_scoring import score_row


def run() -> int:
    preferred = Path(os.getenv("HIGH_VALUE_SOURCE", "output/shanghai_intern_jobs.csv"))
    excel_src = Path("output/jobs_latest.xlsx")
    csv_src = Path("output/shanghai_intern_jobs.csv")
    src = preferred if preferred.exists() else (excel_src if excel_src.exists() else csv_src)
    if not src.exists():
        print("missing source:", str(src))
        return 1
    if src.suffix.lower() == ".xlsx":
        df = pd.read_excel(src, sheet_name="ALL")
    else:
        df = pd.read_csv(src, encoding="utf-8-sig")

    if "publish_time" not in df.columns and "publish_date" in df.columns:
        df["publish_time"] = df["publish_date"]
    if "platform" in df.columns and "source_platform" not in df.columns:
        df["source_platform"] = df["platform"]
    if "job_type" in df.columns and "recruit_type" not in df.columns:
        df["recruit_type"] = df["job_type"]
    if "job_description" not in df.columns and "jd_content" in df.columns:
        df["job_description"] = df["jd_content"]
    if "job_requirement" not in df.columns:
        df["job_requirement"] = ""
    if "financing_round" not in df.columns and "company_stage" in df.columns:
        df["financing_round"] = df["company_stage"]
    if "welfare_tag" not in df.columns and "welfare_tags" in df.columns:
        df["welfare_tag"] = df["welfare_tags"]
    if "unique_id" not in df.columns:
        df["unique_id"] = df.get("jd_url", "").astype(str) + "|" + df.get("job_name", "").astype(str)

    rows = df.to_dict(orient="records")
    scores = []
    reasons = []
    for r in rows:
        s, rs = score_row({k: ("" if pd.isna(v) else str(v)) for k, v in r.items()})
        scores.append(s)
        reasons.append(" | ".join(rs[:8]))

    df["value_score"] = scores
    df["score_reasons"] = reasons
    df = df.sort_values(["value_score", "publish_time"], ascending=[False, False])

    top_jobs = df.head(200).copy()
    group_cols = ["company_name"]
    if "company_level" in df.columns:
        group_cols.append("company_level")
    if "platform" in df.columns:
        group_cols.append("platform")
    company_summary = (
        df.groupby(group_cols, dropna=False)
        .agg(
            jobs_count=("unique_id", "count"),
            avg_score=("value_score", "mean"),
            max_score=("value_score", "max"),
            latest_publish=("publish_time", "max"),
        )
        .reset_index()
        .sort_values(["avg_score", "jobs_count"], ascending=[False, False])
    )

    out = Path("output/high_value_jobs_topN.xlsx")
    with pd.ExcelWriter(out, engine="openpyxl") as w:
        top_jobs.to_excel(w, index=False, sheet_name="top_jobs")
        company_summary.to_excel(w, index=False, sheet_name="company_summary")

    top_jobs.to_csv("output/high_value_jobs_topN.csv", index=False, encoding="utf-8-sig")
    company_summary.to_csv("output/company_value_summary.csv", index=False, encoding="utf-8-sig")

    print("done:", str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
