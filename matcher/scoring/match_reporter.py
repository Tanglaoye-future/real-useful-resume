"""
匹配报告生成模块

生成详细的岗位匹配报告
"""

import json
import logging
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class MatchReporter:
    """匹配报告生成器"""

    def __init__(self, output_dir: str = None):
        """
        初始化报告生成器

        Args:
            output_dir: 报告输出目录
        """
        if output_dir is None:
            # 确保输出路径在主工程文件夹内
            output_dir = Path('c:/Users/Lenovo/projects/ResuMiner_Integrated/data/output/matcher')

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(self, resume: Dict[str, Any],
                       matched_jobs: List[tuple],
                       filter_stats: Dict[str, int] = None) -> str:
        """
        生成匹配报告

        Args:
            resume: 简历数据
            matched_jobs: 匹配岗位列表 [(job, scores), ...]
            filter_stats: 过滤统计信息

        Returns:
            报告文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.output_dir / f'match_report_{timestamp}.md'

        report_content = self._build_markdown_report(
            resume, matched_jobs, filter_stats
        )

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        # 同时生成 JSON 格式的结构化数据
        json_path = self.output_dir / f'match_report_{timestamp}.json'
        json_data = self._build_json_report(resume, matched_jobs, filter_stats)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        logger.info(f"匹配报告已生成: {report_path}")
        return str(report_path)

    def _build_markdown_report(self, resume: Dict[str, Any],
                               matched_jobs: List[tuple],
                               filter_stats: Dict[str, int] = None) -> str:
        """构建 Markdown 格式报告"""
        lines = []

        # 标题
        lines.append("# ResuMiner 智能匹配报告\n")
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 简历概览
        basic = resume.get('basic_info', {})
        lines.append("## 简历概览\n")
        lines.append(f"- **姓名**: {basic.get('name', '未知')}")
        lines.append(f"- **工作年限**: {resume.get('work_years', 0)} 年")
        lines.append(f"- **学历**: {resume.get('education', '未知')}")
        lines.append(f"- **学校**: {resume.get('school', '未知')}")
        lines.append(f"- **期望薪资**: {resume.get('expected_salary', '未设置')} 元/月\n")

        # 技能列表
        skills = resume.get('skills', [])
        lines.append(f"- **技能**: {', '.join(skills)}\n")

        # 过滤统计
        if filter_stats:
            lines.append("## 筛选统计\n")
            lines.append(f"- 总岗位数: {filter_stats.get('total', 0)}")
            lines.append(f"- 通过硬性过滤: {filter_stats.get('passed', 0)}")
            lines.append(f"- 被过滤掉: {filter_stats.get('rejected', 0)}\n")

        # 匹配结果
        lines.append(f"## 高匹配岗位 Top {len(matched_jobs)}\n")

        for i, (job, scores) in enumerate(matched_jobs, 1):
            lines.append(f"### {i}. {job.get('job_name', '未知岗位')}\n")
            lines.append(f"**公司**: {job.get('company_name', '未知公司')}  ")
            lines.append(f"**地点**: {job.get('location', job.get('city', '未知'))}  ")
            lines.append(f"**薪资**: {job.get('salary', '面议')}  ")
            lines.append(f"**匹配度**: {scores.get('overall', 0) * 100:.1f}%\n")

            # 详细分数
            lines.append("**匹配详情**:")
            lines.append(f"- 语义相似度: {scores.get('semantic', 0) * 100:.1f}%")
            lines.append(f"- 技能匹配度: {scores.get('skill', 0) * 100:.1f}%")
            lines.append(f"- 经验匹配度: {scores.get('experience', 0) * 100:.1f}%\n")

            # 亮点与差距
            lines.append("**匹配亮点**:")
            highlights = self._generate_highlights(resume, job)
            for highlight in highlights:
                lines.append(f"- {highlight}")
            lines.append("")

            # JD 摘要
            jd = job.get('job_description', '')
            if len(jd) > 200:
                jd = jd[:200] + "..."
            lines.append(f"**岗位描述**: {jd}\n")

            lines.append("---\n")

        return '\n'.join(lines)

    def _build_json_report(self, resume: Dict[str, Any],
                          matched_jobs: List[tuple],
                          filter_stats: Dict[str, int] = None) -> Dict[str, Any]:
        """构建 JSON 格式报告"""
        return {
            "generated_at": datetime.now().isoformat(),
            "resume_summary": {
                "name": resume.get('basic_info', {}).get('name', ''),
                "work_years": resume.get('work_years', 0),
                "education": resume.get('education', ''),
                "expected_salary": resume.get('expected_salary', 0),
                "skills": resume.get('skills', [])
            },
            "filter_stats": filter_stats or {},
            "matched_jobs": [
                {
                    "job_name": job.get('job_name', ''),
                    "company_name": job.get('company_name', ''),
                    "location": job.get('location', job.get('city', '')),
                    "salary": job.get('salary', ''),
                    "jd_url": job.get('jd_url', ''),
                    "scores": scores,
                    "highlights": self._generate_highlights(resume, job)
                }
                for job, scores in matched_jobs
            ]
        }

    def _generate_highlights(self, resume: Dict[str, Any], job: Dict[str, Any]) -> List[str]:
        """生成匹配亮点"""
        highlights = []

        # 技能匹配亮点
        resume_skills = set(resume.get('skills', []))
        job_skills = set(job.get('skill_tags', []))
        matched_skills = resume_skills & job_skills

        if matched_skills:
            highlights.append(f"掌握核心技能: {', '.join(list(matched_skills)[:3])}")

        # 经验匹配亮点
        if 'Python' in matched_skills and '爬虫' in str(job.get('job_description', '')):
            highlights.append("具备爬虫开发经验，符合岗位要求")

        if 'AI' in str(matched_skills) or '模型部署' in str(matched_skills):
            highlights.append("有AI模型部署经验，是岗位加分项")

        # 学历匹配
        if resume.get('education') in ['本科', '硕士', '博士']:
            highlights.append(f"学历符合要求 ({resume.get('education')})")

        # 工作年限匹配
        resume_years = resume.get('work_years', 0)
        if 1 <= resume_years <= 3:
            highlights.append(f"工作年限 ({resume_years}年) 符合初级/中级岗位要求")

        return highlights if highlights else ["基础条件符合"]
