# Skill: Session Login

## Purpose
Set the active engineer and project context for the current Antigravity session.
All subsequent workflow commands (`/aios-workflow`, `/aios-close`, etc.) use this context.

## When Required
**MANDATORY** — No code modification or workflow execution is permitted without an active login session.
Without login, the AI may only answer questions.

## Context Scope
- Login context is **session-only** — valid for the current Antigravity conversation
- When the conversation ends, the context is lost
- Next conversation requires a new `/aios-login`

## Procedure

1. **Scan engineers** — List all registered engineers from `AIOS/engineers/*/profile.yaml`

2. **Select engineer** — Present list, engineer confirms their identity
   - If only 1 engineer exists, still require confirmation (no auto-login)

3. **Scan projects** — Read selected engineer's `profile.yaml` → `projects` list
   - Also scan `AIOS/projects/` for available projects

4. **Select project** — Present list, engineer selects active project
   - If only 1 project exists, still require confirmation

5. **Verify directories** — Confirm the engineer has subdirectories in the selected project:
   ```
   AIOS/projects/<project>/technical_memos/<engineer>/
   AIOS/projects/<project>/feedback/<engineer>/
   AIOS/projects/<project>/quality_reports/<engineer>/
   ```
   If missing, create them (first-time login to this project).

6. **Set context** — The following values are now active for this session:
   ```
   ACTIVE_ENGINEER = <name>
   ACTIVE_PROJECT = <project_id>
   TM_PATH = AIOS/projects/<project>/technical_memos/<engineer>/
   FEEDBACK_PATH = AIOS/projects/<project>/feedback/<engineer>/
   QR_PATH = AIOS/projects/<project>/quality_reports/<engineer>/
   PITFALL_PATH = AIOS/projects/<project>/pitfalls/  (shared within project)
   GLOBAL_PITFALL_PATH = AIOS/docs/pitfalls/
   ```

7. **Confirm** — Display active session:
   ```
   ✅ Logged in as: KaiwenZheng
   📁 Active project: featurephone_secure
   📝 TM path: AIOS/projects/featurephone_secure/technical_memos/KaiwenZheng/
   ```

## Output
- Session context set (in-memory, not persisted to file)
- All subsequent `/aios-*` commands use this context automatically
