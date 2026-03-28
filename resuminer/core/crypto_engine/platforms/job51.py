import logging
import requests

logger = logging.getLogger(__name__)

class Job51Crypto:
    def __init__(self, rpc_url="http://localhost:5600"):
        self.rpc_url = rpc_url

    def solve_acw_sc_v2(self, arg1):
        """
        通过 RPC 调用浏览器环境计算 acw_sc__v2 Cookie
        """
        try:
            url = f"{self.rpc_url}/invoke/job51/get_acw_sc_v2"
            payload = {"arg1": arg1}
            resp = requests.post(url, json=payload, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    return data.get("result")
            logger.error(f"51job RPC failed: {resp.text}")
        except Exception as e:
            logger.error(f"51job RPC request exception: {e}")
            
        return f"mock_acw_{arg1}"

    def search_jobs(
        self,
        keyword: str,
        page_num: int,
        cookie_str: str = "",
        job_area: str = "020000",
        page_size: int = 20,
        request_id: str = ""
    ):
        try:
            url = f"{self.rpc_url}/invoke/job51/search_jobs"
            payload = {
                "keyword": keyword,
                "pageNum": page_num,
                "jobArea": job_area,
                "pageSize": page_size,
                "cookie": cookie_str,
                "requestId": request_id
            }
            resp = requests.post(url, json=payload, timeout=60)
            if resp.status_code != 200:
                raise RuntimeError(f"51job RPC HTTP {resp.status_code}: {resp.text}")
            data = resp.json()
            if data.get("status") != "success":
                raise RuntimeError(f"51job RPC business error: {data}")
            return data.get("result")
        except Exception as e:
            logger.error(f"51job search RPC request exception: {e}")
            raise

    def solve_slider(self, background_image, slice_image):
        pass
