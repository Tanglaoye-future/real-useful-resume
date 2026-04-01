"""
ResuMiner 报告生成模块

提供各类匹配报告的生成功能
"""

from .application_report import ApplicationReportGenerator, generate_application_report

__all__ = [
    'ApplicationReportGenerator',
    'generate_application_report',
]
