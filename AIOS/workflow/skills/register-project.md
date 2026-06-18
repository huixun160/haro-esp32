# Skill: Register Project

## Purpose
Register a new project in the multi-project AIOS workflow system.

## Input
Project name and metadata from the engineer.

## Procedure

1. **Check if project exists** — Look for `AIOS/projects/<project_id>/project.yaml`
   - If exists → report existing project, offer to join

2. **Prompt for information:**
   - **Project ID** — Short identifier (e.g., `featurephone_secure`, `voice_assistant`)
   - **Display name** — Human-readable name
   - **Description** — Brief project description
   - **Lead** — Engineer who leads the project
   - **Platform** — Target platform
   - **Build target** — Build command identifier (if applicable)

3. **Create project directory structure:**
   ```
   AIOS/projects/<project_id>/
   ├── project.yaml
   ├── technical_memos/
   ├── feedback/
   ├── quality_reports/
   ├── pitfalls/
   └── sync_summaries/
   ```

4. **Project schema:**
   ```yaml
   project: <project_id>
   display_name: "<name>"
   description: "<description>"
   created_at: "<date>"
   lead: <engineer_name>
   modules: []
   build_target: <target>
   platform: <platform>
   tm_counter: 0
   ```

5. **Create lead's subdirectories:**
   ```
   technical_memos/<lead>/
   feedback/<lead>/
   quality_reports/<lead>/session_logs/
   quality_reports/<lead>/specs/
   quality_reports/<lead>/plans/
   quality_reports/<lead>/sync_summaries/
   ```

6. **Update lead's profile** — Add project to `engineers/<lead>/profile.yaml` projects list

## Output
- Project directory structure created
- Lead's subdirectories created
- Lead's profile updated
