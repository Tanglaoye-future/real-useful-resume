import hashlib
import time
import requests
import logging

logger = logging.getLogger(__name__)

class LagouCrypto:
    def __init__(self, rpc_url="http://localhost:5600"):
        self.rpc_url = rpc_url

    def generate_anit_forge_code(self, seed, cookie_str: str = ""):
        try:
            url = f"{self.rpc_url}/invoke/lagou/get_forge_code"
            payload = {"seed": seed, "cookie": cookie_str}
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code != 200:
                raise RuntimeError(f"Lagou RPC HTTP {resp.status_code}: {resp.text}")
            data = resp.json()
            if data.get("status") != "success":
                raise RuntimeError(f"Lagou RPC business error: {data}")
            return data.get("result")
        except Exception as e:
            logger.error(f"Lagou RPC request exception: {e}")
            raise

    def wait_for_manual_unblock(self, cookie_str: str = "", timeout_seconds: int = 300, poll_interval_seconds: float = 2.0, seed: str = "first=true&pn=1&kd=实习"):
        try:
            url = f"{self.rpc_url}/invoke/lagou/wait_for_unblock"
            payload = {
                "cookie": cookie_str,
                "timeout_seconds": timeout_seconds,
                "poll_interval_seconds": poll_interval_seconds,
                "seed": seed
            }
            resp = requests.post(url, json=payload, timeout=timeout_seconds + 10)
            if resp.status_code != 200:
                raise RuntimeError(f"Lagou wait RPC HTTP {resp.status_code}: {resp.text}")
            data = resp.json()
            if data.get("status") != "success":
                raise RuntimeError(f"Lagou wait RPC business error: {data}")
            return data.get("result", {})
        except Exception as e:
            logger.error(f"Lagou wait RPC request exception: {e}")
            raise

    def get_headers(self, cookie_dict, referer_url):
        timestamp = str(int(time.time() * 1000))
        # 实际可能需要组合多个参数作为 seed
        seed = f"v1.0_{timestamp}_search"
        forge_code = self.generate_anit_forge_code(seed)
        
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://www.lagou.com",
            "Referer": referer_url,
            "X-Anit-Forge-Code": forge_code,
            "X-Anit-Forge-Token": "None", 
            "X-Requested-With": "XMLHttpRequest"
        }
        
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
        headers["Cookie"] = cookie_str
        return headers
