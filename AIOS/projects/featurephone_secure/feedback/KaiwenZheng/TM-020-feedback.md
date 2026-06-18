# Feedback — TM-020: Logel Trace Fix & BIN2 Prefix Tracking

**Date:** 2026-03-11
**Memo:** Technical_Memo_20_logelfix
**Outcome:** SUCCESS
**Author:** AIOS Founding Team

---

## Execution Summary

修复 `BIN2_LOG` 未定义链接错误，建立直接 `SCI_TRACE_LOW` 调用链路，设备端 Logel 验证通过。

---

## Completed Work

- [x] 创建 `dap_security_log.h` — 直接调用 `SCI_TRACE_LOW`（非间接链路）
- [x] 修复 `Undefined symbol BIN2_LOG` 链接错误
- [x] 统一 BIN2 日志前缀为 `[bin2]`
- [x] 重新添加 `-DSCI_TRACE_MODE` 到 `dap.mk`
- [x] 添加 tm20_ PoC 测试 trace
- [x] 设备端 Logel 验证：`[bin2]` 和 `tm20_` 可见 ✅
- [x] 记录 recurring pitfall + runbook

---

## Verification Status

| Test | Result |
|---|---|
| 编译 0 errors | ✅ PASS |
| Logel 搜索 `tm20_trace_alive` | ✅ PASS |
| Logel 搜索 `[bin2]` | ✅ PASS |
| 设备端验证 | ✅ PASS |

---

## Next Actions

1. TM-15 Ed25519 调试 — 现在有 Logel 观测能力，可以 dump 签名输入/输出进行对比
2. 移除 tm20_ PoC 测试代码（验证完成后）
