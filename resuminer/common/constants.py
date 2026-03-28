"""
ResuMiner 统一路径管理常量

提供跨平台兼容的目录路径管理，自动创建所需目录
"""

import os

# 项目根目录（自动适配，禁止硬编码修改）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 全项目统一目录常量
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")
LOG_DIR = os.path.join(DATA_DIR, "logs")
COOKIES_DIR = os.path.join(DATA_DIR, "cookies")
TEMP_DIR = os.path.join(DATA_DIR, "temp")

# 各平台专属输出目录常量
JOB51_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "job51")
LIEPIN_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "liepin")
BOSS_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "boss")

# 爬虫日志目录
CRAWLER_LOG_DIR = os.path.join(LOG_DIR, "crawler")

# 自动创建所有目录，不存在则新建，已存在则不报错
for dir_path in [
    DATA_DIR, OUTPUT_DIR, LOG_DIR, COOKIES_DIR, TEMP_DIR,
    JOB51_OUTPUT_DIR, LIEPIN_OUTPUT_DIR, BOSS_OUTPUT_DIR,
    CRAWLER_LOG_DIR
]:
    os.makedirs(dir_path, exist_ok=True)

# 配置文件路径
CONF_DIR = os.path.join(PROJECT_ROOT, "conf")
ENV_FILE = os.path.join(CONF_DIR, ".env")
ENV_EXAMPLE_FILE = os.path.join(CONF_DIR, ".env.example")
GLOBAL_CONFIG_FILE = os.path.join(CONF_DIR, "global_config.py")
PLATFORM_CONF_DIR = os.path.join(CONF_DIR, "platform")

# 平台配置文件路径
JOB51_CONF_FILE = os.path.join(PLATFORM_CONF_DIR, "job51.yaml")
LIEPIN_CONF_FILE = os.path.join(PLATFORM_CONF_DIR, "liepin.yaml")
BOSS_CONF_FILE = os.path.join(PLATFORM_CONF_DIR, "boss.yaml")
