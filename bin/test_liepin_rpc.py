#!/usr/bin/env python3
"""
测试猎聘 RPC 接口
"""

import sys
import requests
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_liepin_rpc():
    """测试猎聘 RPC 接口"""
    url = "http://localhost:5600/invoke/liepin/search_jobs"
    payload = {
        "keyword": "实习",
        "pageNum": 1,
        "city": "020",
        "pageSize": 20
    }
    
    print("=" * 60)
    print("测试猎聘 RPC 接口")
    print("=" * 60)
    print()
    
    try:
        print(f"[1/3] 发送请求: {url}")
        print(f"    Payload: {json.dumps(payload, ensure_ascii=False)}")
        
        resp = requests.post(url, json=payload, timeout=60)
        print(f"    状态码: {resp.status_code}")
        print()
        
        if resp.status_code == 200:
            data = resp.json()
            print("[2/3] 解析响应:")
            print(f"    Status: {data.get('status')}")
            print()
            
            result = data.get("result", {})
            print("[3/3] 结果详情:")
            print(f"    Method: {result.get('method', 'N/A')}")
            print(f"    Total Count: {result.get('total_count', 0)}")
            print(f"    Message: {result.get('message', 'N/A')}")
            print()
            
            # 检查是否被拦截
            if result.get("blocked"):
                print(f"    ⚠️ 被拦截: {result.get('message')}")
                print(f"    Block Type: {result.get('block_type')}")
                print(f"    Title: {result.get('title')}")
                print(f"    URL: {result.get('url')}")
            else:
                # 显示职位数据
                job_data = result.get("data", {})
                job_list = job_data.get("jobCardList", []) or job_data.get("jobList", [])
                
                if job_list:
                    print(f"    ✓ 找到 {len(job_list)} 个职位")
                    print()
                    print("前3个职位:")
                    for i, job in enumerate(job_list[:3]):
                        print(f"    [{i+1}] {job.get('title', 'N/A')[:30]}... - {job.get('company', 'N/A')[:20]}...")
                else:
                    print("    ✗ 没有找到职位")
                    print(f"    Data keys: {list(job_data.keys())}")
        else:
            print(f"    ✗ 请求失败: {resp.text}")
            
    except Exception as e:
        print(f"    ✗ 错误: {e}")


if __name__ == "__main__":
    test_liepin_rpc()
