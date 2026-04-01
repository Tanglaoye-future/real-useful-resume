#!/usr/bin/env python3
"""检查official_jobs_raw_latest.csv"""

import csv
from pathlib import Path
from collections import Counter

csv_file = Path('c:/Users/Lenovo/projects/ResuMiner_main/release_data/official_jobs_raw_latest.csv')

print("="*80)
print("📂 检查 official_jobs_raw_latest.csv")
print("="*80)

with open(csv_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"总行数: {len(rows)}")

# 显示列名
print(f"\n列名: {list(rows[0].keys()) if rows else []}")

# 统计公司分布
companies = [row.get('company_name', '').strip() or row.get('company', '').strip() for row in rows]
companies = [c for c in companies if c]
counter = Counter(companies)

print(f"\n公司分布:")
for company, count in counter.most_common(20):
    print(f"  {company:20s}: {count:>5} 条")

print(f"\n公司总数: {len(counter)}")

# 显示前5条数据
print(f"\n前5条数据示例:")
for i, row in enumerate(rows[:5], 1):
    company = row.get('company_name', '') or row.get('company', '')
    job_name = row.get('job_name', '') or row.get('name', '')
    print(f"  {i}. {company} - {job_name}")
