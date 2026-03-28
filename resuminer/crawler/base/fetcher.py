from curl_cffi import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)

class Fetcher:
    """
    基于 curl_cffi 的高级网络请求器，支持完美的 TLS 和 HTTP/2 指纹伪装。
    替代传统的 requests，用于绕过 BOSS、领英等平台的高级反爬。
    """
    def __init__(self, proxy=None, impersonate="chrome120"):
        self.impersonate = impersonate
        self.proxy = proxy
        self.session = requests.Session(impersonate=self.impersonate)
        if self.proxy:
            self.session.proxies = {
                "http": self.proxy,
                "https": self.proxy
            }

    def update_proxy(self, new_proxy):
        self.proxy = new_proxy
        self.session.proxies = {
            "http": self.proxy,
            "https": self.proxy
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def request(self, method, url, **kwargs):
        """
        发起网络请求，支持自动重试
        """
        try:
            logger.debug(f"[{method}] {url} | impersonate={self.impersonate}")
            response = self.session.request(method, url, **kwargs)
            # 根据需要可以增加状态码判断，抛出异常以触发 retry
            if response.status_code in [403, 429, 999]:
                logger.warning(f"Blocked or Rate limited: {response.status_code}. Might need proxy rotation.")
                response.raise_for_status() 
            return response
        except Exception as e:
            logger.error(f"Request failed: {url} - {e}")
            raise
