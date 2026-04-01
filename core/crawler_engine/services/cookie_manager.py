from playwright.sync_api import sync_playwright
import logging
import time

logger = logging.getLogger(__name__)

class CookieManager:
    """
    使用 Playwright 无头浏览器动态获取各个平台的初始 Cookie，
    以绕过如 51job 的 ACW Challenge 或拉勾网的初始防伪造校验。
    """
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None

    def start_browser(self, headless=True):
        logger.info(f"Starting Playwright browser (headless={headless})...")
        self.playwright = sync_playwright().start()
        # 禁用 webdriver 特征
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="zh-CN",
            timezone_id="Asia/Shanghai"
        )

    def close_browser(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Playwright browser closed.")

    def _get_cookie_string(self, url):
        cookies = self.context.cookies(url)
        return "; ".join([f"{c['name']}={c['value']}" for c in cookies])

    def get_51job_cookie(self):
        """
        突破 51job 的 acw_sc__v2 挑战
        """
        logger.info("Fetching dynamic cookie for 51job...")
        page = self.context.new_page()
        try:
            # 访问搜索页，触发安全盾挑战
            page.goto("https://we.51job.com/pc/search?jobArea=020000&keyword=%E5%AE%9E%E4%B9%A0", wait_until="domcontentloaded", timeout=15000)
            # 等待页面重定向完成（通常安全盾会自动计算 cookie 并重载页面）
            page.wait_for_timeout(3000) 
            
            cookie_str = self._get_cookie_string("https://we.51job.com")
            logger.info(f"Successfully obtained 51job cookies: {cookie_str[:50]}...")
            return cookie_str
        except Exception as e:
            logger.error(f"Failed to get 51job cookie: {e}")
            return ""
        finally:
            page.close()

    def get_lagou_cookie(self):
        """
        突破拉勾网的初始访客追踪 Cookie
        """
        logger.info("Fetching dynamic cookie for Lagou...")
        page = self.context.new_page()
        try:
            page.goto("https://www.lagou.com/jobs/list_%E5%AE%9E%E4%B9%A0?city=%E4%B8%8A%E6%B5%B7", wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)
            
            cookie_str = self._get_cookie_string("https://www.lagou.com")
            logger.info(f"Successfully obtained Lagou cookies: {cookie_str[:50]}...")
            return cookie_str
        except Exception as e:
            logger.error(f"Failed to get Lagou cookie: {e}")
            return ""
        finally:
            page.close()

    def get_shixiseng_cookie(self):
        """
        获取实习僧基础会话 Cookie
        """
        logger.info("Fetching dynamic cookie for Shixiseng...")
        page = self.context.new_page()
        try:
            page.goto("https://www.shixiseng.com/interns", wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)
            
            cookie_str = self._get_cookie_string("https://www.shixiseng.com")
            return cookie_str
        except Exception as e:
            logger.error(f"Failed to get Shixiseng cookie: {e}")
            return ""
        finally:
            page.close()
