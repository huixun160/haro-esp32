#!/usr/bin/env python3
"""
API Guard — Pre-commit hook script

Detects newly introduced public APIs in staged files and checks if they
are registered in AIOS/registry/apis.yaml.

Warn-only (v1): never blocks commit.
"""

import os
import re
import subprocess
import sys

# Resolve project root (hooks/scripts/ -> project root)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
REGISTRY_PATH = os.path.join(PROJECT_ROOT, 'AIOS', 'registry', 'apis.yaml')

# API patterns to detect
API_PATTERNS = [
    re.compile(r'\b(DAP_\w+)\s*\('),
    re.compile(r'\b(DAPS_\w+)\s*\('),
]

SOURCE_EXTENSIONS = {'.c', '.h', '.cpp', '.hpp'}


def get_staged_files():
    """Get list of staged source files."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=5
        )
        files = result.stdout.strip().split('\n')
        return [f for f in files if f and os.path.splitext(f)[1].lower() in SOURCE_EXTENSIONS]
    except Exception:
        return []


def load_registered_apis():
    """Load API names from registry."""
    apis = set()
    if not os.path.exists(REGISTRY_PATH):
        return apis
    try:
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('- api:') or line.startswith('api:'):
                    api_name = line.split(':', 1)[1].strip()
                    apis.add(api_name)
    except Exception:
        pass
    return apis


def scan_file_for_apis(filepath):
    """Scan a file for API function definitions/declarations."""
    found = set()
    try:
        full_path = os.path.join(PROJECT_ROOT, filepath)
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                for pattern in API_PATTERNS:
                    for match in pattern.finditer(line):
                        found.add(match.group(1))
    except Exception:
        pass
    return found


def main():
    staged = get_staged_files()
    if not staged:
        return

    registered = load_registered_apis()
    unregistered = set()

    for filepath in staged:
        apis = scan_file_for_apis(filepath)
        for api in apis:
            if api not in registered:
                unregistered.add(api)

    if unregistered:
        print("\n\033[33m⚠ API GUARD WARNING:\033[0m")
        print("  The following APIs were detected but are NOT registered")
        print("  in AIOS/registry/apis.yaml:\n")
        for api in sorted(unregistered):
            print(f"    • {api}")
        print("\n  Please update the registry using the /aios-workflow.\n")


if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass  # fail-open
