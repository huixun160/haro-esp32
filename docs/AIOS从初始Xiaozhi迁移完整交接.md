# AIOS 从初始 Xiaozhi 工程迁移完整交接

## 文档目的

这份文档不是给“当前已经被改过多轮的仓库”看的，而是给下一个接手的 AI 或开发者看的：

- 如果手里拿的是**最初始的 xiaozhi 工程**，应该如何把它迁移到 **AIOS 的注册认证 + WebSocket 协议**
- 这次迁移过程中，哪些点是必须改的
- 哪些点是容易踩坑的
- 哪些问题已经基本解决
- 哪些问题仍然没有完全解决，尤其是**流式语音输出乱跳**的问题

这份文档尽量把“现象、代码改法、测试证据、失败尝试、剩余风险”全部写清楚，方便下一位接着做，而不是重复从零试错。

---

## 一、背景与目标

### 1. 原始工程的默认链路

最初始的 xiaozhi 工程，核心对话链路默认是围绕原来的 xiaozhi 服务设计的，典型特征包括：

- 启动时通过 OTA/激活接口获取配置
- 使用原有 websocket 或 mqtt 链路
- 协议控制语义是原项目自己的：
  - `hello`
  - `listen`
  - `abort`
  - `tts`
  - `stt`
  - `llm`
- 本地状态机是围绕这套旧语义写的：
  - `Idle -> Connecting -> Listening -> Speaking -> Idle`
- 唤醒词、本地音频处理、显示、播音，全都默认假设“服务端也是 xiaozhi 那套行为”

### 2. 迁移目标

目标不是“只把 ws 地址改掉”，而是**把整条语音对话链路迁移到 AIOS 协议**：

1. 设备端按 AIOS 要求完成注册/认证
2. 从 AIOS `/device/auth` 获取 token 和 websocket 地址
3. websocket 握手头改成 AIOS 要求
4. 连接后按 AIOS 协议发 `device.profile.report`
5. 音频上行、事件下行、取消会话、会话完成等语义全部按 AIOS 处理
6. 不再依赖原来 xiaozhi 服务器的对话协议假设

### 3. 这次迁移的用户真实诉求

用户不是要“兼容一部分 AIOS”，而是要：

- **彻底换成 AIOS 服务器**
- **彻底换成 AIOS websocket**
- 原 xiaozhi 的服务链路不要再继续影响当前对话
- 二次唤醒可用
- 语音回复是稳定的流式播放，不要一句没说完就乱跳

---

## 二、文档依据

这次迁移和排查主要参考以下文档：

- [AIOS设备接入实测记录.md](./AIOS设备接入实测记录.md)
- [AIOS设备注册认证流程.md](./AIOS设备注册认证流程.md)
- [AIOS-websocket协议.md](./AIOS-websocket协议.md)
- [AIOS服务通讯加密流程.md](./AIOS服务通讯加密流程.md)
- [AIOS流式语音输出验收与排查.md](./AIOS流式语音输出验收与排查.md)

---

## 三、如果从“最初始 xiaozhi 工程”开始，必须做的迁移项

这一节按“从干净原始工程迁移”的角度描述，而不是只描述当前仓库状态。

### 1. 补齐 AIOS 认证与加密模块

#### 为什么必须补

AIOS 的 `/device/register`、`/device/auth`、`/device/sync` 不是简单明文 JSON 接口。

如果直接像普通 REST 那样发 JSON，请求会直接被安全层拦掉，典型报错是：

```text
403 Invalid Security Header
```

这说明请求根本没进业务层，而是卡在 AIOS 的安全校验层。

#### 必须实现的能力

设备端要补齐以下能力：

1. Base64 编码/解码
2. 16 字节随机 AES key 生成
3. AES-ECB + PKCS7 对请求体加密
4. 用 AIOS 提供的 RSA 公钥加密 AES key
5. 在请求头中带上加密后的 key
6. 能解密 AIOS 返回的加密响应

#### 本次落点

本次实现最终放到了：

- `main/aios/aios_crypto.cc`
- `main/aios/aios_http_client.cc`
- `main/aios_auth.cc`

如果是从原始工程重新迁移，至少要保证这些源文件被编译进去。

#### 编译层踩坑

最初一个真实坑是：

- 代码里已经写了一部分 AIOS 逻辑
- 但 `main/CMakeLists.txt` 里没有把相关 `.cc` 全部加进去
- 结果是“表面上有 AIOS 代码，运行时却根本不完整”

本次确认需要在 `main/CMakeLists.txt` 里包含：

- `aios/aios_crypto.cc`
- `aios/aios_http_client.cc`
- `aios_auth.cc`

否则迁移一定不完整。

### 2. 在 OTA/启动阶段改为获取 AIOS websocket 配置

#### 原始工程的做法

原始工程通常是在激活/OTA 阶段拿到旧服务器配置，然后把 websocket 或 mqtt 配置写入本地 `Settings`。

#### 迁移后的正确做法

要改成：

1. 启动时调用 AIOS 认证逻辑
2. 从 `/device/auth` 获取：
   - `token`
   - `ws.url`
   - `user.id`
   - `profile_device.device_user_id`
   - `profile_device.config_agentic_id`（bot）
3. 把这些字段写入 `Settings("websocket", true)`
4. 把 `aios_mode` 标志也写进去

#### 本次实现位置

- `main/ota.cc`

关键动作包括：

- 初始化 `AiosAuthClient`
- 获取 `AiosWebsocketConfig`
- 写入：
  - `url`
  - `token`
  - `x-device-id`
  - `x-user-id`
  - `x-bot-id`
  - `x-aios-version`
  - `aios_mode=true`

这一步是整个迁移的入口。如果启动阶段还在读旧配置、旧 URL、旧 provider，那后面所有 websocket 改动都白搭。

### 3. 改 websocket 握手头为 AIOS 规范

#### 原始工程问题

原始 websocket 握手头主要服务于旧 xiaozhi 服务，不适用于 AIOS。

#### AIOS 迁移后必须设置的头

在 websocket 连接阶段，需要改为发送：

- `Authorization: Bearer <token>`
- `X-Device-Id`
- `X-AIOS-Version`
- `X-User-ID`
- `X-Bot-ID`

#### 本次实现位置

- `main/protocols/websocket_protocol.cc`

`OpenAudioChannel()` 里做了这些事情：

1. 从 `Settings("websocket")` 读取 `url/token/x-device-id/x-user-id/x-bot-id`
2. 自动补 `Bearer ` 前缀
3. 在 AIOS 模式下设置 AIOS 头
4. 仍保留旧头：
   - `Protocol-Version`
   - `Device-Id`
   - `Client-Id`

#### 这里的坑

这一步容易犯两个错：

1. **只改 URL，不改头**
- 这样会出现能连 TCP，但服务端协议层无法正常识别设备身份

2. **AIOS 头和旧头混用时，不知道谁生效**
- 当前实现里，AIOS 头会在 `aios_mode_` 下额外补充
- 旧头还在，是为了兼容非 AIOS 场景
- 但从长期看，最稳妥的做法是：**AIOS 模式下彻底隔离旧语义，不只是补头**

### 4. 建连后发送 `device.profile.report`

#### 为什么必须发

AIOS websocket 建连后，设备需要汇报自身能力和音频参数。

#### 本次实现

- `main/protocols/websocket_protocol.cc`
- 在 AIOS websocket 打开后，发送 `device.profile.report`

内容大致包括：

- `event_type = device.profile.report`
- `timestamp`
- `identity.product_id = BOARD_NAME`
- `identity.soft_ver = 3.0`
- `audio.up/down`
  - `format = opus`
  - `sample_rate`
  - `audio_encode = binary`
- `language.src/tgt`
- `mode = vad`

#### 为什么这里选 `mode=vad`

本次后期改成了 `vad`，原因是：

- 最初一版曾尝试保留本地 `up_stream.start/stop` 切段思路
- 实测中这会导致“说完了却没停录、服务端一直等、设备卡 listening”
- 后续改为依赖 AIOS 侧的 `vad` 模式，设备端持续上传音频，不再主动发 `up_stream.start/stop`

### 5. AIOS 模式下改掉旧控制语义

这是整个迁移里最容易被低估的一块。

用户最初的强烈不满，根本原因不是“地址没换对”，而是：

- 表面上换成 AIOS websocket 了
- 但设备运行时仍然保留很多旧 xiaozhi 协议语义
- 结果就是“换了一半”，状态机互相打架

#### 必须改的点 1：停止说话不能再发旧 `abort`

原始工程里，打断播报通常会发旧协议 `abort`。

AIOS 模式下，本次改为：

- `SendAbortSpeaking()` 发送 `conversation.cancel`

实现位置：

- `main/protocols/websocket_protocol.cc`
- `BuildAiosConversationCancel()`

#### 必须改的点 2：AIOS `vad` 模式下不要再发旧的 `up_stream.start/stop`

本次实现为：

- `SendStartListening()` 在 AIOS 模式下只记录统计，不发送 `up_stream.start`
- `SendStopListening()` 在 AIOS 模式下只打印统计，不发送 `up_stream.stop`

日志里会看到：

- `AIOS mode=vad, skip up_stream.start`
- `AIOS mode=vad, skip up_stream.stop`

这一步是为了把切段职责交给 AIOS，而不是本地继续用旧逻辑切。

---

## 四、从“初始 Xiaozhi”迁移时，实际需要改的主要文件

如果下一个 AI 是基于干净原始工程重新做，建议优先关注这些文件。

### 1. `main/CMakeLists.txt`

职责：

- 把 AIOS 所需源码真正编译进去

必须确认：

- `aios/aios_crypto.cc`
- `aios/aios_http_client.cc`
- `aios_auth.cc`
- `protocols/websocket_protocol.cc`
- `ota.cc`
- `application.cc`

### 2. `main/ota.cc`

职责：

- 在启动/检查版本阶段走 AIOS auth
- 获取 websocket 配置并写入 `Settings`

关键点：

- 不要只是继续沿用旧 OTA 返回的 websocket 配置
- 必须以 `/device/auth` 返回值为准

### 3. `main/aios_auth.cc`

职责：

- register/auth/sync
- AIOS 请求加密与响应解密
- 读取/持久化 AIOS 凭据

关键点：

- 兼容 `CONFIG_AIOS_PUBLIC_KEY_B64` 与 `CONFIG_AIOS_PUBLIC_KEY_BASE64`
- 认证失败时，能否自动 fallback 到 register 再 auth

### 4. `main/protocols/websocket_protocol.cc`

职责：

- websocket 握手头
- AIOS 模式识别
- `device.profile.report`
- `conversation.cancel`
- AIOS 文本事件/二进制音频链路桥接

关键点：

- AIOS 模式不能只改 header，必须改运行时语义
- `OpenAudioChannel()` 是 AIOS 握手核心入口

### 5. `main/application.cc`

职责：

- 本地状态机
- 唤醒 / listening / speaking 切换
- AIOS websocket 事件的真正消费逻辑
- TTS 播放收尾与二次唤醒控制

这是后面所有 bug 的中心文件。

### 6. `main/application.h`

职责：

- AIOS 状态变量新增位置

本次新增过的关键状态包括：

- `accept_incoming_tts_audio_`
- `tts_stream_finished_`
- `conversation_completed_`
- `upstream_audio_paused_`
- `suppress_aios_wake_word_until_idle_`
- `last_tts_event_us_`
- `last_tts_audio_us_`
- `aios_tts_packet_count_`
- `assistant_reply_text_`

---

## 五、AIOS 迁移过程中真实踩过的坑

这一节是最重要的经验部分。

### 坑 1：以为只要拿到 access_key/access_secret 就够了

一开始容易误以为：

- 既然文档里有 `access_key/access_secret`
- 那设备只要把它们填进配置，再去调 auth 就好了

但实际接入里，用户明确指出：

- 不能只盯着某个 access_key
- 文档里已经写了 register 流程
- 如果没有现成凭据，就应该走 `/device/register`

结论：

- AIOS 设备接入不能只停留在“静态填 key”
- 必须支持 register -> auth 这一整条链路

### 坑 2：`403 Invalid Security Header` 并不是业务层报错

这个错误非常关键。

第一次遇到时，如果没有认真看文档，很容易误判成：

- 参数错了
- header 少了某个字段
- token 错了

但实际上，这个错误说明：

- 请求还没进入 register/auth/sync 业务层
- 安全层就把请求拦了
- 根因通常是**没有按 AIOS 的加密协议组织请求**

结论：

- 看到这个错误，先查加密和公钥，不要先查业务 JSON

### 坑 3：宏名不统一导致 AIOS 逻辑看似存在，实际没启用

真实遇到的问题包括：

- `CONFIG_AIOS_PUBLIC_KEY_B64`
- `CONFIG_AIOS_PUBLIC_KEY_BASE64`

如果代码只认其中一个宏，另一套配置就会失效。

本次做了兼容处理。

此外还有一个坑：

- 某些 AIOS 路径用 `#if defined(CONFIG_AIOS_API_BASE_URL)` 包起来
- 如果构建配置不满足，代码会被直接裁掉

所以迁移时必须确认：

- AIOS 运行期开关到底是什么
- 不能出现“文档写了 AIOS，运行时却没编进去”的情况

### 坑 4：只换 websocket 地址，不换事件语义

这是前期最本质的错误之一。

表面现象是：

- 能连上 `wss://wapiaios.nextbigseek.com/v2/chat`
- 也能收到 `session.connected`
- 看起来像是已经接上 AIOS 了

但实际上如果设备端仍然：

- 按旧时机发 `listen`
- 按旧方式发 `abort`
- 按旧心智处理 `tts/stt/llm`
- 没把 AIOS 事件完整映射到本地状态机

那么它只是“接上了一个新 ws 地址”，而不是“真正迁到 AIOS 协议”。

这就是后来用户说“你只是改了一半”的根本原因。

### 坑 5：AIOS 模式下，本地仍然继续做旧式切段

前期一度保留了本地 `up_stream.start/stop` 逻辑。

结果是：

- 唤醒后能开始上传
- 但本地 VAD 不一定能稳定判断“说完了”
- `up_stream.stop` 发不出去
- 服务端持续等待更多语音
- 表现为设备一直卡在 listening

后续改法是：

- `device.profile.report` 用 `mode=vad`
- AIOS 模式下跳过 `up_stream.start/stop`
- 让 AIOS 侧接管切段

### 坑 6：同一轮里自己又被唤醒

这是二次唤醒和流式 TTS 混乱的重要来源。

风险链路是：

1. 设备进入 `Speaking`
2. 本地唤醒词检测还开着
3. 扬声器播放的 TTS 被 AFE 误判成唤醒词
4. 当前轮被本地再次打断
5. 状态机重新进 listening / connecting
6. 听感上就是“还没说完就乱跳、乱切、乱蹦”

这个问题和用户听到的现象高度一致。

### 坑 7：`turn.interrupt` 不能想当然地全收下

日志里多次出现：

- `Wake word detected ...`
- 很快收到 `turn.interrupt`
- 然后又持续收到大量 AIOS TTS 音频包
- 最后 `conversation.completed`

这说明：

- `turn.interrupt` 在 AIOS 里可能并不总是表示“现在必须把本地一切都清空”
- 它可能只是服务端在切前一个子轮次或内部阶段

如果本地一收到 `turn.interrupt` 就无脑：

- 清 decoder
- 清状态
- 切 listening

那流式 TTS 必然被搅乱。

本次后期做了一个保护：

- 只有当前本地**确实存在活动播放**时，才响应 `turn.interrupt`
- 否则忽略并打印：
  - `Ignoring AIOS turn.interrupt without active local playback`

---

## 六、二次唤醒问题：现象、原因、踩坑与已做处理

这一部分是用户明确要求总结的重点。

### 1. 用户看到的现象

用户最初反馈：

- 第一轮可以唤醒并对话
- 第二轮开始不稳定，甚至无法再次唤醒
- 有时必须按 `BOOT` 才能继续

### 2. 排查后确认的主要原因

#### 原因 A：上一轮 websocket 没有彻底收干净

如果一轮结束后旧 websocket 还挂着，第二轮继续复用旧连接，就容易出现：

- 状态机以为自己还能继续对话
- 实际服务端端侧已经认为轮次不同或连接状态异常
- 本地表现为“第二轮唤醒没反应”或“进了 listening 但不继续走”

#### 原因 B：活动轮次里本地唤醒词依然工作

如果 speaking/listening 阶段仍允许继续 wake word：

- 当前轮内部会被新的本地 wake 打断
- 二次唤醒逻辑和当前轮逻辑缠在一起
- 体验上会像“后面越来越乱，只能重启或按 BOOT”

#### 原因 C：`turn.interrupt` 打乱本地状态

如果服务端先发了一个 interrupt，而本地无脑切 listening/idle：

- 当前轮本地播放状态会丢失
- 下一轮的唤醒与播放边界也会被污染

### 3. 这次做过的修复

#### 修复 1：回到 idle 时主动关闭 AIOS 音频通道

在 `HandleStateChangedEvent()` 里，进入 `Idle` 时：

- 清 AIOS 当前轮相关状态
- 重新启用本地 wake word
- 如果当前是 AIOS 模式且 audio channel 开着，则 `CloseAudioChannel()`

目的：

- 让下一轮唤醒尽量基于新连接开始
- 避免复用陈旧 websocket

#### 修复 2：AIOS 活动轮次中屏蔽本地再次唤醒

增加了：

- `suppress_aios_wake_word_until_idle_`

行为是：

- 一旦 AIOS 模式从 `idle` 成功进入当前轮
- 就一直屏蔽新的本地 wake word
- 直到真正回到 `idle`

具体作用：

- 防止 speaking 时“自己听自己”
- 防止 listening/speaking 中再次误唤醒

#### 修复 3：AIOS speaking 期间关闭 wake word detection

在 speaking 阶段，不允许本地唤醒词继续工作。

这一步是解决“自唤醒”的关键。

### 4. 当前结论

这部分问题相对比 TTS 流式乱跳更接近解决。

本次后期结果是：

- 二次唤醒曾做到可以正常工作
- 用户也反馈“现在可以二次唤醒了”

但需要强调：

- 二次唤醒能不能稳定，不是一个独立问题
- 它会受 TTS 状态机是否干净、当前轮是否被中途打断影响
- 所以只要流式 TTS 乱跳没彻底解决，二次唤醒的最终稳定性仍有连带风险

---

## 七、当前最核心未解问题：AIOS 流式语音输出乱跳

这是整个迁移中最难、也是用户最不满意的部分。

### 1. 用户描述的典型现象

用户多次明确描述：

- 一句话没说完，它就蹦到别的话
- 它一句话没说完立马又说下一句
- 像多段语音叠在一起
- 文本可能很快显示完，但语音回复乱蹦

### 2. 这个问题不能简单归因给“大模型”

从当前掌握的信息看，**这 99% 不是 GPT/LLM 模型能力问题**，而是设备端 websocket + TTS 生命周期处理问题。

原因是：

- 文本流和音频流本来就是两条链
- AIOS 会下发：
  - `llm.text.delta`
  - `tts.audio.start`
  - 二进制音频包
  - `tts.audio.completed`
  - `conversation.completed`
- 只要设备端对这些事件处理不严谨，就会出现“听起来像模型在乱说”的错觉

实际上很多时候是：

- 音频被打断了
- decoder 被 reset 了
- 状态提前回 listening/idle 了
- 同一轮多段 TTS 没有被当成同一轮处理

### 3. 已经排除或基本排除的方向

这一节非常重要，方便下一个 AI 不要重复踩同一批坑。

#### 已排除 1：不是“根本没切到 AIOS websocket”

已经有明确日志证据：

- `AiosAuth: Calling AIOS auth endpoint: https://apiaios.nextbigseek.com/v2/device/auth`
- `WS: Connecting to websocket server: wss://wapiaios.nextbigseek.com/v2/chat`

因此当前问题不是“还在连旧服务器”。

#### 已排除 2：不是“服务端根本没下发 TTS 音频”

串口已经多次抓到连续 AIOS TTS 二进制音频：

- `AIOS TTS audio received: packets=1`
- `... packets=100`
- `... packets=500`
- `... packets=1000`
- `... packets=1300`
- 之后才有 `tts.audio.completed`

这说明：

- 服务端确实在持续推 TTS 音频
- 不是单纯“服务端没给语音”

#### 已排除 3：不是“二次本地唤醒”这一条单独原因

虽然前期“自己又被唤醒一次”是明确问题，但后期已经对它做了 suppress。

后续日志里，重复 wake 的情况明显减少。

因此，当前乱跳问题即使还和 wake 相关，也已经不再是“单纯被二次唤醒”这么简单。

#### 已排除 4：不是“纯文本显示太快”这个单一原因

中途曾经怀疑：

- 是不是 `llm.text.delta` 文本流太快
- 导致主观感觉像音频也在乱跳

我曾做过一次“文本慢速显示”实验，但这次实验引入了新的显示 bug，已经全部回退。

更重要的是，从协议上说：

- 文本显示快，只会影响视觉节奏
- 不应该直接造成音频跳句

所以它最多是放大问题体感，不是主因。

### 4. 已经尝试过的修复方向

#### 尝试 1：AIOS 模式下让 TTS 生命周期独立于旧 `tts/stt/llm` 类型消息

当前在 `application.cc` 中，已经对 AIOS `event_type` 做了独立处理：

- `session.connected`
- `asr.text.completed`
- `llm.text.delta`
- `llm.text.completed`
- `tts.audio.start`
- `tts.audio.completed`
- `turn.interrupt`
- `conversation.completed`
- `conversation.failed`

目标是避免 AIOS 事件再被旧 `type=tts/stt/llm` 逻辑误处理。

#### 尝试 2：只在新一轮 `tts.audio.start` 时 reset decoder

为了应对 AIOS 一轮回复可能包含多段 TTS：

- 第一次 `tts.audio.start`：`audio_service_.ResetDecoder()`
- 后续同轮 `tts.audio.start`：不重置 decoder

日志会打印：

- `AIOS continuing TTS stream without resetting decoder`

目的是避免“上一段刚播着，下一段 start 又把 decoder 清掉”。

#### 尝试 3：`tts.audio.completed` 不再等价于整轮结束

曾经的问题是：

- 一收到单个 `tts.audio.completed`
- 本地就把 speaking 当成结束

这会导致如果同一轮还有后续片段，直接被截断。

后续改为：

- `tts.audio.completed` 只标记 `tts_stream_finished_ = true`
- 还要等待：
  - `conversation.completed`
  - 本地播放队列确实播空
  - 最近一帧音频已过去一定时间

#### 尝试 4：收尾逻辑改到 clock tick 里统一判定

在 `MAIN_EVENT_CLOCK_TICK` 中增加 AIOS speaking 收尾判断：

- 只有在：
  - `tts_stream_finished_`
  - `conversation_completed_`
  - `last_tts_event_us_` 超过 grace period
  - 且最近 400ms 没有新 TTS 音频
  - 且 `audio_service_.IsIdle()`
- 才真正认为本地播放完成

否则继续保持 speaking。

#### 尝试 5：无本地活动播放时忽略 `turn.interrupt`

如果当前并没有真正本地活动播报：

- `accept_incoming_tts_audio_ == false`
- `state != Speaking`
- `audio_service_.IsIdle() == true`

则忽略 `turn.interrupt`，避免服务端某个清理信号把本地状态机提前搅乱。

### 5. 目前仍然怀疑的根因

截至这份文档编写时，流式语音输出仍然没有被彻底修好。以下是当前最值得继续追的方向。

#### 怀疑点 A：`turn.interrupt` 与本地播放时序仍未完全对齐

这是当前最大的嫌疑。

即使已经加了“无活动播放则忽略”的保护，仍不能证明：

- 所有真正该处理的 interrupt 都处理对了
- 所有不该处理的 interrupt 都被挡掉了

AIOS 服务端的 `turn.interrupt` 在一轮内部可能有更细的语义，而本地当前还是把它简化成“打断当前播放/回 listening”。

这很可能仍然过于粗糙。

#### 怀疑点 B：AIOS 一轮回复内部存在多段 TTS，而本地仍未完全区分“段结束”和“轮结束”

虽然已经加了：

- 同轮 start 不 reset decoder
- `tts.audio.completed` 不立刻收尾

但依然不能保证：

- 一轮内如果出现多次 `tts.audio.start/completed`
- 本地都能正确串起来

如果任何一段边界被误判成整轮结束，听感就会是“上一句没完，下一句蹦出来”。

#### 怀疑点 C：旧协议语义残留仍在干扰 AIOS 模式

这是我认为下一位接手者必须重视的一点。

当前仓库虽然已接入 AIOS，但代码结构上仍保留大量旧 xiaozhi 语义，包括：

- 旧 `type=tts/stt/llm`
- 旧 `listen`
- 旧 `abort`
- 旧 websocket hello 与旧 state 逻辑

即使 AIOS 路径已经独立处理了许多事件，只要这些旧逻辑仍共享同一套状态机和音频生命周期，就仍有可能在某些边界条件下产生副作用。

### 6. 我曾做过但已回退的失败尝试

为了避免下一个 AI 重复走弯路，这里明确写出来。

#### 失败尝试：把文本流式显示速度调慢

用户提出过一个思路：

- 文本现在虽然是流式的，但展示太快
- 会不会文本先很快刷完，导致感觉语音也乱跳

我曾试过：

- 给文字增加单独的 timer
- 每 120ms 或固定节奏显示一小段

结果：

- 这次实验把文本显示逻辑搞坏了
- 出现“只显示一句不动”的新问题
- 根因是事件循环中的 `continue` 逻辑影响了后续事件处理

这部分后来已经全部回退。

结论：

- 文字慢速显示不是当前应继续投入的方向
- 即使将来要做，也应该等 TTS 生命周期彻底稳定后再做

---

## 八、推荐给下一个 AI 的正确接手方式

这一节是给接力调试的人看的。

### 1. 不要从“现象猜想”继续乱改

不要再泛泛地做这些事情：

- 再试一个延迟
- 再试一个 fallback
- 再试一个显示节奏
- 再试一个强制 stop

这些如果没有更精细的证据，很容易只是继续堆补丁。

### 2. 应该先做的事：把 AIOS 模式的 TTS 生命周期单独打点

建议下一位先补充更精细的日志，至少打印：

- 当前轮本地编号 `local_turn_id`
- 每次收到：
  - `tts.audio.start`
  - `tts.audio.completed`
  - `conversation.completed`
  - `turn.interrupt`
- 收到这些事件时的本地状态：
  - `DeviceState`
  - `accept_incoming_tts_audio_`
  - `tts_stream_finished_`
  - `conversation_completed_`
  - `audio_service_.IsIdle()`
  - 最近一帧 TTS 音频到达时间差
  - 解码/播放队列长度（如果能拿到）

只有这样，才能最终确认到底是：

- interrupt 打断错了
- decoder reset 错了
- draining 过早了
- 还是服务端一轮里真的分了多段且本地没有正确串起来

### 3. 如果要彻底做干净，建议把 AIOS 播放状态机从旧链路里拆出来

我现在的判断是：

- 继续在原 `application.cc` 大状态机里打补丁，收益会越来越低
- 最终要真正稳定，最好把 AIOS 模式的对话生命周期单独抽象出来

至少在逻辑上做到：

- AIOS 模式的 speaking/listening/interrupt/completed
- 不再共享旧 xiaozhi 模式下那些隐含假设

### 4. 二次唤醒部分可以保留的思路

当前二次唤醒相关处理，建议大概率保留：

- `idle` 时主动清 AIOS 当前轮状态
- `idle` 时关闭旧 websocket，下一轮新建
- AIOS 活动轮屏蔽 wake word
- speaking 期间关闭 wake word detection

这些方向是对的。

---

## 九、当前代码里已经落过的关键实现点

下面列的是“本次迁移和修复中，当前仓库里已经落地过的关键改法”。如果下一个 AI 用的是原始工程，可以按这些思路重做。

### 1. `main/CMakeLists.txt`

已纳入 AIOS 构建：

- `aios/aios_crypto.cc`
- `aios/aios_http_client.cc`
- `aios_auth.cc`

### 2. `main/ota.cc`

已改成：

- 启动调用 `AiosAuthClient::FetchWebsocketConfig()`
- 把 AIOS websocket 相关配置写进 `Settings("websocket")`
- 写入 `aios_mode=true`

### 3. `main/protocols/websocket_protocol.cc`

已落过的关键点：

- AIOS websocket headers：
  - `Authorization`
  - `X-Device-Id`
  - `X-AIOS-Version`
  - `X-User-ID`
  - `X-Bot-ID`
- AIOS 模式下 `device.profile.report`
- `mode = vad`
- AIOS 模式下跳过 `up_stream.start/stop`
- AIOS 模式 `SendAbortSpeaking()` 改为 `conversation.cancel`

### 4. `main/application.h`

已增加 AIOS 播放与轮次控制状态：

- `accept_incoming_tts_audio_`
- `tts_stream_finished_`
- `conversation_completed_`
- `upstream_audio_paused_`
- `suppress_aios_wake_word_until_idle_`
- `last_tts_event_us_`
- `last_tts_audio_us_`
- `aios_tts_packet_count_`
- `assistant_reply_text_`

### 5. `main/application.cc`

已落过的关键点：

- AIOS `event_type` 独立处理
- `asr.text.completed` 时暂停继续上行麦克风处理
- `llm.text.delta` 只做显示累积
- `tts.audio.start`：首段 reset decoder，后续同轮不 reset
- `tts.audio.completed` 只标记段完成，不直接收尾
- `conversation.completed` 作为整轮结束信号之一
- `clock tick` 里等本地播放真正播空后再回 idle
- `turn.interrupt` 在无活动本地播放时忽略
- 活动 AIOS 轮次里屏蔽本地再次唤醒
- 回 idle 时清状态并关闭 AIOS audio channel

---

## 十、我自己验证过的证据

这一节只记录我在串口、编译、烧录层面真实拿到过的证据，不夸大。

### 1. 编译 / 烧录层

多次执行过：

- 编译成功生成 `build/xiaozhi.bin`
- 使用 `esptool.py` 或 `idf.py` 烧录到 `/dev/ttyACM0`
- 串口刷写结果中出现：
  - `Hash of data verified`

### 2. 启动链路层

多次抓到：

- `AiosAuth: Calling AIOS auth endpoint: https://apiaios.nextbigseek.com/v2/device/auth`
- `WS: Connecting to websocket server: wss://wapiaios.nextbigseek.com/v2/chat`

这足以说明：

- 当前链路已经不是单纯连原来的 xiaozhi 服务器
- AIOS auth 和 AIOS websocket 的主入口是通的

### 3. TTS 音频到达层

抓到过连续大量日志：

- `AIOS TTS audio received: packets=1`
- `AIOS TTS audio received: packets=50`
- `AIOS TTS audio received: packets=100`
- ...
- `AIOS TTS audio received: packets=1300`
- 之后 `tts.audio.completed`

这证明：

- 服务端确实在流式推二进制音频
- 当前问题不是“服务端根本没推 TTS”

### 4. 二次唤醒层

用户中途明确反馈过：

- “现在可以二次唤醒了”

所以这部分至少不是完全无效。

### 5. 不能夸大的部分

我不能诚实地说“流式 TTS 已经彻底修好”。

因为尽管串口日志已经比最早干净很多，但用户的主观听感仍然是：

- 语音回复乱蹦
- 一句话没说完就切后面的话

所以当前结论必须是：

- AIOS 迁移大体完成
- 二次唤醒已部分解决
- 流式 TTS 主问题仍未完全解决

---

## 十一、下一位 AI 最应该优先看的文件

建议按这个顺序看：

1. `main/application.cc`
2. `main/application.h`
3. `main/protocols/websocket_protocol.cc`
4. `main/protocols/protocol.cc`
5. `main/ota.cc`
6. `main/aios_auth.cc`
7. `docs/AIOS设备接入实测记录.md`
8. `docs/AIOS-websocket协议.md`
9. `docs/AIOS设备注册认证流程.md`
10. `docs/AIOS流式语音输出验收与排查.md`

---

## 十二、给下一个 AI 的一句话结论

如果只能用一句话概括这次工作，可以写成：

> 已经把原始 xiaozhi 工程的认证入口、websocket 入口和大部分运行时语义迁到了 AIOS；二次唤醒通过“关闭旧连接、活动轮屏蔽 wake word、speaking 期间禁用 wake word”已经有明显改善；当前最主要未解问题是 AIOS `turn.interrupt`、多段 `tts.audio.start/completed` 与本地 decoder / 播放队列 / 状态机之间仍未完全对齐，导致流式语音输出在用户听感上仍会出现一句没说完就跳下一句的现象。
