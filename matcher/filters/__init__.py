"""
岗位筛选模块 V2

提供硬性规则过滤和高价值岗位筛选功能
支持互联网大厂、外企、独角兽、国企等多类型企业评估
"""

from matcher.filters.hard_filter import HardFilter, FilterRule
from matcher.filters.value_filter import (
    ValueFilter, 
    ValueFilterConfig, 
    CompanyTier, 
    JobValueLevel,
    CompanyClassifier
)

__all__ = [
    'HardFilter',
    'FilterRule',
    'ValueFilter',
    'ValueFilterConfig',
    'CompanyTier',
    'JobValueLevel',
    'CompanyClassifier'
]
