# Skill: Onboard Engineer

## Purpose
Register a new engineer in the AIOS workflow system on first deployment.

## Input
None — this skill is triggered automatically when an unregistered engineer uses the workflow.

## Procedure

1. **Check registration** — Read `AIOS/registry/ownership.yaml` to see if the engineer is already registered.

2. **If not registered**, prompt the engineer for:
   - **Name** — Full name or identifier (e.g. `zhukangwei`)
   - **Role** — Job title (e.g. `Platform Infrastructure Engineer`)
   - **Responsibility** — Primary area of work:
     - DAP runtime
     - APP layer development
     - Security
     - Build system / toolchain
     - Testing / QA
     - Other (specify)

3. **Register** — Add entry to `AIOS/registry/ownership.yaml`:
   ```yaml
   - name: zhukangwei
     role: Platform Infrastructure Engineer
     responsibility: DAP runtime
     modules: []
     registered_at: 2026-03-09
   ```

4. **Welcome orientation** — Present:
   - 📋 `AIOS/AIOS_WORKFLOW.md` — Workflow overview and rules
   - 🏗️ `AIOS/AI_CONTEXT.md` — Project architecture and context
   - 📝 `AIOS/workflow/templates/technical_memo_template.md` — How to write memos
   - ⌨️ Available slash commands: `/aios-workflow`, `/aios-intake`, `/aios-clarify`, `/aios-close`
   - 🧠 `AIOS/MEMORY.md` — Project memory and known pitfalls

5. **Assign initial modules** (optional) — If the engineer knows which modules they will own, register them.

## Output
- Updated `AIOS/registry/ownership.yaml`
- Welcome message with orientation links
