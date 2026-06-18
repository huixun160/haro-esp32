# Frozen Specification — TM-01: AIOS Workflow GitLab Integration

**Session:** KaiwenZheng @ aios_workflow_meta

## MUST
- [ ] `manifest.yaml` 新增 `git:` 段（remote SSH/HTTP + branch_pattern `eng/{engineer}/{project}`）
- [ ] `/aios-close` 输出 push 指引（含工程师名、项目名、分支名、`git push` 命令）
- [ ] `/aios-login` 显示当前分支名（`eng/<engineer>/<project>`）
- [ ] `/aios-onboard` 添加 GitLab 设置提醒（clone + SSH/HTTP 配置）
- [ ] `package-commit` skill 添加 push 提示
- [ ] `git-manual-commit` rule 扩展为 commit + push
- [ ] `README_WORKFLOW.md` 添加 GitLab 章节（clone, SSH, HTTP, branch, push 步骤）
- [ ] 回滚方案：GitLab 不可用时可本地继续工作，恢复后再 push

## SHOULD
- [ ] `memo_guard.py` 添加分支名校验（`eng/<engineer>/<project>` 格式）
- [ ] 验收标准具体化（SSH 测试命令、clone 验证、push exit code）

## MAY
- [ ] `/aios-login` 自动检测 remote 是否已配置

## OUT OF SCOPE
- CI/CD pipelines
- Merge request 策略（未来由专门 agent 负责）
- 权限系统
- 自动化测试
- 冲突解决 agent（Q2.3 提到的，留给未来 TM）

## 关键决策（来自 Clarify）
- GitLab repo 已存在（`192.168.0.92:feature-phone/fp-aios-kz.git`）
- 账号权限由 KaiwenZheng 手动管理
- 一个工程师可有多个分支（per project）
- 有 main 分支，由 KaiwenZheng/James 负责 merge
- GitLab 不可用时降级为本地 Git（方案 A）
