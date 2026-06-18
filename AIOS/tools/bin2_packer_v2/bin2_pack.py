#!/usr/bin/env python3
"""
BIN2 Packer v3 — AIOS Secure Application Packager
(Phase-2: Device Binding + Payload Encryption)

打包格式:
  v2:  [Header(64B)] [Signature(64B)] [Plaintext Payload]     → .bin2
  v3:  [Header(96B)] [Signature(64B)] [Encrypted Payload]     → .bin3

TM-28 新特性:
  - Header 96 bytes（新增 enc_mode + IV + reserved）
  - --encrypt 参数启用 AES-128-CTR 加密（必须同时使用 --bind-file）
  - KDF: SHA256("AIOS-PAYLOAD-V1" || DeviceSecret || binding_id)[0..15]
  - 签名覆盖 encrypted payload（sign-after-encrypt）
  - payload_hash 对应 plaintext（解密后校验）

用法:
  python bin2_pack.py --generate-keys
  python bin2_pack.py input.bin output.bin2                          # v2 UNBOUND
  python bin2_pack.py input.bin output.bin2 --bind-file device.bind  # v2 BOUND
  python bin2_pack.py input.bin output.bin3 --bind-file device.bind --encrypt  # v3 加密
  python bin2_pack.py --verify output.bin3 --pubkey public_key.bin
  python bin2_pack.py --verify output.bin2 --pubkey public_key.bin   # 兼容 v2

依赖:
  pip install pynacl pycryptodome
"""

import argparse
import hashlib
import json
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
BIN2_SIGNATURE_SIZE = 64
BIN2_BINDING_ID_SIZE = 16
BIN2_IV_SIZE = 16

# v2 常量
BIN2_V2_VERSION = 2
BIN2_V2_HEADER_SIZE = 64
BIN2_V2_PAYLOAD_OFFSET = BIN2_V2_HEADER_SIZE + BIN2_SIGNATURE_SIZE  # 128

# v3 常量 (TM-28)
BIN2_V3_VERSION = 3
BIN2_V3_HEADER_SIZE = 96
BIN2_V3_PAYLOAD_OFFSET = BIN2_V3_HEADER_SIZE + BIN2_SIGNATURE_SIZE  # 160

# Binding modes
BIN2_BIND_UNBOUND = 0
BIN2_BIND_DEVICE_BOUND = 1

# Encryption modes (TM-28)
BIN2_ENC_NONE = 0
BIN2_ENC_AES128_CTR = 1

# v2 Header (64 bytes): magic(4) + version(2) + header_size(2) + payload_size(4)
#   + key_id(1) + binding_mode(1) + reserved(2) + binding_id(16) + payload_hash(32)
HEADER_V2_FORMAT = '<4sHHIBBH16s32s'
assert struct.calcsize(HEADER_V2_FORMAT) == BIN2_V2_HEADER_SIZE

# v3 Header (96 bytes): magic(4) + version(2) + header_size(2) + payload_size(4)
#   + key_id(1) + binding_mode(1) + payload_enc_mode(1) + enc_reserved(1)
#   + binding_id(16) + payload_hash(32) + payload_iv(16) + reserved2(16)
HEADER_V3_FORMAT = '<4sHHIBBBB16s32s16s16s'
assert struct.calcsize(HEADER_V3_FORMAT) == BIN2_V3_HEADER_SIZE

# KDF salt (must match C-side bin2_crypto_payload.c)
PAYLOAD_KDF_SALT = b"AIOS-PAYLOAD-V1"
BINDING_KDF_SALT = b"AIOS-BIND-V1"


def derive_payload_key(device_secret, binding_id):
    """
    KDF: payload_key = SHA256(PAYLOAD_KDF_SALT || device_secret || binding_id)[0:16]
    Must match C-side bin2_crypto_payload.c:payload_derive_key()
    """
    h = hashlib.sha256()
    h.update(PAYLOAD_KDF_SALT)
    h.update(device_secret)
    h.update(binding_id)
    return h.digest()[:16]


def derive_binding_id(device_secret):
    """
    Derive binding_id from device_secret (for .bind file alternative).
    Must match C-side device_binding.c:binding_derive_id()
    """
    h = hashlib.sha256()
    h.update(BINDING_KDF_SALT)
    h.update(device_secret)
    full = h.digest()
    return full[:BIN2_BINDING_ID_SIZE]


def aes_ctr_encrypt(key, iv, plaintext):
    """
    AES-128-CTR encryption.
    Uses pycryptodome with nonce=b'' and initial_value=iv (full 16-byte counter).
    ⚠️ Must match C-side dap_aes_ctr_xcrypt() exactly.
    """
    try:
        from Crypto.Cipher import AES
        from Crypto.Util import Counter
    except ImportError:
        print("ERROR: pycryptodome not installed. Run: pip install pycryptodome")
        sys.exit(1)

    # 将 IV 视为 128-bit 大端整数初始值
    iv_int = int.from_bytes(iv, byteorder='big')
    ctr = Counter.new(128, initial_value=iv_int)
    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    return cipher.encrypt(plaintext)


def _print_debug_info(context, header_bytes, signature, payload, message, pubkey,
                      binding_mode=0, binding_id=None, enc_mode=0, iv=None):
    """Print diagnostic info matching device-side trace format."""
    total = len(message)
    msg_hash = hashlib.sha256(message).digest()
    hdr_size = len(header_bytes)

    print(f"\n=== TM-28 DEBUG ({context}) ===")
    print(f"tm15_sig_verify: total={total} hdr={hdr_size}"
          f" sig={BIN2_SIGNATURE_SIZE} pay={len(payload)}")
    print(f"tm15_sig_verify: payload_off={hdr_size + BIN2_SIGNATURE_SIZE}"
          f" signed_region_len={total}")
    print(f"tm15_sig[0..7]={' '.join(f'{b:02x}' for b in signature[:8])}")
    print(f"tm15_pubkey[0..7]={' '.join(f'{b:02x}' for b in pubkey[:8])}")
    print(f"tm15_hdr[0..7]={' '.join(f'{b:02x}' for b in header_bytes[:8])}")
    print(f"tm15_payload[0..7]={' '.join(f'{b:02x}' for b in payload[:8])}")
    print(f"tm15_msg_hash[0..7]={' '.join(f'{b:02x}' for b in msg_hash[:8])}")
    if binding_id:
        print(f"[BIND] mode={'DEVICE_BOUND' if binding_mode == 1 else 'UNBOUND'}"
              f" id={binding_id.hex()}")
    if enc_mode:
        print(f"tm28_enc_mode={enc_mode}")
        if iv:
            print(f"tm28_iv[0..7]={' '.join(f'{b:02x}' for b in iv[:8])}")
    print(f"=== END DEBUG ===")


def load_bind_file(bind_path):
    """加载 .bind 文件，返回 binding_id bytes 和 device_secret bytes"""
    with open(bind_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'binding_id' not in data:
        print(f"ERROR: .bind file missing 'binding_id' field")
        sys.exit(1)

    hex_id = data['binding_id']
    if len(hex_id) != BIN2_BINDING_ID_SIZE * 2:
        print(f"ERROR: binding_id must be {BIN2_BINDING_ID_SIZE * 2} hex chars, got {len(hex_id)}")
        sys.exit(1)

    binding_id = bytes.fromhex(hex_id)

    # device_secret 可选（仅加密模式需要）
    device_secret = None
    if 'device_secret' in data:
        device_secret = bytes.fromhex(data['device_secret'])

    print(f"Loaded binding: id={hex_id}, alg={data.get('binding_alg', '?')}, "
          f"model={data.get('device_model', '?')}")
    return binding_id, device_secret, data


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

    vk_bytes = bytes(vk)
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


def pack_bin2(input_path, output_path, private_key_path, bind_file=None,
              encrypt=False, verbose=False, debug=False):
    """将 BIN1 打包为 BIN2 v2/v3"""

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

    # 确定 binding mode 和 binding_id
    binding_id = b'\x00' * BIN2_BINDING_ID_SIZE
    binding_mode = BIN2_BIND_UNBOUND
    device_secret = None

    if bind_file:
        binding_id, device_secret, bind_data = load_bind_file(bind_file)
        binding_mode = BIN2_BIND_DEVICE_BOUND

    # 加密检查
    if encrypt:
        if not bind_file:
            print("ERROR: --encrypt requires --bind-file (加密必须设备绑定)")
            sys.exit(1)
        if device_secret is None:
            print("ERROR: .bind file must contain 'device_secret' for encryption")
            print("HINT: 使用带 device_secret 的增强版 .bind 文件")
            sys.exit(1)

    # 确定版本
    if encrypt:
        version = BIN2_V3_VERSION
        header_size_val = BIN2_V3_HEADER_SIZE
        enc_mode = BIN2_ENC_AES128_CTR
    else:
        version = BIN2_V2_VERSION
        header_size_val = BIN2_V2_HEADER_SIZE
        enc_mode = BIN2_ENC_NONE

    # 计算明文 payload 的 SHA-256 hash（解密后用于验证）
    payload_hash = hashlib.sha256(payload).digest()
    assert len(payload_hash) == 32

    # 加密 payload
    payload_iv = b'\x00' * BIN2_IV_SIZE
    if encrypt:
        # 生成随机 IV
        payload_iv = os.urandom(BIN2_IV_SIZE)

        # 派生 payload key
        payload_key = derive_payload_key(device_secret, binding_id)

        if verbose:
            print(f"  Encrypting payload: AES-128-CTR")
            print(f"  IV: {payload_iv.hex()}")

        # AES-CTR 加密
        encrypted_payload = aes_ctr_encrypt(payload_key, payload_iv, payload)
        # 签名覆盖加密后的 payload
        sign_payload = encrypted_payload
    else:
        encrypted_payload = payload
        sign_payload = payload

    # 构造 header
    if version == BIN2_V3_VERSION:
        header = struct.pack(
            HEADER_V3_FORMAT,
            BIN2_MAGIC,             # magic
            version,                # version = 3
            header_size_val,        # header_size = 96
            payload_size,           # payload_size
            0,                      # key_id
            binding_mode,           # binding_mode
            enc_mode,               # payload_enc_mode (TM-28)
            0,                      # enc_reserved
            binding_id,             # binding_id (16 bytes)
            payload_hash,           # payload_hash (plaintext SHA-256)
            payload_iv,             # payload_iv (16 bytes) (TM-28)
            b'\x00' * 16           # reserved2 (16 bytes)
        )
    else:
        header = struct.pack(
            HEADER_V2_FORMAT,
            BIN2_MAGIC,
            version,
            header_size_val,
            payload_size,
            0,                      # key_id
            binding_mode,
            0,                      # reserved
            binding_id,
            payload_hash
        )

    assert len(header) == header_size_val

    # 签名覆盖：header + zeros(64) + payload（对于 v3，payload 是加密后的）
    # ADR-002: signature 区域清零后签名
    sig_placeholder = b'\x00' * BIN2_SIGNATURE_SIZE
    message = header + sig_placeholder + sign_payload

    # Ed25519 签名
    signed = sk.sign(message, encoder=RawEncoder)
    signature = signed.signature
    assert len(signature) == BIN2_SIGNATURE_SIZE

    # 组装 BIN2/BIN3 文件
    bin2_data = header + signature + encrypted_payload

    # 写入输出文件
    with open(output_path, 'wb') as f:
        f.write(bin2_data)

    if verbose:
        ext = 'bin3' if encrypt else 'bin2'
        print(f"BIN2 v{version} packed successfully:")
        print(f"  Input:         {input_path} ({payload_size} bytes)")
        print(f"  Output:        {output_path} ({len(bin2_data)} bytes)")
        print(f"  Header:        {header_size_val} bytes (v{version})")
        print(f"  Signature:     {BIN2_SIGNATURE_SIZE} bytes")
        print(f"  Payload:       {payload_size} bytes")
        print(f"  Payload hash:  {payload_hash.hex()}")
        print(f"  Binding mode:  {'DEVICE_BOUND' if binding_mode else 'UNBOUND'}")
        if binding_mode:
            print(f"  Binding ID:    {binding_id.hex()}")
        if encrypt:
            print(f"  Encryption:    AES-128-CTR")
            print(f"  IV:            {payload_iv.hex()}")
        print(f"  Signature hex: {signature.hex()[:32]}...")
    else:
        enc_str = " +encrypted" if encrypt else ""
        bind_str = f"DEVICE_BOUND" if binding_mode else "UNBOUND"
        print(f"OK: {input_path} ({payload_size}B) -> {output_path} ({len(bin2_data)}B)"
              f" v{version} {bind_str}{enc_str}")

    if debug:
        _print_debug_info('pack', header, signature, sign_payload, message,
                          bytes(sk.verify_key), binding_mode, binding_id,
                          enc_mode, payload_iv if encrypt else None)

    return bin2_data


def verify_bin2(bin2_path, public_key_path, verbose=False, debug=False):
    """验证 BIN2 v2/v3 文件"""

    with open(public_key_path, 'rb') as f:
        vk_bytes = f.read()
    vk = VerifyKey(vk_bytes)

    with open(bin2_path, 'rb') as f:
        data = f.read()

    # 至少需要 magic(4) + version(2) + header_size(2) = 8 字节来判断版本
    if len(data) < 8:
        print(f"FAIL: File too small ({len(data)} < 8)")
        return False

    # 先读前 8 字节确定版本和 header size
    magic = data[0:4]
    if magic != BIN2_MAGIC:
        print(f"FAIL: Bad magic {magic}")
        return False

    file_version = struct.unpack_from('<H', data, 4)[0]
    file_header_size = struct.unpack_from('<H', data, 6)[0]

    # 确定使用哪个解析格式
    if file_header_size == BIN2_V3_HEADER_SIZE:
        header_format = HEADER_V3_FORMAT
        header_size = BIN2_V3_HEADER_SIZE
        payload_offset = BIN2_V3_PAYLOAD_OFFSET
    elif file_header_size == BIN2_V2_HEADER_SIZE:
        header_format = HEADER_V2_FORMAT
        header_size = BIN2_V2_HEADER_SIZE
        payload_offset = BIN2_V2_PAYLOAD_OFFSET
    else:
        print(f"FAIL: Unknown header_size {file_header_size}")
        return False

    if len(data) < payload_offset:
        print(f"FAIL: File too small ({len(data)} < {payload_offset})")
        return False

    # 解析 header
    header_bytes = data[:header_size]

    if file_header_size == BIN2_V3_HEADER_SIZE:
        (magic, version, hdr_size, payload_size, key_id, binding_mode,
         enc_mode, enc_reserved, binding_id, payload_hash,
         payload_iv, reserved2) = struct.unpack(header_format, header_bytes)
    else:
        (magic, version, hdr_size, payload_size, key_id, binding_mode,
         reserved, binding_id, payload_hash) = struct.unpack(header_format, header_bytes)
        enc_mode = BIN2_ENC_NONE
        payload_iv = b'\x00' * BIN2_IV_SIZE

    if verbose:
        print(f"Header: version={version}, header_size={hdr_size}, "
              f"payload_size={payload_size}, key_id={key_id}")
        print(f"  Binding: {'DEVICE_BOUND' if binding_mode else 'UNBOUND'}")
        if binding_mode:
            print(f"  Binding ID: {binding_id.hex()}")
        if enc_mode:
            print(f"  Encryption: AES-128-CTR (enc_mode={enc_mode})")
            print(f"  IV: {payload_iv.hex()}")

    # 提取 signature 和 payload
    signature = data[header_size:payload_offset]
    payload = data[payload_offset:]

    if len(payload) != payload_size:
        print(f"FAIL: Payload size mismatch ({len(payload)} != {payload_size})")
        return False

    # 验证签名（message = header + zeros + payload, payload 此处是加密状态）
    message = header_bytes + (b'\x00' * BIN2_SIGNATURE_SIZE) + payload
    try:
        vk.verify(message, signature, encoder=RawEncoder)
        if verbose:
            print("Signature: OK")
    except Exception as e:
        print(f"FAIL: Signature verification failed: {e}")
        if debug:
            _print_debug_info('verify', header_bytes, signature, payload,
                              message, vk_bytes, binding_mode, binding_id,
                              enc_mode, payload_iv if enc_mode else None)
        return False

    # 对于非加密文件，直接验证 hash
    # 对于加密文件，PC 端无 DeviceSecret 无法解密，只验证签名
    if enc_mode == BIN2_ENC_NONE:
        computed_hash = hashlib.sha256(payload).digest()
        if computed_hash != payload_hash:
            print(f"FAIL: Hash mismatch")
            return False
        if verbose:
            print("Hash: OK")
    else:
        if verbose:
            print("Hash: SKIP (encrypted payload, need device-side decrypt to verify)")

    if debug:
        _print_debug_info('verify', header_bytes, signature, payload,
                          message, vk_bytes, binding_mode, binding_id,
                          enc_mode, payload_iv if enc_mode else None)

    # Summary
    if binding_mode == BIN2_BIND_DEVICE_BOUND:
        print(f"Binding: DEVICE_BOUND (id={binding_id.hex()})")
    else:
        print(f"Binding: UNBOUND")

    if enc_mode:
        print(f"Encryption: AES-128-CTR (IV={payload_iv.hex()[:16]}...)")
    else:
        print(f"Encryption: NONE (plaintext)")

    print(f"VERIFY OK: {bin2_path} (v{version})")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='BIN2 v2/v3 Secure Packer for AIOS DAP '
                    '(Phase-2: Device Binding + Payload Encryption)')
    parser.add_argument('input', nargs='?', help='Input BIN1 file')
    parser.add_argument('output', nargs='?', help='Output BIN2/BIN3 file')
    parser.add_argument('--key', default='private_key.bin',
                        help='Private key file (default: private_key.bin)')
    parser.add_argument('--pubkey', default='public_key.bin',
                        help='Public key file (for --verify)')
    parser.add_argument('--generate-keys', action='store_true',
                        help='Generate Ed25519 keypair')
    parser.add_argument('--verify', action='store_true',
                        help='Verify a BIN2/BIN3 file')
    parser.add_argument('--bind-file', default=None,
                        help='Path to device.bind file (enables DEVICE_BOUND mode)')
    parser.add_argument('--encrypt', action='store_true',
                        help='TM-28: Enable AES-128-CTR payload encryption (requires --bind-file)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    parser.add_argument('--debug', action='store_true',
                        help='Print diagnostic info matching device-side trace format')

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

    pack_bin2(args.input, args.output, args.key,
              bind_file=args.bind_file, encrypt=args.encrypt,
              verbose=args.verbose, debug=args.debug)


if __name__ == '__main__':
    main()
