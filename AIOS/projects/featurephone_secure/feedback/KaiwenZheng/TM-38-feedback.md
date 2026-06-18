# Feedback — TM-38: Runtime Memory & App Lifecycle Design

**Date:** 2026-03-23
**Outcome:** SUCCESS

---

## Execution Summary

将 TM-38 从"行为观察"重定向为"架构设计"。通过 `DAP_Loader_unisoc.c` 静态分析确认当前 DAP = 同步单任务 Loader（无生命周期/资源追踪/OOM），然后设计了完整的 Runtime 架构。

## Completed Work

- [x] 现状分析：DAP_ExecuteAP 同步阻塞，Running_AP 局部变量，无全局 APP 表
- [x] 生命周期状态机：INIT → RUNNING → PAUSED → DESTROYED
- [x] Lifecycle Callback API：`DAP_LifecycleEvent` + `TAP_EntryEx`
- [x] Resource Tracker 数据结构：per-APP 追踪 mem/LVGL/timer/socket
- [x] 完整资源回收流程
- [x] OOM 3 级检测 + Kill Policy
- [x] BIN2 Header v4 扩展（memory_required, supports_background）
- [x] 差距分析：7 个新组件 + 7 个文件修改

## Incomplete Work

- [ ] 详细伪代码（仅架构级别）
- [ ] 性能开销估算

## Next Actions

| TM | 内容 | 优先级 |
|----|------|--------|
| **TM-39** | Resource Tracker + DAP_MemAlloc_Tracked | P0 |
| TM-40 | Lifecycle 状态机 + 回调分发 | P1 |
| TM-41 | Background Task + OOM Policy | P2 |
| TM-42 | BIN Header v4 + Packer 更新 | P2 |

## Files Changed

| File | Action |
|------|--------|
| `docs/architecture/runtime_memory_lifecycle.md` | Created — 核心设计文档 |
| `quality_reports/specs/TM-38_spec.md` | Created — 冻结规格 |

## References

- DAP Loader: `Third-party/DAP/platform/unisoc/DAP_Loader_unisoc.c`
- TM-22 pitfall: alloc_base tracking (already fixed)
- TM-37: Module Completion Dashboard (6,306 APIs)
