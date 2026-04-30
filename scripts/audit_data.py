"""Quick data quality audit for jobs.parquet."""
import pathlib
import pandas as pd

df = pd.read_parquet("data/unified/jobs.parquet")

print("=== BASIC STATS ===")
print(f"Total rows : {len(df)}")
print(f"Columns    : {list(df.columns)}")
print()

print("=== PLATFORM BREAKDOWN ===")
print(df["platform"].value_counts().to_string())
print()

print("=== DATE RANGE ===")
if "publish_date" in df.columns:
    dates = df["publish_date"].dropna()
    dates = dates[dates != ""]
    print(f"  non-null: {len(dates)}/{len(df)}")
    if len(dates):
        print(f"  earliest: {sorted(dates)[:3]}")
        print(f"  latest  : {sorted(dates)[-3:]}")
print()

print("=== NULL / EMPTY RATES ===")
key_cols = ["title", "company", "city", "jd_text", "salary_raw",
            "education_req", "publish_date", "url", "source_job_id"]
for col in key_cols:
    if col not in df.columns:
        print(f"  {col:25s} MISSING")
        continue
    null = df[col].isna().sum()
    empty = (df[col].fillna("").astype(str).str.strip() == "").sum()
    rate = 100.0 * empty / len(df)
    print(f"  {col:25s} empty={empty:5d}  ({rate:5.1f}%)")
print()

print("=== JD TEXT QUALITY ===")
jd = df["jd_text"].fillna("").astype(str)
print(f"  avg length  : {jd.str.len().mean():.0f} chars")
print(f"  median      : {jd.str.len().median():.0f} chars")
print(f"  >50 chars   : {(jd.str.len() > 50).sum()} / {len(df)}")
print(f"  >200 chars  : {(jd.str.len() > 200).sum()} / {len(df)}")
print()

print("=== PER-PLATFORM JD QUALITY ===")
for plat, grp in df.groupby("platform"):
    jd_grp = grp["jd_text"].fillna("").astype(str)
    ok = (jd_grp.str.len() > 50).sum()
    print(f"  {plat:30s} rows={len(grp):5d}  jd_ok={ok:5d}  ({100*ok/len(grp):.0f}%)")
print()

print("=== SHIXISENG SAMPLES ===")
sxs = df[df["platform"] == "shixiseng"].head(3)
for i, (_, r) in enumerate(sxs.iterrows()):
    title = str(r.get("title", ""))[:45]
    company = str(r.get("company", ""))[:30]
    salary = str(r.get("salary_raw", ""))[:25]
    jd_len = len(str(r.get("jd_text", "")))
    print(f"  [{i+1}] {title}")
    print(f"      company={company}  salary={salary}  jd_len={jd_len}")

print()
print("=== YINGJIESHENG SAMPLES ===")
yjg = df[df["platform"] == "yingjiesheng"].head(3)
for i, (_, r) in enumerate(yjg.iterrows()):
    title = str(r.get("title", ""))[:45]
    company = str(r.get("company", ""))[:30]
    salary = str(r.get("salary_raw", ""))[:25]
    jd_len = len(str(r.get("jd_text", "")))
    print(f"  [{i+1}] {title}")
    print(f"      company={company}  salary={salary}  jd_len={jd_len}")

print()
print("=== LIEPIN SAMPLES ===")
lp = df[df["platform"] == "liepin"].head(3)
for i, (_, r) in enumerate(lp.iterrows()):
    title = str(r.get("title", ""))[:45]
    company = str(r.get("company", ""))[:30]
    salary = str(r.get("salary_raw", ""))[:25]
    jd_len = len(str(r.get("jd_text", "")))
    print(f"  [{i+1}] {title}")
    print(f"      company={company}  salary={salary}  jd_len={jd_len}")
