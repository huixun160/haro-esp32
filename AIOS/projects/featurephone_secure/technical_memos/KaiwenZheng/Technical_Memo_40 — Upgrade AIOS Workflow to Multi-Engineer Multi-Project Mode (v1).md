# **Technical Memo 40 — Upgrade AIOS Workflow to Multi-Engineer Multi-Project Mode (v1)**





> This memo upgrades the existing single-engineer AIOS workflow into a **multi-engineer, multi-project collaboration system**, with standardized memo naming, shared knowledge, and execution traceability.



------



**Title:** Multi-Engineer Multi-Project AIOS Workflow Upgrade and Memo Naming System



**Project:** AIOS Feature Phone Platform



**Subsystem:** System Integration / Workflow Infrastructure / Collaboration System



**Author:** AIOS Architecture Team



**Priority:** HIGH



**Date:** 2026-03-24



------





## **Background**





The current AIOS workflow is designed for **single-engineer execution**, based on:



- Technical Memo–driven development
- Local Git-based iteration
- AI-assisted execution via skills/agents/hooks





This system works for one engineer but breaks down under multi-engineer collaboration due to:



1. **No engineer identity binding**
2. **No project-level isolation**
3. **No standardized memo ownership**
4. **No shared knowledge synchronization mechanism**
5. **No execution traceability per engineer**





Additionally:



- Feature phone development has **high iteration cost (~30 min per cycle)**
- Mocor platform has **high complexity and poor documentation**
- Historical issues are frequent and non-obvious





This makes **knowledge reuse and coordination critical**.



------





## **Objective**





Upgrade AIOS workflow to support:





### **1. Multi-Engineer Collaboration**





- Engineers operate independently but within a shared system
- Each engineer has isolated working space







### **2. Multi-Project Parallel Execution**





- Multiple projects (DAP / APP / Adapter / etc.) run simultaneously
- Engineers may contribute to multiple projects







### **3. Standardized Memo Ownership**





- Each memo is uniquely bound to:

  

  - engineer
  - project

  

- Naming enforces traceability







### **4. Shared Pitfall Knowledge**





- Engineers contribute to shared pitfall base
- Knowledge synchronized via GitLab







### **5. Zero-Overhead Assignment Model**





- No centralized assignment system
- Engineers self-register work via memo placement + naming





------





## **Current State**





From TM-39 baseline:



- Agents / skills / hooks exist but partially wired 
- Workflow is memo-driven but **single-threaded**
- Technical memos stored in a flat structure
- No engineer-level or project-level segmentation
- Knowledge sharing exists but is not structured for multi-user use





------





## **Scope**





This memo introduces:





### **Structural changes**





- engineer registry
- project registry
- directory restructuring







### **Naming system**





- enforced memo naming convention







### **Workflow extensions**





- new skills for registration and sync
- execution logging







### **Documentation**





- full README for engineers





------





## **Out of Scope**





- CI/CD integration
- Advanced permission systems
- Distributed repo architecture (multi-repo)
- Automated task assignment systems





------





## **Constraints**





1. Must remain **Git-native**
2. Must work in **single-repo GitLab deployment**
3. Must not break existing workflow
4. Must require **minimal new tooling**
5. Must be understandable by non-expert engineers





------





## **Expected Deliverables**







### **1. Directory Structure Upgrade**





Create:

```
AIOS/

engineers/
  A/
    profile.yaml
  B/
    profile.yaml

projects/
  dap_runtime/
    project.yaml
    technical_memos/
      A/
      B/
    feedback/
      A/
      B/
    pitfalls/

  app_architecture/
    project.yaml
    technical_memos/
    feedback/
    pitfalls/
```



------





### **2. Memo Naming Convention**





All memos must follow:

```
<ENGINEER>_<PROJECT>_TM<XX>_<short_name>.md
```

Example:

```
A_dap_runtime_TM12_loader_refactor.md
B_app_architecture_TM07_ui_flow.md
```



------





### **3. Auto Rename Script**





Create:

```
scripts/rename_memo.py
```

Function:



- parse original filename
- inject engineer + project prefix
- enforce naming format





------





### **4. Engineer Registration Skill**



```
workflow/skills/register-engineer/
```

Function:



- create engineer directory
- generate profile.yaml





------





### **5. Project Registration Skill**



```
workflow/skills/register-project/
```

Function:



- create project structure
- initialize memo / feedback / pitfalls directories





------





### **6. Shared Knowledge Sync Skill**



```
workflow/skills/sync-shared-knowledge/
```

Function:



- pull latest pitfalls
- inject relevant context into workflow





------





### **7. Execution Logging Skill**



```
workflow/skills/log-execution/
```

Output:

```
AIOS/projects/<project>/quality_reports/<engineer>/TM-XX_execution_log.md
```



------





### **8. New Agents**







#### **assignment-reviewer**





- detect ownership conflicts
- detect overlapping work







#### **knowledge-curator**





- promote pitfalls to shared docs





------





### **9. Hook Upgrade**





Modify:

```
hooks/scripts/memo_guard.py
```

Add validation:



- filename matches naming convention
- includes engineer + project





------





### **10. README Documentation**





Create:

```
AIOS/README_WORKFLOW.md
```

Must include:



------





## **README Content (MANDATORY)**







### **1. Quick Start**



```
1. register engineer
2. register project
3. create memo
4. place memo in project folder
5. run workflow
```



------





### **2. Memo Naming Rules**





Explain:

```
A_dap_runtime_TM12_loader_refactor.md
```



------





### **3. Project Structure**





Explain directory hierarchy.



------





### **4. Workflow Steps**



```
memo → clarify → freeze → implement → verify → feedback
```



------





### **5. Feedback System**





Explain:



- SUCCESS / PARTIAL / BLOCKED
- feedback location





------





### **6. Pitfall Sharing**





Explain:



- local vs shared pitfalls
- how to contribute





------





### **7. Git Workflow**



```
branch per engineer
commit must include TM id
```



------





## **Verification Method**





- Engineer registration works
- Project registration creates correct structure
- Memo naming auto-correct works
- Workflow runs per engineer independently
- Feedback files generated correctly
- Pitfalls shared via Git pull/push
- No conflicts between engineers





------





## **Potential Risks**







### **Risk 1 — Naming inconsistency**





Mitigation:



- enforce via script + hook





------





### **Risk 2 — Knowledge fragmentation**





Mitigation:



- knowledge-curator agent





------





### **Risk 3 — Engineers bypass workflow**





Mitigation:



- memo_guard hook enforcement





------





## **References**





- Technical Memo 18 — Workflow Feedback Exit Path
- Technical Memo 19 — Antigravity Skill Fix
- Technical Memo 39 — Workflow Baseline Audit
- AIOS Workflow Architecture
- AIOS Agent Architecture





------





# **Final Note**





This upgrade is not a feature.



It is a transition from:

```
single-engineer scripting
```

to:

```
multi-engineer operating system
```

If done correctly:



- engineers stop duplicating mistakes
- system knowledge compounds
- development speed increases non-linearly





If done incorrectly:



- chaos scales with team size





There is no middle ground.



------

