---
description: Intake and parse a Technical Memo
---

# AIOS Intake — Technical Memo Parser

解析 Technical Memo 并准备进入工作流。

## 前置条件
- **必须有活跃的登录 session**（先运行 `/aios-login`）

> ⚠️ **未登录则停止，重定向到 `/aios-login`。**

## 步骤

### 0. Login Gate
验证 ACTIVE_ENGINEER 和 ACTIVE_PROJECT 已设置。
未设置 → **停止**，指引工程师运行 `/aios-login`。

### 1. Check Onboarding
验证 `AIOS/engineers/<ACTIVE_ENGINEER>/profile.yaml` 存在。
未注册 → 重定向到 `/aios-onboard`。

### 1.5. 文件名规范检查
检查 TM 文件名是否符合命名规范：`<ENGINEER>_<PROJECT>_TM<XX>_<name>.md`

如果不符合：
- 自动推断正确的文件名（从文件内容提取 TM 编号和标题）
- **自动重命名文件**到正确格式
- 通知工程师重命名结果

示例：
```
原文件名：Technical Memo 1 — AIOS Workflow GitLab Integration Project (v1).md
重命名为：KaiwenZheng_aios_workflow_meta_TM01_gitlab_integration.md
```

### 2. Parse Memo
Apply the `intake-memo` skill from `AIOS/workflow/skills/intake-memo.md`.
提取：objectives, scope, constraints, deliverables, verification requirements.

### 3. Critique
Apply the `memo-critic` agent from `AIOS/workflow/agents/memo-critic.md`.
评估完整性和质量。

### 4. Report
展示结构化提取结果和发现的问题。
如有问题 → 建议运行 `/aios-clarify`。
如无问题 → 建议运行 `/aios-workflow` 继续。
