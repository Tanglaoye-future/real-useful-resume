#!/usr/bin/env python3
"""检查CDP数据"""

import json
from pathlib import Path
from collections import Counter

cdp_dir = Path('c:/Users/Lenovo/projects/ResuMiner_main/cdp_data')

print("="*80)
print("📂 检查 CDP 数据")
print("="*80)

total = 0
all_jobs = []

for json_file in cdp_dir.glob('*.json'):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if isinstance(data, list):
            jobs = data
        elif isinstance(data, dict):
            jobs = data.get('jobs', [])
        else:
            jobs = []
        
        company = json_file.stem
        print(f"{company:20s}: {len(jobs):>5,} 条")
        total += len(jobs)
        all_jobs.extend(jobs)

print(f"\n{'总计':20s}: {total:>5,} 条")

# 统计公司分布
if all_jobs:
    print("\n" + "="*80)
    print("📊 公司分布")
    print("="*80)
    
    companies = []
    for job in all_jobs:
        if isinstance(job, dict):
            company = job.get('company_name', '') or job.get('company', '') or job.get('org', '')
            if company:
                companies.append(company)
    
    counter = Counter(companies)
    for company, count in counter.most_common(20):
        print(f"  {company:20s}: {count:>5} 条")
