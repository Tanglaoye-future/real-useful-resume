#!/usr/bin/env python3
"""
启动爬虫依赖服务 (Redis + RPC)
"""

import subprocess
import sys
import time
import os
import signal
import atexit
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 服务进程列表
processes = []


def cleanup():
    """清理所有子进程"""
    print("\n正在停止所有服务...")
    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=5)
        except:
            try:
                p.kill()
            except:
                pass
    print("所有服务已停止")


atexit.register(cleanup)


def start_redis():
    """启动 Redis 服务"""
    print("=" * 60)
    print("正在启动 Redis 服务...")
    print("=" * 60)
    
    # 尝试使用 Docker
    try:
        # 检查 Docker 是否可用
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            # 启动 Redis 容器
            subprocess.run(['docker', 'run', '-d', '--name', 'spider_redis', 
                         '-p', '6379:6379', 'redis:alpine'], 
                        capture_output=True)
            print("✓ Redis Docker 容器已启动")
            return True
    except:
        pass
    
    # 尝试本地 Redis
    try:
        # 检查 redis-server 是否可用
        result = subprocess.run(['redis-server', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            # 启动 Redis 服务
            p = subprocess.Popen(['redis-server', '--port', '6379'], 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            processes.append(p)
            time.sleep(2)
            print("✓ Redis 本地服务已启动")
            return True
    except:
        pass
    
    print("✗ Redis 启动失败，请手动安装 Redis")
    print("  Windows: 下载 https://github.com/tporadowski/redis/releases")
    print("  或使用 Docker: docker run -d -p 6379:6379 redis:alpine")
    return False


def start_rpc():
    """启动 RPC 服务"""
    print("\n" + "=" * 60)
    print("正在启动 RPC 服务...")
    print("=" * 60)
    
    # 使用规范路径
    rpc_script = project_root / 'resuminer' / 'core' / 'crawler_engine' / 'rpc' / 'server.py'
    if not rpc_script.exists():
        print(f"✗ RPC 服务脚本不存在: {rpc_script}")
        return False
    
    try:
        # 在后台启动 RPC 服务
        p = subprocess.Popen([sys.executable, str(rpc_script)],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           cwd=str(project_root))
        processes.append(p)
        time.sleep(5)  # 等待服务启动
        print("✓ RPC 服务已启动 (端口 5600)")
        return True
    except Exception as e:
        print(f"✗ RPC 服务启动失败: {e}")
        return False


def check_services():
    """检查服务状态"""
    print("\n" + "=" * 60)
    print("检查服务状态...")
    print("=" * 60)
    
    # 检查 Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✓ Redis 服务正常")
        redis_ok = True
    except Exception as e:
        print(f"✗ Redis 服务异常: {e}")
        redis_ok = False
    
    # 检查 RPC
    try:
        import requests
        resp = requests.get('http://localhost:5600/health', timeout=3)
        if resp.status_code == 200:
            print("✓ RPC 服务正常")
            rpc_ok = True
        else:
            print(f"✗ RPC 服务返回异常状态: {resp.status_code}")
            rpc_ok = False
    except Exception as e:
        print(f"✗ RPC 服务异常: {e}")
        rpc_ok = False
    
    return redis_ok, rpc_ok


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║              ResuMiner 爬虫服务启动工具                      ║
║                                                              ║
║  本工具将启动:                                                ║
║    1. Redis 服务 (端口 6379)                                 ║
║    2. RPC 服务 (端口 5600)                                   ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # 启动 Redis
    redis_started = start_redis()
    if not redis_started:
        print("\n警告: Redis 未启动，爬虫可能无法正常工作")
    
    # 启动 RPC
    rpc_started = start_rpc()
    if not rpc_started:
        print("\n警告: RPC 未启动，爬虫可能无法正常工作")
    
    # 等待服务完全启动
    print("\n等待服务初始化...")
    time.sleep(5)
    
    # 检查服务状态
    redis_ok, rpc_ok = check_services()
    
    if redis_ok and rpc_ok:
        print("\n" + "=" * 60)
        print("✓ 所有服务已就绪，可以运行爬虫了！")
        print("=" * 60)
        print("\n按 Ctrl+C 停止所有服务")
        
        # 保持运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    else:
        print("\n" + "=" * 60)
        print("✗ 部分服务未就绪，请检查配置")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
