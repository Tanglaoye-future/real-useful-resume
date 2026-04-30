"""
Data job recommendations for a 大三 student interested in data roles.
Excludes over-exposed domestic mega-corps.
"""
import re
import pandas as pd

df = pd.read_parquet("data/unified/jobs.parquet")

# ── 1. Filter: data-related titles ───────────────────────────────────────────
DATA_KEYWORDS = re.compile(
    r"数据|data|analyst|分析|BI|bi|算法|机器学习|ML|AI|人工智能|"
    r"挖掘|统计|quantitative|quant|NLP|nlp|商业智能|产品分析|增长|growth|"
    r"risk.*analyst|风控|用研|研究员",
    re.IGNORECASE,
)
data_mask = df["title"].fillna("").str.contains(DATA_KEYWORDS)
data_df = df[data_mask].copy()
print(f"Data-related roles found: {len(data_df)}")

# ── 2. Exclude domestic mega-corps ───────────────────────────────────────────
MEGA = re.compile(
    r"阿里巴巴|alibaba|腾讯|tencent|字节跳动|bytedance|百度|baidu|"
    r"美团|meituan|京东|jd\.com|拼多多|快手|kuaishou|网易|netease|"
    r"滴滴|didi|华为|huawei|小米|xiaomi|oppo|vivo|微博|weibo|"
    r"哔哩哔哩|bilibili|得物|58同城|boss直聘|猎聘",
    re.IGNORECASE,
)
# Also exclude from platform tags (bytedance_crawler etc)
mega_company = data_df["company"].fillna("").str.contains(MEGA, case=False)
mega_platform = data_df["platform"].str.contains(r"bytedance|bilibili|kuaishou|meituan|jd", case=False)
data_df = data_df[~(mega_company | mega_platform)].copy()
print(f"After excluding mega-corps: {len(data_df)}")

# ── 3. Score each job ─────────────────────────────────────────────────────────
def score_job(row):
    score = 0
    title = (row["title"] or "").lower()
    jd    = (row["jd_text"] or "").lower()
    company = (row["company"] or "").lower()

    # JD length — proxy for effort / real role
    jd_len = len(jd)
    if jd_len > 500:  score += 3
    elif jd_len > 200: score += 2
    elif jd_len > 50:  score += 1

    # Has salary info
    if row.get("salary_raw") and str(row["salary_raw"]).strip():
        score += 2

    # Preferred role types for a 大三 data student
    good_titles = r"数据分析|data analyst|BI|商业分析|增长分析|产品分析|数据运营|数据挖掘|data science|研究助理|量化"
    if re.search(good_titles, title, re.I):
        score += 3

    # Interesting industry signals (finance, consulting, tech, research)
    good_industry = r"金融|咨询|科技|互联网|研究|医疗|教育|物流|供应链|零售|消费|游戏"
    if re.search(good_industry, company + jd, re.I):
        score += 1

    # Beginner-friendly signals in JD
    friendly = r"大三|大四|本科|应届|实习|在校|无需经验|不限经验"
    if re.search(friendly, jd, re.I):
        score += 1

    # Red flags — only want senior
    senior_flags = r"3年以上|5年|工作经验.*年|senior.*required"
    if re.search(senior_flags, jd, re.I):
        score -= 3

    # Has URL (linkable)
    if row.get("url") and str(row["url"]).strip():
        score += 1

    return score

data_df["score"] = data_df.apply(score_job, axis=1)

# ── 4. Dedupe by company+title (keep best scored) ────────────────────────────
data_df["dedup_key"] = (
    data_df["company"].fillna("").str.strip().str[:20] + "|" +
    data_df["title"].fillna("").str.strip().str[:20]
)
data_df = data_df.sort_values("score", ascending=False).drop_duplicates("dedup_key")

# ── 5. Top 20 ─────────────────────────────────────────────────────────────────
top = data_df.nlargest(20, "score")[
    ["title", "company", "city", "salary_raw", "platform", "score", "url", "jd_text"]
].reset_index(drop=True)

print("\n=== TOP 20 DATA ROLE RECOMMENDATIONS ===\n")
for i, row in top.iterrows():
    print(f"[{i+1:2d}] {row['title']}")
    print(f"     公司: {row['company']}  |  {row['city']}  |  薪资: {row['salary_raw'] or '未填写'}")
    print(f"     平台: {row['platform']}  |  评分: {row['score']}")
    if row["url"] and str(row["url"]).strip():
        print(f"     链接: {row['url']}")
    jd_preview = str(row["jd_text"] or "")[:200].replace("\n", " ")
    print(f"     JD摘要: {jd_preview}...")
    print()

# ── 6. Industry breakdown of top candidates ──────────────────────────────────
print("\n=== SCORE >= 5 的岗位行业分布 ===")
good = data_df[data_df["score"] >= 5]
print(f"总计 {len(good)} 个高质量数据岗")
print("\n公司 Top 20 (按评分):")
print(good.groupby("company")["score"].max().nlargest(20).to_string())
print("\n平台分布:")
print(good["platform"].value_counts().to_string())
