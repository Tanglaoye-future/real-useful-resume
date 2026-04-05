#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中小微企业匹配系统 - 完整落地实现
基于PRD文档的企业画像提取 + 企业-候选人适配匹配
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
print("🏢 ResuMiner 中小微企业匹配系统")
print("基于企业画像 + 人-企适配的智能匹配")
print("=" * 80)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 导入模块
from matcher.enterprise import EnterpriseProfiler, EnterpriseMatcher

# 1. 加载简历
print("📄 步骤1: 加载简历")
resume_paths = [
    'assets/resume/uploads/resume.json',
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
    # 使用示例简历
    print("   ⚠️ 未找到简历文件，使用示例简历")
    resume = {
        "name": "示例候选人",
        "basic_info": {
            "email": "example@email.com",
            "phone": "138xxxxxxxxx"
        },
        "skills": ["Python", "数据分析", "产品经理", "SQL"],
        "education": "本科",
        "past_industries": ["互联网/SaaS", "企业服务"],
        "past_company_scale": "中型",
        "total_work_year": 2.5,
        "job_demand": "求成长",
        "target_work_mode": "弹性工作制",
        "target_city": "上海",
        "target_salary": "15-25",
        "core_skills": "Python、数据分析、产品经理",
        "core_projects": [
            "负责数据分析平台开发，支撑10万用户",
            "参与产品功能设计，提升用户留存20%"
        ]
    }

resume_name = resume.get('name', resume.get('basic_info', {}).get('name', '未知'))
print(f"   ✅ 简历: {resume_name}")
print(f"   求职诉求: {resume.get('job_demand', '未指定')}")
print(f"   期望工作模式: {resume.get('target_work_mode', '未指定')}")
print(f"   过往行业: {', '.join(resume.get('past_industries', []))}\n")

# 2. 加载岗位数据
print("📊 步骤2: 加载岗位数据")
processed_dir = Path('data/processed')
jobs = []

# 加载高价值和中价值岗位
for pattern in ['high_value_jobs_*.json', 'medium_value_jobs_*.json']:
    files = list(processed_dir.glob(pattern))
    if files:
        latest = max(files, key=lambda p: p.stat().st_mtime)
        with open(latest, 'r', encoding='utf-8') as f:
            data = json.load(f)
            jobs.extend(data)
            print(f"   ✅ 加载 {len(data)} 条岗位 from {latest.name}")

# 如果没有处理后的数据，尝试加载原始数据
if not jobs:
    raw_files = list(Path('data/raw').glob('*.json'))
    for f in raw_files[:1]:  # 只加载第一个
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
            if isinstance(data, list):
                jobs = data
            elif isinstance(data, dict) and 'jobs' in data:
                jobs = data['jobs']
        print(f"   ✅ 加载 {len(jobs)} 条原始岗位")

if not jobs:
    # 使用示例数据
    print("   ⚠️ 未找到岗位数据，使用示例数据")
    jobs = [
        {
            "company_name": "杭州XX科技有限公司",
            "job_name": "产品经理",
            "job_description": "杭州XX科技有限公司成立于2020年，是一家专注于HR SaaS服务的初创企业。团队规模30人，已获得A轮融资。主营产品：智能招聘系统、简历匹配平台。企业文化：扁平化、弹性工作制、创业氛围。",
            "requirements": "本科及以上学历，2年以上产品经验，熟悉HR行业优先",
            "salary": "15-25K",
            "location": "上海",
        },
        {
            "company_name": "上海YY网络科技有限公司",
            "job_name": "数据分析师",
            "job_description": "上海YY网络科技成立于2018年，专注电商数据分析，团队规模80人，B轮融资。企业文化：技术驱动、结果导向。",
            "requirements": "本科及以上学历，数据分析经验，熟练使用SQL和Python",
            "salary": "18-28K",
            "location": "上海",
        },
        {
            "company_name": "北京ZZ人工智能有限公司",
            "job_name": "AI产品经理",
            "job_description": "北京ZZ人工智能成立于2019年，专注AI大模型应用，团队规模50人，A+轮融资。企业文化：技术驱动、扁平化。",
            "requirements": "本科及以上学历，AI产品经验，熟悉大模型技术",
            "salary": "20-35K",
            "location": "北京",
        },
        {
            "company_name": "深圳WW电子商务有限公司",
            "job_name": "电商运营",
            "job_description": "深圳WW电子商务成立于2015年，跨境电商企业，团队规模200人，C轮融资。企业文化：狼性文化、结果导向。",
            "requirements": "本科及以上学历，电商运营经验",
            "salary": "12-20K",
            "location": "深圳",
        },
        {
            "company_name": "杭州MM教育科技有限公司",
            "job_name": "教育产品经理",
            "job_description": "杭州MM教育科技成立于2021年，在线教育SaaS，团队规模20人，天使轮。企业文化：创业氛围、弹性工作。",
            "requirements": "本科及以上学历，教育行业经验",
            "salary": "10-18K",
            "location": "杭州",
        }
    ]

print(f"\n📊 总计: {len(jobs)} 条岗位\n")

# 3. 提取企业画像
print("🏢 步骤3: 提取企业画像")
profiler = EnterpriseProfiler()
enterprises = {}

for job in jobs:
    company_name = job.get('company_name', '')
    if not company_name or company_name in enterprises:
        continue
    
    jd_text = str(job.get('job_description', '')) + ' ' + str(job.get('requirements', ''))
    profile = profiler.extract_from_jd(jd_text, company_name)
    enterprises[company_name] = profile

print(f"   ✅ 提取 {len(enterprises)} 家企业画像\n")

# 显示企业画像示例
print("   企业画像示例（前3家）：")
for i, (name, profile) in enumerate(list(enterprises.items())[:3], 1):
    print(f"   {i}. {name}")
    print(f"      行业: {profile.gb_industry} / {profile.segment}")
    print(f"      规模: {profile.scale} | 阶段: {profile.development_stage}")
    print(f"      文化: {profile.culture}")
print()

# 4. 企业-候选人适配匹配
print("🎯 步骤4: 企业-候选人适配匹配")
matcher = EnterpriseMatcher()

# 为每个岗位计算适配度
matches = []
for job in jobs:
    company_name = job.get('company_name', '')
    if company_name not in enterprises:
        continue
    
    enterprise = enterprises[company_name]
    match_result = matcher.match(resume, enterprise)
    
    matches.append({
        'job': job,
        'enterprise': enterprise,
        'match_result': match_result,
        'total_score': match_result.total_score
    })

# 排序
matches.sort(key=lambda x: x['total_score'], reverse=True)

print(f"   ✅ 完成 {len(matches)} 个岗位的适配匹配\n")

# 5. 显示匹配结果
print("=" * 80)
print("🏆 Top 10 中小微企业推荐（基于人-企适配）")
print("=" * 80)

for i, match in enumerate(matches[:10], 1):
    job = match['job']
    enterprise = match['enterprise']
    result = match['match_result']
    
    company = job.get('company_name', 'Unknown')
    title = job.get('job_name', 'Unknown')
    score = result.total_score
    level = matcher.get_match_level(score)
    
    print(f"\n{i:2d}. [{level}] {company}")
    print(f"    岗位: {title}")
    print(f"    适配得分: {score:.1f}")
    print(f"    行业匹配: {result.industry_match_score:.0f}分 - {result.industry_reason}")
    print(f"    规模匹配: {result.scale_match_score:.0f}分 - {result.scale_reason}")
    print(f"    阶段匹配: {result.stage_match_score:.0f}分 - {result.stage_reason}")
    print(f"    文化匹配: {result.culture_match_score:.0f}分 - {result.culture_reason}")
    print(f"    企业信息: {enterprise.scale} | {enterprise.development_stage} | {enterprise.segment}")

# 6. 统计汇总
print("\n" + "=" * 80)
print("📈 统计汇总")
print("=" * 80)

level_stats = {"强适配": 0, "中适配": 0, "弱适配": 0}
scale_stats = {}
stage_stats = {}

for match in matches:
    result = match['match_result']
    enterprise = match['enterprise']
    
    level = matcher.get_match_level(result.total_score)
    level_stats[level] = level_stats.get(level, 0) + 1
    
    scale = enterprise.scale if enterprise.scale else "未知"
    scale_stats[scale] = scale_stats.get(scale, 0) + 1
    
    stage = enterprise.development_stage if enterprise.development_stage else "未知"
    stage_stats[stage] = stage_stats.get(stage, 0) + 1

print("\n适配等级分布:")
for level, count in sorted(level_stats.items(), key=lambda x: -x[1]):
    print(f"  - {level}: {count} 个")

print("\n企业规模分布:")
for scale, count in sorted(scale_stats.items(), key=lambda x: -x[1]):
    print(f"  - {scale}: {count} 个")

print("\n发展阶段分布:")
for stage, count in sorted(stage_stats.items(), key=lambda x: -x[1]):
    print(f"  - {stage}: {count} 个")

# 7. 保存结果
print("\n💾 保存匹配结果...")
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_dir = Path('data/output/enterprise')
output_dir.mkdir(parents=True, exist_ok=True)

# 保存详细结果
output_file = output_dir / f'sme_match_report_{timestamp}.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'timestamp': timestamp,
        'resume_name': resume_name,
        'total_jobs': len(jobs),
        'total_enterprises': len(enterprises),
        'matches': [
            {
                'job_name': m['job'].get('job_name'),
                'company_name': m['job'].get('company_name'),
                'total_score': m['total_score'],
                'match_level': matcher.get_match_level(m['total_score']),
                'enterprise_profile': m['enterprise'].to_dict(),
                'match_details': m['match_result'].to_dict()
            }
            for m in matches[:20]
        ],
        'statistics': {
            'level_distribution': level_stats,
            'scale_distribution': scale_stats,
            'stage_distribution': stage_stats
        }
    }, f, ensure_ascii=False, indent=2)

print(f"   ✅ 结果已保存: {output_file}")

# 生成Markdown报告
report_file = output_dir / f'sme_match_report_{timestamp}.md'
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(f"# 中小微企业匹配报告\n\n")
    f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write(f"**候选人**: {resume_name}\n\n")
    f.write(f"**求职诉求**: {resume.get('job_demand', '未指定')}\n\n")
    f.write("---\n\n")
    
    f.write("## Top 10 推荐岗位\n\n")
    for i, match in enumerate(matches[:10], 1):
        job = match['job']
        enterprise = match['enterprise']
        result = match['match_result']
        
        f.write(f"### {i}. {job.get('company_name', 'Unknown')}\n\n")
        f.write(f"- **岗位**: {job.get('job_name', 'Unknown')}\n")
        f.write(f"- **适配等级**: {matcher.get_match_level(result.total_score)}\n")
        f.write(f"- **总得分**: {result.total_score:.1f}\n\n")
        f.write(f"**企业画像**:\n")
        f.write(f"- 行业: {enterprise.gb_industry} / {enterprise.segment}\n")
        f.write(f"- 规模: {enterprise.scale}\n")
        f.write(f"- 发展阶段: {enterprise.development_stage}\n")
        f.write(f"- 企业文化: {enterprise.culture}\n\n")
        f.write(f"**匹配详情**:\n")
        f.write(f"- 行业适配: {result.industry_match_score:.0f}分 - {result.industry_reason}\n")
        f.write(f"- 规模适配: {result.scale_match_score:.0f}分 - {result.scale_reason}\n")
        f.write(f"- 阶段适配: {result.stage_match_score:.0f}分 - {result.stage_reason}\n")
        f.write(f"- 文化适配: {result.culture_match_score:.0f}分 - {result.culture_reason}\n\n")
        f.write("---\n\n")
    
    f.write("## 统计汇总\n\n")
    f.write("### 适配等级分布\n\n")
    for level, count in sorted(level_stats.items(), key=lambda x: -x[1]):
        f.write(f"- {level}: {count} 个\n")
    
    f.write("\n### 企业规模分布\n\n")
    for scale, count in sorted(scale_stats.items(), key=lambda x: -x[1]):
        f.write(f"- {scale}: {count} 个\n")
    
    f.write("\n### 发展阶段分布\n\n")
    for stage, count in sorted(stage_stats.items(), key=lambda x: -x[1]):
        f.write(f"- {stage}: {count} 个\n")

print(f"   ✅ 报告已保存: {report_file}")

print("\n" + "=" * 80)
print("✅ 中小微企业匹配完成！")
print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
