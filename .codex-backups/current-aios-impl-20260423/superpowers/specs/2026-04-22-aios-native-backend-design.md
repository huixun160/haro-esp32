# AIOS 原生后端集成设计

- 版本：`v1.0`
- 日期：`2026-04-22`
- 状态：`Draft`

## 1. 目标

将当前项目改造成适配 AIOS 现成后端的设备侧实现，并尽可能复用现有代码库中的音频、板级、UI、状态机和电源管理能力。

本设计采用 `AIOS 原生主导方案`：

- 外部接入协议以 AIOS 文档为准
- 设备侧围绕 AIOS 生命周期组织
- 现有仓库中与本地硬件强相关的能力尽量复用
- 旧的 websocket/mqtt 会话语义不再作为主模型继续扩展

## 2. 设计原则

- 优先复用本地能力层，不复用旧协议语义
- HTTP 接入、WebSocket 会话、AIOS 事件解释分层实现
- 先建立最小闭环，再逐步补齐中断、动作、观测能力
- 所有新增 AIOS 模块集中放入 `main/aios/`

## 3. 复用与替换边界

优先复用：

- `AudioService`
- `DeviceStateMachine`
- `boards/*`
- 显示、LED、电源管理、网络接口抽象
- `Settings`
- `SystemInfo`

优先替换或收缩：

- `Application` 中旧协议解释逻辑
- `Protocol` 相关旧的 listen/tts/mcp 驱动语义
- 现有 `WebsocketProtocol` 作为主会话协议的角色

## 4. 目标架构

### 4.1 AIOS HTTP 接入层

新增：

- `AiosCrypto`
- `AiosHttpClient`

职责：

- 设备注册、认证、同步
- AIOS 公钥初始化
- 请求加密、响应解密封装
- AIOS 凭据持久化

### 4.2 AIOS WebSocket 会话层

新增：

- `AiosWsClient`

职责：

- WebSocket 建连
- 设置 AIOS headers
- 收发文本帧和二进制音频帧
- 心跳与 `session.connected`
- `device.profile.report`
- `up_stream.start/stop`

### 4.3 AIOS 会话编排层

新增：

- `AiosConversationManager`

职责：

- 处理 `conversation.started`
- 处理 `asr.text.completed`
- 处理下行 TTS
- 处理 `turn.interrupt`
- 处理 `conversation.completed`
- 与 `AudioService`、UI、状态机联动

### 4.4 AIOS 动作执行层

新增：

- `AiosActionExecutor`

职责：

- 处理 `tool.execute.request`
- 统一映射到设备内部动作能力
- 保持工具串行执行语义

## 5. 设备状态映射

保留现有主状态，不额外膨胀：

- `starting`
- `activating`
- `idle`
- `listening`
- `speaking`
- `upgrading`

状态映射：

- AIOS HTTP/WS 建立阶段：`activating`
- 可待机：`idle`
- 上行语音：`listening`
- 下行 TTS：`speaking`
- 打断后根据场景回到 `listening` 或 `idle`

## 6. 核心消息流

### 6.1 启动

1. 上电后初始化板级能力和 `AudioService`
2. 执行 AIOS HTTP bootstrap
3. 鉴权成功后建立 WebSocket
4. 收到 `session.connected`
5. 发送 `device.profile.report`

### 6.2 一轮语音

1. 用户触发唤醒/按键
2. 设备进入 `listening`
3. 发送 `up_stream.start`
4. 发送上行音频 binary
5. 发送 `up_stream.stop`
6. 接收 `asr.text.completed`
7. 接收 TTS 音频或相关事件
8. 播放完成后回到 `idle`

### 6.3 打断

收到 `turn.interrupt` 后：

- 立即停止 TTS
- 清空待播缓冲
- 根据当前交互场景切换到 `listening` 或 `idle`

### 6.4 动作执行

收到 `tool.execute.request` 后：

- 进入动作执行层
- 串行执行
- 返回 `tool.execute.completed` 或 `tool.execute.failed`

## 7. 观测与状态记录

新增运行时观测骨架：

- `AiosRuntimeMetrics`
- `AiosEventJournal`

观测目标：

- heap 与最小 heap
- websocket / session connected 状态
- 音频队列深度
- 当前设备状态
- 关键 AIOS 事件时间线

## 8. 实施顺序

1. 增加 AIOS build surface
2. 增加事件常量、凭据与观测骨架
3. 实现 AIOS HTTP bootstrap
4. 实现 AIOS WebSocket bring-up
5. 实现 AIOS conversation manager
6. 实现 tool.execute 动作执行
7. 补充 live smoke、监控与串口观测

## 9. 风险

- `Application` 当前职责过重，迁移阶段容易临时耦合
- Task 早期会出现“构建故意失败到下一个缺失模块”的过渡状态
- AIOS crypto/http/ws/conversation 四层不能同时大改，必须逐层推进
- 若直接把 AIOS 事件散落到板级代码，后续维护成本会迅速升高

## 10. 验收标准

- 在 `ESP-IDF 5.5.4` 下能稳定编译
- 能完成 AIOS HTTP bootstrap
- 能连上 AIOS websocket 并收到 `session.connected`
- 能发送 `device.profile.report`
- 能完成最小上行音频闭环
- 能观测关键运行状态与错误
