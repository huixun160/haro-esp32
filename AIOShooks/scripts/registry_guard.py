#!/usr/bin/env python3
"""
Registry Guard — Pre-commit / pre-push hook script

Validates AIOS registry YAML files for:
- Valid YAML syntax
- Duplicate API names
- Missing module owners

Warn-only (v1): never blocks commit.
"""

import os
import sys

# Resolve project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
REGISTRY_DIR = os.path.join(PROJECT_ROOT, 'AIOS', 'registry')

REGISTRY_FILES = [
    'apis.yaml',
    'modules.yaml',
    'migration-status.yaml',
    'ownership.yaml',
    'decisions.yaml',
]


def check_yaml_syntax(filepath):
    """Basic YAML syntax check (no external dependencies)."""
    issues = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i, line in enumerate(lines, 1):
            stripped = line.rstrip()
            # Check for tabs (YAML uses spaces)
            if '\t' in line and not line.strip().startswith('#'):
                issues.append(f"  Line {i}: Tab character found (YAML requires spaces)")
            # Check for trailing content after list marker
            if stripped.strip().startswith('- ') and ': ' in stripped:
                # Valid YAML key-value in list
                pass
    except Exception as e:
        issues.append(f"  Could not read file: {e}")
    return issues


def check_duplicate_apis(filepath):
    """Check for duplicate API entries in apis.yaml."""
    issues = []
    apis = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                stripped = line.strip()
                if stripped.startswith('- api:') or (stripped.startswith('api:') and '  ' not in line):
                    api_name = stripped.split(':', 1)[1].strip()
                    if api_name and api_name != '[]':
                        if api_name in apis:
                            issues.append(f"  Line {line_num}: Duplicate API: {api_name}")
                        apis.append(api_name)
    except Exception:
        pass
    return issues


def check_module_owners(filepath):
    """Check for modules missing owner field in modules.yaml."""
    issues = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        current_module = None
        has_owner = False

        for line in content.split('\n'):
            stripped = line.strip()
            if stripped.startswith('- module:'):
                if current_module and not has_owner:
                    issues.append(f"  Module '{current_module}' has no owner defined")
                current_module = stripped.split(':', 1)[1].strip()
                has_owner = False
            elif stripped.startswith('owner:') and current_module:
                owner_val = stripped.split(':', 1)[1].strip()
                if owner_val and owner_val not in ('TBD', '""', "''", '[]'):
                    has_owner = True

        if current_module and not has_owner:
            issues.append(f"  Module '{current_module}' has no owner defined")
    except Exception:
        pass
    return issues


def main():
    all_issues = []

    for filename in REGISTRY_FILES:
        filepath = os.path.join(REGISTRY_DIR, filename)
        if not os.path.exists(filepath):
            continue

        # Syntax check
        issues = check_yaml_syntax(filepath)
        if issues:
            all_issues.append((filename, 'Syntax', issues))

        # Specific checks
        if filename == 'apis.yaml':
            issues = check_duplicate_apis(filepath)
            if issues:
                all_issues.append((filename, 'Duplicates', issues))

        if filename == 'modules.yaml':
            issues = check_module_owners(filepath)
            if issues:
                all_issues.append((filename, 'Ownership', issues))

    if all_issues:
        print("\n\033[33m⚠ REGISTRY GUARD WARNING:\033[0m")
        print("  Issues found in AIOS registry files:\n")
        for filename, check_type, issues in all_issues:
            print(f"  [{filename}] ({check_type}):")
            for issue in issues:
                print(f"  {issue}")
        print()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass  # fail-open
