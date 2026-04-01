#!/usr/bin/env python3
"""
优势优先匹配策略引擎

核心思想：优先匹配能发挥个人优势的岗位，而不是盲目追求大厂
"""

import yaml
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class Strength:
    """个人优势定义"""
    name: str
    description: str
    weight: float
    keywords: List[str]


@dataclass
class StrengthCombination:
    """优势组合"""
    name: str
    description: str
    bonus: float
    conditions: List[str]


@dataclass
class JobType:
    """岗位类型定义"""
    name: str
    description: str
    strength_requirements: List[str]
    companies: List[str] = field(default_factory=list)


class StrengthFirstStrategy:
    """
    优势优先匹配策略引擎
    
    核心功能：
    1. 分析个人优势
    2. 计算岗位与优势的匹配度
    3. 基于优势匹配度进行排序
    4. 生成优势优先的投递策略
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """初始化策略引擎"""
        self.config_path = config_path or Path(__file__).parent.parent.parent.parent / 'conf' / 'strength_first_strategy.yaml'
        self.config: Dict = {}
        self.strengths: Dict[str, Strength] = {}
        self.strength_combinations: Dict[str, StrengthCombination] = {}
        self.job_types: Dict[str, JobType] = {}
        
        self._load_config()
        logger.info(f"优势优先策略引擎初始化完成，加载了 {len(self.strengths)} 个优势")
    
    def _load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"优势优先配置文件加载成功: {self.config_path}")
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            raise
        
        # 解析优势配置
        strengths_config = self.config.get('strengths_analysis', {}).get('core_advantages', [])
        for strength_config in strengths_config:
            strength = Strength(
                name=strength_config['name'],
                description=strength_config['description'],
                weight=strength_config['weight'],
                keywords=strength_config['keywords']
            )
            self.strengths[strength.name] = strength
        
        # 解析优势组合
        combinations_config = self.config.get('strengths_analysis', {}).get('strength_combinations', [])
        for combo_config in combinations_config:
            combo = StrengthCombination(
                name=combo_config['name'],
                description=combo_config['description'],
                bonus=combo_config['bonus'],
                conditions=combo_config['conditions']
            )
            self.strength_combinations[combo.name] = combo
        
        # 解析岗位类型
        job_types_config = self.config.get('target_job_types', {}).get('perfect_fit', [])
        for job_type_config in job_types_config:
            job_type = JobType(
                name=job_type_config['name'],
                description=job_type_config['description'],
                strength_requirements=job_type_config['strength_requirements'],
                companies=job_type_config.get('companies', [])
            )
            self.job_types[job_type.name] = job_type
    
    def analyze_personal_strengths(self, resume: Dict) -> Dict[str, float]:
        """
        分析个人优势强度
        
        Args:
            resume: 简历数据
            
        Returns:
            优势名称到强度的映射
        """
        strengths_scores = {}
        
        # 获取简历技能
        resume_skills = set(resume.get('skills', []))
        
        for strength_name, strength in self.strengths.items():
            # 计算优势匹配度
            matched_keywords = []
            for keyword in strength.keywords:
                if any(keyword.lower() in skill.lower() for skill in resume_skills):
                    matched_keywords.append(keyword)
            
            # 优势强度 = 匹配关键词数 / 总关键词数 * 权重
            if strength.keywords:
                match_ratio = len(matched_keywords) / len(strength.keywords)
                strength_score = match_ratio * strength.weight
                strengths_scores[strength_name] = strength_score
                
                logger.debug(f"优势 '{strength_name}': 匹配度 {match_ratio:.2f}, 强度 {strength_score:.3f}")
        
        return strengths_scores
    
    def calculate_strength_match_score(self, job: Dict, personal_strengths: Dict[str, float]) -> float:
        """
        计算岗位与个人优势的匹配度
        
        Args:
            job: 岗位数据
            personal_strengths: 个人优势强度
            
        Returns:
            优势匹配度 (0-1)
        """
        job_text = f"{job.get('job_name', '')} {job.get('job_description', '')} {job.get('job_requirement', '')}"
        job_text_lower = job_text.lower()
        
        total_score = 0.0
        matched_strengths = []
        
        # 检查每个优势是否与岗位匹配
        for strength_name, strength_score in personal_strengths.items():
            strength = self.strengths.get(strength_name)
            if not strength:
                continue
            
            # 检查优势关键词是否出现在岗位描述中
            matched_keywords = []
            for keyword in strength.keywords:
                if keyword.lower() in job_text_lower:
                    matched_keywords.append(keyword)
            
            if matched_keywords:
                # 优势匹配度 = 匹配关键词数 / 总关键词数 * 优势强度
                match_ratio = len(matched_keywords) / len(strength.keywords)
                strength_match_score = match_ratio * strength_score
                total_score += strength_match_score
                matched_strengths.append((strength_name, strength_match_score))
                
                logger.debug(f"岗位匹配优势 '{strength_name}': 关键词 {matched_keywords}, 匹配度 {strength_match_score:.3f}")
        
        # 检查优势组合加分
        combo_bonus = self._calculate_combo_bonus(matched_strengths, job_text_lower)
        total_score += combo_bonus
        
        return min(1.0, total_score)
    
    def _calculate_combo_bonus(self, matched_strengths: List[Tuple[str, float]], job_text: str) -> float:
        """计算优势组合加分"""
        bonus = 0.0
        matched_strength_names = [name for name, _ in matched_strengths]
        
        for combo_name, combo in self.strength_combinations.items():
            # 检查是否满足组合条件
            conditions_met = all(condition in matched_strength_names for condition in combo.conditions)
            
            if conditions_met:
                # 检查组合关键词是否出现在岗位描述中
                combo_keywords = []
                for condition in combo.conditions:
                    strength = self.strengths.get(condition)
                    if strength:
                        combo_keywords.extend(strength.keywords)
                
                # 检查组合关键词匹配
                matched_combo_keywords = [kw for kw in combo_keywords if kw.lower() in job_text]
                if matched_combo_keywords:
                    bonus += combo.bonus
                    logger.debug(f"优势组合 '{combo_name}': 加分 {combo.bonus}")
        
        return bonus
    
    def rank_jobs_by_strength_match(
        self,
        jobs: List[Dict],
        resume: Dict,
        base_match_scores: Optional[Dict[str, float]] = None
    ) -> List[Dict]:
        """
        基于优势匹配度对岗位进行排序
        
        Args:
            jobs: 岗位列表
            resume: 简历数据
            base_match_scores: 基础匹配分数（可选）
            
        Returns:
            排序后的岗位列表
        """
        # 分析个人优势
        personal_strengths = self.analyze_personal_strengths(resume)
        
        print(f"\n🎯 个人优势分析:")
        for strength_name, score in sorted(personal_strengths.items(), key=lambda x: x[1], reverse=True):
            strength = self.strengths.get(strength_name)
            if strength:
                print(f"  {strength_name}: {score:.3f} - {strength.description}")
        
        # 计算每个岗位的优势匹配度
        ranked_jobs = []
        
        for job in jobs:
            job_id = job.get('source_job_id', '')
            
            # 基础匹配分数
            base_score = base_match_scores.get(job_id, 0.5) if base_match_scores else 0.5
            
            # 优势匹配分数
            strength_score = self.calculate_strength_match_score(job, personal_strengths)
            
            # 综合分数（优势优先权重）
            weights = self.config.get('strength_matching_weights', {}).get('strength_first', {})
            skill_weight = weights.get('skill_match', 0.25)
            strength_weight = weights.get('strength_match', 0.60)
            semantic_weight = weights.get('semantic_match', 0.15)
            
            # 简化计算：综合分数 = 基础分数 * 技能权重 + 优势分数 * 优势权重
            composite_score = base_score * skill_weight + strength_score * strength_weight
            
            # 获取匹配的优势
            matched_strengths = self._get_matched_strengths(job, personal_strengths)
            
            ranked_jobs.append({
                'job': job,
                'base_match_score': base_score,
                'strength_match_score': strength_score,
                'composite_score': composite_score,
                'matched_strengths': matched_strengths,
                'job_type': self._classify_job_type(job)
            })
        
        # 按综合分数排序
        ranked_jobs.sort(key=lambda x: x['composite_score'], reverse=True)
        
        return ranked_jobs
    
    def _get_matched_strengths(self, job: Dict, personal_strengths: Dict[str, float]) -> List[str]:
        """获取岗位匹配的优势列表"""
        job_text = f"{job.get('job_name', '')} {job.get('job_description', '')}".lower()
        matched = []
        
        for strength_name, strength_score in personal_strengths.items():
            strength = self.strengths.get(strength_name)
            if not strength:
                continue
            
            # 检查优势关键词是否出现在岗位描述中
            for keyword in strength.keywords:
                if keyword.lower() in job_text:
                    matched.append(strength_name)
                    break
        
        return matched
    
    def _classify_job_type(self, job: Dict) -> str:
        """分类岗位类型"""
        job_text = f"{job.get('job_name', '')} {job.get('job_description', '')}".lower()
        
        # 检查是否属于完美匹配的岗位类型
        for job_type_name, job_type in self.job_types.items():
            # 检查岗位名称或描述中是否包含岗位类型关键词
            if job_type_name.lower() in job_text:
                return job_type_name
            
            # 检查公司是否在目标公司列表中
            company_name = job.get('company_name', '').lower()
            for target_company in job_type.companies:
                if target_company.lower() in company_name:
                    return job_type_name
        
        return "其他"
    
    def generate_strength_first_report(
        self,
        ranked_jobs: List[Dict],
        resume: Dict,
        output_path: Path
    ) -> Path:
        """生成优势优先匹配报告"""
        
        personal_strengths = self.analyze_personal_strengths(resume)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# ResuMiner 优势优先匹配报告\n\n")
            f.write("## 🎯 个人优势分析\n\n")
            
            # 优势分析
            f.write("| 优势名称 | 强度 | 描述 |\n")
            f.write("|---------|------|------|\n")
            for strength_name, score in sorted(personal_strengths.items(), key=lambda x: x[1], reverse=True):
                strength = self.strengths.get(strength_name)
                if strength:
                    f.write(f"| {strength_name} | {score:.3f} | {strength.description} |\n")
            
            f.write("\n## 🏆 优势优先匹配 Top 20\n\n")
            
            # 岗位匹配结果
            f.write("| 排名 | 岗位 | 公司 | 优势匹配度 | 综合分数 | 匹配优势 |\n")
            f.write("|------|------|------|-----------|----------|----------|\n")
            
            for i, item in enumerate(ranked_jobs[:20], 1):
                job = item['job']
                f.write(f"| {i} | {job.get('job_name', '')} | "
                       f"{job.get('company_name', '')} | "
                       f"{item['strength_match_score']*100:.1f}% | "
                       f"{item['composite_score']*100:.1f}% | "
                       f"{', '.join(item['matched_strengths'][:2])} |\n")
            
            # 投递建议
            f.write("\n## 🚀 投递策略建议\n\n")
            f.write("### 优先级排序\n\n")
            f.write("1. **金融科技岗位** - 完美匹配财务+技术复合优势\n")
            f.write("2. **量化开发岗位** - 发挥Python+金融背景优势\n")
            f.write("3. **技术产品经理** - 技术+产品思维复合优势\n")
            f.write("4. **AI应用工程师** - AI技术+业务应用优势\n\n")
            
            f.write("### 简历优化建议\n\n")
            f.write("- **金融科技公司**: 突出财务知识+编程能力\n")
            f.write("- **AI技术公司**: 强调AI模型部署+数据处理能力\n")
            f.write("- **互联网大厂**: 展示全栈开发+项目经验\n")
        
        logger.info(f"优势优先报告已生成: {output_path}")
        return output_path


# 单例模式
_strength_strategy_instance: Optional[StrengthFirstStrategy] = None


def get_strength_strategy(config_path: Optional[Path] = None) -> StrengthFirstStrategy:
    """获取优势优先策略引擎单例"""
    global _strength_strategy_instance
    if _strength_strategy_instance is None:
        _strength_strategy_instance = StrengthFirstStrategy(config_path)
    return _strength_strategy_instance