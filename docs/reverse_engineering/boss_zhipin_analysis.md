# BOSS 直聘 - 抓包与反爬分析报告 (阶段 1)

## 1. 入口选型与优先级
- **Web端 (PC网页)**: `https://www.zhipin.com/web/geek/job`
  - 优点：DOM 结构相对稳定，接口直观。
  - 缺点：反爬极强，具备动态 Token、指纹检测（Canvas/WebGL）、严格的 IP 与账号频率限制，甚至有 TLS 指纹校验。
- **H5/小程序**: 
  - 优点：某些反爬参数可能弱于 PC 端。
  - 缺点：接口经常变更，可能有特定的小程序签名（如微信 `wx.request` 包装的校验）。
- **移动端 APP**:
  - 优点：数据最全。
  - 缺点：存在强 SSL Pinning，需 Frida/Objection 绕过，请求体通常有强加密签名。

**当前结论**：优先针对 **Web 端** 进行深度逆向，因其对分布式部署（无需真机农场）最友好。若 PC Web 端指纹难以 1:1 伪造，备选 H5 接口。

## 2. 核心接口分析 (Web端)

### 2.1 职位搜索列表接口
- **URL**: `https://www.zhipin.com/wapi/zpgeek/search/joblist.json`
- **Method**: GET
- **Query Params**:
  - `scene`: 场景值（如 `1`, `2`）
  - `query`: 搜索关键词（如 `实习`, `2027校招`）
  - `city`: 城市代码（上海为 `101020100`）
  - `experience`: 经验要求（如 `102` 代表应届生）
  - `page`: 页码
  - `pageSize`: 每页数量
- **核心反爬 Header/Cookie**:
  - **`__zp_stoken__`** (Cookie/Query): 核心动态 Token，由前端 JS 收集浏览器指纹（UserAgent, Canvas, WebDriver 状态等）并加密生成。如果缺失或校验失败，接口返回 302 重定向到验证码页面或直接 403。
  - **`zp_token`**: 另一个关键标识。
  - **TLS 指纹**: 服务器可能校验 JA3 签名，如果使用标准 `requests` 库会被识别为非浏览器客户端。

### 2.2 职位详情接口
- **URL**: `https://www.zhipin.com/wapi/zpgeek/job/detail.json`
- **Query Params**:
  - `jid`: 职位 ID（从列表接口获取）
  - `lid`: 追踪 ID（关联列表页的会话）
- **反爬特征**: 同列表接口，高频访问极易触发图形/滑块验证码。

## 3. 疑似加密点与后续突破方向

1. **`__zp_stoken__` 逆向**:
   - **定位**: 在 DevTools 中全局搜索 `__zp_stoken__` 或通过 XHR Breakpoint 拦截 `joblist.json`。
   - **混淆**: 相关的 JS 通常经过高度混淆（如 OLLVM），包含大量的环境检测（`window.navigator.webdriver`, `plugins`, Canvas 渲染哈希等）。
   - **突破计划**: 使用 AST 工具 (`@babel/parser`) 去混淆，或者直接使用基于 Chrome 内核的指纹浏览器（结合 `Playwright-stealth`）/ `curl_cffi` 配合本地 JS V8 引擎执行提取的加密函数。

2. **TLS/HTTP2 指纹伪造**:
   - 标准库（如 Python `requests`）无法过关。
   - **突破计划**: 强制要求使用 `curl_cffi` (Python) 或 `tls-client` (Go) 模拟 Chrome 的 TLS 握手特征。

3. **风控应对 (IP & 账号)**:
   - 单 IP 高频必封，需高质量隧道代理。
   - 某些接口可能需要扫码登录后的 Cookie 才能获取完整数据，需考虑 Cookie 池方案。