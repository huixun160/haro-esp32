#!/usr/bin/env python3
"""
extract_bindingid.py — 从 Logel 导出文本中提取 BindingID

用法:
    python extract_bindingid.py logel_export.txt
    python extract_bindingid.py logel_export.txt --output device.bind

功能:
    1. 从 Logel 导出的文本中搜索 tm25_id 或 BIND derive traces
    2. 提取完整的 16 字节 BindingID
    3. 生成 device.bind JSON 文件

这是固件端文件导出的 PC 侧替代方案。当固件无法通过 SFS 写入
device.bind 时，可以用此工具从 Logel traces 中提取 BindingID。

TM: TM-26 (Phase 1B — Bindfile Export)
"""

import json
import re
import sys
import os


def extract_binding_id(logel_text):
    """从 Logel 文本中提取 BindingID

    搜索两种 trace 格式:
      1. tm25_id[0..7]=XX XX XX XX XX XX XX XX
         tm25_id[8..15]=XX XX XX XX XX XX XX XX
      2. tm26_binding_id=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    """

    # 方法 1: 从 tm26_binding_id 直接提取（32 hex chars）
    m = re.search(r'tm26_binding_id=([0-9a-fA-F]{32})', logel_text)
    if m:
        return m.group(1).lower()

    # 方法 2: 从 tm25_id 两段拼接
    m0 = re.search(r'tm25_id\[0\.\.7\]=([0-9a-fA-F ]{23})', logel_text)
    m1 = re.search(r'tm25_id\[8\.\.15\]=([0-9a-fA-F ]{23})', logel_text)
    if m0 and m1:
        hex_bytes = m0.group(1).split() + m1.group(1).split()
        return ''.join(hex_bytes).lower()

    # 方法 3: 从 BIND derive traces 提取
    derives = re.findall(r'derive: ID\[0\.\.7\]=([0-9a-fA-F ]{23})', logel_text)
    if derives:
        # 取第一个（所有 derive 应该相同）
        hex_bytes = derives[0].split()
        # 只有前 8 字节，需要从 tm25_id[8..15] 补全
        if m1:
            hex_bytes += m1.group(1).split()
            return ''.join(hex_bytes).lower()

    return None


def create_bindfile(binding_id, output_path):
    """生成 device.bind JSON 文件"""
    data = {
        "version": 1,
        "binding_alg": "SHA256-128",
        "binding_id": binding_id,
        "device_model": "ums9117"
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    return data


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_bindingid.py <logel-export.txt> [--output device.bind]")
        print()
        print("从 Logel 导出文本中提取 BindingID 并生成 device.bind 文件。")
        print("当功能机无法通过 SFS 直接生成文件时，使用此工具作为替代方案。")
        sys.exit(1)

    logel_path = sys.argv[1]
    output_path = "device.bind"

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    if not os.path.isfile(logel_path):
        print(f"[FAIL] File not found: {logel_path}")
        sys.exit(1)

    with open(logel_path, 'r', encoding='utf-8', errors='ignore') as f:
        logel_text = f.read()

    print(f"--- Parsing: {logel_path} ---")

    binding_id = extract_binding_id(logel_text)
    if not binding_id:
        print("[FAIL] Could not find BindingID in Logel export.")
        print("       Expected traces: tm25_id[0..7]=... or tm26_binding_id=...")
        sys.exit(1)

    print(f"[OK] BindingID = {binding_id}")

    # 验证
    if len(binding_id) != 32:
        print(f"[WARN] BindingID length: {len(binding_id)} (expected 32)")

    try:
        int(binding_id, 16)
        print(f"[OK] Valid hex")
    except ValueError:
        print(f"[FAIL] Not valid hex: {binding_id}")
        sys.exit(1)

    # 生成 device.bind
    data = create_bindfile(binding_id, output_path)
    print(f"[OK] Written: {output_path}")
    print(f"\n--- device.bind ---")
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
