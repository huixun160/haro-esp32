# Implementation Plan — TM01 README_WORKFLOW 迁移增强

## File Changes
| Action | File | Module | Description |
|--------|------|--------|-------------|
| MODIFY | `AIOS/projects/aios_workflow_meta/technical_memos/PinzhenHe/PinzhenHe_workflowtransform_TM01_claudecodetransfrom.md` | memo | 更新 Author/Date/Project 与验收方式 |
| MODIFY | `AIOS/README_WORKFLOW.md` | workflow_docs | 增加发布前安全检查章节 |
| CREATE | `AIOS/projects/aios_workflow_meta/quality_reports/PinzhenHe/specs/TM-01_spec.md` | quality | 冻结规格归档 |
| CREATE | `AIOS/projects/aios_workflow_meta/quality_reports/PinzhenHe/plans/TM-01_plan.md` | quality | 实施计划归档 |
| CREATE | `AIOS/projects/aios_workflow_meta/quality_reports/PinzhenHe/reports/TM-01_migration_report.md` | quality | 迁移内容清单 |
| CREATE | `AIOS/projects/aios_workflow_meta/quality_reports/PinzhenHe/verification/TM-01_verification_checklist.md` | quality | 验证清单 |
| CREATE | `AIOS/projects/aios_workflow_meta/quality_reports/PinzhenHe/reports/TM-01_diff_summary.md` | quality | 差异摘要 |

## Module Impact
- `workflow_docs`：仅文档增强，不涉及代码逻辑执行路径。
- `quality_reports`：新增本次 TM 的规范化归档文件，便于审计与复盘。

## Risk Areas
- 文档冲突风险：新增内容可能与已有 GitLab 章节重复。  
  - 缓解：仅添加“发布前安全检查”补充段，不改原流程主干。
- 可迁移价值风险：源项目以泄露事件背景为主，通用信息有限。  
  - 缓解：只保留“发布包安全检查”这一通用工程实践。

## ⚠️ Pitfall Briefing

### Matched Pitfalls (2 items)
| # | Pitfall | Relevance | Prevention |
|---|---------|-----------|------------|
| 1 | PowerShell 编码腐蚀源码（MEMORY 2026-03-21） | 本 TM 涉及文档编辑，若用不当写入方式可能破坏编码/换行 | 使用编辑器工具改文档，避免 `Set-Content` 直接覆盖 |
| 2 | 反复踩坑：配置遗漏导致“看似成功实则失效” | 本 TM 为流程文档增强，若缺少发布前检查会重复出现交付隐患 | 在 README 增加发布前安全检查清单 |

### Applicable Runbooks
- [ ] 无强制 runbook（本任务不涉及 make/dap 构建链）

### Key Decisions to Respect
- 登录与工作流机制为 AIOS 核心决策，不在本 TM 修改范围内。
- `README_WORKFLOW.md` 是唯一操作手册，新增信息必须可直接执行。

## Execution Order
1. 更新 TM 元信息（Author/Date/Project/验收方式）。
2. 扫描 `claude-code-main` 并提炼可迁移信息。
3. 修改 `AIOS/README_WORKFLOW.md` 增补安全检查章节。
4. 生成迁移报告、验证清单、差异摘要并归档。
5. 自检改动与路径完整性。
