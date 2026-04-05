# -*- coding: utf-8 -*-
"""
企业-候选人适配匹配模块
实现人-企适配特征计算，解决"能胜任但不愿意去小公司"的问题
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from .enterprise_profiler import EnterpriseProfile


@dataclass
class EnterpriseMatchResult:
    """企业适配匹配结果"""
    industry_match_score: float = 0.0       # 行业赛道适配得分
    scale_match_score: float = 0.0          # 规模与职业适配得分
    stage_match_score: float = 0.0          # 发展阶段适配得分
    culture_match_score: float = 0.0        # 工作模式适配得分
    total_score: float = 0.0                # 总适配得分
    
    # 详细说明
    industry_reason: str = ""               # 行业匹配说明
    scale_reason: str = ""                  # 规模匹配说明
    stage_reason: str = ""                  # 阶段匹配说明
    culture_reason: str = ""                # 文化匹配说明
    
    def to_dict(self) -> Dict:
        return asdict(self)


class EnterpriseMatcher:
    """
    企业-候选人适配匹配器
    计算候选人与企业的适配度，提升中小微企业匹配转化率
    """
    
    # 权重配置（可调整）
    WEIGHTS = {
        'industry': 0.40,      # 行业赛道适配 40%
        'scale': 0.30,         # 规模与职业适配 30%
        'stage': 0.20,         # 发展阶段适配 20%
        'culture': 0.10,       # 工作模式适配 10%
    }
    
    # 行业相关性映射
    INDUSTRY_RELATED = {
        "互联网/电商": ["互联网/SaaS", "互联网/金融科技", "互联网/物流"],
        "互联网/SaaS": ["互联网/电商", "企业服务", "互联网/金融科技"],
        "互联网/游戏": ["互联网/社交", "互联网/教育"],
        "人工智能": ["互联网/SaaS", "软件和信息技术服务业", "互联网/金融科技"],
        "新能源": ["先进制造", "互联网/物流"],
        "生物医药": ["互联网/医疗", "互联网/教育"],
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        初始化匹配器
        
        Args:
            weights: 自定义权重配置
        """
        if weights:
            self.weights = weights
        else:
            self.weights = self.WEIGHTS
    
    def match(self, resume: Dict[str, Any], enterprise: EnterpriseProfile) -> EnterpriseMatchResult:
        """
        计算候选人与企业的适配度
        
        Args:
            resume: 简历数据（已结构化）
            enterprise: 企业画像
            
        Returns:
            EnterpriseMatchResult: 适配匹配结果
        """
        result = EnterpriseMatchResult()
        
        # 1. 行业赛道适配 (40%)
        result.industry_match_score, result.industry_reason = self._match_industry(
            resume.get('past_industries', []),
            enterprise.gb_industry,
            enterprise.segment
        )
        
        # 2. 规模与职业适配 (30%)
        result.scale_match_score, result.scale_reason = self._match_scale(
            resume.get('past_company_scale', ''),
            resume.get('total_work_year', 0),
            enterprise.scale
        )
        
        # 3. 发展阶段适配 (20%)
        result.stage_match_score, result.stage_reason = self._match_stage(
            resume.get('job_demand', ''),
            enterprise.development_stage,
            enterprise.found_year
        )
        
        # 4. 工作模式适配 (10%)
        result.culture_match_score, result.culture_reason = self._match_culture(
            resume.get('target_work_mode', ''),
            enterprise.culture
        )
        
        # 计算总得分
        result.total_score = (
            result.industry_match_score * self.weights['industry'] +
            result.scale_match_score * self.weights['scale'] +
            result.stage_match_score * self.weights['stage'] +
            result.culture_match_score * self.weights['culture']
        )
        
        return result
    
    def _match_industry(self, past_industries: List[str], 
                        enterprise_industry: str, 
                        enterprise_segment: str) -> tuple:
        """
        行业赛道适配匹配
        
        Returns:
            (得分, 说明)
        """
        if not past_industries:
            return 50.0, "无过往行业信息，默认中等适配"
        
        # 检查是否完全一致
        for past in past_industries:
            if past == enterprise_industry or past in enterprise_segment:
                return 100.0, f"行业完全一致：{past}"
        
        # 检查是否相关
        for past in past_industries:
            if past in self.INDUSTRY_RELATED:
                related = self.INDUSTRY_RELATED[past]
                if enterprise_industry in related or any(r in enterprise_segment for r in related):
                    return 70.0, f"行业相关：{past} → {enterprise_industry}"
        
        # 跨行业
        return 30.0, f"跨行业：{past_industries[0]} → {enterprise_industry}"
    
    def _match_scale(self, past_scale: str, work_years: float, 
                     enterprise_scale: str) -> tuple:
        """
        规模与职业适配匹配
        
        逻辑：
        - 应届生/1年内：适合小型/中型企业（成长快）
        - 1-3年：适合中型/大型企业（稳定发展）
        - 3-5年：适合大型/中型企业（技术深度）
        - 5年+：适合大型/中型企业（管理经验）
        
        Returns:
            (得分, 说明)
        """
        scale_order = {"微型": 1, "小型": 2, "中型": 3, "大型": 4, "未知": 2}
        
        past_scale_val = scale_order.get(past_scale, 2)
        enterprise_scale_val = scale_order.get(enterprise_scale, 2)
        
        # 根据工作年限判断适配度
        if work_years < 1:
            # 应届生适合小型/中型
            if enterprise_scale in ["小型", "中型"]:
                return 100.0, f"应届生适合{enterprise_scale}企业，成长空间大"
            elif enterprise_scale == "微型":
                return 70.0, "微型企业风险较高，但机会多"
            else:
                return 60.0, "大型企业体系完善但成长慢"
        
        elif work_years < 3:
            # 1-3年适合中型/大型
            if enterprise_scale in ["中型", "大型"]:
                return 100.0, f"{work_years}年经验适合{enterprise_scale}企业稳定发展"
            elif enterprise_scale == "小型":
                return 70.0, "小型企业机会多但稳定性差"
            else:
                return 50.0, "微型企业风险较高"
        
        else:
            # 3年+适合大型/中型
            if enterprise_scale == "大型":
                return 100.0, f"{work_years}年经验适合大型企业发挥价值"
            elif enterprise_scale == "中型":
                return 80.0, "中型企业有发展空间"
            else:
                return 50.0, "小型/微型企业可能限制发展"
    
    def _match_stage(self, job_demand: str, enterprise_stage: str, 
                     found_year: int) -> tuple:
        """
        发展阶段适配匹配
        
        逻辑：
        - 求稳定 → 成熟期/上市期
        - 求成长 → 成长期
        - 求创业机会 → 初创期
        
        Returns:
            (得分, 说明)
        """
        demand_stage_map = {
            "求稳定": ["成熟期", "上市期"],
            "求成长": ["成长期", "成熟期"],
            "求创业机会": ["初创期", "成长期"],
        }
        
        if not job_demand:
            return 70.0, "无明确求职诉求，默认中等适配"
        
        suitable_stages = demand_stage_map.get(job_demand, [])
        
        if enterprise_stage in suitable_stages:
            if job_demand == "求稳定":
                return 100.0, f"{enterprise_stage}企业稳定性高，符合求稳诉求"
            elif job_demand == "求成长":
                return 100.0, f"{enterprise_stage}企业成长空间大，符合成长诉求"
            else:
                return 100.0, f"{enterprise_stage}企业创业机会多，符合创业诉求"
        
        # 不匹配但相关
        if job_demand == "求稳定" and enterprise_stage in ["成长期"]:
            return 60.0, "成长期企业稳定性一般，但发展较好"
        elif job_demand == "求成长" and enterprise_stage in ["初创期", "上市期"]:
            return 70.0, f"{enterprise_stage}企业成长空间中等"
        elif job_demand == "求创业机会" and enterprise_stage in ["成熟期"]:
            return 40.0, "成熟期企业创业机会较少"
        
        return 30.0, f"{enterprise_stage}企业与求职诉求'{job_demand}'匹配度低"
    
    def _match_culture(self, target_work_mode: str, enterprise_culture: str) -> tuple:
        """
        工作模式适配匹配
        
        Returns:
            (得分, 说明)
        """
        if not target_work_mode or not enterprise_culture:
            return 70.0, "信息不足，默认中等适配"
        
        # 检查是否一致
        if target_work_mode in enterprise_culture:
            return 100.0, f"工作模式完全匹配：{target_work_mode}"
        
        # 检查冲突
        conflicts = {
            "弹性工作": ["996", "大小周"],
            "稳定": ["狼性", "创业"],
        }
        
        for mode, conflict_list in conflicts.items():
            if mode in target_work_mode:
                for conflict in conflict_list:
                    if conflict in enterprise_culture:
                        return 30.0, f"工作模式冲突：期望{mode} vs 实际{conflict}"
        
        return 70.0, "工作模式无明显冲突"
    
    def batch_match(self, resume: Dict[str, Any], 
                    enterprises: Dict[str, EnterpriseProfile]) -> Dict[str, EnterpriseMatchResult]:
        """
        批量计算候选人与多个企业的适配度
        
        Args:
            resume: 简历数据
            enterprises: 企业名称到画像的映射
            
        Returns:
            Dict[str, EnterpriseMatchResult]: 企业名称到匹配结果的映射
        """
        results = {}
        for company_name, enterprise in enterprises.items():
            result = self.match(resume, enterprise)
            results[company_name] = result
        return results
    
    def get_match_level(self, score: float) -> str:
        """
        获取匹配等级
        
        Args:
            score: 适配得分
            
        Returns:
            str: 匹配等级
        """
        if score >= 80:
            return "强适配"
        elif score >= 60:
            return "中适配"
        else:
            return "弱适配"


# 测试代码
if __name__ == "__main__":
    from enterprise_profiler import EnterpriseProfiler
    
    # 创建测试数据
    profiler = EnterpriseProfiler()
    
    test_jd = """
    杭州XX科技有限公司成立于2020年，是一家专注于HR SaaS服务的初创企业。
    团队规模30人，已获得A轮融资。
    主营产品：智能招聘系统、简历匹配平台。
    企业文化：扁平化、弹性工作制、创业氛围。
    """
    
    enterprise = profiler.extract_from_jd(test_jd, "杭州XX科技有限公司")
    
    # 测试简历
    resume = {
        "past_industries": ["互联网/SaaS", "企业服务"],
        "past_company_scale": "中型",
        "total_work_year": 2.5,
        "job_demand": "求成长",
        "target_work_mode": "弹性工作制"
    }
    
    # 匹配
    matcher = EnterpriseMatcher()
    result = matcher.match(resume, enterprise)
    
    print("企业-候选人适配匹配结果：")
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    print(f"\n匹配等级：{matcher.get_match_level(result.total_score)}")
