"""RPC client for yingjiesheng.com — fetches list and detail pages via the
local Playwright RPC server.

Uses the generic `/invoke/yingjiesheng/fetch_detail` endpoint; the server
lazily creates a Playwright page for "yingjiesheng" the first time it is
called (server.py: PlaywrightContext.fetch_detail_html), so no init script
or cookie setup is required.
"""
from __future__ import annotations

import logging

import requests

logger = logging.getLogger(__name__)

LIST_URL_PAGE1 = "https://www.yingjiesheng.com/shanghai/"
LIST_URL_PAGE_N = "https://www.yingjiesheng.com/shanghai-morejob-{n}.html"


class YingjieshengClient:
    """Thin RPC client for yingjiesheng list/detail page fetches."""

    def __init__(self, rpc_url: str = "http://127.0.0.1:5600"):
        self.rpc_url = rpc_url

    def fetch_html(self, url: str, timeout: int = 60) -> dict:
        """Fetch a URL via the RPC server.

        Returns:
            {"html": str, "blocked": bool, "title": str}
            {"html": "", "blocked": False, "error": str}
        """
        if not url:
            return {"html": "", "blocked": False, "error": "url_required"}
        rpc = f"{self.rpc_url}/invoke/yingjiesheng/fetch_detail"
        try:
            resp = requests.post(rpc, json={"url": url}, timeout=timeout)
            if resp.status_code != 200:
                raise RuntimeError(
                    f"Yingjiesheng RPC HTTP {resp.status_code}: {resp.text}"
                )
            data = resp.json()
            if data.get("status") != "success":
                raise RuntimeError(f"Yingjiesheng RPC business error: {data}")
            return data.get("result", {}) or {}
        except Exception as e:
            logger.error("[YingjieshengClient] fetch_html(%s) failed: %s", url, e)
            return {"html": "", "blocked": False, "error": str(e)}

    def fetch_list_html(self, page_num: int) -> dict:
        url = LIST_URL_PAGE1 if page_num <= 1 else LIST_URL_PAGE_N.format(n=page_num)
        return self.fetch_html(url)

    def fetch_detail_html(self, url: str) -> dict:
        return self.fetch_html(url)
