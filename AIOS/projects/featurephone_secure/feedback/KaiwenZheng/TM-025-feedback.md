# Feedback — TM-025: BindingID Logel Exposure Phase 1A

**Date:** 2026-03-12
**Memo:** Technical_Memo_25_LogelbackBindingID_Phase1A.md
**Outcome:** SUCCESS
**Author:** AIOS Core Architecture

---

## Execution Summary

修复了 `device_binding.c` 的编译阻塞（`dap_sha256.h` 不存在），新增 `device_binding_log_id()` 函数实现 BindingID 的 Logel 输出，并在两条路径（DAP init + `*#3472#` debug menu）中集成调用。经两次刷机验证，BindingID 随机性和派生逻辑均正确。

---

## Completed Work

- [x] 修复 `dap_sha256.h` → `sha256.h` 编译错误
- [x] 新增 `device_binding_log_id()` 函数（`[bind] tm25_` 格式）
- [x] 在 `DAP_LoaderInit` 中集成调用
- [x] 在 `*#3472#` debug menu 中集成调用
- [x] 创建架构文档 `device_binding_phase1a.md`
- [x] BindingID 随机性三次对比验证（含 `*#3472#` 路径）

---

## Incomplete Work

无。所有 MUST 要求均已完成。

---

## Blocking Issues

无。

---

## Verification Status

| Test | Result | Notes |
|---|---|---|
| Build verification | PASS | `dap.a` 成功生成 |
| Module build | PASS | `dap_sha256.h` 错误已消除 |
| BindingID Logel 输出 | PASS | `[bind] tm25_init ok` + 分段 hex |
| DeviceSecret 安全性 | PASS | 未泄露明文 |
| 随机性验证 | PASS | 三次 BindingID 均不同 |
| `*#3472#` 路径 | PASS | debug menu 触发 Logel 输出正常 |

---

## Next Actions

1. **TM-26（建议）**：`.bind` 文件自动导出到 `D:\DAP\device.bind`（代码已存在于 `binding_export_bindfile`，需要验证 SFS 写入是否成功）
2. **TM-27（建议）**：PC packer 读取 `.bind` 文件，实现 BIN2 设备绑定打包
3. 考虑将 `device_binding_log_id()` 调用提前到开机初始化路径（当前需要运行 .bin 或输入 `*#3472#` 才触发）

---

## Files Changed

| File | Action | Description |
|---|---|---|
| `Third-party/DAP/security/device_binding.c` | Modified | 修复 include + 新增 `device_binding_log_id()` |
| `Third-party/DAP/security/device_binding.h` | Modified | 新增声明 |
| `Third-party/DAP/platform/unisoc/DAP_Loader_unisoc.c` | Modified | 步骤 4.5 调用 |
| `Third-party/DAP/security/device_identity_debug.c` | Modified | debug menu 调用 |
| `AIOS/docs/architecture/device_binding_phase1a.md` | Created | 架构文档 |
| `AIOS/MEMORY.md` | Modified | 新增 pitfall |

---

## References

- Related memos: TM-15, TM-20, TM-22, TM-23
- Related pitfalls: `AIOS/docs/pitfalls/dap_sha256_include_missing.md`
- Related decisions: ADR-001 (SHA-256 prefix), ADR-003 (DAP_DBG logging), ADR-006 (分阶段实现)
