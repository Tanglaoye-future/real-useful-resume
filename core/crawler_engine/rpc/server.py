import json
import logging
import re
import time
import asyncio
import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn
from playwright.async_api import async_playwright
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RpcServer")


COOKIES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cookies")

_PLATFORM_DOMAINS = {
    "liepin": [".liepin.com", "www.liepin.com", "liepin.com"],
    "job51":  [".51job.com", "we.51job.com", "51job.com", ".51job.com"],
}


def _cookie_path(platform: str) -> str:
    os.makedirs(COOKIES_DIR, exist_ok=True)
    return os.path.join(COOKIES_DIR, f"{platform}_cookies.json")


def load_cookies(platform: str) -> list:
    path = _cookie_path(platform)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load {platform} cookies: {e}")
        return []


def load_liepin_cookies():
    return load_cookies("liepin")


async def save_cookies(context, platform: str):
    """Extract cookies matching the platform's domains and write to disk."""
    try:
        all_cookies = await context.cookies()
        domains = _PLATFORM_DOMAINS.get(platform, [])
        filtered = [c for c in all_cookies if any(d in c.get("domain", "") for d in domains)]
        if not filtered:
            logger.warning(f"save_cookies({platform}): no matching cookies found")
            return 0
        with open(_cookie_path(platform), "w", encoding="utf-8") as f:
            json.dump(filtered, f, ensure_ascii=False, indent=2)
        logger.info(f"save_cookies({platform}): saved {len(filtered)} cookies")
        return len(filtered)
    except Exception as e:
        logger.error(f"save_cookies({platform}) failed: {e}")
        return 0

class PlaywrightContext:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.pages: Dict[str, Any] = {}
        self.detail_pages: Dict[str, Any] = {}  # dedicated pages for detail fetching
        self._detail_lock: asyncio.Lock = None        # serializes detail-page navigations; init in start()
        self._liepin_search_lock: asyncio.Lock = None # serializes liepin search navigations; init in start()
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
            # 只初始化前程无忧和猎聘
            # await self._init_lagou_page()  # 已禁用
            await self._init_job51_page()
            # await self._init_boss_page()  # 已禁用
            await self._init_liepin_page()
            self._detail_lock = asyncio.Lock()
            self._liepin_search_lock = asyncio.Lock()
            await self._init_detail_pages()
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
        # Only auto-save for 51job if we already have saved cookies — means user was previously logged in
        if os.path.exists(_cookie_path("job51")):
            await save_cookies(self.context, "job51")
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

    async def _init_liepin_page(self):
        """Initialize the Liepin search page.
        Injects a fetch+XHR interceptor init script so that search API responses
        are captured into window._liepin_search_resp on every navigation.
        After page.goto(), search_jobs reads that variable via page.evaluate()."""
        logger.info("Initializing Liepin RPC page...")
        page = await self.context.new_page()

        # Inject BEFORE any page JS runs — intercepts both fetch() and XHR.
        # Runs on every navigation of this page object.
        await page.add_init_script("""
        (function() {
            window._liepin_search_resp = null;

            // ── fetch interceptor ─────────────────────────────────────────
            var _orig_fetch = window.fetch;
            window.fetch = async function() {
                var args = Array.prototype.slice.call(arguments);
                var resp = await _orig_fetch.apply(window, args);
                var url = typeof args[0] === 'string' ? args[0]
                        : (args[0] && args[0].url ? args[0].url : '');
                if (url.indexOf('pc-search-job') !== -1 && url.indexOf('cond-init') === -1) {
                    try { window._liepin_search_resp = await resp.clone().json(); } catch(e) {}
                }
                return resp;
            };

            // ── XHR interceptor ───────────────────────────────────────────
            var _origOpen = XMLHttpRequest.prototype.open;
            var _origSend = XMLHttpRequest.prototype.send;
            XMLHttpRequest.prototype.open = function(method, url) {
                this._lp_url = url;
                return _origOpen.apply(this, arguments);
            };
            XMLHttpRequest.prototype.send = function(body) {
                var self = this;
                if (self._lp_url &&
                    self._lp_url.indexOf('pc-search-job') !== -1 &&
                    self._lp_url.indexOf('cond-init') === -1) {
                    self.addEventListener('load', function() {
                        try { window._liepin_search_resp = JSON.parse(self.responseText); } catch(e) {}
                    });
                }
                return _origSend.apply(this, arguments);
            };
        })();
        """)

        liepin_cookies = load_liepin_cookies()
        if liepin_cookies:
            logger.info(f"Loading {len(liepin_cookies)} Liepin cookies...")
            await self.context.add_cookies(liepin_cookies)
        else:
            logger.warning("No Liepin cookies found. Searches may be rate-limited.")

        logger.info("Navigating to Liepin homepage to warm session...")
        await page.goto("https://www.liepin.com", wait_until="domcontentloaded", timeout=20000)
        await asyncio.sleep(2)

        self.pages["liepin"] = page
        logger.info("Liepin RPC page initialized (fetch+XHR init-script mode)")

    async def _init_detail_pages(self):
        """Create dedicated pages for fetching job detail pages.
        These pages share the same authenticated browser context (cookies already set),
        so they can access detail pages without triggering captcha."""
        logger.info("Initializing detail fetch pages...")
        for platform_key, seed_url in [
            ("job51", "https://we.51job.com"),
            ("liepin", "https://www.liepin.com"),
        ]:
            try:
                page = await self.context.new_page()
                await page.goto(seed_url, wait_until="domcontentloaded", timeout=20000)
                await asyncio.sleep(1)
                self.detail_pages[platform_key] = page
                logger.info(f"Detail page initialized: {platform_key}")
            except Exception as e:
                logger.warning(f"Detail page init failed for {platform_key}: {e}")

    async def fetch_detail_html(self, platform: str, url: str) -> dict:
        """Navigate a detail page to the given URL and return its HTML.
        Uses asyncio.Lock to serialize browser navigations — the lock prevents
        concurrent Playwright page.goto() calls on the same page object."""
        async with self._detail_lock:
            page = self.detail_pages.get(platform)
            if page is None:
                # Lazy-create if init failed
                try:
                    page = await self.context.new_page()
                    self.detail_pages[platform] = page
                except Exception as e:
                    return {"html": "", "blocked": False, "error": f"page_create_failed: {e}"}
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(1)
                html = await page.content()
                title = await page.title()
                blocked = bool(re.search(r"验证码|captcha|traceid|security.check|人机验证|安全中心", title, re.I))
                if not blocked:
                    # Also check page text for captcha signals
                    snippet = html[:3000].lower()
                    blocked = bool(re.search(r"captcha|traceid|_waf_is_mobile|请完成验证|访问受限", snippet))
                return {"html": html if not blocked else "", "blocked": blocked, "title": title}
            except Exception as e:
                logger.error(f"fetch_detail_html {platform} {url}: {e}")
                return {"html": "", "blocked": False, "error": str(e)}

    async def stop(self):
        for page in self.detail_pages.values():
            try:
                await page.close()
            except Exception:
                pass
        self.detail_pages.clear()
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

@app.post("/save_cookies/{platform}")
async def save_cookies_endpoint(platform: str):
    """Call this once after manually logging in to persist the session cookies to disk.
    Subsequent RPC restarts will load them automatically."""
    if not pw_ctx.ready:
        raise HTTPException(status_code=503, detail="RPC not ready")
    n = await save_cookies(pw_ctx.context, platform)
    return JSONResponse(content={"saved": n, "platform": platform, "path": _cookie_path(platform)})


@app.post("/save_cookies")
async def save_all_cookies_endpoint():
    """Save cookies for all initialized platforms at once."""
    if not pw_ctx.ready:
        raise HTTPException(status_code=503, detail="RPC not ready")
    results = {}
    for plat in ["job51", "liepin"]:
        results[plat] = await save_cookies(pw_ctx.context, plat)
    return JSONResponse(content={"saved": results})


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
            # Auto-recover if page was closed
            page = pw_ctx.pages.get("job51")
            if not page or page.is_closed():
                logger.warning("[51job] page is closed — recreating...")
                await pw_ctx._init_job51_page()
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
            
        elif platform == "liepin" and action == "search_jobs":
            # ── page.route() interception approach ────────────────────────────
            # page.route() is more reliable than page.on("response"):
            #   • runs an async handler that MUST complete before the page proceeds
            #   • no event-loop scheduling race (async handlers guaranteed to run)
            #   • route.fetch() returns a fully-materialized Response with body
            # We intercept all requests to Liepin's search API, parse the JSON body,
            # then forward the request unchanged via route.fulfill(response=...).
            keyword = payload.get("keyword", "实习")
            pageNum = int(payload.get("pageNum", 1))
            city = payload.get("city", "020")
            pageSize = int(payload.get("pageSize", 20))

            page = pw_ctx.pages.get("liepin")
            # Auto-recover if the page was closed (e.g. user closed the tab manually)
            if not page or page.is_closed():
                logger.warning("[Liepin] page is closed — recreating...")
                await pw_ctx._init_liepin_page()
                page = pw_ctx.pages.get("liepin")
            if not page:
                raise HTTPException(status_code=404, detail="Liepin page not found")

            search_url = (
                f"https://www.liepin.com/zhaopin/"
                f"?key={keyword}&dqs={city}&curPage={pageNum - 1}"
            )

            # Serialize liepin searches
            async with pw_ctx._liepin_search_lock:
                captured: list = []

                def _extract_job_list(data):
                    """Try every known nesting path for Liepin job lists."""
                    if not isinstance(data, dict):
                        return []
                    d1 = data.get("data") or {}
                    d2 = d1.get("data") or {}
                    d_result = d1.get("result") or {}
                    d_search = d1.get("searchResult") or d1.get("search") or {}
                    candidates = [
                        d1.get("jobCardList"),
                        d1.get("jobList"),
                        d2.get("jobCardList"),
                        d2.get("jobList"),
                        d_result.get("jobCardList"),
                        d_result.get("jobList"),
                        d_search.get("jobCardList"),
                        d_search.get("jobList"),
                        data.get("jobCardList"),
                        data.get("jobList"),
                    ]
                    for c in candidates:
                        if c:
                            return c
                    return []

                # ── Strategy 1: JS init-script intercept ─────────────────────
                # The init script patches window.fetch + XHR before React loads,
                # storing the pc-search-job response in window._liepin_search_resp.
                try:
                    await page.evaluate("() => { window._liepin_search_resp = null; }")
                    await page.goto(search_url, wait_until="networkidle", timeout=35000)
                    await asyncio.sleep(1)

                    landed_url = page.url
                    landed_title = await page.title()
                    logger.info(f"[Liepin] landed url={landed_url[:80]} title={landed_title!r}")

                    data = await page.evaluate("() => window._liepin_search_resp")
                    if isinstance(data, dict):
                        d1 = data.get("data") or {}
                        logger.info(
                            f"[Liepin JS-intercept] top={list(data.keys())[:8]} "
                            f"data.keys={list(d1.keys())[:12] if isinstance(d1, dict) else type(d1).__name__} "
                            f"flag={data.get('flag')!r}"
                        )
                        if isinstance(d1, dict):
                            for k, v in d1.items():
                                if isinstance(v, (list, dict)):
                                    logger.info(f"[Liepin JS-intercept] data[{k!r}] type={type(v).__name__} "
                                                f"len={len(v)} "
                                                f"sample_keys={list(v.keys())[:6] if isinstance(v, dict) else (list(v[0].keys())[:6] if v and isinstance(v[0], dict) else '?')}")
                    else:
                        logger.info(f"[Liepin JS-intercept] _liepin_search_resp={data!r}")
                    jobs = _extract_job_list(data)
                    if jobs:
                        captured.extend(jobs)
                        logger.info(f"[Liepin JS-intercept] captured {len(jobs)} jobs")
                except Exception as e:
                    logger.warning(f"[Liepin JS-intercept] error: {e}")

                # ── Strategy 2: capture real request body via expect_request,
                #    then replay via page.evaluate(fetch) ────────────────────
                if not captured:
                    logger.info("[Liepin] trying strategy 2: expect_request + evaluate-replay")
                    try:
                        await page.evaluate("() => { window._liepin_search_resp = null; }")
                        async with page.expect_request(
                            lambda r: "pc-search-job" in r.url and "cond-init" not in r.url,
                            timeout=35000,
                        ) as req_info:
                            await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)

                        xhreq = await req_info.value
                        req_body = xhreq.post_data or "{}"
                        req_url  = xhreq.url
                        logger.info(f"[Liepin req-capture] url={req_url[:80]} body={req_body[:300]}")

                        # replay the identical request from within the page context
                        result = await page.evaluate("""
                        async (args) => {
                            try {
                                const resp = await fetch(args.url, {
                                    method: 'POST',
                                    credentials: 'include',
                                    headers: {'Content-Type': 'application/json',
                                              'Accept': 'application/json'},
                                    body: args.body
                                });
                                if (!resp.ok) return {_err: 'http_' + resp.status};
                                return await resp.json();
                            } catch(e) { return {_err: String(e)}; }
                        }
                        """, {"url": req_url, "body": req_body})

                        logger.info(f"[Liepin eval-replay] result keys={list(result.keys())[:8] if isinstance(result, dict) else result}")
                        jobs = _extract_job_list(result)
                        if jobs:
                            captured.extend(jobs)
                            logger.info(f"[Liepin eval-replay] captured {len(jobs)} jobs")
                    except Exception as e:
                        logger.warning(f"[Liepin strategy-2] error: {e}")

                # ── Captcha / block detection ──────────────────────────────────
                title = await page.title()
                current_url = page.url
                if re.search(r"验证|安全中心|captcha", title, re.I) or "captcha" in current_url.lower():
                    logger.warning(f"[Liepin] blocked: title={title!r}")
                    return JSONResponse(content={
                        "status": "success",
                        "result": {
                            "blocked": True,
                            "message": "需要验证码",
                            "title": title,
                            "url": current_url,
                        }
                    })

                # ── SSR fallback: try window.__NEXT_DATA__ if route captured nothing ──
                if not captured:
                    logger.warning(
                        f"[Liepin] route captured 0 jobs — trying SSR fallback "
                        f"keyword={keyword!r} page={pageNum} title={title!r}"
                    )
                    try:
                        next_data_str = await page.evaluate(
                            "() => { try { return JSON.stringify(window.__NEXT_DATA__ || null) } catch(e) { return null } }"
                        )
                        if next_data_str:
                            nd = json.loads(next_data_str) or {}
                            props = (nd.get("props") or {}).get("pageProps") or {}
                            logger.info(
                                f"[Liepin SSR] __NEXT_DATA__ pageProps keys={list(props.keys())[:10]}"
                            )
                            ssr_jobs = (
                                props.get("jobCardList")
                                or props.get("jobList")
                                or (props.get("data") or {}).get("jobCardList")
                                or (props.get("data") or {}).get("jobList")
                                or (props.get("searchResult") or {}).get("jobCardList")
                                or (props.get("result") or {}).get("jobCardList")
                                or []
                            )
                            if ssr_jobs:
                                captured.extend(ssr_jobs)
                                logger.info(
                                    f"[Liepin SSR] captured {len(ssr_jobs)} jobs from __NEXT_DATA__"
                                )
                            else:
                                logger.warning(
                                    f"[Liepin SSR] __NEXT_DATA__ found but no jobCardList; "
                                    f"pageProps keys={list(props.keys())[:10]}"
                                )
                        else:
                            logger.warning("[Liepin SSR] window.__NEXT_DATA__ is null/undefined")
                    except Exception as e:
                        logger.warning(f"[Liepin SSR] extraction failed: {e}")

                return JSONResponse(content={
                    "status": "success",
                    "result": {
                        "data": {"jobCardList": captured[:pageSize]},
                        "total_count": len(captured),
                        "method": "route_intercept" if captured else "empty",
                    }
                })

        elif platform == "liepin" and action == "scan_page_state":
            # Diagnostic: navigate to a search page and scan all window globals + script tags
            # to find where Liepin embeds job data (SSR state variable discovery).
            keyword = payload.get("keyword", "实习")
            pageNum = int(payload.get("pageNum", 1))
            city = payload.get("city", "020")
            search_url = (
                f"https://www.liepin.com/zhaopin/"
                f"?key={keyword}&dqs={city}&curPage={pageNum - 1}"
            )
            page = pw_ctx.pages.get("liepin")
            if not page or page.is_closed():
                await pw_ctx._init_liepin_page()
                page = pw_ctx.pages.get("liepin")
            async with pw_ctx._liepin_search_lock:
                # Capture ALL network request URLs during page load
                request_urls: list = []
                json_responses: list = []

                def _on_req(req):
                    request_urls.append(f"{req.method} {req.resource_type} {req.url[:120]}")

                async def _on_resp(resp):
                    try:
                        ct = resp.headers.get("content-type", "")
                        if "liepin.com" in resp.url and ("json" in ct or "javascript" in ct):
                            try:
                                body = await resp.text()
                                if "jobCardList" in body or "compName" in body:
                                    json_responses.append({"url": resp.url[:120], "body_preview": body[:400]})
                            except Exception:
                                pass
                    except Exception:
                        pass

                page.on("request", _on_req)
                page.on("response", _on_resp)
                try:
                    await page.goto(search_url, wait_until="networkidle", timeout=30000)
                    await asyncio.sleep(5)
                finally:
                    page.remove_listener("request", _on_req)
                    page.remove_listener("response", _on_resp)

                # Also get HTML snippet to look for embedded JSON
                html = await page.content()
                html_job_snippet = ""
                import re as _re
                m = _re.search(r'(jobCardList.{0,800})', html)
                if m:
                    html_job_snippet = m.group(1)[:500]

                scan_result = await page.evaluate("""() => {
                    const candidates = [
                        '__INITIAL_STATE__','__STATE__','__APP_STATE__','__SS_PROPS__',
                        '__PRELOADED_STATE__','_data','pageState','__DATA__',
                        'window_data','__NUXT__','serverData','__REDUX_STATE__',
                        '__store__','store'
                    ];
                    for (const name of candidates) {
                        try {
                            const val = window[name];
                            if (val && typeof val === 'object') {
                                const s = JSON.stringify(val);
                                if (s && s.length > 100) {
                                    return {source: 'window.' + name, preview: s.slice(0, 600)};
                                }
                            }
                        } catch(e) {}
                    }
                    // Scan all window props for job-related data
                    for (const key of Object.keys(window)) {
                        try {
                            const val = window[key];
                            if (val && typeof val === 'object' && key !== 'document' && key !== 'window') {
                                const s = JSON.stringify(val);
                                if (s && (s.includes('jobCardList') || s.includes('compName') || s.includes('salary') || s.includes('jobName'))) {
                                    return {source: 'window.' + key, preview: s.slice(0, 600)};
                                }
                            }
                        } catch(e) {}
                    }
                    // Check script tags
                    const scripts = document.querySelectorAll('script');
                    for (const s of scripts) {
                        const text = s.textContent || '';
                        if (text.length > 200 && (text.includes('jobCardList') || text.includes('compName'))) {
                            return {source: 'script_tag', preview: text.slice(0, 600)};
                        }
                    }
                    // Return window key list for manual inspection
                    const allKeys = Object.keys(window).filter(k => !['document','window','location','history','navigator','screen','performance','console'].includes(k));
                    return {source: 'not_found', title: document.title, window_keys: allKeys.slice(0, 40)};
                }""")
                # Log network summary to server log
                logger.info(f"[Scan] {len(request_urls)} requests, {len(json_responses)} json_with_jobs")
                liepin_reqs = [u for u in request_urls if "liepin.com" in u][:30]
                return JSONResponse(content={
                    "status": "success",
                    "result": {
                        **scan_result,
                        "network_liepin_requests": liepin_reqs,
                        "json_with_jobs": json_responses[:3],
                        "html_job_snippet": html_job_snippet,
                    }
                })

        elif action == "fetch_detail":
            # Fetch a single job detail page using the authenticated browser context.
            # This avoids captcha because the browser already has valid session cookies.
            url = payload.get("url", "")
            if not url:
                raise HTTPException(status_code=400, detail="url required for fetch_detail")
            result = await pw_ctx.fetch_detail_html(platform, url)
            return JSONResponse(content={"status": "success", "result": result})

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported action {action} for {platform}")
            
    except Exception as e:
        logger.error(f"RPC execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("Starting RPC Server on port 5600...")
    # 注意：不再使用 reload=True，因为它会产生额外的进程并可能导致 Playwright 上下文错乱
    uvicorn.run(app, host="0.0.0.0", port=5600)
