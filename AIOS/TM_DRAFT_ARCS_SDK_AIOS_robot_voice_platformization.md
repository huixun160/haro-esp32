# Technical Memo

**Title:** ARCS SDK 智能机器人接入 AIOS 新语音链路与平台化服务架构改造

**Project:** [待登录后填写项目名，例如 robot_aios]

**Subsystem:** ARCS SDK / Voice Service / Cloud Adapter / UI / Debug / Robot Capability

**Author:** [待登录后填写工程师姓名]

**Priority:** HIGH

**Date:** 2026-04-14

---

## Background

当前仓库已基于 ARCS SDK 具备一套可运行的语音助手基础能力，但现有实现主要围绕 `LSChat` 云链路构建，服务、协议、唤醒、MCP、UI 状态和调试能力之间存在较强耦合，主要表现为：

- 云侧实现集中在 `src/server/lschat_server/voice_cloud.c`，同时承担连接、认证、会话、音频上云、MCP 转发、图像识别等职责
- 唤醒模块位于 `src/server/lschat_server/wakeup/`，直接依赖云链路发送音频
- MCP runtime 位于 `src/server/lschat_server/mcp/`，其 transport 与旧云链路耦合
- 上层 UI 与业务模型主要依赖 `voice_msg` 消息总线，但服务层尚未形成“多云实现可切换”的平台化抽象
- 当前 UI 以 LVGL8 为主，尚未为未来 LVGL9 升级预留清晰的独立切换路径
- 针对 AIOS/PAD 场景的链路调试、UI 调试、音量调试、机械/动作能力验证入口不足，不利于机器人类产品快速联调

本任务需要在不兼容旧链路 `LSChat` 的前提下，引入新的 AIOS 语音链路，并完成服务平台化改造，使智能机器人产品能够基于新协议继续演进。

## Objective

实现一套面向 ARCS SDK 智能机器人的 AIOS 新语音服务基础设施，满足以下目标：

1. 新增 AIOS 云语音链路，提供协议、鉴权、连接管理和会话基础设施
2. 上层语音服务继续通过统一服务接口工作，不再直接绑定旧 `LSChat`
3. 完成 MCP 解耦，使 MCP runtime 能复用于不同云链路，并便于后续设备工具能力扩展
4. 完成唤醒模块独立解耦，使唤醒能力可对接不同云服务
5. 服务层支持按配置切换不同云实现，架构更加平台化
6. 支持服务端断句和持续对话模式
7. 增加更多 UI 配置开关，并为后续从 LVGL8 升级到 LVGL9 预留独立切换路径
8. 增强 AIOS/PAD 场景调试能力，提供 UI 相关调试入口
9. 增加机械/动作相关能力验证入口，满足机器人场景联调需求
10. 增加音量调试手段，便于设备端快速验证播放链路与音量行为

## Current State

结合当前仓库，现状可概括如下：

### 1. 云语音链路

- 旧云语音接口头文件为 `src/server/lschat_server/voice_cloud.h`
- 旧实现集中在 `src/server/lschat_server/voice_cloud.c`
- `src/category/comm/msgs/voice_platform.c` 在网络可用后发起 `voice_cloud_connect()`
- `src/category/comm/msgs/voice_wakeup_msg.c` 在唤醒或按键事件后调用 `voice_cloud_chat_start()` / `voice_cloud_audio_recognition_start()`

### 2. 唤醒链路

- 唤醒算法主逻辑位于 `src/server/lschat_server/wakeup/app_wakeup.c`
- 目前唤醒输出音频直接通过 `voice_cloud_chat_send_audio()` 上送云端
- 唤醒调试能力已有基础，但范围偏窄，主要在 `app_wakeup_debug.c`

### 3. MCP 与工具能力

- MCP runtime 位于 `src/server/lschat_server/mcp/`
- 设备工具分散在 `src/server/lschat_server/mcp_tool_*.c` 与 `src/category/evb/mcp-tools/`
- MCP 异步响应仍通过云链路相关消息回传，缺少明确 transport 边界

### 4. UI 与模型层

- UI 主要位于 `apps-ui/apps/llm/`
- `model_voice.c` 通过 `voice_msg` 总线感知云连接、会话、TTS/IAT、二维码和待机文案等状态
- 设置页已具备基础设置、网络设置、唤醒设置等页面，但缺少独立“调试设置”或“平台能力设置”页面

### 5. 配置与状态

- 当前设备云配置主要由 `src/category/comm/app_datas.c/.h` 管理
- 现有字段偏向旧云链路参数，如 `pid/sid/host/token_url/...`
- 已存在 `src/middleware/config/config_parser.c/.h`，具备更通用的 `auth/websocket/wake_up/role/network` 解析基础，但尚未真正成为运行时主配置入口

## Scope

本任务包含以下内容：

### A. AIOS 云链路基础设施

- 定义并接入 AIOS 协议适配层
- 实现 AIOS 鉴权配置、连接参数、连接生命周期管理
- 实现 AIOS 会话基础设施，包括：
  - 会话启动
  - 音频上行
  - 服务端断句处理
  - 持续对话模式
  - 会话结束与异常收敛

### B. 平台化云服务抽象

- 在服务层引入统一 cloud service facade / provider abstraction
- 将原有上层对 `voice_cloud_*` 的依赖收敛为统一可替换实现
- 支持通过配置选择 AIOS 作为当前云实现
- 不再要求兼容旧 `LSChat` 运行路径，但允许保留少量编译期或迁移期骨架作为重构过渡

### C. MCP 解耦

- 将 MCP runtime 从单一云链路目录中解耦
- 明确 MCP runtime 与 MCP transport 的边界
- 保留现有工具注册方式或等价机制
- 让设备工具能力可被后续其他云链路复用

### D. 唤醒链路解耦

- 将唤醒输出上行从具体云实现中抽离
- 使唤醒模块仅依赖统一的 uplink sink / service interface
- 保持当前唤醒算法和基础行为不回退

### E. UI 与配置平台化

- 扩展配置项，支持：
  - 云实现选择
  - 服务端断句开关
  - 持续对话开关
  - UI 调试开关
  - PAD/AIOS 调试开关
  - 机器人动作验证开关
  - 音量调试开关
  - UI 版本预留（LVGL8 / LVGL9）
- 在 UI 中增加调试相关页面或入口
- 为 LVGL9 升级预留独立路径，不要求本任务内完成 LVGL9 迁移

### F. 调试与机器人验证能力

- 提供 shell 调试入口，至少覆盖：
  - AIOS/PAD 链路状态调试
  - UI 调试入口触发
  - 机器人动作/机械验证事件触发
  - 音量调试与音量状态观察
- 增加必要消息或服务接口，支持后续机械执行机构接入

## Out of Scope

以下内容不属于本任务：

- 兼容并维持旧 `LSChat` 生产可用链路
- 实现完整的真实 AIOS 云端协议细节之外的所有业务能力闭环
- 完成 LVGL9 全量迁移
- 实现机器人完整动作编排系统、运动控制算法或实际机械驱动闭环
- 新增复杂的视觉、多模态、地图导航或设备自治逻辑
- 云端服务端接口本身的定义与改造

## Constraints

1. 以当前 ARCS SDK 工程结构为基础改造，避免大面积破坏现有 `voice_msg` 上层语义
2. 上层 UI/Presenter/Model 尽量保持事件语义稳定，减少无关 UI 回归
3. 默认不兼容旧 `LSChat` 运行链路，但应尽量保留清晰迁移边界，避免形成更深层次耦合
4. 需兼顾嵌入式资源约束，避免引入明显过重的运行时依赖
5. 配置项应尽量通过现有 KV / app_datas / config parser 体系统一管理
6. 调试入口应面向设备端联调，优先保证“能看、能触发、能验证”
7. UI 仍以 LVGL8 运行，LVGL9 仅作为预留配置路径，不在本任务中切主运行时

## Expected Deliverables

1. 平台化云服务接口与 AIOS provider 实现骨架
2. AIOS 鉴权、连接管理、会话基础设施改造
3. 从旧链路中解耦出的 MCP runtime / transport 边界
4. 独立的唤醒 uplink/sink 边界，使唤醒模块不再直接绑定具体云实现
5. 配置扩展，支持云实现、断句、持续对话、UI 版本与调试开关
6. UI 新增调试设置入口和相关开关/动作入口
7. AIOS/PAD/UI/音量/机器人动作的设备端调试入口
8. 机器人动作验证消息或能力触发接口
9. 必要的 Kconfig/CMake/i18n 更新
10. 一份验证清单，说明哪些能力已本地验证、哪些仍依赖真实云端环境

## Verification Method

- [ ] Build verification:
  - 基于当前工程编译通过
  - 新增模块、头文件、Kconfig、CMake 无链接错误

- [ ] Service verification:
  - 网络就绪后能够进入新 cloud service provider 选择路径
  - `voice_platform.c` / `voice_wakeup_msg.c` 通过统一接口工作
  - AIOS provider 能输出关键连接/会话日志

- [ ] Wakeup verification:
  - 唤醒模块编译通过
  - 唤醒音频上行改为走独立 uplink sink
  - 唤醒不会再直接依赖某个具体云实现函数

- [ ] MCP verification:
  - MCP runtime 能正常初始化
  - MCP 请求与响应走独立 transport 消息路径
  - 现有设备工具至少有基础注册与调用能力

- [ ] Dialogue verification:
  - 配置中可开启/关闭服务端断句
  - 配置中可开启/关闭持续对话模式
  - 对应日志或状态可观察

- [ ] UI verification:
  - 设置页存在新增调试入口
  - 调试页中可见关键开关和验证按钮
  - UI 版本预留状态可配置和显示

- [ ] Debug verification:
  - shell 中至少有 AIOS/PAD/UI/音量/动作验证相关命令
  - 音量调试能读写当前音量，且日志可见
  - 机器人动作验证能发布事件或进入验证回调

- [ ] Log verification:
  - 关键日志建议包括：provider select、auth start/result、connect state、session start/finish、sentence segmentation mode、continuous mode、mcp request/response、wakeup uplink、robot action validate

## Potential Risks

- AIOS 协议细节尚未在当前仓库中落地，若缺少真实 SDK 或协议文档，第一阶段可能只能完成可扩展骨架与占位实现
- 旧 `voice_cloud.c` 职责过重，拆分过程中容易引入事件遗漏或状态回归
- MCP 从旧链路中抽离后，若 transport 边界定义不清，可能出现工具响应丢失
- 唤醒模块改为统一 sink 后，若线程或缓冲时序处理不当，可能影响实时性
- UI 新增调试入口后，需注意与现有 presenter/model 导航结构的兼容
- 若实际 AIOS/PAD 调试需求超出当前设备资源限制，后续可能需要再次裁剪入口粒度

## References

- `src/server/lschat_server/voice_cloud.h`
- `src/server/lschat_server/voice_cloud.c`
- `src/server/lschat_server/wakeup/app_wakeup.c`
- `src/server/lschat_server/mcp/mcp.h`
- `src/server/lschat_server/mcp/mcp.c`
- `src/category/comm/msgs/voice_platform.c`
- `src/category/comm/msgs/voice_wakeup_msg.c`
- `src/category/comm/app_datas.h`
- `src/category/comm/app_datas.c`
- `src/middleware/config/config_parser.h`
- `src/middleware/config/config_parser.c`
- `apps-ui/apps/llm/models/model_voice.c`
- `apps-ui/apps/llm/presenters/setting_presenter.c`
- `apps-ui/apps/llm/presenters/setting_wakeup_presenter.c`
- `apps-ui/apps/llm/views/setting_view.c`
- `apps-ui/apps/llm/views/setting/setting_wakeup_view.c`
- `AIOS/workflow/templates/technical_memo_template.md`

## Suggested Follow-up Clarifications For Workflow

建议在 `/aios-workflow` 澄清阶段优先确认以下问题：

1. AIOS 协议是否已有外部接口定义、消息格式、鉴权方式与会话事件清单
2. 本任务是否允许保留旧 `voice_cloud_*` 作为 facade 名称，仅替换底层 provider
3. 持续对话是否仅指云端 session 模式切换，还是还包含本地唤醒抑制/自动重入策略
4. 服务端断句的行为是否要映射到 UI 中间态显示
5. 机器人动作验证当前是否只要求软件事件触发，还是要接真实舵机/执行机构接口
6. LVGL9 预留路径是否只需要配置位，还是要同时规划目录和 presenter/view 分流骨架
