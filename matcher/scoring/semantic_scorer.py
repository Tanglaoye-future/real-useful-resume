"""
语义打分模块

实现漏斗式筛选的第二阶段：语义召回与打分
"""

import logging
import numpy as np
from typing import Dict, Any, List, Tuple, Optional

logger = logging.getLogger(__name__)


class SemanticScorer:
    """语义匹配打分器"""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        初始化语义模型

        Args:
            model_name: 使用的向量化模型名称
        """
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """加载语义模型"""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"加载语义模型: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
        except ImportError:
            logger.warning("sentence-transformers 未安装，语义打分功能将不可用")
            self.model = None
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            self.model = None

    def encode_text(self, text: str) -> Optional[np.ndarray]:
        """将文本编码为向量"""
        if self.model is None:
            return None
        try:
            return self.model.encode(text)
        except Exception as e:
            logger.error(f"文本编码失败: {e}")
            return None

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两段文本的语义相似度

        Args:
            text1: 第一段文本
            text2: 第二段文本

        Returns:
            0-1 之间的相似度分数
        """
        if self.model is None:
            # 降级为关键词匹配
            return self._keyword_similarity(text1, text2)

        emb1 = self.encode_text(text1)
        emb2 = self.encode_text(text2)

        if emb1 is None or emb2 is None:
            return 0.0

        # 计算余弦相似度
        cos_sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(cos_sim)

    def score_job(self, resume: Dict[str, Any], job: Dict[str, Any],
                  weights: Dict[str, float] = None) -> Dict[str, float]:
        """
        计算简历与岗位的匹配分数

        Args:
            resume: 结构化简历数据
            job: 岗位数据
            weights: 各维度权重配置，默认使用优化后的权重

        Returns:
            包含各维度分数的字典
        """
        scores = {}

        # 1. 构建简历文本
        resume_text = self._build_resume_text(resume)

        # 2. 构建岗位文本
        job_text = self._build_job_text(job)

        # 3. 计算整体语义相似度
        scores['semantic'] = self.calculate_similarity(resume_text, job_text)

        # 4. 技能匹配度
        scores['skill'] = self._calculate_skill_match(resume, job)

        # 5. 经验匹配度
        scores['experience'] = self._calculate_experience_match(resume, job)

        # 6. 计算综合得分（可配置权重）
        # 默认使用优化后的权重：技能 45%, 语义 30%, 经验 25%
        default_weights = {
            'skill': 0.45,
            'semantic': 0.30,
            'experience': 0.25
        }

        # 使用传入的权重或默认权重
        weights = weights or default_weights

        scores['overall'] = sum(
            scores.get(key, 0) * weight
            for key, weight in weights.items()
        )

        return scores

    def _build_resume_text(self, resume: Dict[str, Any]) -> str:
        """构建简历文本用于语义匹配"""
        parts = []

        # 基本信息
        basic = resume.get('basic_info', {})
        parts.append(f"姓名：{basic.get('name', '')}")

        # 工作年限
        parts.append(f"工作年限：{resume.get('work_years', 0)}年")

        # 技能
        skills = resume.get('skills', [])
        parts.append(f"技能：{', '.join(skills)}")

        # 工作经历
        work_exp = resume.get('work_experience', [])
        work_text = ' '.join([
            f"{exp.get('position', '')}: {exp.get('description', '')}"
            for exp in work_exp
        ])
        parts.append(f"工作经历：{work_text}")

        # 项目经历
        proj_exp = resume.get('project_experience', [])
        proj_text = ' '.join([
            f"{proj.get('name', '')}: {proj.get('description', '')}"
            for proj in proj_exp
        ])
        parts.append(f"项目经历：{proj_text}")

        return '\n'.join(parts)

    def _build_job_text(self, job: Dict[str, Any]) -> str:
        """构建岗位文本用于语义匹配"""
        parts = []

        parts.append(f"岗位：{job.get('job_name', '')}")
        parts.append(f"公司：{job.get('company_name', '')}")
        parts.append(f"描述：{job.get('job_description', '')}")
        parts.append(f"要求：{job.get('job_requirement', '')}")

        # 技能标签
        skill_tags = job.get('skill_tags', [])
        if skill_tags:
            parts.append(f"技能标签：{', '.join(skill_tags)}")

        return '\n'.join(parts)

    def _calculate_skill_match(self, resume: Dict[str, Any], job: Dict[str, Any]) -> float:
        """计算技能匹配度"""
        from matcher.core.skill_extractor import SkillExtractor

        skill_extractor = SkillExtractor()

        resume_skills = set(resume.get('skills', []))
        job_skills = set(job.get('skill_tags', []))

        # 使用 SkillExtractor 计算匹配度
        return skill_extractor.calculate_skill_match(list(resume_skills), list(job_skills))

    def _normalize_skill_match(self, resume_skills: set, job_skills: set) -> int:
        """技能归一化匹配（处理同义词）"""
        from matcher.core.skill_extractor import SkillExtractor

        skill_extractor = SkillExtractor()

        extra_matches = 0
        for job_skill in job_skills:
            if job_skill in resume_skills:
                continue
            # 检查同义词
            for standard, synonyms in skill_synonyms.items():
                if job_skill in synonyms or job_skill == standard:
                    if any(s in resume_skills for s in synonyms + [standard]):
                        extra_matches += 1
                        break

        return extra_matches

    def _calculate_experience_match(self, resume: Dict[str, Any], job: Dict[str, Any]) -> float:
        """计算经验匹配度"""
        resume_years = resume.get('work_years', 0)

        # 解析岗位要求的工作年限
        import re
        exp_req = job.get('experience_requirement', '')
        match = re.search(r'(\d+)\s*[-~]?\s*(\d*)\s*年', exp_req)

        if not match:
            return 1.0  # 无明确要求，视为匹配

        min_years = int(match.group(1))
        max_years = int(match.group(2)) if match.group(2) else min_years + 5

        if resume_years < min_years:
            return max(0, 1 - (min_years - resume_years) * 0.3)
        elif resume_years > max_years:
            return max(0.5, 1 - (resume_years - max_years) * 0.1)
        else:
            return 1.0

    def _keyword_similarity(self, text1: str, text2: str) -> float:
        """关键词匹配（降级方案）"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0

    def rank_jobs(self, resume: Dict[str, Any], jobs: List[Dict[str, Any]],
                  top_k: int = 20, weights: Dict[str, float] = None) -> List[Tuple[Dict[str, Any], Dict[str, float]]]:
        """
        对岗位列表进行匹配度排序

        Args:
            resume: 简历数据
            jobs: 岗位列表
            top_k: 返回前 K 个结果
            weights: 各维度权重配置

        Returns:
            按匹配度排序的岗位列表
        """
        scored_jobs = []

        for job in jobs:
            scores = self.score_job(resume, job, weights=weights)
            scored_jobs.append((job, scores))

        # 按综合得分排序
        scored_jobs.sort(key=lambda x: x[1]['overall'], reverse=True)

        return scored_jobs[:top_k]
