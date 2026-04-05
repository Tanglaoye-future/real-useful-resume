#!/usr/bin/env python3
"""
数据管道运行脚本

演示完整的数据处理流程：
1. 加载原始爬虫数据
2. 数据标准化
3. 去重处理
4. 硬性条件过滤
5. 高价值岗位筛选
6. 生成筛选报告
"""

import sys
import logging
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from core.data_pipeline import DataPipeline, run_pipeline
from matcher.filters.hard_filter import FilterRule
from matcher.filters.value_filter import ValueFilterConfig, CompanyTier

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/data_pipeline.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def run_basic_pipeline():
    """运行基础数据管道（使用默认配置）"""
    print("\n" + "=" * 60)
    print("运行基础数据管道（默认配置）")
    print("=" * 60 + "\n")

    result = run_pipeline()

    if result['success']:
        print("\n✅ 数据管道运行成功！")
        print(f"\n📊 处理统计:")
        stats = result['stats']
        print(f"  - 原始数据: {stats['raw_count']} 条")
        print(f"  - 硬性过滤通过: {stats['hard_filtered_passed']} 条")
        print(f"  - 高价值岗位: {stats['high_value_count']} 条")
        print(f"  - 中价值岗位: {stats['medium_value_count']} 条")

        print(f"\n📁 输出文件:")
        for category, filepath in result['output_files'].items():
            print(f"  - {category}: {filepath}")

        print(f"\n📝 报告: {result['report']}")
    else:
        print(f"\n❌ 数据管道运行失败: {result.get('error', 'Unknown error')}")

    return result


def run_custom_pipeline():
    """运行自定义配置的数据管道"""
    print("\n" + "=" * 60)
    print("运行自定义数据管道（针对27届上海产品岗位）")
    print("=" * 60 + "\n")

    # 创建数据管道实例
    pipeline = DataPipeline()

    # 配置硬性过滤规则
    hard_rules = FilterRule(
        locations=["上海", "Shanghai", "魔都"],
        min_education="本科",
        blacklist_companies=["外包", "劳务派遣"]
    )
    pipeline.setup_hard_filter(hard_rules)

    # 配置高价值筛选
    value_config = ValueFilterConfig(
        min_company_tier=CompanyTier.TIER_3,  # 只保留中厂及以上
        high_value_keywords=[
            "产品经理", "产品实习", "策略产品", "数据产品",
            "增长产品", "商业化产品", "AI产品", "B端产品", "C端产品"
        ],
        min_salary_score=0.4,  # 最低薪资评分
        min_success_rate=0.3   # 最低投递成功率
    )
    pipeline.setup_value_filter(value_config)

    # 运行完整流程
    result = pipeline.run_full_pipeline()

    if result['success']:
        print("\n✅ 自定义数据管道运行成功！")
        print(f"\n📊 详细统计:")
        stats = result['stats']
        print(f"  - 原始数据: {stats['raw_count']} 条")
        print(f"  - 标准化后: {stats['standardized_count']} 条")
        print(f"  - 硬性过滤通过: {stats['hard_filtered_passed']} 条")
        print(f"  - 硬性过滤拒绝: {stats['hard_filtered_rejected']} 条")
        print(f"  - 高价值岗位: {stats['high_value_count']} 条 ⭐")
        print(f"  - 中价值岗位: {stats['medium_value_count']} 条")
        print(f"  - 低价值岗位: {stats['low_value_count']} 条")
        print(f"  - 已过滤: {stats['filtered_count']} 条")

        print(f"\n📁 输出文件:")
        for category, filepath in result['output_files'].items():
            print(f"  - {category}: {filepath}")

        print(f"\n📝 详细报告: {result['report']}")

        # 显示高价值岗位示例
        if result['high_value_jobs']:
            print("\n🏆 高价值岗位示例（前5条）:")
            for i, job in enumerate(result['high_value_jobs'][:5], 1):
                company = job.get('company_name', 'Unknown')
                title = job.get('job_name', 'Unknown')
                score = job.get('value_score', 0)
                print(f"  {i}. [{company}] {title} (价值分: {score})")
    else:
        print(f"\n❌ 数据管道运行失败: {result.get('error', 'Unknown error')}")

    return result


def run_specific_source(source: str):
    """运行特定数据源的管道"""
    print(f"\n{'=' * 60}")
    print(f"处理数据源: {source}")
    print("=" * 60 + "\n")

    result = run_pipeline(source=source)

    if result['success']:
        print(f"\n✅ {source} 数据处理成功！")
        stats = result['stats']
        print(f"  - 原始数据: {stats['raw_count']} 条")
        print(f"  - 高价值岗位: {stats['high_value_count']} 条")
        print(f"  - 中价值岗位: {stats['medium_value_count']} 条")
    else:
        print(f"\n❌ {source} 数据处理失败: {result.get('error', 'Unknown error')}")

    return result


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='ResuMiner 数据管道')
    parser.add_argument(
        '--mode',
        choices=['basic', 'custom', 'source'],
        default='custom',
        help='运行模式: basic=基础配置, custom=自定义配置(默认), source=指定数据源'
    )
    parser.add_argument(
        '--source',
        choices=['51job', 'liepin', 'official'],
        help='数据源名称（仅在mode=source时使用）'
    )

    args = parser.parse_args()

    # 确保日志目录存在
    Path('logs').mkdir(exist_ok=True)

    if args.mode == 'basic':
        run_basic_pipeline()
    elif args.mode == 'custom':
        run_custom_pipeline()
    elif args.mode == 'source':
        if not args.source:
            print("❌ 请指定数据源: --source [51job|liepin|official]")
            sys.exit(1)
        run_specific_source(args.source)


if __name__ == '__main__':
    main()
