#!/usr/bin/env python3
"""
测试三个平台爬虫能力对比
- 前程无忧 (51job)
- Boss直聘
- 猎聘
"""

import sys
import os
sys.path.insert(0, 'c:\\Users\\Lenovo\\useful-version')

from crawler_engine.spiders.job51_v2 import Job51SpiderV2
from crawler_engine.spiders.boss_v2 import BossSpiderV2
from crawler_engine.spiders.liepin_v2 import LiepinSpiderV2
import json

class MockScheduler:
    """模拟调度器"""
    def __init__(self):
        self.cookies = {}
        
    def throttle(self, host, seconds):
        pass
        
    def get_proxy(self):
        return None
        
    def get_cookie(self, platform):
        return self.cookies.get(platform)
        
    def set_cookie(self, platform, cookie):
        self.cookies[platform] = cookie

def analyze_job_fields(job, platform_name):
    """分析单个 job 的字段完整性"""
    fields = {
        "platform": platform_name,
        "job_title": bool(job.get("job_name") and len(str(job.get("job_name", ""))) > 0),
        "company_name": bool(job.get("company_name") and len(str(job.get("company_name", ""))) > 0),
        "location": bool(job.get("location") and len(str(job.get("location", ""))) > 0),
        "salary": bool(job.get("salary") and len(str(job.get("salary", ""))) > 0),
        "jd_url": bool(job.get("jd_url") and str(job.get("jd_url", "")).startswith("http")),
        "jd_content": bool(job.get("jd_content") and len(str(job.get("jd_content", ""))) > 20),
        "job_description": bool(job.get("job_description") and len(str(job.get("job_description", ""))) > 10),
        "job_requirement": bool(job.get("job_requirement") and len(str(job.get("job_requirement", ""))) > 10),
        "publish_date": bool(job.get("publish_date") and len(str(job.get("publish_date", ""))) > 0),
        "source_job_id": bool(job.get("source_job_id") and len(str(job.get("source_job_id", ""))) > 0),
    }
    
    # 计算完整率
    total_fields = len(fields) - 1  # 排除 platform
    filled_fields = sum(1 for k, v in fields.items() if k != "platform" and v)
    fields["completeness_rate"] = filled_fields / total_fields if total_fields > 0 else 0
    
    return fields

def test_spider(spider_class, platform_name, cookie=""):
    """测试单个爬虫"""
    print(f"\n{'='*70}")
    print(f"测试平台: {platform_name}")
    print(f"{'='*70}")
    
    scheduler = MockScheduler()
    spider = spider_class(scheduler, cookie)
    
    # 检查是否有字段校验机制
    has_validation = hasattr(spider, '_validate_and_enhance_fields')
    print(f"\n字段校验机制: {'✅ 已启用' if has_validation else '❌ 未启用'}")
    
    # 检查是否有 split_jd_sections 方法（继承自 BaseSpider）
    has_split = hasattr(spider, 'split_jd_sections')
    print(f"JD分割方法: {'✅ 已继承' if has_split else '❌ 未继承'}")
    
    # 获取爬虫配置
    print(f"\n爬虫配置:")
    if hasattr(spider, 'max_pages') or hasattr(spider, 'max_safety_pages'):
        max_pages = getattr(spider, 'max_pages', getattr(spider, 'max_safety_pages', 'N/A'))
        print(f"  最大页数: {max_pages}")
    if hasattr(spider, 'keyword'):
        print(f"  关键词: {spider.keyword}")
    if hasattr(spider, 'primary_keywords'):
        print(f"  关键词: {spider.primary_keywords}")
    
    # 检查 parse 方法签名
    import inspect
    if hasattr(spider, 'parse'):
        sig = inspect.signature(spider.parse)
        print(f"  parse方法参数: {list(sig.parameters.keys())}")
    
    return {
        "platform": platform_name,
        "has_validation": has_validation,
        "has_split_jd": has_split,
        "spider_class": spider_class.__name__
    }

def compare_spiders():
    """对比三个平台的爬虫能力"""
    print("="*70)
    print("爬虫能力对比测试")
    print("="*70)
    
    results = []
    
    # 测试前程无忧
    try:
        result_51 = test_spider(Job51SpiderV2, "前程无忧(51job)")
        results.append(result_51)
    except Exception as e:
        print(f"❌ 前程无忧测试失败: {e}")
        results.append({"platform": "前程无忧(51job)", "error": str(e)})
    
    # 测试 Boss直聘
    try:
        result_boss = test_spider(BossSpiderV2, "Boss直聘")
        results.append(result_boss)
    except Exception as e:
        print(f"❌ Boss直聘测试失败: {e}")
        results.append({"platform": "Boss直聘", "error": str(e)})
    
    # 测试猎聘
    try:
        result_liepin = test_spider(LiepinSpiderV2, "猎聘")
        results.append(result_liepin)
    except Exception as e:
        print(f"❌ 猎聘测试失败: {e}")
        results.append({"platform": "猎聘", "error": str(e)})
    
    # 对比结果
    print("\n" + "="*70)
    print("对比结果汇总")
    print("="*70)
    
    print("\n字段校验机制:")
    for r in results:
        status = "✅" if r.get("has_validation") else "❌"
        print(f"  {status} {r['platform']}")
    
    print("\nJD分割方法:")
    for r in results:
        status = "✅" if r.get("has_split_jd") else "❌"
        print(f"  {status} {r['platform']}")
    
    # 判断是否需要同步
    need_sync = False
    job51_has_validation = any(r.get("has_validation") for r in results if r['platform'] == "前程无忧(51job)")
    
    for r in results:
        if r['platform'] != "前程无忧(51job)" and not r.get("has_validation") and job51_has_validation:
            need_sync = True
            break
    
    print("\n" + "="*70)
    if need_sync:
        print("⚠️ 需要同步: Boss直聘和猎聘需要添加字段校验机制")
    else:
        print("✅ 无需同步: 所有平台爬虫能力一致")
    print("="*70)
    
    return results, need_sync

def test_jd_parsing():
    """测试 JD 解析能力"""
    print("\n" + "="*70)
    print("JD 解析能力测试")
    print("="*70)
    
    scheduler = MockScheduler()
    
    # 使用前程无忧的 split_jd_sections 方法测试
    spider_51 = Job51SpiderV2(scheduler, "")
    
    test_jd = """岗位职责：
1. 负责前端页面开发
2. 参与技术方案设计

任职要求：
1. 计算机相关专业本科以上学历
2. 熟悉React、Vue等前端框架
3. 有良好的沟通能力"""
    
    desc, req = spider_51.split_jd_sections(test_jd)
    
    print(f"\n测试 JD 文本:")
    print(f"  岗位职责: {desc[:50]}..." if desc else "  岗位职责: (空)")
    print(f"  任职要求: {req[:50]}..." if req else "  任职要求: (空)")
    
    if desc and req:
        print("\n✅ JD 分割功能正常")
        return True
    else:
        print("\n❌ JD 分割功能异常")
        return False

if __name__ == "__main__":
    try:
        # 测试爬虫能力对比
        results, need_sync = compare_spiders()
        
        # 测试 JD 解析
        jd_ok = test_jd_parsing()
        
        print("\n" + "="*70)
        print("测试完成")
        print("="*70)
        
        if need_sync:
            print("\n建议操作:")
            print("1. 为 Boss直聘添加 _validate_and_enhance_fields 方法")
            print("2. 为猎聘添加 _validate_and_enhance_fields 方法")
            print("3. 确保两个平台都正确调用 split_jd_sections 分割 JD")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
