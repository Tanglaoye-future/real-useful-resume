#!/usr/bin/env python3
"""
猎聘自动化登录脚本
使用 Playwright 打开浏览器，显示登录二维码，用户扫码后保存 Cookie
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


async def login_liepin():
    """
    猎聘自动化登录流程
    1. 打开猎聘登录页面
    2. 显示登录二维码
    3. 等待用户扫码登录
    4. 保存登录后的 Cookie
    """
    print("=" * 60)
    print("猎聘自动化登录")
    print("=" * 60)
    print()
    
    async with async_playwright() as p:
        # 启动浏览器（非无头模式，方便用户操作）
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        
        # 创建新页面
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="zh-CN",
            viewport={"width": 1280, "height": 800}
        )
        
        page = await context.new_page()
        
        # 访问猎聘首页
        print("[1/4] 正在打开猎聘网站...")
        await page.goto("https://www.liepin.com", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        # 检查是否已经登录
        is_logged_in = await page.evaluate("""() => {
            // 检查是否有用户头像或用户名显示
            const userAvatar = document.querySelector('.user-avatar, .header-user-avatar, [class*="user"]');
            const userName = document.querySelector('.user-name, .header-user-name');
            return !!(userAvatar || userName);
        }
        """)
        
        if is_logged_in:
            print("[2/4] 检测到您已经登录！")
        else:
            print("[2/4] 未登录，正在跳转到登录页面...")
            
            # 点击登录按钮
            try:
                # 尝试多种登录按钮选择器
                login_selectors = [
                    'a[href*="login"]',
                    '.login-btn',
                    '.header-login',
                    '[data-selector="login"]',
                    'text=登录',
                    'text=请登录'
                ]
                
                for selector in login_selectors:
                    try:
                        await page.click(selector, timeout=2000)
                        print(f"    点击登录按钮: {selector}")
                        break
                    except:
                        continue
                else:
                    # 如果没有找到登录按钮，直接访问登录页面
                    print("    直接访问登录页面...")
                    await page.goto("https://www.liepin.com/login", wait_until="domcontentloaded")
                
                await asyncio.sleep(3)
                
            except Exception as e:
                print(f"    访问登录页面: {e}")
                await page.goto("https://www.liepin.com/login", wait_until="domcontentloaded")
                await asyncio.sleep(3)
            
            print("[3/4] 请使用猎聘 APP 扫描二维码登录...")
            print("    请在浏览器中完成登录")
            print()
            print("    登录完成后，请按 Enter 键继续...")
            print()
            
            # 等待用户按 Enter 键
            await asyncio.get_event_loop().run_in_executor(None, input)
            
            print("    ✓ 用户确认登录完成")
            login_success = True
            
            # 导航回猎聘首页以确保获取正确的 Cookie
            print("    正在导航回猎聘首页...")
            await page.goto("https://www.liepin.com", wait_until="domcontentloaded")
            await asyncio.sleep(2)
        
        # 保存 Cookie
        print("[4/4] 正在保存 Cookie...")
        cookies = await context.cookies()
        
        # 确保 cookies 目录存在
        cookie_path = get_liepin_cookie_path()
        
        # 保存到文件
        with open(cookie_path, "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        
        print(f"    ✓ Cookie 已保存到: {cookie_path}")
        
        # 显示关键 Cookie
        print()
        print("关键 Cookie 信息:")
        for cookie in cookies:
            if cookie['name'] in ['XSRF-TOKEN', '__uuid', '__sessionId', 'session']:
                print(f"    {cookie['name']}: {cookie['value'][:50]}...")
        
        # 关闭浏览器
        await browser.close()
        
        print()
        print("=" * 60)
        print("登录完成！现在可以运行猎聘爬虫了。")
        print("=" * 60)
        
        return True


def load_liepin_cookies():
    """加载保存的猎聘 Cookie"""
    cookie_path = get_liepin_cookie_path()
    if not os.path.exists(cookie_path):
        return None
    
    with open(cookie_path, "r", encoding="utf-8") as f:
        cookies = json.load(f)
    
    # 转换为字符串格式
    cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
    return cookie_str


def get_liepin_xsrf_token():
    """获取 XSRF-TOKEN"""
    cookie_path = get_liepin_cookie_path()
    if not os.path.exists(cookie_path):
        return None
    
    with open(cookie_path, "r", encoding="utf-8") as f:
        cookies = json.load(f)
    
    for cookie in cookies:
        if cookie['name'] == 'XSRF-TOKEN':
            return cookie['value']
    
    return None


if __name__ == "__main__":
    # 运行登录流程
    result = asyncio.run(login_liepin())
    
    if result:
        # 显示加载的 Cookie
        print()
        print("验证 Cookie 加载:")
        cookies = load_liepin_cookies()
        if cookies:
            print(f"    Cookie 长度: {len(cookies)} 字符")
        
        xsrf_token = get_liepin_xsrf_token()
        if xsrf_token:
            print(f"    XSRF-TOKEN: {xsrf_token[:30]}...")
        else:
            print("    警告: 未找到 XSRF-TOKEN")
