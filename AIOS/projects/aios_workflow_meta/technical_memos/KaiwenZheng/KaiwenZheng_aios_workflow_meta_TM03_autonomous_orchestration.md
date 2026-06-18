# **Technical Memo 3 — Introduce Autonomous Orchestration Mode (**

# **/aios-auto**

# **)**





------



**Title:** Add State-Driven Autonomous Execution Mode for Parallel Development (/aios-auto)



**Project:** AIOS Workflow Infrastructure



**Subsystem:** Workflow / Orchestration / State Machine



**Author:** AIOS Architecture Team



**Priority:** CRITICAL



**Date:** 2026-03-25



------





## **Background**





Current AIOS system has two distinct execution models:





### **Model 1 — Manual Workflow (Existing)**



```
/aios-workflow → human-driven → sequential execution
```

Characteristics:



- Engineer defines task
- AI executes step-by-step
- Human controls direction





------





### **Model 2 — Target Autonomous System (New)**



```
state + module graph → planner → automatic task selection → execution
```

Characteristics:



- System determines next task
- Multiple modules can progress in parallel
- Human only intervenes at critical points





------



Problem:



> TM-02 introduced state + module graph, but there is no runtime system that uses them.



Additionally:



> /aios-workflow must remain stable for manual control and debugging.



------





## **Objective**





Introduce a new command:

```
/aios-auto
```

This command must:



1. Load project state (module_states.yaml)
2. Run planner
3. Identify actionable modules
4. Select one module for execution
5. Execute based on state
6. Propose and validate state transition
7. Persist results





------





## **Key Design Decision**







### **Separation of Modes**



| **Mode**   | **Command**    | **Purpose**                   |
| ---------- | -------------- | ----------------------------- |
| Manual     | /aios-workflow | Human-controlled execution    |
| Autonomous | /aios-auto     | State-driven system execution |



------





## **Current State**





Already available (from TM-02):



- module_graph.yaml
- module_states.yaml
- architecture_constitution.md
- service_contracts/
- acceptance_tests.yaml
- agent_permissions.yaml
- planner.md (read-only)





------





## **Scope**





This memo introduces:



1. New command /aios-auto
2. Planner integration
3. State-based execution routing
4. State transition validation
5. Hook-based enforcement
6. Minimal reviewer agents





------





## **Out of Scope**





- Human Gates (TM-04)
- Build/flash automation
- Integration pipeline
- Multi-agent debate expansion





------





## **Constraints**





1. Must work within markdown + AI execution system
2. Must not break /aios-workflow
3. Must rely on YAML for persistence
4. Must support multi-engineer parallel execution





------





## **Expected Deliverables**





------





### **1. New Command:** 

### **/aios-auto**





Create:

```
AIOS/commands/aios-auto.md
```



------





### **2. Execution Flow**



```
/aios-auto
    ↓
Load state + module graph
    ↓
Run planner
    ↓
Planner-reviewer validates result
    ↓
Select target module
    ↓
Execute task (research / implement / integrate-prep)
    ↓
Propose next state
    ↓
State-transition-reviewer validates
    ↓
Persist state
```



------





### **3. Module Selection Logic**





Priority:



1. SPEC_READY
2. RESEARCHING
3. READY_TO_IMPLEMENT





Limit:

```
one module per execution (v1)
```



------





### **4. Execution Routing**





------





#### **Case A — RESEARCHING**



Outputs:

```
modules/<module>/research_note.md
modules/<module>/api_mapping.md
modules/<module>/risk.md
```



------





#### **Case B — SPEC_READY / READY_TO_IMPLEMENT**



Outputs:

```
code changes
service_contract updates
registry updates
acceptance_tests updates
```



------





#### **Case C — READY_TO_INTEGRATE**



Outputs:

```
integration_precheck.md
```



------





### **5. State Transition**





Example:

```
dap_runtime:
  state: IMPLEMENTING → READY_TO_INTEGRATE
```



------





### **6. State Persistence**





Update:

```
AIOS/projects/<project>/state/module_states.yaml
```



------





### **7. New Agents**





------





#### **Agent:** 

#### **planner-reviewer**



Input:



- module_graph.yaml
- module_states.yaml
- planner output





Output:



- validated ready/block list





Purpose:



- prevent incorrect dependency resolution





------





#### **Agent:** 

#### **state-transition-reviewer**



Input:



- module state
- execution outputs
- proposed next state





Output:



- approve / reject transition





Purpose:



- enforce state machine correctness





------





### **8. New Hooks**





------





#### **Hook:** 

#### **state_guard.py**



Validate:



- YAML correctness
- module consistency
- state enum validity





------





#### **Hook:** 

#### **planner_sync_guard.py**



Ensure:



- planner output matches latest graph/state





------





#### **Hook:** 

#### **state_transition_guard.py**



Validate:



- legal state transitions only





------





### **Hook Location**



```
AIOShooks/scripts/
```



------





## **Verification Method**





------





### **Test 1 — Planner Correctness**





Input:

```
A: []
B: [A]
C: [A]
```

Expected:



- A ready
- B/C blocked





------





### **Test 2 — State Execution**





Initial:

```
ui_service: SPEC_READY
```

After /aios-auto:

```
ui_service: IMPLEMENTING
```



------





### **Test 3 — State Validation**





Invalid transition:

```
RESEARCHING → READY_TO_INTEGRATE
```

Expected:



- rejected by state-transition-reviewer





------





### **Test 4 — Multi-Engineer**





- Two engineers run /aios-auto
- Both read shared state
- No conflict or corruption





------





## **Potential Risks**





------





### **Risk 1 — State drift**





Mitigation:



- hooks enforce integrity





------





### **Risk 2 — Wrong module selection**





Mitigation:



- planner-reviewer agent





------





### **Risk 3 — Over-automation**





Mitigation:



- limit execution scope (1 module per run)





------





## **References**





- Technical Memo 2 — Workflow Parallelization
- module_graph.yaml
- module_states.yaml
- planner.md





------





# **Final Note**





This memo introduces a new capability:

```
system can decide what to do next
```

Before:

```
human decides everything
```

After:

```
system advances automatically until human is required
```

If implemented correctly:



- parallel development becomes real
- workflow becomes scalable
- architect exits execution bottleneck





If not:



- module graph becomes unused
- state system becomes decorative
- system regresses to manual orchestration





------

