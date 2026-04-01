"""
岗位匹配核心模块

整合硬性过滤、语义打分、报告生成等功能
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from matcher.filters.hard_filter import HardFilter, FilterRule
from matcher.scoring.semantic_scorer import SemanticScorer
from matcher.scoring.match_reporter import MatchReporter

logger = logging.getLogger(__name__)


class JobMatcher:
    """岗位匹配器"""

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化岗位匹配器

        Args:
            config: 匹配配置
        """
        self.config = config or {}

        # 初始化各组件
        self.hard_filter = None
        self.semantic_scorer = None
        self.reporter = None

        self._init_components()

    def _init_components(self):
        """初始化匹配组件"""
        # 1. 硬性过滤器
        filter_config = self.config.get('filter', {})
        rules = FilterRule(
            min_salary=filter_config.get('min_salary'),
            max_salary=filter_config.get('max_salary'),
            locations=filter_config.get('locations', []),
            min_work_years=filter_config.get('min_work_years'),
            max_work_years=filter_config.get('max_work_years'),
            min_education=filter_config.get('min_education'),
            required_skills=filter_config.get('required_skills', []),
            blacklist_companies=filter_config.get('blacklist_companies', [])
        )
        self.hard_filter = HardFilter(rules)

        # 2. 语义打分器
        model_name = self.config.get('model', {}).get('embedding_model', 'all-MiniLM-L6-v2')
        self.semantic_scorer = SemanticScorer(model_name)

        # 3. 报告生成器
        self.reporter = MatchReporter()

    def match(self, resume: Dict[str, Any], jobs: List[Dict[str, Any]],
              top_k: int = 20) -> Dict[str, Any]:
        """
        执行完整的匹配流程

        Args:
            resume: 简历数据
            jobs: 岗位列表
            top_k: 返回前 K 个结果

        Returns:
            匹配结果
        """
        logger.info(f"开始匹配: 简历 {resume.get('basic_info', {}).get('name', '未知')} "
                   f"vs {len(jobs)} 个岗位")

        # Phase 1: 硬性过滤
        logger.info("Phase 1: 硬性规则过滤...")
        passed_jobs, rejected_jobs = self.hard_filter.filter(jobs)
        filter_stats = self.hard_filter.get_stats()
        logger.info(f"硬性过滤完成: {filter_stats['passed']} 通过, {filter_stats['rejected']} 被拒绝")

        if not passed_jobs:
            logger.warning("没有岗位通过硬性过滤")
            return {
                'success': False,
                'message': '没有岗位通过硬性过滤',
                'filter_stats': filter_stats,
                'matched_jobs': []
            }

        # Phase 2: 语义打分与排序
        logger.info("Phase 2: 语义打分...")
        # 获取权重配置
        weights = self.config.get('match', {}).get('weights')
        ranked_jobs = self.semantic_scorer.rank_jobs(resume, passed_jobs, top_k=top_k, weights=weights)
        logger.info(f"语义打分完成，Top {len(ranked_jobs)} 岗位已排序")

        # Phase 3: 生成报告
        logger.info("Phase 3: 生成匹配报告...")
        report_path = self.reporter.generate_report(resume, ranked_jobs, filter_stats)

        return {
            'success': True,
            'filter_stats': filter_stats,
            'matched_jobs': ranked_jobs,
            'report_path': report_path,
            'total_jobs': len(jobs),
            'passed_jobs': len(passed_jobs),
            'resume': resume
        }

    def quick_match(self, resume: Dict[str, Any], jobs: List[Dict[str, Any]],
                   min_score: float = 0.5) -> List[tuple]:
        """
        快速匹配，返回符合条件的岗位

        Args:
            resume: 简历数据
            jobs: 岗位列表
            min_score: 最低匹配分数

        Returns:
            匹配的岗位列表 [(job, scores), ...]
        """
        # 硬性过滤
        passed_jobs, _ = self.hard_filter.filter(jobs)

        # 语义打分并筛选
        matched = []
        for job in passed_jobs:
            scores = self.semantic_scorer.score_job(resume, job)
            if scores.get('overall', 0) >= min_score:
                matched.append((job, scores))

        # 排序
        matched.sort(key=lambda x: x[1]['overall'], reverse=True)

        return matched
