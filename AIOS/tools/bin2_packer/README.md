# BIN2 Packer — AIOS Secure Application Packager

## 概述

将原始 BIN1 应用文件打包为 BIN2 安全格式，包含 Ed25519 数字签名和 SHA-256 完整性校验。

## BIN2 文件格式

```
[BIN2 Header (48 bytes)] [Ed25519 Signature (64 bytes)] [Original BIN1 Data]
```

## 依赖安装

```bash
pip install pynacl
```

## 使用方式

### 1. 首次使用：生成密钥对

```bash
python bin2_pack.py --generate-keys
```

输出：
- `private_key.bin` — 私钥（32 字节，**妥善保管！**）
- `public_key.bin` — 公钥（32 字节）
- C 语言公钥数组（复制到 `bin2_crypto.c` 的 `BIN2_PUBLIC_KEY`）

### 2. 打包 BIN2

```bash
python bin2_pack.py input.bin output.bin2
python bin2_pack.py input.bin output.bin2 --key private_key.bin  # 指定私钥
python bin2_pack.py input.bin output.bin2 -v                     # 详细输出
```

### 3. 验证 BIN2（本地测试）

```bash
python bin2_pack.py --verify test_valid.bin2 --pubkey public_key.bin
```

### 4. 生成测试样本

```bash
python generate_test_bins.py input.bin
python generate_test_bins.py input.bin -o test_output/
```

输出 4 个测试文件：

| 文件 | 说明 | 设备端预期 |
|------|------|-----------|
| `test_valid.bin2` | 合法签名 | 运行成功 |
| `test_tampered.bin2` | 篡改 payload | hash 校验失败 |
| `test_original.bin` | 原始 BIN1 | 开发模式运行 |
| `test_badsig.bin2` | 错误签名 | 签名验证失败 |

## 部署流程

1. `python bin2_pack.py --generate-keys`
2. 将终端输出的 C 公钥数组复制到 `Third-party/DAP/security/bin2_crypto.c`
3. 重新编译固件
4. 使用 `bin2_pack.py` 打包应用
5. 将 `.bin2` 文件部署到设备

## ⚠️ 安全注意事项

- `private_key.bin` 是签名私钥，**不得泄露**
- 不要将私钥提交到版本控制
- 建议在 `.gitignore` 中添加 `*.bin` 和 `private_key.bin`
