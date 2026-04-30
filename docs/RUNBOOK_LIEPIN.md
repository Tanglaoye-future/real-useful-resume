# 猎聘全量运行手册（交接版）

本手册用于同学接手后，快速跑通“只抓猎聘 + 全量数据优先”流程。

## 1. 前置条件

- 系统：Windows
- Python 环境：已安装项目依赖（`pip install -r requirements.txt`）
- 必须使用 Chrome 并开启 CDP 调试端口

## 2. 启动浏览器（CDP）

先关闭所有 Chrome 窗口，再执行：

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\jz_code\internship_finding\chrome_dev_profile"
```

然后在该浏览器里手动登录猎聘账号（必须登录）。

## 3. 进入项目目录

```powershell
cd C:\jz_code\internship_finding\ResuMiner
```

## 4. 运行（只猎聘 + 全量优先）

```powershell
$env:FULL_DATA_MODE="1"
$env:ONLY_LIEPIN="1"
$env:PROCESS_RETRY_ONLY="1"
$env:RETRY_BATCH_SIZE="80"
python scripts/overnight_autorun.py
```

说明：

- `FULL_DATA_MODE=1`：先保全量，不做严格筛选门槛卡死。
- `ONLY_LIEPIN=1`：只抓猎聘，绕开 51job WAF 风险。
- `PROCESS_RETRY_ONLY=1`：优先清 backlog，不继续放大未处理队列。
- `RETRY_BATCH_SIZE=80`：每轮处理 80 条，可按机器性能调整。

## 5. 查看结果

```powershell
python tests/check_stats.py
```

重点看：

- `Master 总记录数`
- `成功`
- `未处理`

数据文件：

- `release_data/foreign_master_database_v2.csv`（总库）
- `release_data/foreign_strict_shanghai_candidate_pool_v2.csv`（候选池）
- `release_data/foreign_strict_shanghai_filtered_v2.csv`（当前筛选输出）

## 6. 常见问题

- 出现 `WAF Blocked`：
  - 先暂停脚本，换网络（手机热点），重开 CDP Chrome 后再跑。
- 长时间无增长：
  - 检查是否还在处理大量“岗位已下线”历史链接。
  - 适当降低 `RETRY_BATCH_SIZE`，提高稳定性。
