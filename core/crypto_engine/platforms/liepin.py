#!/usr/bin/env python3
"""
猎聘加密/请求处理模块
通过RPC调用浏览器环境执行请求
"""

import logging
import requests

logger = logging.getLogger(__name__)


class LiepinCrypto:
    """猎聘加密处理类"""
    
    def __init__(self, rpc_url="http://localhost:5600"):
        self.rpc_url = rpc_url
    
    def search_jobs(
        self,
        keyword: str,
        page_num: int,
        city: str = "020",
        page_size: int = 20
    ):
        """
        通过RPC调用猎聘搜索API
        
        Args:
            keyword: 搜索关键词
            page_num: 页码（从1开始）
            city: 城市代码（020=上海）
            page_size: 每页数量
            
        Returns:
            API响应数据
        """
        try:
            url = f"{self.rpc_url}/invoke/liepin/search_jobs"
            payload = {
                "keyword": keyword,
                "pageNum": page_num,
                "city": city,
                "pageSize": page_size
            }
            
            logger.info(f"[LiepinCrypto] Searching: keyword={keyword}, page={page_num}")
            
            resp = requests.post(url, json=payload, timeout=60)
            if resp.status_code != 200:
                raise RuntimeError(f"Liepin RPC HTTP {resp.status_code}: {resp.text}")
            
            data = resp.json()
            if data.get("status") != "success":
                raise RuntimeError(f"Liepin RPC business error: {data}")
            
            # RPC返回的结构: {"status": "success", "result": {...}}
            # result里面包含: {"data": {...}, "total_count": 20, "method": "dom_parsing"} 或 {"blocked": true, "message": "..."}
            rpc_result = data.get("result", {})
            
            # 检查是否被拦截
            if rpc_result.get("blocked"):
                logger.warning(f"[LiepinCrypto] Blocked: {rpc_result.get('message', 'Unknown')}")
                return {"blocked": True, "message": rpc_result.get("message", "需要登录")}
            
            if rpc_result.get("status") == "error":
                logger.error(f"[LiepinCrypto] Error: {rpc_result.get('error')}")
                return {"error": rpc_result.get("error")}
            
            # 返回RPC结果（包含data、total_count、method等）
            return rpc_result
            
        except Exception as e:
            logger.error(f"[LiepinCrypto] Request exception: {e}")
            raise
