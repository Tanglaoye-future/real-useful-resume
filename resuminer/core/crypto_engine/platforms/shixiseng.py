import logging
import requests

logger = logging.getLogger(__name__)

class ShixisengCrypto:
    def __init__(self, rpc_url="http://localhost:5600"):
        self.rpc_url = rpc_url
        self.font_mapping = {}

    def decrypt_text(self, encrypted_text, woff_url=None):
        """
        通过 RPC 调用浏览器环境解密字体
        """
        try:
            url = f"{self.rpc_url}/invoke/shixiseng/decrypt_font"
            payload = {"unicode_str": encrypted_text}
            resp = requests.post(url, json=payload, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    return data.get("result")
            logger.error(f"Shixiseng RPC failed: {resp.text}")
        except Exception as e:
            logger.error(f"Shixiseng RPC request exception: {e}")
            
        return encrypted_text
