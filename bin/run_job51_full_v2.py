#!/usr/bin/env python3
"""
前程无忧全量爬虫 V2 - 优化版本
- 字段配置与猎聘保持一致
- 只限制上海地区
- 分实习和秋招两个关键词
- 全量爬取，提高空页容错
"""

import os
import sys
import csv
import json
import logging
from datetime import datetime
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志 - 使用规范路径
log_dir = project_root / 'data' / 'logs' / 'crawler'
os.makedirs(log_dir, exist_ok=True)
log_file = log_dir / 'job51_full_crawl_v2.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_job51_full_v2():
    """运行前程无忧全量爬虫 V2"""
    # 使用新的 import 路径
    from resuminer.core.crawler_engine.scheduler import RedisScheduler
    from resuminer.core.crawler_engine.spiders.job51_v2 import Job51SpiderV2
    
    logger.info("=" * 70)
    logger.info("前程无忧全量爬虫 V2 启动 - 上海地区实习+秋招")
    logger.info("=" * 70)
    
    # 设置环境变量 - 优化配置
    os.environ['JOB51_JOB_AREA'] = '020000'  # 上海
    os.environ['JOB51_CAMPUS_KEYWORDS'] = '实习,秋招'  # 两个主要关键词
    os.environ['JOB51_INTERN_KEYWORDS'] = '实习,秋招'
    os.environ['JOB51_FALLBACK_KEYWORDS'] = '实习,秋招'
    os.environ['JOB51_MAX_SAFETY_PAGES'] = '500'  # 最大500页
    os.environ['JOB51_EMPTY_STREAK_LIMIT'] = '5'  # 空页容错增加到5页
    os.environ['JOB51_PAGE_SIZE'] = '20'
    os.environ['JOB51_TARGET_MIN_COUNT'] = '5000'  # 目标5000条
    os.environ['JOB51_SCOPE_FILTER_ENABLED'] = '0'  # 关闭严格过滤，提高数据量
    os.environ['JOB51_RECENT_DAYS_FIRST'] = '0'  # 不限制发布时间
    os.environ['JOB51_RECENT_DAYS_FALLBACK'] = '0'
    os.environ['JOB51_THROTTLE_MIN_SECONDS'] = '3'  # 降低延迟，提高速度
    os.environ['JOB51_THROTTLE_MAX_SECONDS'] = '8'
    os.environ['JOB51_FETCH_JD_DETAIL'] = '0'  # 不获取详情页，提高速度
    
    all_jobs = []
    keywords = ['实习', '秋招']  # 与猎聘保持一致的关键词
    start_time = datetime.now()
    
    for idx, keyword in enumerate(keywords, 1):
        logger.info(f"\n【关键词 {idx}/{len(keywords)}】{keyword}")
        logger.info("-" * 70)
        
        try:
            # 设置当前关键词
            os.environ['JOB51_CAMPUS_KEYWORDS'] = keyword
            os.environ['JOB51_INTERN_KEYWORDS'] = keyword
            
            # 创建爬虫实例
            scheduler = RedisScheduler()
            spider = Job51SpiderV2(scheduler)
            
            # 运行爬虫
            jobs = spider.run()
            all_jobs.extend(jobs)
            
            logger.info(f"【{keyword}】完成，获取 {len(jobs)} 条，总计: {len(all_jobs)}")
            
        except Exception as e:
            logger.error(f"【{keyword}】爬取失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            continue
            
    # 所有关键词完成后处理
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60
    
    # 去重 - 使用与猎聘相同的逻辑
    dedup = {}
    for job in all_jobs:
        key = job.get('jd_url', '') or job.get('source_job_id', '')
        if key and key not in dedup:
            dedup[key] = job
    
    unique_jobs = list(dedup.values())
    
    # 使用规范路径保存数据
    output_dir = project_root / 'data' / 'output' / 'job51'
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 保存报告
    report = {
        'platform': '前程无忧',
        'city': '上海',
        'keywords': keywords,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'duration_minutes': round(duration, 2),
        'total_raw': len(all_jobs),
        'total_unique': len(unique_jobs),
        'target_reached': len(unique_jobs) >= 5000
    }
    
    report_file = output_dir / f"job51_report_v2_{timestamp}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 保存JSON数据
    json_file = output_dir / f"job51_data_v2_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(unique_jobs, f, ensure_ascii=False, indent=2)
    
    # 保存CSV - 字段与猎聘保持一致
    csv_file = output_dir / f"job51_jobs_v2_{timestamp}.csv"
    
    if unique_jobs:
        # 定义CSV字段 - 与猎聘保持一致
        fieldnames = [
            'job_name', 'company_name', 'location', 'salary', 'job_type',
            'jd_url', 'jd_content', 'publish_date', 'city',
            'source_job_id', 'source_keyword', 'employment_type',
            'experience_requirement', 'education_requirement',
            'job_tags', 'skill_tags', 'company_industry',
            'company_stage', 'company_size', 'welfare_tags',
            'refresh_time', 'recruitment_count', 'detail_address',
            'company_id', 'company_property',
            'job_description', 'job_requirement'
        ]
        
        with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for job in unique_jobs:
                row = {k: job.get(k, '') for k in fieldnames}
                writer.writerow(row)
        
        logger.info(f"✓ 前程无忧CSV文件已保存: {csv_file}")
    
    logger.info("\n" + "=" * 70)
    logger.info("前程无忧全量爬虫 V2 完成")
    logger.info("=" * 70)
    logger.info(f"原始数据: {len(all_jobs)} 条")
    logger.info(f"去重后: {len(unique_jobs)} 条")
    logger.info(f"耗时: {duration:.1f} 分钟")
    logger.info(f"报告文件: {report_file}")
    logger.info(f"JSON文件: {json_file}")
    logger.info(f"CSV文件: {csv_file}")
    logger.info("=" * 70)
    
    return unique_jobs


if __name__ == "__main__":
    jobs = run_job51_full_v2()
    print(f"\n✓ 前程无忧爬虫 V2 完成，共获取 {len(jobs)} 条数据")
