#!/usr/bin/env python3
"""
read_bindfile.py — 读取并验证 device.bind 文件

用法:
    python read_bindfile.py device.bind
    python read_bindfile.py D:/Filearray/device.bind

输出:
    - JSON 格式校验
    - binding_id 提取
    - 字段完整性检查

TM: TM-26 (Phase 1B — Bindfile Export)
"""

import json
import sys
import os

# 必需字段
REQUIRED_FIELDS = ["version", "binding_alg", "binding_id", "device_model"]
EXPECTED_BINDING_ALG = "SHA256-128"
EXPECTED_BINDING_ID_LEN = 32  # 16 bytes = 32 hex chars


def read_bindfile(filepath):
    """读取并验证 device.bind 文件，返回解析后的 dict"""
    if not os.path.isfile(filepath):
        print(f"[FAIL] File not found: {filepath}")
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    # JSON 解析
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[FAIL] Invalid JSON: {e}")
        return None

    print(f"[OK] JSON parsed successfully")

    # 字段检查
    ok = True
    for field in REQUIRED_FIELDS:
        if field not in data:
            print(f"[FAIL] Missing field: {field}")
            ok = False
        else:
            print(f"[OK] {field} = {data[field]}")

    if not ok:
        return None

    # binding_id 格式检查
    bid = data["binding_id"]
    if len(bid) != EXPECTED_BINDING_ID_LEN:
        print(f"[WARN] binding_id length: {len(bid)} (expected {EXPECTED_BINDING_ID_LEN})")
    try:
        int(bid, 16)
        print(f"[OK] binding_id is valid hex")
    except ValueError:
        print(f"[FAIL] binding_id is not valid hex: {bid}")

    # binding_alg 检查
    if data["binding_alg"] != EXPECTED_BINDING_ALG:
        print(f"[WARN] binding_alg: {data['binding_alg']} (expected {EXPECTED_BINDING_ALG})")

    return data


def main():
    if len(sys.argv) < 2:
        print("Usage: python read_bindfile.py <path-to-device.bind>")
        print("Example: python read_bindfile.py Filearray/device.bind")
        sys.exit(1)

    filepath = sys.argv[1]
    print(f"--- Reading: {filepath} ---")
    data = read_bindfile(filepath)

    if data:
        print(f"\n--- Result ---")
        print(f"binding_id = {data['binding_id']}")
        print(f"device_model = {data['device_model']}")
        print(f"version = {data['version']}")
    else:
        print(f"\n[FAIL] Bindfile validation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
