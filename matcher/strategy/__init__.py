"""
ResuMiner 投递策略模块

提供分层投递策略支持：
- 冲刺层 (Tier Sprint): 顶级大厂
- 主攻层 (Tier Target): 知名公司
- 保底层 (Tier Safety): 稳妥选择
"""

from .application_strategy import (
    ApplicationStrategy,
    CompanyTier,
    StrategyConfig,
    TierFilter,
)

__all__ = [
    'ApplicationStrategy',
    'CompanyTier',
    'StrategyConfig',
    'TierFilter',
]
