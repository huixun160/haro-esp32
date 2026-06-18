# Skill: Package Commit

## Purpose
Guide the engineer through git commit and generate supporting documentation.

## Input
- Completed task with session log
- List of files created/modified/deleted

## Procedure

1. **Generate commit message** — Based on the task:
   ```
   [module] Brief description of change
   
   - Detail 1
   - Detail 2
   
   Memo: Technical_Memo_XX
   ```

2. **Generate PR summary** (for future GitHub workflow):
   ```markdown
   ## Summary
   [What this PR does]
   
   ## Changes
   - [File changes list]
   
   ## Testing
   - [Verification results]
   
   ## Related
   - Memo: [reference]
   ```

3. **Generate sync summary** — Feed into `scripts/generate_sync_summary.py`:
   - New APIs added
   - Modified APIs
   - New modules
   - Migration updates
   - New pitfalls

4. **Guide git operations** — Per `git-manual-commit` rule:
   - Show `git status` output
   - Provide exact `git add` and `git commit` commands
   - Wait for engineer confirmation
   - Do NOT execute git commands directly

5. **Guide push** — After commit, provide push instructions:
   - Show current branch: `eng/<ACTIVE_ENGINEER>/<ACTIVE_PROJECT>`
   - Provide `git push -u origin eng/<ACTIVE_ENGINEER>/<ACTIVE_PROJECT>`
   - If first time: suggest `git checkout -B eng/<ACTIVE_ENGINEER>/<ACTIVE_PROJECT>` first
   - Wait for push confirmation
   - If GitLab unavailable: note that push can be done later

## Output
- Commit message text
- PR summary (saved to project quality_reports)
- Git commit + push guidance for engineer
