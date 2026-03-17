# internship_finding

多源官方校招/实习抓取与清洗项目（字节/腾讯/快手/小红书/美团/阿里/京东），用于产出可投递岗位池与公司行动看板。

## 目录

- `official_multi_crawler.py`：官方源抓取主入口
- `merge_file.py`：清洗、规则判定、评分、看板输出
- `parsers/`：公司适配器（按公司定制字段解析）
- `rules/`：27届规则与城市归一化
- `utils/link_checker.py`：链接健康检查
- `run_kuaishou_daily.ps1`：一键运行脚本
- `organize_workspace.ps1`：产物整理脚本

## 运行

```powershell
python official_multi_crawler.py
python merge_file.py
```

或直接执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\run_kuaishou_daily.ps1
```

## 输出

- 运行产物默认写入 `outputs/`（已在 `.gitignore` 忽略）
- 本仓库额外保留一份可分享快照到 `release_data/`，用于版本对比与复盘
