#!/usr/bin/env python3
"""V3版本爬虫测试脚本"""

import logging
import sys
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/v3_test_20260327.log', encoding='utf-8')
    ]
)
logger = logging.getLogger('V3Test')

def test_boss_v3():
    """测试 Boss V3"""
    logger.info('='*60)
    logger.info('开始测试 Boss V3 爬虫')
    logger.info('='*60)
    
    from crawler_engine.spiders.boss_v3 import BossSpiderV3
    from crawler_engine.scheduler import RedisScheduler
    
    scheduler = RedisScheduler()
    spider = BossSpiderV3(scheduler=scheduler, base_cookie='')
    spider.max_pages = 1  # 只测试1页
    
    try:
        jobs = spider.run()
        logger.info(f'Boss V3 测试完成，采集到 {len(jobs)} 条职位')
        if jobs:
            for i, job in enumerate(jobs[:3]):
                name = job.get('job_name', 'N/A')
                company = job.get('company_name', 'N/A')
                logger.info(f'  职位{i+1}: {name} - {company}')
        return len(jobs)
    except Exception as e:
        logger.error(f'Boss V3 测试失败: {e}', exc_info=True)
        return 0

def test_liepin_v3():
    """测试 Liepin V3"""
    logger.info('')
    logger.info('='*60)
    logger.info('开始测试 Liepin V3 爬虫')
    logger.info('='*60)
    
    from crawler_engine.spiders.liepin_v3 import LiepinSpiderV3
    from crawler_engine.scheduler import RedisScheduler
    
    scheduler = RedisScheduler()
    spider = LiepinSpiderV3(scheduler=scheduler, base_cookie='')
    spider.max_pages = 1  # 只测试1页
    
    try:
        jobs = spider.run()
        logger.info(f'Liepin V3 测试完成，采集到 {len(jobs)} 条职位')
        if jobs:
            for i, job in enumerate(jobs[:3]):
                name = job.get('job_name', 'N/A')
                company = job.get('company_name', 'N/A')
                logger.info(f'  职位{i+1}: {name} - {company}')
        return len(jobs)
    except Exception as e:
        logger.error(f'Liepin V3 测试失败: {e}', exc_info=True)
        return 0

if __name__ == '__main__':
    boss_count = test_boss_v3()
    liepin_count = test_liepin_v3()
    
    logger.info('')
    logger.info('='*60)
    logger.info('V3 测试汇总')
    logger.info('='*60)
    logger.info(f'Boss V3: {boss_count} 条职位')
    logger.info(f'Liepin V3: {liepin_count} 条职位')
    logger.info('测试完成')
