import pandas as pd
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

master_path = ROOT / "release_data" / "foreign_master_database_v2.csv"
filtered_path = ROOT / "release_data" / "foreign_strict_shanghai_filtered_v2.csv"

if master_path.exists():
    df = pd.read_csv(master_path)
    print(f"Master 总记录数: {len(df)}")
    print(f"状态统计: \n{df['detail_status'].value_counts() if 'detail_status' in df.columns else '无状态列'}")
else:
    print("Master 数据库不存在")

if filtered_path.exists():
    df_f = pd.read_csv(filtered_path)
    print(f"\n优质过滤池 (Filtered) 记录数: {len(df_f)}")
    if len(df_f) > 0:
        print(df_f[['company_name', 'job_name', '总分']].head())
else:
    print("\n优质过滤池 (Filtered) 不存在")
