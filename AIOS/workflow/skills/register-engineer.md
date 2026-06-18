# Skill: Register Engineer

## Purpose
Register a new engineer in the multi-engineer AIOS workflow system.

## Input
None — triggered by `/aios-onboard` or when an unregistered engineer uses any `/aios-*` command.

## Procedure

1. **Check registration** — Look for `AIOS/engineers/<name>/profile.yaml`
   - If exists → skip registration, proceed to workflow

2. **Prompt for information:**
   - **Name** — Identifier (e.g., `KaiwenZheng`)
   - **Role** — Job title
   - **Organization** — Company/team
   - **Responsibility** — Primary area of work
   - **Projects** — Which project(s) to join (list from `AIOS/projects/`)
   - **Modules owned** — Which modules (optional, can be `[]`)

3. **Create engineer directory:**
   ```
   AIOS/engineers/<name>/profile.yaml
   ```

4. **Profile schema:**
   ```yaml
   name: <name>
   role: <role>
   organization: <org>
   responsibility: <area>
   registered_at: "<date>"
   projects:
     - project: <project_id>
       role: lead | contributor
       joined_at: "<date>"
   modules_owned: []
   contact:
     gitlab: "@<username>"
   preferences:
     language: zh-CN | en
     review_depth: brief | detailed
   ```

5. **Create project subdirectories** for each joined project:
   ```
   AIOS/projects/<project>/technical_memos/<name>/
   AIOS/projects/<project>/feedback/<name>/
   AIOS/projects/<project>/quality_reports/<name>/
   ```

6. **Welcome orientation** — Present the same orientation as `onboard-engineer.md`:
   - Point to `AIOS/README_WORKFLOW.md`
   - Point to `AIOS/AI_CONTEXT.md`
   - Explain slash commands

## Output
- Engineer directory and profile.yaml created
- Project subdirectories created for the engineer
- Welcome message with orientation
