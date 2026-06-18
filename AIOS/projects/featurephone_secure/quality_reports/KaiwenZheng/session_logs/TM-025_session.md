# Session Log — TM-25: BindingID Logel Exposure Phase 1A

**Date:** 2026-03-12
**Task:** TM-25 — Logel 返回 BindingID（Phase 1A）
**Duration:** ~2 hours
**Author:** AIOS Core Architecture

---

## Summary

修复了 `device_binding.c` 的编译错误（`dap_sha256.h` → `sha256.h`），新增 `device_binding_log_id()` 函数通过 Logel 输出 BindingID，并在 DAP 初始化和 `*#3472#` 调试菜单两条路径中集成调用。验证了两次不同 DeviceSecret 生成不同 BindingID，确认随机性正确。

---

## Files Modified

| File | Action | Description |
|---|---|---|
| `Third-party/DAP/security/device_binding.c` | Modified | 修复 `#include "dap_sha256.h"` → `"sha256.h"`；新增 `device_binding_log_id()` |
| `Third-party/DAP/security/device_binding.h` | Modified | 新增 `device_binding_log_id()` 声明 |
| `Third-party/DAP/platform/unisoc/DAP_Loader_unisoc.c` | Modified | 步骤 4.5 调用 `device_binding_log_id()` |
| `Third-party/DAP/security/device_identity_debug.c` | Modified | `*#3472#` 路径也调用 `device_binding_log_id()` |
| `AIOS/docs/architecture/device_binding_phase1a.md` | Created | 设备绑定架构文档 |
| `AIOS/MEMORY.md` | Modified | 新增 TM-25 pitfall 记录 |

---

## Key Decisions

- **触发方式改为双路径**：原计划只在 `DAP_LoaderInit` 中触发，但发现 `DAP_LoaderInit` 是 lazy init（仅在运行 .bin 时触发），因此额外在 `*#3472#` 调试菜单路径中也加入调用

---

## Deviations from Spec

- Memo 建议触发方式 A（DAP 初始化路径），实际增加了第二条路径（`*#3472#` debug menu），因为 `DAP_LoaderInit` 不在开机时执行

---

## Verification Results

| Test | Result | Notes |
|---|---|---|
| Build verification | PASS | 编译通过，`dap.a` 成功生成 |
| `dap_sha256.h` error | PASS | 不再报错 |
| BindingID Logel 可见 | PASS | `[bind] tm25_init ok` + 16 字节 hex |
| DeviceSecret 未泄露 | PASS | Logel 中仅有 BindingID |
| 随机性验证 | PASS | 三次刷机产生不同 BindingID |
| `*#3472#` 路径验证 | PASS | debug menu 路径也能触发 Logel 输出 |

### BindingID 对比记录

| 次数 | 触发方式 | BindingID |
|---|---|---|
| 第 1 次 | 运行 .bin（DAP_LoaderInit） | `b76fbe818c2209d5bfdc65d214523158` |
| 第 2 次（重刷后） | 运行 .bin（DAP_LoaderInit） | `c932cc919e88e54ba1213c5c0a25c022` |
| 第 3 次（重刷后） | `*#3472#` debug menu | `0183c6f46de5a22d6aea7aff61d4fa63` |
