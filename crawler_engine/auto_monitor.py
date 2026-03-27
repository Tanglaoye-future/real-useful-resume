#!/usr/bin/env python3
"""
全局自动监控模块
每次运行爬虫时自动启用监控和生成报告
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class AutoMonitor:
    """自动监控器 - 全局单例模式"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self.enabled = os.getenv("ENABLE_AUTO_MONITORING", "1") == "1"
        self.auto_report = os.getenv("AUTO_GENERATE_REPORT", "1") == "1"
        self.output_dir = os.getenv("REPORT_OUTPUT_DIR", "output/monitoring")
        
        # 确保输出目录存在
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # 监控数据
        self.start_time = None
        self.platform_stats = {}
        self.quality_issues = []
        self.real_time_logs = []
        
        if self.enabled:
            logger.info("[AutoMonitor] 全局自动监控已启用")
    
    def start_monitoring(self):
        """开始监控"""
        if not self.enabled:
            return
        
        self.start_time = datetime.now()
        self.platform_stats = {}
        self.quality_issues = []
        self.real_time_logs = []
        
        logger.info("[AutoMonitor] 监控开始")
        self._log_event("monitoring_started", {"timestamp": self.start_time.isoformat()})
    
    def record_platform_start(self, platform_name: str):
        """记录平台开始"""
        if not self.enabled:
            return
        
        self.platform_stats[platform_name] = {
            "start_time": datetime.now(),
            "status": "running",
            "jobs_collected": 0,
            "quality_metrics": {}
        }
        logger.info(f"[AutoMonitor] {platform_name} 开始爬取")
    
    def record_platform_complete(self, platform_name: str, jobs: List[Dict], 
                                  quality_metrics: Dict[str, Any] = None):
        """记录平台完成"""
        if not self.enabled:
            return
        
        end_time = datetime.now()
        stats = self.platform_stats.get(platform_name, {})
        start_time = stats.get("start_time", end_time)
        duration = (end_time - start_time).total_seconds()
        
        self.platform_stats[platform_name].update({
            "end_time": end_time,
            "status": "completed",
            "duration": duration,
            "jobs_collected": len(jobs),
            "quality_metrics": quality_metrics or self._calculate_quality_metrics(jobs)
        })
        
        logger.info(f"[AutoMonitor] {platform_name} 完成: {len(jobs)}条职位, 耗时{duration:.1f}秒")
        
        # 检查质量问题
        self._check_quality_issues(platform_name, jobs, quality_metrics)
    
    def record_platform_error(self, platform_name: str, error: str):
        """记录平台错误"""
        if not self.enabled:
            return
        
        self.platform_stats[platform_name].update({
            "end_time": datetime.now(),
            "status": "error",
            "error": error
        })
        
        logger.error(f"[AutoMonitor] {platform_name} 错误: {error}")
        self.quality_issues.append({
            "platform": platform_name,
            "type": "execution_error",
            "message": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def _calculate_quality_metrics(self, jobs: List[Dict]) -> Dict[str, Any]:
        """计算质量指标"""
        if not jobs:
            return {"completeness_rate": 0, "avg_jd_length": 0}
        
        # 字段完整率
        required_fields = ["job_name", "company_name", "location", "salary", 
                          "jd_content", "job_description", "job_requirement", "jd_url"]
        
        completeness_scores = []
        jd_lengths = []
        
        for job in jobs:
            score = 0
            for field in required_fields:
                value = job.get(field, "")
                if field in ["jd_content", "job_description", "job_requirement"]:
                    if len(str(value)) > 20:
                        score += 1
                elif value:
                    score += 1
            completeness_scores.append(score / len(required_fields))
            
            jd_len = len(str(job.get("jd_content", "")))
            jd_lengths.append(jd_len)
        
        return {
            "completeness_rate": sum(completeness_scores) / len(completeness_scores) * 100,
            "avg_jd_length": sum(jd_lengths) / len(jd_lengths),
            "min_jd_length": min(jd_lengths) if jd_lengths else 0,
            "max_jd_length": max(jd_lengths) if jd_lengths else 0
        }
    
    def _check_quality_issues(self, platform_name: str, jobs: List[Dict], 
                              quality_metrics: Dict = None):
        """检查质量问题"""
        min_rate = float(os.getenv("MIN_FIELD_COMPLETENESS_RATE", "95"))
        min_jd_len = int(os.getenv("MIN_JD_LENGTH", "50"))
        
        metrics = quality_metrics or self._calculate_quality_metrics(jobs)
        
        # 检查完整率
        if metrics.get("completeness_rate", 0) < min_rate:
            self.quality_issues.append({
                "platform": platform_name,
                "type": "low_completeness",
                "message": f"字段完整率 {metrics['completeness_rate']:.1f}% 低于阈值 {min_rate}%",
                "timestamp": datetime.now().isoformat()
            })
        
        # 检查JD长度
        if metrics.get("avg_jd_length", 0) < min_jd_len:
            self.quality_issues.append({
                "platform": platform_name,
                "type": "short_jd",
                "message": f"平均JD长度 {metrics['avg_jd_length']:.0f} 低于阈值 {min_jd_len}",
                "timestamp": datetime.now().isoformat()
            })
    
    def _log_event(self, event_type: str, data: Dict):
        """记录事件"""
        self.real_time_logs.append({
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "data": data
        })
    
    def generate_report(self) -> str:
        """生成监控报告"""
        if not self.enabled or not self.auto_report:
            return ""
        
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds() if self.start_time else 0
        
        # 生成报告内容
        report_lines = [
            "# 爬虫全量爬取监控报告",
            "",
            f"**报告生成时间**: {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**总耗时**: {total_duration:.1f}秒 ({total_duration/60:.1f}分钟)",
            "",
            "## 执行汇总",
            "",
            "| 平台 | 状态 | 职位数 | 耗时(秒) | 完整率 | JD平均长度 |",
            "|---|---|---:|---:|---:|---:|"
        ]
        
        total_jobs = 0
        for platform, stats in self.platform_stats.items():
            status = stats.get("status", "unknown")
            status_icon = "✅" if status == "completed" else "❌" if status == "error" else "⏳"
            jobs = stats.get("jobs_collected", 0)
            duration = stats.get("duration", 0)
            metrics = stats.get("quality_metrics", {})
            completeness = metrics.get("completeness_rate", 0)
            jd_len = metrics.get("avg_jd_length", 0)
            
            report_lines.append(
                f"| {platform} | {status_icon} {status} | {jobs} | {duration:.1f} | {completeness:.1f}% | {jd_len:.0f} |"
            )
            total_jobs += jobs
        
        report_lines.extend([
            "",
            f"**总计**: {len(self.platform_stats)}个平台, {total_jobs}条职位",
            "",
            "## 质量指标详情",
            ""
        ])
        
        for platform, stats in self.platform_stats.items():
            metrics = stats.get("quality_metrics", {})
            report_lines.extend([
                f"### {platform}",
                "",
                f"- **职位数**: {stats.get('jobs_collected', 0)}",
                f"- **字段完整率**: {metrics.get('completeness_rate', 0):.1f}%",
                f"- **JD平均长度**: {metrics.get('avg_jd_length', 0):.0f}字符",
                f"- **JD长度范围**: {metrics.get('min_jd_length', 0):.0f} - {metrics.get('max_jd_length', 0):.0f}字符",
                ""
            ])
        
        # 质量问题
        report_lines.extend([
            "## 质量问题",
            ""
        ])
        
        if self.quality_issues:
            report_lines.append("| 平台 | 类型 | 问题描述 | 时间 |")
            report_lines.append("|---|---|---|---|")
            for issue in self.quality_issues:
                report_lines.append(
                    f"| {issue['platform']} | {issue['type']} | {issue['message']} | {issue['timestamp']} |"
                )
        else:
            report_lines.append("✅ 未发现质量问题")
        
        report_lines.extend([
            "",
            "## 实时监控日志",
            ""
        ])
        
        # 添加关键事件日志
        for log in self.real_time_logs[-20:]:  # 只显示最近20条
            timestamp = log['timestamp'].split('T')[1].split('.')[0] if 'T' in log['timestamp'] else log['timestamp']
            report_lines.append(f"- [{timestamp}] {log['event']}")
        
        report_lines.extend([
            "",
            "## 结论",
            ""
        ])
        
        # 生成结论
        success_count = sum(1 for s in self.platform_stats.values() if s.get("status") == "completed")
        error_count = sum(1 for s in self.platform_stats.values() if s.get("status") == "error")
        
        if error_count == 0 and len(self.quality_issues) == 0:
            report_lines.append(f"✅ **爬取成功**: 所有{success_count}个平台均成功完成，数据质量达标")
        elif error_count > 0:
            report_lines.append(f"⚠️ **部分成功**: {success_count}个平台成功，{error_count}个平台失败")
        else:
            report_lines.append(f"🟡 **完成但有警告**: 所有平台完成，但存在{len(self.quality_issues)}个质量问题")
        
        report_content = "\n".join(report_lines)
        
        # 保存报告
        timestamp = end_time.strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.output_dir, f"crawler_report_{timestamp}.md")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # 同时保存JSON格式 - 处理datetime序列化
        json_file = os.path.join(self.output_dir, f"crawler_report_{timestamp}.json")
        
        # 转换platform_stats中的datetime
        serializable_stats = {}
        for platform, stats in self.platform_stats.items():
            serializable_stats[platform] = {}
            for key, value in stats.items():
                if isinstance(value, datetime):
                    serializable_stats[platform][key] = value.isoformat()
                else:
                    serializable_stats[platform][key] = value
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": end_time.isoformat(),
                "total_duration": total_duration,
                "platforms": serializable_stats,
                "quality_issues": self.quality_issues,
                "summary": {
                    "total_platforms": len(self.platform_stats),
                    "success_count": success_count,
                    "error_count": error_count,
                    "total_jobs": total_jobs,
                    "quality_issues_count": len(self.quality_issues)
                }
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"[AutoMonitor] 报告已生成: {report_file}")
        return report_file
    
    def finish_monitoring(self):
        """完成监控并生成报告"""
        if not self.enabled:
            return
        
        self._log_event("monitoring_finished", {
            "timestamp": datetime.now().isoformat(),
            "platforms": list(self.platform_stats.keys())
        })
        
        report_file = self.generate_report()
        
        logger.info("[AutoMonitor] 监控结束")
        return report_file


# 全局监控实例
auto_monitor = AutoMonitor()
