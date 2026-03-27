import json
import logging
import time
import asyncio
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn
from playwright.async_api import async_playwright
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RpcServer")

class PlaywrightContext:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.pages: Dict[str, Any] = {}
        self.ready = False
        self.startup_error = ""

    async def start(self):
        logger.info("Starting RPC Playwright context in async mode...")
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=False,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="zh-CN"
            )
            await self._init_lagou_page()
            await self._init_job51_page()
            await self._init_boss_page()
            self.ready = True
            self.startup_error = ""
            logger.info("RPC Playwright context is ready")
        except Exception as e:
            self.ready = False
            self.startup_error = str(e)
            logger.error(f"RPC startup failed: {e}")
            raise

    async def _init_lagou_page(self):
        logger.info("Initializing Lagou RPC page...")
        page = await self.context.new_page()
        init_js = """
            window.rpc_get_forge_code = async function(seed) {
                const res = await fetch('/jobs/positionAjax.json?px=default&city=%E4%B8%8A%E6%B5%B7&needAddtionalResult=false', {
                    method: 'POST',
                    credentials: 'include',
                    mode: 'same-origin',
                    redirect: 'follow',
                    cache: 'no-store',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Accept': 'application/json, text/javascript, */*; q=0.01'
                    },
                    body: seed
                });
                const text = await res.text();
                if (text.includes('滑动验证页面') || text.includes('_waf_is_mobile') || text.includes('验证页面')) {
                    return { blocked: true, block_type: 'slider_captcha', raw: text.slice(0, 1200) };
                }
                let parsed;
                try {
                    parsed = JSON.parse(text);
                } catch (err) {
                    parsed = { parse_error: String(err), raw: text };
                }
                if (!res.ok) {
                    return { http_status: res.status, body: parsed };
                }
                return parsed;
            };
        """
        await page.add_init_script(init_js)
        logger.info("Navigating to Lagou...")
        await page.goto("https://www.lagou.com/jobs/list_%E5%AE%9E%E4%B9%A0?city=%E4%B8%8A%E6%B5%B7", wait_until="domcontentloaded")
        available = await page.evaluate("() => typeof window.rpc_get_forge_code === 'function'")
        if not available:
            raise RuntimeError("window.rpc_get_forge_code injection failed")
        self.pages["lagou"] = page
        logger.info("Lagou RPC page initialized")

    async def _init_job51_page(self):
        logger.info("Initializing 51job RPC page...")
        page = await self.context.new_page()
        init_js = """
            window.rpc_job51_search_jobs = async function(payload) {
                const keyword = payload.keyword || '实习';
                const pageNum = String(payload.pageNum || 1);
                const jobArea = payload.jobArea || '020000';
                const pageSize = String(payload.pageSize || 20);
                const requestId = payload.requestId || '';
                const apiParams = new URLSearchParams({
                    api_key: '51job',
                    timestamp: String(Math.floor(Date.now() / 1000)),
                    keyword: keyword,
                    searchType: '2',
                    function: '',
                    industry: '',
                    jobArea: jobArea,
                    jobArea2: '',
                    landmark: '',
                    metro: '',
                    salary: '',
                    workYear: '',
                    degree: '',
                    companyType: '',
                    companySize: '',
                    jobType: '',
                    issueDate: '',
                    sortType: '0',
                    pageNum: pageNum,
                    requestId: requestId,
                    pageSize: pageSize,
                    source: '1',
                    accountId: '',
                    pageCode: 'sou|sou|soulb',
                    scene: '7'
                });
                const res = await fetch('/api/job/search-pc?' + apiParams.toString(), {
                    method: 'GET',
                    credentials: 'include',
                    mode: 'same-origin',
                    redirect: 'follow',
                    cache: 'no-store',
                    headers: {
                        'Accept': 'application/json, text/plain, */*'
                    }
                });
                const text = await res.text();
                if (text.includes('滑动验证页面') || text.includes('_waf_is_mobile') || text.includes('验证页面')) {
                    return { blocked: true, block_type: 'slider_captcha', raw: text.slice(0, 1200) };
                }
                let parsed;
                try {
                    parsed = JSON.parse(text);
                } catch (err) {
                    parsed = { parse_error: String(err), raw: text };
                }
                if (!res.ok) {
                    return { http_status: res.status, body: parsed };
                }
                return parsed;
            };
        """
        await page.add_init_script(init_js)
        await page.goto("https://we.51job.com/pc/search?jobArea=020000&keyword=%E5%AE%9E%E4%B9%A0&pageCode=1", wait_until="domcontentloaded")
        available = await page.evaluate("() => typeof window.rpc_job51_search_jobs === 'function'")
        if not available:
            raise RuntimeError("window.rpc_job51_search_jobs injection failed")
        self.pages["job51"] = page
        logger.info("51job RPC page initialized")

    async def _init_boss_page(self):
        logger.info("Initializing Boss RPC page...")
        page = await self.context.new_page()
        init_js = """
            window.rpc_boss_get_stoken = async function(payload) {
                const seed = payload.seed || '';
                const ts = payload.ts || Date.now();
                
                // Boss直聘的 stoken 生成逻辑
                // 这里使用简化版，实际应该调用 Boss 的加密函数
                try {
                    // 尝试使用页面上的加密函数
                    if (typeof window.zp !== 'undefined' && window.zp.encrypt) {
                        const result = await window.zp.encrypt(seed, ts);
                        return { status: 'success', result: result };
                    }
                    
                    // 备用方案：返回简化版 stoken
                    const fallbackToken = btoa(seed + '_' + ts).replace(/=/g, '');
                    return { status: 'success', result: fallbackToken };
                } catch (err) {
                    return { status: 'error', error: String(err) };
                }
            };
        """
        await page.add_init_script(init_js)
        logger.info("Navigating to Boss...")
        await page.goto("https://www.zhipin.com/shanghai/", wait_until="domcontentloaded")
        available = await page.evaluate("() => typeof window.rpc_boss_get_stoken === 'function'")
        if not available:
            raise RuntimeError("window.rpc_boss_get_stoken injection failed")
        self.pages["boss"] = page
        logger.info("Boss RPC page initialized")

    async def stop(self):
        for page in self.pages.values():
            await page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.ready = False

    async def evaluate_async(self, platform: str, js_code: str):
        page = self.pages.get(platform)
        if not page:
            raise Exception(f"Page for {platform} not found")
        return await page.evaluate(js_code)

    async def evaluate_with_arg(self, platform: str, expression: str, arg: Any):
        page = self.pages.get(platform)
        if not page:
            raise Exception(f"Page for {platform} not found")
        return await page.evaluate(expression, arg)

    async def set_lagou_cookies(self, cookie_str: str):
        if not cookie_str:
            return
        cookies = []
        for part in cookie_str.split(";"):
            kv = part.strip()
            if not kv or "=" not in kv:
                continue
            name, value = kv.split("=", 1)
            name = name.strip()
            if not name:
                continue
            cookies.append({
                "name": name,
                "value": value.strip(),
                "domain": ".lagou.com",
                "path": "/",
                "secure": True
            })
        if cookies:
            await self.context.add_cookies(cookies)

    async def set_job51_cookies(self, cookie_str: str):
        if not cookie_str:
            return
        cookies = []
        for part in cookie_str.split(";"):
            kv = part.strip()
            if not kv or "=" not in kv:
                continue
            name, value = kv.split("=", 1)
            name = name.strip()
            if not name:
                continue
            cookies.append({
                "name": name,
                "value": value.strip(),
                "domain": ".51job.com",
                "path": "/",
                "secure": True
            })
        if cookies:
            await self.context.add_cookies(cookies)

pw_ctx = PlaywrightContext()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await pw_ctx.start()
    yield
    # Shutdown
    await pw_ctx.stop()

app = FastAPI(title="Crawler RPC Engine", lifespan=lifespan)

@app.get("/health")
async def health():
    return JSONResponse(content={
        "status": "ok" if pw_ctx.ready else "error",
        "ready": pw_ctx.ready,
        "initialized_platforms": list(pw_ctx.pages.keys()),
        "startup_error": pw_ctx.startup_error
    })

@app.post("/invoke/{platform}/{action}")
async def invoke_rpc(platform: str, action: str, request: Request):
    if not pw_ctx.ready:
        raise HTTPException(status_code=503, detail=f"RPC context not ready: {pw_ctx.startup_error or 'starting'}")
    if platform not in pw_ctx.pages:
        raise HTTPException(status_code=404, detail=f"Platform {platform} not initialized in RPC server")
        
    try:
        payload = await request.json()
    except:
        payload = {}

    try:
        if platform == "boss" and action == "get_stoken":
            seed = payload.get("seed", "")
            ts = payload.get("ts", "")
            result = await pw_ctx.evaluate_async(platform, f"window.rpc_get_stoken('{seed}', '{ts}')")
            return JSONResponse(content={"status": "success", "result": result})
            
        elif platform == "lagou" and action == "get_forge_code":
            seed = payload.get("seed", "")
            cookie_str = payload.get("cookie", "")
            await pw_ctx.set_lagou_cookies(cookie_str)
            result = await pw_ctx.evaluate_with_arg(platform, "(seed) => window.rpc_get_forge_code(seed)", seed)
            return JSONResponse(content={"status": "success", "result": result})

        elif platform == "lagou" and action == "wait_for_unblock":
            cookie_str = payload.get("cookie", "")
            await pw_ctx.set_lagou_cookies(cookie_str)
            seed = payload.get("seed", "first=true&pn=1&kd=实习")
            timeout_seconds = int(payload.get("timeout_seconds", 300))
            poll_interval_seconds = float(payload.get("poll_interval_seconds", 2.0))
            start_ts = time.time()
            checks = 0
            last_result = None
            while True:
                checks += 1
                probe_result = await pw_ctx.evaluate_with_arg(platform, "(seed) => window.rpc_get_forge_code(seed)", seed)
                last_result = probe_result
                blocked = isinstance(probe_result, dict) and probe_result.get("blocked")
                if not blocked:
                    return JSONResponse(content={
                        "status": "success",
                        "result": {
                            "unblocked": True,
                            "waited_seconds": round(time.time() - start_ts, 2),
                            "checks": checks,
                            "probe_result": probe_result
                        }
                    })
                if time.time() - start_ts >= timeout_seconds:
                    return JSONResponse(content={
                        "status": "success",
                        "result": {
                            "unblocked": False,
                            "waited_seconds": round(time.time() - start_ts, 2),
                            "checks": checks,
                            "last_result": last_result
                        }
                    })
                await asyncio.sleep(poll_interval_seconds)
            
        elif platform == "job51" and action == "search_jobs":
            cookie_str = payload.get("cookie", "")
            await pw_ctx.set_job51_cookies(cookie_str)
            request_payload = {
                "keyword": payload.get("keyword", "实习"),
                "pageNum": payload.get("pageNum", 1),
                "jobArea": payload.get("jobArea", "020000"),
                "pageSize": payload.get("pageSize", 20),
                "requestId": payload.get("requestId", "")
            }
            result = await pw_ctx.evaluate_with_arg(platform, "(payload) => window.rpc_job51_search_jobs(payload)", request_payload)
            return JSONResponse(content={"status": "success", "result": result})
            
        elif platform == "zhaopin" and action == "get_x_zp_token":
            result = await pw_ctx.evaluate_async(platform, "window.rpc_get_x_zp_token()")
            return JSONResponse(content={"status": "success", "result": result})
            
        elif platform == "shixiseng" and action == "decrypt_font":
            unicode_str = payload.get("unicode_str", "")
            result = await pw_ctx.evaluate_async(platform, f"window.rpc_decrypt_font('{unicode_str}')")
            return JSONResponse(content={"status": "success", "result": result})
            
        elif platform == "liepin" and action == "get_fscp_headers":
            data_str = json.dumps(payload.get("data", {}))
            result = await pw_ctx.evaluate_async(platform, f"window.rpc_get_fscp_headers({data_str})")
            return JSONResponse(content={"status": "success", "result": json.loads(result)})

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported action {action} for {platform}")
            
    except Exception as e:
        logger.error(f"RPC execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("Starting RPC Server on port 5600...")
    # 注意：不再使用 reload=True，因为它会产生额外的进程并可能导致 Playwright 上下文错乱
    uvicorn.run(app, host="0.0.0.0", port=5600)
