# LinkedIn 领英中国 - 抓包与反爬分析报告 (阶段 1)

## 1. 入口选型与优先级
- **免登录 Web 端 (Public Jobs)**: `https://www.linkedin.com/jobs/search`
  - 优点：无需管理复杂的登录态，适合基础职位数据采集。
  - 缺点：显示的职位信息受限，且在多次翻页后会强制要求登录（弹窗遮挡或重定向）。
- **登录态 Web 端**: 
  - 优点：数据完整。
  - 缺点：账号风控极严，极易被识别为自动化操作并封禁账号。

**当前结论**: 采用 **免登录 Web 端 + 高频代理 IP 轮换** 的策略进行。由于无需维护昂贵的领英账号池，此方案成本更低、更具可扩展性。

## 2. 核心接口分析 (免登录 Web端)

### 2.1 职位搜索页面 / 懒加载接口
- **URL**: `https://www.linkedin.com/jobs/search` (初始 HTML) / `https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search` (滚动加载的 HTML 片段)
- **Method**: GET
- **Query Params**:
  - `keywords`: 搜索词（如 `Intern`）
  - `location`: 地点（如 `Shanghai`）
  - `start`: 偏移量（翻页控制，通常以 25 为步长）
- **响应特征**:
  - 接口返回的是渲染好的 HTML 片段 (`<li>` 节点)，需要使用 CSS 选择器进行解析。

### 2.2 核心反爬机制
1. **强制登录拦截 (Auth Wall)**:
   - 当同一个 IP 访问超过一定页数（如 `start > 100`），或者请求头特征不符合真实浏览器时，服务器会返回 HTTP 999 状态码，或者重定向到登录页面 (`/authwall`)。
2. **Cookie 追踪**:
   - `bcookie`, `lidc` 等 Cookie 用于追踪用户会话。如果一个会话发出了过多异常请求，整个会话会被拉黑。
3. **高级浏览器指纹检测**:
   - 领英的安全团队在业内非常顶尖，他们会检测 TLS 握手特征（JA3）、HTTP/2 帧设置（JA4/HTTP2 Fingerprinting）。

## 3. 疑似加密点与后续突破方向

1. **TLS/HTTP2 指纹伪造 (核心难点)**:
   - **机制**: 标准的 `requests` 会在 TLS 握手阶段立即暴露。
   - **突破计划**: **必须** 使用 `curl_cffi` (Python) 或 `tls-client` (Go)，并将其伪装参数严格设置为最新版 Chrome (`impersonate="chrome120"` 等)。
2. **代理与会话的强绑定策略**:
   - **突破计划**: 
     - 在 `fetcher` 模块中实现“一次性会话”模式：每个代理 IP 只分配一个特定的任务（如只抓取某一个关键词的前 3 页）。
     - 每次切换 IP 时，必须完全清除所有的 Cookie 缓存，重新生成一套新的伪造 User-Agent，避免领英后端将不同 IP 的请求关联到一起。
3. **无头浏览器备选方案**:
   - 如果纯 HTTP 请求的成功率依然低于预期，需要在 `crypto-engine` 外挂一层基于 Playwright + `stealth` 插件的渲染集群，完全模拟真实 DOM 和 JS 执行环境。