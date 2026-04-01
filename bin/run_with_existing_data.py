#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ResuMiner 基于现有数据运行匹配
使用已有的爬取数据进行简历匹配
"""

import os
import sys
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
import logging
log_dir = project_root / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f'match_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_official_jobs() -> List[Dict]:
    """加载官网爬虫数据 - 从多个来源合并"""
    logger.info("="*80)
    logger.info("📂 加载官网爬虫数据")
    logger.info("="*80)
    
    all_jobs = []
    
    # 支持Docker环境和本地环境
    # Docker环境中数据挂载到 /app/external_data
    docker_data_dir = Path('/app/external_data')
    docker_raw_dir = Path('/app/external_raw')
    
    # 本地环境路径
    local_data_dir = Path('c:/Users/Lenovo/projects/ResuMiner_main/release_data')
    local_outputs_dir = Path('c:/Users/Lenovo/projects/ResuMiner_main/outputs/raw')
    
    # 优先使用Docker路径
    if docker_data_dir.exists():
        main_data_dir = docker_data_dir
        outputs_dir = docker_raw_dir
        logger.info("🐳 使用Docker环境数据路径")
    else:
        main_data_dir = local_data_dir
        outputs_dir = local_outputs_dir
        logger.info("💻 使用本地环境数据路径")
    
    # 1. 加载 official_jobs_raw_latest.csv (最完整的原始数据)
    raw_file = main_data_dir / 'official_jobs_raw_latest.csv'
    if raw_file.exists():
        logger.info(f"📄 找到原始数据: {raw_file}")
        try:
            jobs = []
            with open(raw_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    job = {
                        'source_job_id': row.get('external_job_id', '') or row.get('url', ''),
                        'job_name': row.get('name', ''),
                        'company_name': row.get('company', ''),
                        'location': row.get('city', '上海'),
                        'city': row.get('city', '上海'),
                        'salary': row.get('salary', ''),
                        'job_description': row.get('jd_raw', ''),
                        'job_requirement': '',
                        'experience_requirement': row.get('duration', ''),
                        'education_requirement': row.get('academic', ''),
                        'source': 'official_raw',
                        'platform': row.get('source', 'official'),
                        'crawled_at': row.get('collect_time', datetime.now().isoformat()),
                    }
                    jobs.append(job)
            logger.info(f"✅ 加载 {len(jobs)} 条官网原始岗位")
            all_jobs.extend(jobs)
        except Exception as e:
            logger.error(f"❌ 加载失败: {e}")
    
    # 2. 加载 internship_shanghai_latest.csv (处理过的数据)
    shanghai_file = main_data_dir / 'internship_shanghai_latest.csv'
    if shanghai_file.exists():
        logger.info(f"📄 找到上海实习数据: {shanghai_file}")
        try:
            jobs = []
            with open(shanghai_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    job = {
                        'source_job_id': row.get('url', ''),
                        'job_name': row.get('name', ''),
                        'company_name': row.get('company', ''),
                        'location': row.get('city', '上海'),
                        'city': row.get('city', '上海'),
                        'salary': '',
                        'job_description': row.get('jd_raw', ''),
                        'job_requirement': '',
                        'experience_requirement': '',
                        'education_requirement': '',
                        'source': 'official_shanghai',
                        'platform': row.get('source', 'official'),
                        'crawled_at': datetime.now().isoformat(),
                    }
                    jobs.append(job)
            logger.info(f"✅ 加载 {len(jobs)} 条上海实习岗位")
            all_jobs.extend(jobs)
        except Exception as e:
            logger.error(f"❌ 加载失败: {e}")
    
    # 3. 加载 outputs/raw 目录的数据
    if outputs_dir.exists():
        logger.info(f"📄 检查 outputs/raw 目录")
        for csv_file in outputs_dir.glob('*_official_raw.csv'):
            try:
                jobs = []
                with open(csv_file, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    company_name = csv_file.stem.replace('_official_raw', '')
                    for row in reader:
                        job = {
                            'source_job_id': row.get('job_id', '') or row.get('url', ''),
                            'job_name': row.get('job_name', '') or row.get('name', ''),
                            'company_name': row.get('company_name', '') or row.get('company', company_name),
                            'location': row.get('location', '上海'),
                            'city': row.get('city', '上海'),
                            'salary': row.get('salary', ''),
                            'job_description': row.get('job_description', '') or row.get('jd_raw', ''),
                            'job_requirement': row.get('job_requirement', ''),
                            'experience_requirement': row.get('experience_requirement', ''),
                            'education_requirement': row.get('education_requirement', ''),
                            'source': 'official_outputs',
                            'platform': company_name,
                            'crawled_at': datetime.now().isoformat(),
                        }
                        jobs.append(job)
                if jobs:
                    logger.info(f"✅ 加载 {len(jobs)} 条 {company_name} 岗位")
                    all_jobs.extend(jobs)
            except Exception as e:
                logger.error(f"❌ 加载 {csv_file.name} 失败: {e}")
    
    logger.info(f"\n📊 官网数据总计: {len(all_jobs)} 条")
    
    if not all_jobs:
        logger.warning("⚠️ 未找到官网数据文件")
    
    return all_jobs


def load_third_party_jobs() -> List[Dict]:
    """加载第三方平台数据"""
    logger.info("\n" + "="*80)
    logger.info("📂 加载第三方平台数据")
    logger.info("="*80)
    
    jobs = []
    
    # 尝试从本地ResuMiner加载数据
    base_dir = Path('c:/Users/Lenovo/projects/ResuMiner/data/output')
    
    # 加载51job数据
    job51_dir = base_dir / 'job51'
    if job51_dir.exists():
        json_files = list(job51_dir.glob('*_data_*.json'))
        if json_files:
            latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
            logger.info(f"📄 找到51job数据: {latest_file}")
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for job in data:
                            job['platform'] = '51job'
                            job['source'] = 'third_party'
                        jobs.extend(data)
                    elif isinstance(data, dict) and 'jobs' in data:
                        for job in data['jobs']:
                            job['platform'] = '51job'
                            job['source'] = 'third_party'
                        jobs.extend(data['jobs'])
                logger.info(f"✅ 加载 {len(jobs)} 条51job岗位")
            except Exception as e:
                logger.error(f"❌ 加载51job失败: {e}")
    
    # 加载猎聘数据
    liepin_dir = base_dir / 'liepin'
    if liepin_dir.exists():
        json_files = list(liepin_dir.glob('*_data_*.json'))
        if json_files:
            latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
            logger.info(f"📄 找到猎聘数据: {latest_file}")
            try:
                liepin_jobs = []
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for job in data:
                            job['platform'] = 'liepin'
                            job['source'] = 'third_party'
                        liepin_jobs = data
                    elif isinstance(data, dict) and 'jobs' in data:
                        for job in data['jobs']:
                            job['platform'] = 'liepin'
                            job['source'] = 'third_party'
                        liepin_jobs = data['jobs']
                jobs.extend(liepin_jobs)
                logger.info(f"✅ 加载 {len(liepin_jobs)} 条猎聘岗位")
            except Exception as e:
                logger.error(f"❌ 加载猎聘失败: {e}")
    
    if not jobs:
        logger.warning("⚠️ 未找到第三方平台数据文件")
    else:
        logger.info(f"✅ 第三方平台共加载 {len(jobs)} 条岗位")
    
    return jobs


def merge_and_deduplicate(jobs1: List[Dict], jobs2: List[Dict]) -> List[Dict]:
    """合并并去重"""
    logger.info("\n" + "="*80)
    logger.info("🔄 合并数据并去重")
    logger.info("="*80)
    
    all_jobs = jobs1 + jobs2
    logger.info(f"合并前: {len(jobs1)} + {len(jobs2)} = {len(all_jobs)} 条")
    
    # 去重：基于公司名+岗位名
    seen = set()
    unique_jobs = []
    
    for job in all_jobs:
        key = f"{job.get('company_name', '')}_{job.get('job_name', '')}"
        if key and key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    logger.info(f"去重后: {len(unique_jobs)} 条 (去重 {len(all_jobs) - len(unique_jobs)} 条)")
    
    # 添加上海地点硬性过滤
    logger.info("\n" + "="*80)
    logger.info("🎯 硬性条件过滤：仅保留上海岗位")
    logger.info("="*80)
    
    shanghai_jobs = []
    for job in unique_jobs:
        location = job.get('location', '') or job.get('city', '')
        # 检查是否包含上海
        if location and '上海' in str(location):
            shanghai_jobs.append(job)
    
    logger.info(f"上海岗位: {len(shanghai_jobs)} 条 (过滤掉 {len(unique_jobs) - len(shanghai_jobs)} 条非上海岗位)")
    
    return shanghai_jobs


def save_raw_data(jobs: List[Dict], output_dir: Path):
    """保存原始数据"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'integrated_jobs_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    
    logger.info(f"💾 原始数据已保存: {output_file}")
    return output_file


def run_resume_matching(jobs: List[Dict]) -> Dict[str, Any]:
    """执行简历匹配"""
    logger.info("\n" + "="*80)
    logger.info("🎯 开始简历匹配")
    logger.info("="*80)
    
    try:
        # 导入匹配系统
        from matcher.core.matcher import JobMatcher
        
        # 加载简历 - 尝试多个路径
        resume_paths = [
            project_root / 'resumes' / 'my_resume.json',
            project_root / 'my_resume.json',
            Path('c:/Users/Lenovo/projects/ResuMiner/my_resume.json'),
            Path('c:/Users/Lenovo/projects/ResuMiner_main/my_resume.json'),
        ]
        
        resume = None
        for resume_file in resume_paths:
            if resume_file.exists():
                logger.info(f"📄 加载简历: {resume_file}")
                with open(resume_file, 'r', encoding='utf-8') as f:
                    resume = json.load(f)
                break
        
        if not resume:
            logger.error("❌ 未找到简历文件")
            return {'success': False, 'message': '简历文件不存在'}
        
        logger.info(f"📄 简历: {resume.get('basic_info', {}).get('name', '未知')}")
        
        # 创建匹配器
        config = {
            'model': {'embedding_model': 'paraphrase-multilingual-MiniLM-L12-v2'},
            'match': {
                'weights': {
                    'skill': 0.40,
                    'semantic': 0.35,
                    'experience': 0.25
                }
            }
        }
        
        matcher = JobMatcher(config)
        
        # 执行匹配
        result = matcher.match(resume, jobs, top_k=100)
        
        if result.get('success'):
            logger.info(f"✅ 匹配完成: {len(result.get('matched_jobs', []))} 个匹配岗位")
        else:
            logger.warning(f"⚠️ 匹配未完成: {result.get('message')}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 匹配过程出错: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {'success': False, 'message': str(e)}


def generate_reports(result: Dict[str, Any]):
    """生成报告"""
    logger.info("\n" + "="*80)
    logger.info("📊 生成投递策略报告")
    logger.info("="*80)
    
    try:
        from matcher.report.application_report import ApplicationReportGenerator
        
        generator = ApplicationReportGenerator()
        
        # 获取匹配结果数据
        matched_jobs = result.get('matched_jobs', [])
        resume = result.get('resume', {})
        
        if matched_jobs:
            report_path = generator.generate_application_report(matched_jobs, resume)
            logger.info(f"✅ 投递报告已生成: {report_path}")
        else:
            logger.warning("⚠️ 没有匹配岗位，跳过投递报告生成")
            
    except Exception as e:
        logger.error(f"❌ 生成报告出错: {e}")
        import traceback
        logger.error(traceback.format_exc())


def main():
    """主函数"""
    print("="*80)
    print("🚀 ResuMiner 基于现有数据运行匹配")
    print("="*80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 加载数据
    official_jobs = load_official_jobs()
    third_party_jobs = load_third_party_jobs()
    
    # 合并数据
    all_jobs = merge_and_deduplicate(official_jobs, third_party_jobs)
    
    if not all_jobs:
        print("\n❌ 没有加载到任何岗位数据")
        print("\n请确保以下文件存在:")
        print("  - ResuMiner_main/release_data/internship_shanghai_latest.csv")
        print("  - 或 ResuMiner/data/output/crawler/*.json")
        return 1
    
    # 保存原始数据
    raw_dir = project_root / 'data' / 'raw'
    save_raw_data(all_jobs, raw_dir)
    
    # 执行简历匹配
    result = run_resume_matching(all_jobs)
    
    # 生成报告
    if result.get('success'):
        generate_reports(result)
    
    print("\n" + "="*80)
    print("✅ 匹配流程执行完成！")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
