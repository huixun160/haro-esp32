# TM-02 兼容性分析报告：AIOS 与 Codex/Cursor 适配方案（文档版）

## 1. 背景与目标
- 背景：AIOS 为功能机与嵌入式约束场景，开发环境与通用软件工程差异大。
- 本轮目标：给出 Codex/Cursor 接入 AIOS 的兼容性分析与 Adapter 方案，不做代码实现。
- 约束确认：
  - 以文档交付为主。
  - 不改现有 build/flash 代码链路。
  - 保留未来扩展到其他 AI 工具的能力。

## 2. 兼容性评估结论（总览）

| 维度 | Codex | Cursor | 结论 |
|---|---|---|---|
| 工程结构理解 | 中-高 | 中-高 | 需提供结构描述文件提升稳定性 |
| 构建系统适配 | 中 | 中 | 需 Adapter 封装统一入口，避免直接调用底层脚本 |
| 工具链调用能力 | 中 | 中 | 需白名单命令与环境探测 |
| 调试与日志支持 | 中 | 中 | 需统一日志解析与模式库 |
| 安全可控性 | 中 | 中 | 需二次确认与危险操作分级 |

结论：可接入，但必须经过 Adapter 层治理，不能直接裸连 legacy 工具链。

## 3. 关键不兼容点（至少 5 项）与落地方案

### 3.1 非标准工程结构导致入口识别不稳定
- 症状：AI 工具难以自动识别“哪个目录是主入口、哪个是平台层、哪个是输出层”。
- 根因：AIOS 目录历史包袱重，跨模块路径与命名不统一。
- 方案：
  - 引入工程描述文件 `aios_project.yaml`（见第 5 节）。
  - 将“模块边界、构建入口、输出产物”结构化声明给 AI。

### 3.2 构建系统与工具链强平台绑定
- 症状：AI 生成通用命令（如标准 cmake/make）无法在目标工程工作。
- 根因：Arm CC + 定制脚本 + Windows 环境依赖明显。
- 方案：
  - 通过 Adapter 定义统一命令语义：`build/flash/logs`。
  - 由 Adapter 将语义命令映射为项目内真实命令与参数模板。

### 3.3 烧录流程高风险，误操作代价高
- 症状：flash 操作可能误刷设备，存在中断风险。
- 根因：设备模式切换与工具调用需要人工确认，不应被 AI 自动直驱。
- 方案：
  - 将 flash 设为“受控动作”：默认人工确认、支持审批日志。
  - 增加执行前检查：设备识别、目标包校验、版本匹配校验。

### 3.4 日志体系非统一，AI 难做稳定解析
- 症状：日志来源分散、关键词不统一，AI 反馈可重复性差。
- 根因：历史模块各自打印风格不同，缺少统一模式库。
- 方案：
  - 建立日志模式词典（成功/失败/风险信号）。
  - 在 Adapter 中提供日志分层解析：构建日志、烧录日志、运行日志分流处理。

### 3.5 AI 代码生成容易偏离嵌入式约束
- 症状：可能生成超内存、超依赖、不可链接代码。
- 根因：通用 LLM 对嵌入式约束缺少上下文边界。
- 方案：
  - 提供“生成前置约束模板”（模块边界、禁用 API、资源上限）。
  - 增加“生成后静态检查清单”（头文件来源、依赖层级、内存与线程约束）。

### 3.6 兼容范围扩展性不足（可选加固）
- 症状：仅为 Codex/Cursor 定制会导致未来迁移成本高。
- 根因：工具特性被写死在流程里。
- 方案：
  - 使用 `tool_profile` 机制，按工具声明能力矩阵，不改主流程。
  - 将 AI 工具差异收敛到配置层，不收敛到业务流程层。

## 4. Adapter 层设计（仅设计，不实现）

## 4.1 架构分层
1. `Intent Layer`：接收 AI 意图（build/flash/logs/analyze）。
2. `Policy Layer`：权限校验、风险分级、确认策略。
3. `Execution Layer`：命令映射与执行（受控调用）。
4. `Feedback Layer`：日志解析与结构化反馈（JSON/markdown）。

## 4.2 最小能力接口（草案）
- `adapter.build(target, profile)` -> `{status, artifact_hint, logs}`
- `adapter.flash(image, device)` -> `{status, confirmation_id, logs}`
- `adapter.logs(source, filters)` -> `{status, highlights, anomalies}`
- `adapter.inspect(project)` -> `{status, structure_summary, warnings}`

## 4.3 安全策略
- 风险动作（flash/批量替换/跨目录写入）必须二次确认。
- 执行日志可追溯（时间、发起者、参数摘要、结果）。
- 提供“只读演练模式”用于首次接入验证。

## 5. AIOS 工程结构描述方案（`aios_project.yaml` 示例）

```yaml
project:
  id: aios_workflow_meta
  platform: unisoc_featurephone
  language: [c, makefile, markdown]

layout:
  source_roots:
    - AIOS
    - make
    - Third-party
  workflow_root: .agents/workflows
  reports_root: AIOS/projects/aios_workflow_meta/quality_reports

build:
  entry_hints:
    - make.bat
    - mm.bat
  toolchain: armcc
  outputs_hint:
    - build/*/img/*.pac
    - out/*.bin

operations:
  commands:
    build: "aios build"
    flash: "aios flash"
    logs: "aios logs"
  risk_level:
    build: medium
    flash: high
    logs: low

policies:
  require_confirmation:
    - flash
  forbid_direct:
    - raw_mass_replace
    - unbounded_delete
```

说明：以上为结构描述草案，用于 AI 理解项目，不代表本轮实现。

## 6. Build/Flash/Log 的 AI 接入流程设计

## 6.1 Build 接入
- 输入：目标平台、构建配置、可选模块。
- 处理：Adapter 进行环境探测与命令映射。
- 输出：构建状态、产物路径提示、关键错误摘要。

## 6.2 Flash 接入
- 输入：镜像路径、设备标识。
- 处理：执行前确认 + 参数校验 + 设备状态检查。
- 输出：烧录结果、失败分型、回滚建议。

## 6.3 Logs 接入
- 输入：日志源、时间窗、关键词。
- 处理：结构化提取成功信号与异常信号。
- 输出：摘要、根因候选、下一步排查建议。

## 7. AI 代码生成规范（Prompt + 模板）设计

## 7.1 Prompt 约束模板（建议）
- 指定模块边界：仅允许修改目标目录。
- 指定依赖边界：禁止引入未批准第三方依赖。
- 指定资源边界：内存/栈/线程模型约束。
- 指定输出格式：变更清单 + 风险说明 + 验证步骤。

## 7.2 代码骨架模板（建议）
- Header include 顺序规范。
- 错误码与日志输出统一模板。
- 平台 API 适配层调用模板（禁止直连危险接口）。

## 8. 日志解析与反馈机制设计
- 统一模式：
  - 成功模式：`BUILD SUCCESS`, `FLASH OK`（可扩展）
  - 失败模式：`error`, `assert`, `exception`, `failed`
- 输出结构：
  - `summary`：任务状态
  - `highlights`：关键日志片段
  - `anomalies`：异常分型
  - `actions`：下一步建议

## 9. 分阶段落地路线图（建议）
1. 阶段 1（文档与配置）：完善 `aios_project.yaml`、命令映射表、日志模式库。
2. 阶段 2（最小可用）：实现只读 `inspect/logs`。
3. 阶段 3（受控执行）：接入 `build`，引入结果回传结构。
4. 阶段 4（高风险治理）：接入 `flash`，启用审批与审计。

## 10. 验收建议（文档型）
- 必要文档齐全，且可直接指导后续实现。
- 不出现“默认自动 flash”类高风险设计。
- 方案明确区分“本轮设计”与“后续实现”。

## 附：Assignment Reviewer 结果
- 结论：`WARNING`
- 原因：输入 memo 文件名 `PinzhwnHe_AIOSjianrong_TM02_AIOS.md` 未完全满足命名规范，且工程师名疑似拼写偏差（`PinzhwnHe` vs `PinzhenHe`）。
- 处理：本轮不重命名原文件，避免路径断裂；建议在后续 TM 统一规范命名。
