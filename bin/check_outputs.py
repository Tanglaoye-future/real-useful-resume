#!/usr/bin/env python3
"""检查outputs/raw目录中的数据"""

import csv
from pathlib import Path
from collections import Counter

outputs_dir = Path('c:/Users/Lenovo/projects/ResuMiner_main/outputs/raw')

print("="*80)
print("📂 检查 outputs/raw 目录")
print("="*80)

total = 0
all_jobs = []

for csv_file in outputs_dir.glob('*_official_raw.csv'):
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        company = csv_file.name.replace('_official_raw.csv', '')
        print(f"{company:20s}: {len(rows):>5,} 条")
        total += len(rows)
        all_jobs.extend(rows)

print(f"\n{'总计':20s}: {total:>5,} 条")

# 统计公司分布
print("\n" + "="*80)
print("📊 公司分布")
print("="*80)

companies = [row.get('company_name', '').strip() or row.get('company', '').strip() for row in all_jobs]
companies = [c for c in companies if c]
counter = Counter(companies)

for company, count in counter.most_common(20):
    print(f"  {company:20s}: {count:>5} 条")
