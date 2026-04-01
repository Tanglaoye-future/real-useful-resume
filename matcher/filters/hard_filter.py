"""
硬性规则过滤模块

实现漏斗式筛选的第一阶段：硬性规则过滤
"""

import logging
import re
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FilterRule:
    """筛选规则配置"""
    min_salary: Optional[int] = None  # 最低薪资要求
    max_salary: Optional[int] = None  # 最高薪资要求
    locations: List[str] = None  # 目标地点列表
    min_work_years: Optional[int] = None  # 最低工作年限
    max_work_years: Optional[int] = None  # 最高工作年限
    min_education: Optional[str] = None  # 最低学历
    required_skills: List[str] = None  # 必须技能
    blacklist_companies: List[str] = None  # 黑名单公司


class HardFilter:
    """硬性规则过滤器"""

    EDUCATION_LEVEL = {
        "大专": 1,
        "本科": 2,
        "硕士": 3,
        "博士": 4
    }

    def __init__(self, rules: FilterRule = None):
        self.rules = rules or FilterRule()
        self.rejected_count = 0
        self.passed_count = 0

    def filter(self, jobs: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        执行硬性过滤

        Args:
            jobs: 岗位列表

        Returns:
            (通过的岗位列表, 被拒绝的岗位列表)
        """
        passed = []
        rejected = []

        for job in jobs:
            is_passed, reason = self._check_job(job)
            if is_passed:
                passed.append(job)
                self.passed_count += 1
            else:
                job['reject_reason'] = reason
                rejected.append(job)
                self.rejected_count += 1

        logger.info(f"硬性过滤完成: {len(passed)} 通过, {len(rejected)} 被拒绝")
        return passed, rejected

    def _check_job(self, job: Dict[str, Any]) -> Tuple[bool, str]:
        """检查单个岗位是否符合硬性要求"""

        # 1. 检查地点
        if self.rules.locations:
            job_location = job.get('location', '') or job.get('city', '')
            if not any(loc in job_location for loc in self.rules.locations):
                return False, f"地点不匹配: {job_location}"

        # 2. 检查薪资
        if self.rules.min_salary is not None:
            salary_match = self._parse_salary(job.get('salary', ''))
            if salary_match and salary_match < self.rules.min_salary:
                return False, f"薪资低于要求: {salary_match} < {self.rules.min_salary}"

        # 3. 检查工作年限
        if self.rules.min_work_years is not None or self.rules.max_work_years is not None:
            job_years = self._parse_work_years(job.get('experience_requirement', ''))
            if job_years is not None:
                if self.rules.min_work_years and job_years < self.rules.min_work_years:
                    return False, f"工作年限不足: {job_years}年 < {self.rules.min_work_years}年"
                if self.rules.max_work_years and job_years > self.rules.max_work_years:
                    return False, f"工作年限超出: {job_years}年 > {self.rules.max_work_years}年"

        # 4. 检查学历
        if self.rules.min_education:
            job_edu = job.get('education_requirement', '')
            if not self._check_education(job_edu, self.rules.min_education):
                return False, f"学历不满足: {job_edu}"

        # 5. 检查黑名单公司
        if self.rules.blacklist_companies:
            company = job.get('company_name', '')
            if any(black in company for black in self.rules.blacklist_companies):
                return False, f"黑名单公司: {company}"

        return True, "通过"

    def _parse_salary(self, salary_text: str) -> Optional[int]:
        """解析薪资文本，返回最低薪资（元/月）"""
        if not salary_text:
            return None

        # 匹配 "15-25K" 或 "15K-25K" 格式
        k_match = re.search(r'(\d+)[-K~]+(\d+)[K千]', salary_text, re.IGNORECASE)
        if k_match:
            return int(k_match.group(1)) * 1000

        # 匹配 "15000-25000" 格式
        num_match = re.search(r'(\d{4,5})\s*[-~]\s*\d{4,5}', salary_text)
        if num_match:
            return int(num_match.group(1))

        # 匹配单个数字
        single_match = re.search(r'(\d+)[K千]', salary_text, re.IGNORECASE)
        if single_match:
            return int(single_match.group(1)) * 1000

        return None

    def _parse_work_years(self, exp_text: str) -> Optional[int]:
        """解析工作年限要求"""
        if not exp_text:
            return None

        # 匹配 "3-5年" 或 "3年以上" 格式
        match = re.search(r'(\d+)\s*[-~]?\s*\d*\s*年', exp_text)
        if match:
            return int(match.group(1))

        # 匹配 "经验不限"
        if '不限' in exp_text or '经验不限' in exp_text:
            return 0

        return None

    def _check_education(self, job_edu: str, min_edu: str) -> bool:
        """检查学历是否满足最低要求"""
        if not job_edu or not min_edu:
            return True

        job_level = self.EDUCATION_LEVEL.get(job_edu, 0)
        min_level = self.EDUCATION_LEVEL.get(min_edu, 0)

        return job_level >= min_level

    def get_stats(self) -> Dict[str, int]:
        """获取过滤统计信息"""
        return {
            'passed': self.passed_count,
            'rejected': self.rejected_count,
            'total': self.passed_count + self.rejected_count
        }
