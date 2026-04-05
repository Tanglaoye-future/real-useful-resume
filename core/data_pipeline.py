"""
数据管道模块

整合数据加载、标准化、硬性过滤、高价值筛选的完整流程
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from matcher.filters.hard_filter import HardFilter, FilterRule
from matcher.filters.value_filter import ValueFilter, ValueFilterConfig

logger = logging.getLogger(__name__)


class DataPipeline:
    """数据管道 - 整合完整的数据处理流程"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.raw_data_dir = Path("data/raw")
        self.output_dir = Path("data/processed")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 初始化过滤器
        self.hard_filter = None
        self.value_filter = None

        # 统计数据
        self.stats = {
            'raw_count': 0,
            'standardized_count': 0,
            'hard_filtered_passed': 0,
            'hard_filtered_rejected': 0,
            'high_value_count': 0,
            'medium_value_count': 0,
            'low_value_count': 0,
            'filtered_count': 0
        }

    def load_raw_data(self, source: str = None) -> List[Dict[str, Any]]:
        """
        加载原始爬虫数据

        Args:
            source: 数据源名称 (如 '51job', 'liepin', 'official')，为None则加载所有

        Returns:
            原始岗位数据列表
        """
        jobs = []

        if source:
            # 加载特定来源的数据
            source_dir = self.raw_data_dir / source
            if source_dir.exists():
                jobs.extend(self._load_from_directory(source_dir))
        else:
            # 加载所有来源的数据
            if self.raw_data_dir.exists():
                for subdir in self.raw_data_dir.iterdir():
                    if subdir.is_dir():
                        jobs.extend(self._load_from_directory(subdir))

        self.stats['raw_count'] = len(jobs)
        logger.info(f"加载原始数据: {len(jobs)} 条")
        return jobs

    def _load_from_directory(self, directory: Path) -> List[Dict[str, Any]]:
        """从目录加载所有JSON文件"""
        jobs = []

        for json_file in directory.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # 处理不同格式的数据
                    if isinstance(data, list):
                        jobs.extend(data)
                    elif isinstance(data, dict):
                        # 可能是单个岗位或包含jobs字段
                        if 'jobs' in data:
                            jobs.extend(data['jobs'])
                        else:
                            jobs.append(data)

            except Exception as e:
                logger.warning(f"加载文件失败 {json_file}: {e}")

        return jobs

    def standardize(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        标准化岗位数据格式

        Args:
            jobs: 原始岗位列表

        Returns:
            标准化后的岗位列表
        """
        standardized = []

        for job in jobs:
            try:
                std_job = self._standardize_single_job(job)
                if std_job:
                    standardized.append(std_job)
            except Exception as e:
                logger.warning(f"标准化岗位失败: {e}")

        self.stats['standardized_count'] = len(standardized)
        logger.info(f"标准化完成: {len(standardized)} 条")
        return standardized

    def _standardize_single_job(self, job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """标准化单个岗位数据"""
        # 字段映射表
        field_mappings = {
            'job_name': ['job_name', 'title', 'position_name', 'name', 'jobTitle'],
            'company_name': ['company_name', 'company', 'compName', 'companyName'],
            'location': ['location', 'city', 'work_city', 'workCity', 'address'],
            'salary': ['salary', 'salary_desc', 'salaryDesc', 'compensation'],
            'job_description': ['job_description', 'description', 'jobDesc', 'jd', 'detail'],
            'requirements': ['requirements', 'requirement', 'req', 'qualifications'],
            'experience_requirement': ['experience_requirement', 'experience', 'work_exp', 'workExp'],
            'education_requirement': ['education_requirement', 'education', 'edu', 'eduLevel'],
            'benefits': ['benefits', 'welfare', 'perks', 'companyBenefits'],
            'source': ['source', 'platform', 'data_source'],
            'url': ['url', 'job_url', 'detail_url', 'link'],
            'publish_time': ['publish_time', 'publishTime', 'post_time', 'create_time']
        }

        std_job = {}

        # 应用字段映射
        for std_field, possible_fields in field_mappings.items():
            for field in possible_fields:
                if field in job and job[field]:
                    std_job[std_field] = job[field]
                    break
            else:
                std_job[std_field] = None

        # 保留原始数据
        std_job['_raw'] = job

        # 数据清洗
        if std_job.get('job_name'):
            std_job['job_name'] = std_job['job_name'].strip()

        if std_job.get('company_name'):
            std_job['company_name'] = std_job['company_name'].strip()

        if std_job.get('location'):
            std_job['location'] = std_job['location'].strip()

        return std_job

    def deduplicate(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        去重处理

        Args:
            jobs: 岗位列表

        Returns:
            去重后的岗位列表
        """
        seen = set()
        unique_jobs = []

        for job in jobs:
            # 生成唯一标识
            company = job.get('company_name', '')
            title = job.get('job_name', '')
            location = job.get('location', '')

            key = f"{company}_{title}_{location}".lower()

            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)

        logger.info(f"去重完成: {len(jobs)} -> {len(unique_jobs)} 条")
        return unique_jobs

    def setup_hard_filter(self, rules: FilterRule = None):
        """
        配置硬性过滤器

        Args:
            rules: 筛选规则配置
        """
        if rules is None:
            # 默认规则：筛选上海地区、27届可投递的岗位
            rules = FilterRule(
                locations=["上海", "Shanghai"],
                min_education="本科"
            )

        self.hard_filter = HardFilter(rules)
        logger.info("硬性过滤器已配置")

    def setup_value_filter(self, config: ValueFilterConfig = None):
        """
        配置高价值筛选器

        Args:
            config: 高价值筛选配置
        """
        self.value_filter = ValueFilter(config)
        logger.info("高价值筛选器已配置")

    def run_hard_filter(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        执行硬性过滤

        Args:
            jobs: 标准化后的岗位列表

        Returns:
            通过硬性过滤的岗位列表
        """
        if self.hard_filter is None:
            self.setup_hard_filter()

        passed, rejected = self.hard_filter.filter(jobs)

        self.stats['hard_filtered_passed'] = len(passed)
        self.stats['hard_filtered_rejected'] = len(rejected)

        logger.info(f"硬性过滤: 通过 {len(passed)}, 拒绝 {len(rejected)}")
        return passed

    def run_value_filter(self, jobs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        执行高价值筛选

        Args:
            jobs: 通过硬性过滤的岗位列表

        Returns:
            按价值等级分类的岗位字典
        """
        if self.value_filter is None:
            self.setup_value_filter()

        high_value, filtered = self.value_filter.filter(jobs)

        # 进一步分类高价值和中价值
        high = []
        medium = []

        for job in high_value:
            if job.get('value_level') == '高价值':
                high.append(job)
                self.stats['high_value_count'] += 1
            else:
                medium.append(job)
                self.stats['medium_value_count'] += 1

        # 分类过滤的岗位
        low = []
        filtered_out = []

        for job in filtered:
            if job.get('value_level') == '低价值':
                low.append(job)
                self.stats['low_value_count'] += 1
            else:
                filtered_out.append(job)
                self.stats['filtered_count'] += 1

        logger.info(f"高价值筛选: 高价值 {len(high)}, 中价值 {len(medium)}, "
                   f"低价值 {len(low)}, 已过滤 {len(filtered_out)}")

        return {
            'high': high,
            'medium': medium,
            'low': low,
            'filtered': filtered_out
        }

    def run_full_pipeline(self, source: str = None) -> Dict[str, Any]:
        """
        运行完整数据管道流程

        Args:
            source: 数据源名称，为None则处理所有数据

        Returns:
            处理结果和统计信息
        """
        logger.info("=" * 60)
        logger.info("开始运行数据管道")
        logger.info("=" * 60)

        # 1. 加载原始数据
        raw_jobs = self.load_raw_data(source)
        if not raw_jobs:
            logger.error("没有找到原始数据")
            return {'success': False, 'error': 'No raw data found'}

        # 2. 标准化
        std_jobs = self.standardize(raw_jobs)

        # 3. 去重
        unique_jobs = self.deduplicate(std_jobs)

        # 4. 硬性过滤
        hard_filtered = self.run_hard_filter(unique_jobs)

        # 5. 高价值筛选
        value_result = self.run_value_filter(hard_filtered)

        # 6. 保存结果
        output_files = self._save_results(value_result)

        # 7. 生成报告
        report = self._generate_report(value_result, output_files)

        logger.info("=" * 60)
        logger.info("数据管道运行完成")
        logger.info("=" * 60)

        return {
            'success': True,
            'stats': self.stats,
            'output_files': output_files,
            'report': report,
            'high_value_jobs': value_result['high'],
            'medium_value_jobs': value_result['medium']
        }

    def _save_results(self, value_result: Dict[str, List[Dict]]) -> Dict[str, str]:
        """保存处理结果到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_files = {}

        # 保存高价值岗位
        if value_result['high']:
            high_file = self.output_dir / f"high_value_jobs_{timestamp}.json"
            with open(high_file, 'w', encoding='utf-8') as f:
                json.dump(value_result['high'], f, ensure_ascii=False, indent=2)
            output_files['high'] = str(high_file)
            logger.info(f"高价值岗位已保存: {high_file}")

        # 保存中价值岗位
        if value_result['medium']:
            medium_file = self.output_dir / f"medium_value_jobs_{timestamp}.json"
            with open(medium_file, 'w', encoding='utf-8') as f:
                json.dump(value_result['medium'], f, ensure_ascii=False, indent=2)
            output_files['medium'] = str(medium_file)
            logger.info(f"中价值岗位已保存: {medium_file}")

        # 保存低价值岗位
        if value_result['low']:
            low_file = self.output_dir / f"low_value_jobs_{timestamp}.json"
            with open(low_file, 'w', encoding='utf-8') as f:
                json.dump(value_result['low'], f, ensure_ascii=False, indent=2)
            output_files['low'] = str(low_file)

        # 保存已过滤岗位
        if value_result['filtered']:
            filtered_file = self.output_dir / f"filtered_jobs_{timestamp}.json"
            with open(filtered_file, 'w', encoding='utf-8') as f:
                json.dump(value_result['filtered'], f, ensure_ascii=False, indent=2)
            output_files['filtered'] = str(filtered_file)

        return output_files

    def _generate_report(self, value_result: Dict, output_files: Dict) -> str:
        """生成处理报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"pipeline_report_{timestamp}.md"

        report = f"""# 数据管道处理报告

生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 处理统计

| 阶段 | 数量 |
|------|------|
| 原始数据 | {self.stats['raw_count']} |
| 标准化后 | {self.stats['standardized_count']} |
| 硬性过滤通过 | {self.stats['hard_filtered_passed']} |
| 硬性过滤拒绝 | {self.stats['hard_filtered_rejected']} |
| **高价值岗位** | **{self.stats['high_value_count']}** |
| **中价值岗位** | **{self.stats['medium_value_count']}** |
| 低价值岗位 | {self.stats['low_value_count']} |
| 已过滤 | {self.stats['filtered_count']} |

## 价值分布

- 高价值岗位: {len(value_result['high'])} 条
- 中价值岗位: {len(value_result['medium'])} 条
- 低价值岗位: {len(value_result['low'])} 条
- 已过滤: {len(value_result['filtered'])} 条

## 输出文件

"""

        for category, filepath in output_files.items():
            report += f"- {category}: `{filepath}`\n"

        report += "\n## 公司等级分布\n\n"

        # 添加公司等级分布
        if self.value_filter:
            tier_dist = self.value_filter.get_tier_distribution(
                value_result['high'] + value_result['medium']
            )
            for tier, count in tier_dist.items():
                if count > 0:
                    report += f"- {tier}: {count} 条\n"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        logger.info(f"报告已生成: {report_file}")
        return str(report_file)

    def get_stats(self) -> Dict[str, int]:
        """获取处理统计"""
        return self.stats.copy()


# 便捷函数
def run_pipeline(source: str = None, config: Dict = None) -> Dict[str, Any]:
    """
    便捷函数：运行完整数据管道

    Args:
        source: 数据源名称
        config: 配置字典

    Returns:
        处理结果
    """
    pipeline = DataPipeline(config)
    return pipeline.run_full_pipeline(source)
