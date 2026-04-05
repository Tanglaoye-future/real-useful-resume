#!/usr/bin/env python3
"""
简历匹配 V2 - 基于新高价值筛选算法的匹配流程
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 设置项目路径
project_root = Path(__file__).parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

print("=" * 80)
print("🚀 ResuMiner 简历匹配 V2")
print("基于新高价值筛选算法（支持外企/独角兽/国企）")
print("=" * 80)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 1. 加载简历
print("📄 步骤1: 加载简历")
resume_paths = [
    'assets/resume/uploads/唐圣昕_简历.json',
    'resume_upload/resume.json',
    'project_package/resume/resume.json',
]

resume = None
for path in resume_paths:
    if Path(path).exists():
        print(f"   加载: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            resume = json.load(f)
        break

if not resume:
    print("❌ 未找到简历文件")
    sys.exit(1)

resume_name = resume.get('name', resume.get('basic_info', {}).get('name', '未知'))
print(f"   ✅ 简历: {resume_name}\n")

# 2. 加载高价值岗位数据（V2）
print("📊 步骤2: 加载高价值岗位数据（V2）")
processed_dir = Path('data/processed')
jobs = []

# 加载高价值岗位
high_value_files = list(processed_dir.glob('high_value_jobs_*.json'))
if high_value_files:
    latest = max(high_value_files, key=lambda p: p.stat().st_mtime)
    print(f"   高价值岗位: {latest.name}")
    with open(latest, 'r', encoding='utf-8') as f:
        high_jobs = json.load(f)
        jobs.extend(high_jobs)
        print(f"   ✅ 加载 {len(high_jobs)} 条")

# 加载中价值岗位
medium_value_files = list(processed_dir.glob('medium_value_jobs_*.json'))
if medium_value_files:
    latest = max(medium_value_files, key=lambda p: p.stat().st_mtime)
    print(f"   中价值岗位: {latest.name}")
    with open(latest, 'r', encoding='utf-8') as f:
        medium_jobs = json.load(f)
        jobs.extend(medium_jobs)
        print(f"   ✅ 加载 {len(medium_jobs)} 条")

print(f"\n📊 总计: {len(jobs)} 条岗位\n")

if not jobs:
    print("❌ 没有岗位数据")
    sys.exit(1)

# 3. 简单匹配（基于关键词和分数）
print("🎯 步骤3: 执行简历匹配")

# 提取简历关键词
resume_text = json.dumps(resume, ensure_ascii=False).lower()
resume_skills = []
if 'skills' in resume:
    resume_skills = [s.lower() for s in resume.get('skills', [])]

# 计算匹配分数
matches = []
for job in jobs:
    job_text = (
        str(job.get('job_name', '')) + ' ' +
        str(job.get('job_description', '')) + ' ' +
        str(job.get('requirements', ''))
    ).lower()
    
    # 基础匹配分（基于关键词重叠）
    match_score = 0
    
    # 技能匹配
    skill_matches = 0
    for skill in resume_skills:
        if skill in job_text:
            skill_matches += 1
    if resume_skills:
        match_score += (skill_matches / len(resume_skills)) * 40
    
    # 岗位名称匹配
    job_name = str(job.get('job_name', '')).lower()
    if '产品' in job_name and '产品' in resume_text:
        match_score += 20
    if '数据' in job_name and '数据' in resume_text:
        match_score += 20
    if '分析' in job_name and '分析' in resume_text:
        match_score += 10
    
    # 加上高价值分数的权重
    total_score = job.get('total_score', 0)
    final_score = match_score + (total_score * 0.3)  # 高价值分数占30%
    
    matches.append({
        'job': job,
        'match_score': min(final_score, 100),
        'keyword_score': match_score,
        'value_score': total_score
    })

# 排序
matches.sort(key=lambda x: x['match_score'], reverse=True)

print(f"   ✅ 匹配完成: {len(matches)} 个岗位\n")

# 4. 显示结果
print("=" * 80)
print("🏆 Top 15 推荐岗位（基于高价值筛选V2 + 简历匹配）")
print("=" * 80)

for i, match in enumerate(matches[:15], 1):
    job = match['job']
    details = job.get('score_details', {})
    company_info = details.get('company', {})
    
    company = job.get('company_name', 'Unknown')
    title = job.get('job_name', 'Unknown')
    match_score = match['match_score']
    total_score = job.get('total_score', 0)
    tier = company_info.get('tier', '?')
    company_type = company_info.get('type', '?')
    
    print(f"\n{i:2d}. [{tier}-{company_type}] {company}")
    print(f"    岗位: {title}")
    print(f"    综合匹配度: {match_score:.1f}% | 高价值评分: {total_score:.1f}")
    print(f"    薪资: {job.get('salary', 'N/A')} | 地点: {job.get('location', 'N/A')}")

# 5. 统计信息
print("\n" + "=" * 80)
print("📈 统计汇总")
print("=" * 80)

tier_stats = {}
company_types = {}
for match in matches[:20]:
    job = match['job']
    details = job.get('score_details', {})
    company_info = details.get('company', {})
    tier = company_info.get('tier', '未知')
    company_type = company_info.get('type', '未知')
    tier_stats[tier] = tier_stats.get(tier, 0) + 1
    company_types[company_type] = company_types.get(company_type, 0) + 1

print("\n公司分级分布:")
for tier, count in sorted(tier_stats.items(), key=lambda x: -x[1]):
    print(f"  - {tier}: {count} 个")

print("\n企业类型分布:")
for ctype, count in sorted(company_types.items(), key=lambda x: -x[1]):
    print(f"  - {ctype}: {count} 个")

# 6. 保存结果
print("\n💾 保存匹配结果...")
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_dir = Path('data/output/matcher')
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / f'match_report_v2_{timestamp}.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'timestamp': timestamp,
        'resume_name': resume_name,
        'total_jobs': len(jobs),
        'total_matches': len(matches),
        'matches': matches[:30]
    }, f, ensure_ascii=False, indent=2)

print(f"   ✅ 结果已保存: {output_file}")

print("\n" + "=" * 80)
print("✅ 简历匹配V2完成！")
print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
