## 2026-04-27（本地）对话压缩记录：Claude 终端 + Cursor Chat（你和我）

> 目的：把今天终端里 Claude 的关键结论、以及你和我这次会话做“可追溯但不啰嗦”的 compact 记录，方便以后复盘与复跑。

---

## Claude（终端 1.txt）今天做了什么（高信号摘要）

### 外企官网（official sites）爬取结论（Phase 2 / P0）
- **结论**：外企全球官网对“上海实习”不是高产渠道，**6 个 P0 里只有 Amazon 真正产出**。
- **实测结果表（核心）**：
  - **Amazon**：Shanghai 132（总岗）→ **20 实习 ✅**（JD 通常 1.7K–3K 字符，pipeline 可用）
  - **Microsoft**：Shanghai 15（总岗）→ 0 实习（只有 1 条标题像 Internship，且 API 详情 JD 为空）
  - **Google**：Shanghai 20（总岗）→ 0 实习（多为资深/管理岗）
  - **Unilever / P&G / Citadel**：0（或 location/JD 指向非上海等“真阴性”）
- **解释**：大量上海实习通过高校合作/校招公众号/聚合站投放，而非全球 ATS 公网投放。

### Indeed + SmartShanghai 可行性探针（Probe）
- **Indeed（cn.indeed.com / indeed.com）**：Cloudflare “Security Check”，Playwright+UA+locale 也过不去 → **建议跳过**（ToS/维护成本高）
- **SmartShanghai**：纯 HTTP 可抓（200 OK），岗位 URL 规律 `/jobs/<category>/<id>` → **可实现**

### SmartShanghai 实际产出（本轮）
- **总 listings**：28
- **真实实习**：1 条（`Shanghai Program Coordinator Internship` / Absolute Internship）
- **产物**：`data/raw/smartshanghai/smartshanghai_20260427_123247.{jsonl,csv,log,_summary.txt}`
- **顺带结论**：SmartShanghai 小而精（外籍/英文向），量级远小于实习僧；实习僧仍是最大盘子。

### BOSS 直聘可行性结论（最终）
- 多种 Playwright/stealth/Chrome channel 方案均被拦；patchright 只能过主页静态检测。
- **搜索行为触发 GeeTest 滑块验证码**（`geetest_challenge/validate/seccode`），属于“付费问题”：
  - 可行路径：接 **2Captcha/YesCaptcha** 等（成本低但灰度/ToS 边缘），或买第三方数据源。
  - 结论：**免费爬到此为止**，不建议在本轮投入大量工程。

---

## 你和我（Cursor Chat）今天完成了什么（高信号摘要）

### A) ResuMiner：应届生（Yingjiesheng）A 选项落地（详情页补全）
- 目标：把 Phase1 只抓到的 375 个 URL stub，做 Phase2 详情页补全（title/company/jd_content）。
- **改造**：`scripts/run_yingjiesheng_crawl.py`
  - 增加 Phase2：Playwright 逐条打开 `jd_url`，抽取 `h1` + 正文，写入 `jd_content`
  - 支持 `YJS_INPUT_JSONL`：可跳过 Phase1 直接对已有 jsonl 做 enrich
  - 修复 Windows cp1252 终端导致中文 `UnicodeEncodeError`（stdout/stderr reconfigure）
- **全量跑通并确认覆盖率**：`rows with jd_content: 375/375`
- **输出（latest 版本见下）**：`data/raw/yingjiesheng/yingjiesheng_latest_enriched.*`

### B) “只保留最新输出、每次覆盖旧数据”的统一策略
你提出需求：所有 crawler/pipeline 输出都应该覆盖旧数据，目录里只保留最新结果。

#### 已引入的通用工具
- 新增：`scripts/output_latest.py`
  - `prune_directory(...)`：按 glob 清理旧时间戳文件，只保留 latest
  - Windows 下文件被 Excel 占用时，删除失败会跳过（不让 pipeline 因 PermissionError 崩溃）

#### 已改为 latest 输出 + 自动清理的 runner
- `scripts/run_smartshanghai_crawl.py`
  - 输出固定为：`data/raw/smartshanghai/smartshanghai_latest.{jsonl,csv,log,_summary.txt}`
  - 自动清理旧的 `smartshanghai_<TS>.*`
- `scripts/run_yingjiesheng_crawl.py`
  - 输出固定为：`data/raw/yingjiesheng/yingjiesheng_latest.*` 以及 `yingjiesheng_latest_enriched.*`
  - 自动清理旧的 `yingjiesheng_<TS>.*`
- `scripts/run_shixiseng_timeboxed.py`
  - 输出固定为：`data/raw/shixiseng/shixiseng_latest.*`
  - 自动清理旧的 `shixiseng_overnight_<TS>.*`
  - 同时修复 Windows 终端中文编码报错（stdout/stderr reconfigure）

#### 清理历史文件（已执行）
- `data/raw/smartshanghai/` 旧时间戳文件已删除，只剩 `smartshanghai_latest.*`

---

## 为什么 `data/raw/` 根目录之前会有“散落文件”，以及今天怎么处理
- 散落文件主要是 **跨源聚合/候选池快照**（不是单一站点原始数据）：
  - `foreign_candidate_raw_*.json` 来自 `scripts/foreign_pipeline_v2.py`
  - `integrated_jobs_*.json` 来自 `bin/run_with_existing_data.py`
- **今天做的整理**：
  1) 把历史散落文件迁移归档到 `data/raw/merged/`
  2) 把上述两个 pipeline 也改成 **latest 输出**：
     - `scripts/foreign_pipeline_v2.py`：写 `data/raw/foreign_candidate_raw_latest.json` 并清理旧 `foreign_candidate_raw_*.json`
     - `bin/run_with_existing_data.py`：写 `integrated_jobs_latest.json` 并清理旧 `integrated_jobs_*.json`
  3) 现在 `data/raw/` 根目录已保持干净（无散落文件）

---

## 当前“latest 输出”一览（你以后只看这些）
- `data/raw/smartshanghai/`：`smartshanghai_latest.*`
- `data/raw/yingjiesheng/`：`yingjiesheng_latest.*` + `yingjiesheng_latest_enriched.*`
- `data/raw/shixiseng/`：`shixiseng_latest.*`
- `data/raw/`：`foreign_candidate_raw_latest.json`

