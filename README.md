# ResuMiner

多源官方校招/实习岗位抓取仓库，当前收录字节、腾讯、快手、小红书、美团、阿里、京东等来源，包含爬虫代码与可复用数据产物。

## 项目结构

- `official_multi_crawler.py`：主抓取入口（统一调度多公司官方源）
- `crawlers/`：各公司抓取器
- `crawlers/cdp/`：基于 CDP 的反爬抓取脚本
- `parsers/`：公司字段适配与解析逻辑
- `rules/`：27届规则与城市归一化规则
- `config.py`：抓取参数配置
- `cdp_data/`：CDP 抓取结果（JSON）
- `outputs/raw/`：公司级原始 CSV 输出
- `release_data/`：对外可分享的数据快照
- `official_jobs_raw.csv`：汇总原始岗位数据

## 运行方式

安装依赖后可直接运行主入口：

```powershell
python official_multi_crawler.py
```

也可以按公司入口运行（示例）：

```powershell
python crawlers\run_all_official.py
```

## 数据说明

- `cdp_data/*.json`：CDP 会话抓取的结构化原始结果
- `outputs/raw/*.csv`：按公司拆分的官方岗位原始数据
- `release_data/*.csv`：对外发布快照（汇总、质量、看板等）
- `official_jobs_raw.csv`：全量官方岗位原始汇总
