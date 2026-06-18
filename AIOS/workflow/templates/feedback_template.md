# Feedback Artifact Template

Use this template to generate a structured feedback artifact at the end of every memo execution.

**File naming convention:** `AIOS/feedback/TM-XXX-feedback.md`

---

```markdown
# Feedback — TM-XXX: [Title]

**Date:** YYYY-MM-DD
**Memo:** Technical_Memo_XXX_[filename].md
**Outcome:** SUCCESS | PARTIAL | BLOCKED
**Author:** [Engineer Name]

---

## Execution Summary

<!-- 1-3 sentence summary of what this memo execution achieved -->

---

## Completed Work

<!-- Bulleted list of items successfully implemented and verified -->
- [ ] Item 1
- [ ] Item 2

---

## Incomplete Work

<!-- Items that were started but not finished -->
<!-- For each, explain how far it got and what remains -->
- [ ] Item — status, remaining work

---

## Blocking Issues

<!-- Issues that prevented completion -->
<!-- For each: symptom, root cause (if known), and suggested resolution -->
| Issue | Symptom | Root Cause | Suggested Resolution |
|---|---|---|---|
| Issue 1 | ... | ... | ... |

---

## Verification Status

<!-- Results from the verification checklist -->
| Test | Result | Notes |
|---|---|---|
| Test 1 | PASS / FAIL / SKIP | ... |

---

## Next Actions

<!-- Recommended actions for the next engineer or memo -->
<!-- Include: what to do first, dependencies, and any cautions -->
1. Action 1
2. Action 2

---

## Files Changed

| File | Action | Description |
|---|---|---|
| path/to/file | Created / Modified / Deleted | Brief description |

---

## References

- Related memos: TM-XX, TM-YY
- Related pitfalls: `AIOS/docs/pitfalls/xxx.md`
- Related decisions: ADR-XXX
```
