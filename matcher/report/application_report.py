#!/usr/bin/env python3
"""
岗位投递报告生成器

功能：
1. 生成详细的岗位投递报告
2. 提供投递优先级排序
3. 给出简历定制化建议
4. 生成投递时间规划
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class JobApplication:
    """岗位投递信息"""
    rank: int
    job_name: str
    company_name: str
    location: str
    salary: str
    strength_match_score: float
    composite_score: float
    matched_strengths: List[str]
    job_description: str
    job_requirement: str
    source_job_id: str
    platform: str
    
    # 投递建议
    priority: str = ""
    application_strategy: str = ""
    resume_tips: List[str] = None
    cover_letter_tips: str = ""


class ApplicationReportGenerator:
    """岗位投递报告生成器"""
    
    def __init__(self):
        # 确保输出路径在主工程文件夹内
        project_root = Path('c:/Users/Lenovo/projects/ResuMiner_Integrated')
        self.report_dir = project_root / 'data' / 'output' / 'application_reports'
        self.report_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_application_report(
        self,
        ranked_jobs: List[Dict],
        resume: Dict,
        strategy_config: Dict = None
    ) -> Path:
        """
        生成岗位投递报告
        
        Args:
            ranked_jobs: 排序后的岗位列表
            resume: 简历数据
            strategy_config: 策略配置
            
        Returns:
            报告文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.report_dir / f"application_report_{timestamp}.md"
        
        # 准备岗位投递信息
        applications = self._prepare_applications(ranked_jobs)
        
        # 生成报告内容
        with open(report_path, 'w', encoding='utf-8') as f:
            self._write_header(f, resume)
            self._write_summary(f, applications)
            self._write_priority_list(f, applications)
            self._write_detailed_recommendations(f, applications)
            self._write_application_schedule(f, applications)
            self._write_resume_customization(f, applications, resume)
            self._write_follow_up_guide(f)
        
        return report_path
    
    def _prepare_applications(self, ranked_jobs: List[tuple]) -> List[JobApplication]:
        """准备岗位投递信息"""
        applications = []
        
        for i, (job, scores) in enumerate(ranked_jobs[:50], 1):  # 取前50个
            # 确定投递优先级
            priority = self._determine_priority(scores, i)
            
            # 生成投递策略
            strategy = self._generate_strategy(job, scores)
            
            # 生成简历建议
            resume_tips = self._generate_resume_tips(job, scores)
            
            # 生成求职信建议
            cover_letter = self._generate_cover_letter_tips(job, scores)
            
            # 生成匹配优势
            matched_strengths = self._generate_matched_strengths(job, scores)
            
            # 获取薪资（如果为空则显示"面议"）
            salary = job.get('salary', '')
            if not salary or salary.strip() == '':
                salary = '面议'
            
            app = JobApplication(
                rank=i,
                job_name=job.get('job_name', ''),
                company_name=job.get('company_name', ''),
                location=job.get('location', ''),
                salary=salary,
                strength_match_score=scores.get('strength', 0),
                composite_score=scores.get('overall', 0),
                matched_strengths=matched_strengths,
                job_description=job.get('job_description', '')[:200] + '...' if len(job.get('job_description', '')) > 200 else job.get('job_description', ''),
                job_requirement=job.get('job_requirement', '')[:200] + '...' if len(job.get('job_requirement', '')) > 200 else job.get('job_requirement', ''),
                source_job_id=job.get('source_job_id', ''),
                platform=job.get('platform', ''),
                priority=priority,
                application_strategy=strategy,
                resume_tips=resume_tips,
                cover_letter_tips=cover_letter
            )
            
            applications.append(app)
        
        return applications
    
    def _generate_matched_strengths(self, job: Dict, scores: Dict) -> List[str]:
        """生成匹配优势列表"""
        strengths = []
        
        # 基于各项分数生成优势
        semantic_score = scores.get('semantic', 0)
        skill_score = scores.get('skill', 0)
        experience_score = scores.get('experience', 0)
        
        if semantic_score >= 0.6:
            strengths.append(f"语义匹配度高 ({semantic_score*100:.0f}%)")
        if skill_score >= 0.5:
            strengths.append(f"技能匹配良好 ({skill_score*100:.0f}%)")
        if experience_score >= 0.5:
            strengths.append(f"经验符合要求 ({experience_score*100:.0f}%)")
        
        # 基于岗位内容生成优势
        job_name = job.get('job_name', '')
        job_desc = job.get('job_description', '')
        
        if 'Python' in job_name or 'Python' in job_desc:
            strengths.append("Python技能匹配")
        if 'AI' in job_name or '大模型' in job_name or '算法' in job_name:
            strengths.append("AI/算法方向契合")
        if '后端' in job_name or '服务端' in job_name:
            strengths.append("后端开发经验匹配")
        if '实习' in job_name:
            strengths.append("实习岗位适合在校生")
        if '2027' in job_name or '27届' in job_name:
            strengths.append("面向2027届，年级匹配")
        
        # 基于公司生成优势
        company = job.get('company_name', '')
        if any(tech in company for tech in ['字节', '阿里', '腾讯', '美团', '快手', '哔哩', '小红书']):
            strengths.append("一线互联网公司")
        
        if not strengths:
            strengths.append("综合条件符合")
        
        return strengths
    
    def _determine_priority(self, scores: Dict, rank: int) -> str:
        """确定投递优先级"""
        composite_score = scores.get('overall', 0)
        
        if rank <= 5 and composite_score >= 0.4:
            return "🔥 立即投递"
        elif rank <= 15 and composite_score >= 0.35:
            return "⭐ 高优先级"
        elif rank <= 30 and composite_score >= 0.3:
            return "✅ 推荐投递"
        else:
            return "📋 备选考虑"
    
    def _generate_strategy(self, job: Dict, scores: Dict) -> str:
        """生成投递策略"""
        company = job.get('company_name', '')
        job_name = job.get('job_name', '')
        
        strategies = []
        
        # 基于公司类型
        if any(tech in company for tech in ['字节', '阿里', '腾讯', '美团', '百度']):
            strategies.append("大厂竞争激烈，突出技术实力和项目经验")
        elif any(fintech in company for fintech in ['证券', '银行', '金融', '蚂蚁']):
            strategies.append("强调财务+技术复合背景优势")
        elif any(ai in company for ai in ['AI', '智能', '科技']):
            strategies.append("突出AI技术和数据处理能力")
        
        # 基于匹配分数
        if scores.get('semantic', 0) > 0.7:
            strategies.append("语义匹配度高，强调技术栈契合")
        if scores.get('skill', 0) > 0.7:
            strategies.append("技能匹配度高，突出核心技能")
        
        return "；".join(strategies) if strategies else "标准投递流程"
    
    def _generate_resume_tips(self, job: Dict, scores: Dict) -> List[str]:
        """生成简历定制化建议"""
        job_name = job.get('job_name', '')
        job_desc = job.get('job_description', '')
        
        tips = []
        
        # 技能关键词匹配
        if 'Python' in job_desc:
            tips.append("在技能栏中突出Python编程能力")
        if 'Java' in job_desc:
            tips.append("强调Java开发经验和Spring Boot项目")
        if 'AI' in job_desc or '人工智能' in job_desc or '大模型' in job_desc:
            tips.append("添加AI模型部署和机器学习项目经验")
        if '产品' in job_name or 'Product' in job_name:
            tips.append("使用Figma设计案例展示产品思维")
        if '前端' in job_name or 'Vue' in job_desc or 'React' in job_desc:
            tips.append("突出前端开发经验和项目案例")
        
        return tips if tips else ["使用标准简历模板即可"]
    
    def _generate_cover_letter_tips(self, job: Dict, scores: Dict) -> str:
        """生成求职信建议"""
        company = job.get('company_name', '')
        job_name = job.get('job_name', '')
        
        tips = f"针对{company}的{job_name}岗位，求职信应重点强调：\n\n"
        
        # 基于岗位内容生成建议
        if 'AI' in job_name or '算法' in job_name:
            tips += "• AI技术应用场景和模型部署经验\n"
        if '产品' in job_name:
            tips += "• 产品思维和用户需求分析能力\n"
        if '前端' in job_name or '客户端' in job_name:
            tips += "• 前端开发经验和用户体验优化案例\n"
        if '后端' in job_name or '服务端' in job_name:
            tips += "• 后端架构设计和高并发处理经验\n"
        if '产品' in job_name:
            tips += "• 产品思维和用户体验设计的实践经验\n"
        
        tips += "\n建议结构：\n"
        tips += "1. 开场：表达对公司和岗位的兴趣\n"
        tips += "2. 核心优势：结合岗位要求展示匹配度\n"
        tips += "3. 项目经验：用具体案例证明能力\n"
        tips += "4. 结尾：表达期待面试的愿望\n"
        
        return tips
    
    def _write_header(self, f, resume: Dict):
        """写入报告头部"""
        f.write("# ResuMiner 岗位投递报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n")
        f.write(f"**候选人**: {resume.get('basic_info', {}).get('name', '未知')}\n")
        f.write(f"**工作年限**: {resume.get('work_years', 0)} 年\n")
        f.write(f"**核心技能**: {', '.join(resume.get('skills', [])[:5])}\n\n")
        
        f.write("---\n\n")
    
    def _write_summary(self, f, applications: List[JobApplication]):
        """写入摘要"""
        f.write("## 📊 投递概览\n\n")
        
        # 统计各优先级数量
        priority_counts = {}
        for app in applications:
            priority_counts[app.priority] = priority_counts.get(app.priority, 0) + 1
        
        f.write("| 优先级 | 数量 | 建议行动 |\n")
        f.write("|--------|------|----------|\n")
        
        priority_order = ["🔥 立即投递", "⭐ 高优先级", "✅ 推荐投递", "📋 备选考虑"]
        for priority in priority_order:
            count = priority_counts.get(priority, 0)
            if count > 0:
                if "立即" in priority:
                    action = "本周内完成投递"
                elif "高" in priority:
                    action = "2周内完成投递"
                elif "推荐" in priority:
                    action = "1个月内完成投递"
                else:
                    action = "持续关注"
                f.write(f"| {priority} | {count} | {action} |\n")
        
        f.write("\n")
    
    def _write_priority_list(self, f, applications: List[JobApplication]):
        """写入优先级列表"""
        f.write("## 🎯 投递优先级列表\n\n")
        
        # 按优先级分组
        priority_groups = {}
        for app in applications:
            priority = app.priority
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(app)
        
        # 按优先级顺序输出
        priority_order = ["🔥 立即投递", "⭐ 高优先级", "✅ 推荐投递", "📋 备选考虑"]
        
        for priority in priority_order:
            if priority in priority_groups:
                apps = priority_groups[priority]
                f.write(f"### {priority} ({len(apps)}个)\n\n")
                
                for app in apps[:10]:  # 每个优先级最多显示10个
                    f.write(f"**{app.rank}. {app.job_name}**\n")
                    f.write(f"- 公司: {app.company_name}\n")
                    f.write(f"- 地点: {app.location}\n")
                    f.write(f"- 薪资: {app.salary}\n")
                    f.write(f"- 优势匹配度: {app.strength_match_score*100:.1f}%\n")
                    f.write(f"- 综合分数: {app.composite_score*100:.1f}%\n")
                    f.write(f"- 匹配优势: {', '.join(app.matched_strengths)}\n")
                    f.write(f"- 投递策略: {app.application_strategy}\n\n")
        
        f.write("\n")
    
    def _write_detailed_recommendations(self, f, applications: List[JobApplication]):
        """写入详细推荐"""
        f.write("## 💡 详细投递建议\n\n")
        
        # Top 10 详细建议
        f.write("### Top 10 岗位详细建议\n\n")
        
        for app in applications[:10]:
            f.write(f"#### {app.rank}. {app.job_name} - {app.company_name}\n\n")
            
            f.write(f"**岗位信息**:\n")
            f.write(f"- 地点: {app.location}\n")
            f.write(f"- 薪资: {app.salary}\n")
            f.write(f"- 平台: {app.platform}\n")
            f.write(f"- 岗位ID: {app.source_job_id}\n\n")
            
            f.write(f"**匹配分析**:\n")
            f.write(f"- 优势匹配度: {app.strength_match_score*100:.1f}%\n")
            f.write(f"- 综合分数: {app.composite_score*100:.1f}%\n")
            f.write(f"- 匹配优势: {', '.join(app.matched_strengths)}\n\n")
            
            f.write(f"**投递策略**:\n")
            f.write(f"{app.application_strategy}\n\n")
            
            f.write(f"**简历优化建议**:\n")
            for tip in app.resume_tips:
                f.write(f"- {tip}\n")
            f.write("\n")
            
            f.write(f"**求职信建议**:\n")
            f.write(f"{app.cover_letter_tips}\n\n")
            
            f.write("---\n\n")
    
    def _write_application_schedule(self, f, applications: List[JobApplication]):
        """写入投递时间表"""
        f.write("## 📅 投递时间规划\n\n")
        
        today = datetime.now()
        
        # 第一周：立即投递
        f.write("### 第一周（立即投递）\n\n")
        week1_apps = [app for app in applications if "立即" in app.priority][:5]
        for i, app in enumerate(week1_apps, 1):
            date = today + timedelta(days=i)
            f.write(f"- **{date.strftime('%m月%d日')}**: {app.company_name} - {app.job_name}\n")
        
        f.write("\n")
        
        # 第二周：高优先级
        f.write("### 第二周（高优先级）\n\n")
        week2_apps = [app for app in applications if "高" in app.priority][:5]
        for i, app in enumerate(week2_apps, 1):
            date = today + timedelta(days=7+i)
            f.write(f"- **{date.strftime('%m月%d日')}**: {app.company_name} - {app.job_name}\n")
        
        f.write("\n")
        
        # 第三-四周：推荐投递
        f.write("### 第三-四周（推荐投递）\n\n")
        week3_apps = [app for app in applications if "推荐" in app.priority][:10]
        for i, app in enumerate(week3_apps, 1):
            date = today + timedelta(days=14+i)
            f.write(f"- **{date.strftime('%m月%d日')}**: {app.company_name} - {app.job_name}\n")
        
        f.write("\n")
    
    def _write_resume_customization(self, f, applications: List[JobApplication], resume: Dict):
        """写入简历定制化建议"""
        f.write("## 📝 简历定制化指南\n\n")
        
        # 分析Top岗位的共同要求
        all_strengths = []
        for app in applications[:20]:
            all_strengths.extend(app.matched_strengths)
        
        strength_counts = {}
        for strength in all_strengths:
            strength_counts[strength] = strength_counts.get(strength, 0) + 1
        
        f.write("### 基于匹配结果的简历重点\n\n")
        f.write("根据Top 20岗位的匹配分析，你的简历应重点突出以下优势：\n\n")
        
        for strength, count in sorted(strength_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / 20) * 100
            f.write(f"- **{strength}**: 在{percentage:.0f}%的匹配岗位中被认可\n")
        
        f.write("\n")
        
        # 技能展示建议
        f.write("### 技能展示优先级\n\n")
        f.write("1. **技术技能**: Python, Java, Spring Boot, Vue/React\n")
        f.write("2. **AI技能**: AI模型部署, 爬虫开发, 数据处理\n")
        f.write("3. **金融技能**: 财务知识, 数据分析, 量化基础\n")
        f.write("4. **产品技能**: Figma, 原型设计, 用户体验\n\n")
        
        f.write("### 项目经验排序建议\n\n")
        f.write("1. **金融相关技术项目** - 展示财务+技术复合能力\n")
        f.write("2. **全栈开发项目** - 展示完整开发能力\n")
        f.write("3. **AI/数据项目** - 展示AI技术和数据处理能力\n")
        f.write("4. **产品设计项目** - 展示产品思维和设计能力\n\n")
    
    def _write_follow_up_guide(self, f):
        """写入跟进指南"""
        f.write("## 📞 投递后跟进指南\n\n")
        
        f.write("### 跟进时间节点\n\n")
        f.write("- **投递后3天**: 检查邮件，确认是否收到自动回复\n")
        f.write("- **投递后1周**: 如未收到回复，可发送跟进邮件\n")
        f.write("- **投递后2周**: 如仍未回复，可尝试联系HR或内推人\n")
        f.write("- **面试后1天**: 发送感谢邮件\n")
        f.write("- **面试后1周**: 如未收到反馈，可礼貌询问进展\n\n")
        
        f.write("### 跟进邮件模板\n\n")
        f.write("**主题**: 关于[岗位名称]申请的状态查询 - [你的姓名]\n\n")
        f.write("尊敬的HR：\n\n")
        f.write("您好！我于[日期]投递了贵公司的[岗位名称]职位。\n\n")
        f.write("我对这个岗位非常感兴趣，相信我的[核心优势]能为贵公司带来价值。\n\n")
        f.write("想了解一下目前的招聘进展，期待有机会与您进一步交流。\n\n")
        f.write("祝好！\n")
        f.write("[你的姓名]\n")
        f.write("[联系方式]\n\n")
        
        f.write("---\n\n")
        f.write("**报告生成完成！祝你求职顺利！** 🎉\n")


# 便捷函数
def generate_application_report(
    ranked_jobs: List[Dict],
    resume: Dict,
    strategy_config: Dict = None
) -> Path:
    """便捷函数：生成岗位投递报告"""
    generator = ApplicationReportGenerator()
    return generator.generate_application_report(ranked_jobs, resume, strategy_config)