# 项目目录说明

## 核心代码
- `official_multi_crawler.py`：官方站抓取主入口（当前重点快手）
- `merge_file.py`：合并清洗、评分、目标池与看板输出
- `parsers/`：公司适配器
- `rules/`：届别规则、城市归一规则
- `run_kuaishou_daily.ps1`：每日自动化运行脚本

## 历史归档
- `archive/history/shixiseng/`：实习僧历史抓取脚本与数据
- `archive/history/legacy_runs/`：历史跑批快照与旧实验文件
- `archive/history/debug/`：历史调试与排障材料

## 常用输出
- `official_jobs_raw.csv`：官方抓取原始汇总
- `internship_all_master.csv`：清洗后主库
- `dashboard_kuaishou_*.csv`：快手行动看板
