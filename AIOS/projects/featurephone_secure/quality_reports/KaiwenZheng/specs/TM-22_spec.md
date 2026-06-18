# Frozen Specification — TM-22: BIN2 Buffer Fix

## MUST
- [x] 保存 `DAP_MemAlloc` 原始基地址 (`alloc_base`)，不被 BIN2 指针前移覆盖
- [x] 所有 `DAP_MemFree` 调用使用 `alloc_base` 而非 `Running_AP`
- [x] `DAP_ReleaseAP` 正确处理 BIN2 handle（alloc_base 含 BIN2 头部）
- [x] 添加 `tm22_` 诊断 trace 输出 `alloc_base` 和 `Running_AP` 地址
- [ ] BIN1 路径回归无影响
- [ ] BIN2 路径不再触发 `SCI_Release_Buffer` assert

## SHOULD
- [x] 创建根因文档 `docs/tm22_memoryleak_trace_analysis.md`
- [ ] 设备端 Logel 验证 `tm22_` trace 可见

## MAY
- [ ] TM-21 恢复：抓取 `tm15_msg_hash` 与 PC 端 `fd f1 03 cc 1d a4 0d 42` 对比

## OUT OF SCOPE
- Ed25519 实现修复（属于 TM-21 范围）
- DeviceSecret 绑定
- BIN2 payload 加密
- App Store 后端

Approved by: AIOS Founding Team
Date: 2026-03-11
