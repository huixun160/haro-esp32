# Frozen Specification — TM-35 AIOS API 梳理、YAML 注册与决策报告生成 (V2)

> Based on TM-35 memo + clarification answers (2026-03-23)

---

## Clarification Answers (embedded)

| Q# | Answer |
|---|---|
| Q1 (ABI ID 体系) | TM-35 的目标是梳理 **Unisoc 底层可用 API**（非 DAP 已有 API），为决策"哪些迁入 DAP / 哪些走其他架构"提供数据支撑。与 `dap_interface_id.h` 独立。 |
| Q2 (验证 APP) | 当前只梳理，不验证可用性。未来可能构造假设参考 app 验证。 |
| Q3 (YAML 验证) | 选 (c)：`yamllint` 格式校验 + Python `yaml.safe_load` + schema 校验脚本 |
| 存储位置 | `AIOS/registry/apis.yaml`(机器可读 YAML) + `AIOS/docs/api/`(人类可读 markdown) 两者都用 |
| ABI 字段 | `abi` 字段设为 optional，当前阶段不强制填写 |

---

## MUST

- [ ] **M1** — 全量扫描 Unisoc 底层 API 来源文件，输出 `AIOS/docs/api/api_inventory.md`
  - 扫描范围：DAP platform 封装层（`DAP_InstallOSAPI_unisoc.c`、`DAP_Loader_unisoc.c`、`dap_gui_unisoc.c`、`dap_audio_bridge.c`）+ 对应的 Unisoc 底层 API
  - 覆盖模块：Memory / File / Timer / Debug / Time / GUI / Audio
  - 每个 API 记录：名称、所属模块、参数、返回值、功能说明、来源
- [ ] **M2** — 将所有已梳理 API 注册到 `AIOS/registry/apis.yaml`（扩展现有 28 条记录）
  - YAML schema 添加 TM-35 新字段：`module`、`level`(L1/L2/L3)、`stability`、`source`、`constraints`、`dependency`、`exposure`
  - `abi` 字段 optional
  - 保持向后兼容现有 28 条记录
- [ ] **M3** — 定义并实施 `AIOS/registry/schema/api_schema.yaml` 用于 schema 校验
- [ ] **M4** — 输出 3 份分析报告：
  - `AIOS/docs/api/reports/api_summary.md` — 统计: API 总数 / 各模块数量 / L1-L3 分布 / stable-beta 比例
  - `AIOS/docs/api/reports/api_gap_analysis.md` — 缺失能力 / 重复实现 / 设计不合理
  - `AIOS/docs/api/reports/api_risk_analysis.md` — 直接暴露底层 / ABI 不稳定 / 强耦合 / 不可迁移
- [ ] **M5** — YAML 验证通过：`yamllint` + Python schema 校验脚本
- [ ] **M6** — API 无重复 ID / 每个 API 有 level 与 module

## SHOULD

- [ ] **S1** — 输出 Service Mapping：`AIOS/docs/api/aios_service_architecture.md`
  - Service 划分（UI / Network / Storage / Media / System 等）
  - 每个 Service 的 API 列表（引用 registry YAML）
  - Mermaid 架构图
- [ ] **S2** — 扫描现有 Unisoc SDK 头文件中尚未被 DAP 封装的 API（发现潜在能力）
- [ ] **S3** — 报告与 YAML 数据保持一致（报告可从 YAML 生成/验证）

## MAY

- [ ] **Y1** — ABI 候选生成：从 YAML 中自动生成 `abi_v1_draft.h` 草案
  - 仅针对已确认迁入 DAP 的 API（当前阶段可能无此类 API）
- [ ] **Y2** — 自动化报告生成脚本（从 YAML 生成 markdown 报告）

## OUT OF SCOPE

- 实际代码重构（只做梳理，不改代码）
- 性能优化
- UI 开发
- SDK 发布
- 修改现有 `dap_interface_id.h` 或 `dap_api.h`
- 设备验证（本任务纯文档/数据产出）

---

Approved by: ___________  
Date: ___________
