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
    env["ONLY_LIEPIN"] = "0"           # crawl both 51job + liepin (RPC handles captcha)
    env["USE_EXISTING_RAW"] = "0"     # actually crawl fresh pages each cycle
    env["USE_ALL_LOCAL_RAW"] = "1"    # aggregate all historical snapshots for coarse filter
    env["USE_MERGED_POOL"] = "1"
    env["PROCESS_RETRY_ONLY"] = "0"
    env["PAGES_PER_SOURCE"] = str(random.choice([10, 15, 20]))  # ~10-20 pages/keyword
    env["RETRY_BATCH_SIZE"] = str(random.choice([50, 80, 100]))
    env["DETAIL_REQ_TIMEOUT"] = str(random.choice([10, 12, 15]))
    env["DETAIL_WORKERS"] = str(random.choice([2, 3]))
    env["JOB51_RPC_TIMEOUT"] = "8"
    env["LIEPIN_RPC_TIMEOUT"] = "30"  # XHR interception needs time for page load + networkidle
    env["RPC_DETAIL_TIMEOUT"] = "45"

    log(
        f"cycle={cycle} start "
        f"PAGES_PER_SOURCE={env['PAGES_PER_SOURCE']} RETRY_BATCH_SIZE={env['RETRY_BATCH_SIZE']}"
    )
    cmd = [sys.executable, str(ROOT / "scripts" / "foreign_pipeline_v2.py")]
    # shorter cycle timeout for visible progress
    cycle_timeout = int(os.getenv("CYCLE_TIMEOUT_SEC", "2400"))  # 40 min: list crawl + detail fetch
    proc = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=cycle_timeout)
    tail = "\n".join((proc.stdout or "").splitlines()[-14:])
    log(f"cycle={cycle} exit={proc.returncode}\n{tail}")
    if proc.stderr:
        err_tail = "\n".join(proc.stderr.splitlines()[-12:])
        log(f"cycle={cycle} stderr_tail:\n{err_tail}")


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
        # jitter sleep to reduce anti-bot risk
        sleep_s = random.randint(25, 75)
        log(f"sleep {sleep_s}s")
        time.sleep(sleep_s)
    log("overnight done")


if __name__ == "__main__":
    main()
