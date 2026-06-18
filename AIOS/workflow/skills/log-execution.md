# Skill: Log Execution

## Purpose
Record which workflow components (agents, skills, rules) were invoked during a task execution, providing an audit trail for traceability.

## When to Invoke
- Automatically during workflow execution (called by `execute-task` and `close-task`)
- Creates structured markers in the session log

## Procedure

1. **Track invocations** — During workflow execution, record each component invocation:
   - Agent name and timestamp
   - Skill name and timestamp
   - Rule checked and result (pass/fail/skipped)

2. **Generate execution log section** for the session log:
   ```markdown
   ## Execution Trace

   | # | Component | Type | Timestamp | Result |
   |---|-----------|------|-----------|--------|
   | 1 | memo-critic | agent | 14:05 | invoked |
   | 2 | intake-memo | skill | 14:05 | completed |
   | 3 | api-governor | agent | 14:20 | invoked |
   | 4 | boundary-reviewer | agent | 14:20 | invoked |
   | 5 | api-registration-required | rule | 14:25 | passed |
   ```

3. **Engineer stamp** — Every entry includes:
   - `Author: <engineer_name>`
   - `Project: <project_id>`

4. **Save** — Append to session log at:
   ```
   AIOS/projects/<project>/quality_reports/<engineer>/session_logs/TM-XX_session_log.md
   ```

## Output
- Execution trace section in session log
- Audit trail of which components ran
