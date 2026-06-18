# Skill: Close Task

## Purpose
Finalize a completed task by producing session documentation, pitfall records, and registry updates.

## Input
- Completed implementation
- Verification results from engineer

## Procedure

1. **Session Log** — Write a session log to `AIOS/quality_reports/session_logs/`:
   - Date and task title
   - Summary of what was done
   - Files created/modified/deleted
   - Key decisions made during implementation
   - Any deviations from the original spec

2. **Pitfall Records** — For any bugs, gotchas, or non-obvious behaviors encountered:
   - Create entries in `AIOS/docs/pitfalls/`
   - Follow the format in `pitfall-log-required` rule

3. **Registry Updates** — Verify all registries are up to date:
   - `registry/apis.yaml` — all new/modified APIs registered
   - `registry/modules.yaml` — any new modules registered
   - `registry/migration-status.yaml` — migration progress updated
   - `registry/decisions.yaml` — any architectural decisions recorded

4. **MEMORY.md** — Update project memory with:
   - New pitfalls
   - Key decisions
   - Working configuration changes

## Output
- Session log file
- Pitfall records (if any)
- Updated registry files
- Updated MEMORY.md
