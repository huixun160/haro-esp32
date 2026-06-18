# BIN2 签名验证硬编码 BIN2_HEADER_SIZE 常量

- **TM:** TM-28 (BIN2 Payload Encryption)
- **日期:** 2026-03-13
- **严重度:** 🔴 致命 (所有 v2 文件签名验证失败)

## Symptom

TM-28 将 `BIN2_HEADER_SIZE` 从 64 改为 96 后，所有 v2 `.bin2` 文件签名验证失败。
Logel: `tm15_sig_verify: total=860 hdr=96`（应为 `total=828 hdr=64`）

## Root Cause

`bin2_crypto.c` 中签名验证函数使用硬编码常量 `BIN2_HEADER_SIZE` 和 `BIN2_PAYLOAD_OFFSET`，
未读取 `header->header_size` 实际值。当常量改为 96 后，v2 文件（header_size=64）的签名范围计算错误。

共 3 处硬编码：
1. `total_size = BIN2_HEADER_SIZE + ...` (L157)
2. DAP_DBG trace 中引用 `BIN2_HEADER_SIZE` (L159/161)
3. `mut_sig_area = header + BIN2_HEADER_SIZE` (L189)

## Fix

全部改为读取 `header->header_size`。

## Prevention Rule

**修改 `bin2_format.h` 中任何常量后，必须全局搜索该常量的所有使用点，确认每处是否应该用常量还是从 header 实际读取。**

相关命令：`grep -rn "BIN2_HEADER_SIZE\|BIN2_PAYLOAD_OFFSET" Third-party/DAP/`
