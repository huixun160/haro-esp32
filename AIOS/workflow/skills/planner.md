# Skill: Planner

## Purpose
Analyze module dependencies and current states to identify which modules are ready to advance and which are blocked. This is the "brain" of the parallel execution system.

## Version
**V1 — Read-Only.** The planner does NOT modify any state files. It only reads and produces analysis output.

## When to Invoke
- **Automatically** at the start of every `/aios-workflow` execution (before task planning)
- May also be invoked manually for status overview

## Input
- `AIOS/projects/<project>/state/module_graph.yaml` — module dependency graph
- `AIOS/projects/<project>/state/module_states.yaml` — current module states

## Procedure

1. **Load module graph**
   - Parse `module_graph.yaml`
   - Build dependency tree: module → list of dependencies

2. **Load module states**
   - Parse `module_states.yaml`
   - Map each module to its current state and owner

3. **Classify modules by readiness**
   For each module, evaluate:

   | Condition | Classification |
   |---|---|
   | All deps are `CLOSED` AND module is `INTAKE` | **READY** — can begin work |
   | All deps are `CLOSED` AND module is `RESEARCHING`/`SPEC_READY` | **IN_PROGRESS** — already advancing |
   | All deps are `CLOSED` AND module is in any `READY_FOR_*` state | **WAITING_HUMAN** — needs human gate |
   | Module has no deps AND module is `INTAKE` | **READY** — no blockers |
   | Any dep is NOT `CLOSED` | **BLOCKED** — waiting on dependencies |
   | Module is `CLOSED` | **DONE** |

4. **Detect parallelism opportunities**
   - Find all modules classified as `READY` simultaneously
   - These can be assigned to different engineers/conversations

5. **Detect bottlenecks**
   - Find modules that block the most downstream modules
   - Flag as **CRITICAL PATH** items

6. **Generate output**
   Present two structured reports:

### ready_modules.md
```markdown
# Ready Modules — [project] — [date]

| Module | Current State | Deps Satisfied | Suggested Next State |
|--------|--------------|----------------|---------------------|
| abi_v1 | INTAKE | (no deps) | RESEARCHING |
| ui_service | INTAKE | abi_v1=CLOSED | RESEARCHING |

## Parallelism
- N modules can be worked on simultaneously
- Suggested assignments: [based on engineer profiles]
```

### blocked_modules.md
```markdown
# Blocked Modules — [project] — [date]

| Module | Current State | Blocking Deps | Blocked By |
|--------|--------------|---------------|------------|
| app_runtime | INTAKE | dap_runtime(INTAKE), ui_service(INTAKE) | 3 deps unmet |

## Critical Path
- [module] blocks N downstream modules — prioritize this
```

## Output
Two markdown reports (ready + blocked). Does NOT modify any files.

## Constraints
- **Read-only** — never writes to `module_states.yaml` or `module_graph.yaml`
- Must handle missing modules gracefully (warn, don't crash)
- Must handle circular dependencies (detect and flag as ERROR)
