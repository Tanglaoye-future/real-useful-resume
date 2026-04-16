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
- **数据管道处理**: 完整的数据处理流程（加载→标准化→去重→硬性过滤→高价值筛选）
- **高价值岗位筛选 V2**: 基于公司分级（S/A/B/C四级）、企业类型（互联网大厂/外企/独角兽/国企）、岗位含金量的多维度评估
- **智能语义匹配**: 基于BERT的语义相似度计算，精准匹配岗位与简历
- **硬性条件过滤**: 支持地点、学历、经验等硬性条件筛选
- **投递策略生成**: 自动生成投递优先级和定制化建议
- **数据去重合并**: 智能去重算法，避免重复岗位

---

## 🚀 快速开始

### 交接运行手册（推荐）

如果是同学接手并需要快速跑“只猎聘 + 全量优先”模式，请先看：

- [RUNBOOK_LIEPIN.md](./RUNBOOK_LIEPIN.md)

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

### 配置简历

将你的简历保存为JSON格式，放置在项目根目录或 `assets/resume/uploads/` 目录下：

```json
{
  "name": "你的名字",
  "basic_info": {
    "email": "your.email@example.com",
    "phone": "138xxxxxxxxx"
  },
  "skills": ["Python", "数据分析", "产品经理"],
  "education": "本科",
  "projects": [...],
  "work_experience": [...]
}
```

### 运行完整流程

```bash
# 1. 运行数据管道（数据处理流程）
python run_data_pipeline.py

# 2. 运行简历匹配 V2
python run_matching_v2.py

# 3. 或使用整合流水线
python bin/run_integrated_pipeline.py
```

### 查看生成的报告

```bash
# 查看数据管道报告
cat data/processed/pipeline_report_*.md

# 查看匹配报告
cat data/output/matcher/match_report_*.json
```

---

## 📁 项目结构

```
ResuMiner/
├── bin/                          # 可执行脚本
│   ├── run_integrated_pipeline.py # 整合流水线
│   ├── run_full_pipeline.py      # 完整流程脚本
│   └── run_with_existing_data.py # 使用已有数据运行匹配
├── core/                         # 核心模块
│   ├── data_pipeline.py          # 数据管道
│   ├── crawler_engine/           # 爬虫引擎
│   │   ├── spiders/              # 爬虫实现
│   │   ├── scheduler.py          # Redis调度器
│   │   ├── rpc/                  # RPC服务
│   │   └── base_spider.py        # 爬虫基类
│   └── crypto_engine/            # 加密引擎
├── matcher/                      # 匹配系统
│   ├── core/                     # 核心匹配逻辑
│   ├── filters/                  # 过滤器
│   │   ├── hard_filter.py        # 硬性条件过滤
│   │   └── value_filter.py       # 高价值岗位筛选 V2
│   ├── generator/                # 生成器
│   ├── report/                   # 报告生成
│   ├── scoring/                  # 评分系统
│   └── strategy/                 # 策略模块
├── crawlers/                     # 官网爬虫实现
│   └── official/                 # CDP官网爬虫
├── data/                         # 数据目录
│   ├── processed/                # 数据管道输出
│   │   ├── high_value_jobs_*.json    # 高价值岗位
│   │   ├── medium_value_jobs_*.json  # 中价值岗位
│   │   └── pipeline_report_*.md      # 处理报告
│   └── output/                   # 输出数据
├── run_data_pipeline.py          # 数据管道运行脚本
├── run_matching_v2.py            # 简历匹配 V2
├── requirements.txt              # 依赖配置
└── README.md                     # 项目说明
```

---

## 📊 数据管道使用指南

### 快速开始

```bash
# 运行数据管道（使用默认配置）
python run_data_pipeline.py

# 使用自定义配置
python run_data_pipeline.py --mode custom
```

### 高价值筛选 V2 配置

```python
from matcher.filters.value_filter import ValueFilterConfig

config = ValueFilterConfig(
    # 公司维度权重50%，岗位维度权重50%
    company_weight=0.5,
    job_weight=0.5,
    # 最低总分要求
    min_total_score=60.0,
    # 高价值岗位阈值
    high_value_threshold=75.0,
    # 高价值岗位类型
    high_value_job_types=[
        "产品经理", "产品实习", "策略产品", "数据产品",
        "增长产品", "商业化产品", "AI产品"
    ]
)
```

### 公司分级说明（V2）

| 等级 | 名称 | 说明 | 示例 |
|------|------|------|------|
| S级 | 顶级 | 互联网大厂/世界500强外企 | 字节跳动、腾讯、阿里巴巴、百度、Google、Microsoft |
| A级 | 头部 | 行业头部企业/独角兽/头部金融科技 | 美团、拼多多、京东、网易、快手、滴滴、蚂蚁集团 |
| B级 | 中腰部 | 中厂/准独角兽/地方国企 | B站、小红书、小米、携程、米哈游 |
| C级 | 补充赛道 | 小而美初创/优质中小企 | 其他优质公司 |

### 企业类型评估

系统支持以下企业类型的加分项评估：

- **互联网大厂**: 核心业务部门、技术栈匹配度
- **外企**: 落户支持、培训体系、全球轮岗机会
- **独角兽**: 核心业务岗、期权激励、赛道前景
- **国企**: 稳定编制、落户保障、福利完善

### 输出文件说明

运行数据管道后会生成以下文件：

```
data/processed/
├── high_value_jobs_*.json      # 高价值岗位（优先投递）
├── medium_value_jobs_*.json    # 中价值岗位（备选投递）
├── low_value_jobs_*.json       # 低价值岗位
├── filtered_jobs_*.json        # 已过滤岗位（不推荐）
└── pipeline_report_*.md        # 处理报告
```

---

## 🎯 简历匹配 V2

### 运行匹配

```bash
python run_matching_v2.py
```

### 匹配流程

1. **加载简历**: 自动扫描 `assets/resume/uploads/` 目录
2. **加载高价值岗位**: 使用数据管道V2输出的高价值/中价值岗位
3. **关键词匹配**: 基于简历技能与岗位描述的关键词匹配
4. **综合评分**: 结合匹配度和高价值评分进行排序
5. **生成报告**: 输出Top推荐岗位和统计信息

---

## 📊 数据流程

### 数据管道流程

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   官网爬虫数据   │     │  第三方平台数据  │     │   其他数据源    │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────┬───────────┴───────────┬───────────┘
                     ▼                       ▼
            ┌─────────────────┐     ┌─────────────────┐
            │   数据加载      │────►│   数据标准化    │
            └─────────────────┘     └─────────────────┘
                                                  │
                                                  ▼
                                         ┌─────────────────┐
                                         │    去重处理     │
                                         └────────┬────────┘
                                                  │
                                                  ▼
                                         ┌─────────────────┐
                                         │   硬性条件过滤   │
                                         │ • 地点筛选      │
                                         │ • 学历要求      │
                                         │ • 黑名单过滤    │
                                         └────────┬────────┘
                                                  │
                                                  ▼
                                         ┌─────────────────┐
                                         │  高价值筛选 V2  │
                                         │ • 公司分级      │
                                         │ • 企业类型      │
                                         │ • 岗位含金量    │
                                         └────────┬────────┘
                    ┌─────────────────────────────┼─────────────────────────────┐
                    │                             │                             │
                    ▼                             ▼                             ▼
           ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
           │   高价值岗位     │          │   中价值岗位     │          │   已过滤岗位     │
           └─────────────────┘          └─────────────────┘          └─────────────────┘
```

---

## 🕷️ 爬虫架构

### 官网CDP爬虫

使用Playwright连接Chrome DevTools Protocol (CDP) 进行高级爬虫拦截：

```bash
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
```

支持平台：51job（前程无忧）、猎聘

---

## ⚙️ 环境变量配置

```bash
# 51job爬虫配置
export JOB51_JOB_AREA="020000"           # 上海
export JOB51_CAMPUS_KEYWORDS="实习"
export JOB51_MAX_SAFETY_PAGES="100"

# 猎聘爬虫配置
export LIEPIN_KEYWORD="实习"
export LIEPIN_CITY="020"                 # 上海
export LIEPIN_MAX_PAGES="100"

# Redis配置（可选）
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
```

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

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

---

<p align="center">
  <b>Made with ❤️ by 唐圣昕 & 张靖恒</b>
</p>
