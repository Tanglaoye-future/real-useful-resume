"""
ResuMiner 统一日志模块

基于 logging.yaml 配置初始化，全项目使用统一的日志实例
"""

import logging
import logging.config
import os
import yaml
from pathlib import Path
from typing import Optional


def setup_logging(config_path: Optional[str] = None):
    """
    设置日志配置
    
    Args:
        config_path: 日志配置文件路径，默认使用 conf/logging.yaml
    """
    if config_path is None:
        # 从项目根目录查找
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / 'conf' / 'logging.yaml'
    
    if isinstance(config_path, Path):
        config_path = str(config_path)
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        # 确保日志目录存在
        for handler in config.get('handlers', {}).values():
            if 'filename' in handler:
                log_file = handler['filename']
                log_dir = os.path.dirname(log_file)
                if log_dir:
                    os.makedirs(log_dir, exist_ok=True)
        
        logging.config.dictConfig(config)
    else:
        # 使用默认配置
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称，建议使用模块路径如 'resuminer.crawler.job51'
    
    Returns:
        Logger 实例
    """
    return logging.getLogger(name)


class LoggerMixin:
    """日志混入类，为类提供统一的日志接口"""
    
    @property
    def logger(self) -> logging.Logger:
        """获取类对应的日志记录器"""
        return logging.getLogger(self.__class__.__module__ + '.' + self.__class__.__name__)


# 初始化日志（在导入时自动执行）
setup_logging()
