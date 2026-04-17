"""Async batch link accessibility checker with configurable concurrency."""
import asyncio
from typing import List, Dict


async def check_one(url: str, timeout: int) -> Dict[str, str]:
    """Check a single URL for HTTP accessibility."""
    import aiohttp
    result = {"url": url, "status": "UNKNOWN", "reason": ""}
    try:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.head(url, timeout=aiohttp.ClientTimeout(total=timeout), allow_redirects=True, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
                }) as resp:
                    if resp.status < 400:
                        result["status"] = "OK"
                        result["reason"] = f"HTTP {resp.status}"
                    elif resp.status == 404 or resp.status == 410:
                        result["status"] = "NOT_FOUND"
                        result["reason"] = f"HTTP {resp.status} Not Found"
                    else:
                        result["status"] = "ERROR"
                        result["reason"] = f"HTTP {resp.status}"
            except asyncio.TimeoutError:
                result["status"] = "TIMEOUT"
                result["reason"] = f"Timeout after {timeout}s"
            except Exception as e:
                result["status"] = "ERROR"
                result["reason"] = str(e)[:120]
    except ImportError:
        # Fallback without aiohttp: use requests synchronously
        import requests as req_lib
        try:
            r = req_lib.head(url, timeout=timeout, allow_redirects=True, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            })
            if r.status_code < 400:
                result["status"] = "OK"
                result["reason"] = f"HTTP {r.status_code}"
            else:
                result["status"] = "ERROR"
                result["reason"] = f"HTTP {r.status_code}"
        except Exception as e:
            result["status"] = "ERROR"
            result["reason"] = str(e)[:120]
    return result


async def check_links_batch(urls: List[str], max_concurrent: int = 12, timeout: int = 12) -> List[Dict]:
    """Check multiple URLs concurrently. Returns list of {url, status, reason} dicts."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _check_with_limit(u):
        async with semaphore:
            await asyncio.sleep(0.05)  # tiny stagger
            return await check_one(u, timeout)

    tasks = [_check_with_limit(u) for u in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    output = []
    for u, r in zip(urls, results):
        if isinstance(r, Exception):
            output.append({"url": u, "status": "ERROR", "reason": str(r)})
        else:
            output.append(r)
    return output
