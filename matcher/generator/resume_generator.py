"""
个性化简历生成模块

基于 JD 优化简历表述，生成 ATS 友好的简历
"""

import json
import logging
import re
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ResumeGenerator:
    """简历生成器"""

    def __init__(self, api_key: str = None, model_mode: str = 'local'):
        """
        初始化简历生成器

        Args:
            api_key: API 模式下的密钥
            model_mode: 'local' 或 'api'
        """
        self.api_key = api_key
        self.model_mode = model_mode
        self.output_dir = None

    def generate(self, resume: Dict[str, Any], job: Dict[str, Any],
                 output_format: str = 'markdown') -> str:
        """
        生成优化后的简历

        Args:
            resume: 原始简历数据
            job: 目标岗位数据
            output_format: 输出格式 ('markdown' 或 'json')

        Returns:
            生成的简历内容或文件路径
        """
        # 1. 提取 JD 关键词
        jd_keywords = self._extract_jd_keywords(job)
        logger.info(f"提取 JD 关键词: {jd_keywords}")

        # 2. 构建优化后的简历
        if self.model_mode == 'api' and self.api_key:
            optimized = self._generate_with_api(resume, job, jd_keywords)
        else:
            optimized = self._generate_local(resume, job, jd_keywords)

        # 3. 格式化输出
        if output_format == 'markdown':
            return self._format_markdown(optimized, job)
        else:
            return json.dumps(optimized, ensure_ascii=False, indent=2)

    def _extract_jd_keywords(self, job: Dict[str, Any]) -> Dict[str, list]:
        """
        从 JD 中提取关键词

        Returns:
            {'required': [...], 'preferred': [...]}
        """
        keywords = {
            'required': [],
            'preferred': []
        }

        # 合并 JD 文本
        jd_text = ' '.join([
            job.get('job_description', ''),
            job.get('job_requirement', ''),
            ' '.join(job.get('skill_tags', []))
        ])

        # 技能关键词库
        skill_keywords = [
            'Python', 'Java', 'Go', 'Golang', 'Vue', 'React', 'Spring Boot',
            'MySQL', 'Redis', 'MongoDB', 'Elasticsearch', 'Kafka', 'RabbitMQ',
            'Docker', 'Kubernetes', 'K8s', 'Linux', 'Git', 'Jenkins',
            '爬虫', '数据采集', '数据分析', '数据挖掘',
            '机器学习', '深度学习', 'AI', '模型部署', 'TensorFlow', 'PyTorch',
            '高并发', '分布式', '微服务', 'RESTful API',
            'Figma', '产品设计', '需求分析'
        ]

        jd_lower = jd_text.lower()

        for skill in skill_keywords:
            if skill.lower() in jd_lower:
                # 判断是必需还是优先
                if any(word in jd_text for word in ['必须', '必需', '要求', '必备', '熟悉']):
                    keywords['required'].append(skill)
                else:
                    keywords['preferred'].append(skill)

        # 去重
        keywords['required'] = list(set(keywords['required']))
        keywords['preferred'] = list(set(keywords['preferred']))

        return keywords

    def _generate_local(self, resume: Dict[str, Any], job: Dict[str, Any],
                       jd_keywords: Dict[str, list]) -> Dict[str, Any]:
        """
        本地生成优化简历（不调用 API）

        策略：
        1. 调整经历顺序，将最匹配的置顶
        2. 优化经历描述，自然嵌入 JD 关键词
        3. 保持经历真实性，仅调整表述
        """
        optimized = json.loads(json.dumps(resume))  # 深拷贝

        # 1. 优化工作经历顺序
        work_exp = optimized.get('work_experience', [])
        if work_exp:
            optimized['work_experience'] = self._reorder_experience(
                work_exp, jd_keywords
            )

        # 2. 优化项目经历顺序
        proj_exp = optimized.get('project_experience', [])
        if proj_exp:
            optimized['project_experience'] = self._reorder_experience(
                proj_exp, jd_keywords
            )

        # 3. 优化技能展示
        skills = optimized.get('skills', [])
        optimized['skills'] = self._optimize_skills(skills, jd_keywords)

        # 4. 添加求职意向
        optimized['job_target'] = {
            'position': job.get('job_name', ''),
            'company': job.get('company_name', ''),
            'keywords_matched': jd_keywords['required'] + jd_keywords['preferred']
        }

        return optimized

    def _generate_with_api(self, resume: Dict[str, Any], job: Dict[str, Any],
                          jd_keywords: Dict[str, list]) -> Dict[str, Any]:
        """使用 API 生成优化简历"""
        try:
            import dashscope
            dashscope.api_key = self.api_key

            prompt = self._build_prompt(resume, job, jd_keywords)

            response = dashscope.Generation.call(
                model='qwen-turbo',
                prompt=prompt,
                result_format='message'
            )

            if response.status_code == 200:
                content = response.output.choices[0].message.content
                # 尝试解析 JSON
                try:
                    return json.loads(content)
                except:
                    # 如果不是 JSON，包装成结构化数据
                    return {
                        'optimized_content': content,
                        'original_resume': resume,
                        'target_job': job
                    }
            else:
                logger.error(f"API 调用失败: {response.message}")
                return self._generate_local(resume, job, jd_keywords)

        except Exception as e:
            logger.error(f"API 生成失败，降级到本地生成: {e}")
            return self._generate_local(resume, job, jd_keywords)

    def _build_prompt(self, resume: Dict[str, Any], job: Dict[str, Any],
                     jd_keywords: Dict[str, list]) -> str:
        """构建 LLM Prompt"""
        return f"""你是一名专业的简历优化顾问。请根据以下岗位描述，优化这份简历，让它更匹配这个岗位。

【重要原则】
1. 绝对不要编造任何未在原始简历中出现的经历
2. 仅调整表述方式，用 STAR 法则重写描述
3. 自然嵌入 JD 关键词，但不要堆砌
4. 将与岗位最匹配的经历置顶

【岗位描述】
岗位名称：{job.get('job_name', '')}
公司名称：{job.get('company_name', '')}
岗位描述：{job.get('job_description', '')}
岗位要求：{job.get('job_requirement', '')}

【JD 核心关键词】
必需技能：{', '.join(jd_keywords['required'])}
优先技能：{', '.join(jd_keywords['preferred'])}

【原始简历】
{json.dumps(resume, ensure_ascii=False, indent=2)}

请输出优化后的完整简历，使用 JSON 格式，保持原始简历的结构。
"""

    def _reorder_experience(self, experiences: list, jd_keywords: Dict[str, list]) -> list:
        """根据 JD 关键词重新排序经历"""
        all_keywords = jd_keywords['required'] + jd_keywords['preferred']

        def relevance_score(exp):
            """计算经历与 JD 的相关度分数"""
            text = ' '.join([
                exp.get('description', ''),
                exp.get('position', ''),
                exp.get('name', '')
            ]).lower()

            score = 0
            for keyword in all_keywords:
                if keyword.lower() in text:
                    score += 2 if keyword in jd_keywords['required'] else 1

            return score

        # 按相关度排序，相同分数保持原有顺序
        return sorted(experiences, key=relevance_score, reverse=True)

    def _optimize_skills(self, skills: list, jd_keywords: Dict[str, list]) -> list:
        """优化技能展示顺序"""
        all_jd_keywords = jd_keywords['required'] + jd_keywords['preferred']

        # 将匹配 JD 的技能前置
        matched = []
        unmatched = []

        for skill in skills:
            is_matched = any(
                jd_kw.lower() in skill.lower() or skill.lower() in jd_kw.lower()
                for jd_kw in all_jd_keywords
            )
            if is_matched:
                matched.append(skill)
            else:
                unmatched.append(skill)

        return matched + unmatched

    def _format_markdown(self, resume: Dict[str, Any], job: Dict[str, Any]) -> str:
        """格式化为 Markdown 简历"""
        lines = []

        # 标题
        basic = resume.get('basic_info', {})
        lines.append(f"# {basic.get('name', '简历')}")
        lines.append(f"**求职意向**: {job.get('job_name', '')} | {job.get('company_name', '')}\n")

        # 基本信息
        lines.append("## 基本信息")
        lines.append(f"- **电话**: {basic.get('phone', '')}")
        lines.append(f"- **邮箱**: {basic.get('email', '')}")
        lines.append(f"- **地点**: {basic.get('location', '')}")
        lines.append(f"- **工作年限**: {resume.get('work_years', 0)} 年")
        lines.append(f"- **学历**: {resume.get('education', '')}")
        lines.append(f"- **学校**: {resume.get('school', '')}\n")

        # 技能
        lines.append("## 技能专长")
        skills = resume.get('skills', [])
        lines.append(', '.join(skills))
        lines.append("")

        # 工作经历
        lines.append("## 工作经历")
        for exp in resume.get('work_experience', []):
            lines.append(f"### {exp.get('company', exp.get('company_name', ''))}")
            lines.append(f"**{exp.get('position', '')}** | {exp.get('duration', '')}")
            lines.append("")
            lines.append(exp.get('description', ''))
            lines.append("")

        # 项目经历
        lines.append("## 项目经历")
        for proj in resume.get('project_experience', []):
            lines.append(f"### {proj.get('name', '')}")
            lines.append(f"{proj.get('duration', '')}")
            lines.append("")
            lines.append(proj.get('description', ''))
            lines.append("")

        # 教育经历
        lines.append("## 教育经历")
        for edu in resume.get('education_experience', []):
            lines.append(f"- **{edu.get('school', '')}** | {edu.get('major', '')} | {edu.get('degree', '')} | {edu.get('duration', '')}")

        return '\n'.join(lines)

    def save_resume(self, content: str, filename: str = None) -> str:
        """保存简历到文件"""
        if self.output_dir is None:
            # 确保输出路径在主工程文件夹内
            self.output_dir = Path('c:/Users/Lenovo/projects/ResuMiner_Integrated/data/output/matcher')

        self.output_dir.mkdir(parents=True, exist_ok=True)

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'optimized_resume_{timestamp}.md'

        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"简历已保存: {filepath}")
        return str(filepath)
