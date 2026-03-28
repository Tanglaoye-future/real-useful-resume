#!/usr/bin/env python3
"""
ResuMiner 统一入口脚本

支持通过参数调度不同平台、不同任务的执行

Usage:
    python bin/main.py <command> [options]

Commands:
    crawl <platform>     运行指定平台的爬虫
    login <platform>     运行指定平台的登录脚本
    start-services       启动服务（Redis + RPC）
    etl                  运行数据处理

Examples:
    python bin/main.py crawl job51
    python bin/main.py crawl liepin
    python bin/main.py login liepin
    python bin/main.py start-services
"""

import argparse
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from resuminer.common import get_logger, setup_logging

# 设置日志
setup_logging()
logger = get_logger('resuminer.bin.main')


def run_crawl(platform: str, **kwargs):
    """运行爬虫"""
    logger.info(f"启动 {platform} 平台爬虫")
    
    if platform == 'job51':
        from run_job51_full_v2 import run_job51_full_v2
        return run_job51_full_v2()
    elif platform == 'liepin':
        from run_liepin_full import run_liepin_full
        return run_liepin_full()
    else:
        logger.error(f"不支持的平台: {platform}")
        return None


def run_login(platform: str, **kwargs):
    """运行登录脚本"""
    logger.info(f"启动 {platform} 平台登录")
    
    if platform == 'liepin':
        login_script = project_root / 'liepin_login.py'
        if login_script.exists():
            import subprocess
            result = subprocess.run([sys.executable, str(login_script)], capture_output=False)
            return result.returncode == 0
        else:
            logger.error(f"登录脚本不存在: {login_script}")
            return False
    else:
        logger.error(f"不支持的平台: {platform}")
        return False


def start_services(**kwargs):
    """启动服务"""
    logger.info("启动服务（Redis + RPC）")
    
    services_script = project_root / 'start_services.py'
    if services_script.exists():
        import subprocess
        result = subprocess.run([sys.executable, str(services_script)], capture_output=False)
        return result.returncode == 0
    else:
        logger.error(f"服务启动脚本不存在: {services_script}")
        return False


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description='ResuMiner 统一入口',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s crawl job51           # 运行前程无忧爬虫
  %(prog)s crawl liepin          # 运行猎聘爬虫
  %(prog)s login liepin          # 运行猎聘登录
  %(prog)s start-services        # 启动服务
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # crawl 命令
    crawl_parser = subparsers.add_parser('crawl', help='运行爬虫')
    crawl_parser.add_argument('platform', choices=['job51', 'liepin', 'boss'], help='平台名称')
    crawl_parser.add_argument('--keyword', '-k', help='关键词')
    crawl_parser.add_argument('--city', '-c', help='城市代码')
    
    # login 命令
    login_parser = subparsers.add_parser('login', help='运行登录')
    login_parser.add_argument('platform', choices=['liepin', 'boss'], help='平台名称')
    
    # start-services 命令
    subparsers.add_parser('start-services', help='启动服务（Redis + RPC）')
    
    # etl 命令
    etl_parser = subparsers.add_parser('etl', help='运行数据处理')
    etl_parser.add_argument('--input', '-i', help='输入文件')
    etl_parser.add_argument('--output', '-o', help='输出文件')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'crawl':
            result = run_crawl(args.platform)
            if result:
                logger.info(f"爬虫执行成功，获取 {len(result)} 条数据")
                return 0
            else:
                logger.error("爬虫执行失败")
                return 1
                
        elif args.command == 'login':
            success = run_login(args.platform)
            return 0 if success else 1
            
        elif args.command == 'start-services':
            success = start_services()
            return 0 if success else 1
            
        else:
            logger.error(f"未知命令: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        logger.info("用户中断执行")
        return 130
    except Exception as e:
        logger.error(f"执行异常: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
