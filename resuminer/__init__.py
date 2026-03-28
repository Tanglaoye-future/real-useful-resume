"""
ResuMiner - 招聘数据爬虫系统

ResuMiner 是一个面向国内主流招聘平台（前程无忧51job、猎聘网、BOSS直聘）的
招聘数据爬虫系统，具备多平台账号/cookies管理、请求加密/移动端逆向工程、
分布式爬虫引擎、数据ETL清洗、数据落地导出、运行监控与日志追踪等核心能力。

Usage:
    from resuminer import get_config, get_logger
    
    config = get_config()
    logger = get_logger('my_module')
"""

__version__ = '2.0.0'
__author__ = 'ResuMiner Team'

from resuminer.common import get_config, get_logger, setup_logging

__all__ = ['get_config', 'get_logger', 'setup_logging']
