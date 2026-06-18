---
description: Generate clarification questions for a Technical Memo
---

# AIOS Clarify — Memo Clarification

Generate targeted questions for ambiguous or incomplete Technical Memos.

## Prerequisites
- **Must have an active login session** (run `/aios-login` first)

> ⚠️ **If no login session is active, STOP and redirect to `/aios-login`.**

## Steps

### 0. Login Gate
Verify active session context exists (ACTIVE_ENGINEER and ACTIVE_PROJECT are set).
If not set → **STOP**, instruct engineer to run `/aios-login` first.

### 1. Context
Read the Technical Memo (provided by engineer or from `/aios-intake` output).

### 2. Generate Questions
Apply the `clarify-memo` skill from `AIOS/workflow/skills/clarify-memo.md`.
Generate specific, prioritized clarification questions.

### 3. Present
Present numbered questions to the engineer.
Wait for answers.

### 4. Next Step
Once all questions are answered, suggest:
- Running `/aios-workflow` to continue with spec freeze and implementation
- Or reviewing the updated memo for completeness
