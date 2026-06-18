# Task 6 记录：下行事件、TTS 与打断

- 状态：`未开始`
- 对应任务：`Task 6: Implement Downstream AIOS Events, TTS Playback, and Interrupt`

## 当前目标

- 接入 `conversation.started`
- 接入 `asr.text.completed`
- 接入下行 TTS
- 接入 `turn.interrupt`
- 打通 `conversation.completed`

## 当前预期风险

- `turn.interrupt` 如果只停 UI 不清音频缓冲，会出现“表面打断、实际还在播”
- 下行 TTS 与现有 speaking/listening 状态切换容易冲突

## 待补记录

- 本任务做了什么
- 修改文件
- 验证结果
- 遇到的坑
- 下一阻塞点
