# Frozen Specification — TM-21: BIN2 Signature Verification Failure Root Cause Isolation and Fix

## MUST

- [ ] 在 `bin2_crypto.c` 增加 message hash 诊断日志，打印 SHA-256(signed_region) 前 8 字节
- [ ] 在 `bin2_pack.py` 增加 `--debug` 模式，输出与设备端完全同口径的诊断信息
- [ ] 打印设备端实际 signed region 长度、偏移量、header/signature/payload 前 8 字节
- [ ] 明确根因属于「结论 A（signed region 不一致）」还是「结论 B（Ed25519 实现问题）」
- [ ] 修复验签失败问题，使 `test_valid.bin2` 通过、`test_tampered.bin2` 和 `test_badsig.bin2` 被拒绝
- [ ] 保持 Logel trace 全程可用，所有日志使用已验证链路（`DAP_DBG` 或 `BIN2_LOG`）
- [ ] 编译通过：0 link error，0 undefined symbol
- [ ] 输出根因定位文档 `docs/tm15_sigfail_rootcause.md`
- [ ] 日志单条 < 128 字符，使用结构化 `tm15_` 前缀格式

## SHOULD

- [ ] 在设备端增加固定测试向量验证 Ed25519 实现（若 Step 4 判定为结论 B）
- [ ] 打印设备端 SHA-256(signed_region) 与 PC 端完全对齐的 hash，供人工比对
- [ ] 输出设备验证记录 `docs/tm15_sigfix_validation.md`

## MAY

- [ ] 在 `generate_test_bins.py` 中也增加 `--debug` 输出
- [ ] 为 `bin2_pack.py --verify` 增加 `--debug` 输出

## OUT OF SCOPE

- DeviceSecret 设备绑定
- BIN2 payload 加密
- PAC 中 DAP core 加密/运行时解密
- App Store 后端
- Key rotation / revocation
- 更换 BIN2 整体协议设计

Approved by: ________
Date: 2026-03-11
