# Frozen Specification — TM-40: Multi-Engineer Multi-Project Workflow Upgrade

## MUST
- [ ] Create `AIOS/engineers/KaiwenZheng/profile.yaml` with expanded schema (projects, modules_owned, contact, preferences)
- [ ] Create `AIOS/projects/featurephone_secure/project.yaml` with project metadata
- [ ] Create project subdirectories: `technical_memos/`, `feedback/`, `quality_reports/`, `pitfalls/`, `sync_summaries/`
- [ ] Migrate all 45 TMs to `projects/featurephone_secure/technical_memos/KaiwenZheng/`
- [ ] Migrate all 38 feedback files to `projects/featurephone_secure/feedback/KaiwenZheng/`
- [ ] Migrate all session logs, specs, plans to `projects/featurephone_secure/quality_reports/KaiwenZheng/`
- [ ] Classify and migrate 24 pitfalls: global (docs/pitfalls/) vs project-level
- [ ] Create `workflow/manifest.yaml` listing all agents, skills, rules, dependencies
- [ ] Create 4 new skills: register-engineer, register-project, sync-shared-knowledge, log-execution
- [ ] Create 2 new agents: assignment-reviewer, knowledge-curator
- [ ] Upgrade `hooks/scripts/memo_guard.py` for naming convention validation
- [ ] Create `AIOS/README_WORKFLOW.md` with Quick Start, naming rules, project structure, workflow steps, feedback, pitfall sharing, git workflow
- [ ] Update `AIOS_WORKFLOW.md`, `AI_CONTEXT.md`, and `.agents/workflows/*.md` for new paths
- [ ] Engineer stamp: MEMORY.md entries and pitfall files include `Author` and `Project` fields
- [ ] Memo naming: `<ENGINEER>_<PROJECT>_TM<XX>_<name>.md` (engineer-first)
- [ ] TM numbering: per-project incremental
- [ ] 3-layer pitfall system: global (docs/pitfalls/) → project (projects/*/pitfalls/) with promotion via knowledge-curator

## SHOULD
- [ ] Deprecate `registry/ownership.yaml` with notice pointing to `engineers/*/profile.yaml`
- [ ] Place .gitkeep in emptied legacy directories (technical_memos/, feedback/, quality_reports/)
- [ ] Keep existing pitfalls that are global as-is in `docs/pitfalls/`

## MAY
- [ ] Add `preferences` field to `profile.yaml` (language, review_depth)
- [ ] Add pitfall `scope: platform | project` field to pitfall template

## OUT OF SCOPE
- CI/CD integration
- Advanced permission systems
- Multi-repo architecture
- Automated task assignment
- GitLab multi-branch (deferred to next TM)

Approved by: KaiwenZheng
Date: 2026-03-24
