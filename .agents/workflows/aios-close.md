---
description: Close an AIOS task with documentation and git guidance
---

# AIOS Close — Task Closeout

Finalize a completed task with all required documentation and registry updates.

## Prerequisites
- **Must have an active login session** (run `/aios-login` first)

> ⚠️ **If no login session is active, STOP and redirect to `/aios-login`.**

## Steps

### 0. Login Gate
Verify active session context exists (ACTIVE_ENGINEER and ACTIVE_PROJECT are set).
If not set → **STOP**, instruct engineer to run `/aios-login` first.

### 1. Closeout Review
Apply the `closeout-reviewer` agent from `AIOS/workflow/agents/closeout-reviewer.md`.

### 2. Session Log
Apply the `close-task` skill from `AIOS/workflow/skills/close-task.md`.
Generate session log in `AIOS/projects/<ACTIVE_PROJECT>/quality_reports/<ACTIVE_ENGINEER>/session_logs/`.

### 3. Pitfall Records
Create pitfall entries with **Author** and **Project** fields:
- `AIOS/projects/<ACTIVE_PROJECT>/pitfalls/` for project-level pitfalls
- `AIOS/docs/pitfalls/` for global/platform pitfalls

### 3.5. Knowledge Curation
Apply the `knowledge-curator` agent from `AIOS/workflow/agents/knowledge-curator.md`.

### 4. Feedback Artifact
Apply the `close-feedback` skill from `AIOS/workflow/skills/close-feedback.md`.
Save to `AIOS/projects/<ACTIVE_PROJECT>/feedback/<ACTIVE_ENGINEER>/TM-XXX-feedback.md`.

### 5. Memory Update
Update `AIOS/MEMORY.md` with **Author** and **Project** fields on each new entry.

### 6. Sync Summary
Run `python AIOS/scripts/generate_sync_summary.py --registry AIOS/registry/`.
Save to `AIOS/projects/<ACTIVE_PROJECT>/quality_reports/<ACTIVE_ENGINEER>/sync_summaries/`.

### 7. Git Commit + Push
Apply the `package-commit` skill from `AIOS/workflow/skills/package-commit.md`.
```
git add -A
git commit -m "[task] <description>

Memo: TM-<number>
Author: <ACTIVE_ENGINEER>
Project: <ACTIVE_PROJECT>"
```

Then push to GitLab:
```
git push -u origin eng/<ACTIVE_ENGINEER>/<ACTIVE_PROJECT>
```

> 如果 GitLab 不可用，可以先跳过 push，恢复后再推送。

### 8. Complete
Task is closed.
