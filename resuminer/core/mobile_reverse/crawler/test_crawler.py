#!/usr/bin/env python3
"""
移动端爬虫测试脚本
"""

import sys
sys.path.insert(0, str(Path(__file__).parent))

from crawler.boss_mobile_crawler import BossMobileCrawler

def test_search():
    """测试搜索功能"""
    print("测试移动端搜索...")
    
    crawler = BossMobileCrawler(
        # TODO: 填写实际的密钥和 token
        app_key="",
        app_secret="",
        token=""
    )
    
    jobs = crawler.search_jobs(keyword="实习", page=1)
    print(f"获取到 {len(jobs)} 个职位")
    
    for job in jobs[:3]:
        print(f"  - {job.title} @ {job.company}")

if __name__ == "__main__":
    test_search()
