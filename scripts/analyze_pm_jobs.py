"""Product manager / product intern job recommendations for 大三 student."""
import re
import pandas as pd

df = pd.read_parquet("data/unified/jobs.parquet")

PRODUCT_KW = re.compile(
    r"产品|product\s*manager|产品经理|产品助理|产品运营|产品策略|"
    r"产品研究|用研|UX|用户体验|交互设计|增长产品|商业产品|"
    r"产品实习|product intern|PM实习",
    re.IGNORECASE,
)
pm_df = df[df["title"].fillna("").str.contains(PRODUCT_KW)].copy()
print(f"Product roles found: {len(pm_df)}")

MEGA = re.compile(
    r"阿里巴巴|alibaba|腾讯|tencent|字节跳动|bytedance|百度|baidu|"
    r"美团|meituan|京东|jd\.com|拼多多|快手|kuaishou|网易|netease|"
    r"滴滴|didi|华为|huawei|小米|xiaomi|oppo|vivo|微博|weibo|"
    r"哔哩哔哩|bilibili|58同城|boss直聘|猎聘",
    re.IGNORECASE,
)
mega_co = pm_df["company"].fillna("").str.contains(MEGA, case=False)
mega_pl = pm_df["platform"].str.contains(r"bytedance|bilibili|kuaishou|meituan|jd", case=False)
pm_df = pm_df[~(mega_co | mega_pl)].copy()
print(f"After excluding mega-corps: {len(pm_df)}")


def score_pm(row):
    s = 0
    title = (row["title"] or "").lower()
    jd    = (row["jd_text"] or "").lower()
    jd_len = len(jd)
    if jd_len > 500:   s += 3
    elif jd_len > 200: s += 2
    elif jd_len > 50:  s += 1

    if row.get("salary_raw") and str(row["salary_raw"]).strip():
        s += 2

    # Core PM intern titles
    if re.search(r"产品经理实习|pm实习|产品实习|product.*intern|产品助理", title, re.I):
        s += 3
    elif re.search(r"产品经理|product manager", title, re.I):
        s += 2

    # Interesting verticals for a 大三 student
    if re.search(r"增长|to\s*b|saas|出海|国际化|金融|医疗|教育|工业|硬件|汽车|电商|消费", jd + " " + title, re.I):
        s += 1

    # Beginner-friendly language
    if re.search(r"大三|大四|本科|应届|实习|在校|不限经验|无需经验", jd, re.I):
        s += 1

    # Senior / director penalty
    if re.search(r"总监|3年以上|5年以上|8年|高级产品经理|资深产品|senior\s+pm", jd + " " + title, re.I):
        s -= 3

    # Has direct URL
    if row.get("url") and str(row["url"]).strip():
        s += 1

    return s


pm_df["score"] = pm_df.apply(score_pm, axis=1)
pm_df["dedup_key"] = (
    pm_df["company"].fillna("").str.strip().str[:20] + "|" +
    pm_df["title"].fillna("").str.strip().str[:20]
)
pm_df = pm_df.sort_values("score", ascending=False).drop_duplicates("dedup_key")

top = pm_df.nlargest(25, "score")[
    ["title", "company", "city", "salary_raw", "platform", "score", "url", "jd_text"]
].reset_index(drop=True)

print("\n=== TOP PRODUCT ROLE RECOMMENDATIONS ===\n")
for i, row in top.iterrows():
    title   = row["title"]
    company = row["company"]
    salary  = row["salary_raw"] or "未填写"
    plat    = row["platform"]
    sc      = row["score"]
    url     = str(row["url"] or "").strip()
    jd_p    = str(row["jd_text"] or "")[:220].replace("\n", " ")
    print(f"[{i+1:2d}] score={sc}  {title}")
    print(f"     公司: {company}  |  薪资: {salary}  |  {plat}")
    if url:
        print(f"     链接: {url}")
    print(f"     JD: {jd_p}")
    print()

good = pm_df[pm_df["score"] >= 5]
print(f"\n=== score>=5 共 {len(good)} 个产品岗 ===")
print("\n公司分布 Top 15:")
print(good["company"].value_counts().head(15).to_string())
print("\n平台分布:")
print(good["platform"].value_counts().to_string())
