#!/usr/bin/env python3
"""测试数据加载"""

import csv
from pathlib import Path

# 加载CSV文件
shanghai_file = Path('c:/Users/Lenovo/projects/ResuMiner_main/release_data/internship_shanghai_latest.csv')

with open(shanghai_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    
print(f"总共 {len(rows)} 条数据")
print(f"\n前5条数据:")
for i, row in enumerate(rows[:5], 1):
    print(f"{i}. 公司: '{row.get('company', 'N/A')}', 岗位: '{row.get('name', 'N/A')}'")
    
# 检查是否有空的公司名
empty_company = [row for row in rows if not row.get('company', '').strip()]
print(f"\n公司名为空的数据: {len(empty_company)} 条")

# 统计各公司数量
from collections import Counter
companies = [row.get('company', '') for row in rows if row.get('company', '').strip()]
company_counts = Counter(companies)
print(f"\nTop 10 公司:")
for company, count in company_counts.most_common(10):
    print(f"  {company}: {count} 条")
