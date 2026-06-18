# Technical Memo

**Title:** Robot AIOS Stage0-05 Speaker 播放链路与音量控制实现

**Project:** robot_aios

**Subsystem:** Speaker / Player / Volume / TTS Playback

**Author:** hepinzhen

**Priority:** HIGH

**Date:** 2026-04-15

---

## Background

白板第 5 项是 `Speaker`。在整个架构顺序里，它位于 Mic 之后，说明 Stage0 的要求是：先能把语音流送上去，再把返回的 TTS/提示音从 Speaker 播出来，并且具备最基本的音量控制和调试能力。

当前仓库中已经有 player、tone、volume 和若干音频 MCP 工具，可直接复用，但还缺少统一的 speaker service 与 runtime 事件桥接。

## Objective

完成 Stage0 speaker 链路，满足以下目标：

1. 新建统一的 speaker facade，封装播放和音量控制
2. runtime 收到 TTS URL / TTS 文本结束等事件后，能驱动现有 player 播放
3. 保持 `VOICE_MSG_PLAYER_*` 事件可用
4. 增加 shell 音量调试命令
5. UI 和 MCP 后续都通过统一 speaker service 工作

## Current State

当前可复用文件：

- 音频播放：`src/middleware/player/audio_player.c`
- player 管理：`src/middleware/player/player_mgr.c`
- 音量接口：`src/middleware/player/listen_volume.h`
- 短音效：`src/middleware/player/short_player.c`
- 提示音：`src/middleware/tone/app_tone.c`
- 现有音量 MCP 工具：`src/server/lschat_server/mcp_tool_volume.c`

现状问题：

- 还没有统一 speaker service
- 事件到播放器之间的桥接关系不集中
- 音量调试入口分散

## Scope

本任务按以下顺序实现：

### A. 新建 speaker service

新增目录或文件：

- `src/server/speaker_service/speaker_service.h`
- `src/server/speaker_service/speaker_service.c`
- `src/server/speaker_service/CMakeLists.txt`

接口至少包含：

- `int speaker_service_play_tts_url(const char *url);`
- `int speaker_service_play_prompt(const char *id_or_path);`
- `int speaker_service_stop(void);`
- `int speaker_service_set_volume(int vol);`
- `int speaker_service_get_volume(void);`
- `int speaker_service_mute(int mute);`

要求：

- service 内部复用现有 `player` / `listen_volume`
- 上层不再直接调用 `listen_set_volume()` 或零散 player API

### B. 新建 runtime 到 speaker 的桥接

新增文件：

- `src/server/aios_runtime/ai_runtime_speaker_bridge.c`
- `src/server/aios_runtime/ai_runtime_speaker_bridge.h`

职责：

- 订阅 `VOICE_MSG_CLOUD_TTS_URL`
- 需要时订阅其他 runtime/speaker 相关事件
- 收到 TTS URL 后调用 `speaker_service_play_tts_url()`
- 播放状态变化时继续发布 `VOICE_MSG_PLAYER_*`

### C. 增加 shell 调试入口

在 `src/shell/cmd/` 下新增：

- `shell_speaker_debug.c`

要求支持：

- `speaker vol get`
- `speaker vol set <0-100>`
- `speaker mute on`
- `speaker mute off`
- `speaker stop`

### D. 收敛现有音量工具

检查并修改：

- `src/server/lschat_server/mcp_tool_volume.c`

要求：

- 内部改为调用 `speaker_service_*`
- 不再直接散落调用底层 volume API

## Out of Scope

以下内容本任务不做：

- 不做音频解码器重构
- 不做复杂播单管理
- 不做音乐播放器产品功能
- 不做 TTS 合成服务本身

## Constraints

1. speaker service 只封装播放与音量，不实现云协议
2. shell/MCP/UI 后续统一走 speaker service
3. 播放状态继续复用 `VOICE_MSG_PLAYER_*`
4. 本任务优先打通 TTS/提示音最小闭环

## Expected Deliverables

1. `speaker_service.*`
2. `ai_runtime_speaker_bridge.*`
3. `shell_speaker_debug.c`
4. `mcp_tool_volume.c` 改为复用 speaker service
5. `VOICE_MSG_PLAYER_*` 状态链路可观察

## Verification Method

- [ ] Build verification: `cmake --build /home/shiro/project-haro/build --parallel 8` 成功
- [ ] Speaker verification: 收到 `VOICE_MSG_CLOUD_TTS_URL` 后触发实际播放逻辑
- [ ] Volume verification: `speaker vol get/set` 可用，音量变化生效
- [ ] Refactor verification: `mcp_tool_volume.c` 改为依赖 `speaker_service.h`
- [ ] Log verification: 日志至少包含 `speaker play`, `speaker stop`, `volume set`

## Potential Risks

- 若 service 只是包一层但上层仍直接调底层 API，后续无法真正收敛
- 若不继续发布 `VOICE_MSG_PLAYER_*`，现有 UI/状态机会断链
- 若音量范围与底层 API 语义不一致，容易出现 UI 显示和实际音量不一致

## References

- `AIOS/workflow/templates/technical_memo_template.md`
- `src/middleware/player/audio_player.c`
- `src/middleware/player/player_mgr.c`
- `src/middleware/player/listen_volume.h`
- `src/middleware/tone/app_tone.c`
- `src/server/lschat_server/mcp_tool_volume.c`
- `src/framework/voice_msg.h`
