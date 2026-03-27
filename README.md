# 字节跳动招聘信息爬虫（极简版）

用于个人校招/实习信息收集：一键抓取“企业官方招聘渠道 + 第三方平台（牛客等）”的岗位信息，统一清洗、去重并导出，方便筛选、整理与投递。

## 目录结构

```
.
├─ output/                 # 导出的 Excel（自动创建）
├─ bytedance_crawler.py    # 爬虫主程序
├─ requirements.txt        # 依赖
└─ README.md
```

## 安装步骤（Windows / macOS / Linux 通用）

1) 建议创建虚拟环境（可选但推荐）

```bash
python -m venv .venv
```

Windows（PowerShell）：

```bash
.\.venv\Scripts\Activate.ps1
```

macOS / Linux：

```bash
source .venv/bin/activate
```

2) 安装依赖

```bash
pip install -r requirements.txt
```

3) 安装 Playwright 浏览器（必须做一次）

```bash
python -m playwright install chromium
```

## 运行命令

直接运行即可开始爬取（默认会弹出浏览器窗口，方便观察）

```bash
python bytedance_crawler.py
```

如果你想无头运行（不显示浏览器），设置环境变量：

Windows（PowerShell）：

```bash
$env:HEADLESS="1"
python bytedance_crawler.py
```

macOS / Linux：

```bash
HEADLESS=1 python bytedance_crawler.py
```

## 输出说明

- 输出目录：`output/`
- 默认输出（覆盖写入）
  - `output/jobs_latest.xlsx`（按梯队分Sheet：S/A/B/C + ALL）
  - `output/jobs_latest.csv`
  - `output/jobs_latest.json`
- 字段包含：unique_id、company_name、company_level、job_name、recruit_type、work_location、salary_range、publish_time、deadline、department、job_description、job_requirement、recruit_count、delivery_link、source_platform、crawl_time、original_url
- 增强字段（第三方平台）：company_nature、financing_round、company_scale、welfare_tag

## 注意事项

- 默认只抓配置文件中开启的平台与企业，且按梯队 S→A→B→C 串行调度；单源失败不会中断整体。
- 合规提示：仅抓取公开发布岗位信息；遵守各站点 robots/条款；对合规不确定的第三方平台默认关闭。
- 反爬与稳定性：内置随机等待与人类行为模拟；如遇验证码/登录限制，建议 `HEADLESS=0` 观察后重试或关闭对应平台开关。
- 增量更新：默认启用，会将结果合并到 `output/jobs_latest.json` 并按 unique_id 覆盖更新；发布时间过滤策略可在 `config.py` 的 INCREMENTAL 中调整。
- 日志：运行日志输出到 `logs/crawl_YYYYMMDD.log`，可用于定位单公司/单平台失败原因。
- 第三方精准扩圈：已支持实习僧、猎聘（可在 `config.py` 中开关），默认启用黑名单去重与上海筛选。

## 使用方式

1) 安装依赖与浏览器驱动

```bash
pip install -r requirements.txt
playwright install
```

2) 修改配置

编辑 [config.py](file:///c:/Users/Lenovo/Desktop/useful-version/config.py)：
- 企业梯队名单、公司别名、公司官方入口
- 平台开关（默认仅 official + nowcoder）
- 频率、页数、增量窗口、输出格式等

3) 运行

```bash
python bytedance_crawler.py
```

4) 生成高价值岗位榜单

```bash
python -m etl.high_value_report
```

可选环境变量：
- `HEADLESS=1`：无头模式
- `KEEP_HISTORY=1`：保留历史输出

## 常见问题

1) 报错 `playwright` 相关依赖缺失或浏览器未安装
- 先执行：`pip install -r requirements.txt`
- 再执行：`python -m playwright install chromium`

2) Excel 没有数据/数据很少
- 可能是当天岗位较少或页面加载不稳定，可多运行几次。
- 脚本会按“上海 + 技术/产品关键词 + 招聘类型关键词”做筛选，筛选较严格时结果会变少。
