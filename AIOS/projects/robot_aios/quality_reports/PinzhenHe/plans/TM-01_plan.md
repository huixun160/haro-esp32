# Implementation Plan - TM-01 Robot AIOS Voice Platformization

## File Changes
| Action | File | Module | Description |
|--------|------|--------|-------------|
| CREATE | `AIOS/projects/robot_aios/quality_reports/PinzhenHe/specs/TM-01_spec.md` | quality | 冻结规格归档 |
| CREATE | `AIOS/projects/robot_aios/quality_reports/PinzhenHe/plans/TM-01_plan.md` | quality | 实施计划归档 |
| CREATE | `src/server/lschat_server/voice_aios_stub.c` | cloud provider | AIOS provider stub and observability hooks |
| CREATE | `src/server/lschat_server/voice_service_debug.h` | cloud debug | Runtime debug/provider control public interface |
| CREATE | `src/server/lschat_server/voice_service_debug.c` | cloud debug | Provider/status/debug/robot validation helpers |
| CREATE | `src/server/lschat_server/wakeup/wakeup_uplink_sink.h` | wakeup | Wakeup uplink sink boundary |
| CREATE | `src/server/lschat_server/wakeup/wakeup_uplink_sink.c` | wakeup | Default wakeup uplink sink implementation |
| CREATE | `src/shell/cmd/aios.c` | shell | TM01 shell debug entrypoints |
| CREATE | `apps-ui/apps/llm/presenters/setting_debug_presenter.c` | ui | 平台调试页 presenter |
| CREATE | `apps-ui/apps/llm/views/setting/setting_debug_view.h` | ui | 平台调试页 view API |
| CREATE | `apps-ui/apps/llm/views/setting/setting_debug_view.c` | ui | 平台调试页 view 实现 |
| CREATE | `AIOS/docs/architecture/robot_aios_voice_platformization_tm01.md` | docs | TM01 架构边界说明 |
| MODIFY | `src/server/lschat_server/voice_cloud.h` | cloud facade | 扩展 provider / AIOS / debug config fields |
| MODIFY | `src/server/lschat_server/voice_cloud.c` | cloud facade | Provider select, AIOS stub routing, MCP transport hookup |
| MODIFY | `src/server/lschat_server/CMakeLists.txt` | build | 编译新增 runtime/debug/provider 文件 |
| MODIFY | `src/server/lschat_server/mcp/mcp.h` | mcp | 增加 transport 注册接口 |
| MODIFY | `src/server/lschat_server/mcp/mcp.c` | mcp | 异步响应改走 transport boundary |
| MODIFY | `src/server/lschat_server/wakeup/CMakeLists.txt` | wakeup | 编译 uplink sink 文件 |
| MODIFY | `src/server/lschat_server/wakeup/app_wakeup.c` | wakeup | 输出音频改走 uplink sink |
| MODIFY | `src/category/comm/app_datas.h` | config | 扩展 provider/debug/ui version runtime fields |
| MODIFY | `src/category/comm/app_datas.c` | config | 加载默认值、ROMFS 键、日志输出 |
| MODIFY | `src/category/comm/msgs/voice_platform.c` | platform | provider-aware connect path + TM01 validation event logging |
| MODIFY | `src/category/comm/msgs/voice_wakeup_msg.c` | wakeup | continuous/session flags routed via app data |
| MODIFY | `src/middleware/config/config_parser.h` | config parser | 扩展 AIOS/platformization schema |
| MODIFY | `src/middleware/config/config_parser.c` | config parser | 解析 AIOS/provider/debug/ui version fields |
| MODIFY | `src/framework/voice_msg.h` | framework | 新增 TM01 平台调试/验证消息 |
| MODIFY | `src/shell/cmd/CMakeLists.txt` | shell | 编译 `aios.c` |
| MODIFY | `apps-ui/apps/llm/models/model_voice.h` | ui model | 增加 TM01 debug/model facade APIs |
| MODIFY | `apps-ui/apps/llm/models/model_voice.c` | ui model | 连接 provider/debug runtime helpers |
| MODIFY | `apps-ui/apps/llm/lisa_ui_nav_scr_ids.h` | ui nav | 注册调试页导航 ID |
| MODIFY | `apps-ui/apps/llm/lisa_ui_app.c` | ui nav | 注册调试页 screen |
| MODIFY | `apps-ui/apps/llm/presenters/CMakeLists.txt` | ui build | 编译调试页 presenter |
| MODIFY | `apps-ui/apps/llm/views/setting/CMakeLists.txt` | ui build | 编译调试页 view |
| MODIFY | `apps-ui/apps/llm/presenters/setting_presenter.c` | ui | 设置主页新增平台调试入口 |
| MODIFY | `AIOS/registry/apis.yaml` | governance | 注册新增 public APIs |

## Module Impact
- `cloud facade`：`voice_cloud_*` 对上层保留不变，但底层具备 provider 选择与 AIOS stub 路径。
- `config/runtime`：`app_datas` 成为 TM01 provider/debug/ui version 的运行时承载点，`config_parser` 同步扩展 schema。
- `mcp runtime`：异步响应通过 transport callback 发送，弱化对旧消息回传路径的耦合。
- `wakeup`：wake-up 输出流通过 sink boundary 上送，便于后续替换具体云实现。
- `shell/ui`：新增可观测调试面，用于 provider、PAD、robot validation、volume 等 TM01 联调。
- `governance/docs`：新增架构说明与 API 注册，满足 workflow 治理要求。

## Risk Areas
- `voice_cloud.c` 现有职责很重，改动点集中。
  - 缓解：保持符号级 facade，不大拆已有 LSC 逻辑，只在入口增加 provider 路由。
- `apps-ui` 现有设置页是手工注册导航结构，新增页面容易遗漏注册点。
  - 缓解：一次性同时改 `nav ids`、`app init`、`setting presenter`、`CMakeLists`。
- `listen_volume` / 播放链路在当前仓库的编译归属不够直观。
  - 缓解：调试接口优先使用已存在函数声明，若运行时未启用则保持日志型 fallback。
- workflow pitfall path 与仓库现实不完全一致（`AIOS/docs/pitfalls/` 缺失）。
  - 缓解：本轮将 `AIOS/MEMORY.md`、`docs/runbooks/`、项目级 pitfalls 作为有效 briefing 来源并在文档中显式记录。

## ⚠️ Pitfall Briefing

### Matched Pitfalls (2 items)
| # | Pitfall | Relevance | Prevention |
|---|---------|-----------|------------|
| 1 | Contaminated snapshot / heavy voice-assistant merge risk (`AIOS/MEMORY.md`, 2026-03-16) | 本轮直接触碰历史上“职责过重”的语音链路核心文件 | 保持窄 shim 和增量边界，不做一次性大迁移 |
| 2 | Workflow path drift after TM-40 (`AIOS/MEMORY.md`, 2026-03-24) | 当前 workflow 文档引用的 `AIOS/docs/pitfalls/` 在仓库中缺失 | 以项目记忆和现存 runbook 为准，并在归档文档中明确这一现实差异 |

### Applicable Runbooks
- [ ] `AIOS/docs/runbooks/build_flash_debug.md` — 在编译校验与后续人工联调阶段使用
- [ ] `AIOS/docs/runbooks/environment_setup.md` — 若本地构建或工具链环境异常时回查

### Key Decisions to Respect
- TM owner / author 按 `weizongquan` 处理；当前执行环境按 `PinzhenHe` 路径归档。
- `voice_cloud_*` 保留窄兼容 facade，不承诺 LSChat 生产运行兼容。
- 连续对话仅表示云端 / session 行为；本地 wakeup suppression 不纳入 TM01。
- 机器人动作验证以软件事件 + shell/UI 触发 + 回调/日志为完成标准。
- LVGL9 仅做配置位和最小 skeleton，不做全量迁移。
- TM01 验收门槛为“可编译 + 路由通 + 日志/Hook/UI wiring 就绪”，真实云端/真设备闭环留到人工验证。

## Execution Order
1. 归档冻结规格与实施计划。
2. 扩展 `app_datas` / `config_parser` / `voice_msg`，先把 provider/debug/runtime 元数据落下来。
3. 在 `voice_cloud_*` facade 中接入 provider 选择，并新增 AIOS stub provider。
4. 为 MCP 加 transport boundary，并在 cloud facade 中注册发送回调。
5. 为 wakeup 输出流增加 sink boundary，并替换直接上云调用。
6. 增加 shell 调试入口，先完成 provider/status/robot/PAD/volume 的 CLI 联调面。
7. 增加 UI debug 页面与 model glue，接通 TM01 关键状态和触发按钮。
8. 更新架构文档与 API registry。
9. 进行本地编译/静态校验，整理哪些能力已本地验证、哪些仍待真实云端/设备环境。
