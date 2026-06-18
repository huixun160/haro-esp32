# Rule: Pitfall Review Required

Before implementation begins, the AI **must** review accumulated project pitfalls to avoid repeating past mistakes.

## Requirements

1. **Planning phase:** The `pitfall-scan` skill must be applied during Task Planning. Its output (Pitfall Briefing) must be included in the Implementation Plan.
2. **Implementation phase:** Before modifying any file, check the Pitfall Briefing for relevant warnings.
3. **Build system changes:** If the task modifies `make/dap/dap.mk` or any `.mk` file, the full `dap_mk_checklist.md` runbook must be executed as the final step before compilation.
4. **Recurring pitfalls:** Any pitfall marked with ⚠️ (recurring) in `MEMORY.md` must be explicitly addressed in the implementation plan — either confirming it does not apply, or describing the mitigation.

## Rationale

The `dap.mk` flags-missing pitfall was hit 3 times across TM-15, TM-19, and TM-20 because accumulated knowledge was not consulted during planning. This rule closes the feedback loop.
