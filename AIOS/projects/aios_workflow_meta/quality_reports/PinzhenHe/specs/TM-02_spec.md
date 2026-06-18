# Frozen Specification - TM-02 AIOS 与 Codex/Cursor 兼容性分析与适配方案

## MUST
- [ ] 交付一份中文兼容性分析报告，覆盖 Codex 与 Cursor 在 AIOS 场景下的接入可行性。
- [ ] 至少识别 5 个关键不兼容点，并给出可落地的缓解方案与风险说明。
- [ ] 给出可扩展的 Adapter 层设计，支持未来新增 AI 编程工具而不重构主流程。
- [ ] 给出 AIOS 工程结构描述方案（含 `aios_project.yaml` 示例草案）。
- [ ] 给出 build/flash/log 流程的 AI 接入方案设计（仅设计，不实现）。
- [ ] 输出文档均为中文。
- [ ] 修正原 memo 中 `out.bin` 作为唯一验收产物的描述偏差，不作为本次硬性验收条件。

## SHOULD
- [ ] 给出安全与权限控制策略（尤其是 flash 风险控制）。
- [ ] 给出面向 AI 生成代码的规范模板（Prompt 约束与代码骨架建议）。
- [ ] 给出分阶段落地路线图（PoC/试点/全面接入）。

## MAY
- [ ] 给出最小 CLI 命令集建议（例如 `aios build|flash|logs`）的接口草案。
- [ ] 给出与现有 AIOS workflow 的映射关系图（命令到技能/规则）。

## OUT OF SCOPE
- 不实现 Adapter CLI 或任何自动化脚本。
- 不改动现有底层芯片驱动与编译系统实现。
- 不执行真实设备烧录与真实构建验证。
- 不进行模型训练、微调或 IDE 完整开发。

Approved by: PinzhenHe
Date: 2026-04-13
