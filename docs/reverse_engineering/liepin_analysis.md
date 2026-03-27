# 猎聘 - 抓包与反爬分析报告 (阶段 1)

## 1. 入口选型与优先级
- **Web端**: `https://www.liepin.com/zhaopin/`
  - 优点：支持基于筛选条件的结构化查询，DOM结构相对成熟。
  - 缺点：核心 API 有较强的请求头风控（自定义 Header 签名）。部分页面存在服务端渲染混淆，高频请求容易触发图形验证码。
- **H5端**:
  - 优点：部分反爬规则较 PC 端宽松。
  - 缺点：数据展示不如 PC 端全面。

**当前结论**：优先选择 **Web 端 API** 作为切入点，通过逆向其请求头签名来保证稳定获取 JSON 数据；若 API 难以突破，备选方案是走 Puppeteer/Playwright 直接监听浏览器 XHR 响应。

## 2. 核心接口分析 (Web端)

### 2.1 职位搜索列表接口
- **URL**: `https://www.liepin.com/api/com.liepin.searchfront4c.pc-search-job`
- **Method**: POST
- **Payload (JSON)**:
  包含 `mainSearchPcConditionForm`（含城市 `city`、关键词 `key`、当前页码 `currentPage` 等参数）和 `passThroughForm`（场景追踪参数）。
- **核心反爬 Header**:
  - **`X-Fscp-Std-Info`** / **`X-Fscp-Trace-Id`** / **`X-Fscp-Bi-Stat`**: 猎聘自定义的风控 Header。这些参数通常由前端 JS 收集浏览器指纹、时间戳等信息经过加密生成。缺失或错误会导致接口返回 `-1400`（无效通讯数据）或直接 403。
  - **`X-Requested-With`**: `XMLHttpRequest`

### 2.2 职位详情接口
- **URL**: 猎聘通常直接通过跳转详情页 URL（如 `https://www.liepin.com/job/123456.shtml`）获取数据。
- **反爬特征**: 
  - 详情页通常是服务端渲染 (SSR) 的 HTML。
  - 高频访问详情页极易触发猎聘的安全中心验证码拦截（通常是极验或自研图形验证码）。

## 3. 疑似加密点与后续突破方向

1. **请求头签名逆向 (核心难点)**:
   - **定位**: 在 DevTools 中全局搜索 `X-Fscp-`，定位生成这些 Header 的 JS 拦截器或风控 SDK（如 `fscp.js` 或类似名称的文件）。
   - **机制**: 分析其是否采用了 AES/RSA 加密或复杂的哈希算法，以及参与签名的因子（如 Cookie 中的 session id、时间戳、请求 body 的哈希等）。
   - **突破计划**: 
     - 使用 AST 还原混淆的 JS 算法。
     - 用 Go/Python 重新实现该签名生成逻辑，或者通过本地部署 Node.js 服务来执行提出来的 JS 签名函数。

2. **行为风控与验证码**:
   - **机制**: 猎聘对无登录态（或 Cookie 异常）的高频请求容忍度极低。
   - **突破计划**:
     - 必须携带高质量的真实登录 Cookie 进行请求。
     - 引入 Redis 调度器严格控制单个账号/IP 的请求频率（建议 >= 3秒）。
     - 若触发验证码，准备接入打码平台或使用 PaddleOCR + 轨迹算法过图形验证。