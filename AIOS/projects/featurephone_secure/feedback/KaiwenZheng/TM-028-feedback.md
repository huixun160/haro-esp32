# TM-28 Feedback — BIN2 Payload Encryption

- **Outcome:** ✅ SUCCESS
- **Date:** 2026-03-13
- **Verification:** Phase 1 (v2 regression) ✅ + Phase 2 (v3 encrypted .bin3) ✅

## Completed Work

- BIN2 v3 header (96B): `payload_enc_mode`, `payload_iv[16]`, `reserved2[16]`
- AES-128-CTR implementation (`dap_aes.c`, tiny-AES-c port)
- Payload crypto wrapper (`bin2_crypto_payload.c`, KDF + decrypt)
- v2/v3 backward compatible loader (`bin2_loader.c`)
- Packer v3 support (`bin2_pack.py`, `--encrypt` flag)
- AES-CTR KAT (`test_aes_ctr_kat.py`, NIST SP 800-38A)

## Bugs Fixed During Verification

1. **bin2_crypto.c 硬编码 BIN2_HEADER_SIZE** → 改为 `header->header_size`
2. **DAP_ReleaseAP 硬编码偏移** → 改为 `bin2_get_payload_offset_from_buffer()`
3. **BSS 重分配后从磁盘重读密文** → 加密 BIN2 用 `memcpy` 保留解密数据
4. **ARM I-cache 一致性** → 添加 cache flush（辅助修复）

## Incomplete / Deferred

- [ ] ⚠️ **`device_binding.c` 中的 `tm28_DEBUG_secret` 临时 trace 未删除**
  - 必须在 TM-33（错误码/接口/架构文档收口）阶段删除
  - 搜索关键词: `tm28_DEBUG_secret`
  - 文件: `Third-party/DAP/security/device_binding.c`

## Next Actions

1. **TM-33 收口阶段:** 删除 `tm28_DEBUG_secret` trace 代码并重新烧录
2. 考虑将 `device_secret` 导出流程自动化（PC 工具 + 设备协同）
3. 跨设备加密 .bin3 异常场景测试（可在后续 TM 中覆盖）
