# Skill: Sync Shared Knowledge

## Purpose
Synchronize pitfall knowledge between project-level and global-level, and inject relevant context into the current workflow.

## When to Invoke
- During `pitfall-scan` (extended to cover project-level pitfalls)
- After `/aios-close` when new pitfalls are created
- Manually when an engineer suspects a cross-project issue

## Procedure

### Pull Phase (at workflow start)
1. Read global pitfalls from `AIOS/docs/pitfalls/`
2. Read project pitfalls from `AIOS/projects/<current_project>/pitfalls/`
3. Merge into a combined Pitfall Briefing for the current task

### Push Phase (at workflow close)
1. For each new pitfall created during the task:
   - Check `scope` field: `platform` or `project`
   - If `scope: project` → save to `AIOS/projects/<project>/pitfalls/`
   - If `scope: platform` → save to `AIOS/docs/pitfalls/`
2. If a project pitfall is later found in 2+ projects → recommend promotion to global

### Promotion Check
1. Scan all `AIOS/projects/*/pitfalls/` directories
2. For each pitfall, compare `affected_module` and `symptom` against other projects
3. If similar pitfall exists in another project → flag for `knowledge-curator` agent review

## Integration with pitfall-scan
The `pitfall-scan` skill should be updated to:
1. Scan `AIOS/docs/pitfalls/` (global) — existing behavior
2. **NEW:** Also scan `AIOS/projects/<current_project>/pitfalls/`
3. Merge results into a single Pitfall Briefing

## Output
- Combined pitfall knowledge available for current task
- New pitfalls routed to correct level (global vs project)
- Promotion candidates flagged
