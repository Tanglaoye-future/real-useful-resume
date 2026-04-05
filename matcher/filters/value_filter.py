"""
高价值岗位筛选模块

实现漏斗式筛选的第二阶段：高价值岗位筛选
基于公司分级、岗位含金量、投递成功率等多维度评估
"""

import logging
import re
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class CompanyTier(Enum):
    """公司分级"""
    TIER_1 = 1  # 一线大厂
    TIER_2 = 2  # 二线大厂/知名独角兽
    TIER_3 = 3  # 中厂/优质创业公司
    TIER_4 = 4  # 小厂/普通公司
    UNKNOWN = 5  # 未知


class JobValueLevel(Enum):
    """岗位价值等级"""
    HIGH = "高价值"
    MEDIUM = "中价值"
    LOW = "低价值"
    FILTERED = "已过滤"


@dataclass
class ValueFilterConfig:
    """高价值筛选配置"""
    # 公司分级权重
    tier_weights: Dict[CompanyTier, float] = field(default_factory=lambda: {
        CompanyTier.TIER_1: 1.0,
        CompanyTier.TIER_2: 0.8,
        CompanyTier.TIER_3: 0.6,
        CompanyTier.TIER_4: 0.3,
        CompanyTier.UNKNOWN: 0.5
    })

    # 最低公司等级要求（默认接受TIER_3及以上）
    min_company_tier: CompanyTier = CompanyTier.TIER_3

    # 岗位关键词加分
    high_value_keywords: List[str] = field(default_factory=lambda: [
        "产品经理", "产品实习", "策略产品", "数据产品",
        "增长产品", "商业化产品", "AI产品", "B端产品"
    ])

    # 技术难度过高关键词（过滤）
    high_tech_keywords: List[str] = field(default_factory=lambda: [
        "算法工程师", "机器学习", "深度学习", "计算机视觉",
        "自然语言处理", "推荐算法", "搜索算法", "自动驾驶",
        "量化交易", "区块链开发", "底层开发", "内核开发"
    ])

    # 低价值关键词（过滤）
    low_value_keywords: List[str] = field(default_factory=lambda: [
        "销售", "客服", "地推", "电销", "催收", "外包",
        "兼职", "日结", "小时工", "劳务派遣"
    ])

    # 薪资评分阈值
    min_salary_score: float = 0.5

    # 投递成功率阈值
    min_success_rate: float = 0.3


class CompanyClassifier:
    """公司分级分类器"""

    # 一线大厂
    TIER_1_COMPANIES = [
        "字节跳动", "ByteDance", "抖音", "TikTok",
        "阿里巴巴", "Alibaba", "淘宝", "天猫", "蚂蚁集团",
        "腾讯", "Tencent", "微信", "QQ",
        "百度", "Baidu",
        "美团", "Meituan",
        "京东", "JD",
        "拼多多", "PDD",
        "快手", "Kuaishou",
        "小红书", "Xiaohongshu",
        "网易", "NetEase",
        "华为", "Huawei",
        "小米", "Xiaomi"
    ]

    # 二线大厂/知名独角兽
    TIER_2_COMPANIES = [
        "哔哩哔哩", "Bilibili", "B站",
        "携程", "Ctrip",
        "滴滴", "Didi",
        "蔚来", "NIO",
        "理想汽车", "Li Auto",
        "小鹏汽车", "XPeng",
        "贝壳", "Beike",
        "知乎", "Zhihu",
        "得物", "Dewu",
        "米哈游", "MiHoYo",
        "莉莉丝", "Lilith",
        "商汤", "SenseTime",
        "旷视", "Megvii",
        "科大讯飞", "iFlytek",
        "用友", "Yonyou",
        "金蝶", "Kingdee",
        "深信服", "Sangfor",
        "奇安信", "QiAnXin"
    ]

    # 中厂/优质创业公司
    TIER_3_COMPANIES = [
        "BOSS直聘", "BOSS Zhipin",
        "猎聘", "Liepin",
        "拉勾", "Lagou",
        "智联", "Zhaopin",
        "前程无忧", "51job",
        "斗鱼", "Douyu",
        "虎牙", "Huya",
        "欢聚", "JOYY",
        "映客", "Inke",
        "陌陌", "Momo",
        "探探", "Tantan",
        "Soul",
        "Keep",
        "喜马拉雅", "Ximalaya",
        "蜻蜓FM", "Qingting",
        "网易云音乐", "NetEase Music"
    ]

    @classmethod
    def classify(cls, company_name: str) -> CompanyTier:
        """根据公司名称判断等级"""
        if not company_name:
            return CompanyTier.UNKNOWN

        company_name = company_name.lower()

        for company in cls.TIER_1_COMPANIES:
            if company.lower() in company_name:
                return CompanyTier.TIER_1

        for company in cls.TIER_2_COMPANIES:
            if company.lower() in company_name:
                return CompanyTier.TIER_2

        for company in cls.TIER_3_COMPANIES:
            if company.lower() in company_name:
                return CompanyTier.TIER_3

        return CompanyTier.TIER_4


class ValueFilter:
    """高价值岗位筛选器"""

    def __init__(self, config: ValueFilterConfig = None):
        self.config = config or ValueFilterConfig()
        self.classifier = CompanyClassifier()
        self.stats = {
            'high_value': 0,
            'medium_value': 0,
            'low_value': 0,
            'filtered': 0
        }

    def filter(self, jobs: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        执行高价值筛选

        Args:
            jobs: 已通过硬性过滤的岗位列表

        Returns:
            (高价值岗位列表, 低价值/已过滤岗位列表)
        """
        high_value_jobs = []
        filtered_jobs = []

        for job in jobs:
            result = self._evaluate_job(job)
            job['value_level'] = result['level'].value
            job['value_score'] = result['score']
            job['value_factors'] = result['factors']

            if result['level'] in [JobValueLevel.HIGH, JobValueLevel.MEDIUM]:
                high_value_jobs.append(job)
                if result['level'] == JobValueLevel.HIGH:
                    self.stats['high_value'] += 1
                else:
                    self.stats['medium_value'] += 1
            else:
                job['filter_reason'] = result['reason']
                filtered_jobs.append(job)
                if result['level'] == JobValueLevel.LOW:
                    self.stats['low_value'] += 1
                else:
                    self.stats['filtered'] += 1

        logger.info(f"高价值筛选完成: 高价值{self.stats['high_value']}, "
                   f"中价值{self.stats['medium_value']}, "
                   f"低价值{self.stats['low_value']}, "
                   f"已过滤{self.stats['filtered']}")

        # 按价值分数排序
        high_value_jobs.sort(key=lambda x: x.get('value_score', 0), reverse=True)

        return high_value_jobs, filtered_jobs

    def _evaluate_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """评估单个岗位的价值"""
        factors = {}
        score = 0.0

        # 1. 公司分级评分 (权重: 30%)
        company_name = job.get('company_name', '')
        company_tier = self.classifier.classify(company_name)
        company_score = self.config.tier_weights.get(company_tier, 0.5)
        factors['company_tier'] = company_tier.name
        factors['company_score'] = company_score
        score += company_score * 0.3

        # 检查最低公司等级要求
        if company_tier.value > self.config.min_company_tier.value:
            return {
                'level': JobValueLevel.FILTERED,
                'score': score,
                'factors': factors,
                'reason': f"公司等级过低: {company_tier.name}"
            }

        # 2. 岗位类型评分 (权重: 25%)
        job_title = job.get('job_name', '') + ' ' + job.get('job_description', '')
        job_type_score = self._evaluate_job_type(job_title)
        factors['job_type_score'] = job_type_score
        score += job_type_score * 0.25

        # 检查技术难度
        if self._has_high_tech_keywords(job_title):
            return {
                'level': JobValueLevel.FILTERED,
                'score': score,
                'factors': factors,
                'reason': "技术难度过高，不适合产品岗位投递"
            }

        # 检查低价值关键词
        if self._has_low_value_keywords(job_title):
            return {
                'level': JobValueLevel.FILTERED,
                'score': score,
                'factors': factors,
                'reason': "低价值岗位类型"
            }

        # 3. 薪资评分 (权重: 20%)
        salary_score = self._evaluate_salary(job.get('salary', ''))
        factors['salary_score'] = salary_score
        score += salary_score * 0.2

        # 4. 投递成功率评分 (权重: 15%)
        success_rate_score = self._evaluate_success_rate(job)
        factors['success_rate_score'] = success_rate_score
        score += success_rate_score * 0.15

        # 5. 其他加分项 (权重: 10%)
        bonus_score = self._evaluate_bonus_factors(job)
        factors['bonus_score'] = bonus_score
        score += bonus_score * 0.1

        # 确定价值等级
        if score >= 0.75:
            level = JobValueLevel.HIGH
        elif score >= 0.5:
            level = JobValueLevel.MEDIUM
        else:
            level = JobValueLevel.LOW

        return {
            'level': level,
            'score': round(score, 2),
            'factors': factors,
            'reason': None
        }

    def _evaluate_job_type(self, job_text: str) -> float:
        """评估岗位类型价值"""
        if not job_text:
            return 0.5

        job_text = job_text.lower()

        # 高价值关键词匹配
        high_value_matches = sum(1 for keyword in self.config.high_value_keywords
                                if keyword.lower() in job_text)

        if high_value_matches >= 2:
            return 1.0
        elif high_value_matches == 1:
            return 0.8
        elif "产品" in job_text:
            return 0.6
        else:
            return 0.4

    def _has_high_tech_keywords(self, job_text: str) -> bool:
        """检查是否包含高技术难度关键词"""
        if not job_text:
            return False

        job_text = job_text.lower()
        return any(keyword.lower() in job_text
                  for keyword in self.config.high_tech_keywords)

    def _has_low_value_keywords(self, job_text: str) -> bool:
        """检查是否包含低价值关键词"""
        if not job_text:
            return False

        job_text = job_text.lower()
        return any(keyword.lower() in job_text
                  for keyword in self.config.low_value_keywords)

    def _evaluate_salary(self, salary_text: str) -> float:
        """评估薪资水平 (0-1分)"""
        if not salary_text:
            return 0.5

        # 提取薪资数字
        # 匹配 "15-25K" 格式
        k_match = re.search(r'(\d+)[-~]+(\d+)[K千]', salary_text, re.IGNORECASE)
        if k_match:
            min_salary = int(k_match.group(1))
            max_salary = int(k_match.group(2))
            avg_salary = (min_salary + max_salary) / 2

            # 实习生日薪评分标准
            if avg_salary >= 300:  # 300元/天以上
                return 1.0
            elif avg_salary >= 200:
                return 0.8
            elif avg_salary >= 150:
                return 0.6
            elif avg_salary >= 100:
                return 0.4
            else:
                return 0.2

        # 匹配 "15000-25000" 格式 (月薪)
        num_match = re.search(r'(\d{4,5})\s*[-~]\s*\d{4,5}', salary_text)
        if num_match:
            salary = int(num_match.group(1))
            # 转换为日薪估算 (月薪/21.75)
            daily_salary = salary / 21.75

            if daily_salary >= 300:
                return 1.0
            elif daily_salary >= 200:
                return 0.8
            elif daily_salary >= 150:
                return 0.6
            else:
                return 0.4

        return 0.5

    def _evaluate_success_rate(self, job: Dict[str, Any]) -> float:
        """评估投递成功率"""
        score = 0.5  # 基础分

        # 根据公司等级调整
        company_name = job.get('company_name', '')
        company_tier = self.classifier.classify(company_name)

        # 一线大厂竞争激烈，成功率相对较低
        if company_tier == CompanyTier.TIER_1:
            score -= 0.1
        elif company_tier == CompanyTier.TIER_3:
            score += 0.1  # 中厂竞争相对较小

        # 根据JD完整度判断
        jd = job.get('job_description', '')
        if jd and len(jd) > 200:
            score += 0.1

        # 根据发布时间判断 (越新越好)
        # 这里简化处理，实际可以解析时间字段

        return min(max(score, 0.0), 1.0)

    def _evaluate_bonus_factors(self, job: Dict[str, Any]) -> float:
        """评估其他加分项"""
        score = 0.0

        # JD完整度
        jd = job.get('job_description', '')
        if jd:
            if len(jd) > 500:
                score += 0.4
            elif len(jd) > 300:
                score += 0.3
            elif len(jd) > 100:
                score += 0.2

        # 有明确的技能要求（说明岗位定义清晰）
        requirements = job.get('requirements', '')
        if requirements and len(requirements) > 50:
            score += 0.3

        # 有福利描述
        benefits = job.get('benefits', '')
        if benefits:
            score += 0.3

        return min(score, 1.0)

    def get_stats(self) -> Dict[str, int]:
        """获取筛选统计信息"""
        return self.stats.copy()

    def get_tier_distribution(self, jobs: List[Dict[str, Any]]) -> Dict[str, int]:
        """获取公司等级分布统计"""
        distribution = {tier.name: 0 for tier in CompanyTier}

        for job in jobs:
            company_name = job.get('company_name', '')
            tier = self.classifier.classify(company_name)
            distribution[tier.name] += 1

        return distribution
