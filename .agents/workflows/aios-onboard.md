---
description: First-time AIOS engineer onboarding
---

# AIOS Onboard — Engineer Registration

Register a new engineer in the multi-engineer AIOS workflow system.

## Steps

### 1. Check Registration
Check if `AIOS/engineers/<name>/profile.yaml` exists.
If registered, skip to Step 4 (orientation).

### 2. Register Engineer
Apply the `register-engineer` skill from `AIOS/workflow/skills/register-engineer.md`.
- Prompt for name, role, organization, responsibility
- Create `AIOS/engineers/<name>/profile.yaml`

### 3. Project Assignment
List existing projects from `AIOS/projects/`:
- If projects exist → ask engineer which to join
- If no projects exist → ask if they want to create one

**To create a new project:**
Apply the `register-project` skill from `AIOS/workflow/skills/register-project.md`.
- Prompt for project ID, display name, description, platform, build target
- Create `AIOS/projects/<project_id>/` directory structure
- Create the engineer's subdirectories within the project

**To join an existing project:**
- Add project to engineer's `profile.yaml` → `projects` list
- Create the engineer's subdirectories within the project

### 4. GitLab Setup
Check if the repository has git initialized: `git status`

**If this is a fresh setup (no repo cloned yet):**
Guide the engineer to clone from GitLab:
```bash
# SSH (推荐):
git clone git@192.168.0.92:feature-phone/fp-aios-kz.git

# 或 HTTP:
git clone http://192.168.0.92/feature-phone/fp-aios-kz.git
```

**SSH 未配置？** 详细步骤见 `AIOS/README_WORKFLOW.md` 的 GitLab 章节。

**创建工程师分支：**
```bash
git checkout -B eng/<name>/<project>
```

### 5. Orientation
Present the workflow overview:
- 📋 `AIOS/README_WORKFLOW.md` — Multi-engineer workflow guide
- 🏗️ `AIOS/AI_CONTEXT.md` — Project architecture and context
- 📝 `AIOS/workflow/templates/technical_memo_template.md` — How to write memos
- ⌨️ Slash commands: `/aios-login`, `/aios-workflow`, `/aios-intake`, `/aios-clarify`, `/aios-close`
- 🧠 `AIOS/MEMORY.md` — Project memory and known pitfalls
- 📦 `AIOS/workflow/manifest.yaml` — Component registry

### 6. Auto Login
After successful registration, automatically apply `session-login` skill from `AIOS/workflow/skills/session-login.md` to log the engineer into their selected project.

### 7. Confirmation
Show the registered profile.yaml entry and active session.
Guide the engineer to commit:
```
git add AIOS/engineers/<name>/ AIOS/projects/<project>/
git commit -m "[onboard] Register engineer: <name>, project: <project>"
```
