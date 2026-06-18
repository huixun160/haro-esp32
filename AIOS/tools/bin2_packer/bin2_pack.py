#!/usr/bin/env python3
"""
BIN2 Packer — AIOS Secure Application Packager

将原始 BIN1 文件打包为 BIN2 安全格式：
  [BIN2 Header (48 bytes)] [Ed25519 Signature (64 bytes)] [Original BIN1 Data]

用法:
  python bin2_pack.py --generate-keys                    # 生成密钥对
  python bin2_pack.py input.bin output.bin2               # 使用默认密钥打包
  python bin2_pack.py input.bin output.bin2 --key pk.bin  # 指定私钥

依赖:
  pip install pynacl
"""

import argparse
import hashlib
import struct
import sys
import os

try:
    from nacl.signing import SigningKey, VerifyKey
    from nacl.encoding import RawEncoder
except ImportError:
    print("ERROR: PyNaCl not installed. Run: pip install pynacl")
    sys.exit(1)

# ============================================================================
# BIN2 格式常量（必须与 bin2_format.h 严格一致）
# ============================================================================

BIN2_MAGIC = b'BIN2'
BIN2_VERSION = 1
BIN2_HEADER_SIZE = 48
BIN2_SIGNATURE_SIZE = 64
BIN2_PAYLOAD_OFFSET = BIN2_HEADER_SIZE + BIN2_SIGNATURE_SIZE  # 112

# Header 结构（小端序）：
#   magic:        4s  (4 bytes)
#   version:      H   (uint16)
#   header_size:  H   (uint16)
#   payload_size: I   (uint32)
#   key_id:       B   (uint8)
#   binding_mode: B   (uint8)
#   reserved:     H   (uint16)
#   payload_hash: 32s (32 bytes)
HEADER_FORMAT = '<4sHHIBBH32s'
assert struct.calcsize(HEADER_FORMAT) == BIN2_HEADER_SIZE, \
    f"Header format size mismatch: {struct.calcsize(HEADER_FORMAT)} != {BIN2_HEADER_SIZE}"



def _print_debug_info(context, header_bytes, signature, payload, message, pubkey):
    """TM-21: Print diagnostic info matching device-side tm15_ trace format."""
    total = len(message)
    msg_hash = hashlib.sha256(message).digest()

    print(f"\n=== TM-21 DEBUG ({context}) ===")
    print(f"tm15_sig_verify: total={total} hdr={BIN2_HEADER_SIZE}"
          f" sig={BIN2_SIGNATURE_SIZE} pay={len(payload)}")
    print(f"tm15_sig_verify: payload_off={BIN2_PAYLOAD_OFFSET}"
          f" signed_region_len={total}")
    print(f"tm15_sig[0..7]={' '.join(f'{b:02x}' for b in signature[:8])}")
    print(f"tm15_pubkey[0..7]={' '.join(f'{b:02x}' for b in pubkey[:8])}")
    print(f"tm15_hdr[0..7]={' '.join(f'{b:02x}' for b in header_bytes[:8])}")
    print(f"tm15_payload[0..7]={' '.join(f'{b:02x}' for b in payload[:8])}")
    print(f"tm15_msg_hash[0..7]={' '.join(f'{b:02x}' for b in msg_hash[:8])}")
    print(f"=== END DEBUG ===")


def generate_keys(output_dir='.'):
    """生成 Ed25519 密钥对"""
    sk = SigningKey.generate()
    vk = sk.verify_key

    sk_path = os.path.join(output_dir, 'private_key.bin')
    vk_path = os.path.join(output_dir, 'public_key.bin')

    with open(sk_path, 'wb') as f:
        f.write(bytes(sk))
    with open(vk_path, 'wb') as f:
        f.write(bytes(vk))

    # 输出 C 语言格式的公钥（方便复制到 bin2_crypto.c）
    vk_bytes = bytes(vk)
    c_array = ', '.join(f'0x{b:02x}' for b in vk_bytes)
    c_lines = []
    for i in range(0, 32, 8):
        line_bytes = vk_bytes[i:i+8]
        c_lines.append('    ' + ', '.join(f'0x{b:02x}' for b in line_bytes))

    print(f"Keys generated:")
    print(f"  Private key: {sk_path} ({len(bytes(sk))} bytes)")
    print(f"  Public key:  {vk_path} ({len(vk_bytes)} bytes)")
    print(f"\nC 语言公钥（复制到 bin2_crypto.c 的 BIN2_PUBLIC_KEY）:")
    print("static const uint8 BIN2_PUBLIC_KEY[32] = {")
    for i, line in enumerate(c_lines):
        comma = ',' if i < len(c_lines) - 1 else ''
        print(f"{line}{comma}")
    print("};")

    return sk_path, vk_path


def pack_bin2(input_path, output_path, private_key_path, verbose=False, debug=False):
    """将 BIN1 打包为 BIN2"""

    # 读取私钥
    with open(private_key_path, 'rb') as f:
        sk_bytes = f.read()
    if len(sk_bytes) != 32:
        print(f"ERROR: Private key must be 32 bytes, got {len(sk_bytes)}")
        sys.exit(1)
    sk = SigningKey(sk_bytes)

    # 读取 BIN1 payload
    with open(input_path, 'rb') as f:
        payload = f.read()

    if len(payload) == 0:
        print("ERROR: Input file is empty")
        sys.exit(1)

    payload_size = len(payload)

    # 计算 SHA-256 hash
    payload_hash = hashlib.sha256(payload).digest()
    assert len(payload_hash) == 32

    # 构造 header
    header = struct.pack(
        HEADER_FORMAT,
        BIN2_MAGIC,             # magic
        BIN2_VERSION,           # version
        BIN2_HEADER_SIZE,       # header_size
        payload_size,           # payload_size
        0,                      # key_id (Phase-0: 0)
        0,                      # binding_mode (UNBOUND)
        0,                      # reserved
        payload_hash            # payload_hash
    )
    assert len(header) == BIN2_HEADER_SIZE

    # 签名覆盖：header(48) + zeros(64) + payload
    # 与设备端一致：signature 区域清零后签名整个文件
    sig_placeholder = b'\x00' * BIN2_SIGNATURE_SIZE
    message = header + sig_placeholder + payload

    # Ed25519 签名
    signed = sk.sign(message, encoder=RawEncoder)
    signature = signed.signature
    assert len(signature) == BIN2_SIGNATURE_SIZE

    # 组装 BIN2 文件
    bin2_data = header + signature + payload

    # 写入输出文件
    with open(output_path, 'wb') as f:
        f.write(bin2_data)

    if verbose:
        print(f"BIN2 packed successfully:")
        print(f"  Input:         {input_path} ({payload_size} bytes)")
        print(f"  Output:        {output_path} ({len(bin2_data)} bytes)")
        print(f"  Header:        {BIN2_HEADER_SIZE} bytes")
        print(f"  Signature:     {BIN2_SIGNATURE_SIZE} bytes")
        print(f"  Payload:       {payload_size} bytes")
        print(f"  Payload hash:  {payload_hash.hex()}")
        print(f"  Signature hex: {signature.hex()[:32]}...")
    else:
        print(f"OK: {input_path} ({payload_size}B) -> {output_path} ({len(bin2_data)}B)")

    if debug:
        _print_debug_info('pack', header, signature, payload, message,
                          bytes(sk.verify_key))

    return bin2_data


def verify_bin2(bin2_path, public_key_path, verbose=False, debug=False):
    """验证 BIN2 文件（用于本地测试）"""

    with open(public_key_path, 'rb') as f:
        vk_bytes = f.read()
    vk = VerifyKey(vk_bytes)

    with open(bin2_path, 'rb') as f:
        data = f.read()

    if len(data) < BIN2_PAYLOAD_OFFSET:
        print(f"FAIL: File too small ({len(data)} < {BIN2_PAYLOAD_OFFSET})")
        return False

    # 解析 header
    header_bytes = data[:BIN2_HEADER_SIZE]
    magic, version, header_size, payload_size, key_id, binding_mode, reserved, payload_hash = \
        struct.unpack(HEADER_FORMAT, header_bytes)

    if magic != BIN2_MAGIC:
        print(f"FAIL: Bad magic {magic}")
        return False

    if verbose:
        print(f"Header: version={version}, payload_size={payload_size}, key_id={key_id}, binding={binding_mode}")

    # 提取 signature 和 payload
    signature = data[BIN2_HEADER_SIZE:BIN2_PAYLOAD_OFFSET]
    payload = data[BIN2_PAYLOAD_OFFSET:]

    if len(payload) != payload_size:
        print(f"FAIL: Payload size mismatch ({len(payload)} != {payload_size})")
        return False

    # 验证 hash
    computed_hash = hashlib.sha256(payload).digest()
    if computed_hash != payload_hash:
        print(f"FAIL: Hash mismatch")
        return False
    if verbose:
        print("Hash: OK")

    # 验证签名（message = header + zeros + payload）
    message = header_bytes + (b'\x00' * BIN2_SIGNATURE_SIZE) + payload
    try:
        vk.verify(message, signature, encoder=RawEncoder)
        if verbose:
            print("Signature: OK")
    except Exception as e:
        print(f"FAIL: Signature verification failed: {e}")
        if debug:
            _print_debug_info('verify', header_bytes, signature, payload,
                              message, vk_bytes)
        return False

    if debug:
        _print_debug_info('verify', header_bytes, signature, payload,
                          message, vk_bytes)

    print(f"VERIFY OK: {bin2_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description='BIN2 Secure Packer for AIOS DAP')
    parser.add_argument('input', nargs='?', help='Input BIN1 file')
    parser.add_argument('output', nargs='?', help='Output BIN2 file')
    parser.add_argument('--key', default='private_key.bin', help='Private key file (default: private_key.bin)')
    parser.add_argument('--pubkey', default='public_key.bin', help='Public key file (for --verify)')
    parser.add_argument('--generate-keys', action='store_true', help='Generate Ed25519 keypair')
    parser.add_argument('--verify', action='store_true', help='Verify a BIN2 file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--debug', action='store_true',
                        help='Print diagnostic info matching device-side tm15_ trace format')

    args = parser.parse_args()

    if args.generate_keys:
        generate_keys()
        return

    if args.verify:
        if not args.input:
            parser.error("--verify requires input file")
        success = verify_bin2(args.input, args.pubkey, args.verbose, args.debug)
        sys.exit(0 if success else 1)

    if not args.input or not args.output:
        parser.error("input and output files are required")

    if not os.path.exists(args.key):
        print(f"ERROR: Private key not found: {args.key}")
        print("Run: python bin2_pack.py --generate-keys")
        sys.exit(1)

    pack_bin2(args.input, args.output, args.key, args.verbose, args.debug)


if __name__ == '__main__':
    main()
