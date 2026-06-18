# Frozen Specification — TM-02 Parallelization & State-Driven Execution (Milestone 1)

> Scoped to **Milestone 1 only**: module_graph + module_states + planner (read-only)

## MUST

- [ ] Create `AIOS/projects/<project>/state/` directory structure
- [ ] Create `module_graph.yaml` — machine-readable module dependency graph
- [ ] Create `module_states.yaml` — persistent per-module state tracking (state + owner fields)
- [ ] Define valid state enum in `manifest.yaml` (`states:` section): INTAKE, RESEARCHING, SPEC_READY, READY_TO_IMPLEMENT, IMPLEMENTING, READY_FOR_MANUAL_BUILD, READY_FOR_MANUAL_FLASH, READY_FOR_MANUAL_LOG_CAPTURE, READY_TO_INTEGRATE, BLOCKED, CLOSED
- [ ] Implement planner logic as a new skill (`planner.md`) that reads `module_graph.yaml` + `module_states.yaml` and outputs `ready_modules.md` + `blocked_modules.md`
- [ ] Planner V1 is **read-only** — does not modify state files
- [ ] Create `architecture_constitution.md` with 5 core rules (APP→DAP boundary, DAP no business logic, Service Layer ownership, Adapter = only Mocor touch, ABI = only APP interface)

## SHOULD

- [ ] Create initial `service_contracts/` directory with at least one example contract YAML
- [ ] Create `acceptance_tests.yaml` with per-module test definitions
- [ ] Create `agent_permissions.yaml` restricting agent modification paths
- [ ] Populate `module_graph.yaml` with actual AIOS module dependencies (abi_v1, dap_runtime, ui_service, ui_adapter, app_runtime)
- [ ] Create test mini-graph for planner verification

## MAY

- [ ] Create `abi_v1.h` stub (placeholder C header for DAP→APP interface)
- [ ] Add `architecture-reviewer` agent definition
- [ ] Add `integration-critic` agent definition

## OUT OF SCOPE

- Workflow state machine integration (Week 2)
- Human Gate implementation (Week 2)
- Integration Layer artifacts (Week 3)
- Agent self-review / self-debate mode (Week 3)
- Any code changes to DAP runtime or C source files
- CI/CD pipeline or build automation

Approved by: KaiwenZheng
Date: 2026-03-25
