# TM-01 Migration Report

## Source Scanned
- `hpz_legacy_code/claude-code-main/README.md`
- `hpz_legacy_code/claude-code-main/src/projectOnboardingState.ts`

## Candidate Information Identified
1. 发布产物可能因 source map 暴露源码（通用发布安全风险）。
2. Onboarding 步骤状态机思想（可完成项 + 条件使能 + 完成标记）。
3. 项目入口/目录级别探索建议（先入口，再模块）。

## Migration Decision
- **Accepted**：发布前安全检查（防止 source map / 源码泄露）  
  - 迁移到：`AIOS/README_WORKFLOW.md` 的 GitLab 协作章节下。
- **Deferred**：Onboarding 状态机设计  
  - 原因：偏产品实现细节，适合放到未来 workflow 设计 TM，不适合直接放入工程师操作手册。
- **Rejected**：泄露事件背景叙述、特定产品内部名词  
  - 原因：不属于 AIOS 工作流通用操作知识。

## Final Migration Summary
- 在 `README_WORKFLOW.md` 新增“发布前安全检查（防止源码意外泄露）”小节。
- 保持原有 AIOS 流程主干不变，仅补充可执行检查项。
