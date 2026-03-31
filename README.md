# ResuMiner

ResuMiner 是一个面向大厂校招/实习岗位的抓取与数据发布仓库，当前版本聚焦 8 家公司：

- 字节跳动
- 腾讯
- 快手
- 小红书
- 美团
- 阿里巴巴
- 京东
- 哔哩哔哩

本仓库当前采用两条主线：

- CDP 逐公司抓取（抗风控主通道）
- 上海实习总表构建与链接可用性校验

## 当前版本能力

- 基于 CDP 连接真实浏览器会话，抓取各公司官方站点数据
- 输出公司级原始数据（`outputs/raw/*.csv`）与 CDP 原始包（`cdp_data/*.json`）
- 构建上海实习全量总表
- 对总表链接做批量可用性校验，输出可直接投递版本

## 项目结构

- `crawlers/cdp/`：各公司 CDP 抓取脚本（主抓取通道）
- `crawlers/xiaohongshu_crawler.py`：小红书官方抓取脚本
- `official_multi_crawler.py`：多源聚合入口（连接 CDP 并做统一解析）
- `parsers/`：公司解析适配层
- `rules/`：届别与城市规则
- `cdp_data/`：CDP 抓取原始 JSON
- `outputs/raw/`：公司级原始 CSV
- `release_data/`：对外发布数据快照

## 环境要求

- Python 3.10+
- 已安装 Playwright 与 Chromium 运行环境
- 已启动带调试端口的浏览器（CDP）：

```powershell
chrome --remote-debugging-port=9222
```

## 运行方式

### 1) 按公司执行 CDP 抓取（推荐）

```powershell
python crawlers/cdp/cdp_tencent.py
python crawlers/cdp/cdp_kuaishou.py
python crawlers/cdp/cdp_meituan.py
python crawlers/cdp/cdp_alibaba.py
python crawlers/cdp/cdp_jd.py
python crawlers/cdp/cdp_bilibili.py
```

字节当前使用独立脚本：

```powershell
python c:\jz_code\internship_finding\real-useful-resume\bytedance_crawler.py
```

小红书使用：

```powershell
python crawlers/xiaohongshu_crawler.py
```

### 2) 生成上海总表

```powershell
python c:\jz_code\internship_finding\scripts\build_shanghai_internship_latest.py
```

### 3) 链接校验

基于 `utils/link_checker.py` 执行批量校验，产出：

- `release_data/internship_shanghai_link_validation_latest.csv`
- `release_data/internship_shanghai_verified_only_latest.csv`

## release_data 文件说明

- `internship_shanghai_latest.csv`：上海岗位全量总表
- `internship_shanghai_verified_only_latest.csv`：仅保留链接可访问（OK）的岗位
- `internship_shanghai_link_validation_latest.csv`：全量 + 链接状态明细
- `internship_shanghai_new_this_update.csv`：本次相对基线的新增岗位
- `internship_target_jobs_latest.csv`：历史基线/对照快照

## 当前版本已验证项

- 核心脚本语法检查通过：
  - `official_multi_crawler.py`
  - `crawlers/cdp/*.py`
  - `crawlers/xiaohongshu_crawler.py`
  - `parsers/*.py`
  - `rules/*.py`
- 上海总表构建脚本可执行：
  - `scripts/build_shanghai_internship_latest.py`

## 当前版本快照（2026-03-30）

- 上海总岗位：2932
- 八大厂均已覆盖
- 链接校验：2932/2932 可访问

## 注意事项

- CDP 脚本依赖已登录且可访问目标页面的浏览器上下文
- 网络波动可能导致短时超时，建议对 `RISKY` 结果做二次复核
- 本仓库默认使用“逐公司抓取 + 产物校验”流程，不建议一把全量盲跑
