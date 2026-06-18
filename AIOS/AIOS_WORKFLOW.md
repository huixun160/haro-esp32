# AIOS Memo-Driven Development Workflow

All engineering tasks on the AIOS Feature Phone Platform must follow this Technical Memo workflow.

> **For new engineers:** See `AIOS/README_WORKFLOW.md` for the full multi-engineer guide.

---

## Execution Sequence

```
1  Technical memo intake
2  Ambiguity clarification
3  Spec freeze
4  Implementation
5  Engineer verification
6  Knowledge consolidation
7  Git commit (manual by engineer)
```

---

## Rules

1. **No memo, no implementation.** AI must not implement tasks without a technical memo as input.
2. **Clarification first.** If a memo contains ambiguities, AI must ask clarification questions before modifying any code.
3. **Spec freeze before code.** After clarification, AI must generate a frozen specification before implementation begins.
4. **API registration required.** All new or modified public APIs must be registered in `registry/apis.yaml` before or during implementation.
5. **Pitfall logging required.** All resolved platform bugs and debugging insights must be recorded in `docs/pitfalls/`.
6. **Git is manual.** AI guides the engineer to run `git add`, `git commit`, and `git push` manually in the terminal. AI checks if `git init` is needed. Engineer confirms completion before proceeding to the next workflow cycle.

---

## Workflow Entry Points

| Slash Command | Purpose |
|---------------|---------|
| `/aios-workflow` | Full memo-driven workflow cycle |
| `/aios-onboard` | First-time engineer onboarding |
| `/aios-intake` | Parse and intake a technical memo |
| `/aios-clarify` | Generate clarification questions |
| `/aios-close` | Close task: docs, registry, git guidance |

---

## Related Files

- `README_WORKFLOW.md` — Multi-engineer workflow guide
- `AI_CONTEXT.md` — Persistent project context for AI
- `MEMORY.md` — Living project memory
- `engineers/` — Engineer profiles (per-engineer `profile.yaml`)
- `projects/` — Project directories (memos, feedback, pitfalls per project)
- `registry/` — Machine-readable project state
- `workflow/` — Rules, skills, agents, templates
- `workflow/manifest.yaml` — Complete component registry
- `scripts/` — Automation utilities
