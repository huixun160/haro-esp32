#!/usr/bin/env python3
"""
AIOS API Registry Schema Validator
TM-35: Validates AIOS/registry/apis.yaml against schema rules.

Usage:
    python AIOS/scripts/validate_api_schema.py

Checks:
    1. YAML can be parsed (yaml.safe_load)
    2. All required fields present for each API entry
    3. Enum values are valid (module, level, stability, source)
    4. API names are unique (no duplicates)
    5. Every API has module and level (M6)
"""

import sys
import os
import yaml

# Schema definitions
VALID_MODULES = {
    'memory', 'filesystem', 'timer', 'debug', 'time',
    'gui', 'audio', 'security', 'loader', 'sdk',
    'network', 'device'
}

VALID_LEVELS = {'L1', 'L2', 'L3'}

VALID_STABILITY = {'stable', 'beta', 'alpha', 'unstable', 'deprecated'}

VALID_SOURCES = {'unisoc_os', 'unisoc_mmi', 'unisoc_audio', 'dap_custom'}

REQUIRED_FIELDS = [
    'api', 'module', 'level', 'stability', 'source',
    'layer_from', 'layer_to', 'input', 'output', 'description'
]


def validate(registry_path):
    errors = []
    warnings = []

    # 1. Parse YAML
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        errors.append(f"YAML parse error: {e}")
        return errors, warnings
    except FileNotFoundError:
        errors.append(f"File not found: {registry_path}")
        return errors, warnings

    if not data or 'apis' not in data:
        errors.append("Missing 'apis' root key")
        return errors, warnings

    apis = data['apis']
    if not isinstance(apis, list):
        errors.append("'apis' must be a list")
        return errors, warnings

    # 2. Check each entry
    seen_names = set()

    for i, entry in enumerate(apis):
        idx = f"Entry #{i+1}"

        if not isinstance(entry, dict):
            errors.append(f"{idx}: not a dict")
            continue

        api_name = entry.get('api', f'<unnamed-{i}>')
        idx = f"[{api_name}]"

        # Required fields
        for field in REQUIRED_FIELDS:
            if field not in entry:
                errors.append(f"{idx}: missing required field '{field}'")

        # Uniqueness
        if api_name in seen_names:
            errors.append(f"{idx}: duplicate API name")
        seen_names.add(api_name)

        # Enum validation
        module = entry.get('module')
        if module and module not in VALID_MODULES:
            errors.append(f"{idx}: invalid module '{module}' (valid: {VALID_MODULES})")

        level = entry.get('level')
        if level and level not in VALID_LEVELS:
            errors.append(f"{idx}: invalid level '{level}' (valid: {VALID_LEVELS})")

        stability = entry.get('stability')
        if stability and stability not in VALID_STABILITY:
            errors.append(f"{idx}: invalid stability '{stability}' (valid: {VALID_STABILITY})")

        source = entry.get('source')
        if source and source not in VALID_SOURCES:
            errors.append(f"{idx}: invalid source '{source}' (valid: {VALID_SOURCES})")

    # Summary
    print(f"Validated {len(apis)} API entries from {registry_path}")
    print(f"  Unique API names: {len(seen_names)}")
    print(f"  Errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")

    return errors, warnings


def main():
    # Find registry path relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    registry_path = os.path.join(project_root, 'AIOS', 'registry', 'apis.yaml')

    # Allow override via command line
    if len(sys.argv) > 1:
        registry_path = sys.argv[1]

    print(f"AIOS API Schema Validator (TM-35)")
    print(f"Registry: {registry_path}")
    print("=" * 60)

    errors, warnings = validate(registry_path)

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  [WARN] {w}")

    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  [FAIL] {e}")
        print(f"\nVALIDATION FAILED ({len(errors)} errors)")
        sys.exit(1)
    else:
        print("\n[OK] All checks passed!")
        sys.exit(0)


if __name__ == '__main__':
    main()
