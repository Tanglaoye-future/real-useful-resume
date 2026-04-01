#!/usr/bin/env python3
"""
ResuMiner 完整流程运行脚本
从爬虫数据获取到匹配报告生成的全流程
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

# 设置项目路径
project_root = Path(__file__).parent.parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

# 配置日志
import logging
log_dir = project_root / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f'full_pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_official_crawlers():
    """运行官网爬虫"""
    logger.info("="*80)
    logger.info("🚀 步骤1: 运行官网CDP爬虫")
    logger.info("="*80)
    
    crawlers_dir = project_root / 'crawlers' / 'official'
    crawlers = [
        ('cdp_tencent.py', '腾讯'),
        ('cdp_meituan.py', '美团'),
        ('cdp_alibaba.py', '阿里'),
        ('cdp_jd.py', '京东'),
        ('cdp_kuaishou.py', '快手'),
        ('cdp_bilibili.py', '哔哩哔哩'),
        ('cdp_bytedance.py', '字节跳动'),
    ]
    
    all_jobs = []
    
    for crawler_file, company_name in crawlers:
        crawler_path = crawlers_dir / crawler_file
        if not crawler_path.exists():
            logger.warning(f"⚠️ 爬虫文件不存在: {crawler_path}")
            continue
        
        logger.info(f"\n📍 开始爬取: {company_name}")
        try:
            result = subprocess.run(
                [sys.executable, str(crawler_path)],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=str(project_root)
            )
            
            if result.returncode == 0:
                logger.info(f"   ✅ {company_name} 爬取成功")
                # 检查输出文件
                output_dir = project_root / 'data' / 'raw' / 'official'
                if output_dir.exists():
                    json_files = list(output_dir.glob(f'{company_name.lower()}_*.json'))
                    if json_files:
                        latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
                        with open(latest_file, 'r', encoding='utf-8') as f:
                            jobs = json.load(f)
                            all_jobs.extend(jobs)
                            logger.info(f"   📊 获取 {len(jobs)} 条岗位")
            else:
                logger.error(f"   ❌ {company_name} 爬取失败")
                if result.stderr:
                    logger.error(f"   错误: {result.stderr[:200]}")
                    
        except subprocess.TimeoutExpired:
            logger.error(f"   ⏱️ {company_name} 爬取超时")
        except Exception as e:
            logger.error(f"   ❌ {company_name} 异常: {e}")
    
    logger.info(f"\n✅ 官网爬虫完成: 共 {len(all_jobs)} 条岗位")
    return all_jobs

def run_third_party_crawlers():
    """运行第三方平台爬虫"""
    logger.info("\n" + "="*80)
    logger.info("🚀 步骤2: 运行第三方平台爬虫")
    logger.info("="*80)
    
    spiders_dir = project_root / 'core' / 'crawler_engine' / 'spiders'
    all_jobs = []
    
    # 51job爬虫
    logger.info("\n📍 开始爬取: 前程无忧(51job)")
    try:
        job51_script = spiders_dir / 'job51_v2.py'
        if job51_script.exists():
            # 设置环境变量
            env = os.environ.copy()
            env['JOB51_JOB_AREA'] = '020000'  # 上海
            env['JOB51_CAMPUS_KEYWORDS'] = '实习'
            env['JOB51_MAX_SAFETY_PAGES'] = '10'  # 限制页数用于测试
            
            result = subprocess.run(
                [sys.executable, str(job51_script)],
                capture_output=True,
                text=True,
                timeout=600,
                cwd=str(project_root),
                env=env
            )
            
            if result.returncode == 0:
                logger.info("   ✅ 51job 爬取成功")
            else:
                logger.warning("   ⚠️ 51job 可能需要特殊配置")
    except Exception as e:
        logger.error(f"   ❌ 51job 异常: {e}")
    
    # 猎聘爬虫
    logger.info("\n📍 开始爬取: 猎聘")
    try:
        liepin_script = spiders_dir / 'liepin_v2.py'
        if liepin_script.exists():
            env = os.environ.copy()
            env['LIEPIN_KEYWORD'] = '实习'
            env['LIEPIN_CITY'] = '020'  # 上海
            
            result = subprocess.run(
                [sys.executable, str(liepin_script)],
                capture_output=True,
                text=True,
                timeout=600,
                cwd=str(project_root),
                env=env
            )
            
            if result.returncode == 0:
                logger.info("   ✅ 猎聘 爬取成功")
            else:
                logger.warning("   ⚠️ 猎聘 可能需要特殊配置")
    except Exception as e:
        logger.error(f"   ❌ 猎聘 异常: {e}")
    
    logger.info(f"\n✅ 第三方平台爬虫完成")
    return all_jobs

def collect_all_data():
    """收集所有爬虫数据"""
    logger.info("\n" + "="*80)
    logger.info("📊 步骤3: 收集和整合数据")
    logger.info("="*80)
    
    all_jobs = []
    
    # 1. 收集官网爬虫数据
    official_dir = project_root / 'data' / 'raw' / 'official'
    if official_dir.exists():
        for json_file in official_dir.glob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    jobs = json.load(f)
                    all_jobs.extend(jobs)
                    logger.info(f"   📁 {json_file.name}: {len(jobs)} 条")
            except Exception as e:
                logger.warning(f"   ⚠️ 读取 {json_file.name} 失败: {e}")
    
    # 2. 检查ResuMiner_main的数据
    main_data_dir = Path('c:/Users/Lenovo/projects/ResuMiner_main/release_data')
    if main_data_dir.exists():
        csv_files = [
            'official_jobs_raw_latest.csv',
            'internship_shanghai_latest.csv'
        ]
        for csv_file in csv_files:
            csv_path = main_data_dir / csv_file
            if csv_path.exists():
                logger.info(f"   📁 找到数据文件: {csv_file}")
    
    logger.info(f"\n✅ 数据收集完成: 共 {len(all_jobs)} 条岗位")
    return all_jobs

def run_matching():
    """运行匹配流程"""
    logger.info("\n" + "="*80)
    logger.info("🎯 步骤4: 运行简历匹配")
    logger.info("="*80)
    
    try:
        result = subprocess.run(
            [sys.executable, 'bin/run_with_existing_data.py'],
            capture_output=True,
            text=True,
            timeout=1800,
            cwd=str(project_root)
        )
        
        if result.returncode == 0:
            logger.info("   ✅ 匹配流程完成")
            # 显示输出
            if result.stdout:
                lines = result.stdout.split('\n')
                for line in lines[-20:]:  # 显示最后20行
                    if line.strip():
                        logger.info(f"   {line}")
        else:
            logger.error("   ❌ 匹配流程失败")
            if result.stderr:
                logger.error(f"   错误: {result.stderr[:500]}")
                
    except subprocess.TimeoutExpired:
        logger.error("   ⏱️ 匹配流程超时")
    except Exception as e:
        logger.error(f"   ❌ 匹配流程异常: {e}")

def verify_outputs():
    """验证输出文件"""
    logger.info("\n" + "="*80)
    logger.info("✅ 步骤5: 验证输出结果")
    logger.info("="*80)
    
    output_dir = project_root / 'data' / 'output'
    
    # 检查匹配报告
    matcher_dir = output_dir / 'matcher'
    if matcher_dir.exists():
        md_files = list(matcher_dir.glob('match_report_*.md'))
        json_files = list(matcher_dir.glob('match_report_*.json'))
        logger.info(f"   📄 匹配报告: {len(md_files)} 个Markdown, {len(json_files)} 个JSON")
        
        if md_files:
            latest = max(md_files, key=lambda p: p.stat().st_mtime)
            logger.info(f"   📄 最新报告: {latest.name}")
    
    # 检查投递报告
    app_dir = output_dir / 'application_reports'
    if app_dir.exists():
        app_files = list(app_dir.glob('application_report_*.md'))
        logger.info(f"   📄 投递报告: {len(app_files)} 个")
        
        if app_files:
            latest = max(app_files, key=lambda p: p.stat().st_mtime)
            logger.info(f"   📄 最新报告: {latest.name}")
    
    # 检查工程包
    pkg_dir = project_root / 'project_package'
    if pkg_dir.exists():
        logger.info(f"   📦 工程包已创建")

def main():
    """主函数"""
    logger.info("="*80)
    logger.info("🚀 ResuMiner 完整流程")
    logger.info("从爬虫到匹配的端到端测试")
    logger.info("="*80)
    logger.info(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"项目路径: {project_root}")
    
    start_time = time.time()
    
    # 步骤1: 运行官网爬虫
    official_jobs = run_official_crawlers()
    
    # 步骤2: 运行第三方平台爬虫
    third_party_jobs = run_third_party_crawlers()
    
    # 步骤3: 收集数据
    all_jobs = collect_all_data()
    
    # 步骤4: 运行匹配
    run_matching()
    
    # 步骤5: 验证输出
    verify_outputs()
    
    # 总结
    elapsed = time.time() - start_time
    logger.info("\n" + "="*80)
    logger.info("🎉 完整流程执行完成!")
    logger.info("="*80)
    logger.info(f"总耗时: {elapsed:.1f} 秒")
    logger.info(f"日志文件: {log_file}")
    logger.info("="*80)

if __name__ == '__main__':
    main()
