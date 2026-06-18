下面是一份**可以直接派给工程师执行的 Technical Memo**。

目标是：在 **AIOS Memo-Driven Workflow** 中引入 **Git-level Hooks 体系**，用于自动执行工程治理规则（API 注册、Memo 绑定、文档同步、Pitfall 记录、同步摘要等）。设计遵循 **IDE 无关、Git 原生、Fail-open、<1 秒执行** 的原则。



------





# **Technical Memo**







## **Add Git Hooks Governance Layer to AIOS Memo-Driven Workflow (v1)**





**Project:** AIOS Feature Phone Platform

**Subsystem:** DAP / APP / System Integration

**Author:** Architecture Team

**Target Engineer:** Platform Infrastructure Engineer

**Priority:** HIGH



------





# **1. Objective**





Introduce a **Git Hooks Governance Layer** to enforce the AIOS memo-driven development workflow.



Hooks will automatically:



- ensure code changes are linked to a **Technical Memo**
- enforce **API registry updates**
- encourage **pitfall documentation**
- generate **sync summaries for the team**
- maintain **machine-readable project state**





The system must work regardless of IDE (Antigravity / Claude / Cursor / CLI).



------





# **2. Design Principles**







### **Principle 1 — IDE Independence**





Hooks must rely on **Git hooks + Python scripts**, not IDE-specific hook systems.





### **Principle 2 — Fail-Open**





If a hook script crashes, it must **not block development**.





### **Principle 3 — Fast Execution**





Hooks must execute in **<1 second**.





### **Principle 4 — Governance, Not Build**





Hooks must not run heavy tasks (compilation, simulator).





### **Principle 5 — Knowledge Synchronization**





Code and knowledge must evolve together.



------





# **3. Directory Structure**





Engineer must create the following structure.

```
AIOS/

hooks/
  pre-commit
  pre-push
  post-merge

hooks/scripts/
  api_guard.py
  registry_guard.py
  memo_guard.py
  pitfall_guard.py
  generate_sync_summary.py
```



------





# **4. Hook Responsibilities**





We deploy **three Git hooks**.

| **Hook**   | **Trigger**      | **Purpose**                 |
| ---------- | ---------------- | --------------------------- |
| pre-commit | git commit       | enforce memo + API registry |
| pre-push   | git push         | validate registry integrity |
| post-merge | git pull / merge | generate sync summary       |



------





# **5. Pre-Commit Hook**





File:

```
hooks/pre-commit
```

Content:

```
#!/bin/bash

python hooks/scripts/api_guard.py
python hooks/scripts/registry_guard.py
python hooks/scripts/memo_guard.py
python hooks/scripts/pitfall_guard.py

exit 0
```

Make executable:

```
chmod +x hooks/pre-commit
```



------





# **6. API Guard Script**





File:

```
hooks/scripts/api_guard.py
```

Purpose:



Detect newly introduced public APIs and verify they exist in:

```
registry/apis.yaml
```

Basic detection logic:



- scan .c and .h files
- detect exported functions (DAP_ prefix or public headers)
- compare against registry





Example behavior:

```
WARNING: API detected but not registered

DAP_RegisterApp

Please update registry/apis.yaml
```

Do **not block commit** (warn only in v1).



------





# **7. Registry Guard Script**





File:

```
hooks/scripts/registry_guard.py
```

Purpose:



Validate registry consistency.



Checks:

| **Validation**       | **Description**       |
| -------------------- | --------------------- |
| YAML syntax          | registry files valid  |
| duplicate APIs       | no duplicates         |
| missing module owner | each module has owner |

Example warning:

```
WARNING: module dap_loader has no owner defined
```



------





# **8. Memo Guard Script**





File:

```
hooks/scripts/memo_guard.py
```

Purpose:



Ensure code changes reference a **Technical Memo**.



Rules:



- If files in src/, dap/, mmi/, or adapter/ change
- Commit message must contain:



```
TM-xxx
```

Example valid commit:

```
TM-004 implement DAP download manager
```

Example warning:

```
WARNING: Commit contains code changes but no Technical Memo reference
```



------





# **9. Pitfall Guard Script**





File:

```
hooks/scripts/pitfall_guard.py
```

Purpose:



Encourage knowledge capture.



If commit message contains:

```
fix
bug
crash
panic
segfault
```

Hook prints reminder:

```
Did you update docs/pitfalls/known-issues.md ?
```



------





# **10. Pre-Push Hook**





File:

```
hooks/pre-push
```

Content:

```
#!/bin/bash

python hooks/scripts/api_guard.py
python hooks/scripts/registry_guard.py

exit 0
```

Purpose:



Ensure registry consistency before pushing to remote.



------





# **11. Post-Merge Hook**





File:

```
hooks/post-merge
```

Content:

```
#!/bin/bash

python hooks/scripts/generate_sync_summary.py
```

Purpose:



Generate a team sync report after merges.



------





# **12. Sync Summary Script**





File:

```
hooks/scripts/generate_sync_summary.py
```

Output example:

```
AIOS Platform Sync Summary

New APIs
- DAP_RegisterApp

Modified APIs
- DAP_LoadBin

Migration Updates
- MMK_CreateWin -> DAP_UI_CreateWindow

New Pitfalls
- NV reset required for simulator
```

This summary helps engineers quickly understand project changes.



------





# **13. Hook Installation**





Engineer must link hooks into Git.



Run:

```
ln -s ../../hooks/pre-commit .git/hooks/pre-commit
ln -s ../../hooks/pre-push .git/hooks/pre-push
ln -s ../../hooks/post-merge .git/hooks/post-merge
```

Verify:

```
ls .git/hooks
```



------





# **14. Expected Workflow with Hooks**





Developer workflow becomes:

```
Write Technical Memo
      ↓
AI executes task
      ↓
Engineer verifies
      ↓
git commit (pre-commit hook runs)
      ↓
git push (pre-push hook runs)
      ↓
git pull/merge (post-merge summary)
```

Hooks enforce governance automatically.



------





# **15. Performance Constraints**





Hooks must meet:

| **Metric**          | **Target**            |
| ------------------- | --------------------- |
| Execution time      | <1 second             |
| Python dependencies | standard library only |
| Crash behavior      | fail-open             |



------





# **16. Acceptance Criteria**





Hooks system considered operational if:



- pre-commit warns when memo reference missing
- API guard detects new interfaces
- registry validation works
- sync summary generated after merges





------





# **17. Deployment Time Estimate**



| **Task**        | **Time** |
| --------------- | -------- |
| directory setup | 10 min   |
| scripts         | 2 hours  |
| hook linking    | 10 min   |
| testing         | 1 hour   |

Total:



**~3 hours**



------





# **18. Future Enhancements**





Planned improvements:



1. automatic **API dependency graph**
2. **legacy API detection**
3. **architecture diagram generation**
4. **DAP vs Mocor boundary analysis**
5. **automated code scanning**





These features will evolve the system into an **AIOS Platform Knowledge Graph**.



------





# **Final Note**





Hooks are not a convenience feature.



They are the **automated enforcement layer** of the AIOS engineering governance system.



Without hooks, workflow rules become optional.

With hooks, **engineering discipline becomes automatic**.



------



如果你愿意，我可以继续帮你做一件**对这个项目极其关键的升级**：



我可以给你设计一个 **Mocor / DAP C 代码自动扫描器**，它会自动生成：



- API registry
- 模块依赖图
- DAP vs legacy 调用图
- 系统架构图





这个工具在功能机平台项目里会非常有价值。