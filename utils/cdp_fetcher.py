from playwright.sync_api import sync_playwright
import time
import logging
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_detail_via_cdp(target_url: str) -> str:
    """
    通过 CDP 连接到本地真实浏览器，绕过风控获取页面内容
    """
    with sync_playwright() as p:
        try:
            # 1. 连接到本地开启了 9222 调试端口的 Chrome
            logging.info(f"正在通过 CDP 连接到浏览器获取: {target_url}")
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            
            # 2. 获取当前的上下文和页面
            context = browser.contexts[0]
            # 优先使用一个新标签页，避免覆盖用户当前正在看的页面
            page = context.new_page()
            
            # 3. 拦截请求，过滤掉不必要的图片/视频/字体以提高速度，但保留 JS 和 CSS 以防反爬
            page.route("**/*.{png,jpg,jpeg,mp4,gif,woff,woff2,ttf,svg}", lambda route: route.abort())
            
            # 注入 stealth 脚本，掩盖 Playwright 特征
            stealth_js = """
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
                Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
                );
                Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
            """
            page.add_init_script(stealth_js)
            
            # 伪造真实的请求头和来源 (Referer)
            is_51job = "51job.com" in target_url
            is_liepin = "liepin.com" in target_url
            
            # 针对 51job 等严格平台的随机化访问间隔和鼠标轨迹
            time.sleep(random.uniform(2.5, 5.0))
            
            # 4. 访问目标岗位详情页 (加入 Referer)
            try:
                if is_51job:
                    # 假装从 51job 的搜索页或首页点进去的
                    referer = "https://we.51job.com/pc/search"
                    page.goto(target_url, wait_until="domcontentloaded", timeout=30000, referer=referer)
                elif is_liepin:
                    referer = "https://www.liepin.com/zhaopin/"
                    page.goto(target_url, wait_until="domcontentloaded", timeout=30000, referer=referer)
                else:
                    page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            except Exception as e:
                if "Timeout" in str(e):
                    logging.warning(f"页面加载超时，尝试直接获取现有内容: {target_url}")
                else:
                    raise
            
            # 5. 模拟真人微调滚动，触发懒加载
            page.mouse.wheel(0, 500)
            page.wait_for_timeout(1000)
            page.mouse.wheel(0, 300)
            page.wait_for_timeout(500)
            
            def safe_get_content(p):
                for _ in range(5):
                    try:
                        return p.content()
                    except Exception as ex:
                        if "navigating" in str(ex).lower() or "navigation" in str(ex).lower():
                            time.sleep(1.5)
                        else:
                            raise
                return ""
            
            # 6. 检查是否出现验证码或风控页面
            html_content = safe_get_content(page)
            
            # 检查岗位是否已下线或不存在（猎聘常见）
            if "此页面似乎不存在" in html_content or "职位已下线" in html_content or "停止招聘" in html_content:
                logging.warning(f"该岗位已下线或页面不存在: {target_url}")
                page.close()
                return "JOB_OFFLINE"
                
            # 检查 51job 严重拦截 (403/Security Threat)
            if "Sorry, your request has been blocked as it may cause potential threats" in html_content or "ac110001" in html_content:
                logging.error(f"遭遇 51job 严重 WAF 拦截 (403 Blocked): {target_url}")
                page.close()
                return "WAF_BLOCKED"
            
            def is_blocked(html: str) -> bool:
                lower_html = html.lower()
                return any(k in lower_html for k in ["安全中心", "访问受限", "请完成验证", "captcha", "traceid", "verify", "滑块", "访问验证", "拖动到最右边"])

            if is_blocked(html_content):
                logging.warning("检测到风控页面/验证码，尝试自动滑动或等待手动处理！")
                
                # 尝试简单识别并滑动滑块 (针对截图里的那种横向滑块)
                try:
                    # 针对 51job 滑块可能存在于 iframe 中的情况
                    slider = None
                    box = None
                    
                    # 1. 尝试主页面查找
                    slider_locator = page.locator(".nc_iconfont.btn_slide").first
                    if not slider_locator.is_visible(timeout=1000):
                        slider_locator = page.locator(".btn_slide").first
                        
                    if slider_locator.is_visible(timeout=1000):
                        slider = slider_locator
                        box = slider.bounding_box()
                    else:
                        # 2. 尝试在所有的 iframe 中查找滑块
                        for frame in page.frames:
                            try:
                                frame_slider = frame.locator(".nc_iconfont.btn_slide").first
                                if not frame_slider.is_visible(timeout=500):
                                    frame_slider = frame.locator(".btn_slide").first
                                if frame_slider.is_visible(timeout=500):
                                    # 注意: frame.locator 拿不到相对于主页面的 absolute box
                                    # 但可以用 frame 内的坐标进行简单操作，或者让 page 直接基于视口操作
                                    logging.info(f"在 iframe ({frame.name}) 中找到滑块")
                                    box = frame_slider.bounding_box()
                                    if box:
                                        # 为了安全，直接用 frame.mouse 会报错，用 page.mouse 需要绝对坐标
                                        # 如果是 iframe，最好用 locator.hover() 和 mouse.down()
                                        frame_slider.hover()
                                        page.mouse.down()
                                        page.mouse.move(box["x"] + 150, box["y"], steps=10)
                                        time.sleep(0.1)
                                        page.mouse.move(box["x"] + 350, box["y"], steps=15)
                                        time.sleep(0.2)
                                        page.mouse.move(box["x"] + 500, box["y"], steps=5)
                                        page.mouse.up()
                                        time.sleep(2)
                                        break
                            except Exception:
                                pass

                    # 3. 主页面的滑动处理
                    if box and slider:
                        logging.info("找到主页面滑块元素，尝试自动滑动...")
                        
                        start_x = box["x"] + box["width"] / 2
                        start_y = box["y"] + box["height"] / 2
                        
                        page.mouse.move(start_x, start_y)
                        page.mouse.down()
                        time.sleep(0.1)
                        
                        # 模拟真人的曲线和停顿
                        # 51job 滑块一般比较长，直接拖过头确保成功，然后加一点回弹
                        page.mouse.move(start_x + 100, start_y + random.uniform(-2, 2), steps=5)
                        time.sleep(random.uniform(0.05, 0.1))
                        page.mouse.move(start_x + 300, start_y + random.uniform(-2, 2), steps=10)
                        time.sleep(random.uniform(0.05, 0.15))
                        page.mouse.move(start_x + 500, start_y + random.uniform(-2, 2), steps=5)
                        
                        # 稍微回弹一下再松手，更像真人
                        page.mouse.move(start_x + 480, start_y + random.uniform(-1, 1), steps=2)
                        
                        page.mouse.up()
                        time.sleep(2.5) # 给它一点时间验证
                        
                    html_content = safe_get_content(page)
                except Exception as slide_e:
                    logging.debug(f"自动滑动尝试失败: {slide_e}")

                # 如果自动滑动没成功，或者没找到滑块，等待用户手动处理
                if is_blocked(html_content):
                    logging.warning("自动滑动未能解决，请在打开的浏览器中手动处理！")
                    for _ in range(15):
                        time.sleep(2)
                        html_content = safe_get_content(page)
                        if not is_blocked(html_content):
                            logging.info("验证码似乎已手动解决，等待页面加载完成...")
                            page.wait_for_timeout(3000)
                            html_content = safe_get_content(page)
                            break
            
            # 关闭我们临时开的标签页
            page.close()
            return html_content
            
        except Exception as e:
            logging.error(f"CDP 获取失败: {e}")
            return ""

if __name__ == "__main__":
    # 测试代码
    test_url = "https://www.liepin.com/job/1980753073.shtml" # 随便找个岗位链接测试
    html = fetch_detail_via_cdp(test_url)
    if html:
        print(f"成功绕过风控，获取到页面长度: {len(html)}")
    else:
        print("获取失败，请确保已启动带有 --remote-debugging-port=9222 的 Chrome。")
