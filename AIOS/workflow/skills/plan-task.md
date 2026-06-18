# Skill: Plan Task

## Purpose
Produce a detailed implementation plan from a frozen specification.

## Input
Frozen specification (from `freeze-spec`).

## Procedure

1. **Pitfall Scan** — Apply `pitfall-scan` skill first (if not already done by the workflow orchestrator). Obtain the Pitfall Briefing.
2. Identify all files that need to be created, modified, or deleted
3. List affected modules and their dependencies
4. Identify risk areas:
   - Modules with complex dependencies
   - Code paths that touch hardware abstraction
   - **Matched pitfalls from the Pitfall Briefing** (mandatory — do not skip)
   - APIs that need registration (check `AIOS/registry/apis.yaml`)
5. Determine execution order based on dependencies
6. Estimate complexity for each change
7. **Embed Pitfall Briefing** — Copy the Pitfall Briefing into the plan (see Output Format below)
8. **Archive** — Save the plan to `AIOS/quality_reports/plans/TM-<number>_plan.md`

## Output Format

```markdown
# Implementation Plan — [Task Title]

## File Changes
| Action | File | Module | Description |
|--------|------|--------|-------------|
| CREATE | path | module | ... |
| MODIFY | path | module | ... |
| DELETE | path | module | ... |

## Module Impact
- module_a → [description of impact]
- module_b → [description of impact]

## Risk Areas
- [risk description and mitigation]

## ⚠️ Pitfall Briefing

### Matched Pitfalls (N items)
| # | Pitfall | Relevance | Prevention |
|---|---------|-----------|------------|
| 1 | [title] | [why it matches] | [prevention action] |

### Applicable Runbooks
- [ ] [runbook name] — [when to execute]

### Key Decisions to Respect
- [decision] — [consequence]

## Execution Order
1. [first change]
2. [second change]
...
```
