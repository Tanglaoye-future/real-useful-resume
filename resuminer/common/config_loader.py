"""
ResuMiner 统一配置加载模块

提供全局唯一配置实例，统一管理全局配置、环境变量、平台配置的加载
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigLoader:
    """统一配置加载器"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._config = {}
        self._load_all()
    
    def _load_all(self):
        """加载所有配置"""
        # 加载环境变量
        self._load_env()
        
        # 加载平台配置
        self._load_platform_configs()
        
        # 加载日志配置路径
        self._config['LOGGING_CONFIG'] = self._get_logging_config_path()
    
    def _load_env(self):
        """加载环境变量"""
        # 首先尝试加载 .env 文件
        env_path = self._get_project_root() / 'conf' / '.env'
        if env_path.exists():
            load_dotenv(env_path)
        
        # Redis 配置
        self._config['REDIS'] = {
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', 6379)),
            'db': int(os.getenv('REDIS_DB', 0))
        }
        
        # RPC 配置
        self._config['RPC'] = {
            'host': os.getenv('RPC_HOST', 'localhost'),
            'port': int(os.getenv('RPC_PORT', 5600))
        }
        
        # 日志配置
        self._config['LOG'] = {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'dir': os.getenv('LOG_DIR', './data/logs')
        }
        
        # 数据输出配置
        self._config['OUTPUT'] = {
            'dir': os.getenv('OUTPUT_DIR', './data/output'),
            'cookies_dir': os.getenv('COOKIES_DIR', './data/cookies'),
            'temp_dir': os.getenv('TEMP_DIR', './data/temp')
        }
        
        # 前程无忧配置
        self._config['JOB51'] = {
            'job_area': os.getenv('JOB51_JOB_AREA', '020000'),
            'campus_keywords': os.getenv('JOB51_CAMPUS_KEYWORDS', '实习,秋招').split(','),
            'intern_keywords': os.getenv('JOB51_INTERN_KEYWORDS', '实习,秋招').split(','),
            'fallback_keywords': os.getenv('JOB51_FALLBACK_KEYWORDS', '实习').split(','),
            'max_safety_pages': int(os.getenv('JOB51_MAX_SAFETY_PAGES', 500)),
            'empty_streak_limit': int(os.getenv('JOB51_EMPTY_STREAK_LIMIT', 5)),
            'page_size': int(os.getenv('JOB51_PAGE_SIZE', 20)),
            'target_min_count': int(os.getenv('JOB51_TARGET_MIN_COUNT', 5000))
        }
        
        # 猎聘配置
        self._config['LIEPIN'] = {
            'city_code': os.getenv('LIEPIN_CITY_CODE', '020'),
            'keywords': os.getenv('LIEPIN_KEYWORDS', '实习,秋招').split(','),
            'max_pages': int(os.getenv('LIEPIN_MAX_PAGES', 500)),
            'page_size': int(os.getenv('LIEPIN_PAGE_SIZE', 20)),
            'target_count': int(os.getenv('LIEPIN_TARGET_COUNT', 5000))
        }
        
        # Boss直聘配置
        self._config['BOSS'] = {
            'keywords': os.getenv('BOSS_KEYWORDS', '实习,秋招').split(','),
            'city': os.getenv('BOSS_CITY', '101020100')
        }
    
    def _load_platform_configs(self):
        """加载平台专属 YAML 配置"""
        platform_dir = self._get_project_root() / 'conf' / 'platform'
        
        if not platform_dir.exists():
            return
        
        for config_file in platform_dir.glob('*.yaml'):
            platform_name = config_file.stem
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    platform_config = yaml.safe_load(f)
                    if platform_config:
                        self._config[f'{platform_name.upper()}_YAML'] = platform_config
            except Exception as e:
                print(f"Warning: Failed to load platform config {config_file}: {e}")
    
    def _get_project_root(self) -> Path:
        """获取项目根目录"""
        # 从当前文件位置向上查找
        current_file = Path(__file__).resolve()
        # resuminer/common/config_loader.py -> 项目根目录
        return current_file.parent.parent.parent
    
    def _get_logging_config_path(self) -> str:
        """获取日志配置文件路径"""
        return str(self._get_project_root() / 'conf' / 'logging.yaml')
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self._config.get(key, default)
    
    def get_redis(self) -> Dict[str, Any]:
        """获取 Redis 配置"""
        return self._config.get('REDIS', {})
    
    def get_rpc(self) -> Dict[str, Any]:
        """获取 RPC 配置"""
        return self._config.get('RPC', {})
    
    def get_log(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self._config.get('LOG', {})
    
    def get_output(self) -> Dict[str, Any]:
        """获取输出配置"""
        return self._config.get('OUTPUT', {})
    
    def get_platform(self, platform: str) -> Dict[str, Any]:
        """获取平台配置"""
        return self._config.get(platform.upper(), {})
    
    def get_platform_yaml(self, platform: str) -> Dict[str, Any]:
        """获取平台 YAML 配置"""
        return self._config.get(f'{platform.upper()}_YAML', {})
    
    def get_project_root(self) -> Path:
        """获取项目根目录"""
        return self._get_project_root()
    
    def get_cookies_path(self, platform: str) -> str:
        """获取平台 cookies 文件路径"""
        cookies_dir = self.get_output().get('cookies_dir', './data/cookies')
        return os.path.join(cookies_dir, f'{platform}_cookies.json')
    
    def get_output_path(self, platform: str) -> str:
        """获取平台输出目录"""
        output_dir = self.get_output().get('dir', './data/output')
        return os.path.join(output_dir, platform)


# 全局配置实例
config = ConfigLoader()


def get_config() -> ConfigLoader:
    """获取全局配置实例"""
    return config
