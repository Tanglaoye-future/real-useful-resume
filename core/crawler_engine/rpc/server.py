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


def load_liepin_cookies():
    """加载猎聘 Cookie"""
    cookie_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cookies", "liepin_cookies.json")
    if not os.path.exists(cookie_path):
        return []
    
    try:
        with open(cookie_path, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        return cookies
    except Exception as e:
        logger.error(f"Failed to load Liepin cookies: {e}")
        return []

class PlaywrightContext:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.pages: Dict[str, Any] = {}
        self.detail_pages: Dict[str, Any] = {}  # dedicated pages for detail fetching
        self._detail_lock: asyncio.Lock = None   # serializes browser navigations; init in start()
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
        logger.info("Initializing Liepin RPC page...")
        page = await self.context.new_page()
        
        # 加载保存的 Cookie
        liepin_cookies = load_liepin_cookies()
        if liepin_cookies:
            logger.info(f"Loading {len(liepin_cookies)} Liepin cookies...")
            await self.context.add_cookies(liepin_cookies)
        else:
            logger.warning("No Liepin cookies found. Please run liepin_login.py first.")
        
        # 注入猎聘页面解析函数 - 使用页面导航和DOM解析
        init_js = """
            window.rpc_liepin_search_jobs = async function(payload) {
                const keyword = payload.keyword || '实习';
                const pageNum = parseInt(payload.pageNum || 1);
                const city = payload.city || '020';
                const pageSize = parseInt(payload.pageSize || 20);
                
                // 构建搜索URL
                const url = `https://www.liepin.com/zhaopin/?key=${encodeURIComponent(keyword)}&dqs=${city}&curPage=${pageNum - 1}`;
                
                try {
                    // 导航到搜索页面
                    window.location.href = url;
                    
                    // 等待页面加载完成
                    await new Promise(resolve => setTimeout(resolve, 3000));
                    
                    // 等待职位列表加载
                    let retries = 0;
                    let jobCards = [];
                    
                    while (retries < 10 && jobCards.length === 0) {
                        await new Promise(resolve => setTimeout(resolve, 1000));
                        
                        // 尝试多种选择器
                        const selectors = [
                            '.job-card-pc-container',
                            '.sojob-item-main',
                            '.job-list-item',
                            '[data-selector="job-card"]',
                            '.job-card',
                            'li[data-jobid]'
                        ];
                        
                        for (const selector of selectors) {
                            jobCards = document.querySelectorAll(selector);
                            if (jobCards.length > 0) {
                                break;
                            }
                        }
                        
                        retries++;
                    }
                    
                    if (jobCards.length === 0) {
                        // 检查是否被拦截
                        const title = document.title || '';
                        const currentUrl = window.location.href;
                        
                        if (title.includes('验证') || title.includes('安全') || currentUrl.includes('captcha')) {
                            return {
                                blocked: true,
                                block_type: 'captcha',
                                message: '需要验证码',
                                title: title,
                                url: currentUrl
                            };
                        }
                        
                        // 尝试使用JavaScript提取数据
                        const jobs = await window._extractJobsFromPage();
                        if (jobs && jobs.length > 0) {
                            return {
                                status: 'success',
                                result: {
                                    data: {
                                        jobCardList: jobs
                                    }
                                },
                                total_count: jobs.length,
                                method: 'js_extraction'
                            };
                        }
                        
                        return {
                            status: 'success',
                            result: {
                                data: {
                                    jobCardList: []
                                }
                            },
                            total_count: 0,
                            message: 'No job cards found'
                        };
                    }
                    
                    // 解析职位卡片
                    const jobs = [];
                    jobCards.forEach((card, index) => {
                        try {
                            const job = {};
                            
                            // 标题
                            const titleElem = card.querySelector('.job-title, .title, h3, a, .job-name');
                            job.title = titleElem ? titleElem.textContent.trim() : '';
                            
                            // 链接
                            const linkElem = card.querySelector('a[href*="job"]') || card.querySelector('a');
                            job.href = linkElem ? linkElem.href : '';
                            if (job.href && job.href.includes('/job/')) {
                                job.job_id = job.href.match(/\/job\/(\d+)/)?.[1] || '';
                            }
                            
                            // 公司
                            const compElem = card.querySelector('.company-name, .comp-name, [class*="company"]');
                            job.company = compElem ? compElem.textContent.trim() : '';
                            
                            // 薪资
                            const salaryElem = card.querySelector('.salary, [class*="salary"]');
                            job.salary = salaryElem ? salaryElem.textContent.trim() : '';
                            
                            // 地点
                            const locElem = card.querySelector('.job-location, .location, [class*="location"]');
                            job.location = locElem ? locElem.textContent.trim() : '上海';
                            
                            // 经验要求
                            const expElem = card.querySelector('.job-exp, .exp, [class*="exp"]');
                            job.experience = expElem ? expElem.textContent.trim() : '';
                            
                            // 学历
                            const eduElem = card.querySelector('.job-edu, .edu, [class*="edu"]');
                            job.education = eduElem ? eduElem.textContent.trim() : '';
                            
                            // 标签
                            const tagElems = card.querySelectorAll('.job-tag, .tag, [class*="tag"]');
                            job.tags = Array.from(tagElems).map(t => t.textContent.trim()).filter(t => t);
                            
                            if (job.title) {
                                jobs.push(job);
                            }
                        } catch (e) {
                            console.error('Error parsing job card:', e);
                        }
                    });
                    
                    return {
                        status: 'success',
                        result: {
                            data: {
                                jobCardList: jobs
                            }
                        },
                        total_count: jobs.length,
                        method: 'dom_parsing'
                    };
                    
                } catch (err) {
                    return {
                        status: 'error',
                        error: String(err),
                        error_type: 'navigation_failed'
                    };
                }
            };
            
            // 备用：从页面提取数据的函数
            window._extractJobsFromPage = async function() {
                const jobs = [];
                
                // 尝试从页面脚本中提取数据
                const scripts = document.querySelectorAll('script');
                for (const script of scripts) {
                    const text = script.textContent;
                    if (text.includes('jobCardList') || text.includes('jobList')) {
                        try {
                            const match = text.match(/jobCardList\s*:\s*(\[.*?\])/);
                            if (match) {
                                return JSON.parse(match[1]);
                            }
                        } catch (e) {
                            // 忽略解析错误
                        }
                    }
                }
                
                return jobs;
            };
        """
        await page.add_init_script(init_js)
        logger.info("Navigating to Liepin homepage...")
        await page.goto("https://www.liepin.com", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        available = await page.evaluate("() => typeof window.rpc_liepin_search_jobs === 'function'")
        if not available:
            raise RuntimeError("window.rpc_liepin_search_jobs injection failed")
        self.pages["liepin"] = page
        logger.info("Liepin RPC page initialized")

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
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(2)
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
            
        elif platform == "liepin" and action == "search_jobs":
            keyword = payload.get("keyword", "实习")
            pageNum = payload.get("pageNum", 1)
            city = payload.get("city", "020")
            pageSize = payload.get("pageSize", 20)
            
            # 构建搜索URL
            url = f"https://www.liepin.com/zhaopin/?key={keyword}&dqs={city}&curPage={pageNum - 1}"
            
            # 获取猎聘页面
            page = pw_ctx.pages.get("liepin")
            if not page:
                raise HTTPException(status_code=404, detail="Liepin page not found")
            
            try:
                # 导航到搜索页面
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(3)  # 等待页面加载
                
                # 等待职位列表加载
                retries = 0
                job_cards = []
                
                while retries < 10 and len(job_cards) == 0:
                    await asyncio.sleep(1)
                    
                    # 尝试多种选择器
                    selectors = [
                        '.job-card-pc-container',
                        '.sojob-item-main',
                        '.job-list-item',
                        '[data-selector="job-card"]',
                        '.job-card',
                        'li[data-jobid]'
                    ]
                    
                    for selector in selectors:
                        try:
                            job_cards = await page.query_selector_all(selector)
                            if len(job_cards) > 0:
                                break
                        except:
                            continue
                    
                    retries += 1
                
                if len(job_cards) == 0:
                    # 检查是否被拦截
                    title = await page.title()
                    current_url = page.url
                    
                    if "验证" in title or "安全" in title or "captcha" in current_url.lower():
                        return JSONResponse(content={
                            "status": "success",
                            "result": {
                                "blocked": True,
                                "block_type": "captcha",
                                "message": "需要验证码",
                                "title": title,
                                "url": current_url
                            }
                        })
                    
                    # 尝试使用JavaScript提取数据
                    jobs = await page.evaluate("""() => {
                        const jobs = [];
                        
                        // 尝试从页面脚本中提取数据
                        const scripts = document.querySelectorAll('script');
                        for (const script of scripts) {
                            const text = script.textContent;
                            if (text.includes('jobCardList') || text.includes('jobList')) {
                                try {
                                    const match = text.match(/jobCardList\\s*:\\s*(\\[.*?\\])/);
                                    if (match) {
                                        return JSON.parse(match[1]);
                                    }
                                } catch (e) {
                                    // 忽略解析错误
                                }
                            }
                        }
                        
                        return jobs;
                    }""")
                    
                    if jobs and len(jobs) > 0:
                        return JSONResponse(content={
                            "status": "success",
                            "result": {
                                "data": {
                                    "jobCardList": jobs
                                },
                                "total_count": len(jobs),
                                "method": "js_extraction"
                            }
                        })
                    
                    return JSONResponse(content={
                        "status": "success",
                        "result": {
                            "data": {
                                "jobCardList": []
                            },
                            "total_count": 0,
                            "message": "No job cards found"
                        }
                    })
                
                # 解析职位卡片
                jobs = []
                for card in job_cards[:pageSize]:
                    try:
                        job = {}
                        
                        # 标题
                        title_elem = await card.query_selector('.job-title, .title, h3, a, .job-name')
                        if title_elem:
                            job['title'] = await title_elem.text_content() or ''
                            job['title'] = job['title'].strip()
                        
                        # 链接
                        link_elem = await card.query_selector('a[href*="job"]') or await card.query_selector('a')
                        if link_elem:
                            href = await link_elem.get_attribute('href') or ''
                            job['href'] = href
                            if href and '/job/' in href:
                                import re
                                match = re.search(r'/job/(\\d+)', href)
                                if match:
                                    job['job_id'] = match.group(1)
                        
                        # 公司
                        comp_elem = await card.query_selector('.company-name, .comp-name, [class*="company"]')
                        if comp_elem:
                            job['company'] = await comp_elem.text_content() or ''
                            job['company'] = job['company'].strip()
                        
                        # 薪资
                        salary_elem = await card.query_selector('.salary, [class*="salary"]')
                        if salary_elem:
                            job['salary'] = await salary_elem.text_content() or ''
                            job['salary'] = job['salary'].strip()
                        
                        # 地点
                        loc_elem = await card.query_selector('.job-location, .location, [class*="location"]')
                        if loc_elem:
                            job['location'] = await loc_elem.text_content() or '上海'
                            job['location'] = job['location'].strip()
                        
                        # 经验要求
                        exp_elem = await card.query_selector('.job-exp, .exp, [class*="exp"]')
                        if exp_elem:
                            job['experience'] = await exp_elem.text_content() or ''
                            job['experience'] = job['experience'].strip()
                        
                        # 学历
                        edu_elem = await card.query_selector('.job-edu, .edu, [class*="edu"]')
                        if edu_elem:
                            job['education'] = await edu_elem.text_content() or ''
                            job['education'] = job['education'].strip()
                        
                        # 标签
                        tag_elems = await card.query_selector_all('.job-tag, .tag, [class*="tag"]')
                        job['tags'] = []
                        for tag_elem in tag_elems:
                            tag_text = await tag_elem.text_content()
                            if tag_text:
                                job['tags'].append(tag_text.strip())
                        
                        if job.get('title'):
                            jobs.append(job)
                    except Exception as e:
                        continue
                
                return JSONResponse(content={
                    "status": "success",
                    "result": {
                        "data": {
                            "jobCardList": jobs
                        },
                        "total_count": len(jobs),
                        "method": "dom_parsing"
                    }
                })
                
            except Exception as e:
                return JSONResponse(content={
                    "status": "error",
                    "error": str(e),
                    "error_type": "navigation_failed"
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
