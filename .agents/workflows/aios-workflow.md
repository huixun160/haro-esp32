---
description: Full AIOS Memo-Driven Development Workflow cycle
---

# AIOS Workflow — Full Cycle

Execute the complete memo-driven development cycle for a Technical Memo.

## Prerequisites
- Engineer must be registered in `AIOS/engineers/<name>/profile.yaml` (run `/aios-onboard` first if not)
- **Must have an active login session** (run `/aios-login` first)
- A Technical Memo must be provided as input

> ⚠️ **If no login session is active, STOP and redirect to `/aios-login`.** Without login, only questions may be answered — no code changes permitted.

## Steps

### 0. Login Gate
Verify active session context exists (ACTIVE_ENGINEER and ACTIVE_PROJECT are set).
If not set → **STOP**, instruct engineer to run `/aios-login` first.
All paths below use the active session context.

### 1. Memo Intake
Read and apply the `intake-memo` skill from `AIOS/workflow/skills/intake-memo.md`.
Parse the provided Technical Memo and extract structured information.

### 2. Memo Critique
Apply the `memo-critic` agent from `AIOS/workflow/agents/memo-critic.md`.
Check for missing requirements, ambiguous goals, and missing verification criteria.

### 3. Ambiguity Clarification
If the memo-critic identified issues, apply the `clarify-memo` skill from `AIOS/workflow/skills/clarify-memo.md`.
Present clarification questions to the engineer and wait for answers.

### 4. Spec Freeze
Apply the `freeze-spec` skill from `AIOS/workflow/skills/freeze-spec.md`.
Generate MUST/SHOULD/MAY/OUT-OF-SCOPE specification and get engineer approval.
Archive approved spec to `AIOS/projects/<ACTIVE_PROJECT>/quality_reports/<ACTIVE_ENGINEER>/specs/TM-<number>_spec.md`.

### 5. Pitfall Scan & Task Planning
**First**, apply the `pitfall-scan` skill from `AIOS/workflow/skills/pitfall-scan.md`.
Scan `AIOS/MEMORY.md`, `AIOS/docs/pitfalls/` (global), and `AIOS/projects/<ACTIVE_PROJECT>/pitfalls/` (project-level).
Use `sync-shared-knowledge` skill from `AIOS/workflow/skills/sync-shared-knowledge.md`.
**Then**, apply the `plan-task` skill from `AIOS/workflow/skills/plan-task.md`.
Archive plan to `AIOS/projects/<ACTIVE_PROJECT>/quality_reports/<ACTIVE_ENGINEER>/plans/TM-<number>_plan.md`.

### 5.5. Assignment Review
Apply the `assignment-reviewer` agent from `AIOS/workflow/agents/assignment-reviewer.md`.

### 6. Implementation
Apply the `execute-task` skill from `AIOS/workflow/skills/execute-task.md`.
Apply the `log-execution` skill from `AIOS/workflow/skills/log-execution.md`.
Follow ALL rules in `AIOS/workflow/rules/`.

### 7. Verification Preparation
Apply the `prepare-verification` skill from `AIOS/workflow/skills/prepare-verification.md`.

### 8. Engineer Verification
**STOP** — Engineer performs verification manually.

### 9. Task Closeout
Apply the `closeout-reviewer` agent from `AIOS/workflow/agents/closeout-reviewer.md`.
Apply the `knowledge-curator` agent from `AIOS/workflow/agents/knowledge-curator.md`.
Apply the `close-task` skill from `AIOS/workflow/skills/close-task.md`.
Session logs go to `AIOS/projects/<ACTIVE_PROJECT>/quality_reports/<ACTIVE_ENGINEER>/session_logs/`.

### 10. Git Commit
Apply the `package-commit` skill from `AIOS/workflow/skills/package-commit.md`.
Follow `git-manual-commit` rule.

### 11. Complete
Workflow cycle is complete.
