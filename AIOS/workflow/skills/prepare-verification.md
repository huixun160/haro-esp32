# Skill: Prepare Verification

## Purpose
Generate a verification checklist for the engineer to validate the implementation.

## Input
Completed implementation and frozen spec.

## Procedure

1. From the frozen spec, derive testable success criteria
2. Generate verification steps for each platform:

### Build Verification
- Exact build command to run
- Expected output / exit code
- Known build warnings to ignore

### Simulator Verification
- Steps to launch simulator
- Steps to trigger the implemented feature
- Expected UI behavior or log output

### Device Verification (if applicable)
- Flashing procedure
- Steps to test on hardware
- Expected device behavior

### Log Verification
- Expected log entries (with patterns)
- Log tool to use (e.g. Logel)
- How to filter relevant logs

## Output Format

```markdown
# Verification Checklist — [Task Title]

## Build Steps
- [ ] Run: `[build command]`
- [ ] Expected: [exit code / output]

## Simulator Steps
- [ ] Step 1: ...
- [ ] Step 2: ...
- [ ] Expected: ...

## Device Steps
- [ ] Step 1: ...
- [ ] Expected: ...

## Expected Logs
- `[log pattern 1]` — indicates [meaning]
- `[log pattern 2]` — indicates [meaning]

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Failure Indicators
- [indicator 1] — means [problem]
- [indicator 2] — means [problem]
```
