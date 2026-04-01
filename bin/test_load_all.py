#!/usr/bin/env python3
"""测试加载所有官网数据"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bin.run_with_existing_data import load_official_jobs

jobs = load_official_jobs()
print(f"\n{'='*80}")
print(f"总计加载: {len(jobs)} 条官网岗位")
print(f"{'='*80}")
