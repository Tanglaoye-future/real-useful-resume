import os
import random
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
from fake_useragent import UserAgent
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright
from playwright_stealth import Stealth


# 列表页入口（后续通过 ?current= 页码 控制最多抓取5页）
START_URL = "https://jobs.bytedance.com/campus/position"
MAX_PAGES = 5
MIN_DELAY_S = 1.5
MAX_DELAY_S = 3.5
MAX_JOBS = 120
LIST_LIMIT = 20

NOWCODER_ENTERPRISE_URL = "https://www.nowcoder.com/enterprise/665"
NOWCODER_MAX_PAGES = 1
NOWCODER_LIST_LIMIT = 20

CITY_KEYWORD = "上海"
ROLE_KEYWORDS = [
    "软件",
    "开发",
    "全栈",
    "研发",
    "后端",
    "前端",
    "算法",
    "客户端",
    "测试",
    "工程",
    "SRE",
    "数据",
    "产品",
    "产品经理",
    "AI产品",
    "PM",
]
RECRUIT_TYPE_KEYWORDS = ["暑期", "实习", "提前批", "秋招", "校招"]

STEALTH = Stealth()

OUTPUT_LATEST_NAME = "字节跳动校招岗位_最新.xlsx"
CLEAN_OLD_OUTPUT = True
KEEP_HISTORY = os.getenv("KEEP_HISTORY", "0") == "1"

OUTPUT_COLUMNS = [
    "来源",
    "公司名",
    "岗位名",
    "工作城市",
    "招聘类型",
    "岗位职责",
    "岗位要求",
    "投递链接",
    "岗位发布时间",
    "报名截止时间",
    "采集时间",
]


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def random_delay(min_s: float = MIN_DELAY_S, max_s: float = MAX_DELAY_S) -> None:
    import time

    time.sleep(random.uniform(min_s, max_s))


def safe_text(s: Optional[str]) -> str:
    if not s:
        return ""
    return re.sub(r"\s+", " ", s).strip()


def pick_user_agent() -> str:
    try:
        ua = UserAgent()
        for _ in range(25):
            cand = ua.random
            if not cand:
                continue
            if any(x in cand for x in ["Mobile", "Android", "iPhone", "iPad"]):
                continue
            if not ("Chrome/" in cand or "Edg/" in cand):
                continue
            return cand
        return ua.random
    except Exception:
        return (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )


def ensure_output_dir() -> Path:
    out_dir = Path(__file__).resolve().parent / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def build_output_path(out_dir: Path) -> Path:
    return out_dir / OUTPUT_LATEST_NAME


def build_history_output_path(out_dir: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return out_dir / f"字节跳动校招岗位_{ts}.xlsx"


def cleanup_old_outputs(out_dir: Path) -> None:
    if not CLEAN_OLD_OUTPUT:
        return
    for p in out_dir.glob("字节跳动校招岗位_*.xlsx"):
        if p.name == OUTPUT_LATEST_NAME:
            continue
        try:
            p.unlink()
        except Exception:
            pass


def human_like_actions(page: Page) -> None:
    # 轻量的人类行为模拟：鼠标移动 + 滚动 + 小幅随机等待
    try:
        w = page.viewport_size["width"] if page.viewport_size else 1200
        h = page.viewport_size["height"] if page.viewport_size else 800
        x = random.randint(50, max(60, w - 50))
        y = random.randint(50, max(60, h - 50))
        page.mouse.move(x, y, steps=random.randint(8, 25))
    except Exception:
        pass

    try:
        page.mouse.wheel(0, random.randint(200, 900))
    except Exception:
        pass

    random_delay(0.4, 1.1)


def normalize_date_text(text: str) -> str:
    text = safe_text(text)
    if not text:
        return ""
    m = re.search(r"(\d{4})[./-](\d{1,2})[./-](\d{1,2})", text)
    if m:
        y, mo, d = m.groups()
        return f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"
    m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", text)
    if m:
        y, mo, d = m.groups()
        return f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"
    return ""


def extract_between(text: str, starts: List[str], ends: List[str]) -> str:
    t = text
    best: Optional[Tuple[int, int]] = None
    for sk in starts:
        si = t.find(sk)
        if si == -1:
            continue
        for ek in ends:
            ei = t.find(ek, si + len(sk))
            if ei == -1:
                continue
            span = (si + len(sk), ei)
            if best is None or (span[1] - span[0]) < (best[1] - best[0]):
                best = span
    if not best:
        return ""
    chunk = t[best[0] : best[1]]
    return safe_text(chunk)


def should_keep(title: str, city: str, recruit_type: str, category: str) -> bool:
    city = safe_text(city)
    recruit_type = safe_text(recruit_type)
    text = safe_text(f"{title} {category}")

    if CITY_KEYWORD and CITY_KEYWORD not in city:
        return False
    if ROLE_KEYWORDS and not any(k.lower() in text.lower() for k in ROLE_KEYWORDS):
        return False
    if RECRUIT_TYPE_KEYWORDS and not any(k in recruit_type for k in RECRUIT_TYPE_KEYWORDS):
        return False
    return True


def should_keep_any_city(title: str, recruit_type: str, category: str) -> bool:
    recruit_type = safe_text(recruit_type)
    text = safe_text(f"{title} {category}")
    if ROLE_KEYWORDS and not any(k.lower() in text.lower() for k in ROLE_KEYWORDS):
        return False
    if RECRUIT_TYPE_KEYWORDS and not any(k in recruit_type for k in RECRUIT_TYPE_KEYWORDS):
        return False
    return True


def extract_list_cards(page: Page) -> List[Dict[str, str]]:
    try:
        cards = page.evaluate(
            """() => {
                const base = location.href;
                const absUrl = (h) => {
                    try { return new URL(h, base).href; } catch (e) { return null; }
                };

                const getText = (el) => (el && el.textContent ? el.textContent.replace(/\\s+/g, " ").trim() : "");
                const uniq = new Set();
                const out = [];

                const anchors = Array.from(document.querySelectorAll('a[href*="/campus/position/"][href*="/detail"]'));
                const pickCard = (a) => {
                    let cur = a;
                    for (let i = 0; i < 10 && cur; i++) {
                        if (cur.querySelectorAll) {
                            const titleCount = cur.querySelectorAll('span[class*="positionItem-title-text"]').length;
                            const subCount = cur.querySelectorAll('div[class*="positionItem-subTitle"]').length;
                            if (titleCount === 1 && subCount >= 1) return cur;
                        }
                        cur = cur.parentElement;
                    }
                    return a.parentElement || a;
                };

                for (const a of anchors) {
                    const href = absUrl(a.getAttribute("href"));
                    if (!href) continue;
                    if (!/\\/campus\\/position\\/\\d+\\/detail/.test(new URL(href).pathname)) continue;
                    if (uniq.has(href)) continue;
                    uniq.add(href);

                    const card = pickCard(a);

                    const titleEl = card.querySelector('span[class*="positionItem-title-text"]')
                        || card.querySelector('span[class*="title-text"]')
                        || card.querySelector('h3, h4');
                    const title = getText(titleEl) || getText(a);

                    const rawSubSpans = Array.from(card.querySelectorAll('div[class*="positionItem-subTitle"] span'))
                        .map(getText)
                        .filter(Boolean);
                    const subSpans = [];
                    for (const t of rawSubSpans) {
                        if (subSpans.length === 0 || subSpans[subSpans.length - 1] !== t) subSpans.push(t);
                    }

                    let city = subSpans[0] || "";
                    let recruitType = subSpans[1] || "";
                    let category = subSpans[2] || "";

                    const cardText = getText(card);
                    if (!city && cardText.includes("上海")) city = "上海";
                    if (!recruitType) {
                        if (cardText.includes("实习")) recruitType = "实习";
                        else if (cardText.includes("校招")) recruitType = "校招";
                        else if (cardText.includes("提前批")) recruitType = "提前批";
                        else if (cardText.includes("秋招")) recruitType = "秋招";
                    }

                    out.push({ title, city, recruit_type: recruitType, category, url: href });
                }

                return out;
            }""",
        )
        return list(cards) if cards else []
    except Exception:
        pass

    try:
        html = page.content()
        urls = sorted(set(re.findall(r"https://jobs\\.bytedance\\.com/campus/position/\\d+/detail", html)))
        return [{"title": "", "city": "", "recruit_type": "", "category": "", "url": u} for u in urls]
    except Exception:
        return []


def extract_field_by_label(body_text: str, labels: List[str]) -> str:
    t = body_text
    for label in labels:
        m = re.search(rf"{re.escape(label)}\s*[:：]?\s*(.+)", t)
        if m:
            value = safe_text(m.group(1))
            if value:
                value = re.split(r"\s{2,}", value)[0]
                value = re.split(r"(岗位职责|职位描述|任职要求|岗位要求|投递|截止|发布时间)", value)[0]
                return safe_text(value)
    return ""


def extract_detail_texts(detail_page: Page, url: str) -> Dict[str, str]:
    detail_page.goto(url, wait_until="domcontentloaded", timeout=60000)
    try:
        try:
            detail_page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
        html_snapshot = detail_page.content()
    except Exception:
        html_snapshot = ""
    random_delay()
    human_like_actions(detail_page)

    try:
        detail_page.wait_for_timeout(random.randint(400, 900))
    except Exception:
        pass

    body_text = ""
    try:
        body_text = detail_page.locator("body").inner_text(timeout=15000)
    except Exception:
        body_text = ""
    body_text = body_text or ""

    publish_date = normalize_date_text(extract_field_by_label(body_text, ["发布时间", "发布于", "发布", "更新于"]))
    deadline = normalize_date_text(extract_field_by_label(body_text, ["截止时间", "报名截止", "投递截止", "结束时间", "截止"]))

    if not publish_date or not deadline:
        html = html_snapshot
        if not html:
            try:
                html = detail_page.content()
            except Exception:
                html = ""

        if not publish_date:
            m = re.search(r"publishTime\D{0,20}(\d{10,13})", html, flags=re.I) if html else None
            if not m:
                try:
                    html2 = detail_page.content()
                except Exception:
                    html2 = ""
                m = re.search(r"publishTime\D{0,20}(\d{10,13})", html2, flags=re.I) if html2 else None
            if m:
                ts = int(m.group(1))
                if ts > 10_000_000_000:
                    ts //= 1000
                try:
                    publish_date = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                except Exception:
                    pass

        if not deadline:
            for pat in [
                r"deadline\D{0,20}(\d{10,13})",
                r"applyDeadline\D{0,20}(\d{10,13})",
                r"endTime\D{0,20}(\d{10,13})",
            ]:
                m = re.search(pat, html, flags=re.I) if html else None
                if not m:
                    try:
                        html2 = detail_page.content()
                    except Exception:
                        html2 = ""
                    m = re.search(pat, html2, flags=re.I) if html2 else None
                if not m:
                    continue
                ts = int(m.group(1))
                if ts > 10_000_000_000:
                    ts //= 1000
                try:
                    deadline = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                    break
                except Exception:
                    pass

    responsibility = extract_between(
        body_text,
        starts=["岗位职责", "职位描述", "工作职责"],
        ends=["岗位要求", "任职要求", "职位要求", "加分项", "投递", "相关职位", "工作地点", "投递截止", "截止时间"],
    )
    requirement = extract_between(
        body_text,
        starts=["岗位要求", "任职要求", "职位要求"],
        ends=["加分项", "投递", "相关职位", "工作地点", "投递截止", "截止时间", "岗位职责", "职位描述"],
    )

    if not publish_date or not deadline:
        try:
            detail_page.wait_for_timeout(800)
        except Exception:
            pass
        try:
            html_end = detail_page.content()
        except Exception:
            html_end = ""
        if not publish_date and html_end:
            m = re.search(r"publishTime\D{0,20}(\d{10,13})", html_end, flags=re.I)
            if m:
                ts = int(m.group(1))
                if ts > 10_000_000_000:
                    ts //= 1000
                try:
                    publish_date = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                except Exception:
                    pass
        if not deadline and html_end:
            for pat in [
                r"deadline\D{0,20}(\d{10,13})",
                r"applyDeadline\D{0,20}(\d{10,13})",
                r"endTime\D{0,20}(\d{10,13})",
            ]:
                m = re.search(pat, html_end, flags=re.I)
                if not m:
                    continue
                ts = int(m.group(1))
                if ts > 10_000_000_000:
                    ts //= 1000
                try:
                    deadline = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                    break
                except Exception:
                    pass

    return {
        "岗位职责": responsibility,
        "岗位要求": requirement,
        "岗位发布时间": publish_date,
        "报名截止时间": deadline,
    }


def crawl_bytedance_official(context: BrowserContext) -> List[Dict[str, str]]:
    page = new_stealth_page(context)
    print("[1/5] 字节校招官网：抓取列表页岗位卡片 ...")
    cards: List[Dict[str, str]] = []
    for current in range(1, MAX_PAGES + 1):
        list_url = f"{START_URL}?current={current}&limit={LIST_LIMIT}"
        print(f"[1/5] 字节列表页 {current}/{MAX_PAGES}：{list_url}")
        page.goto(list_url, wait_until="domcontentloaded", timeout=60000)
        try:
            page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
        try:
            page.wait_for_selector('a[href*="/campus/position/"][href*="/detail"]', timeout=20000)
        except Exception:
            pass
        random_delay()
        human_like_actions(page)

        batch = extract_list_cards(page)
        if not batch:
            try:
                page.wait_for_timeout(1500)
            except Exception:
                pass
            batch = extract_list_cards(page)
        if not batch:
            continue

        cards.extend(batch)
        if len(cards) >= MAX_JOBS:
            break

    uniq_cards: List[Dict[str, str]] = []
    seen_url = set()
    for c in cards:
        u = c.get("url", "")
        if not u or u in seen_url:
            continue
        seen_url.add(u)
        uniq_cards.append(c)
    uniq_cards = uniq_cards[:MAX_JOBS]

    print(f"[1/5] 字节候选卡片：{len(uniq_cards)} 条")
    results: List[Dict[str, str]] = []
    for idx, c in enumerate(uniq_cards, start=1):
        title = safe_text(c.get("title"))
        city = safe_text(c.get("city"))
        recruit_type = safe_text(c.get("recruit_type"))
        category = safe_text(c.get("category"))
        url = safe_text(c.get("url"))

        if not should_keep(title, city, recruit_type, category):
            continue

        print(f"[2/5] 字节详情 {idx}/{len(uniq_cards)}：{title} | {city} | {recruit_type}")
        random_delay()
        detail_page = new_stealth_page(context)
        try:
            detail = extract_detail_texts(detail_page, url)
            results.append(
                {
                    "来源": "字节校招官网",
                    "公司名": "字节跳动",
                    "岗位名": title,
                    "工作城市": city,
                    "招聘类型": recruit_type,
                    "岗位职责": detail.get("岗位职责", ""),
                    "岗位要求": detail.get("岗位要求", ""),
                    "投递链接": url,
                    "岗位发布时间": detail.get("岗位发布时间", ""),
                    "报名截止时间": detail.get("报名截止时间", "") or "官网未提供",
                    "采集时间": now_str(),
                }
            )
        except Exception as e:
            print(f"[2/5] ⚠️ 字节该岗位提取失败，已跳过：{e}")
        finally:
            try:
                detail_page.close()
            except Exception:
                pass
    return results


def extract_nowcoder_job_detail(page: Page, url: str) -> Dict[str, str]:
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    try:
        page.wait_for_load_state("networkidle", timeout=20000)
    except Exception:
        pass
    random_delay()
    human_like_actions(page)

    body_text = ""
    try:
        body_text = page.locator("body").inner_text(timeout=15000)
    except Exception:
        body_text = ""
    body_text = body_text or ""

    title = ""
    try:
        title = safe_text(page.locator("h1").first.text_content(timeout=3000))
    except Exception:
        title = ""
    if not title:
        try:
            title = safe_text(page.locator("h2").first.text_content(timeout=3000))
        except Exception:
            title = ""

    publish_date = ""
    m = re.search(r"\b(\d{4}[./-]\d{1,2}[./-]\d{1,2})\b", body_text)
    if m:
        publish_date = normalize_date_text(m.group(1))

    recruit_type = ""
    head_chunk = "\n".join(body_text.splitlines()[:120])
    if "实习" in head_chunk:
        recruit_type = "实习"
    elif "提前批" in head_chunk:
        recruit_type = "提前批"
    elif "秋招" in head_chunk:
        recruit_type = "秋招"
    elif "校招" in head_chunk:
        recruit_type = "校招"

    city = ""
    m_loc = re.search(r"(工作地点|地点|城市)\s*[:：]?\s*([^\n]{1,30})", body_text)
    if m_loc:
        loc_txt = safe_text(m_loc.group(2))
        if "上海" in loc_txt:
            city = "上海"
        else:
            m2 = re.search(r"(北京|上海|深圳|杭州|广州|成都|武汉|西安|南京|苏州|重庆|天津|长沙|厦门|珠海)", loc_txt)
            if m2:
                city = m2.group(1)

    if not city:
        if "上海市" in body_text or "\n上海\n" in body_text:
            city = "上海"
        else:
            m2 = re.search(r"(北京|上海|深圳|杭州|广州|成都|武汉|西安|南京|苏州|重庆|天津|长沙|厦门|珠海)市", body_text)
            if m2:
                city = m2.group(1)

    responsibility = extract_between(
        body_text,
        starts=["岗位职责", "职位描述", "工作职责"],
        ends=["岗位要求", "任职要求", "职位要求", "投递", "字节跳动", "移动版"],
    )
    requirement = extract_between(
        body_text,
        starts=["岗位要求", "任职要求", "职位要求"],
        ends=["投递", "字节跳动", "查看其他", "笔试题目", "面试经验", "移动版"],
    )

    return {
        "公司名": "字节跳动" if "字节跳动" in body_text else "",
        "岗位名": title,
        "工作城市": city,
        "招聘类型": recruit_type,
        "岗位职责": responsibility,
        "岗位要求": requirement,
        "投递链接": url,
        "岗位发布时间": publish_date,
        "报名截止时间": "",
        "采集时间": now_str(),
    }


def extract_nowcoder_job_cards(page: Page) -> List[Dict[str, str]]:
    try:
        cards = page.evaluate(
            """() => {
                const abs = (h) => { try { return new URL(h, location.href).href; } catch (e) { return null; } };
                const getText = (el) => (el && el.innerText ? el.innerText.replace(/\\s+/g, " ").trim() : "");
                const anchors = Array.from(document.querySelectorAll('a[href*="/jobs/detail/"]'));
                const out = [];
                const seen = new Set();
                for (const a of anchors) {
                    const href = abs(a.getAttribute("href"));
                    if (!href) continue;
                    if (seen.has(href)) continue;
                    seen.add(href);
                    const card = a.closest('li, div') || a;
                    const txt = getText(card);
                    out.push({ url: href, text: txt });
                }
                return out;
            }"""
        )
        return list(cards) if cards else []
    except Exception:
        return []


def crawl_nowcoder(context: BrowserContext) -> List[Dict[str, str]]:
    page = new_stealth_page(context)
    print("[3/5] 牛客网：进入字节跳动企业页并收集职位链接（仅保留上海） ...")

    job_urls: List[str] = []
    deadline_global = ""
    for page_no in range(1, NOWCODER_MAX_PAGES + 1):
        list_url = f"{NOWCODER_ENTERPRISE_URL}?page={page_no}&recruitType=1"
        print(f"[3/5] 牛客企业页 {page_no}/{NOWCODER_MAX_PAGES}：{list_url}")
        page.goto(list_url, wait_until="domcontentloaded", timeout=60000)
        try:
            page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
        random_delay()
        human_like_actions(page)

        try:
            body = page.locator("body").inner_text(timeout=8000)
        except Exception:
            body = ""

        if any(k in (body or "") for k in ["安全校验", "人机验证", "滑动验证", "请完成验证"]):
            print("[3/5] 牛客网触发验证/登录限制，本次跳过牛客抓取。")
            return []

        if not deadline_global and body:
            m = re.search(
                r"网申时间\s*[:：]?\s*(\d{4}[./-]\d{1,2}[./-]\d{1,2})\s*[~\-]\s*(\d{4}[./-]\d{1,2}[./-]\d{1,2})",
                body,
            )
            if m:
                deadline_global = normalize_date_text(m.group(2))

        cards = extract_nowcoder_job_cards(page)
        for c in cards:
            u = safe_text(c.get("url")).replace("&amp;", "&").split("#")[0]
            txt = safe_text(c.get("text"))
            if not u:
                continue
            if "上海" not in txt:
                continue
            if u not in job_urls:
                job_urls.append(u)
        if len(job_urls) >= NOWCODER_MAX_PAGES * NOWCODER_LIST_LIMIT:
            break

    job_urls = job_urls[: NOWCODER_MAX_PAGES * NOWCODER_LIST_LIMIT]
    print(f"[3/5] 牛客候选职位链接：{len(job_urls)} 条；企业页截止时间：{deadline_global or '未识别'}")

    results: List[Dict[str, str]] = []
    for idx, url in enumerate(job_urls, start=1):
        print(f"[3/5] 牛客详情 {idx}/{len(job_urls)}：{url}")
        random_delay()
        detail_page = new_stealth_page(context)
        try:
            row = extract_nowcoder_job_detail(detail_page, url)
            row["工作城市"] = CITY_KEYWORD
            if not should_keep(row.get("岗位名", ""), row.get("工作城市", ""), row.get("招聘类型", ""), ""):
                continue
            row["来源"] = "牛客网"
            if not row.get("公司名"):
                row["公司名"] = "字节跳动"
            if deadline_global and not row.get("报名截止时间"):
                row["报名截止时间"] = deadline_global
            results.append(row)
        except Exception as e:
            print(f"[3/5] ⚠️ 牛客该岗位提取失败，已跳过：{e}")
        finally:
            try:
                detail_page.close()
            except Exception:
                pass
    if not results:
        print("[3/5] 牛客网未找到上海岗位（或页面未提供上海标识），本次牛客输出为0。")
    return results


def new_stealth_page(context: BrowserContext) -> Page:
    p = context.new_page()
    try:
        STEALTH.apply_stealth_sync(p)
    except Exception:
        pass
    return p


def launch(playwright: Playwright) -> Tuple[Browser, BrowserContext]:
    ua = pick_user_agent()
    print(f"[0/5] 本次使用UA: {ua}")

    browser = playwright.chromium.launch(
        headless=os.getenv("HEADLESS", "0") == "1",
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
        ],
    )
    context = browser.new_context(
        user_agent=ua,
        viewport={"width": 1280, "height": 800},
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
    )
    return browser, context


def main() -> int:
    out_dir = ensure_output_dir()
    out_path = build_output_path(out_dir)
    cleanup_old_outputs(out_dir)

    print("[0/5] 启动浏览器 ...")
    with sync_playwright() as playwright:
        browser, context = launch(playwright)
        all_rows: List[Dict[str, str]] = []
        try:
            all_rows.extend(crawl_bytedance_official(context))
        except Exception as e:
            print(f"[1/5] ⚠️ 字节校招官网抓取失败：{e}")

        try:
            all_rows.extend(crawl_nowcoder(context))
        except Exception as e:
            print(f"[3/5] ⚠️ 牛客网抓取失败：{e}")

        try:
            browser.close()
        except Exception:
            pass

    print("[4/5] 写入Excel ...")
    df = pd.DataFrame(all_rows, columns=OUTPUT_COLUMNS)
    df = df.fillna("")

    try:
        try:
            if out_path.exists():
                out_path.unlink()
        except Exception:
            pass
        df.to_excel(out_path, index=False)
    except PermissionError:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fallback = out_dir / f"字节跳动校招岗位_最新_无法覆盖_{ts}.xlsx"
        df.to_excel(fallback, index=False)
        out_path = fallback
        print("[4/5] ⚠️ 输出文件正在被占用（可能Excel打开中），已改为写入临时文件。关闭Excel后重跑即可覆盖最新文件。")
    print(f"[5/5] 完成 ✅ 已保存：{out_path}")
    if KEEP_HISTORY:
        try:
            import shutil

            hist = build_history_output_path(out_dir)
            shutil.copyfile(out_path, hist)
            print(f"[5/5] 已额外保留历史文件：{hist}")
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    try:
        from main import run

        raise SystemExit(run())
    except ImportError:
        raise SystemExit(main())

