import os
import random
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
RUN_LOG = LOG_DIR / f"overnight_autorun_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"


def log(msg: str):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(RUN_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def read_master_stats():
    p = ROOT / "release_data" / "foreign_master_database_v2.csv"
    if not p.exists():
        return {"master": 0, "clear": 0, "unclear": 0, "unprocessed": 0}
    df = pd.read_csv(p).fillna("")
    return {
        "master": len(df),
        "clear": int((df["jd_visibility"] == "清晰可见").sum()) if "jd_visibility" in df.columns else 0,
        "unclear": int((df["jd_visibility"] == "不清晰").sum()) if "jd_visibility" in df.columns else 0,
        "unprocessed": int((df["detail_status"] == "未处理").sum()) if "detail_status" in df.columns else 0,
    }


def run_one_cycle(cycle: int):
    env = os.environ.copy()
    env["ONLY_LIEPIN"] = os.getenv("ONLY_LIEPIN", "1")  # 目前主攻猎聘全量，默认绕开51job的风控
    env["USE_EXISTING_RAW"] = os.getenv("USE_EXISTING_RAW", "0")  # actually crawl fresh pages each cycle
    env["USE_ALL_LOCAL_RAW"] = os.getenv("USE_ALL_LOCAL_RAW", "1")  # aggregate historical snapshots
    env["USE_MERGED_POOL"] = os.getenv("USE_MERGED_POOL", "1")
    env["PROCESS_RETRY_ONLY"] = os.getenv("PROCESS_RETRY_ONLY", "0")
    env["USE_CDP"] = os.getenv("USE_CDP", "1")  # Enable CDP bypass for Liepin details
    
    # 修正变量名为 MAX_PAGES (v2 管道使用的名称)，同时由于长尾矩阵有 30 个词
    # 每一轮爬取每个词 2-4 页即可（即一轮爬取 60-120 页列表），防止单轮运行时间过长
    env["MAX_PAGES"] = os.getenv("MAX_PAGES", str(random.choice([2, 3, 4])))
    
    env["RETRY_BATCH_SIZE"] = os.getenv("RETRY_BATCH_SIZE", str(random.choice([50, 80, 100])))
    env["DETAIL_REQ_TIMEOUT"] = os.getenv("DETAIL_REQ_TIMEOUT", str(random.choice([10, 12, 15])))
    env["DETAIL_WORKERS"] = "1"  # 降并发为单线程，最大程度降低封控概率
    env["JOB51_RPC_TIMEOUT"] = "8"
    env["LIEPIN_RPC_TIMEOUT"] = "30"  # XHR interception needs time for page load + networkidle
    env["RPC_DETAIL_TIMEOUT"] = "45"
    
    # 强制解除单次测试 300 条的限制，进入无限过夜模式
    if "TEST_MAX_ROWS" in env:
        del env["TEST_MAX_ROWS"]

    log(
        f"cycle={cycle} start "
        f"MAX_PAGES={env['MAX_PAGES']} RETRY_BATCH_SIZE={env['RETRY_BATCH_SIZE']}"
    )
    cmd = [sys.executable, str(ROOT / "scripts" / "foreign_pipeline_v2.py")]
    # shorter cycle timeout for visible progress
    # [Fix] 增加循环超时时间，从40分钟增加到120分钟(7200秒)，因为长尾词全量抓取及详情页下载很慢
    cycle_timeout = int(os.getenv("CYCLE_TIMEOUT_SEC", "7200"))  # 120 min: list crawl + detail fetch
    
    # 移除 capture_output=True, 让子进程直接输出到终端，让用户看到实时进度
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), env=env, timeout=cycle_timeout)
        log(f"cycle={cycle} exit={proc.returncode}")
    except subprocess.TimeoutExpired:
        log(f"cycle={cycle} timeout_expired")
        raise


def main():
    # default 8 hours; user can override
    hours = float(os.getenv("OVERNIGHT_HOURS", "8"))
    deadline = time.time() + hours * 3600
    cycle = 1
    log(f"overnight start hours={hours}")
    max_cycles = int(os.getenv("MAX_CYCLES", "0"))  # 0 means unlimited within deadline
    while time.time() < deadline:
        if max_cycles > 0 and cycle > max_cycles:
            log(f"reach MAX_CYCLES={max_cycles}, stop")
            break
        before = read_master_stats()
        log(f"before stats={before}")
        try:
            run_one_cycle(cycle)
        except subprocess.TimeoutExpired:
            log(f"cycle={cycle} timeout_expired")
        except Exception as e:
            log(f"cycle={cycle} exception={type(e).__name__}:{e}")
        after = read_master_stats()
        log(f"after stats={after}")
        cycle += 1
        # Sleep between cycles to avoid ban
        sleep_sec = random.uniform(60, 180)  # 延长大批次之间的休息时间 1-3分钟
        log(f"sleep {sleep_sec:.1f}s")
        time.sleep(sleep_sec)
    log("overnight done")


if __name__ == "__main__":
    main()
