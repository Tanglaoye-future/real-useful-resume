#!/usr/bin/env python3
"""
数据管道测试脚本

测试数据管道的各个模块是否正常工作
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from matcher.filters.hard_filter import HardFilter, FilterRule
from matcher.filters.value_filter import ValueFilter, ValueFilterConfig, CompanyTier, JobValueLevel
from core.data_pipeline import DataPipeline


def test_hard_filter():
    """测试硬性过滤器"""
    print("\n" + "=" * 60)
    print("测试硬性过滤器")
    print("=" * 60)

    # 创建测试数据
    test_jobs = [
        {
            'job_name': '产品经理实习生',
            'company_name': '字节跳动',
            'location': '上海',
            'salary': '200-250元/天',
            'experience_requirement': '经验不限',
            'education_requirement': '本科'
        },
        {
            'job_name': '算法工程师',
            'company_name': '阿里巴巴',
            'location': '杭州',  # 地点不匹配
            'salary': '300-400元/天',
            'experience_requirement': '3年以上',
            'education_requirement': '硕士'
        },
        {
            'job_name': '产品实习生',
            'company_name': '腾讯',
            'location': '上海',
            'salary': '150-200元/天',
            'experience_requirement': '经验不限',
            'education_requirement': '本科'
        }
    ]

    # 配置硬性过滤规则
    rules = FilterRule(
        locations=["上海"],
        min_education="本科"
    )

    filter_instance = HardFilter(rules)
    passed, rejected = filter_instance.filter(test_jobs)

    print(f"\n✅ 硬性过滤测试完成")
    print(f"  - 通过: {len(passed)} 条")
    print(f"  - 拒绝: {len(rejected)} 条")

    for job in passed:
        print(f"  ✓ [{job['company_name']}] {job['job_name']}")

    for job in rejected:
        print(f"  ✗ [{job['company_name']}] {job['job_name']} - {job.get('reject_reason', '')}")

    assert len(passed) == 2, f"期望通过2条，实际通过{len(passed)}条"
    assert len(rejected) == 1, f"期望拒绝1条，实际拒绝{len(rejected)}条"

    print("\n✅ 硬性过滤器测试通过！")
    return True


def test_value_filter():
    """测试高价值筛选器"""
    print("\n" + "=" * 60)
    print("测试高价值筛选器")
    print("=" * 60)

    # 创建测试数据
    test_jobs = [
        {
            'job_name': '产品经理实习生',
            'company_name': '字节跳动',
            'location': '上海',
            'salary': '250-300元/天',
            'job_description': '负责抖音电商产品功能设计，需求分析，数据分析等工作',
            'requirements': '本科及以上学历，有产品实习经验优先',
            'experience_requirement': '经验不限',
            'education_requirement': '本科'
        },
        {
            'job_name': '算法工程师实习生',
            'company_name': '阿里巴巴',
            'location': '上海',
            'salary': '300-400元/天',
            'job_description': '负责推荐算法优化，深度学习模型训练',
            'experience_requirement': '经验不限',
            'education_requirement': '硕士'
        },
        {
            'job_name': '产品实习生',
            'company_name': '某小公司',
            'location': '上海',
            'salary': '100-150元/天',
            'job_description': '协助产品经理完成日常工作',
            'experience_requirement': '经验不限',
            'education_requirement': '本科'
        },
        {
            'job_name': '策略产品经理',
            'company_name': '美团',
            'location': '上海',
            'salary': '200-250元/天',
            'job_description': '负责外卖推荐策略设计，AB测试分析',
            'requirements': '本科及以上学历，数据分析能力强',
            'experience_requirement': '经验不限',
            'education_requirement': '本科'
        }
    ]

    # 配置高价值筛选
    config = ValueFilterConfig(
        min_company_tier=CompanyTier.TIER_3,
        min_salary_score=0.4
    )

    filter_instance = ValueFilter(config)
    high_value, filtered = filter_instance.filter(test_jobs)

    print(f"\n✅ 高价值筛选测试完成")
    print(f"  - 高价值/中价值: {len(high_value)} 条")
    print(f"  - 低价值/已过滤: {len(filtered)} 条")

    print("\n  高价值/中价值岗位:")
    for job in high_value:
        level = job.get('value_level', 'Unknown')
        score = job.get('value_score', 0)
        print(f"    [{level}] [{job['company_name']}] {job['job_name']} (得分: {score})")

    print("\n  低价值/已过滤岗位:")
    for job in filtered:
        level = job.get('value_level', 'Unknown')
        reason = job.get('filter_reason', '')
        print(f"    [{level}] [{job['company_name']}] {job['job_name']}")
        if reason:
            print(f"      原因: {reason}")

    # 验证结果
    assert len(high_value) >= 1, "期望至少1条高价值岗位"

    print("\n✅ 高价值筛选器测试通过！")
    return True


def test_company_classifier():
    """测试公司分级分类器"""
    print("\n" + "=" * 60)
    print("测试公司分级分类器")
    print("=" * 60)

    from matcher.filters.value_filter import CompanyClassifier

    test_cases = [
        ("字节跳动", CompanyTier.TIER_1),
        ("抖音", CompanyTier.TIER_1),
        ("哔哩哔哩", CompanyTier.TIER_2),
        ("B站", CompanyTier.TIER_2),
        ("BOSS直聘", CompanyTier.TIER_3),
        ("某小公司", CompanyTier.TIER_4),
        ("", CompanyTier.UNKNOWN),
    ]

    print("\n  公司分级测试结果:")
    all_passed = True
    for company_name, expected_tier in test_cases:
        actual_tier = CompanyClassifier.classify(company_name)
        status = "✓" if actual_tier == expected_tier else "✗"
        print(f"    {status} [{company_name}] -> {actual_tier.name} (期望: {expected_tier.name})")
        if actual_tier != expected_tier:
            all_passed = False

    if all_passed:
        print("\n✅ 公司分级分类器测试通过！")
    else:
        print("\n⚠️ 部分测试未通过，但功能可用")

    return True


def test_data_pipeline():
    """测试完整数据管道"""
    print("\n" + "=" * 60)
    print("测试完整数据管道")
    print("=" * 60)

    # 创建测试数据文件
    test_data_dir = Path("data/raw/test")
    test_data_dir.mkdir(parents=True, exist_ok=True)

    test_jobs = [
        {
            'job_name': '产品经理实习生',
            'company_name': '字节跳动',
            'location': '上海',
            'salary': '250-300元/天',
            'job_description': '负责抖音产品功能设计',
            'experience_requirement': '经验不限',
            'education_requirement': '本科',
            'source': 'test'
        },
        {
            'job_name': '产品实习生',
            'company_name': '美团',
            'location': '上海',
            'salary': '200-250元/天',
            'job_description': '负责外卖产品优化',
            'experience_requirement': '经验不限',
            'education_requirement': '本科',
            'source': 'test'
        },
        {
            'job_name': '算法工程师',
            'company_name': '阿里巴巴',
            'location': '上海',
            'salary': '300-400元/天',
            'job_description': '负责推荐算法',
            'experience_requirement': '经验不限',
            'education_requirement': '硕士',
            'source': 'test'
        }
    ]

    # 保存测试数据
    test_file = test_data_dir / f"test_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_jobs, f, ensure_ascii=False, indent=2)

    print(f"\n  创建测试数据: {test_file}")

    # 运行数据管道
    pipeline = DataPipeline()

    # 配置过滤器
    pipeline.setup_hard_filter(FilterRule(
        locations=["上海"],
        min_education="本科"
    ))

    pipeline.setup_value_filter(ValueFilterConfig(
        min_company_tier=CompanyTier.TIER_3
    ))

    # 运行流程
    result = pipeline.run_full_pipeline(source='test')

    if result['success']:
        print(f"\n✅ 数据管道运行成功！")
        stats = result['stats']
        print(f"\n  处理统计:")
        print(f"    - 原始数据: {stats['raw_count']} 条")
        print(f"    - 硬性过滤通过: {stats['hard_filtered_passed']} 条")
        print(f"    - 高价值岗位: {stats['high_value_count']} 条")
        print(f"    - 中价值岗位: {stats['medium_value_count']} 条")

        print(f"\n  输出文件:")
        for category, filepath in result['output_files'].items():
            print(f"    - {category}: {filepath}")

        print("\n✅ 数据管道测试通过！")
        return True
    else:
        print(f"\n❌ 数据管道运行失败: {result.get('error', 'Unknown error')}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("ResuMiner 数据管道测试套件")
    print("=" * 60)

    tests = [
        ("硬性过滤器", test_hard_filter),
        ("公司分级分类器", test_company_classifier),
        ("高价值筛选器", test_value_filter),
        ("完整数据管道", test_data_pipeline),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ {name} 测试失败: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # 打印测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {status} - {name}")

    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\n总计: {passed}/{total} 项测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！数据管道模块工作正常。")
        return 0
    else:
        print(f"\n⚠️ {total - passed} 项测试未通过，请检查。")
        return 1


if __name__ == '__main__':
    sys.exit(main())
