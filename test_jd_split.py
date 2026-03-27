#!/usr/bin/env python3
"""
测试 JD 分割逻辑修复效果
"""

import sys
sys.path.insert(0, 'c:\\Users\\Lenovo\\useful-version')

from crawler_engine.base_spider import BaseSpider
from crawler_engine.scheduler import RedisScheduler

class TestSpider(BaseSpider):
    def __init__(self):
        # 创建一个模拟的调度器
        class MockScheduler:
            def throttle(self, host, seconds):
                pass
            def get_proxy(self):
                return None
        super().__init__("Test", MockScheduler(), "")

    def run(self):
        pass

    def parse(self, response):
        pass

def test_split_jd_sections():
    spider = TestSpider()

    # 测试用例 1: 标准格式（带明确标记）
    jd1 = """岗位职责：
1. 负责前端页面开发
2. 参与技术方案设计

任职要求：
1. 计算机相关专业本科以上学历
2. 熟悉React、Vue等前端框架
3. 有良好的沟通能力"""

    desc1, req1 = spider.split_jd_sections(jd1)
    print("=" * 50)
    print("测试用例 1: 标准格式（带明确标记）")
    print(f"岗位职责: {desc1[:50]}...")
    print(f"任职要求: {req1[:50]}...")
    print(f"✅ 通过" if req1 and desc1 else "❌ 失败")

    # 测试用例 2: 无明确标记的 JD
    jd2 = """我们正在寻找一位有激情的前端工程师。

你将负责：
- 开发和维护公司核心产品的前端界面
- 与设计师和后端工程师协作

希望你具备：
- 扎实的JavaScript基础
- 熟悉现代前端开发流程
- 对用户体验有追求"""

    desc2, req2 = spider.split_jd_sections(jd2)
    print("\n" + "=" * 50)
    print("测试用例 2: 无明确标记的 JD")
    print(f"岗位职责: {desc2[:50]}...")
    print(f"任职要求: {req2[:50]}...")
    print(f"✅ 通过" if req2 else "🟡 使用兜底策略")

    # 测试用例 3: 只有任职要求标记
    jd3 = """职位描述：
负责公司产品的后端开发工作，参与系统架构设计。

职位要求：
1. 3年以上Java开发经验
2. 熟悉Spring Boot、MySQL
3. 有微服务架构经验优先"""

    desc3, req3 = spider.split_jd_sections(jd3)
    print("\n" + "=" * 50)
    print("测试用例 3: 只有任职要求标记")
    print(f"岗位职责: {desc3[:50]}...")
    print(f"任职要求: {req3[:50]}...")
    print(f"✅ 通过" if req3 else "❌ 失败")

    # 测试用例 4: 短文本
    jd4 = "负责前端开发，要求熟悉React。"
    desc4, req4 = spider.split_jd_sections(jd4)
    print("\n" + "=" * 50)
    print("测试用例 4: 短文本")
    print(f"岗位职责: {desc4}")
    print(f"任职要求: {req4}")
    print(f"✅ 通过" if desc4 else "❌ 失败")

    # 测试用例 5: 空文本
    desc5, req5 = spider.split_jd_sections("")
    print("\n" + "=" * 50)
    print("测试用例 5: 空文本")
    print(f"岗位职责: '{desc5}'")
    print(f"任职要求: '{req5}'")
    print(f"✅ 通过" if desc5 == "" and req5 == "" else "❌ 失败")

    # 测试用例 6: 占位符内容
    jd6 = "详情需进入页面提取"
    desc6, req6 = spider.split_jd_sections(jd6)
    print("\n" + "=" * 50)
    print("测试用例 6: 占位符内容")
    print(f"岗位职责: '{desc6}'")
    print(f"任职要求: '{req6}'")
    print(f"✅ 通过" if desc6 == "" and req6 == "" else "❌ 失败")

    print("\n" + "=" * 50)
    print("测试完成!")

if __name__ == "__main__":
    test_split_jd_sections()
