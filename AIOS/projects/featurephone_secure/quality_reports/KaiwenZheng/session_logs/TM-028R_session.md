# Session Log — TM-28R: Security Baseline Recovery

**Date:** 2026-03-15
**Memo:** Technical_Memo_28R_security+baseline_recovery.md
**Engineer:** KaiwenZheng
**Outcome:** SUCCESS

---

## Summary

从 TM27 clean baseline 成功恢复 TM28（BIN2 Payload Encryption）全部功能。
通过两阶段方式执行：先合并 AIOS 文档（pitfalls/feedback/runbooks/spec/plan），再恢复安全代码（可信 cherry-pick + 不可信文件手动修改）。
新手机设备端验证通过：v2 BIN2 回归正常，v3 加密 BIN3 解密执行成功。

---

## Files Created/Modified

| File | Action | Description |
|------|--------|-------------|
| `Third-party/DAP/security/dap_aes.c` | Created | AES-128-CTR 实现 (tiny-AES-c port) |
| `Third-party/DAP/security/dap_aes.h` | Created | AES 头文件 |
| `Third-party/DAP/security/bin2_crypto_payload.c` | Created | Payload KDF + AES-CTR 解密 |
| `Third-party/DAP/security/bin2_crypto_payload.h` | Created | Payload 加密头文件 |
| `Third-party/DAP/security/bin2_format.h` | Replaced | v2→v3, 64→96B header, +enc_mode/IV |
| `Third-party/DAP/security/bin2_loader.c` | Replaced | +decrypt dispatch, v2/v3 兼容, I-cache flush |
| `Third-party/DAP/security/bin2_loader.h` | Modified | +bin2_get_payload_offset_from_buffer 声明 |
| `Third-party/DAP/security/bin2_crypto.c` | Replaced | header_size 动态读取 |
| `Third-party/DAP/security/device_binding.c` | Replaced | +payload key 材料接口 |
| `Third-party/DAP/platform/unisoc/DAP_Loader_unisoc.c` | Modified | 动态 offset + 加密 BSS memcpy + 新错误码 |
| `Third-party/DAP/platform/unisoc/DAP_FMM_Integration.c` | Modified | +.bin3 扩展名 |
| `make/dap/dap.mk` | Modified | +dap_aes.c, +bin2_crypto_payload.c |
| `AIOS/MEMORY.md` | Modified | +2 pitfalls, +4 ADRs, 更新 facts |
| `AIOS/registry/apis.yaml` | Modified | +3 TM-28 API, 更新 IsBinFile 描述 |
| `AIOS/feedback/TM-028-feedback.md` | Copied | 从污染快照合并 |
| `AIOS/docs/runbooks/tm28_verification_runbook.md` | Copied | 从污染快照合并 |
| `AIOS/docs/pitfalls/bin2_crypto_hardcoded_header_size.md` | Copied | TM-28 pitfall |
| `AIOS/docs/pitfalls/bin2_encrypted_bss_reread.md` | Copied | TM-28 pitfall |
| `AIOS/technical_memos/Technical_Memo_28_bin2payloadencryption.md` | Copied | 原始 TM-28 memo |
| `AIOS/quality_reports/specs/TM-28_spec.md` | Copied | Frozen spec |
| `AIOS/quality_reports/plans/TM-28_plan.md` | Copied | 实施计划 |
| `AIOS/tools/bin2_packer_v2/bin2_pack.py` | Replaced | v3 + --encrypt |
| `AIOS/tools/bin2_packer_v2/test_aes_ctr_kat.py` | Copied | AES KAT 测试 |
| `AIOS/tools/bin2_packer_v2/test/tm28r_phone/` | Created | 新手机测试数据 (bind + BIN2×4 + BIN3×1) |

---

## Key Decisions

- **ADR-012~015:** 从污染快照合并（AES tiny-AES-c, Payload KDF 独立 Salt, Sign-after-Encrypt, BSS memcpy）
- **动态 payload offset:** 使用 `bin2_get_payload_offset_from_buffer()` 替代固定 `bin2_get_payload_offset()`，确保 v2/v3 兼容
- **不信任 dap.mk:** 手动添加 2 个 SOURCES 而非从污染快照复制

---

## Verification Results

| Case | 文件 | 预期 | 实际 |
|------|------|------|------|
| 1 | test_unbound.bin2 | ✅ 运行成功 | ✅ (由用户确认) |
| 2 | test_bound.bin2 | ✅ 运行成功 | ✅ (由用户确认) |
| 3 | test_tampered_bound.bin2 | ❌ 拒绝 | ❌ (由用户确认) |
| 4 | test_crossdevice.bin2 | ❌ 拒绝 | ❌ (由用户确认) |
| 5 | test_encrypted.bin3 | ✅ 运行成功 | ✅ Logel 确认完整流程 |

### BIN3 Logel Trace 确认

```
tm15_bin2_verify: v=3, hdr=96, pay=572, bind=1, enc=1
tm15_BIN2 signature OK
tm27_verify OK: binding_mode=1
tm28_kdf: derived payload key OK
tm28_decrypt_ok: decrypted 572 bytes
tm28_cache_flush: payload 572 bytes flushed
tm15_BIN2 verify success (encrypted+decrypted)
tm28_BSS_realloc_enc: memcpy 572 bytes from decrypted payload
```

---

## 设备信息

| 设备 | Binding ID |
|------|-----------|
| tm28r_phone | `75c4b33c4cca62d7c7c5c8b5775729f1` |
