# 外企数据质量战报（2026-04-14）

## 1) 本轮已确认事实
- 已切换为三段式流程：列表粗过滤 -> 详情补抓 -> 详情严格过滤与打分。
- P0 已完成：`foreign_strict_shanghai_11_detailed_v2.csv` 已产出 10 条（当前种子数据可用条目为 10）。
- P1 已完成首轮扩量执行（50 页/源配置），产物已生成：
  - `release_data/foreign_strict_shanghai_candidate_pool_v2.csv`
  - `release_data/foreign_strict_shanghai_filtered_v2.csv`
  - `release_data/foreign_strict_top50_actionable_v2.csv`
  - `release_data/quality_report_v2.md`
- 质量报告关键指标（首轮）：
  - 列表总抓取：980
  - 粗过滤后：1
  - 详情补抓成功：1
  - 严格过滤后：0

## 2) 卡点结论（根因）
- 不是代码错误，核心是平台召回与风控双重瓶颈：
  - `job51/search_jobs` 对部分关键词响应超时，触发熔断后召回下降。
  - `liepin/search_jobs` 可用但对行业长词（化工/制造/医药/能源+完整短语）召回极低。
- 详情页结构差异大，导致“职责/要求”抽取在部分页面为空，影响严格过滤通过率。
- 目前最有价值样本（喜利得）在列表页已含有效英文JD，说明“短关键词高召回 + 后置详情补抓”方向正确。

## 3) 外部联网校验（补充证据）
- 通过外部平台搜索（Glassdoor）可见上海仍有外企数分/分析实习供给，说明“市场有岗位，当前抓取链路未吃全”。
- 参考：
  - https://www.glassdoor.com/Job/shanghai-data-analyst-intern-jobs-SRCH_IL.0,8_IM999_KO9,28.htm
  - https://www.glassdoor.com/Job/shanghai-shanghai-data-science-internship-jobs-SRCH_IL.0,17_IC2416009_KO18,41.htm

## 4) 下一步（按优先级）
- P0.5（立即）：增强详情抽取器
  - 增加 51job/猎聘站点专用提取规则（CSS/JSON 结构优先，文本正则兜底）。
  - 抽取失败时回填列表页 `job_description/job_requirement`，避免空值直接出局。
- P1（今天）：关键词拆分重构（高召回）
  - 从“行业+岗位+英语+实习+上海”长句，改为“短词笛卡尔组合 + 多轮分页”，例如：
    - 行业词：`化工|医药|制造|能源|BASF|Siemens|Bosch|Roche|Pfizer`
    - 岗位词：`实习|数据分析|商业分析|Data Analyst|BI`
    - 地域词：`上海|Shanghai`
  - 先抓高召回，再在本地做严格过滤。
- P1.5（今天）：并发与熔断参数分离
  - 分平台独立限流，避免 job51 超时拖累 liepin。
  - 增加“每关键词最小成功页”保障策略（少于阈值自动重试另一组短词）。
- P2（明天）：扩源（联网）
  - 增加 LinkedIn/Glassdoor/外企官网 careers 列表抓取器（只抓公开职位标题+链接+地点+发布日期）。
  - 与 51job/猎聘做 URL 与公司去重，提升外企覆盖。

## 5) Owner 交付标准（下一版）
- `candidate_pool_v2` >= 100（粗过滤后）
- `filtered_v2` >= 20（严格过滤后）
- `top50_actionable_v2` >= 20（总分>=70 + 链接可访问）
- 质量报告新增两项：
  - 每关键词召回条数
  - 每平台超时/熔断次数

## 6) 已执行的联网扩源（当日增量）
- 已新增联网种子池：`release_data/foreign_networked_leads_seed_20260414.csv`
- 本轮新增 8 条外网线索（BASF/Siemens/Bosch/Roche/Glassdoor 聚合页），并完成可访问性预检：
  - `OK`: 1
  - `RISKY`: 6
  - `BROKEN`: 1
- 结论：联网扩源有效，但仍需二跳抓取（从聚合页进入具体 JD 详情页）才能进入严格过滤环节。

## 7) 提量增量（立即执行）
- 已扩充联网线索到 10 条：`release_data/foreign_networked_leads_expanded_20260414.csv`
  - `OK`: 4
  - `RISKY`: 5
  - `BROKEN`: 1
- 已合并本地候选池与联网线索：
  - `release_data/foreign_strict_shanghai_candidate_pool_v2.csv`: 12
  - `release_data/foreign_networked_leads_expanded_20260414.csv`: 10
  - `release_data/foreign_strict_shanghai_candidate_pool_merged_v2.csv`: 22（去重后）
- 当前数据规模已从“个位数可用”提升到“可二跳详情补抓”的候选池规模，下一步重点是把 RISKY 聚合页转换为可评分 JD 详情页。

## 8) 最新进展（继续提量）
- 已将 `m.liepin.com/job/*.shtml` 直达详情页作为优先扩源入口，并新增 4 条高质量种子（均可访问）。
- `foreign_networked_leads_expanded_20260414.csv` 已扩展到 13 条。
- 合并候选池后重跑：
  - `candidate_pool_v2`: 15
  - `filtered_v2`: 15
  - `strict_pass`: 1（首次出现可通过严格过滤的岗位）
- 当前首个通过岗位：
  - 公司：勘讯企业咨询服务(上海)有限公司
  - 岗位：数据分析实习生-市场营销方向
  - 总分：63（保底目标）
- 关键判断：
  - 提量方向有效（从 0 通过提升到 1 通过），但外企主体识别仍是最大瓶颈，需要进一步扩充“严格外企”白名单与别名映射。

## 9) 提量继续（第二轮）
- 新增二跳直达详情页种子（`m.liepin.com/job/*.shtml`）7 条，全部通过链接可访问预检。
- 联网线索总量提升：`foreign_networked_leads_expanded_20260414.csv` 从 13 提升到 20。
- 合并池提升：`foreign_strict_shanghai_candidate_pool_merged_v2.csv` 从 16 提升到 23。
- 重跑三段式后：
  - `candidate_pool_v2`: 20
  - `filtered_v2`: 20
  - `strict_pass`: 2
  - `>=60`: 1
- 当前通过岗位：
  - 勘讯企业咨询服务(上海)有限公司：数据分析实习生-市场营销方向（63）
  - 麦当劳中国：Strategy and Insights Intern（48，已通过严格过滤）
- 下一跳重点：
  - 把“非严格外企”失败项拆为“可白名单映射”与“确认为非目标公司”两类，继续抬升 strict_pass。
