"""RPC client for shixiseng.com — fetches list and detail pages via the
local Playwright RPC server.

Mirrors crawlers/rpc/liepin_client.py but uses the generic
`/invoke/shixiseng/fetch_detail` endpoint for both list and detail pages,
since the RPC server already initialises a Shixiseng-authenticated page
via `_init_detail_pages` (server.py).
"""
from __future__ import annotations

import logging
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

LIST_URL_BASE = "https://www.shixiseng.com/interns"


class ShixisengClient:
    """Thin RPC client for shixiseng list/detail page fetches."""

    def __init__(self, rpc_url: str = "http://127.0.0.1:5600"):
        self.rpc_url = rpc_url

    # ------------------------------------------------------------------
    # Generic page fetch (shared by list + detail)
    # ------------------------------------------------------------------

    def fetch_html(self, url: str, timeout: int = 60) -> dict:
        """Fetch a Shixiseng URL via the RPC server and return its HTML.

        Returns a dict shaped like:
            {"html": str, "blocked": bool, "title": str}
            {"html": "", "blocked": False, "error": str}
        """
        if not url:
            return {"html": "", "blocked": False, "error": "url_required"}
        rpc = f"{self.rpc_url}/invoke/shixiseng/fetch_detail"
        try:
            resp = requests.post(rpc, json={"url": url}, timeout=timeout)
            if resp.status_code != 200:
                raise RuntimeError(f"Shixiseng RPC HTTP {resp.status_code}: {resp.text}")
            data = resp.json()
            if data.get("status") != "success":
                raise RuntimeError(f"Shixiseng RPC business error: {data}")
            return data.get("result", {}) or {}
        except Exception as e:
            logger.error("[ShixisengClient] fetch_html(%s) failed: %s", url, e)
            return {"html": "", "blocked": False, "error": str(e)}

    # ------------------------------------------------------------------
    # Convenience wrappers
    # ------------------------------------------------------------------

    def fetch_list_html(self, page_num: int, city: str = "上海",
                         keyword: str = "") -> dict:
        params = {"page": page_num, "city": city}
        if keyword:
            params["keyword"] = keyword
        url = f"{LIST_URL_BASE}?{urlencode(params)}"
        return self.fetch_html(url)

    def fetch_detail_html(self, url: str) -> dict:
        return self.fetch_html(url)
