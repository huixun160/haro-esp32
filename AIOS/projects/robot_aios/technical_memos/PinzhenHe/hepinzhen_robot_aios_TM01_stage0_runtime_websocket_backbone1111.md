# Technical Memo

**Title:** Robot AIOS Stage0-01 底座链路实现：NuttX / EventBus / websocket / AI runtime

**Project:** robot_aios

**Subsystem:** System Integration / Runtime / EventBus / Cloud Adapter

**Author:** hepinzhen

**Priority:** HIGH

**Date:** 2026-04-15

---

## Background

白板架构的第一层顺序是：`EventBus + NuttX` 作为底座，之上先打通 `websocket + AI runtime`。这一步不是做业务页面，而是先建立整个机器人系统的主干链路。后续的控制、UI、Mic、Speaker、Camera 都必须挂到这条主链路上，不能各自直接调用旧的 `voice_cloud_*` 或自建消息总线。

当前仓库已经有可复用基础：

- 现有系统事件总线使用 `src/framework/voice_msg.h`
- 平台联网后连云逻辑位于 `src/category/comm/msgs/voice_platform.c`
- 旧云链路接口位于 `src/server/lschat_server/voice_cloud.h` / `src/server/lschat_server/voice_cloud.c`
- 上层 UI 已经订阅 `VOICE_MSG_CLOUD_*` 事件，见 `apps-ui/apps/llm/models/model_voice.c`

本任务说明书的目的，是让大模型先完成 Stage0 的主干代码，让后续任务都能基于统一 runtime 接口开发。

## Objective

完成一套可运行的 Stage0 runtime 主干，满足以下硬性目标：

1. 保留 `voice_msg` 作为当前阶段唯一 EventBus，不新建第二套消息总线
2. 将“联网后建立 websocket 会话”的入口从直接调用 `voice_cloud_connect()` 改为调用新的 AI runtime facade
3. 新 AI runtime 对外发布的状态事件仍然复用 `VOICE_MSG_CLOUD_*`，保证现有 `model_voice.c` 不需要大改即可继续工作
4. 为后续 Mic/Speaker/Camera/Control 提供统一的 session API、audio uplink API、image request API
5. 第一阶段允许内部先复用旧 `voice_cloud.c` 能力作为 provider，但业务层不得再直接依赖 `voice_cloud_*`

## Current State

当前代码存在以下耦合点，需要被本任务收敛：

1. `src/category/comm/msgs/voice_platform.c`
   - 在 `voice_system_network_probe_success()` 中直接构造 `voice_cloud_connect_config`
   - 直接调用 `voice_cloud_connect()`

2. `src/category/comm/msgs/voice_wakeup_msg.c`
   - 直接调用 `voice_cloud_chat_start()`
   - 直接调用 `voice_cloud_audio_recognition_start()` / `voice_cloud_audio_recognition_stop()`

3. `apps-ui/apps/llm/models/model_voice.c`
   - 已经稳定依赖 `VOICE_MSG_CLOUD_CONNECTED`
   - 已经稳定依赖 `VOICE_MSG_CLOUD_SESSION_STARTING`
   - 已经稳定依赖 `VOICE_MSG_CLOUD_IAT_*` / `VOICE_MSG_CLOUD_TTS_*`

4. `src/category/comm/app_datas.c/.h`
   - 已经维护 `pid/sid/did/host/token_url/port/scheme/full_duplex/...`
   - 可继续作为 Stage0 runtime 配置源

## Scope

本任务只做主干，不做 UI 页面和具体设备能力。必须按下面顺序实现：

### A. 新建 runtime facade

新增目录：

- `src/server/aios_runtime/`

至少创建以下文件：

- `src/server/aios_runtime/ai_runtime.h`
- `src/server/aios_runtime/ai_runtime.c`
- `src/server/aios_runtime/ai_runtime_provider.h`
- `src/server/aios_runtime/ai_runtime_provider_lschat.c`
- `src/server/aios_runtime/CMakeLists.txt`

接口要求：

- `int ai_runtime_connect(const struct ai_runtime_connect_config *cfg);`
- `int ai_runtime_session_start(const struct ai_runtime_session_config *cfg);`
- `int ai_runtime_session_stop(void);`
- `int ai_runtime_send_audio(const uint8_t *data, uint32_t len);`
- `int ai_runtime_image_recognize(const uint8_t *jpeg, uint32_t len);`
- `int ai_runtime_is_connected(void);`

说明：

- `ai_runtime_provider_lschat.c` 内部可以暂时转调旧 `voice_cloud_*`
- 但 `voice_platform.c`、`voice_wakeup_msg.c`、后续新模块都只能依赖 `ai_runtime.h`

### B. 兼容当前 UI 事件模型

要求新 runtime 在 provider 层继续发布现有 `VOICE_MSG_CLOUD_*` 事件：

- `VOICE_MSG_CLOUD_CONNECTING`
- `VOICE_MSG_CLOUD_CONNECTED`
- `VOICE_MSG_CLOUD_DISCONNECTED`
- `VOICE_MSG_CLOUD_SESSION_STARTING`
- `VOICE_MSG_CLOUD_SESSION_FINISHED`
- `VOICE_MSG_CLOUD_IAT_*`
- `VOICE_MSG_CLOUD_TTS_*`

约束：

- 不允许为了“架构更干净”而把 `model_voice.c` 整体推倒重来
- Stage0 先保证上层能继续收到稳定事件

### C. 替换平台联网入口

修改：

- `src/category/comm/msgs/voice_platform.c`

改造要求：

- 保留原有 `app_datas` 读取逻辑
- 不再直接 include `voice_cloud.h`
- 改为 include `ai_runtime.h`
- 在网络就绪时调用 `ai_runtime_connect()`

### D. 为后续任务预留统一入口

在 `ai_runtime.h` 中预留后续任务会用到的能力：

- 会话开始/结束
- 音频上行
- 图像识别
- 可选的工具调用入口占位

本任务不要求工具调用完整闭环，但头文件中要预留清晰扩展位。

### E. 编译接入

修改构建文件，使 `src/server/aios_runtime/` 被编译：

- `src/server/CMakeLists.txt` 或当前 server 聚合 CMake
- 需要时补充 `Kconfig`

## Out of Scope

以下内容本任务不做：

- 不做新的 UI 页面
- 不做 Mic 实际采音转发
- 不做 Speaker 播放控制
- 不做 Camera/CV 识别实现
- 不做机器人控制逻辑
- 不要求移除旧 `voice_cloud.c`

## Constraints

1. `voice_msg` 是 Stage0 唯一 EventBus，不能再造新的 event framework
2. 上层 UI 事件语义必须保持基本兼容
3. `voice_platform.c` 和后续业务入口不能再直接依赖 `voice_cloud.h`
4. 所有新对外 API 命名统一使用 `ai_runtime_*`
5. 如果新增公共头文件或公共接口，需要同步登记到 `AIOS/registry/apis/` 对应注册表

## Expected Deliverables

1. 新增 `src/server/aios_runtime/` 目录及 facade/provider 代码骨架
2. `voice_platform.c` 改为通过 `ai_runtime_connect()` 建立主链路
3. provider 层继续发布 `VOICE_MSG_CLOUD_*` 事件，保证 `model_voice.c` 兼容
4. runtime 头文件中定义稳定的 session/audio/image API
5. CMake/Kconfig 完成编译接入

## Verification Method

- [ ] Build verification: `cmake --build /home/shiro/project-haro/build --parallel 8` 成功，无新链接错误
- [ ] Runtime verification: 网络探测成功后日志显示进入 `ai_runtime_connect()`，而不是直接调用 `voice_cloud_connect()`
- [ ] Event verification: UI 仍能收到 `VOICE_MSG_CLOUD_CONNECTED`、`VOICE_MSG_CLOUD_SESSION_STARTING` 等事件
- [ ] Dependency verification: `voice_platform.c` 中不再 include `voice_cloud.h`
- [ ] Log verification: 日志中至少出现 `ai_runtime connect`, `provider selected`, `cloud connected`

## Potential Risks

- 若 facade 只做简单转发却不收敛依赖，后续模块仍会继续直接 include `voice_cloud.h`
- 若擅自改动 `VOICE_MSG_CLOUD_*` 语义，UI 会出现隐性回归
- 若 provider 抽象设计过重，Stage0 会被架构工作拖慢

## References

- `AIOS/workflow/templates/technical_memo_template.md`
- `src/framework/voice_msg.h`
- `src/category/comm/msgs/voice_platform.c`
- `src/server/lschat_server/voice_cloud.h`
- `src/server/lschat_server/voice_cloud.c`
- `apps-ui/apps/llm/models/model_voice.c`
- `src/category/comm/app_datas.h`
