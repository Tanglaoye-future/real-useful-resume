# ResuMiner - 招聘数据爬虫系统

ResuMiner 是一个面向国内主流招聘平台（前程无忧51job、猎聘网、BOSS直聘）的招聘数据爬虫系统，具备多平台账号/cookies管理、请求加密/移动端逆向工程、分布式爬虫引擎、数据ETL清洗、数据落地导出、运行监控与日志追踪等核心能力。

## 🏗️ 项目结构

```
ResuMiner/
├── bin/                        # 统一入口脚本目录
│   ├── main.py                 # 项目主入口
│   ├── run_job51_full_v2.py    # 前程无忧爬虫
│   └── run_liepin_full.py      # 猎聘爬虫
├── conf/                       # 统一配置目录
│   ├── .env.example            # 环境变量示例
│   ├── logging.yaml            # 日志配置
│   └── platform/               # 平台专属配置
│       ├── job51.yaml
│       └── liepin.yaml
├── data/                       # 数据目录（git忽略）
│   ├── logs/                   # 日志文件
│   ├── output/                 # 输出数据
│   │   ├── job51/
│   │   └── liepin/
│   ├── temp/                   # 临时文件
│   └── cookies/                # Cookie文件
├── docs/                       # 项目文档
│   ├── README.md
│   └── LICENSE
├── resuminer/                  # 核心源码包
│   ├── common/                 # 通用工具层
│   │   ├── config_loader.py    # 统一配置加载
│   │   ├── logger.py           # 统一日志
│   │   └── exceptions.py       # 统一异常
│   ├── crawler/                # 爬虫业务层
│   │   ├── base/               # 爬虫基类
│   │   ├── job51/              # 前程无忧
│   │   └── liepin/             # 猎聘
│   ├── core/                   # 底层引擎层
│   │   ├── crawler_engine/     # 爬虫引擎
│   │   ├── crypto_engine/      # 加密引擎
│   │   └── mobile_reverse/     # 移动端逆向
│   └── etl/                    # 数据处理层
├── deploy/                     # 部署文件
│   ├── Dockerfile
│   └── docker-compose.yml
├── tests/                      # 测试目录
├── .gitignore                  # Git忽略规则
└── requirements.txt            # 依赖清单
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp conf/.env.example conf/.env
# 编辑 conf/.env 填写实际配置
```

### 3. 运行爬虫

```bash
# 使用统一入口
python bin/main.py crawl job51
python bin/main.py crawl liepin

# 或直接运行
python bin/run_job51_full_v2.py
python bin/run_liepin_full.py
```

## 📖 使用指南

### 统一入口

```bash
# 查看帮助
python bin/main.py --help

# 运行前程无忧爬虫
python bin/main.py crawl job51

# 运行猎聘爬虫
python bin/main.py crawl liepin

# 运行登录
python bin/main.py login liepin

# 启动服务
python bin/main.py start-services
```

### 配置管理

配置文件位于 `conf/` 目录：

- `conf/.env` - 环境变量（敏感信息，git忽略）
- `conf/.env.example` - 环境变量示例
- `conf/logging.yaml` - 日志配置
- `conf/platform/*.yaml` - 平台专属配置

### 数据输出

数据文件输出到 `data/output/` 目录：

- `data/output/job51/` - 前程无忧数据
- `data/output/liepin/` - 猎聘数据

## 🔧 核心模块

### 统一配置

```python
from resuminer import get_config

config = get_config()
redis_config = config.get_redis()
job51_config = config.get_platform('job51')
```

### 统一日志

```python
from resuminer import get_logger

logger = get_logger('my_module')
logger.info('Hello World')
```

### 爬虫基类

```python
from resuminer.crawler.base import BaseSpider, RedisScheduler

class MySpider(BaseSpider):
    def run(self):
        # 实现爬虫逻辑
        pass
```

## 📝 开发规范

1. **代码规范**: 遵循 PEP8
2. **导入规范**: 使用 `resuminer` 根包绝对导入
3. **日志规范**: 使用 `resuminer.common.logger`
4. **配置规范**: 使用 `resuminer.common.config_loader`
5. **异常规范**: 使用 `resuminer.common.exceptions`

## 📄 许可证

MIT License
