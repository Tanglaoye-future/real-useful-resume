"""
ResuMiner 爬虫业务层

分平台业务实现，包含前程无忧、猎聘、BOSS直聘等平台的爬虫实现
"""

from resuminer.crawler.base.base_spider import BaseSpider
from resuminer.crawler.base.scheduler import RedisScheduler
from resuminer.crawler.base.fetcher import Fetcher

__all__ = ['BaseSpider', 'RedisScheduler', 'Fetcher']
