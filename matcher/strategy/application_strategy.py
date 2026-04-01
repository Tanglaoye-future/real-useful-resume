#!/usr/bin/env python3
"""
投递策略引擎 - 生产级实现

支持基于公司分层的智能投递策略：
1. 冲刺层 (Tier Sprint) - 顶级大厂
2. 主攻层 (Tier Target) - 知名公司  
3. 保底层 (Tier Safety) - 稳妥选择
"""

import yaml
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any
from collections import defaultdict
from datetime import datetime, timedelta
import pandas as pd

# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class CompanyInfo:
    """公司信息"""
    name: str
    aliases: List[str] = field(default_factory=list)
    departments: List[str] = field(default_factory=list)
    tier: str = "unknown"
    
    def matches(self, company_name: str) -> bool:
        """检查公司名称是否匹配"""
        company_lower = company_name.lower()
        if self.name.lower() in company_lower:
            return True
        for alias in self.aliases:
            if alias.lower() in company_lower:
                return True
        return False


@dataclass
class TierFilter:
    """层级筛选条件"""
    min_match_score: float = 0.50
    max_work_years: int = 5
    locations: List[str] = field(default_factory=list)
    job_types: List[str] = field(default_factory=list)
    salary_range: str = "unlimited"
    
    def check_job(self, job: Dict, match_score: float) -> Tuple[bool, str]:
        """检查岗位是否符合筛选条件"""
        # 匹配度检查
        if match_score < self.min_match_score:
            return False, f"匹配度 {match_score:.2f} < 最低要求 {self.min_match_score}"
        
        # 地点检查
        if self.locations:
            location = job.get('location', '') + job.get('city', '')
            if not any(loc in location for loc in self.locations):
                return False, f"地点 {location} 不在目标城市列表中"
        
        # 工作年限检查
        experience_req = job.get('experience_requirement', '')
        if experience_req and '年' in experience_req:
            import re
            years_match = re.search(r'(\d+)', experience_req)
            if years_match:
                required_years = int(years_match.group(1))
                if required_years > self.max_work_years:
                    return False, f"要求工作年限 {required_years} 年 > 最大接受 {self.max_work_years} 年"
        
        return True, "通过"


@dataclass
class StrategyConfig:
    """投递策略配置"""
    batch_size: int = 3
    interval_days: int = 7
    max_applications: int = 15
    resume_customization: bool = True
    cover_letter: bool = False


@dataclass
class CompanyTier:
    """公司层级定义"""
    name: str
    description: str
    priority: int
    target_ratio: float
    companies: List[CompanyInfo] = field(default_factory=list)
    filters: TierFilter = field(default_factory=TierFilter)
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    
    def get_company_tier(self, company_name: str) -> Optional[str]:
        """获取公司所属层级"""
        for company in self.companies:
            if company.matches(company_name):
                return self.name
        return None


class ApplicationStrategy:
    """
    投递策略引擎
    
    生产级实现，支持：
    - 从配置文件加载策略
    - 公司层级识别
    - 分层筛选和排序
    - 投递计划生成
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        初始化策略引擎
        
        Args:
            config_path: 配置文件路径，默认使用 conf/application_strategy.yaml
        """
        self.config_path = config_path or Path(__file__).parent.parent.parent.parent / 'conf' / 'application_strategy.yaml'
        self.config: Dict = {}
        self.tiers: Dict[str, CompanyTier] = {}
        self.company_map: Dict[str, Tuple[str, CompanyInfo]] = {}  # company_name -> (tier_name, CompanyInfo)
        
        self._load_config()
        self._build_company_map()
        
        logger.info(f"策略引擎初始化完成，加载了 {len(self.tiers)} 个层级")
    
    def _load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"配置文件加载成功: {self.config_path}")
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            raise
        
        # 解析各层级
        company_tiers_config = self.config.get('company_tiers', {})
        
        for tier_key, tier_config in company_tiers_config.items():
            tier = CompanyTier(
                name=tier_config.get('name', tier_key),
                description=tier_config.get('description', ''),
                priority=tier_config.get('priority', 99),
                target_ratio=tier_config.get('target_ratio', 0.33),
                companies=[
                    CompanyInfo(
                        name=c['name'],
                        aliases=c.get('aliases', []),
                        departments=c.get('departments', [])
                    )
                    for c in tier_config.get('companies', [])
                ],
                filters=TierFilter(
                    min_match_score=tier_config.get('filters', {}).get('min_match_score', 0.50),
                    max_work_years=tier_config.get('filters', {}).get('max_work_years', 5),
                    locations=tier_config.get('filters', {}).get('locations', []),
                    job_types=tier_config.get('filters', {}).get('job_types', []),
                    salary_range=tier_config.get('filters', {}).get('salary_range', 'unlimited')
                ),
                strategy=StrategyConfig(
                    batch_size=tier_config.get('strategy', {}).get('batch_size', 3),
                    interval_days=tier_config.get('strategy', {}).get('interval_days', 7),
                    max_applications=tier_config.get('strategy', {}).get('max_applications', 15),
                    resume_customization=tier_config.get('strategy', {}).get('resume_customization', True),
                    cover_letter=tier_config.get('strategy', {}).get('cover_letter', False)
                )
            )
            self.tiers[tier_key] = tier
    
    def _build_company_map(self):
        """构建公司名称到层级的映射"""
        for tier_key, tier in self.tiers.items():
            for company in tier.companies:
                # 主名称
                self.company_map[company.name.lower()] = (tier_key, company)
                # 别名
                for alias in company.aliases:
                    self.company_map[alias.lower()] = (tier_key, company)
    
    def get_company_tier(self, company_name: str) -> Tuple[str, int, Optional[CompanyInfo]]:
        """
        获取公司所属层级
        
        Args:
            company_name: 公司名称
            
        Returns:
            (tier_key, priority, CompanyInfo)
            tier_key: tier_sprint / tier_target / tier_safety / unknown
            priority: 数字越小优先级越高
            CompanyInfo: 公司详细信息
        """
        company_lower = company_name.lower()
        
        # 直接匹配
        if company_lower in self.company_map:
            tier_key, company_info = self.company_map[company_lower]
            return tier_key, self.tiers[tier_key].priority, company_info
        
        # 模糊匹配
        for name, (tier_key, company_info) in self.company_map.items():
            if name in company_lower or company_lower in name:
                return tier_key, self.tiers[tier_key].priority, company_info
        
        return 'unknown', 99, None
    
    def calculate_priority_score(
        self,
        job: Dict,
        match_score: float,
        tier_key: str
    ) -> float:
        """
        计算岗位优先级分数
        
        公式：公司层级分 + 匹配度分 + 复合背景加分
        
        Args:
            job: 岗位信息
            match_score: 基础匹配分数 (0-1)
            tier_key: 公司层级key
            
        Returns:
            优先级分数 (0-100)
        """
        # 1. 公司层级分
        tier_scores = {
            'tier_sprint': 40,
            'tier_target': 30,
            'tier_safety': 20,
            'unknown': 0
        }
        tier_score = tier_scores.get(tier_key, 0)
        
        # 2. 匹配度分 (最高50分)
        match_score_points = match_score * 50
        
        # 3. 复合背景加分
        bonus = self._calculate_composite_bonus(job)
        
        total = tier_score + match_score_points + bonus
        return min(100, total)
    
    def _calculate_composite_bonus(self, job: Dict) -> float:
        """计算复合背景加分"""
        bonus = 0.0
        
        # 获取复合背景配置
        composite_config = self.config.get('composite_scoring', {})
        if not composite_config.get('enabled', False):
            return 0.0
        
        backgrounds = composite_config.get('backgrounds', {})
        bonuses_config = composite_config.get('bonuses', {})
        
        # 这里简化处理，实际应该根据简历内容判断
        # 返回基础加分
        job_type = job.get('job_type', '')
        
        if job_type == 'tech':
            bonus += 3  # 技术岗基础加分
        elif job_type == 'finance':
            bonus += 5  # 金融岗基础加分
        elif job_type == 'product':
            bonus += 2  # 产品岗基础加分
        
        return bonus
    
    def filter_and_rank_jobs(
        self,
        jobs: List[Dict],
        match_scores: Dict[str, float],
        target_tier: Optional[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        筛选并排序岗位
        
        Args:
            jobs: 岗位列表
            match_scores: 岗位ID到匹配分数的映射
            target_tier: 目标层级，None表示所有层级
            
        Returns:
            按层级分组的排序后岗位 {tier_key: [job_dict, ...]}
        """
        results = defaultdict(list)
        
        for job in jobs:
            job_id = job.get('source_job_id', '')
            match_score = match_scores.get(job_id, 0)
            company_name = job.get('company_name', '')
            
            # 获取公司层级
            tier_key, priority, company_info = self.get_company_tier(company_name)
            
            # 如果指定了目标层级，跳过其他层级
            if target_tier and tier_key != target_tier:
                continue
            
            # 获取该层级的筛选条件
            tier_config = self.tiers.get(tier_key)
            if tier_config:
                passed, reason = tier_config.filters.check_job(job, match_score)
                if not passed:
                    logger.debug(f"岗位被过滤: {job.get('job_name')} - {reason}")
                    continue
            
            # 计算优先级分数
            priority_score = self.calculate_priority_score(job, match_score, tier_key)
            
            # 添加到结果
            job_with_score = {
                'job': job,
                'match_score': match_score,
                'priority_score': priority_score,
                'tier': tier_key,
                'tier_priority': priority,
                'company_info': company_info
            }
            results[tier_key].append(job_with_score)
        
        # 对每个层级内的岗位按优先级分数排序
        for tier_key in results:
            results[tier_key].sort(key=lambda x: x['priority_score'], reverse=True)
        
        return dict(results)
    
    def generate_application_plan(
        self,
        ranked_jobs: Dict[str, List[Dict]],
        start_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        生成投递计划
        
        Args:
            ranked_jobs: 按层级分组的排序后岗位
            start_date: 开始日期，默认明天
            
        Returns:
            投递计划
        """
        if start_date is None:
            start_date = datetime.now() + timedelta(days=1)
        
        plan = {
            'generated_at': datetime.now().isoformat(),
            'start_date': start_date.isoformat(),
            'tiers': {}
        }
        
        current_date = start_date
        
        for tier_key in ['tier_sprint', 'tier_target', 'tier_safety']:
            if tier_key not in ranked_jobs:
                continue
            
            tier_config = self.tiers.get(tier_key)
            if not tier_config:
                continue
            
            jobs = ranked_jobs[tier_key]
            strategy = tier_config.strategy
            
            # 限制数量
            max_jobs = min(len(jobs), strategy.max_applications)
            selected_jobs = jobs[:max_jobs]
            
            # 生成批次
            batches = []
            for i in range(0, len(selected_jobs), strategy.batch_size):
                batch_jobs = selected_jobs[i:i + strategy.batch_size]
                batch = {
                    'date': current_date.strftime('%Y-%m-%d'),
                    'jobs': [
                        {
                            'job_name': j['job'].get('job_name', ''),
                            'company': j['job'].get('company_name', ''),
                            'priority_score': j['priority_score'],
                            'match_score': j['match_score']
                        }
                        for j in batch_jobs
                    ]
                }
                batches.append(batch)
                current_date += timedelta(days=strategy.interval_days)
            
            plan['tiers'][tier_key] = {
                'name': tier_config.name,
                'total_jobs': len(selected_jobs),
                'batches': batches,
                'strategy': {
                    'batch_size': strategy.batch_size,
                    'interval_days': strategy.interval_days,
                    'resume_customization': strategy.resume_customization,
                    'cover_letter': strategy.cover_letter
                }
            }
        
        return plan
    
    def get_resume_customization_config(self, tier_key: str) -> Dict:
        """获取简历定制化配置"""
        customization_config = self.config.get('resume_customization', {})
        return customization_config.get(tier_key, {})
    
    def get_matching_weights(self, tier_key: str) -> Dict[str, float]:
        """获取匹配权重配置"""
        weights_config = self.config.get('matching_weights', {})
        
        # 先尝试获取层级特定权重
        tier_weights = weights_config.get(tier_key)
        if tier_weights:
            return tier_weights
        
        # 返回基础权重
        return weights_config.get('base', {
            'skill': 0.40,
            'semantic': 0.35,
            'experience': 0.25
        })
    
    def export_strategy_report(self, output_path: Path):
        """导出策略报告"""
        report = {
            'version': self.config.get('version', '1.0.0'),
            'generated_at': datetime.now().isoformat(),
            'tiers': {}
        }
        
        for tier_key, tier in self.tiers.items():
            report['tiers'][tier_key] = {
                'name': tier.name,
                'description': tier.description,
                'company_count': len(tier.companies),
                'target_ratio': tier.target_ratio,
                'filters': {
                    'min_match_score': tier.filters.min_match_score,
                    'max_work_years': tier.filters.max_work_years,
                    'locations': tier.filters.locations
                },
                'strategy': {
                    'batch_size': tier.strategy.batch_size,
                    'max_applications': tier.strategy.max_applications
                }
            }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"策略报告已导出: {output_path}")


# 单例模式
_strategy_instance: Optional[ApplicationStrategy] = None


def get_strategy(config_path: Optional[Path] = None) -> ApplicationStrategy:
    """获取策略引擎单例"""
    global _strategy_instance
    if _strategy_instance is None:
        _strategy_instance = ApplicationStrategy(config_path)
    return _strategy_instance
