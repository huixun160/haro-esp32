#!/usr/bin/env python3
"""
verify_workflow_paths.py — Scan AIOS workflow files for broken cross-references.

Scans all .md files under .agents/workflows/ and AIOS/workflow/ for path
references to other AIOS files. Reports any referenced paths that don't exist.

Usage:
    python AIOS/scripts/verify_workflow_paths.py
"""

import os
import re
import sys

# Project root is two levels up from AIOS/scripts/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))

# Directories to scan for workflow files
SCAN_DIRS = [
    os.path.join(PROJECT_ROOT, '.agents', 'workflows'),
    os.path.join(PROJECT_ROOT, 'AIOS', 'workflow'),
]

# Pattern to match path references in backticks: `AIOS/...` or `.agents/...`
PATH_PATTERN = re.compile(r'`((?:AIOS|\.agents)/[^\s`*]+\.(?:md|yaml|py))`')

# Patterns to exclude (templates with placeholders)
EXCLUDE_PATTERNS = [
    'TM-XXX',
    'TM-<number>',
    '<memo_number>',
    '<short_name>',
    '<source_path>',
    '/xxx.',
    '<name>',
    '<project_id>',
    '<engineer>',
    '<project>',
    '<ACTIVE_ENGINEER>',
    '<ACTIVE_PROJECT>',
]


def find_md_files(directory):
    """Recursively find all .md files in a directory."""
    md_files = []
    if not os.path.isdir(directory):
        return md_files
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith('.md'):
                md_files.append(os.path.join(root, f))
    return md_files


def extract_path_references(filepath):
    """Extract all AIOS/... and .agents/... path references from a file."""
    refs = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            for match in PATH_PATTERN.finditer(line):
                path_ref = match.group(1)
                # Skip template placeholders
                if any(excl in path_ref for excl in EXCLUDE_PATTERNS):
                    continue
                refs.append((line_num, path_ref))
    return refs


def verify_path(path_ref):
    """Check if a referenced path exists relative to project root."""
    full_path = os.path.join(PROJECT_ROOT, path_ref)
    return os.path.exists(full_path)


def main():
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Scanning workflow files for broken cross-references...\n")

    all_files = []
    for scan_dir in SCAN_DIRS:
        all_files.extend(find_md_files(scan_dir))

    if not all_files:
        print("[WARN] No .md files found to scan")
        sys.exit(1)

    total_refs = 0
    broken_refs = []
    valid_refs = 0

    for filepath in sorted(all_files):
        rel_path = os.path.relpath(filepath, PROJECT_ROOT)
        refs = extract_path_references(filepath)
        if not refs:
            continue

        for line_num, path_ref in refs:
            total_refs += 1
            if verify_path(path_ref):
                valid_refs += 1
            else:
                broken_refs.append((rel_path, line_num, path_ref))

    # Report
    print(f"Files scanned:  {len(all_files)}")
    print(f"References found: {total_refs}")
    print(f"Valid:          {valid_refs}")
    print(f"Broken:         {len(broken_refs)}")
    print()

    if broken_refs:
        print("BROKEN REFERENCES:")
        print("-" * 60)
        for source, line, target in broken_refs:
            print(f"  {source}:{line}")
            print(f"    -> {target}")
            print()
        sys.exit(1)
    else:
        print("[OK] All cross-references are valid.")
        sys.exit(0)


if __name__ == '__main__':
    main()
