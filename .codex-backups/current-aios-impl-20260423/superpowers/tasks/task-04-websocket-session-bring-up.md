# Task 4 记录：AIOS WebSocket Session Bring-Up

- 状态：`进行中`
- 对应任务：`Task 4: Implement AIOS WebSocket Session Bring-Up`

## 当前目标

- 创建 `AiosWsClient`
- 接入 AIOS WebSocket header 和 `session.connected` 最小处理
- 在 `Application` 中完成 HTTP bootstrap 之后的 WS bring-up

## 计划实现形状

- `AiosWsClient` 独立持有 websocket 连接、凭据、运行时指标和事件日志
- `Application` 只负责持有客户端、初始化和调用 `Connect()`
- 不把这部分逻辑塞进旧的 `Protocol/WebsocketProtocol`

## 当前阻塞点

- 当前 build 失败点是：
  - `main/aios/aios_ws_client.cc` 缺失

## 已识别风险

- 计划文档原文写的是 Task 4 后整体 `build PASS`
- 但由于 Task 1 已经把 `aios_conversation_manager.cc`、`aios_action_executor.cc` 也提前注册到了 CMake
- 所以 Task 4 的真实目标应调整为：
  - 把失败点继续后移到下一批缺失模块

## 待补记录

- 完成实现后补：
  - 实际修改文件
  - 真实 build 结果
  - `session.connected` 处理和 `device.profile.report` 发送细节
  - 本任务踩坑
