#!/usr/bin/env python3
"""测试数据加载 - 检查编码问题"""

import csv
from pathlib import Path

# 加载CSV文件
shanghai_file = Path('c:/Users/Lenovo/projects/ResuMiner_main/release_data/internship_shanghai_latest.csv')

# 先读取原始字节
with open(shanghai_file, 'rb') as f:
    raw = f.read(200)
    print(f"原始字节: {raw[:100]}")
    print(f"是否有BOM: {raw[:3] == b'\\xef\\xbb\\xbf'}")

# 尝试不同的编码
for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']:
    try:
        with open(shanghai_file, 'r', encoding=encoding) as f:
            reader = csv.DictReader(f)
            rows = list(reader)[:3]
            print(f"\n{encoding}:")
            for i, row in enumerate(rows, 1):
                company = row.get('company', 'N/A')
                name = row.get('name', 'N/A')
                print(f"  {i}. 公司: '{company}', 岗位: '{name}'")
                # 打印实际键
                if i == 1:
                    print(f"     键: {list(row.keys())}")
    except Exception as e:
        print(f"{encoding}: 错误 - {e}")
