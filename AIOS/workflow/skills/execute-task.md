# Skill: Execute Task

## Purpose
Implement code changes, documentation updates, and registry entries according to the implementation plan.

## Input
Implementation plan (from `plan-task`).

## Procedure

0. **Pitfall Pre-Flight Check** (before any code changes):
   - Read the **⚠️ Pitfall Briefing** section from the implementation plan
   - For each matched pitfall, confirm the prevention action is understood
   - If the plan involves `make/dap/dap.mk`, load `AIOS/docs/runbooks/dap_mk_checklist.md` and keep it active throughout implementation
   - If any recurring pitfall (⚠️) applies, flag it explicitly before proceeding

1. Follow the execution order from the implementation plan
2. For each file change:
   - Make the code modification
   - Ensure code follows existing project conventions
   - Add inline comments for non-obvious logic
3. Update documentation:
   - Create/update architecture docs in `AIOS/docs/architecture/`
   - Create/update API docs in `AIOS/docs/api/`
   - Record any runbook steps in `AIOS/docs/runbooks/`
4. Update registries:
   - Register new APIs in `AIOS/registry/apis.yaml` (per `api-registration-required` rule)
   - Update module registry if new modules are created
   - Update migration status if legacy APIs are wrapped
5. After each logical change, verify:
   - Code compiles (if applicable in current environment)
   - No unintended side effects in dependent modules
6. **Post-implementation pitfall check:**
   - Re-check applicable runbook checklists (e.g., `dap_mk_checklist.md`)
   - Confirm no matched pitfall was triggered

## Rules
- Follow all workflow rules in `AIOS/workflow/rules/`
- Do not skip API registration
- Record any discovered pitfalls immediately
- **Do not skip pitfall pre-flight check** (per `pitfall-review-required` rule)

