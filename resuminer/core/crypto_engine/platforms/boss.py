import os
import json
import logging
import requests

logger = logging.getLogger(__name__)

class BossCrypto:
    def __init__(self, rpc_url="http://localhost:5600"):
        self.rpc_url = rpc_url

    def generate_stoken(self, seed, timestamp):
        """
        通过 RPC 调用浏览器环境生成 __zp_stoken__
        """
        try:
            url = f"{self.rpc_url}/invoke/boss/get_stoken"
            payload = {"seed": seed, "ts": timestamp}
            resp = requests.post(url, json=payload, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    return data.get("result")
                else:
                    logger.warning(f"RPC business error: {data}")
            else:
                logger.error(f"RPC failed with status {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"RPC request exception: {e}")
        
        # 备用方案：生成简化版 stoken
        import base64
        fallback = base64.b64encode(f"{seed}_{timestamp}".encode()).decode().replace('=', '')
        logger.info(f"Using fallback stoken: {fallback[:20]}...")
        return fallback

    def get_ja3_fingerprint(self):
        return "chrome120"
