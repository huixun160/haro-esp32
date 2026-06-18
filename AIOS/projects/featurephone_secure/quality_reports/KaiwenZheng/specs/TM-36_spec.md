# Frozen Specification — TM-36 Unisoc 平台全量普查与分层决策报告

> Based on TM-36 memo + clarification answers (2026-03-23)

---

## Clarification Answers

| Q# | Answer |
|---|---|
| Q1 (PDF 解析) | 方案 (c)：批量提取 + 关键文档精读。先全量索引，再逐模块深入 |
| Q2 (输出路径) | `docs/api/modules/` + `docs/architecture/` = markdown 人读；`registry/capabilities/` + `registry/apis/` = YAML AI 读 |
| Q3 (分阶段) | 极细粒度：每个模块一个 Phase，先 OS Core → FS → GUI/MMI → Network → ... |
| Q4 (Schema) | `level` (L1/L2/L3) 与 `layer` (APP_CANDIDATE/SERVICE_CANDIDATE/...) 并行共存 |
| Q5 (Deprecated) | 标记为 deprecated 但不删除/不修改代码 |
| 开放1 (PDF 库) | 自行决定，目标是 PDF 可被 LLM 阅读 |
| 开放2 (apis 拆分) | 选 B：按模块拆分 `registry/apis/X.yaml` |
| 开放3 (调用链) | 是，同时参考文档和源码 |

---

## MUST

- [ ] **M1** — 构建 `pdf_extract.py` 工具，支持 PDF→text/markdown 提取
- [ ] **M2** — 生成 `knowledgebase_index.md` — 全量 116 文档目录索引
- [ ] **M3** — 按模块输出 capability YAML：`registry/capabilities/X.yaml`
- [ ] **M4** — 按模块输出人类可读文档：`docs/api/modules/X.md`
- [ ] **M5** — 按模块输出 API YAML：`registry/apis/X.yaml`
- [ ] **M6** — 每个 API 标记 `layer` 标签 (APP_CANDIDATE/SERVICE_CANDIDATE/ADAPTER_ONLY/OS_INTERNAL/UNKNOWN)
- [ ] **M7** — 每个 API 保留 `level` 标签 (L1/L2/L3)，与 `layer` 并行
- [ ] **M8** — Capability Schema：`registry/schema/capability_schema.yaml`
- [ ] **M9** — 覆盖核心模块：OS Core / FileSystem / GUI·MMI / Network / Telephony / Audio
- [ ] **M10** — Master Report：`docs/api/master_report.md`（决策支撑总报告）
- [ ] **M11** — 平台架构文档：`docs/architecture/platform_overview.md` + `capability_map.md`

## SHOULD

- [ ] **S1** — 覆盖扩展模块：Bluetooth / Camera / HAL
- [ ] **S2** — 调用链分析：grep 源码中模块间调用关系
- [ ] **S3** — 每个模块文档中包含调用流程图（Mermaid）
- [ ] **S4** — 标记已被 DAP 封装 vs 未封装的 API（DAP 覆盖率）

## MAY

- [ ] **Y1** — 分层决策文档：`docs/architecture/layer_decision.md`
- [ ] **Y2** — SDK v1 候选 API 列表

## OUT OF SCOPE

- 不修改任何现有 C 代码
- 不做最终架构决策（只做预分层标记）
- 不做废弃接口删除
- 不做设备验证
- 不修改 TM-35 已有的 `apis.yaml`（但新增模块拆分到 `registry/apis/X.yaml`）

---

Approved by: ___________
Date: ___________
