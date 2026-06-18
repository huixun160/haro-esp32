#!/usr/bin/env python3
"""
Pitfall Guard — Pre-commit hook script

Detects bug-fix-related keywords in commit messages and reminds
engineers to update the pitfalls documentation.

Warn-only (v1): never blocks commit.
"""

import os
import re
import sys

# Resolve project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
COMMIT_MSG_FILE = os.path.join(PROJECT_ROOT, '.git', 'COMMIT_EDITMSG')

# Keywords that suggest a bug fix
BUG_KEYWORDS = re.compile(
    r'\b(fix|bug|crash|panic|segfault|workaround|hotfix|patch|regression)\b',
    re.IGNORECASE
)

PITFALLS_DIR = os.path.join(PROJECT_ROOT, 'AIOS', 'docs', 'pitfalls')


def get_commit_message():
    """Read the commit message."""
    if os.path.exists(COMMIT_MSG_FILE):
        try:
            with open(COMMIT_MSG_FILE, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            pass

    if len(sys.argv) > 1:
        msg_file = sys.argv[1]
        if os.path.exists(msg_file):
            try:
                with open(msg_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                pass

    return ""


def main():
    commit_msg = get_commit_message()
    if not commit_msg:
        return

    match = BUG_KEYWORDS.search(commit_msg)
    if match:
        keyword = match.group(1)
        print(f"\n\033[36m💡 PITFALL GUARD REMINDER:\033[0m")
        print(f"  Your commit message contains '{keyword}'.")
        print(f"  Consider documenting this in:")
        print(f"    AIOS/docs/pitfalls/")
        print()
        print(f"  Capturing pitfalls helps future engineers avoid the same issue.")
        print(f"  Template: symptom → root cause → fix → prevention\n")


if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass  # fail-open
