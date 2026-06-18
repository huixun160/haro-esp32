# Implementation Plan - TM-02 文档交付型适配方案

## File Changes
| Action | File | Module | Description |
|--------|------|--------|-------------|
| CREATE | `AIOS/projects/aios_workflow_meta/quality_reports/PinzhenHe/specs/TM-02_spec.md` | quality | 冻结规格归档 |
| CREATE | `AIOS/projects/aios_workflow_meta/quality_reports/PinzhenHe/plans/TM-02_plan.md` | quality | 实施计划归档 |
| CREATE | `AIOS/projects/aios_workflow_meta/quality_reports/PinzhenHe/reports/TM-02_compatibility_analysis.md` | report | 兼容性分析与适配设计主报告 |
| CREATE | `AIOS/projects/aios_workflow_meta/quality_reports/PinzhenHe/verification/TM-02_verification_checklist.md` | verification | 文档验收清单 |
| CREATE | `AIOS/projects/aios_workflow_meta/quality_reports/PinzhenHe/session_logs/TM-02_session_log_2026-04-13.md` | quality | 会话与执行追踪归档 |

## Module Impact
- `quality_reports`：新增 TM-02 文档资产，无代码改动。
- `workflow governance`：补充一次“文档型 TM”执行样例，便于后续复用。

## Risk Areas
- 需求歧义风险：原 memo 包含实现型与分析型混合表述。
  - 缓解：已澄清为“文档为主，不做实现”。
- 验收偏差风险：原文出现 `out.bin` 产物要求（已确认是幻觉输出）。
  - 缓解：改为文档完整性与可执行性评审。
- 命名合规风险：当前 TM 文件名不满足规范 `<ENGINEER>_<PROJECT>_TM<XX>_<name>.md`。
  - 缓解：记录 assignment-reviewer 告警，不在本轮重命名，避免破坏用户输入路径。

## ⚠️ Pitfall Briefing

### Matched Pitfalls (3 items)
| # | Pitfall | Relevance | Prevention |
|---|---------|-----------|------------|
| 1 | `powershell-encoding-corruption.md` | 本轮产出大量中文文档，错误写入方式会损坏编码 | 使用受控编辑写入；不对源码做 `Set-Content` 覆盖 |
| 2 | `windows_gbk_unicode.md` | Windows 控制台编码容易导致显示/输出异常 | 文档与日志中使用 ASCII 安全标记为主 |
| 3 | `broad-string-replace-corruption.md` | 批量替换可能误伤关键内容 | 不做无边界全局替换，按文件逐项生成 |

### Applicable Runbooks
- [ ] 无强制 runbook（本任务不改 `make/dap/dap.mk`，不触发 `dap_mk_checklist`）

### Key Decisions to Respect
- 文档语言统一中文（工程师确认）。
- 本轮不实现 CLI/脚本，只做设计方案。
- 适配范围以 Codex/Cursor 为当前目标，但设计保持可扩展。
- 原 memo 中 `out.bin` 验收项不作为本轮标准。

## Execution Order
1. 完成 intake + memo critique + clarify 结论收敛。
2. 生成冻结规格并归档。
3. 输出 TM-02 兼容性分析主报告（含 Adapter 设计、结构描述、流程方案、安全策略）。
4. 生成文档型验证清单。
5. 生成会话日志与执行追踪。
