#!/usr/bin/env python3
"""
AIOS Sync Summary Generator

Reads AIOS registry YAML files and generates a summary of changes
since the last sync point.

Usage:
    python generate_sync_summary.py --help
    python generate_sync_summary.py --registry <registry_dir> [--since <git_ref>]
    python generate_sync_summary.py --registry <registry_dir> --output <file>

Examples:
    python generate_sync_summary.py --registry ../registry/
    python generate_sync_summary.py --registry ../registry/ --since HEAD~1
    python generate_sync_summary.py --registry ../registry/ --output sync_report.md
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime


def get_git_diff(filepath, since='HEAD~1'):
    """Get git diff for a file since a given reference."""
    try:
        result = subprocess.run(
            ['git', 'diff', since, '--', filepath],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout
    except (subprocess.SubprocessError, FileNotFoundError):
        return ""


def parse_yaml_additions(diff_text, key_field):
    """Parse added entries from a git diff of a YAML file."""
    additions = []
    current_entry = None

    for line in diff_text.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            clean = line[1:].strip()
            if clean.startswith(f'- {key_field}:'):
                if current_entry:
                    additions.append(current_entry)
                current_entry = clean.split(':', 1)[1].strip()
            elif current_entry and ':' in clean:
                pass  # metadata line, skip
        else:
            if current_entry:
                additions.append(current_entry)
                current_entry = None

    if current_entry:
        additions.append(current_entry)

    return additions


def generate_summary(registry_dir, since='HEAD~1'):
    """Generate a sync summary from registry changes."""
    sections = []

    # APIs
    apis_file = os.path.join(registry_dir, 'apis.yaml')
    if os.path.exists(apis_file):
        diff = get_git_diff(apis_file, since)
        new_apis = parse_yaml_additions(diff, 'api')
        if new_apis:
            sections.append(('New APIs', new_apis))

    # Modules
    modules_file = os.path.join(registry_dir, 'modules.yaml')
    if os.path.exists(modules_file):
        diff = get_git_diff(modules_file, since)
        new_modules = parse_yaml_additions(diff, 'module')
        if new_modules:
            sections.append(('New Modules', new_modules))

    # Migration
    migration_file = os.path.join(registry_dir, 'migration-status.yaml')
    if os.path.exists(migration_file):
        diff = get_git_diff(migration_file, since)
        updates = parse_yaml_additions(diff, 'legacy_api')
        if updates:
            sections.append(('Migration Updates', updates))

    # Decisions
    decisions_file = os.path.join(registry_dir, 'decisions.yaml')
    if os.path.exists(decisions_file):
        diff = get_git_diff(decisions_file, since)
        new_decisions = parse_yaml_additions(diff, 'title')
        if new_decisions:
            sections.append(('New Decisions', new_decisions))

    return sections


def format_markdown(sections, since):
    """Format summary as markdown."""
    lines = [
        f"# AIOS Sync Summary",
        f"",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Since:** `{since}`",
        f"",
        f"---",
        f"",
    ]

    if not sections:
        lines.append("No registry changes detected since last sync.")
    else:
        for title, items in sections:
            lines.append(f"## {title}")
            lines.append("")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='AIOS Sync Summary Generator — Generate registry change summaries',
        epilog='Part of the AIOS Memo-Driven Development Workflow'
    )
    parser.add_argument(
        '--registry', required=True,
        help='Path to the AIOS registry directory'
    )
    parser.add_argument(
        '--since', default='HEAD~1',
        help='Git reference to compare against (default: HEAD~1)'
    )
    parser.add_argument(
        '--output', default=None,
        help='Output file path (default: stdout)'
    )

    args = parser.parse_args()

    if not os.path.isdir(args.registry):
        print(f"Error: Registry directory not found: {args.registry}",
              file=sys.stderr)
        sys.exit(1)

    sections = generate_summary(args.registry, args.since)
    report = format_markdown(sections, args.since)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Summary written to: {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == '__main__':
    main()
