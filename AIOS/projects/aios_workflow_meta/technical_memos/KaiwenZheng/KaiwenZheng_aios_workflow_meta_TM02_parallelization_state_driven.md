

# **Technical Memo 2 — AIOS Workflow Parallelization & State-Driven Execution Upgrade**





------



**Title:** Upgrade AIOS Workflow to State-Driven Parallel Execution System with Human Gates



**Project:** AIOS Feature Phone Platform



**Subsystem:** System Integration / Workflow Infrastructure



**Author:** AIOS Architecture Team



**Priority:** HIGH



**Date:** 2026-03-25



------





## **Background**





Current AIOS development relies on:

```
human-driven task decomposition → agent execution → manual build/flash/debug → human decision
```

This creates a fundamental bottleneck:



- All task decomposition exists only in the architect’s mind
- Workflow executes tasks sequentially
- No explicit dependency graph
- No structured state transitions
- No formal handling of mandatory manual steps (build / flash / log)





Additionally:



- Mocor platform is complex and poorly documented
- Many APIs are unreliable or undocumented
- Build–flash–verify cycle is slow (~20–40 minutes per iteration)





As a result:



> The system is not self-propagating — it depends on continuous human orchestration.



------





## **Objective**





Upgrade AIOS workflow from:

```
memo-driven sequential executor
```

to:

```
state-driven parallel execution system with explicit human gates
```

Specifically:



1. Enable **parallel development across multiple modules**

2. Externalize architecture into **machine-readable structures**

3. Introduce **state machine–driven execution**

4. Separate:

   

   - research
   - implementation
   - integration

   

5. Explicitly model **manual operations as Human Gates**

6. Allow workflow to:

   

   - auto-advance when possible
   - pause and request human input when necessary

   





------





## **Current State**







### **Workflow**





- Technical Memo–driven execution
- No dependency graph between modules
- No parallel scheduling
- No explicit lifecycle states







### **Execution Model**





- Human defines next task
- Agents execute in isolation
- No integration-level awareness







### **Critical Gaps**





1. No **module-level decomposition**
2. No **dependency graph**
3. No **execution state tracking**
4. No **structured handling of manual operations**
5. No **clear separation between research and implementation**





------





## **Scope**





This memo introduces:





### **1. Architecture Externalization**





Create machine-readable core files:

```
AIOS/
  architecture_constitution.md
  module_graph.yaml
  service_contracts/
  abi_v1.h
  acceptance_tests.yaml
  agent_permissions.yaml
```



------





### **2. Workflow State Machine**





Introduce states:

```
INTAKE
RESEARCHING
SPEC_READY
READY_TO_IMPLEMENT
IMPLEMENTING
READY_FOR_MANUAL_BUILD
READY_FOR_MANUAL_FLASH
READY_FOR_MANUAL_LOG_CAPTURE
READY_TO_INTEGRATE
BLOCKED
CLOSED
```



------





### **3. Module Graph System**





Create:

```
module_graph.yaml
```

Example:

```
modules:
  - name: abi_v1
    deps: []

  - name: dap_runtime
    deps: [abi_v1]

  - name: ui_service
    deps: [abi_v1]

  - name: ui_adapter
    deps: [ui_service]

  - name: app_runtime
    deps: [dap_runtime, ui_service]
```



------





### **4. Research vs Implementation Separation**





Define two execution lanes:





#### **Research Lane**





- analyze Mocor behavior

- identify valid/invalid APIs

- produce:

  

  - mapping docs
  - risk notes
  - recommendations

  







#### **Implementation Lane**





- only starts after SPEC_READY

- produces:

  

  - code
  - docs
  - registry updates

  





------





### **5. Human Gate System (CRITICAL)**





Introduce explicit workflow checkpoints:





#### **Gate 1 — Manual Build**



State:

```
READY_FOR_MANUAL_BUILD
```

Workflow must:



- output build command
- define expected artifacts
- pause execution
- request result input





------





#### **Gate 2 — Manual Flash**



State:

```
READY_FOR_MANUAL_FLASH
```

Workflow must:



- output flash steps (ResearchDownload + key sequence)

- list verification points:

  

  - boot success
  - crash / assert
  - UI behavior

  





------





#### **Gate 3 — Manual Log Capture**



State:

```
READY_FOR_MANUAL_LOG_CAPTURE
```

Workflow must:



- output Logel usage steps
- request exported log file
- feed logs into analysis stage





------





### **6. Planner Mechanism**





Introduce planner logic:



- read module_graph.yaml

- detect modules with satisfied dependencies

- assign state:

  

  - RESEARCHING
  - READY_TO_IMPLEMENT
  - READY_TO_INTEGRATE

  





------





### **7. Integration Layer**





Introduce integration outputs:

```
integration_report.md
blocked_modules.md
flash_candidate_builds.md
```

Purpose:



- detect contract mismatch
- identify blocked modules
- prepare candidates for manual validation





------





## **Out of Scope**





- Full automation of build / flash / log tools
- CI/CD pipeline
- Complete agent autonomy
- Telephony / advanced service expansion





------





## **Constraints**





1. Manual build/flash/log steps must remain human-executed
2. Workflow must explicitly pause at human gates
3. Must be compatible with existing AIOS workflow structure
4. Must not introduce heavy external dependencies
5. Must support incremental adoption





------





## **Expected Deliverables**





1. Create architecture files:



```
architecture_constitution.md
module_graph.yaml
service_contracts/
abi_v1.h
acceptance_tests.yaml
agent_permissions.yaml
```



------





1. Update workflow to support state machine





------





1. Implement planner logic:







- dependency resolution
- module readiness detection





------





1. Implement Human Gate handling:







- build gate
- flash gate
- log capture gate





------





1. Generate integration artifacts:



```
integration_report.md
blocked_modules.md
flash_candidate_builds.md
```



------





1. Update documentation:



```
AIOS_WORKFLOW.md
```

Include:



- state definitions
- execution flow
- human gate behavior





------





## **Verification Method**





- Module graph correctly parsed
- Planner identifies parallelizable modules
- Workflow transitions states correctly
- Human gates trigger correctly and pause execution
- Integration report generated
- Multiple modules can progress concurrently





------





## **Potential Risks**







### **Risk 1 — Over-complexity**





If module graph or state machine is too complex, engineers may not follow it.



Mitigation:



- keep schema minimal
- iterate gradually





------





### **Risk 2 — Incorrect dependency modeling**





Wrong dependencies → false parallelism → integration failure



Mitigation:



- manually review initial module_graph.yaml





------





### **Risk 3 — Research and implementation mixed**





Agents may skip research phase and directly implement unstable APIs.



Mitigation:



- enforce RESEARCHING → SPEC_READY transition





------





## **References**





- Technical Memo Template 
- Technical Memo 39 — Workflow Baseline Audit
- Technical Memo 40 — Multi-Engineer Workflow
- AIOS Architecture (DAP / Service / Adapter model)





------





# **Final Note**





This memo does not aim to automate everything.



It aims to:



> **convert AIOS workflow from human-driven execution into a system that can autonomously advance until it reaches a human gate.**



If successful:



- parallel development becomes real
- human effort is focused on high-value steps
- system complexity becomes manageable





If not:



- development remains bottlenecked by a single operator
- parallel execution remains an illusion





