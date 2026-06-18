# Verification Checklist - TM-02 AIOS 与 Codex/Cursor 兼容性分析（文档型）

## 验证范围说明
- 本 TM 为文档交付型任务，不包含代码实现、构建产物和设备烧录。
- 因此本清单以“文档完整性、可执行性、风险控制充分性”为核心。

## Build Steps
- [ ] 本轮无代码构建步骤（N/A）
- [ ] 说明文档已明确“后续实现阶段”所需构建入口（通过）

## Simulator Steps
- [ ] 本轮无模拟器执行步骤（N/A）
- [ ] 方案文档已定义未来模拟验证入口（通过）

## Device Steps
- [ ] 本轮无设备烧录执行（N/A）
- [ ] 文档已规定 flash 为高风险受控操作，不可默认自动执行（通过）

## 文档完整性检查
- [ ] 已存在冻结规格：`specs/TM-02_spec.md`
- [ ] 已存在实施计划：`plans/TM-02_plan.md`
- [ ] 已存在主报告：`reports/TM-02_compatibility_analysis.md`
- [ ] 报告包含不少于 5 个不兼容点与对应缓解方案
- [ ] 报告包含可扩展 Adapter 架构设计
- [ ] 报告包含 `aios_project.yaml` 草案
- [ ] 报告语言为中文
- [ ] 已剔除“`out.bin` 为唯一验收产物”的不合理约束

## Expected Logs
- `[WORKFLOW] intake completed` - 备忘录完成结构化提取
- `[WORKFLOW] clarify completed` - 澄清问题已收敛
- `[WORKFLOW] spec frozen` - 冻结规格已归档
- `[WORKFLOW] plan archived` - 计划已归档
- `[WORKFLOW] report archived` - 主报告已归档

## Success Criteria
- [ ] TM-02 形成完整文档闭环（spec/plan/report/verification/session_log）
- [ ] 不包含未授权代码实现或高风险自动化操作
- [ ] 后续实现团队可直接据此进入 PoC 开发

## Failure Indicators
- 缺失任一关键归档文件 - 表示流程未闭环
- 报告未覆盖风险控制策略 - 表示方案不可落地
- 混入实现承诺但无验证基础 - 表示规格与计划不一致
