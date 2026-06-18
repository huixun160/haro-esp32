#!/usr/bin/env python3
"""
BIN2 v2 测试样本生成器 — TM-27 Device-Bound BIN2 验证

生成 4 个测试文件用于设备端验证：
  Case 1: test_unbound.bin2         — UNBOUND 模式（任何设备可运行）
  Case 2: test_bound.bin2           — DEVICE_BOUND 模式（仅绑定设备可运行）
  Case 3: test_tampered_bound.bin2  — 绑定 BIN2 但篡改 payload（签名/hash 失败）
  Case 4: test_crossdevice.bin2     — 用假 binding_id 绑定（目标设备 binding 不匹配）

用法:
  python generate_test_bins_v2.py <input.bin> --bind-file device.bind
  python generate_test_bins_v2.py <input.bin> --bind-file device.bind --output-dir test/output

依赖:
  pip install pynacl

设备端验证预期:
  Case 1: BIN2_OK (0)           → Logel: tm27_verify OK: binding_mode=0
  Case 2: BIN2_OK (0)           → Logel: tm27_verify OK: binding_mode=1
  Case 3: BIN2_ERR_SIGNATURE(-2) or BIN2_ERR_HASH(-3) → Logel: verify failed: signature/hash
  Case 4: BIN2_ERR_BINDING (-6) → Logel: tm27_verify FAIL: binding ret=-2

错误码速查:
  BIN2_OK            =  0  验证成功
  BIN2_ERR_NOT_BIN2  =  1  不是 BIN2 格式
  BIN2_ERR_HEADER    = -1  header 非法
  BIN2_ERR_SIGNATURE = -2  签名失败
  BIN2_ERR_HASH      = -3  hash 不匹配
  BIN2_ERR_SIZE      = -4  大小不一致
  BIN2_ERR_VERSION   = -5  版本不支持
  BIN2_ERR_BINDING   = -6  设备绑定不匹配
"""

import argparse
import hashlib
import json
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

# ============================================================================
# BIN2 v2 格式常量（必须与 bin2_format.h + bin2_pack.py 严格一致）
# ============================================================================

BIN2_MAGIC = b'BIN2'
BIN2_VERSION = 2
BIN2_HEADER_SIZE = 64
BIN2_SIGNATURE_SIZE = 64
BIN2_PAYLOAD_OFFSET = BIN2_HEADER_SIZE + BIN2_SIGNATURE_SIZE  # 128
BIN2_BINDING_ID_SIZE = 16

# Binding modes
BIN2_BIND_UNBOUND = 0
BIN2_BIND_DEVICE_BOUND = 1

# Header 结构（小端序, 64 bytes total）:
#   magic:        4s  (4 bytes)
#   version:      H   (uint16)
#   header_size:  H   (uint16)
#   payload_size: I   (uint32)
#   key_id:       B   (uint8)
#   binding_mode: B   (uint8)
#   reserved:     H   (uint16)
#   binding_id:   16s (16 bytes)
#   payload_hash: 32s (32 bytes)
HEADER_FORMAT = '<4sHHIBBH16s32s'
assert struct.calcsize(HEADER_FORMAT) == BIN2_HEADER_SIZE


def make_bin2_v2(payload, sk, binding_mode=BIN2_BIND_UNBOUND,
                 binding_id=None):
    """从 payload、私钥和绑定信息构造 BIN2 v2 文件"""
    if binding_id is None:
        binding_id = b'\x00' * BIN2_BINDING_ID_SIZE

    payload_hash = hashlib.sha256(payload).digest()

    header = struct.pack(
        HEADER_FORMAT,
        BIN2_MAGIC,
        BIN2_VERSION,
        BIN2_HEADER_SIZE,
        len(payload),
        0,                  # key_id
        binding_mode,
        0,                  # reserved
        binding_id,
        payload_hash
    )
    assert len(header) == BIN2_HEADER_SIZE

    # 签名覆盖: header + zeros(64) + payload (ADR-002)
    message = header + (b'\x00' * BIN2_SIGNATURE_SIZE) + payload
    signed = sk.sign(message, encoder=RawEncoder)
    signature = signed.signature

    return header + signature + payload


def load_bind_file(bind_path):
    """加载 .bind 文件，返回 binding_id bytes (16 bytes)"""
    with open(bind_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'binding_id' not in data:
        print(f"ERROR: .bind file missing 'binding_id' field")
        sys.exit(1)

    hex_id = data['binding_id']
    if len(hex_id) != BIN2_BINDING_ID_SIZE * 2:
        print(f"ERROR: binding_id must be {BIN2_BINDING_ID_SIZE * 2} hex chars, "
              f"got {len(hex_id)}")
        sys.exit(1)

    binding_id = bytes.fromhex(hex_id)
    return binding_id, data


def main():
    parser = argparse.ArgumentParser(
        description='BIN2 v2 Test Sample Generator (TM-27)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
测试验证预期:
  Case 1: test_unbound.bin2         → 任何设备运行成功  (BIN2_OK = 0)
  Case 2: test_bound.bin2           → 绑定设备运行成功  (BIN2_OK = 0)
  Case 3: test_tampered_bound.bin2  → 签名/hash 验证失败 (ERR = -2 或 -3)
  Case 4: test_crossdevice.bin2     → 绑定验证失败       (BIN2_ERR_BINDING = -6)
""")
    parser.add_argument('input', help='Input BIN1 file (original app .bin)')
    parser.add_argument('--key', default='private_key.bin',
                        help='Private key file (default: private_key.bin)')
    parser.add_argument('--bind-file', required=True,
                        help='Path to device.bind file (from target device)')
    parser.add_argument('--output-dir', '-o', default='test/output',
                        help='Output directory (default: test/output)')
    args = parser.parse_args()

    # ---- 检查输入文件 ----
    if not os.path.exists(args.input):
        print(f"ERROR: Input file not found: {args.input}")
        sys.exit(1)

    if not os.path.exists(args.key):
        print(f"ERROR: Private key not found: {args.key}")
        print("Run: python bin2_pack.py --generate-keys")
        sys.exit(1)

    if not os.path.exists(args.bind_file):
        print(f"ERROR: Bind file not found: {args.bind_file}")
        sys.exit(1)

    # ---- 读取密钥 ----
    with open(args.key, 'rb') as f:
        sk_bytes = f.read()
    if len(sk_bytes) != 32:
        print(f"ERROR: Private key must be 32 bytes, got {len(sk_bytes)}")
        sys.exit(1)
    sk = SigningKey(sk_bytes)

    # ---- 读取 BIN1 payload ----
    with open(args.input, 'rb') as f:
        payload = f.read()
    if len(payload) == 0:
        print("ERROR: Input file is empty")
        sys.exit(1)

    # ---- 读取 bindfile ----
    binding_id, bind_data = load_bind_file(args.bind_file)

    print(f"=" * 60)
    print(f"BIN2 v2 Test Generator — TM-27")
    print(f"=" * 60)
    print(f"Input:        {args.input} ({len(payload)} bytes)")
    print(f"Bind file:    {args.bind_file}")
    print(f"Binding ID:   {binding_id.hex()}")
    print(f"Binding alg:  {bind_data.get('binding_alg', '?')}")
    print(f"Device model: {bind_data.get('device_model', '?')}")
    print(f"Output dir:   {args.output_dir}")
    print(f"=" * 60)

    os.makedirs(args.output_dir, exist_ok=True)

    # ==================================================================
    # Case 1: UNBOUND BIN2 — 任何设备可运行
    # ==================================================================
    unbound_bin2 = make_bin2_v2(payload, sk,
                                binding_mode=BIN2_BIND_UNBOUND)
    path1 = os.path.join(args.output_dir, 'test_unbound.bin2')
    with open(path1, 'wb') as f:
        f.write(unbound_bin2)
    print(f"\n[Case 1] test_unbound.bin2         ({len(unbound_bin2):>6} bytes)")
    print(f"         binding_mode=UNBOUND (0)")
    print(f"         Expected: ANY device → RUN OK (BIN2_OK = 0)")
    print(f"         Logel:    'tm27_verify OK: binding_mode=0'")

    # ==================================================================
    # Case 2: DEVICE_BOUND BIN2 — 仅绑定设备可运行
    # ==================================================================
    bound_bin2 = make_bin2_v2(payload, sk,
                              binding_mode=BIN2_BIND_DEVICE_BOUND,
                              binding_id=binding_id)
    path2 = os.path.join(args.output_dir, 'test_bound.bin2')
    with open(path2, 'wb') as f:
        f.write(bound_bin2)
    print(f"\n[Case 2] test_bound.bin2           ({len(bound_bin2):>6} bytes)")
    print(f"         binding_mode=DEVICE_BOUND (1)")
    print(f"         binding_id={binding_id.hex()}")
    print(f"         Expected: BOUND device → RUN OK (BIN2_OK = 0)")
    print(f"                   OTHER device → REJECT  (BIN2_ERR_BINDING = -6)")
    print(f"         Logel:    'tm27_verify OK: binding_mode=1' (match)")
    print(f"                   'tm27_verify FAIL: binding ret=-2' (mismatch)")

    # ==================================================================
    # Case 3: TAMPERED BOUND BIN2 — 篡改 payload，签名/hash 失败
    # ==================================================================
    tampered = bytearray(bound_bin2)
    # 篡改 payload 区域最后一个字节
    tampered[-1] ^= 0xFF
    path3 = os.path.join(args.output_dir, 'test_tampered_bound.bin2')
    with open(path3, 'wb') as f:
        f.write(bytes(tampered))
    print(f"\n[Case 3] test_tampered_bound.bin2  ({len(tampered):>6} bytes)")
    print(f"         binding_mode=DEVICE_BOUND (1) + payload tampered")
    print(f"         Expected: ANY device → REJECT")
    print(f"         Error:    BIN2_ERR_SIGNATURE (-2) or BIN2_ERR_HASH (-3)")
    print(f"         Logel:    'verify failed: signature' or 'verify failed: hash'")

    # ==================================================================
    # Case 4: CROSS-DEVICE BIN2 — 用虚假 binding_id，模拟跨设备
    # ==================================================================
    # 生成一个完全不同的 binding_id（翻转所有 bit）
    fake_binding_id = bytes(b ^ 0xFF for b in binding_id)
    crossdevice_bin2 = make_bin2_v2(payload, sk,
                                     binding_mode=BIN2_BIND_DEVICE_BOUND,
                                     binding_id=fake_binding_id)
    path4 = os.path.join(args.output_dir, 'test_crossdevice.bin2')
    with open(path4, 'wb') as f:
        f.write(crossdevice_bin2)
    print(f"\n[Case 4] test_crossdevice.bin2     ({len(crossdevice_bin2):>6} bytes)")
    print(f"         binding_mode=DEVICE_BOUND (1)")
    print(f"         binding_id={fake_binding_id.hex()} (FAKE — inverted)")
    print(f"         Expected: ANY device → REJECT (BIN2_ERR_BINDING = -6)")
    print(f"         Logel:    'tm27_verify FAIL: binding ret=-2'")
    print(f"                   '[BIND] verify: MISMATCH REJECTED'")

    # ==================================================================
    # Summary
    # ==================================================================
    print(f"\n{'=' * 60}")
    print(f"生成完成: 4 个测试文件")
    print(f"{'=' * 60}")
    print(f"  {path1}")
    print(f"  {path2}")
    print(f"  {path3}")
    print(f"  {path4}")
    print(f"\n错误码速查:")
    print(f"  BIN2_OK            =  0  验证成功")
    print(f"  BIN2_ERR_SIGNATURE = -2  签名失败")
    print(f"  BIN2_ERR_HASH      = -3  hash 不匹配")
    print(f"  BIN2_ERR_BINDING   = -6  设备绑定不匹配")
    print(f"  BIND_ERR_MISMATCH  = -2  BindingID 比对失败 (binding_verify 返回)")


if __name__ == '__main__':
    main()
