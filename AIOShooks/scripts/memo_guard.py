#!/usr/bin/env python3
"""
Memo Guard — Pre-commit hook script

Ensures code changes are linked to a Technical Memo by checking
the commit message for a TM-XX pattern (e.g. TM-17-workflowhook).

Monitored source directories:
  Third-party/DAP/, MS_MMI_Main/, DAPS/, MS_Ref/, common/, BASE/

Warn-only (v1): never blocks commit.
"""

import os
import re
import subprocess
import sys

# Resolve project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
COMMIT_MSG_FILE = os.path.join(PROJECT_ROOT, '.git', 'COMMIT_EDITMSG')

# TM reference pattern: TM-<number> optionally followed by -<name>
TM_PATTERN = re.compile(r'TM-\d+', re.IGNORECASE)

# Source directories that require a memo reference
SOURCE_DIRS = [
    'Third-party/DAP/',
    'MS_MMI_Main/',
    'DAPS/',
    'MS_Ref/',
    'common/',
    'BASE/',
    'chip_drv/',
    'connectivity/',
    'RTOS/',
]


def get_staged_files():
    """Get list of staged files."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=5
        )
        return [f for f in result.stdout.strip().split('\n') if f]
    except Exception:
        return []


def has_source_changes(files):
    """Check if any staged file is in a monitored source directory."""
    for f in files:
        f_normalized = f.replace('\\', '/')
        for src_dir in SOURCE_DIRS:
            if f_normalized.startswith(src_dir):
                return True
    return False


def get_commit_message():
    """Read the commit message."""
    # Try COMMIT_EDITMSG first (available during commit)
    if os.path.exists(COMMIT_MSG_FILE):
        try:
            with open(COMMIT_MSG_FILE, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            pass

    # Fallback: try to get from command line arg
    if len(sys.argv) > 1:
        msg_file = sys.argv[1]
        if os.path.exists(msg_file):
            try:
                with open(msg_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                pass

    return ""


def check_memo_naming():
    """Check if staged memo files follow the naming convention."""
    staged = get_staged_files()
    if not staged:
        return

    # Pattern: <ENGINEER>_<PROJECT>_TM<XX>_<name>.md
    NAMING_PATTERN = re.compile(
        r'^[A-Za-z]+_[a-z_]+_TM\d+_[a-z0-9_]+\.md$'
    )

    bad_names = []
    for f in staged:
        f_normalized = f.replace('\\', '/')
        # Only check files in projects/*/technical_memos/
        if '/projects/' in f_normalized and '/technical_memos/' in f_normalized:
            basename = os.path.basename(f)
            if not NAMING_PATTERN.match(basename):
                bad_names.append(basename)

    if bad_names:
        print("\n\033[33m⚠ MEMO GUARD WARNING (naming):\033[0m")
        print("  The following memos do not follow the naming convention:")
        print("  Format: <ENGINEER>_<PROJECT>_TM<XX>_<name>.md\n")
        for name in bad_names:
            print(f"    • {name}")
        print("\n  Example: KaiwenZheng_featurephone_secure_TM01_loader.md\n")


def check_branch_naming():
    """Check if current branch follows eng/<engineer>/<project> pattern."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=5
        )
        branch = result.stdout.strip()
        if not branch or branch == 'HEAD':
            return

        BRANCH_PATTERN = re.compile(r'^eng/[A-Za-z]+/[a-z_]+$')
        if branch != 'main' and branch != 'master' and not BRANCH_PATTERN.match(branch):
            print("\n\033[33m⚠ MEMO GUARD WARNING (branch):\033[0m")
            print(f"  Current branch '{branch}' does not follow naming convention.")
            print("  Format: eng/<engineer>/<project>")
            print("  Example: eng/KaiwenZheng/featurephone_secure\n")
    except Exception:
        pass


def main():
    staged = get_staged_files()
    if not staged:
        return

    if not has_source_changes(staged):
        check_memo_naming()
        check_branch_naming()
        return

    commit_msg = get_commit_message()

    if not TM_PATTERN.search(commit_msg):
        print("\n\033[33m⚠ MEMO GUARD WARNING:\033[0m")
        print("  Commit contains source code changes but no Technical Memo reference.")
        print("  Please include a memo reference in your commit message, e.g.:")
        print()
        print("    TM-17-workflowhook implement git hooks governance")
        print()
        print("  Format: TM-<number>[-<short-name>] <description>")
        print("  Memos are stored in: AIOS/projects/*/technical_memos/\n")

    check_memo_naming()
    check_branch_naming()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass  # fail-open
