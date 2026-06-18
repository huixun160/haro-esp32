# Frozen Specification — TM-28 BIN2 Payload Encryption

## MUST
- [ ] BIN2 header 扩展到 96 字节（新增 `payload_enc_mode` 1B + `enc_reserved` 1B + `payload_iv` 16B + `reserved2` 14B）
- [ ] BIN2 版本号升至 v3，`BIN2_VERSION = 3`
- [ ] 文件扩展名 `.bin3`，`DAP_FMM_IsBinFile` 识别 `.bin3`
- [ ] AES-128-CTR 加密 payload，实现来自 tiny-AES-c（裁剪 CTR-only，`dap_aes_` 前缀）
- [ ] KDF: `payload_key = SHA256("AIOS-PAYLOAD-V1" || DeviceSecret || binding_id)[0..15]`
- [ ] 随机 IV: packer 每次 `os.urandom(16)` 写入 header
- [ ] 加密必须绑定: `payload_enc_mode != 0` → `binding_mode` 必须为 `DEVICE_BOUND`
- [ ] 签名/加密顺序: packer 先加密 → 组装 → 签名; loader 先验签 → 验绑 → 解密 → 执行
- [ ] 解密就地操作 (in-place)，禁止新增 malloc/free 路径
- [ ] Logel trace 保留: `tm28_enc_mode`, `tm28_decrypt_start`, `tm28_decrypt_ok`
- [ ] 新增错误码: `BIN2_ERR_ENC_MODE = -7`, `BIN2_ERR_DECRYPT = -8`
- [ ] CTR known-answer test: 同一 key+IV+plaintext 在 Python 和 C 端输出逐字节相同

## SHOULD
- [ ] 架构文档 `AIOS/docs/architecture/bin2_payload_encryption.md`
- [ ] 回归测试覆盖旧 Phase-0/Phase-1 样本（test_original.bin, test_valid.bin2, test_tampered.bin2, test_badsig.bin2）
- [ ] PC packer `--debug` 模式输出 payload_enc_mode, IV, signed_region_len
- [ ] offset 常量集中在 `bin2_format.h`，禁止 magic numbers 分散

## MAY
- [ ] 未来 header 预留 `kdf_id`, `cipher_id`, `iv_len` 字段（当前用 reserved 占位）
- [ ] `extract_bindingid.py` 同步支持 v3 header 解析

## OUT OF SCOPE
- App Store 云端签名/密钥下发
- 云端设备注册/账户系统
- DAP 本体混淆/字符串清理
- PAC / DAP core blob 保护
- Key rotation / revocation
- 文件系统/分区隔离
- SDK 暴露面分层/自动化裁剪
- 新 bindfile 格式设计
- BIN1 支持移除
- AEAD 模式

Approved by: KaiwenZheng
Date: 2026-03-13
