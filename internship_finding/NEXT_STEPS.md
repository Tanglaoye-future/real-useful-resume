# 后续迭代计划（快手已上线）

## 当前状态
- 快手日常抓取、合并清洗、行动看板已可稳定运行
- 上海投递约束已生效，目标岗位池仅保留上海岗位

## 本周计划（优先级从高到低）
1. 腾讯接入
   - 完成 `TencentAdapter` 列表与详情字段对齐
   - 输出 `official_tencent_api` 并并入现有合并链路
2. 多公司看板泛化
   - 将 `generate_kuaishou_dashboard` 重构为 `generate_dashboard(df_all, company_name)`
   - 同步输出 `dashboard_tencent_*`
3. 自动化脚本升级
   - 从 `run_kuaishou_daily.ps1` 升级到 `run_daily.ps1`
   - 支持按公司开关（kuaishou / tencent / bytedance）

## 质量守则
- 只保留上海岗位进入投递目标池
- 看板必须输出“今日新增高置信上海数据岗”
- 每次运行必须产生日志并可追溯失败原因
