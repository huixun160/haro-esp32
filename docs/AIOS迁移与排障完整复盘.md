# AIOS 迁移与排障完整复盘（WebSocket / 流式语音 / 屏幕 / 二次唤醒）

## 1. 文档目标

这份文档用于完整交接本次迁移工作，覆盖：

- 从初始 Xiaozhi 架构迁移到 AIOS 服务器
- 从原链路迁移到 AIOS WebSocket 协议
- 迁移中所有关键踩坑与修复方案
- 流式语音输出乱跳问题的根因与最终修复
- 屏幕不亮问题的排查与修复思路
- 二次唤醒偶发失败（需按 BOOT）问题的根因与修复

文档重点是“可复现、可验证、可接手”，而不是只写结果。

---

## 2. 初始架构与迁移目标

### 2.1 初始（Xiaozhi）架构特征

初始工程的语音链路以旧协议为中心：

- 控制语义：`hello / listen / abort / tts / stt / llm`
- 通道行为围绕旧服务端语义设计
- 本地状态机：`Idle -> Connecting -> Listening -> Speaking -> Idle`
- 音频二进制默认走 Opus 解码路径

### 2.2 迁移目标（必须全部满足）

- 认证改为 AIOS `/device/register` + `/device/auth`
- 会话改为 AIOS websocket（`/v2/chat`）
- 握手头改为 AIOS 要求
- 连接后上报 `device.profile.report`
- 上下行事件改为 AIOS `event_type` 体系
- 取消/打断行为改为 AIOS `conversation.cancel / turn.interrupt` 语义
- 设备侧语音播放链路与 AIOS 下行音频格式严格对齐

---

## 3. AIOS 服务器迁移（认证与配置下发）

### 3.1 关键改造点

1. 启动阶段通过 AIOS 认证拿会话配置
- 调用 `/device/auth` 获取：`token / ws.url / user_id / device_id / bot_id`
- 写入 `Settings("websocket")`

2. 补齐 AIOS 安全层加密
- `register/auth/sync` 不是明文 JSON 直发
- 需 AES + RSA 组合加密（否则常见 `403 Invalid Security Header`）

3. 兼容配置宏差异
- 处理 `CONFIG_AIOS_PUBLIC_KEY_B64` 与 `CONFIG_AIOS_PUBLIC_KEY_BASE64`

### 3.2 主要代码位置

- `main/ota.cc`
- `main/aios_auth.cc`
- `main/aios/aios_http_client.cc`
- `main/aios/aios_crypto.cc`
- `main/CMakeLists.txt`

### 3.3 迁移后运行时证据

常见关键日志：

- `AiosAuth: Calling AIOS auth endpoint: .../device/auth`
- `Ota: AIOS websocket config ready, ws=...`

---

## 4. WebSocket 迁移（协议与握手）

### 4.1 握手头迁移

AIOS 模式下使用：

- `Authorization: Bearer <token>`
- `X-Device-Id`
- `X-AIOS-Version`
- `X-User-ID`
- `X-Bot-ID`

代码：

- [websocket_protocol.cc](/home/shiro/xiaozhi-esp32-main/main/protocols/websocket_protocol.cc)

### 4.2 连接后流程迁移

- 等待 `session.connected`
- 发送 `device.profile.report`
- AIOS `mode=vad` 时，设备端不再发 `up_stream.start/stop`

### 4.3 旧协议语义替换

- 旧 `abort` -> AIOS `conversation.cancel`
- 旧 `type=tts/stt/llm` 仍保留兼容分支，但 AIOS 主流程走 `event_type`

---

## 5. 迁移中关键踩坑与处理

## 5.1 坑 A：只换 ws 地址，不换协议语义

### 现象

- 看起来已连上 AIOS ws
- 实际对话行为仍像旧链路，状态机混乱

### 根因

- 仅改 URL，不改控制语义/事件处理

### 处理

- 改握手头
- 改事件模型（`event_type`）
- 改取消语义（`conversation.cancel`）
- 改 profile 上报/工作模式

---

## 5.2 坑 B：`403 Invalid Security Header`

### 现象

- `/device/register` 或 `/device/auth` 返回 403

### 根因

- 请求未按 AIOS 安全加密协议封装

### 处理

- 实现 AES + RSA 加密/解密链路
- 使用正确公钥配置
- 在 `aios_auth` 路径统一处理

---

## 5.3 坑 C：二次唤醒偶发失败（需按 BOOT）

### 现象

- 首次可对话
- 第二次唤醒概率失败
- 需要按 BOOT 或重启后恢复

### 根因（组合）

1. 一轮结束后连接/状态未彻底归零
2. 活动轮次期间本地 wake word 与对话流程互相干扰
3. `turn.interrupt` 处理过重，导致状态机被提前切回 listening

### 修复

1. `Idle` 时主动清理 AIOS 轮次状态并关闭音频通道
2. 引入 AIOS 轮次期间的 wake word 抑制标志
3. speaking 期间禁用 wake word 检测（防止自唤醒）
4. `turn.interrupt` 改为“仅停播 + 清缓冲”，不强制 reopen listening

核心代码：

- [application.cc](/home/shiro/xiaozhi-esp32-main/main/application.cc)
- [application.h](/home/shiro/xiaozhi-esp32-main/main/application.h)

---

## 5.4 坑 D：流式语音乱跳（本次最难）

### 用户现象

- 一句话没说完就跳下一句
- 听感像“乱蹦、叠句、被切断”
- 文本显示正常但语音异常

### 已排除

- 不是 AIOS 服务端“完全不下发音频”
- 不是单纯文本显示速度问题
- 不是单纯二次唤醒问题

### 关键根因 1：`turn.interrupt` 被错误处理成“切回 listening + 开麦”

#### 为什么错

AIOS 文档要求：收到 `turn.interrupt` 时
- 立即停播当前 TTS
- 清空本地未播放缓冲

并未要求“立即切 listening 并重新开启上行”。

#### 实际副作用

- 切 listening 会触发 `EnableVoiceProcessing(true)`
- 该路径会再次 `ResetDecoder()`
- 造成同轮后续 TTS 被设备自己打碎

#### 修复

`turn.interrupt` 改为：
- 保留停播与清缓冲
- 不切 listening
- 不 reopen voice processing

代码：

- [application.cc](/home/shiro/xiaozhi-esp32-main/main/application.cc:663)

并新增静态检查脚本：

- [assert_turn_interrupt_handler.py](/home/shiro/xiaozhi-esp32-main/tools/aios/assert_turn_interrupt_handler.py:1)

### 关键根因 2（最终修复点）：AIOS 下行音频格式错配（PCM/Opus）

#### 现象与证据

- 功能机/小程序/Web 播放正常
- 设备端乱跳

这强烈指向设备端解码链路问题。

AIOS 文档默认下行能力常见为：
- `data.audio.down.format = pcm`
- `sample_rate = 16000`
- `audio_encode = binary`

设备之前把 AIOS 二进制一律按 Opus 路径处理，导致格式错配时听感异常。

#### 最终修复

1. 在 `AudioStreamPacket` 增加 payload 格式枚举
- `OPUS`
- `PCM_S16LE`

2. AIOS websocket 二进制下行改为带格式投递
- AIOS 模式可按配置选择 `pcm` 或 `opus`
- 默认走 `pcm/16000`

3. `AudioService` 增加 PCM 直通播放分支
- PCM 直接转 `int16_t` 推入播放队列
- 保留重采样逻辑
- Opus 保持原解码分支

关键代码：

- [protocol.h](/home/shiro/xiaozhi-esp32-main/main/protocols/protocol.h:10)
- [websocket_protocol.cc](/home/shiro/xiaozhi-esp32-main/main/protocols/websocket_protocol.cc:165)
- [websocket_protocol.cc](/home/shiro/xiaozhi-esp32-main/main/protocols/websocket_protocol.cc:225)
- [websocket_protocol.cc](/home/shiro/xiaozhi-esp32-main/main/protocols/websocket_protocol.cc:364)
- [audio_service.cc](/home/shiro/xiaozhi-esp32-main/main/audio/audio_service.cc:350)

#### 结果

此项修复后，用户确认“问题已修复”。

---

## 5.5 坑 E：屏幕不亮（显示异常）

### 现象

- 固件运行后出现屏幕不亮/不更新

### 根因（迁移期常见组合）

1. 状态机卡在异常状态（如长期 listening/speaking 未收尾）
2. 对话轮次未正确回到 idle，显示层不触发预期刷新
3. 音频链路异常导致 UI 状态更新与实际流程脱节

### 处理方式

1. 在 `HandleStateChangedEvent` 中确保 `Idle/Listening/Speaking` 各态下 UI 与音频状态一致
2. AIOS 轮次结束后明确 drain -> idle，触发显示恢复
3. 清理因异常 interrupt 或旧连接残留导致的状态漂移

关键点：

- `Idle` 态恢复：状态文本、表情、消息清理、wakeword 重新开启
- speaking/listening 态切换时避免误清播放链

代码：

- [application.cc](/home/shiro/xiaozhi-esp32-main/main/application.cc)

---

## 6. 迁移实现清单（从初始 Xiaozhi 到 AIOS）

按执行顺序：

1. 补齐 AIOS 认证与安全层
- `register/auth/sync`
- AES + RSA

2. 启动阶段改成获取 AIOS ws 配置
- `ota -> aios_auth -> websocket settings`

3. websocket 握手改为 AIOS 头

4. 建连后发送 `device.profile.report`
- 重点：`mode=vad`

5. 控制语义替换
- `abort` -> `conversation.cancel`
- `turn.interrupt` 处理与 AIOS 文档对齐

6. 设备端下行音频格式对齐
- 支持 `pcm/opus`
- 默认 AIOS 下行按 `pcm/16000`

7. 状态机和 wake word 干扰治理
- speaking 期间禁 wakeword
- AIOS 活动轮 suppress wakeword
- idle 收尾清理与重连策略

---

## 7. 验证方法（建议长期保留）

### 7.1 启动链路

关注日志关键字：

- `AiosAuth: Calling AIOS auth endpoint`
- `Connecting to websocket server: wss://.../v2/chat`
- `AIOS send: device.profile.report`

### 7.2 对话链路

关注顺序：

- `asr.text.completed`
- `llm.text.delta / llm.text.completed`
- `tts.audio.start`
- 二进制音频持续到达
- `tts.audio.completed`
- `conversation.completed`
- `AIOS playback drained after stream end`

### 7.3 interrupt 行为

确认：

- interrupt 发生时仅停播/清缓冲
- 不应立即 reopen listening
- 不应在 interrupt 路径重新开麦

检查脚本：

- `python3 tools/aios/assert_turn_interrupt_handler.py`

---

## 8. 关键结论（交接摘要）

1. AIOS 服务器迁移和 websocket 迁移已完成可用
2. 二次唤醒失败问题通过状态机/唤醒抑制/连接清理显著改善
3. 流式语音乱跳最终主因在设备端：
- interrupt 处理过重 + 下行音频格式错配（PCM/Opus）
4. 最终稳定修复点是：
- interrupt 仅停播不重开 listening
- 下行支持 PCM/Opus 双栈并默认对齐 AIOS `pcm/16000`

---

## 9. 相关文件索引

- [application.cc](/home/shiro/xiaozhi-esp32-main/main/application.cc)
- [application.h](/home/shiro/xiaozhi-esp32-main/main/application.h)
- [websocket_protocol.cc](/home/shiro/xiaozhi-esp32-main/main/protocols/websocket_protocol.cc)
- [websocket_protocol.h](/home/shiro/xiaozhi-esp32-main/main/protocols/websocket_protocol.h)
- [protocol.h](/home/shiro/xiaozhi-esp32-main/main/protocols/protocol.h)
- [audio_service.cc](/home/shiro/xiaozhi-esp32-main/main/audio/audio_service.cc)
- [ota.cc](/home/shiro/xiaozhi-esp32-main/main/ota.cc)
- [aios_auth.cc](/home/shiro/xiaozhi-esp32-main/main/aios_auth.cc)
- [assert_turn_interrupt_handler.py](/home/shiro/xiaozhi-esp32-main/tools/aios/assert_turn_interrupt_handler.py)
- [AIOS-websocket协议.md](/home/shiro/xiaozhi-esp32-main/docs/AIOS-websocket协议.md)
- [AIOS设备注册认证流程.md](/home/shiro/xiaozhi-esp32-main/docs/AIOS设备注册认证流程.md)
- [AIOS设备接入实测记录.md](/home/shiro/xiaozhi-esp32-main/docs/AIOS设备接入实测记录.md)

