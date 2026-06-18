# Feedback — TM-028R: Security Baseline Recovery

**Date:** 2026-03-15
**Memo:** Technical_Memo_28R_security+baseline_recovery.md
**Outcome:** SUCCESS
**Author:** KaiwenZheng

---

## Execution Summary

从 TM27 clean baseline 成功恢复 TM28 全部功能（BIN2 Payload Encryption: AES-128-CTR）。
采用两阶段方式：(1) AIOS 文档合并 (2) 安全代码恢复。编译通过，新手机设备端 v2 回归 + v3 加密验证全部通过。

---

## Completed Work

- [x] Stage 1: AIOS 文档合并（MEMORY.md, feedback, pitfalls, runbooks, spec, plan, packer tools）
- [x] Stage 2: 可信安全文件 cherry-pick（8 files from contaminated snapshot）
- [x] Stage 3: 不可信文件手动修改（dap.mk, DAP_Loader_unisoc.c, DAP_FMM_Integration.c, bin2_loader.h）
- [x] Stage 4: 编译烧录成功
- [x] Stage 4: v2 BIN2 回归验证（4 cases）
- [x] Stage 4: v3 加密 BIN3 验证（Logel trace 确认完整加密解密流程）

---

## Incomplete Work

无。所有 TM-28R 恢复目标已完成。

---

## Blocking Issues

无。

---

## Verification Status

| Test | Result | Notes |
|------|--------|-------|
| v2 Unbound | PASS | 运行成功 |
| v2 Bound | PASS | 运行成功 |
| v2 Tampered | PASS | 被拒绝 |
| v2 CrossDevice | PASS | 被拒绝 |
| v3 Encrypted BIN3 | PASS | 解密执行成功，BSS memcpy 路径生效 |

---

## Bugs Fixed (预防性)

1. **动态 payload offset** — `bin2_get_payload_offset()` 对 v2 文件返回错误的 160 偏移，改用 `bin2_get_payload_offset_from_buffer()` 动态返回 128(v2)/160(v3)
2. **加密 BSS memcpy** — 加密 BIN2 BSS 重分配不从文件重读（重读=密文），用 memcpy 保留解密数据
3. **I-cache flush** — bin2_loader.c 已包含解密后 cache 一致性处理

---

## Next Actions

1. **tm28_DEBUG_secret trace 移除** — 当前 DeviceSecret 仍通过 Logel 输出（安全风险），需在后续 memo 中清理
2. 考虑 TM-29 或后续安全增强

---

## References

- Related memos: TM-23, TM-25, TM-26, TM-27, TM-28
- Related decisions: ADR-012~015 (AES, KDF, Sign-after-Encrypt, BSS memcpy)
- Session log: `AIOS/quality_reports/session_logs/TM-028R_session.md`
- Original TM-28 feedback: `AIOS/feedback/TM-028-feedback.md`
