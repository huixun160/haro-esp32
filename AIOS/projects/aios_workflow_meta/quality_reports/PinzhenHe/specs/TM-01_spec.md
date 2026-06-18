# Frozen Specification — 梳理 Claude-code-main 并迁移到 README_WORKFLOW

## MUST
- [ ] 以 `AIOS/README_WORKFLOW.md` 作为唯一目标文档进行增补与修订。
- [ ] 扫描 `hpz_legacy_code/claude-code-main`（含源码与文档）并提取可迁移信息。
- [ ] 保持 AIOS 现有核心流程不变（注册/登录/TM/执行/收尾），仅做补充与增强。
- [ ] 输出迁移报告、验证清单、差异摘要三类交付物。
- [ ] 完成后可由当前工程师独立阅读并验收可读性。

## SHOULD
- [ ] 新增内容与原文风格一致（标题层级、表格、命令块格式一致）。
- [ ] 迁移内容优先选择“跨项目通用实践”，避免引入特定产品背景叙述。
- [ ] 对来源信息做分类（命令、流程、协作、安全、踩坑）。

## MAY
- [ ] 在后续 TM 中继续追加“项目探索建议”章节（如入口文件定位、模块分层阅读顺序）。
- [ ] 为后续自动化校验新增发布前 checklist 脚本。

## OUT OF SCOPE
- 修改 `claude-code-main` 项目本身。
- 迁移与 AIOS 工作流无关的业务细节。
- 执行 git commit/push。

Approved by: PinzhenHe
Date: 2026-04-07
