"""
爬虫基础模块

提供爬虫基类、调度器、请求器等通用能力
"""

from resuminer.crawler.base.base_spider import BaseSpider
from resuminer.crawler.base.scheduler import RedisScheduler
from resuminer.crawler.base.fetcher import Fetcher

__all__ = ['BaseSpider', 'RedisScheduler', 'Fetcher']
