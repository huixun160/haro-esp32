# Feedback — TM-019: Logel Fix Pilot Research

**Date:** 2026-03-10
**Memo:** Technical_Memo_19_logelfix_pilotresearch.md
**Outcome:** PARTIAL
**Author:** AIOS Founding Team

---

## Execution Summary

完成平台 trace 机制研究和根因定位。已修改 `dap.mk`，添加 PoC 测试点。等待设备验证。

---

## Completed Work

- [x] 确认 `SCI_TRACE_LOW` 是平台标准 trace API（1145+ 调用）
- [x] 找到根因：`SCI_TRACE_MODE` 未在 `dap.mk` 定义
- [x] 添加 `-DSCI_TRACE_MODE` 到 `dap.mk`
- [x] 添加 3 条 PoC 测试 trace 到 `device_identity.c`
- [x] 生成研究文档 `logel_fix_pilot_research.md`
- [x] 生成反馈文档 `logel_trace_feedback.md`
- [x] 确认 DAP security 文件不含 `os_api.h`，需通过 `DAP_DBG` 间接输出

---

## Incomplete Work

- [ ] 设备端验证：3 条 PoC 日志是否在 Logel 中可见
- [ ] 如果 PoC 通过：验证 TM-15 的 `tm15_*` 诊断日志也可见

---

## Blocking Issues

| Issue | Symptom | Root Cause | Suggested Resolution |
|---|---|---|---|
| 需设备验证 | 无法确认 trace 链路是否真正打通 | 代码已修改但未烧录 | 编译烧录后在 Logel 搜 `tm19_` |

---

## Verification Status

| Test | Result | Notes |
|---|---|---|
| 根因分析 | ✅ PASS | `SCI_TRACE_MODE` 编译开关 |
| dap.mk 修改 | ✅ PASS | 已添加 `-DSCI_TRACE_MODE` |
| PoC trace 嵌入 | ✅ PASS | 3 条 `tm19_*` 日志 |
| 设备 Logel 验证 | ⏳ PENDING | 等待工程师编译烧录 |

---

## Next Actions

1. 编译烧录固件，在 Logel 搜索 `tm19_trace_alive`
2. 如果 3 条 PoC 日志可见 → trace 链路通，进入 TM-15 Ed25519 调试
3. 如果不可见 → 在 `DAP_OSAssociated_unisoc.c` 中直接加 `SCI_TRACE_LOW("tm19_direct_test")` 排除间接路径问题

---

## References

- Pitfall: `AIOS/docs/pitfalls/sci_trace_mode_missing.md`
- Research: `AIOS/docs/logel_fix_pilot_research.md`
- Feedback: `AIOS/docs/logel_trace_feedback.md`
