# Feedback — TM-022: BIN2 Buffer Fix + Memory Leak Root Cause

**Date:** 2026-03-11
**Memo:** Technical_Memo_22_bin2fixbuffer.md
**Outcome:** SUCCESS ✅
**Author:** AIOS Founding Team

---

## Execution Summary

定位并修复了两个 BIN2 集成 bug，使 BIN2 安全链从签名到执行完全闭环。同时确认 TM-21 的 Ed25519 签名验证也已通过。

---

## Completed Work

- [x] **Bug #1 — Running_AP 指针偏移**：BIN2 unwrap 后 `Running_AP` 前移 112 字节，原始 `DAP_MemAlloc` 基地址丢失 → `DAP_MemFree` 释放偏移指针导致 heap 损坏
- [x] **Bug #2 — BSS 重读文件偏移错误**：BSS 重分配路径从文件偏移 0 重读（读到 BIN2 header），应从偏移 112 开始读 BIN1 payload
- [x] 添加 `alloc_base` 变量追踪原始分配基地址
- [x] `DAP_ReleaseAP` 支持 BIN2 handle（通过 `bin2_detect` 定位 `TApplication`）
- [x] 添加 `tm22_` 诊断 trace
- [x] `dap.mk` checklist 验证
- [x] 创建根因文档 `docs/tm22_memoryleak_trace_analysis.md`
- [x] 创建冻结规格 `AIOS/quality_reports/specs/TM-22_spec.md`
- [x] 更新 `AIOS/MEMORY.md`
- [x] 创建 pitfall `AIOS/docs/pitfalls/bin2_pointer_offset_heap_corruption.md`

---

## 附带确认：TM-21 签名验证已通过

设备 trace 确认：
```
tm15_msg_hash[0..7]=fd f1 03 cc 1d a4 0d 42   ← 与 PC 端完全一致
ed25519_verify ret=0 (0=OK)                     ← 签名验证通过
tm15_BIN2 verify success                        ← BIN2 完整验证成功
```

**TM-21 结论 A/B 判定：不属于 A 也不属于 B** — signed region 一致且 Ed25519 实现正确。TM-21 阶段看到的验签失败实际上是在修复前的旧代码上测试，当时代码本身就能通过验签（ret=0），真正的阻塞问题是 TM-22 的内存 bug 导致后续崩溃。

---

## Verification Status

| Test | Result |
|------|--------|
| `test_original.bin` → 正常执行 | ✅ PASS |
| `test_valid.bin2` → 正常执行 | ✅ PASS |
| `test_tampered.bin2` → ERR-10 拒绝 | ✅ PASS |
| `test_badsig.bin2` → ERR-10 拒绝 | ✅ PASS |
| 编译 0 errors | ✅ PASS |
| `dap.mk` checklist | ✅ PASS |

---

## 新增/修改文件清单

| File | Action | Description |
|------|--------|-------------|
| `Third-party/DAP/platform/unisoc/DAP_Loader_unisoc.c` | MODIFIED | Bug #1 + Bug #2 修复 + tm22_ trace |
| `docs/tm22_memoryleak_trace_analysis.md` | CREATED | 根因分析 |
| `AIOS/quality_reports/specs/TM-22_spec.md` | CREATED | 冻结规格 |
| `AIOS/docs/pitfalls/bin2_pointer_offset_heap_corruption.md` | CREATED | Pitfall 记录 |
| `AIOS/docs/pitfalls/bin2_bss_realloc_file_offset.md` | CREATED | Pitfall 记录 (Bug #2) |
| `AIOS/docs/runbooks/bin2_migration_checklist.md` | CREATED | BIN→BIN2 迁移检查清单 |
| `AIOS/MEMORY.md` | UPDATED | 新增 TM-22 pitfall + key decision |

---

## Git Guidance

```bash
git add Third-party/DAP/platform/unisoc/DAP_Loader_unisoc.c
git add docs/tm22_memoryleak_trace_analysis.md
git add AIOS/quality_reports/specs/TM-22_spec.md
git add AIOS/docs/pitfalls/bin2_pointer_offset_heap_corruption.md
git add AIOS/docs/pitfalls/bin2_bss_realloc_file_offset.md
git add AIOS/docs/runbooks/bin2_migration_checklist.md
git add AIOS/MEMORY.md
git add AIOS/technical_memos/Technical_Memo_22_bin2fixbuffer.md
git add AIOS/feedback/TM-022-feedback.md

git commit -m "TM-22: Fix BIN2 loader integration bugs + verify full security chain

Two critical bugs fixed in DAP_Loader_unisoc.c:
1. Running_AP pointer offset: alloc_base tracking prevents heap corruption
2. BSS realloc re-read: seek to payload_off=112 for BIN2 files

Device verification: all 4 test cases pass
- test_original.bin: normal execution (BIN1 compat)
- test_valid.bin2: signature OK + normal execution
- test_tampered.bin2: correctly rejected (ERR-10)
- test_badsig.bin2: correctly rejected (ERR-10)

Also confirms TM-21: Ed25519 verify ret=0, msg_hash matches PC"
```

> ⚠️ 请手动在终端执行以上命令。

---

## References

- Memo: `AIOS/technical_memos/Technical_Memo_22_bin2fixbuffer.md`
- Spec: `AIOS/quality_reports/specs/TM-22_spec.md`
- Root Cause: `docs/tm22_memoryleak_trace_analysis.md`
- Pitfalls: `AIOS/docs/pitfalls/bin2_*.md`
- Migration Guide: `AIOS/docs/runbooks/bin2_migration_checklist.md`
