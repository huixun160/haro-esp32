#!/usr/bin/env python3
"""
BIN2 测试样本生成器

生成 4 个测试文件用于设备端验证：
  1. test_valid.bin2      — 合法签名 BIN2（预期: 运行成功）
  2. test_tampered.bin2   — 篡改 payload（预期: hash 校验失败）
  3. test_badsig.bin2     — 错误签名（预期: 签名验证失败）
  4. test_original.bin    — 原始 BIN1（预期: 开发模式直接运行）

用法:
  python generate_test_bins.py <input.bin> [--key private_key.bin]

依赖:
  pip install pynacl
"""

import argparse
import hashlib
import struct
import sys
import os
import shutil

try:
    from nacl.signing import SigningKey, VerifyKey
    from nacl.encoding import RawEncoder
except ImportError:
    print("ERROR: PyNaCl not installed. Run: pip install pynacl")
    sys.exit(1)

# BIN2 格式常量
BIN2_MAGIC = b'BIN2'
BIN2_VERSION = 1
BIN2_HEADER_SIZE = 48
BIN2_SIGNATURE_SIZE = 64
BIN2_PAYLOAD_OFFSET = BIN2_HEADER_SIZE + BIN2_SIGNATURE_SIZE
HEADER_FORMAT = '<4sHHIBBH32s'


def make_bin2(payload, sk):
    """从 payload 和私钥构造合法 BIN2"""
    payload_hash = hashlib.sha256(payload).digest()
    header = struct.pack(
        HEADER_FORMAT,
        BIN2_MAGIC, BIN2_VERSION, BIN2_HEADER_SIZE,
        len(payload), 0, 0, 0, payload_hash
    )
    message = header + (b'\x00' * BIN2_SIGNATURE_SIZE) + payload
    signed = sk.sign(message, encoder=RawEncoder)
    return header + signed.signature + payload


def main():
    parser = argparse.ArgumentParser(description='Generate BIN2 test samples')
    parser.add_argument('input', help='Input BIN1 file (original app)')
    parser.add_argument('--key', default='private_key.bin', help='Private key file')
    parser.add_argument('--output-dir', '-o', default='.', help='Output directory')
    args = parser.parse_args()

    if not os.path.exists(args.key):
        print(f"ERROR: Private key not found: {args.key}")
        print("Run: python bin2_pack.py --generate-keys")
        sys.exit(1)

    # 读取私钥
    with open(args.key, 'rb') as f:
        sk = SigningKey(f.read())

    # 读取原始 BIN1
    with open(args.input, 'rb') as f:
        payload = f.read()

    print(f"Input: {args.input} ({len(payload)} bytes)")
    os.makedirs(args.output_dir, exist_ok=True)

    # ======================================================================
    # Case 1: 合法 BIN2
    # ======================================================================
    valid_bin2 = make_bin2(payload, sk)
    path1 = os.path.join(args.output_dir, 'test_valid.bin2')
    with open(path1, 'wb') as f:
        f.write(valid_bin2)
    print(f"[Case 1] test_valid.bin2       ({len(valid_bin2)} bytes) — valid BIN2, should RUN")

    # ======================================================================
    # Case 2: 篡改 payload（翻转最后一个字节）
    # ======================================================================
    tampered_payload = bytearray(payload)
    tampered_payload[-1] ^= 0xFF  # 翻转最后一个字节
    tampered_bin2 = make_bin2(bytes(tampered_payload), sk)
    # 但这会生成一个正确签名的"篡改"文件
    # 我们需要的是：用原始签名但篡改后的 payload
    # 所以先生成合法 BIN2，然后修改 payload 部分
    tampered = bytearray(valid_bin2)
    tampered[-1] ^= 0xFF  # 篡改 payload 的最后一个字节
    path2 = os.path.join(args.output_dir, 'test_tampered.bin2')
    with open(path2, 'wb') as f:
        f.write(bytes(tampered))
    print(f"[Case 2] test_tampered.bin2    ({len(tampered)} bytes) — tampered payload, should FAIL (hash)")

    # ======================================================================
    # Case 3: 原始 BIN1（不变）
    # ======================================================================
    path3 = os.path.join(args.output_dir, 'test_original.bin')
    shutil.copy2(args.input, path3)
    print(f"[Case 3] test_original.bin     ({len(payload)} bytes) — original BIN1, should RUN (dev mode)")

    # ======================================================================
    # Case 4: 错误签名（用不同的密钥签名）
    # ======================================================================
    bad_sk = SigningKey.generate()  # 生成一个不同的密钥
    badsig_bin2 = make_bin2(payload, bad_sk)
    path4 = os.path.join(args.output_dir, 'test_badsig.bin2')
    with open(path4, 'wb') as f:
        f.write(badsig_bin2)
    print(f"[Case 4] test_badsig.bin2      ({len(badsig_bin2)} bytes) — wrong key signature, should FAIL (signature)")

    print(f"\nAll 4 test files generated in: {os.path.abspath(args.output_dir)}")
    print("\n测试验证预期:")
    print("  Case 1: test_valid.bin2     → 运行成功, 日志: 'BIN2 detected', 'BIN2 verify success'")
    print("  Case 2: test_tampered.bin2  → 拒绝执行, 日志: 'BIN2 verify failed: signature'")
    print("  Case 3: test_original.bin   → 运行成功, 无 BIN2 日志 (BIN1 dev mode)")
    print("  Case 4: test_badsig.bin2    → 拒绝执行, 日志: 'BIN2 verify failed: signature'")


if __name__ == '__main__':
    main()
