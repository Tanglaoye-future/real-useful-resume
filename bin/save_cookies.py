#!/usr/bin/env python3
"""
手动保存猎聘 Cookie 脚本
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def get_liepin_cookie_path():
    """获取猎聘 Cookie 保存路径 - 使用规范路径"""
    cookies_dir = project_root / 'data' / 'cookies'
    os.makedirs(cookies_dir, exist_ok=True)
    return str(cookies_dir / 'liepin_cookies.json')


async def save_cookies():
    """连接到已打开的浏览器并保存 Cookie"""
    print("=" * 60)
    print("保存猎聘 Cookie")
    print("=" * 60)
    print()
    
    async with async_playwright() as p:
        # 尝试连接到已打开的浏览器
        try:
            print("[1/3] 尝试连接到已打开的浏览器...")
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            print("    ✓ 已连接到浏览器")
        except Exception as e:
            print(f"    ✗ 无法连接到浏览器: {e}")
            print("    请确保浏览器已打开并开启了远程调试端口")
            return False
        
        # 获取所有上下文
        contexts = browser.contexts
        if not contexts:
            print("    ✗ 没有找到浏览器上下文")
            return False
        
        print(f"[2/3] 找到 {len(contexts)} 个浏览器上下文")
        
        # 获取第一个上下文的 Cookie
        context = contexts[0]
        cookies = await context.cookies()
        
        print(f"    获取到 {len(cookies)} 个 Cookie")
        
        # 显示关键 Cookie
        print()
        print("关键 Cookie:")
        for cookie in cookies:
            if cookie['name'] in ['XSRF-TOKEN', '__uuid', '__sessionId', 'session', 'acw_tc', 'aliyungf_tc']:
                print(f"    {cookie['name']}: {cookie['value'][:50]}...")
        
        # 确保 cookies 目录存在
        cookie_path = get_liepin_cookie_path()
        
        # 保存到文件
        print()
        print("[3/3] 保存 Cookie...")
        with open(cookie_path, "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        
        print(f"    ✓ Cookie 已保存到: {cookie_path}")
        
        await browser.close()
        
        print()
        print("=" * 60)
        print("Cookie 保存完成！")
        print("=" * 60)
        
        return True


if __name__ == "__main__":
    result = asyncio.run(save_cookies())
    
    if result:
        # 验证保存的 Cookie
        cookie_path = get_liepin_cookie_path()
        if os.path.exists(cookie_path):
            with open(cookie_path, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            
            print()
            print("验证保存的 Cookie:")
            print(f"    总共 {len(cookies)} 个 Cookie")
            
            xsrf_token = None
            for cookie in cookies:
                if cookie['name'] == 'XSRF-TOKEN':
                    xsrf_token = cookie['value']
                    break
            
            if xsrf_token:
                print(f"    XSRF-TOKEN: {xsrf_token[:30]}...")
            else:
                print("    警告: 未找到 XSRF-TOKEN")
