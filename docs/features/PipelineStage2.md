# Pipeline Stage 2 — 简历 → JD 推荐

> Stage 1-3（Stage1 文档）已经把所有 JD 标准化到 `data/unified/jobs.parquet`。
> Stage 2 在它之上加 **embedding 索引 + 简历输入 + 打分 + 报告**。

## 1. 模块图

```
config/preferences.yaml ─┐
                         ├─► matcher.score (硬过滤+5维打分)
data/resumes/*.md ───────┘                │
            │                             │
            ▼                             ▼
   matcher.resume_loader              matcher.render → outputs/recommendations/<UTC>/
            │                             ▲
            ▼                             │
   bge-small-zh encode ─► resume_vec ─────┤
                                          │
data/unified/jobs.parquet ─► pipeline.build_index ─► index/jobs_embeddings.npz
                                                  └► index/jobs_meta.parquet
```

每个箭头方向都是单向数据流。Stage 1 的 `jobs.parquet` 是 SSOT，Stage 2 只读不写。

## 2. 文件清单

| Path | 角色 |
|---|---|
| `pipeline/build_index.py` | 离线一次性：jobs.parquet → 向量 npz + slim meta |
| `matcher/resume_loader.py` | 读 PDF / MD / DOCX / TXT → 纯文本 |
| `matcher/score.py` | 硬过滤 + 5 维加权打分（语义/关键词/标题/城市/类型） |
| `matcher/render.py` | Top-N → CSV + Markdown + HTML |
| `scripts/recommend_jobs.py` | 主入口，串起所有上面的步骤 |
| `config/preferences.example.yaml` | 偏好模板（git tracked） |
| `data/resumes/example_resume.md` | 简历模板（git tracked） |

## 3. 依赖

```text
sentence-transformers >= 2.2.0
pdfplumber            >= 0.11.0
python-docx           >= 1.1.0
pyyaml                >= 6.0
pandas, numpy, pyarrow, pydantic   # 已在 Stage 1
```

## 4. 配置：`config/preferences.yaml`

设计原则（CLAUDE.md "trace every config field end to end"）：每个字段都有且仅有一个消费者。

| 字段 | 消费者 | 写错的后果 |
|---|---|---|
| `resume.path` | `scripts/recommend_jobs.py` | 文件找不到，立即报错 |
| `resume.parse_min_chars` | `matcher/resume_loader.py` | 简历过短被拒（多半是图片型 PDF） |
| `filters.target_cities` | `matcher/score.py:apply_filters` | 不在列表的 JD 被丢 |
| `filters.target_job_types` | 同上 | 类型不符的 JD 被丢 |
| `filters.exclude_keywords` | 同上 | 命中关键词的 JD 被丢（标题+正文，词边界感知） |
| `filters.exclude_companies` | 同上 | 公司名精确匹配则丢 |
| `filters.min_jd_chars` | 同上 | 太短的 JD 被丢；**默认 100**，不要设 200，否则会刷掉整批 liepin（详见 §11） |
| `scoring.weights.*` | `matcher/score.py:final_score` | 排序变化（自动归一化为和=1） |
| `scoring.target_titles` | `matcher/score.py:title_score` | 命中加分（词边界） |
| `scoring.must_have_keywords` | `matcher/score.py:keyword_score` | 命中加 1.0 |
| `scoring.nice_to_have_keywords` | 同上 | 命中加 0.5 |
| `scoring.big_tech_companies` | `matcher/score.py:is_big_tech` | 列表：所有触发软降权的公司别名（substring，case-insensitive） |
| `scoring.big_tech_penalty` | `matcher/score.py:final_score` | 大厂行的 final 分数乘以这个系数；范围 [0, 1]，1.0 关闭，0.0 完全屏蔽 |
| `output.top_n` | `scripts/recommend_jobs.py` | Top-N 行数 |
| `output.formats` | `matcher/render.py` | 哪些渲染器跑 |

> 启动时若 `preferences.yaml` 不存在，会自动 fallback 到 `preferences.example.yaml`。

## 5. 打分公式

所有分量都被规范到 `[0, 1]`：

```
base  = w_sem * semantic
      + w_kw  * keyword
      + w_ti  * title
      + w_lo  * location
      + w_jt  * job_type

final = base * (big_tech_penalty if is_big_tech(company) else 1.0)
```

其中：

- **semantic** = `(cosine(resume_vec, jd_vec) + 1) / 2`，bge 已 L2 归一化
- **keyword** = `(Σ must * 1.0 + Σ nice * 0.5) / max_possible`
- **title** = 1.0 if any `target_titles` 命中标题 else 0.0
- **location** = 1.0 if `city ∈ target_cities` else 0.0
- **job_type** = 1.0 if `job_type ∈ target_job_types` else 0.0
- **is_big_tech**：公司名（lowercase）是否包含 `scoring.big_tech_companies`
  里的任意别名（substring）。`big_tech_penalty=0.3` 表示大厂的最终分被乘 0.3，
  让中小企更容易上 Top-N，但大厂仍可见（不是 hard filter）。详见 §11。

**词边界感知**：纯 ASCII 关键词（如 `AI`, `R`, `SQL`）用单词边界匹配，避免误中
`Associate`, `Researcher`, `MySQL` 等子串。中文关键词走 plain `str.contains`。

## 6. 怎么跑

```powershell
# 0) 一次性：装依赖
py -3.11 -m pip install -r requirements.txt

# 1) 一次性（或 jobs.parquet 重建后）：构建索引（首次会下载 ~100MB bge 模型）
py -3.11 pipeline/build_index.py

# 2) 把 example 偏好复制成你自己的，然后改
copy config\preferences.example.yaml config\preferences.yaml

# 3) 替换简历
#    把你的简历放到 data/resumes/，扩展名支持 .md / .pdf / .docx / .txt
#    在 preferences.yaml 里把 resume.path 指过去

# 4) 出推荐
py -3.11 scripts/recommend_jobs.py
# 或者临时覆盖：
py -3.11 scripts/recommend_jobs.py --resume data/resumes/my.pdf --top 30
```

输出到 `outputs/recommendations/<UTC_TS>/`：

- `recommendations.csv`  —— Excel/数据分析用
- `recommendations.md`   —— GitHub/IDE 直接看
- `recommendations.html` —— 浏览器可读，可点击 URL 跳转
- `run_meta.json`        —— 这次运行的所有元信息（时间、模型、过滤统计、权重、指纹）

**永不覆盖**：每次运行都是新文件夹（CLAUDE.md "append-only result storage"）。

## 7. 验证结果（最近一次）

| 指标 | 值 |
|---|---|
| jobs.parquet 行数 | 456 |
| 向量维度 | 512（`BAAI/bge-small-zh-v1.5`） |
| 索引文件 | ~930 KB (`index/jobs_embeddings.npz`) |
| 编码速度 | ~5 jobs/s on CPU（首次约 90s） |
| 硬过滤 | 456 → 294（drop city=25, type=8, short=19, kw=110） |
| 打分耗时 | 136 ms |
| 大厂池子 | 1 行（百度·上海·网络安全工程师） |
| Top-20 质量（example 简历） | 上交大 AI 应用支持、维亚生物 AI 算法、地平线智驾 RL、中证指数数据分析、Amazon BA/SDE Intern 等 |

33/33 matcher tests + 36/36 pipeline tests = **69/69 pass**
(`pytest tests/`).

## 8. Reproducibility 保证

- 索引 npz 里存了 `model_name` 和 `fingerprint = sha1(sorted job_ids + jd_text lengths)`。
- 推荐运行时会把索引里的 `job_id` 集合和 `jobs_meta.parquet` 比对，对不上就报错让你重建索引。
- `outputs/recommendations/<UTC_TS>/run_meta.json` 里记录了：模型名、指纹、权重、过滤统计、输入简历路径、时间戳。

把这四样固定下来，任何一次推荐都能精确复现。

## 9. 已知问题 / 后续改进

| # | 现象 | 根因 | 建议方向 |
|---|---|---|---|
| ~~1~~ | ~~yingjiesheng `title==company`~~ | 已修复：`adapter_yingjiesheng` 检测到时从 `jd_text` 第一行 fallback。详见 Stage 1 文档 |
| ~~2~~ | ~~Amazon 同 JD 不去重~~ | 已修复：`pipeline.dedupe` 加了 `(company, jd_text[:500])` 第三层 hash。详见 Stage 1 文档 |
| 3 | `salary_raw` 大量为空（official 来源完全没数据） | 源数据本身没有 | 不做硬过滤；薪资改由用户在 prefs 里描述偏好 |
| 4 | seniority 多为 unknown | Stage 1 未做实体抽取 | Stage 3 加规则/NER 提升 seniority 准确率 |
| 5 | 多语言简历未测 | 只跑了中文 | 测纯英文简历，必要时换 `BAAI/bge-base-en-v1.5` |
| 6 | bge-small-zh 对长 JD（>512 token）会截断 | 模型固有限制 | 大 JD 走滑窗 mean-pool，或换 `bge-m3`（更长上下文） |
| 7 | 部分 liepin 大厂仍因 JD < 100 字符进不了池 | 列表页 API 返回的 JD 太短 | 等爬虫加上详情页 enrichment；之前不要把 `min_jd_chars` 调更低 |

## 11. 大厂软降权 (big-tech soft-deprioritization)

**问题**：上海实习池子里互联网八大厂（BAT + TMD + 京东 + 网易）数量虽不多但
品牌势能大，容易在语义打分上挤占 Top-N 位置，把更值得申请的中小企推到后面。

**设计**（CLAUDE.md "trace every config field end to end"）：

| 谁产生 | 谁读取 | 谁强制 | 写错的后果 |
|---|---|---|---|
| 用户在 `config/preferences.yaml` 里写 `scoring.big_tech_companies` 列表 | `matcher/score.py:is_big_tech` | `matcher/score.py:final_score`：`final = base * penalty` 仅对大厂行 | 列表为空 → 全部 `False`，penalty 变 no-op；penalty 不在 [0,1] → 自动 clamp |

匹配逻辑：公司名 lowercase 后做 substring 比对（`"阿里巴巴"` 匹配 `"阿里巴巴（中国）有限公司"`，`"腾讯"` 匹配 `"腾讯科技 (上海)"`）。完整别名见
`config/preferences.example.yaml`。

**为什么是软降权而不是硬过滤**：用户明确要求"看得到但排靠后"。硬过滤的话整批
大厂直接消失，反而损失了"知道有大厂在招但优先看其他"这层信息。`penalty=0.3`
让大厂从 base rank 39 推到 final rank 294（验证案例：百度·上海·网络安全工程师），
仍然在报告里可见。

**渲染**：`matcher/render.py` 在 Markdown / HTML 里给大厂行打 `大厂·已软降 ×0.30`
标记，并显示 `base` 分（penalty 前）和 `final` 分（penalty 后）的对比，方便
用户判断 penalty 是否合理。CSV 多出 `is_big_tech` 和 `base` 两列。

**关键的隐性依赖**：`scoring.big_tech_penalty` 只在 hard filter 之后生效。
如果 `filters.min_jd_chars` 设得过高把所有大厂都先刷掉了，penalty 就没有作用
对象，效果就是"大厂消失了"。Liepin 来源 JD 短（80~150 字符），
`min_jd_chars` 必须 ≤ 实际 JD 长度才能让 penalty 真正介入。
默认 100 是经过验证的折中值。

## 10. 与 Stage 1 的接口

Stage 2 只通过这两个文件依赖 Stage 1：

- 读 `data/unified/jobs.parquet`（schema 见 `pipeline/schema.py`）
- 读 `data/unified/jobs.jsonl`（可选，仅用于人工 sanity check）

任何时候 Stage 1 重新 ingest，**都必须重跑 `pipeline/build_index.py`**，否则 fingerprint 校验会拒绝运行。
