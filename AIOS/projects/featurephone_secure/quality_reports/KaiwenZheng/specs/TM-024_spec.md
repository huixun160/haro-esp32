# Frozen Specification — TM-24: Fix Antigravity AIOS Skill Command Integration

**Date:** 2026-03-12
**Approved by:** AIOS Founding Team

---

## MUST

- [x] Audit all `.agents/workflows/*.md` files — confirm YAML frontmatter and structure
- [ ] Verify all cross-references in workflow/skill/agent/rule files resolve to existing paths
- [ ] Create architecture doc: `AIOS/docs/architecture/antigravity_skill_architecture.md`
- [ ] Create command reference: `AIOS/docs/architecture/workflow_command_reference.md`
- [ ] Create path validation script: `AIOS/scripts/verify_workflow_paths.py`

## SHOULD

- [ ] Document known limitations of LLM-driven workflow execution
- [ ] Add troubleshooting section for common "command not working" scenarios

## MAY

- [ ] Add a `// turbo-all` annotation to frequently used workflows for faster execution

## OUT OF SCOPE

- Designing new workflow agents
- Modifying AIOS engineering policies
- Implementing new workflow features
- CI pipeline integration
- Autocomplete UI behavior (controlled by Antigravity IDE, not project config)
