

# **Technical Memo**







## **Deploy Memo-Driven AIOS Development Workflow (v1)**





**Project:** AIOS Feature Phone Platform

**Subsystem:** DAP / APP / System Integration

**Author:** Architecture Team

**Target Engineer:** Platform Infrastructure Engineer

**Priority:** HIGH



------





# **1. Objective**





Deploy a **Technical Memo–Driven Engineering Workflow** for the AIOS feature phone platform.



This workflow must support:



1️⃣ Technical memo driven task execution

2️⃣ AI clarification before execution

3️⃣ AI-assisted implementation

4️⃣ Engineer verification loop

5️⃣ Knowledge consolidation

6️⃣ Git/GitHub synchronization



The workflow must be:



- IDE independent
- Git native
- machine readable
- scalable to multiple engineers





------





# **2. Problem Statement**





Current engineering workflow has the following issues:

| **Problem**                        | **Impact**               |
| ---------------------------------- | ------------------------ |
| Unknown APIs                       | duplicated interfaces    |
| Missing architecture documentation | onboarding difficulty    |
| Repeated debugging pitfalls        | engineering inefficiency |
| Unclear module ownership           | code conflicts           |
| Knowledge stored in chats          | project memory loss      |

These issues will worsen as the platform grows.



------





# **3. Design Principles**





This system is based on five principles.





### **Principle 1 — Memo Driven Development**





Every engineering task must begin with a **Technical Memo**.



No memo → no implementation.



------





### **Principle 2 — Clarification Before Execution**





AI must identify ambiguities and ask clarification questions before modifying code.



------





### **Principle 3 — Human Verification**





AI prepares verification steps.

Engineer performs the verification.



------





### **Principle 4 — Knowledge Persistence**





Every completed task must produce:



- documentation
- registry updates
- pitfall records





------





### **Principle 5 — Git as the Single Source of Truth**





All knowledge must be versioned alongside code.



------





# **4. Workflow Overview**





Complete workflow cycle:

```
Technical Memo
        ↓
Memo Intake
        ↓
Ambiguity Detection
        ↓
Clarification Q&A
        ↓
Spec Freeze
        ↓
Implementation
        ↓
Engineer Verification
        ↓
Knowledge Consolidation
        ↓
Git Commit / PR
        ↓
Next Technical Memo
```



------





# **5. Repository Structure**





Engineer must initialize the following directory structure.

```
AIOS/

AIOS_WORKFLOW.md
AI_CONTEXT.md
MEMORY.md

technical_memos/

docs/
  architecture/
  api/
  runbooks/
  pitfalls/

registry/
  apis.yaml
  modules.yaml
  migration-status.yaml
  ownership.yaml
  decisions.yaml

workflow/
  rules/
  agents/
  skills/
  templates/

scripts/
  api_scanner.py
  generate_sync_summary.py

quality_reports/
  plans/
  specs/
  session_logs/
  sync_summaries/
```



------





# **6. AIOS_WORKFLOW.md**





Create file:

```
AIOS_WORKFLOW.md
```

This file defines the project workflow rules.



Example content:

```
# AIOS Memo Driven Development Workflow

All engineering tasks must follow the Technical Memo workflow.

Execution sequence:

1 Technical memo intake
2 Ambiguity clarification
3 Spec freeze
4 Implementation
5 Engineer verification
6 Knowledge consolidation
7 Git commit

AI must not implement tasks without a technical memo.

If memo contains ambiguities, AI must ask clarification questions.
```



------





# **7. AI_CONTEXT.md**





This file provides **persistent project context for AI systems**.



Example structure:

```
Project: AIOS Feature Phone Platform

Architecture Layers:

APP
↓
DAP Runtime
↓
Adapter Layer
↓
Mocor OS
↓
Hardware

Current DAP Responsibilities:

bin loader
app registry
runtime memory relocation
app lifecycle

Legacy APIs must be accessed only via adapter layer.
```



------





# **8. Registry System**





Registry stores **machine-readable project state**.



Create directory:

```
registry/
```



------





## **8.1 API Registry**





File:

```
registry/apis.yaml
```

Example:

```
- api: DAP_RegisterApp
  layer_from: APP
  layer_to: DAP
  owner: platform_team
  stability: beta
  thread_context: app_task
  input: app_manifest_t*
  output: int
  error_codes:
    - DAP_OK
    - DAP_EINVAL
    - DAP_EEXIST
```



------





## **8.2 Module Registry**



```
registry/modules.yaml
```

Example:

```
- module: dap_loader
  owner: platform_team
  layer: dap_core
  depends_on:
    - relocation_engine
    - app_registry
```



------





## **8.3 Migration Registry**



```
registry/migration-status.yaml
```

Example:

```
- legacy_api: MMK_CreateWin
  dap_wrapper: DAP_UI_CreateWindow
  status: wrapped
  remaining_calls: 12
```



------





# **9. Workflow Rules**





Create:

```
workflow/rules/
```



------





## **memo-required.md**



```
All tasks must begin with a Technical Memo.

AI must not implement tasks without memo input.
```



------





## **ambiguity-first.md**



```
If memo contains unclear information, AI must ask clarification questions before execution.
```



------





## **spec-freeze.md**



```
After clarification, AI must generate a frozen spec before implementation.
```



------





## **api-registration-required.md**



```
All public APIs must be registered in registry/apis.yaml before implementation.
```



------





## **pitfall-log-required.md**



```
All resolved platform bugs must create an entry in docs/pitfalls.
```



------





# **10. Workflow Skills**





Create:

```
workflow/skills/
```



------





## **intake-memo**





Purpose:



Parse technical memo.



Extract:



- objectives
- scope
- constraints
- deliverables
- verification requirements





------





## **clarify-memo**





Purpose:



Generate clarification questions.



Example questions:



- which module should implement this API?
- is legacy compatibility required?
- simulator or real-device verification?
- does API require versioning?





------





## **freeze-spec**





Generate specification:

```
MUST
SHOULD
MAY
OUT OF SCOPE
```



------





## **plan-task**





Produce:



- file modification list
- module impact list
- risk areas





------





## **execute-task**





Modify:



- source code
- documentation
- registry





------





## **prepare-verification**





Output engineer checklist:

```
build command
simulator steps
expected log outputs
success criteria
```



------





## **close-task**





Produce:



- session log
- pitfall record
- registry updates





------





## **package-commit**





Generate:

```
commit message
PR summary
sync summary
```



------





# **11. Workflow Agents**





Create:

```
workflow/agents/
```



------





## **memo-critic**





Checks:



- missing requirements
- ambiguous goals
- missing verification criteria





------





## **api-governor**





Checks:



- duplicated APIs
- missing error codes
- naming consistency





------





## **boundary-reviewer**





Checks:



- direct legacy calls
- architecture violations





------





## **embedded-reviewer**





Checks:



- pointer safety
- memory usage
- return value validation





------





## **closeout-reviewer**





Checks:



- docs updated
- registry updated
- verification checklist exists





------





# **12. Technical Memo Template**





Create template:

```
workflow/templates/technical_memo_template.md
```

Example:

```
Title:

Background:

Objective:

Current State:

Scope:

Out of Scope:

Constraints:

Expected Deliverables:

Verification Method:

Potential Risks:
```



------





# **13. Verification Checklist Template**



```
workflow/templates/verification_checklist.md
```

Example:

```
Build Steps
Simulator Steps
Device Steps
Expected Logs
Success Criteria
Failure Indicators
```



------





# **14. Sync Summary Script**





Create:

```
scripts/generate_sync_summary.py
```

Outputs:

```
New APIs
Modified APIs
New Modules
Migration Updates
New Pitfalls
```



------





# **15. Deployment Steps**





Engineer must perform the following steps.





### **Step 1**





Create directory structure.



------





### **Step 2**





Create registry YAML files.



------





### **Step 3**





Create workflow rules.



------





### **Step 4**





Create workflow skills.



------





### **Step 5**





Create workflow agents.



------





### **Step 6**





Add memo template.



------





### **Step 7**





Test workflow with sample memo.



------





# **16. Acceptance Criteria**





System is operational if:



- tasks require technical memo
- AI asks clarification questions
- APIs tracked in registry
- pitfalls documented
- sync summaries generated





------





# **17. Estimated Deployment Time**



| **Task**       | **Time** |
| -------------- | -------- |
| repo structure | 1 hour   |
| workflow rules | 2 hours  |
| skills         | 3 hours  |
| agents         | 2 hours  |
| testing        | 2 hours  |

Total:



**~1 working day**



------





# **Final Note**





This workflow is not documentation.



It is **AIOS Engineering Governance Infrastructure**.



It enables:



- scalable engineering collaboration
- platform knowledge persistence
- safe architecture evolution
- AI-assisted development without losing control



