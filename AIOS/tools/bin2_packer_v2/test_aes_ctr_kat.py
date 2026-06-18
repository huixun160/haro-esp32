#!/usr/bin/env python3
"""
AES-128-CTR Known-Answer Test — TM-28 坑2 防范

验证 Python pycryptodome 和 C dap_aes 的 CTR 计数器一致性。
生成一组已知向量，C 端和 Python 端必须产生相同的密文。

NIST SP 800-38A F.5.1/F.5.2 AES-128 CTR Test Vectors:
  Key:       2b7e151628aed2a6abf7158809cf4f3c
  IV/CTR:    f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff
  Plaintext: 6bc1bee22e409f96e93d7e117393172a
              ae2d8a571e03ac9c9eb76fac45af8e51
              30c81c46a35ce411e5fbc1191a0a52ef
              f69f2445df4f9b17ad2b417be66c3710
  Ciphertext:874d6191b620e3261bef6864990db6ce
              9806f66b7970fdff8617187bb9fffdff
              5ae4df3edbd5d35e5b4f09020db03eab
              1e031dda2fbe03d1792170a0f3009cee

用法:
  python test_aes_ctr_kat.py              # 运行测试
  python test_aes_ctr_kat.py --generate   # 生成 C 测试向量代码
"""

import sys

def run_kat():
    """Run NIST AES-128-CTR known-answer test"""
    try:
        from Crypto.Cipher import AES
        from Crypto.Util import Counter
    except ImportError:
        print("ERROR: pycryptodome not installed. Run: pip install pycryptodome")
        sys.exit(1)

    # NIST SP 800-38A F.5.1 AES-128-CTR vectors
    key = bytes.fromhex('2b7e151628aed2a6abf7158809cf4f3c')
    iv  = bytes.fromhex('f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff')

    plaintext = bytes.fromhex(
        '6bc1bee22e409f96e93d7e117393172a'
        'ae2d8a571e03ac9c9eb76fac45af8e51'
        '30c81c46a35ce411e5fbc1191a0a52ef'
        'f69f2445df4f9b17ad2b417be66c3710'
    )

    expected_ct = bytes.fromhex(
        '874d6191b620e3261bef6864990db6ce'
        '9806f66b7970fdff8617187bb9fffdff'
        '5ae4df3edbd5d35e5b4f09020db03eab'
        '1e031dda2fbe03d1792170a0f3009cee'
    )

    # Use same Counter setup as bin2_pack.py:
    # nonce=b'', full 128-bit big-endian initial_value
    iv_int = int.from_bytes(iv, byteorder='big')
    ctr = Counter.new(128, initial_value=iv_int)
    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    ciphertext = cipher.encrypt(plaintext)

    print("=== AES-128-CTR Known-Answer Test (NIST SP 800-38A F.5.1) ===")
    print(f"Key:        {key.hex()}")
    print(f"IV:         {iv.hex()}")
    print(f"Plaintext:  {plaintext.hex()[:32]}...")
    print(f"Expected:   {expected_ct.hex()[:32]}...")
    print(f"Got:        {ciphertext.hex()[:32]}...")

    if ciphertext == expected_ct:
        print("PASS ✓ Python CTR matches NIST vector")
    else:
        print("FAIL ✗ Python CTR does NOT match NIST vector!")
        print(f"  Expected: {expected_ct.hex()}")
        print(f"  Got:      {ciphertext.hex()}")
        return False

    # Also test non-aligned length (7 bytes)
    short_pt = bytes.fromhex('6bc1bee22e409f')  # 7 bytes
    iv_int2 = int.from_bytes(iv, byteorder='big')
    ctr2 = Counter.new(128, initial_value=iv_int2)
    cipher2 = AES.new(key, AES.MODE_CTR, counter=ctr2)
    short_ct = cipher2.encrypt(short_pt)
    # Should match first 7 bytes of NIST ciphertext
    expected_short = expected_ct[:7]

    print(f"\nNon-aligned test (7 bytes):")
    print(f"  Expected: {expected_short.hex()}")
    print(f"  Got:      {short_ct.hex()}")

    if short_ct == expected_short:
        print("  PASS ✓ Non-aligned CTR works correctly")
    else:
        print("  FAIL ✗ Non-aligned CTR mismatch!")
        return False

    # Decrypt test (CTR encrypt == decrypt)
    iv_int3 = int.from_bytes(iv, byteorder='big')
    ctr3 = Counter.new(128, initial_value=iv_int3)
    cipher3 = AES.new(key, AES.MODE_CTR, counter=ctr3)
    decrypted = cipher3.encrypt(ciphertext)  # CTR: encrypt==decrypt

    if decrypted == plaintext:
        print(f"\nRoundtrip test:")
        print(f"  PASS ✓ encrypt->decrypt recovers plaintext")
    else:
        print(f"\nRoundtrip test:")
        print(f"  FAIL ✗ roundtrip mismatch!")
        return False

    print("\n=== ALL KAT TESTS PASSED ===")
    return True


def generate_c_vectors():
    """Generate C code for device-side KAT"""
    print("""
// AES-128-CTR Known-Answer Test (NIST SP 800-38A F.5.1)
// Copy this into a test function on device-side

static void tm28_aes_ctr_kat(void) {
    static const uint8 key[16] = {
        0x2b,0x7e,0x15,0x16,0x28,0xae,0xd2,0xa6,
        0xab,0xf7,0x15,0x88,0x09,0xcf,0x4f,0x3c
    };
    static const uint8 iv[16] = {
        0xf0,0xf1,0xf2,0xf3,0xf4,0xf5,0xf6,0xf7,
        0xf8,0xf9,0xfa,0xfb,0xfc,0xfd,0xfe,0xff
    };
    static const uint8 plaintext[64] = {
        0x6b,0xc1,0xbe,0xe2,0x2e,0x40,0x9f,0x96,
        0xe9,0x3d,0x7e,0x11,0x73,0x93,0x17,0x2a,
        0xae,0x2d,0x8a,0x57,0x1e,0x03,0xac,0x9c,
        0x9e,0xb7,0x6f,0xac,0x45,0xaf,0x8e,0x51,
        0x30,0xc8,0x1c,0x46,0xa3,0x5c,0xe4,0x11,
        0xe5,0xfb,0xc1,0x19,0x1a,0x0a,0x52,0xef,
        0xf6,0x9f,0x24,0x45,0xdf,0x4f,0x9b,0x17,
        0xad,0x2b,0x41,0x7b,0xe6,0x6c,0x37,0x10
    };
    static const uint8 expected_ct[64] = {
        0x87,0x4d,0x61,0x91,0xb6,0x20,0xe3,0x26,
        0x1b,0xef,0x68,0x64,0x99,0x0d,0xb6,0xce,
        0x98,0x06,0xf6,0x6b,0x79,0x70,0xfd,0xff,
        0x86,0x17,0x18,0x7b,0xb9,0xff,0xfd,0xff,
        0x5a,0xe4,0xdf,0x3e,0xdb,0xd5,0xd3,0x5e,
        0x5b,0x4f,0x09,0x02,0x0d,0xb0,0x3e,0xab,
        0x1e,0x03,0x1d,0xda,0x2f,0xbe,0x03,0xd1,
        0x79,0x21,0x70,0xa0,0xf3,0x00,0x9c,0xee
    };

    uint8 buf[64];
    uint8 iv_copy[16];
    DAP_AES_ctx ctx;
    int i, pass = 1;

    memcpy(buf, plaintext, 64);
    memcpy(iv_copy, iv, 16);

    dap_aes_init(&ctx, key);
    dap_aes_ctr_xcrypt(&ctx, iv_copy, buf, 64);

    for (i = 0; i < 64; ++i) {
        if (buf[i] != expected_ct[i]) {
            SCI_TRACE_LOW("tm28_kat FAIL at byte %d: got 0x%02x expected 0x%02x",
                          i, buf[i], expected_ct[i]);
            pass = 0;
            break;
        }
    }

    if (pass) {
        SCI_TRACE_LOW("tm28_kat PASS: AES-128-CTR matches NIST vector");
    }
}
""")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='AES-128-CTR Known-Answer Test')
    parser.add_argument('--generate', action='store_true',
                        help='Generate C test code')
    args = parser.parse_args()

    if args.generate:
        generate_c_vectors()
    else:
        success = run_kat()
        sys.exit(0 if success else 1)
