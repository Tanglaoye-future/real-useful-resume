## LinkedIn 爬虫（登录后录制式采集）

你当前的设想是“登录后滑动截屏 → 解析截图”。这个路线**可行**，但要提前接受两个现实：

- **风控/封号风险不会因为截图而消失**：只要是自动化控制浏览器、批量翻页、异常频率访问，LinkedIn 仍然可能检测到（行为、节奏、指纹、请求模式）。截图只是把“数据抽取”从 DOM 改成像素层。
- **纯 OCR 的准确率/成本会显著更差**：尤其是职位描述（长文本、换行、展开折叠、语言混杂）。所以这里采用 **DOM 文本抽取为主、截图为审计/兜底** 的混合方案。

本目录提供的 pipeline 是：

1. **capture**：在已登录的浏览器会话中，随着你滚动浏览，把当前可见的 job card 以及右侧详情文本抓取出来；同时保存截图
2. **raw 输出**：写入 `data/raw/linkedin/linkedin_YYYYMMDD.jsonl`
3. **ingest**：复用项目现有 `scripts/ingest_all.py` → 进入统一 `Job` schema

### 安装（可选依赖）

项目根的 `requirements.txt` 不强制加入浏览器依赖。你需要单独安装：

```bash
pip install -r linkedin/requirements.txt
python -m playwright install chromium
```

### 使用

1) 运行录制脚本（会打开一个可复用的浏览器 profile）：

```bash
py linkedin/run_capture.py
```

2) 在打开的页面里**手动登录** LinkedIn（只需一次，后续会复用 profile）。

3) 进入 Jobs 搜索结果页，开始滚动浏览。脚本会：

- 每隔几秒保存一张截图到 `outputs/linkedin/screenshots/<run_id>/`
- 尝试从页面 DOM 抽取：`url/title/company/location/jd_text/publish_date`
- 去重后写入 `data/raw/linkedin/linkedin_<date>.jsonl`

4) 入库统一数据：

```bash
py scripts/ingest_all.py --jsonl-mirror
```

### 重要注意事项（避免“必封号”行为）

- 不要用高频滚动/秒级点击遍历；建议保持**人工节奏**，且每次录制控制在较短时间段
- 不要在一个会话里跨大量关键词组合批量跑；更像真实用户浏览
- 避免同时开多个自动化实例；同账号/同 IP 的异常并发风险很高

