# Session Log — TM-17 Git Hooks Governance Layer

**Date:** 2026-03-09
**Engineer:** KaiwenZheng
**Memo:** Technical_Memo_17_workflowhooks

---

## Summary

Implemented Git Hooks Governance Layer for the AIOS Memo-Driven Workflow. Created 3 cross-platform Git hooks and 4 Python guard scripts at the project root level. All hooks are warn-only (v1) and use stdlib-only Python.

## Files Created

| File | Purpose |
|------|---------|
| `hooks/scripts/api_guard.py` | Detects unregistered APIs in staged files |
| `hooks/scripts/registry_guard.py` | Validates registry YAML syntax, duplicates, ownership |
| `hooks/scripts/memo_guard.py` | Checks commit messages for TM-XX reference |
| `hooks/scripts/pitfall_guard.py` | Reminds to document bug fixes |
| `hooks/pre-commit` | Runs all 4 guards before commit |
| `hooks/pre-push` | Runs api_guard + registry_guard before push |
| `hooks/post-merge` | Generates sync summary after merge |
| `hooks/install_hooks.py` | Cross-platform hook installer (Win+Mac) |

## Key Decisions

- **Cross-platform Python** hooks instead of bash scripts (Windows + Mac compat)
- **Project root** location for hooks (repo-level infrastructure)
- **Reuse existing scripts** — guard scripts reference `AIOS/scripts/` logic patterns
- **TM-XX-name format** for commit message memo references (e.g. `TM-17-workflowhook`)
- **Actual project directories** in memo_guard source path matching

## Issues Encountered

- Windows GBK console encoding error with Unicode symbols → fixed with ASCII alternatives
