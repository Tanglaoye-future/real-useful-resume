# 拉勾网 - 抓包与反爬分析报告 (阶段 1)

## 1. 入口选型与优先级
- **Web端**: `https://www.lagou.com/`
  - 优点：拉勾的 Web 端主要依赖 JSON API 返回数据，结构化好。
  - 缺点：拥有极强的请求头校验（防重放攻击）和 Cookie 动态绑定机制，反爬策略非常活跃。
- **移动端 APP / 小程序**:
  - 缺点：抓包成本较高，且需要处理 APP 专属的签名机制。

**当前结论**：优先选择 **Web 端 API**。其核心挑战在于突破 `X-Anit-Forge-Code` 及动态 Cookie 验证。

## 2. 核心接口分析 (Web端)

### 2.1 职位搜索列表接口
- **URL**: `https://www.lagou.com/jobs/positionAjax.json`
- **Method**: POST
- **Query Params**:
  - `px`: 排序方式
  - `city`: 城市
  - `needAddtionalResult`: `false`
- **Payload (Form Data)**:
  - `first`: 是否首页 (`true`/`false`)
  - `pn`: 页码
  - `kd`: 关键词
- **核心反爬机制**:
  - **`X-Anit-Forge-Code`** 和 **`X-Anit-Forge-Token`**: 这两个请求头是拉勾最核心的反爬参数。
  - **`X-Requested-With`**: 必须是 `XMLHttpRequest`。
  - **Referer 强校验**: 必须带上合法的来源页面 URL（如 `https://www.lagou.com/jobs/list_...`）。
  - **动态 Cookie (`user_trace_token`, `X_HTTP_TOKEN`)**: 必须先访问一次 HTML 页面获取初始 Cookie，然后再请求 API。如果直接裸请求 API 会被拦截。

## 3. 疑似加密点与后续突破方向

1. **`X-Anit-Forge` 签名逆向**:
   - **定位**: 在 DevTools 中给 `X-Anit-Forge-Code` 下请求断点。这部分逻辑通常被打包在一个混淆的全局 JS 文件中。
   - **机制**: 该 Token 通常是由当前页面的一个隐藏元素、时间戳以及一个随机数通过复杂算法（如类似 MD5 加盐或特定位移操作）生成的。
   - **突破计划**: 提取出生成该头部的 JS 核心代码，利用 Python 的 `PyExecJS` 或本地 Node 服务传入必要参数动态生成这组 Headers。

2. **Session 与 Cookie 维护**:
   - **机制**: 拉勾对会话的连贯性要求极高。
   - **突破计划**: 
     - 爬虫流程必须设计为：首先 GET 请求主搜索页（带上正常的 UA 和 TLS 指纹），解析并保存响应中的 Cookie。
     - 然后携带该 Cookie 和生成的 `X-Anit-Forge` Header 发送 POST 请求到 `positionAjax.json`。
     - 如果遇到 `{"status": false, "msg": "您操作太频繁,请稍后再试"}`，需立即触发 Cookie 更换机制或挂起等待。