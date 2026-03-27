# 招聘数据采集系统 - 运维与部署手册

## 1. 架构概述
本系统采用分布式的多线程并发架构，核心组件包括：
- **Spider Engine**: 基于 Python 的爬虫调度中心，使用 `curl_cffi` 绕过高级 TLS 指纹检测。
- **Crypto Engine**: 包含 JS 逆向（V8 引擎环境）与字体解析逻辑，用于突破 BOSS直聘、拉勾、实习僧等平台的动态加密和反爬限制。
- **Redis**: 作为任务队列、URL 去重过滤器以及全局代理池与节流控制器（Throttle）的存储中心。

## 2. Docker 部署指南

### 2.1 环境准备
- 安装 Docker 引擎 (>= 20.10)
- 安装 Docker Compose (>= 1.29)

### 2.2 构建与启动
1. **克隆代码并进入目录**：
   确保 `Dockerfile` 和 `docker-compose.yml` 在当前目录。
2. **构建镜像**：
   ```bash
   docker-compose build
   ```
3. **启动服务 (后台运行)**：
   ```bash
   docker-compose up -d
   ```
4. **查看日志**：
   ```bash
   docker-compose logs -f spider_engine
   ```
   *注意：初次启动时，若在日志中看到 `No data collected to save.`，通常是因为没有填入有效的 Cookie。*

### 2.3 获取结果数据
由于 `docker-compose.yml` 中配置了数据卷映射，爬虫生成的 `shanghai_intern_jobs.csv` 或其他输出文件，会同步出现在宿主机的 `./output` 目录下。

## 3. Cookie 管理与代理池配置

### 3.1 动态 Cookie 注入
系统强制依赖有效的登录态 Cookie（尤其是 BOSS、拉勾、智联）。
- **短期方案**：在 `run_spiders.py` 中的 `cookies` 字典手动填入最新的抓包 Cookie。
- **长期方案**：建议开发一个辅助的服务，使用 Playwright 定期无头登录这些平台，将刷新后的 Cookie 写入 Redis。然后在 `run_spiders.py` 初始化时从 Redis 读取最新 Cookie。

### 3.2 代理 IP 池 (Proxy Pool)
单 IP 高频访问会立刻触发风控（HTTP 403 / 429 或重定向到图形验证码）。
- **配置方法**：修改 `scheduler.py`，增加一个定时从代理供应商（如快代理、芝麻代理）API 获取代理 IP 的定时任务，并写入 Redis 的 `spider:proxies:pool` 集合中。
- `fetcher.py` 内部已经实现了当遇到封禁状态码时自动从 Scheduler 获取新代理的轮换机制。

## 4. 常见反爬应对策略与告警处理

### 4.1 异常现象 1: 频繁收到 403 / 302 重定向
**原因**：
- Cookie 已过期。
- IP 被目标网站封禁。
- TLS 指纹被识破。
**解决**：
- 更新 Cookie。
- 检查代理池的可用率。
- 确认 `fetcher.py` 中的 `impersonate` 参数（如 `chrome120`）是否需要随 Chrome 版本更新。

### 4.2 异常现象 2: 解析出错或返回内容为乱码/空 JSON
**原因**：
- 目标接口的加密签名算法已更新（例如 BOSS 的 `__zp_stoken__` 算法变动）。
- 实习僧的字体文件映射变动导致 `fontTools` 解析失败。
**解决**：
- 进入 `crypto_engine/ast_tools/`，重新下载最新的目标 JS 文件，运行反混淆脚本，更新 `crypto_engine/js/` 下的核心算法文件。
- 检查 `shixiseng.py` 的字体下载逻辑。

### 4.3 监控与告警
建议在 `run_spiders.py` 捕获到连续 5 次以上的 `raise_for_status()` 异常时，通过企业微信/钉钉 Webhook 发送告警，提示运维人员及时更新 Cookie 或逆向算法。