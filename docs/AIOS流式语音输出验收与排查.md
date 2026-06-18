# AIOS流式语音输出验收与排查

## 目标

把设备对话链路彻底收敛到 AIOS 协议与 AIOS websocket，并验证流式语音输出满足以下要求：

1. 唤醒后可以稳定进入 AIOS websocket 对话链路
2. TTS 播放期间不会自唤醒、不会自打断
3. 同一轮回复中，多段 TTS 可以连续播放，不会出现上一句没播完就跳下一句
4. 播报结束后，设备能回到可再次唤醒状态

## 验收标准

### A. 链路标准

串口日志必须满足：

- 出现 `AiosAuth: Calling AIOS auth endpoint`
- 出现 `WS: Connecting to websocket server: wss://.../v2/chat`
- 不出现 `api.tenclass.net`
- 不出现 `mqtt.xiaozhi.me`

### B. 单轮流式播报标准

对设备说一句完整问题，例如“今天天气怎么样”，期望：

- 出现 `Received event message: asr.text.completed`
- 出现 `Received event message: llm.text.delta`
- 出现 `Received event message: tts.audio.start`
- 播放期间不出现新的 `Wake word detected`
- 播放期间不出现异常 `turn.interrupt`
- 出现 `Received event message: tts.audio.completed`
- 出现 `Received event message: conversation.completed`
- 最后出现 `AIOS playback drained after stream end`

### C. 连续对话标准

执行两轮连续测试：

1. 唤醒 + 提问
2. 等待播报结束
3. 再次唤醒 + 提问

期望：

- 第二轮仍能唤醒
- 第二轮仍能正常播报
- 无需按 `BOOT`

## 重点排查项

### 1. 自唤醒/自打断

风险：

- 设备在 `Speaking` 状态下继续开启本地唤醒词检测
- 扬声器播放的 TTS 被本地唤醒引擎误判为唤醒词

对应策略：

- AIOS 播报期间关闭本地唤醒词检测

### 2. 多段 TTS 被错误收尾

风险：

- `tts.audio.completed` 或 `conversation.completed` 到达时，本地播放队列短暂为空
- 状态机过早切回 `idle`
- 后续同轮音频被丢弃、截断，造成“上一句没播完就跳下一句”

对应策略：

- 同轮后续 `tts.audio.start` 不重置 decoder
- 收尾时同时参考：
  - `tts.audio.completed`
  - `conversation.completed`
  - 最近一帧 TTS 二进制音频到达时间
  - 本地播放队列是否真正播空

### 3. 协议混用

风险：

- 设备仍发送旧协议 `abort/listen/tts` 控制信令
- AIOS websocket 只部分接管链路

对应策略：

- AIOS 模式下，停止当前轮次统一走 `conversation.cancel`
- 旧 `type=tts/stt/llm` 仅保留给非 AIOS 模式

## 建议日志关键字

抓串口时重点过滤：

- `AiosAuth`
- `Connecting to websocket server`
- `Wake word detected`
- `Received event message`
- `tts.audio.start`
- `tts.audio.completed`
- `conversation.completed`
- `turn.interrupt`
- `AIOS TTS audio received`
- `AIOS playback drained after stream end`

## 当前结论记录

- 当前工程确实存在“旧协议逻辑 + AIOS 协议逻辑”并存的情况
- 本次修复方向以“只保留 AIOS 对话链路的运行时语义”为准
- 所有完成声明必须以最新编译、烧录、串口证据为准
