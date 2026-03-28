#!/usr/bin/env python3
"""
猎聘全量爬虫 - 目标3000+条数据
使用多关键词策略确保数据量
"""

import os
import sys
import time
import json
import csv
import logging
from datetime import datetime
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志 - 使用规范路径
log_dir = project_root / 'data' / 'logs' / 'crawler'
os.makedirs(log_dir, exist_ok=True)
log_file = log_dir / 'liepin_full_crawl.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 设置环境变量 - 全量爬取配置
os.environ['LIEPIN_MAX_PAGES'] = '500'  # 每关键词500页（最大限制）
os.environ['LIEPIN_CITY'] = '020'  # 上海


def run_liepin_full():
    """运行猎聘全量爬虫 - 多关键词策略"""
    # 使用新的 import 路径
    from resuminer.core.crawler_engine.scheduler import RedisScheduler
    from resuminer.core.crawler_engine.spiders.liepin_v6 import LiepinSpiderV6
    
    logger.info("=" * 70)
    logger.info("猎聘全量爬虫启动 - 目标3000+条数据")
    logger.info("=" * 70)
    
    all_jobs = []
    # 上海地区全量爬取：实习 + 秋招 两大关键词（实习数据量更大）
    keywords = ['实习', '秋招']
    
    start_time = datetime.now()
    
    for idx, keyword in enumerate(keywords, 1):
        logger.info(f"\n【关键词 {idx}/{len(keywords)}】{keyword}")
        logger.info("-" * 70)
        
        try:
            # 设置当前关键词
            os.environ['LIEPIN_KEYWORD'] = keyword
            
            # 创建爬虫实例
            scheduler = RedisScheduler()
            spider = LiepinSpiderV6(scheduler)
            
            # 运行爬虫
            jobs = spider.run()
            
            # 添加到总列表
            all_jobs.extend(jobs)
            
            logger.info(f"【{keyword}】完成，获取 {len(jobs)} 条，总计: {len(all_jobs)}")
            
            # 全量爬取模式：不提前终止，遍历所有关键词的所有页面
            logger.info(f"\n✓ 当前关键词完成，累计数据: {len(all_jobs)} 条")
            
            # 关键词之间休息
            if idx < len(keywords):
                sleep_time = 10
                logger.info(f"休息 {sleep_time} 秒后切换下一个关键词...")
                time.sleep(sleep_time)
                
        except Exception as e:
            logger.error(f"【{keyword}】爬取失败: {e}")
            continue
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60
    
    # 去重
    dedup = {}
    for job in all_jobs:
        key = job.get('jd_url', '') or job.get('source_job_id', '')
        if key and key not in dedup:
            dedup[key] = job
    
    unique_jobs = list(dedup.values())
    
    # 使用规范路径保存数据
    output_dir = project_root / 'data' / 'output' / 'liepin'
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 保存结果
    report = {
        'platform': '猎聘',
        'city': '上海',
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'duration_minutes': round(duration, 2),
        'total_raw': len(all_jobs),
        'total_unique': len(unique_jobs),
        'keywords': keywords,
        'target_reached': len(unique_jobs) >= 3000
    }
    
    report_file = output_dir / f"liepin_report_{timestamp}.json"
    
    # 保存报告
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 保存JSON数据
    data_file = output_dir / f"liepin_data_{timestamp}.json"
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(unique_jobs, f, ensure_ascii=False, indent=2)
    
    # 保存CSV数据 - 猎聘专用文件
    csv_file = output_dir / f"liepin_jobs_{timestamp}.csv"
    if unique_jobs:
        # 获取所有字段
        fieldnames = list(unique_jobs[0].keys())
        with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(unique_jobs)
        logger.info(f"✓ 猎聘CSV文件已保存: {csv_file}")
    
    logger.info("\n" + "=" * 70)
    logger.info("猎聘全量爬虫完成")
    logger.info("=" * 70)
    logger.info(f"原始数据: {len(all_jobs)} 条")
    logger.info(f"去重后: {len(unique_jobs)} 条")
    logger.info(f"耗时: {duration:.1f} 分钟")
    logger.info(f"报告文件: {report_file}")
    logger.info(f"JSON文件: {data_file}")
    logger.info(f"CSV文件: {csv_file}")
    logger.info("=" * 70)
    
    return unique_jobs


if __name__ == "__main__":
    jobs = run_liepin_full()
    print(f"\n✓ 猎聘爬虫完成，共获取 {len(jobs)} 条数据")
