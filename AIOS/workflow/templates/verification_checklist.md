# Verification Checklist Template

> Generate this checklist after implementation is complete.
> Save to: `AIOS/quality_reports/plans/verification_<memo_number>.md`

**Task:** [Task title from Technical Memo]
**Memo:** [Technical Memo reference]
**Date:** [YYYY-MM-DD]
**Engineer:** [Name]

---

## Build Steps

- [ ] Run: `[exact build command]`
- [ ] Expected exit code: `0`
- [ ] Expected output: [description]
- [ ] Known warnings to ignore: [list or "none"]

## Simulator Steps

- [ ] Launch simulator: `[command]`
- [ ] Navigate to: [menu path or action]
- [ ] Trigger: [action to test the feature]
- [ ] Expected UI behavior: [what should happen]
- [ ] Observe: [what to look for]

## Device Steps *(if applicable)*

- [ ] Flash device: `[flash command or tool]`
- [ ] Boot and navigate to: [path]
- [ ] Trigger: [action]
- [ ] Expected behavior: [what should happen on device]

## Expected Logs

| Log Pattern | Meaning | Tool |
|-------------|---------|------|
| `[pattern]` | [what it indicates] | [Logel / UART / etc.] |

## Success Criteria

- [ ] [Criterion 1 — specific and measurable]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Failure Indicators

| Indicator | Meaning | Action |
|-----------|---------|--------|
| [indicator] | [what went wrong] | [what to do] |

## Results

**Status:** [ ] PASS / [ ] FAIL
**Notes:** [Engineer fills in after verification]
**Date Verified:** [YYYY-MM-DD]
