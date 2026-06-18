---
description: Create a new AIOS project
---

# AIOS New Project — 新建项目

为已注册工程师创建一个新项目。

## 前置条件
- 工程师必须已注册（`AIOS/engineers/<name>/profile.yaml` 存在）
- 如果未注册，请先运行 `/aios-onboard`

## 步骤

### 1. 验证身份
检查是否有已注册工程师。如果未注册 → 重定向到 `/aios-onboard`。

### 2. 收集项目信息
询问工程师以下信息：
- **项目 ID**（短名，例如 `featurephone_app_arch`）
- **显示名称**（例如 `Feature Phone App Architecture`）
- **描述**（简短说明）
- **平台**（例如 `Unisoc Mocor`）
- **构建目标**（如果有）

### 3. 创建项目
Apply the `register-project` skill from `AIOS/workflow/skills/register-project.md`.
- 创建 `AIOS/projects/<project_id>/project.yaml`
- 创建项目目录结构（technical_memos, feedback, quality_reports, pitfalls）
- 创建工程师个人子目录

### 4. 更新工程师档案
将新项目添加到 `AIOS/engineers/<engineer>/profile.yaml` 的 `projects` 列表。

### 5. 确认
显示创建结果：
```
✅ 项目已创建：<project_id>
📁 路径：AIOS/projects/<project_id>/
📝 你的 TM 目录：AIOS/projects/<project_id>/technical_memos/<engineer>/
🔢 TM 编号从 TM-01 开始
```

### 6. 提示登录
提示工程师运行 `/aios-login` 切换到新项目，或者直接自动登录到新项目。

### 7. Git 提交
引导工程师提交：
```
git add AIOS/projects/<project_id>/ AIOS/engineers/<engineer>/profile.yaml
git commit -m "[project] 创建项目: <project_id>"
```
