# 多线程并行招聘数据采集系统

这是一个企业级的多线程爬虫架构，专为采集上海地区互联网及外企的实习与校招岗位设计。支持多个招聘平台并行采集，具备随机 User-Agent、动态延时、请求重试等基础反爬能力，并将最终数据去重后输出为标准化 CSV。

## 1. 支持的平台
- BOSS直聘
- 拉勾网
- 前程无忧 (51job)
- 智联招聘
- 应届生求职网
- LinkedIn 领英中国
- 实习僧
- 猎聘

## 2. 环境配置
请确保你的机器已安装 Python 3.8+，然后执行以下命令安装依赖：

```bash
pip install -r requirements.txt
```

依赖包含：
- `requests`: 发送 HTTP 请求
- `beautifulsoup4`, `lxml`: HTML 解析
- `pandas`: 数据处理与 CSV 导出
- `fake-useragent`: 随机生成请求头 UA
- `tenacity`: 网络请求重试机制

## 3. Cookie 配置与准备 (重要)
大多数招聘平台（特别是 BOSS 直聘、拉勾网、智联招聘）对未登录状态的访问限制极为严格。在运行代码前，你**必须**手动提供有效的 Cookie。

**如何获取 Cookie：**
1. 使用 Chrome/Edge 浏览器，最好开启**无痕模式**。
2. 打开对应平台官网（如 `zhipin.com`），登录你的账号。
3. 按 `F12` 打开开发者工具，切换到 `Network` (网络) 面板。
4. 刷新页面，找到主文档请求或核心接口请求（通常是第一个或者带有 `search`, `list` 等字样的请求）。
5. 在右侧 `Headers` 面板中，找到 `Request Headers` 下的 `cookie:` 字段。
6. 复制整个 Cookie 字符串。

**填入代码：**
打开 `run_spiders.py` 文件，找到 `main()` 函数中的 `cookies` 字典，将你复制的 Cookie 替换进去：

```python
cookies = {
    "boss": "此处粘贴BOSS直聘的Cookie",
    "lagou": "此处粘贴拉勾网的Cookie",
    "job51": "此处粘贴前程无忧的Cookie",
    "zhaopin": "此处粘贴智联招聘的Cookie",
    "yingjiesheng": "此处粘贴应届生求职网的Cookie",
    "linkedin": "此处粘贴LinkedIn的Cookie",
    "shixiseng": "此处粘贴实习僧的Cookie",
    "liepin": "此处粘贴猎聘的Cookie"
}
```

## 4. 运行爬虫
配置好 Cookie 后，在终端中运行主程序：

```bash
python run_spiders.py
```

**运行逻辑说明：**
1. 调度器会通过 `ThreadPoolExecutor` 为每个平台分配一个独立的线程，实现平台级高并发。
2. 每个爬虫类继承自 `BaseSpider`，内置了失败重试（`tenacity`）和随机延时策略。
3. 抓取完成后，系统会使用 Pandas 合并所有数据，依据 `jd_url` 进行去重。
4. 最终结果保存在当前目录下的 `shanghai_intern_jobs.csv` 文件中，编码为 `utf-8-sig`，可直接用 Excel 打开。

## 5. 全局字段标准（统一口径）
所有平台 Spider 必须通过 `BaseSpider.format_data()` 输出数据，主流程会按 `BaseSpider.STANDARD_FIELDS` 对齐列顺序。当前标准字段如下：

- `job_name`, `company_name`, `location`, `city`, `district`
- `salary`, `salary_min`, `salary_max`, `salary_unit`, `salary_count`
- `job_type`, `employment_type`, `experience_requirement`, `education_requirement`
- `platform`, `source_job_id`, `source_keyword`
- `jd_url`, `jd_content`, `job_description`, `job_requirement`
- `job_tags`, `skill_tags`
- `company_industry`, `company_stage`, `company_size`, `welfare_tags`
- `publish_date`, `crawl_time`

## 6. 后续扩展与维护
- **修改搜索条件**：进入 `spiders/` 目录下各个爬虫文件的 `run()` 方法，修改 `params` 中的关键词（如 `query`, `kw`）或城市代码。
- **页面解析失效**：招聘网站前端结构经常变动，如果发现某个平台抓取不到数据，请检查该平台 Spider 的 `parse()` 方法中的 CSS 选择器或 JSON 键路径是否需要更新。
- **应对高级反爬**：目前的架构适用于基础反爬。若遇到需要滑动验证码或高度动态加载（完全由 JS 渲染且接口加密）的情况，可能需要将 `requests` 替换为 `Playwright` 或 `Selenium`，但整体多线程架构可保持不变。

## 7. 前程无忧行业聚焦预设
`job51_v2` 已支持行业聚焦预设，可通过 `JOB51_FOCUS_PROFILE` 一键切换：

- `internet`：偏互联网/软件/AI/电商岗位
- `foreign`：偏外企/外资/咨询/快消岗位
- `fmcg`：偏快消/零售/品牌/渠道岗位
- `balanced`：综合模式（默认）
- `custom`：使用自定义关键词（`JOB51_PREFERRED_*` 和 `JOB51_BLOCKED_*`）

常用环境变量：

- `JOB51_FOCUS_FILTER_ENABLED=1` 开启行业聚焦过滤
- `JOB51_FOCUS_STRICT_MODE=1` 严格模式，仅保留命中目标行业/公司的岗位
- `JOB51_FOCUS_MIN_SCORE=1` 过滤评分阈值

示例（互联网模式）：

```bash
$env:RUN_JOB51='1'
$env:JOB51_FOCUS_PROFILE='internet'
$env:JOB51_FOCUS_FILTER_ENABLED='1'
$env:JOB51_FOCUS_STRICT_MODE='1'
python run_spiders.py
```
