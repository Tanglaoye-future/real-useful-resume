#!/usr/bin/env python3
"""
测试Boss直聘页面结构
"""

import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()
        
        # 访问搜索页面
        url = "https://www.zhipin.com/web/geek/job?query=实习&city=101020100&page=1"
        logger.info(f"访问: {url}")
        page.goto(url, wait_until="networkidle", timeout=60000)
        
        # 等待一下
        page.wait_for_timeout(3000)
        
        # 获取页面标题
        title = page.title()
        logger.info(f"页面标题: {title}")
        
        # 尝试多种选择器
        selectors = [
            ".job-card-wrapper",
            ".job-card",
            "[data-jobid]",
            ".search-job-result .job-card",
            ".job-list .job-card",
            "li.job-card-wrapper",
            ".card-list .card",
            ".job-list-item",
        ]
        
        for selector in selectors:
            try:
                cards = page.query_selector_all(selector)
                if cards:
                    logger.info(f"选择器 '{selector}' 找到 {len(cards)} 个元素")
            except Exception as e:
                logger.debug(f"选择器 '{selector}' 失败: {e}")
        
        # 保存页面内容用于分析
        html = page.content()
        with open("boss_page_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        logger.info("页面内容已保存到 boss_page_debug.html")
        
        browser.close()

if __name__ == '__main__':
    analyze_page()
