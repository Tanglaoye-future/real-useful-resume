#!/usr/bin/env python3
"""
Boss直聘两种方案对比测试
"""

import logging
import sys
import time
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('BossComparison')

def test_api_scheme():
    """测试API方案"""
    logger.info("="*60)
    logger.info("测试方案A: API方案")
    logger.info("="*60)
    
    from crawler_engine.scheduler import RedisScheduler
    from crawler_engine.spiders.boss_v2_api import BossSpiderV2API
    
    scheduler = RedisScheduler()
    spider = BossSpiderV2API(scheduler=scheduler, base_cookie="")
    spider.max_pages = 3  # 测试3页
    
    start_time = time.time()
    try:
        jobs = spider.run()
        duration = time.time() - start_time
        
        logger.info(f"API方案结果: {len(jobs)}条职位, 耗时{duration:.1f}秒")
        return {
            "scheme": "API",
            "jobs": len(jobs),
            "duration": duration,
            "success": len(jobs) > 0
        }
    except Exception as e:
        logger.error(f"API方案失败: {e}")
        return {
            "scheme": "API",
            "jobs": 0,
            "duration": time.time() - start_time,
            "success": False,
            "error": str(e)
        }

def test_pw_scheme():
    """测试Playwright方案"""
    logger.info("="*60)
    logger.info("测试方案B: Playwright方案")
    logger.info("="*60)
    
    from crawler_engine.scheduler import RedisScheduler
    from crawler_engine.spiders.boss_v2_pw import BossSpiderV2PW
    
    scheduler = RedisScheduler()
    spider = BossSpiderV2PW(scheduler=scheduler, base_cookie="")
    spider.max_pages = 3  # 测试3页
    
    start_time = time.time()
    try:
        jobs = spider.run()
        duration = time.time() - start_time
        
        logger.info(f"Playwright方案结果: {len(jobs)}条职位, 耗时{duration:.1f}秒")
        return {
            "scheme": "Playwright",
            "jobs": len(jobs),
            "duration": duration,
            "success": len(jobs) > 0
        }
    except Exception as e:
        logger.error(f"Playwright方案失败: {e}")
        return {
            "scheme": "Playwright",
            "jobs": 0,
            "duration": time.time() - start_time,
            "success": False,
            "error": str(e)
        }

if __name__ == '__main__':
    logger.info("开始Boss直聘爬虫方案对比测试")
    logger.info("="*60)
    
    # 测试API方案
    result_api = test_api_scheme()
    
    logger.info("")
    
    # 测试Playwright方案
    result_pw = test_pw_scheme()
    
    # 对比结果
    logger.info("")
    logger.info("="*60)
    logger.info("对比结果汇总")
    logger.info("="*60)
    
    for result in [result_api, result_pw]:
        scheme = result["scheme"]
        jobs = result["jobs"]
        duration = result["duration"]
        success = result["success"]
        
        status = "✅ 成功" if success else "❌ 失败"
        logger.info(f"{scheme}: {status}, {jobs}条职位, {duration:.1f}秒")
    
    # 推荐最优方案
    logger.info("")
    logger.info("="*60)
    logger.info("最优方案推荐")
    logger.info("="*60)
    
    if result_api["success"] and result_pw["success"]:
        # 都成功，比较效率
        if result_api["jobs"] > result_pw["jobs"]:
            logger.info("推荐: API方案 (数据量更多)")
        elif result_pw["jobs"] > result_api["jobs"]:
            logger.info("推荐: Playwright方案 (数据量更多)")
        else:
            # 数据量相同，比较速度
            if result_api["duration"] < result_pw["duration"]:
                logger.info("推荐: API方案 (速度更快)")
            else:
                logger.info("推荐: Playwright方案 (速度更快)")
    elif result_api["success"]:
        logger.info("推荐: API方案 (Playwright失败)")
    elif result_pw["success"]:
        logger.info("推荐: Playwright方案 (API失败)")
    else:
        logger.info("两个方案都失败，需要进一步优化")
    
    logger.info("")
    logger.info("测试完成!")
