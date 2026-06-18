# Skill: Freeze Spec

## Purpose
Generate a frozen specification from a clarified Technical Memo.

## Input
- Memo summary (from `intake-memo`)
- Clarification answers (from engineer)

## Procedure

1. Consolidate memo and answers into a unified requirements list
2. Classify each requirement:
   - **MUST** — Required for task completion. Blocker if not implemented.
   - **SHOULD** — Expected behavior. Should be implemented unless blocked.
   - **MAY** — Optional enhancement. Implement if time allows.
   - **OUT OF SCOPE** — Explicitly excluded from this task.
3. Present the frozen spec to the engineer for review
4. Engineer must approve before implementation begins
5. **Archive** — Save the approved spec to `AIOS/quality_reports/specs/TM-<number>_spec.md`

## Output Format

```markdown
# Frozen Specification — [Task Title]

## MUST
- [ ] Requirement 1
- [ ] Requirement 2

## SHOULD
- [ ] Requirement 3

## MAY
- [ ] Requirement 4

## OUT OF SCOPE
- Item A
- Item B

Approved by: [engineer name]
Date: [date]
```
