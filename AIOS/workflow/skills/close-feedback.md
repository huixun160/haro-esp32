# Skill: Close Feedback

## Purpose
Generate a structured feedback artifact at the end of every memo execution, regardless of outcome (SUCCESS, PARTIAL, or BLOCKED).

## Input
- Completed implementation state
- Verification results (if any)
- Session log (from `close-task` skill)
- Pitfall records (if any)
- Engineer's assessment of outcome

## Procedure

1. **Determine Outcome** — Ask the engineer (or infer from verification results):
   - **SUCCESS** — All MUST requirements are met, verification passes
   - **PARTIAL** — Some work is completed, but not all MUST items are done
   - **BLOCKED** — Cannot proceed due to an unresolved dependency or issue

2. **Populate Template** — Use `workflow/templates/feedback_template.md`:
   - Fill in metadata (date, memo ref, outcome, author)
   - List completed work items
   - List incomplete work items with status and remaining effort
   - Document blocking issues with symptoms, root causes, and suggested resolutions
   - Record verification results
   - Provide actionable next steps

3. **Generate Feedback File** — Save to:
   ```
   AIOS/feedback/TM-XXX-feedback.md
   ```
   Where `XXX` is the zero-padded memo number.

4. **Cross-Reference** — Ensure feedback references:
   - Related pitfall entries (if any were created)
   - Related ADR entries (if any decisions were made)
   - Session log entry

5. **Present to Engineer** — Show the feedback artifact for review before committing.

## Output
- Feedback artifact file in `AIOS/feedback/`
- Cross-referenced with session log and pitfall records

## Outcome Definitions

| Outcome | Criteria |
|---|---|
| **SUCCESS** | All MUST requirements met, verification passes |
| **PARTIAL** | Some MUST items done, others remain; or verification incomplete |
| **BLOCKED** | Cannot proceed; dependency/issue prevents further work |

## Integration with aios-close

This skill is called **automatically** by the `/aios-close` workflow, between the session log step and the git commit step. The engineer may also invoke it manually if they need to record a BLOCKED outcome before completing any implementation.
