# Frozen Specification — TM-38: Runtime Memory & App Lifecycle Design

**Date:** 2026-03-23
**Repurposed:** 行为分析 → **架构设计文档**（不改代码）

---

## MUST

- [ ] **现状分析：** 静态代码分析确认当前 DAP = 单任务 Loader（无 lifecycle/memory mgmt）
- [ ] **Runtime 模型设计：** 单 APP 前台 + 后台任务（网络/定时器可后台运行）
- [ ] **内存策略：** 共享 heap（SCI_ALLOC），增加 OOM 检测和处理策略设计
- [ ] **资源回收设计：** APP 退出/被 kill 时完整回收 — 内存 + LVGL 对象 + 定时器 + 网络连接
- [ ] **生命周期状态机：** 定义 APP 状态 (INIT → RUNNING → BACKGROUND → DESTROYED)
- [ ] **API 定义：** 设计 lifecycle callback API（onPause/onResume/onDestroy）
- [ ] **BIN Header 扩展方案：** 允许声明内存需求等新字段
- [ ] **差距分析：** 现状 vs 设计 → 后续 TM 实现清单

## SHOULD

- [ ] 资源追踪表设计（per-APP 分配记录）
- [ ] Kill policy 设计（OOM 时杀后台任务的规则）
- [ ] 与 LVGL / COAPI / Network 的集成点说明

## MAY

- [ ] 参考其他嵌入式 RTOS 多任务方案
- [ ] 未来 inter-APP 通信机制草案

## OUT OF SCOPE

- 代码实现（→ 后续 TM）
- 真机实验验证
- BIN 格式向后兼容性破坏

---

Approved by: ___
Date: 2026-03-23
