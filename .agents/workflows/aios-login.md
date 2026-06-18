---
description: Login to AIOS — set active engineer and project for this session
---

# AIOS Login — Session Context

Set the active engineer and project for this working session.

> ⚠️ **Login is mandatory.** Without an active session, only questions may be answered — no code changes, no workflow execution.

## Steps

### 1. Login
Apply the `session-login` skill from `AIOS/workflow/skills/session-login.md`.
- List registered engineers from `AIOS/engineers/`
- Engineer confirms identity
- List available projects from engineer's `profile.yaml`
- Engineer selects project
- Set session context

### 2. Context Summary
Display:
```
✅ Logged in as: <engineer>
📁 Active project: <project>
📝 TM path: AIOS/projects/<project>/technical_memos/<engineer>/
🔢 Next TM number: TM-<XX> (from project.yaml tm_counter)
🌿 Branch: eng/<engineer>/<project>
🔗 Remote: git@192.168.0.92:feature-phone/fp-aios-kz.git
```

### 3. Ready
Session is active. Engineer may now use:
- `/aios-workflow` — Full development cycle
- `/aios-intake` — Parse a memo
- `/aios-clarify` — Clarify a memo
- `/aios-close` — Close a task
