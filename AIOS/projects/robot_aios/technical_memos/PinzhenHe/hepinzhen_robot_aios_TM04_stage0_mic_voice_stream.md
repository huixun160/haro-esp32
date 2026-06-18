# Technical Memo

**Title:** Robot AIOS Stage0-04 Mic 与语音流上行链路实现

**Project:** robot_aios

**Subsystem:** Audio Record / Wakeup / Runtime Audio Uplink

**Author:** hepinzhen

**Priority:** HIGH

**Date:** 2026-04-15

---

## Background

白板第 4 项是 `Mic + 语音流`。这一步的开发目标非常明确：把设备端采音、唤醒/按键触发、runtime 会话和音频上行串起来，形成一条真正工作的 mic uplink 链路。

当前仓库中已经有录音模块、唤醒消息、旧云会话入口，但这些部分还没有通过统一 runtime facade 收敛。

## Objective

完成 Stage0 mic uplink 主链路，满足以下目标：

1. 录音开始/停止由统一 runtime session 驱动
2. `voice_wakeup_msg.c` 不再直接调用 `voice_cloud_audio_recognition_start/stop`
3. `audio_record_listener_add()` 必须从当前空实现修复为真正可注册监听器
4. 当 session running 时，录音帧会通过 `ai_runtime_send_audio()` 上行
5. 增加 mic 状态日志和至少一个 shell 级调试入口

## Current State

当前与本任务直接相关的文件：

- 录音模块：`src/middleware/audio/audio_record.c`
- 唤醒事件：`src/category/comm/msgs/voice_wakeup_msg.c`
- 唤醒算法：`src/server/lschat_server/wakeup/app_wakeup.c`
- 旧云接口：`src/server/lschat_server/voice_cloud.h`

当前问题很具体：

1. `audio_record_listener_add()` 目前是空实现，监听器并未真正加入链表
2. `voice_wakeup_msg.c` 直接依赖 `voice_cloud_*`
3. 没有统一的 “session running -> send audio frame” 桥接模块

## Scope

本任务按以下顺序实现：

### A. 修复录音监听器机制

修改：

- `src/middleware/audio/audio_record.c`

要求：

- 恢复 `audio_record_listener_add()` 的真实实现
- 确保 listener add/remove 线程安全
- 防止重复注册同一个回调
- 在没有 listener 时允许录音线程继续运行但不崩溃

如果有对应头文件，也同步检查并补齐声明。

### B. 新建 runtime 音频桥接模块

新增文件：

- `src/server/aios_runtime/ai_runtime_audio_uplink.c`
- `src/server/aios_runtime/ai_runtime_audio_uplink.h`

职责：

- 订阅 session start / finish 事件
- 在 session 开始时调用 `audio_record_start()`
- 注册录音监听器
- 在收到 PCM 帧时调用 `ai_runtime_send_audio()`
- 在 session 结束时停止录音并取消监听

### C. 改造唤醒与按键入口

修改：

- `src/category/comm/msgs/voice_wakeup_msg.c`

改造要求：

- 不再 include `voice_cloud.h`
- 改为 include `ai_runtime.h`
- 关键词唤醒后调用 `ai_runtime_session_start()`
- 按键按下/抬起使用统一 session start/stop 入口

### D. 增加 mic 调试入口

在 `src/shell/cmd/` 下新增或扩展命令，建议：

- `shell_mic_debug.c`

要求支持：

- `mic start`
- `mic stop`
- `mic status`
- `mic oneshot <ms>`

说明：

- `mic oneshot` 只需要验证录音链路和日志，不要求保存文件

### E. 事件与日志

若当前 `voice_msg.h` 中缺少 mic/record 状态事件，可新增：

- `VOICE_MSG_RECORD_STARTING`
- `VOICE_MSG_RECORD_STARTED`
- `VOICE_MSG_RECORD_STOPPED`
- `VOICE_MSG_RECORD_ERROR`

要求：

- mic 链路关键状态必须能从日志中定位

## Out of Scope

以下内容本任务不做：

- 不做 AEC/VAD/降噪算法优化
- 不做音频文件落盘
- 不做复杂唤醒策略重构
- 不做完整 full duplex 策略优化

## Constraints

1. 录音链路必须复用现有 `audio_record.c`，不要另起一套录音服务
2. 唤醒和按键入口统一调用 runtime facade
3. 音频上行模块只做桥接，不在其中实现云协议逻辑
4. 所有状态流仍通过 `voice_msg`

## Expected Deliverables

1. `audio_record_listener_add()` 从空实现修复为可用实现
2. `ai_runtime_audio_uplink.*` 新增
3. `voice_wakeup_msg.c` 改用 `ai_runtime_*`
4. shell mic 调试命令
5. mic 链路关键状态日志与必要事件

## Verification Method

- [ ] Build verification: `cmake --build /home/shiro/project-haro/build --parallel 8` 成功
- [ ] Code verification: `audio_record_listener_add()` 不再为空实现
- [ ] Wakeup verification: `voice_wakeup_msg.c` 中不再 include `voice_cloud.h`
- [ ] Runtime verification: session start 后出现 `audio_record_start` 与 `ai_runtime_send_audio` 日志
- [ ] Shell verification: `mic start/stop/status` 有明确响应

## Potential Risks

- `audio_record.c` 原实现存在注释掉的链表逻辑，恢复时要注意锁和内存释放
- 若 session 生命周期管理不严，可能导致重复注册 listener 或停止不干净
- 若 mic 上行桥接直接写协议，会再次破坏 runtime 分层

## References

- `AIOS/workflow/templates/technical_memo_template.md`
- `src/middleware/audio/audio_record.c`
- `src/category/comm/msgs/voice_wakeup_msg.c`
- `src/server/lschat_server/wakeup/app_wakeup.c`
- `src/server/lschat_server/voice_cloud.h`
- `src/framework/voice_msg.h`
