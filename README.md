# ResuMiner - 智能岗位匹配系统

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue.svg" alt="Python 3.11">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</p>

<p align="center">
  <b>基于AI的智能岗位匹配与投递策略生成系统</b>
</p>

---

## 📖 项目简介

ResuMiner 是一个智能化的岗位匹配系统，通过整合多源招聘数据（官网爬虫 + 第三方平台），利用自然语言处理和机器学习技术，为求职者提供精准的岗位匹配推荐和个性化的投递策略。

### ✨ 核心功能

- **多源数据整合**: 支持官网爬虫（字节跳动、阿里、腾讯、美团等）+ 第三方平台（51job、猎聘）数据融合
- **智能语义匹配**: 基于BERT的语义相似度计算，精准匹配岗位与简历
- **硬性条件过滤**: 支持地点、学历、经验等硬性条件筛选
- **投递策略生成**: 自动生成投递优先级和定制化建议
- **数据去重合并**: 智能去重算法，避免重复岗位

---

## 🚀 快速开始

### 环境准备

1. **安装Python 3.11+**
2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **启动RPC服务**（用于第三方平台爬虫）
```bash
python core/crawler_engine/rpc/server.py
```

4. **启动Chrome浏览器**（用于官网CDP爬虫）
```bash
chrome.exe --remote-debugging-port=9222
```

### 运行完整流程

```bash
# 运行整合流水线（官网爬虫 + 第三方平台爬虫 + 匹配）
python bin/run_integrated_pipeline.py

# 或使用已有数据运行匹配
python bin/run_with_existing_data.py
```

### 查看生成的报告

```bash
# 查看投递报告
cat data/output/application_reports/application_report_*.md

# 查看匹配报告
cat data/output/matcher/match_report_*.md
```

---

## 📁 项目结构

```
ResuMiner_Integrated/
├── bin/                          # 可执行脚本
│   ├── run_integrated_pipeline.py # 整合流水线（爬虫+匹配）
│   ├── run_full_pipeline.py      # 完整流程脚本
│   ├── run_with_existing_data.py # 使用已有数据运行匹配
│   └── create_project_package.py # 工程包创建脚本
├── core/                         # 核心模块
│   ├── crawler_engine/           # 爬虫引擎
│   │   ├── spiders/              # 爬虫实现
│   │   │   ├── job51_v2.py       # 51job爬虫V2
│   │   │   ├── liepin_v6.py      # 猎聘爬虫V6
│   │   │   └── ...
│   │   ├── scheduler.py          # Redis调度器
│   │   ├── rpc/                  # RPC服务
│   │   │   └── server.py         # Playwright RPC服务器
│   │   └── base_spider.py        # 爬虫基类
│   └── crypto_engine/            # 加密引擎
│       └── platforms/            # 各平台加密模块
├── matcher/                      # 匹配系统
│   ├── core/                     # 核心匹配逻辑
│   ├── filters/                  # 过滤器
│   ├── generator/                # 生成器
│   ├── report/                   # 报告生成
│   ├── scoring/                  # 评分系统
│   └── strategy/                 # 策略模块
├── crawlers/                     # 官网爬虫实现
│   └── official/                 # CDP官网爬虫
│       ├── cdp_tencent.py        # 腾讯爬虫
│       ├── cdp_meituan.py        # 美团爬虫
│       ├── cdp_alibaba.py        # 阿里爬虫
│       ├── cdp_jd.py             # 京东爬虫
│       ├── cdp_kuaishou.py       # 快手爬虫
│       ├── cdp_bilibili.py       # 哔哩哔哩爬虫
│       └── cdp_bytedance.py      # 字节爬虫
├── parsers/                      # 数据解析器
├── rules/                        # 规则配置
├── data/                         # 数据目录
│   ├── output/                   # 输出数据
│   │   ├── application_reports/  # 投递报告
│   │   ├── matcher/              # 匹配报告
│   │   └── raw/                  # 原始数据
│   └── raw/                      # 爬虫原始数据
│       ├── 51job/                # 51job数据
│       ├── liepin/               # 猎聘数据
│       ├── official/             # 官网数据
│       └── merged/               # 合并数据
├── project_package/              # 工程包输出
├── logs/                         # 日志文件
├── requirements.txt              # 依赖配置
└── README.md                     # 项目说明
```

---

## 🔧 配置说明

### 简历配置

将你的简历保存为 `my_resume.json` 格式：

```json
{
  "basic_info": {
    "name": "你的名字",
    "email": "your.email@example.com",
    "phone": "138xxxxxxxxx"
  },
  "skills": ["Python", "Java", "Go", "Vue", "React"],
  "work_years": 1,
  "education": "本科",
  "projects": [...],
  "work_experience": [...]
}
```

### 环境变量配置

```bash
# 51job爬虫配置
export JOB51_JOB_AREA="020000"           # 上海
export JOB51_CAMPUS_KEYWORDS="实习"
export JOB51_MAX_SAFETY_PAGES="100"
export JOB51_THROTTLE_MIN_SECONDS="3"
export JOB51_THROTTLE_MAX_SECONDS="8"

# 猎聘爬虫配置
export LIEPIN_KEYWORD="实习"
export LIEPIN_CITY="020"                 # 上海
export LIEPIN_MAX_PAGES="100"
export LIEPIN_THROTTLE_MIN="5"
export LIEPIN_THROTTLE_MAX="10"

# Redis配置（可选）
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
```

---

## 📊 数据流程

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   官网爬虫数据   │     │  第三方平台数据  │     │    简历数据     │
│  (6,724条岗位)  │     │ (20,341条岗位)  │     │   (JSON格式)   │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────┬───────────┘                       │
                     ▼                                   │
            ┌─────────────────┐                          │
            │   数据合并去重   │                          │
            │  (27,065→6,787) │                          │
            └────────┬────────┘                          │
                     ▼                                   │
            ┌─────────────────┐                          │
            │  上海地点过滤   │◄─────────────────────────┤
            │  (6,787→5,330) │    硬性条件筛选          │
            └────────┬────────┘                          │
                     ▼                                   │
            ┌─────────────────┐     ┌─────────────────┐  │
            │  语义相似度计算  │◄────│   BERT模型编码   │  │
            │  (技能+语义+经验)│     │                 │  │
            └────────┬────────┘     └─────────────────┘  │
                     ▼                                   │
            ┌─────────────────┐                          │
            │   匹配结果排序   │                          │
            │   (Top 100)     │                          │
            └────────┬────────┘                          │
                     ▼                                   │
            ┌─────────────────┐     ┌─────────────────┐  │
            │  投递策略生成   │────►│   报告输出      │  │
            │  (优先级+建议)  │     │ (Markdown/JSON) │  │
            └─────────────────┘     └─────────────────┘  │
```

---

## 🕷️ 爬虫架构

### 官网CDP爬虫

使用Playwright连接Chrome DevTools Protocol (CDP) 进行高级爬虫拦截：

```python
# 启动Chrome（带CDP端口）
chrome.exe --remote-debugging-port=9222

# 爬虫通过CDP连接浏览器
browser = p.chromium.connect_over_cdp("http://localhost:9222")
```

支持公司：腾讯、美团、阿里巴巴、京东、快手、哔哩哔哩、字节跳动

### 第三方平台爬虫

使用RPC架构绕过反爬机制：

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Spider V2  │────►│  RPC Server │────►│  Playwright │
│  (Python)   │     │  (FastAPI)  │     │  (Browser)  │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Target     │
                    │  Website    │
                    └─────────────┘
```

支持平台：51job（前程无忧）、猎聘

---

## 👥 作者信息

### 唐圣昕
- **职责**: PRD文档撰写、第三方平台爬虫分支开发、DevOps支持
- **贡献**: 
  - 负责项目需求分析和产品文档编写
  - 开发51job、猎聘等第三方平台爬虫模块
  - 搭建CI/CD流程和部署方案
  - 数据整合与处理流程设计

### 张靖恒
- **职责**: 官网爬虫开发、爬虫技术栈确定、数据处理流程设计
- **贡献**:
  - 开发字节跳动、阿里、腾讯、美团等官网爬虫
  - 确定全项目爬虫技术栈（Playwright + CDP）
  - 设计数据清洗、去重、合并流程
  - 架构整体爬虫调度系统

---

## 📈 项目统计

- **官网数据**: 6,724 条岗位
  - 字节跳动、阿里、腾讯、美团、快手、哔哩哔哩、小红书、京东
- **第三方平台**: 20,341 条岗位
  - 51job: 3,924 条
  - 猎聘: 16,417 条
- **合并去重后**: 6,787 条
- **上海岗位**: 5,330 条（硬性过滤）
- **匹配精度**: Top 100 岗位，综合匹配度 60%+

---

## 🛠️ 技术栈

- **Python 3.11**: 核心开发语言
- **Playwright**: 浏览器自动化爬虫
- **CDP (Chrome DevTools Protocol)**: 高级爬虫拦截
- **FastAPI**: RPC服务框架
- **BERT/Sentence-Transformers**: 语义相似度计算
- **Pandas**: 数据处理与分析
- **Redis**: 任务调度与去重

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

---

## 🙏 致谢

感谢所有为本项目提供数据支持和技术建议的朋友们！

---

<p align="center">
  <b>Made with ❤️ by 唐圣昕 & 张靖恒</b>
</p>
