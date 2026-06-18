#!/usr/bin/env python3
"""
AIOS API Scanner

Scans C/H source files for API function signatures and outputs them
in a format suitable for registration in AIOS/registry/apis.yaml.

Usage:
    python api_scanner.py --help
    python api_scanner.py --path <source_path> [--pattern <pattern>] [--output <format>]

Examples:
    python api_scanner.py --path ../../Third-party/DAP/ --pattern "DAP_*"
    python api_scanner.py --path ../../MS_MMI_Main/ --pattern "MMI*" --output yaml
"""

import argparse
import os
import re
import sys


# Common API patterns in the AIOS codebase
DEFAULT_PATTERNS = [
    r'\b(DAP_\w+)\s*\(',           # DAP_ prefixed functions
    r'\b(DAPS_\w+)\s*\(',          # DAPS_ prefixed functions
    r'\b(MMI\w+_\w+)\s*\(',        # MMI prefixed functions
    r'PUBLIC\s+\w+\s+(\w+)\s*\(',  # PUBLIC visibility functions
]

# File extensions to scan
SOURCE_EXTENSIONS = {'.c', '.h', '.cpp', '.hpp'}


def scan_file(filepath, patterns):
    """Scan a single file for API patterns."""
    apis = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                for pattern in patterns:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        api_name = match.group(1)
                        apis.append({
                            'name': api_name,
                            'file': filepath,
                            'line': line_num,
                            'context': line.strip(),
                        })
    except (IOError, OSError) as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
    return apis


def scan_directory(path, patterns):
    """Recursively scan a directory for API patterns."""
    all_apis = []
    for root, dirs, files in os.walk(path):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in SOURCE_EXTENSIONS:
                filepath = os.path.join(root, fname)
                all_apis.extend(scan_file(filepath, patterns))
    return all_apis


def format_text(apis):
    """Format API list as plain text."""
    if not apis:
        return "No APIs found."
    lines = []
    seen = set()
    for api in apis:
        if api['name'] not in seen:
            seen.add(api['name'])
            lines.append(f"{api['name']}  ({api['file']}:{api['line']})")
    return '\n'.join(lines)


def format_yaml(apis):
    """Format API list as YAML for registry."""
    if not apis:
        return "apis: []"
    lines = ["apis:"]
    seen = set()
    for api in apis:
        if api['name'] not in seen:
            seen.add(api['name'])
            lines.append(f"  - api: {api['name']}")
            lines.append(f"    source_file: {api['file']}")
            lines.append(f"    source_line: {api['line']}")
            lines.append(f"    owner: TBD")
            lines.append(f"    stability: TBD")
            lines.append(f"    description: TBD")
            lines.append("")
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='AIOS API Scanner — Scan source files for API signatures',
        epilog='Part of the AIOS Memo-Driven Development Workflow'
    )
    parser.add_argument(
        '--path', required=True,
        help='Source file or directory to scan'
    )
    parser.add_argument(
        '--pattern', default=None,
        help='Custom regex pattern to search for (default: built-in DAP/DAPS/MMI patterns)'
    )
    parser.add_argument(
        '--output', choices=['text', 'yaml'], default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--extensions', nargs='+', default=None,
        help='File extensions to scan (default: .c .h .cpp .hpp)'
    )

    args = parser.parse_args()

    # Build pattern list
    if args.pattern:
        patterns = [args.pattern]
    else:
        patterns = DEFAULT_PATTERNS

    # Override extensions if specified
    if args.extensions:
        global SOURCE_EXTENSIONS
        SOURCE_EXTENSIONS = {f'.{ext.lstrip(".")}' for ext in args.extensions}

    # Scan
    path = args.path
    if os.path.isfile(path):
        apis = scan_file(path, patterns)
    elif os.path.isdir(path):
        apis = scan_directory(path, patterns)
    else:
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.output == 'yaml':
        print(format_yaml(apis))
    else:
        print(format_text(apis))

    # Summary to stderr
    unique = len(set(a['name'] for a in apis))
    print(f"\n--- Found {unique} unique APIs in {len(apis)} occurrences ---",
          file=sys.stderr)


if __name__ == '__main__':
    main()
