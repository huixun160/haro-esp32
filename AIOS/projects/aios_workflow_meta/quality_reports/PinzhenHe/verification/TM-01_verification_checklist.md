# TM-01 Verification Checklist

## 1) 内容完整性
- [x] 已输出迁移报告（`reports/TM-01_migration_report.md`）
- [x] 已修订 `AIOS/README_WORKFLOW.md`
- [x] 已输出差异摘要（`reports/TM-01_diff_summary.md`）

## 2) 格式一致性
- [x] 新增章节遵循 README 现有中文说明风格
- [x] 命令块与条目样式保持一致
- [x] 未破坏原有标题层级与结构

## 3) 逻辑一致性
- [x] 未修改 AIOS 核心工作流流程
- [x] 新增内容为协作与发布安全补充，不与既有规则冲突
- [x] 未引入外部项目专属业务逻辑

## 4) 可读性（工程师自验）
- [x] 当前工程师可独立理解新增检查项
- [x] 新增检查项可直接执行，非概念性描述

## 5) 手工命令建议（可选）
```bash
git diff -- AIOS/README_WORKFLOW.md
```
