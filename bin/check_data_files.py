#!/usr/bin/env python3
"""检查数据文件行数"""

import csv
from pathlib import Path

data_dir = Path('c:/Users/Lenovo/projects/ResuMiner_main/release_data')

print("="*80)
print("📂 检查官网数据文件")
print("="*80)

for csv_file in data_dir.glob('*.csv'):
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        rows = list(reader)
        print(f"{csv_file.name:50s} : {len(rows):>6,} 行")

print("\n" + "="*80)
print("📊 详细检查 internship_shanghai_latest.csv")
print("="*80)

shanghai_file = data_dir / 'internship_shanghai_latest.csv'
with open(shanghai_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    
print(f"总行数: {len(rows)}")

# 统计各公司数量
from collections import Counter
companies = [row.get('company', '').strip() for row in rows if row.get('company', '').strip()]
company_counts = Counter(companies)

print(f"\nTop 20 公司:")
for company, count in company_counts.most_common(20):
    print(f"  {company:20s}: {count:>4} 条")

print(f"\n公司总数: {len(company_counts)}")
