# Rule: First-Deploy Onboarding

When an engineer uses the AIOS workflow for the first time (no entry in `AIOS/registry/ownership.yaml`), the system must:

1. **Detect first-time use** — Check if the current engineer has an entry in `ownership.yaml`
2. **Prompt for registration** — Ask the engineer:
   - Full name (e.g. `zhukangwei`)
   - Job title / role (e.g. `Platform Infrastructure Engineer`)
   - Primary responsibility area (e.g. `DAP runtime`, `APP layer`, `Security`)
3. **Register in ownership.yaml** — Add the engineer's information with the current date
4. **Welcome message** — Provide a brief orientation:
   - Point to `AIOS_WORKFLOW.md` for workflow overview
   - Point to `AI_CONTEXT.md` for project context
   - Point to `workflow/templates/` for memo template
   - Explain the `/aios-*` slash commands

This ensures every engineer is tracked and oriented before contributing.
