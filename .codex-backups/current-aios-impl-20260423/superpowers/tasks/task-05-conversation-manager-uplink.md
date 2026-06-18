# Task 5 记录：AIOS Conversation Manager Uplink

- 状态：`未开始`
- 对应任务：`Task 5: Implement AIOS Conversation Manager for Uplink Audio`

## 当前目标

- 新增 `AiosConversationManager`
- 接管上行音频发送窗口
- 让 `AudioService` 的上行发送逐步从旧 `Protocol` 迁移到 AIOS 会话管理器

## 当前预期风险

- 旧的 `Application` 和 `Protocol` 仍然强绑定 listen/tts 语义
- 如果直接把 AIOS 逻辑写进旧分支，状态机会变乱

## 待补记录

- 本任务做了什么
- 修改文件
- 验证结果
- 遇到的坑
- 下一阻塞点
