
# AIOS websocket协议v3.0 规范说明

# 更新日志

| **版本** | **日期** | **更新说明**                                                                                                                                                       |
| -------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| v3.10          | 20260325       | 修改pad.event.send下行事件，新增PAD三个参数，标记gain、tau参数为保留字段    
| v3.9           | 20260325       | 新增下行事件 `turn.interrupt`。当当前轮次被打断或取消时，服务端主动通知设备立即停止当前 TTS 播放并清空本地缓冲。 |
| v3.8           | 20260321       | 添加 VAD 模式。在 `device.profile.report` 中添加了 mode 字段。                      |
| v3.7           | 20260314       | 新增pad.event.send下行事件，ASR结束后推送表情PAD参数，用于设备端表情展示 |
| v3.6           | 20260110       | 规范上下行音频格式，包括 format、 sample_rate，audio_encode 等字段。规范下行音频的流程                                                                                   |
| v3.5           | 20260105       | 优化协议，规范定义。去掉使用 websocket 传递图片的做法。去掉了 BotID 和 ConversationID 字段。设备端无需定义这些字段。                                                     |
| v3.4           | 20251227       | 简化描述。添加术语定义。                                                           |
| v3.3           | 20251225       | **优化ws Header和设备信息上报**                                                                                                                                    |
| v3.2           | 20251225       | **优化二进制流传输**: 废弃Base64图片上传。引入 `up_stream.start/stop`事件对二进制流进行显式帧控制，允许音频和图片共用二进制通道，同时保证传输的原子性。          |
| v3.1           | 20251225       | **增加硬性约束**: 1. 新增协议设计原则。2. 明确 `tool.execute`串行语义与 `ack`确认阶段。3. 新增 `device.profile.report`事件。                                 |
| v3.0           | 20251224       | **重大重构**: 1. 将工具执行命令与 `ASCP协议`对齐，废弃整数编码。 2. 增加 `device.state.update`和 `tool.execute.failed`上行事件。 3. 统一并优化事件命名规范。 |
| v2.3           | 20251205       | 增加心跳机制, 优化心跳频率及超时机制描述                                                                |
| v2.2           | 20251119       | 增加文本、图片上报的事件                                              |
| v2.1           | 20251022       | 增加用于鉴权的product_id, user_id等信息                   |
| v2.0           | 20251016       | 优化上下行音频配置参数优化接入服务选择扩充多模态数据的传输和交互                                                                                                         |
| v1.0           | 20250901       | 完成通用对话，翻译对话的协议                                             |

## TODO-2026-01-05

- HTTP  文件上传/文件下载
- 设备接入鉴权流程：如何鉴权、是否分服（需和运维同事讨论）
- 设备与平台的信息同步（HTTP）
  - 设备上报 profile ：设备的静态属性，如版本号、设备型号、音频相关参数、IP 地址、系统语言。
  - 设备拉取最新状态：可能是设备信息、配置信息、账户信息等。

# 0. 术语定义

- 会话：指一次完整的对话，包括用户输入、智能体响应、工具执行等多个步骤。每一个会话云端会分配一个唯一的会话ID（`session_id`）。在后续的执行中都会传递，用于标识当前的对话上下文。
  - 当设备发起语音，则新的会话开始。

# 1. 协议设计原则与硬性约束

本章节定义了协议实现中**不可协商的语义和行为约束**，旨在消除模糊性，确保在分布式环境下的行为确定性。所有协议的实现方（设备端与服务端）都必须严格遵守。

### 原则1：指令执行的串行化 (Execution Order)

- **规则**：在单一会话（`session`）中，所有 `tool.execute.request`指令**必须被视为串行任务**。设备端必须按照接收到的顺序处理这些指令。
- **并发处理**：如果设备端当前正在执行一个指令而收到了新的 `tool.execute.request`，**必须**立即回复 `tool.execute.failed`事件，并携带 `"reason": "busy"`。
- **释义**：本协议默认不处理指令的并行执行与资源锁。接入服务的并行规划应转化为一系**列串行的指令**下发。此规则强制简化了设备端的任务队列与状态管理。

### 原则2：回执确认的语义 (Acknowledgement Semantic)

- **规则**：`ack.event_succeeded`事件的语义被严格定义为 **“已接受 (Accepted)”**。
- **“已接受”** 意味着服务端已完成以下操作：
  1. **已接收 (Received)**：消息已到达服务端。
  2. **已校验 (Validated)**：消息结构、参数类型等符合协议规范。
  3. **已入队 (Enqueued)**：消息已被放入内部处理队列，并保证后续会被处理。
- **释义**：此 `ack`**不保证**业务逻辑已执行完毕，而是承诺“请求已被接纳并将被处理”。客户端在收到 `ack`后即可认为请求已成功提交，无需等待业务结果。

### 原则3：取消操作（conversation.cancel`）的~~作用域 (Cancellation Scope)~~   无需作用域，服务器会取消全部当前对话

- **规则**：当当前轮次因显式取消、用户打断或新输入替换而非正常结束时，服务端**必须**下发 `turn.interrupt` 事件。
- **客户端行为**：
  1. 收到 `turn.interrupt` 后，客户端**必须**立即停止当前 TTS 播放。
  2. 客户端**必须**清空本地尚未播放的 TTS 缓冲。
  3. `turn.interrupt` 是幂等信令，重复收到时客户端应安全忽略重复副作用。

### 原则4：对话与工具的生命周期 (Lifecycle Independence)

- **规则**：`conversation.completed`事件的发送与 `tool.execute.*`的回执在协议层面**相互独立**。
- **`conversation.completed`的定义**：此事件仅代表“**当前轮次的语言交互已经完成**”（即ASCP识别、LLM回复、TTS播报等流程结束）。
- **`tool.execute.completed/failed`的定义**：此事件代表“**一个物理世界或软件工具的动作执行完成**”。
- **释义**：允许一个耗时较长的工具（如“去厨房倒杯水”）在语言交互结束后很长一段时间才返回结果。客户端UI需要自行管理和展示这些长时间运行的后台任务状态，而不应假定 `conversation.completed`代表一切都已结束。

### 原则5：显式帧的二进制流传输 (Framed Binary Streaming)

- **规则**：为在单一WebSocket连接上支持多种二进制数据类型（如音频、图片）的高性能传输，同时避免解析歧义，所有二进制数据都**必须**通过一个“开始-数据-停止”的显式帧序列来传输。
- **硬性约束**：
  1. **信令先行**：在发送任何二进制 `DATA`帧之前，客户端**必须**先发送一个 `up_stream.start`的JSON文本事件，声明即将开始的二进制流的类型和元数据。
  2. **数据传输**：在 `up_stream.start`之后，客户端可以发送一或多个连续的二进制 `DATA`帧。
  3. **信令断后**：在所有二进制 `DATA`帧发送完毕后，客户端**必须**发送一个 `up_stream.stop`的JSON文本事件，以标记二进制流的结束。
  4. **严格串行**：在一个 `start`和 `stop`信令之间，**严禁**插入任何其他类型的二进制数据流。整个序列（`start`→`DATA`帧→`stop`）必须是原子的。

### 原则6：文本数据的格式强制 (Text/JSON Mandate)

- **规则**：所有涉及**文本内容**（如 ASR 识别结果、LLM 文本流）、**控制信令**（如 ASCP 指令、握手配置）及**状态上报**的数据，**必须**且**仅能**通过 WebSocket 的 **Text Frame** 以 **JSON** 格式传输。
- **硬性约束**：
  - **禁止混用**：严禁为了追求微小的网络传输压缩比，将文本字符串（UTF-8）或结构化指令封装在 Binary Frame 中传输。
  - **通道隔离**：WebSocket Binary Frame **仅**被授权用于传输“媒体流数据”（音频 PCM/Opus、图片二进制）。
- **释义**：此原则确立了协议的 **“可读性优先 (Readability First)”** 策略。文本数据作为业务逻辑的核心载体，必须保持人类可读、易于调试（Debuggable）且对 Web/App 端友好。

### 原则7：设备与服务器维持单一websocket 链接

- 设备链接服务器会携带自身的唯一标识 `X-Device-Id`，服务器会根据该标识来识别设备。
- 如果存在两个相同的 `X-Device-Id`，服务器会拒绝第二个连接，提示“设备已连接”。

## 2. 双向流式对话协议

端侧设备请求与智能体对话的协议

```mermaid
sequenceDiagram
    autonumber
    participant User as 用户
    participant Device as 设备
    participant Agent as 智能体
    participant Manager as 管理平台
    participant Service as 其他服务

    %% 建立连接阶段
    rect rgb(230,245,255)
    note over User,Service: 1. 建立连接
    Device->>Agent: 请求WebSocket连接
    Agent-->>Device: 响应连接, 发送 session.connected
    Device->>Agent: 发送device.profile.report
    Agent-->>Device: 发送 conversation.started
    end

    %% 状态上报 (S_Self)
    rect rgb(230, 255, 230)
    note over Device, Agent: 2. 设备状态实时同步
    Device->>Agent: device.state.update (电量, 姿态等)
    end

    %% 正常对话阶段
    rect rgb(255,245,230)
    note over User,Service: 3. 正常对话
    User->>Device: 说话(语音输入)
    Device->>Agent: 发送 up_stream.start (type=audio)
    Device->>Agent: 二进制音频流
    Device->>Agent: 发送 up_stream.stop
    Agent-->>Device: asr.text.completed (返回语音识别结果)
    Agent->>Agent: 理解用户意图，构建应答路由

    alt 用户意图：请求执行控制操作工具
        Agent-->>Device: tool.execute.request (内嵌ASCP指令)
        alt 设备执行成功
            Device-->>Agent: tool.execute.completed
        else 设备执行失败
            Device-->>Agent: tool.execute.failed (含失败原因)
        end
    else 普通对话（无需调用工具）
        note right of Agent: 直接生成模型回复
    end

    Agent-->>Device: llm.text.completed (大模型文本输出)
    Device-->>User: 展示文本
    Agent-->>Device: 二进制音频流 (TTS) 或 tts.audio.delta
    Device-->>User: 播放TTS语音
    opt 用户在 TTS 播放中打断
        Agent-->>Device: turn.interrupt
        Device->>Device: 停止播放并清空TTS缓冲
    end
    Agent-->>Device: tts.audio.completed (告知：语音合成完成)

    Agent-->>Device: conversation.completed (本轮对话结束)
    end
```

# 3. websocket建立连接

**header说明**：

WebSocket 连接建立时，客户端需要通过 HTTP 请求头来传递认证信息和设备标识。

| **Header 名称** | 必填 | **说明**                                                                                                                                                                                         | **示例值**             |
| :-------------------- | :--- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------- |
| `X-Device-Id`       | ✅   | 设备的唯一标识符。在 WebSocket 握手阶段传递给服务端，用于设备身份识别。                                                                                                                                | `867400020316612`          |
| `Authorization`     | ✅   | 鉴权令牌，采用 `Bearer` 方案。客户端需携带有效的 Token 以完成身份验证。                                                                                                                              | `Bearer eyJhbGciOiJIUz...` |
| `X-AIOS-Version`    | ✅   | AIOS ws 协议版本，用于服务器向下兼容处理。                                                                                                                                                             | `3.0`                      |
| `X-User-ID`         | ⚪   | **身份**： <br /> **APP/Web端**：**必填**，明确操作用户。 <br />**设备端**：**选填**。<br />通常设备通过 TLS 双向认证或 DeviceID 绑定了 Owner，服务端可自动推导 UserID。 | usr_998                      |
| `X-Bot-ID`          | ✅   | **寻址**：指定要连接的智能体 ID。服务端据此加载对应的 Prompt 和工具集。                                                                                                                          | AG_xxxxx                     |

**连接参数说明：**

| **参数类别** | **参数名** | **必填** | **可选值**                         | **说明**                              |
| ------------------ | ---------------- | -------------- | ---------------------------------------- | ------------------------------------------- |
| **连接地址** | URL(测试环境）   | ✅             | wss://api.apsets.com/agentTestWS/v3/chat | websocket地址，实现接入服务的对话           |
|                    | URL(生产环境)    | ✅             | wss://api.apsets.com/agentWS/v3/chat     | websocket地址，实现接入服务的对话，正式环境 |

测试用假数据

```json
headers = {
    "X-Device-Id": "867400020316612",
    "Authorization": "Bearer MwTKyLOYEWSoxai0YEeYoiZK2sAdtfuQlWau/IIB5GWrSGrv8Wl2GXLSK0vZHiZHcmXKW4ljnTfP8OMX/SengCiui26A1fwsmZuTebUC7wka25YMbKOHD/9JRXqpWZRtAS4HELP2Z9dsN83DlSA8Mw==",
    "X-AIOS-Version": "3.0",
    "X-User-ID": "867400020316612",
    "X-Bot-ID" : "AG_xxxxx"
}  
```

# 3. 心跳协议

格式：UTF-8 编码的 JSON 字符串（或等效字节流）

| 参数       | 类型   | 是否必选 | 说明                |
| :--------- | :----- | :------- | :------------------ |
| event_type | String | 必选     | ping / pong         |
| timestamp  | int    | 必选     | Unix 时间戳，单位秒 |

#### 上行（客户端 → 服务端）

```json
{
    "event_type": "ping",
    "timestamp": 1767579484
}
```

#### 下行（服务端 → 客户端）

```json
{
    "event_type": "pong",
    "timestamp": 1767579484
}
```

- 用途：应用层确保连接正常。
- 进入应用之后，为了体验效果，心跳间隔设置为 3 秒。退出应用之后，可改为 120 秒一次，以降低服务器压力。
- 如果ping 失败（ping 发送失败或者 pong 丢失），设备需处理重连。如果服务器端心跳超时，则需标记设备为离线状态。
- 任意正常通讯的消息，对设备和服务器来说，都是有效的心跳消息。双方都应重置超时 timer。

# 4. 上行事件说明

设备侧发送给接入服务侧的事件

### 上报文本内容（`user.text.completed`可选）

当设备发送 user.text.completed 消息到服务器，可以视为一次新的会话的开始。如果之前的会话没有结束，则主动结束之前的会话。

- **事件类型**：`user.text.completed`
- **事件说明**：
  - 设备侧通过文本方式发送用户对话内容，替代音频上报，作为可选项。
  - **注意**：发送此事件后，服务端应视为用户已完成输入。
- **事件结构**：

| 参数       | 类型   | 是否必选 | 说明                                           |
| :--------- | :----- | :------- | :--------------------------------------------- |
| event_type | String | 必选     | 固定为user.text.completed。                    |
| timestamp  | int    | 必选     | Unix 时间戳，单位秒                            |
| data       | Object | 必选     | 包含文本消息的具体内容。                       |
| data.text  | String | 必选     | 用户输入的文本内容（例如：“帮我打开空调”）。 |

- **事件示例**：

```JSON
{
  "event_type": "user.text.completed",
  "timestamp": 1767579484,
  "data": {
    "text": "你好"
  }
}
```

### 设备能力与状态上报

#### 静态能力上报 (device.profile.report)

- **事件类型**：`device.profile.report`
- **事件说明**：
  - 用于设备在连接建立后，主动向接入服务（`S_Self`模块）上报其固有的、不会变化的硬件能力和静态档案。
  - 这使得AIOS具备“即插即用”的能力，无需在云端预先注册所有 `product_id`的详细信息。
- **事件结构**：

| **参数路径 (JSON Path)**   | **类型** | **必选** | **说明**              | **示例 / 枚举值**                      |
| -------------------------------- | -------------- | -------------- | --------------------------- | -------------------------------------------- |
| **event_type**             | String         | ✅             | 事件类型固定值              | `device.profile.report`                    |
| timestamp                        | int            | 必选           | Unix 时间戳，单位秒         |                                              |
| **data**                   | Object         | ✅             | 核心数据包                  | -                                            |
| **data.identity**          | Object         | ✅             | **身份信息**          | -                                            |
| `data.identity.product_id`     | String         | ✅             | 设备型号标识                | `fp-fphn-v1`                               |
| `data.identity.hard_ver`       | String         | ⚪             | 硬件版本号                  | `v1.0`, `rev_b`                          |
| `data.identity.firm_ver`       | String         | ⚪             | 固件版本号                  | `1.2.4`                                    |
| `data.identity.soft_ver`       | String         | ✅             | SDK或软件版本号             | `3.3.0`                                    |
| **data.audio**             | Object         | ✅             | **TTS音频参数**       | -                                            |
| `data.audio.down.sample_rate`  | Int            | ✅              | TTS采样率                   | `16000`                                    |
| `data.audio.down.format`       | String         | ✅             | TTS 音频格式                | `pcm`                                      |
| `data.audio.down.audio_encode` | String         | ✅              | TTS 音频传输编码方式        | `binary                                      |
| `data.audio.up.sample_rate`    | Int            | ✅              | ASR采样率                   | `16000`                                    |
| `data.audio.up.format`         | String         | ✅              | ASR 音频格式                | `pcm`                                      |
| `data.audio.up.audio_encode`   | String         | ✅              | ASR 音频传输编码方式        | `binary                                      |
| **data.language**          | Object         | ⚪             | **语言偏好**          | -                                            |
| `data.language.src`            | String         | ✅              | 用户输入语言                | zh-cn  zh-tw  other(en)                      |
| `data.language.tgt`            | String         | ✅              | 期望回复语言                | zh-cn  zh-tw  other(en)                      |
| **data.body_schema**       | Object         | ⚪             | **身体图式** (扩展用) | -                                            |
| `data.body_schema.components`  | Array          | ⚪             | 挂载的硬件组件列表          | `[{"type":"sensor.camera", ...}]`          |
| `data.mode`                   | String          | ⚪             |  工作模式          |   silence（静音模式，仅文本，没有语音返回）；no_vad（对讲机语音模式，没有 VAD，默认）；vad（VAD模式）    |


```
mode = "vad"， 说明工作在 VAD 模式下，设备的上行语音流不需要发送 `up_stream.start` 和 `up_stream.stop`这样的文本协议标记。语音流持续上传.

- `no_vad`：必须发送 `up_stream.start/up_stream.stop`
- `vad`：不需要额外切段文本信令
- `silence`：只表示不返回 TTS，不改变上行控制方式
```

- **事件示例**：

  ```JSON
  {
    "event_type": "device.profile.report",
    "timestamp": 1767579484,
    "data": {
      "identity": {
        "product_id": "ESP32_SPEAKER_V1",
        "hard_ver": "1.0",
        "firm_ver": "2.0.1",
        "soft_ver": "3.3.0"
      },
      "audio": {
        "up":{
          "format":"pcm", // amr  opus
          "sample_rate": 16000, 
          "audio_encode": "binary"
        },
        "down": {
          "format":"pcm", // amr  opus
          "sample_rate": 16000, 
          "audio_encode": "binary"
        }
      },
      "language": {
        "src": "zh-cn",
        "tgt": "zh-cn"
      }
    }
  }
  ```

测试用假数据

```json
{
  "event_type":"device.profile.report",
  "timestamp": 1767579484,
  "data":{
    "identity":{
      "product_id":"fp-fphn-v1", 
      "soft_ver":"3.0",
    },
    "audio":{
      "down":{
        "role":"wanwan",
      }
    },
    "language":{
      "src":"zh-cn",
      "tgt":"zh-cn",
    }
   }
}
```

#### 动态状态上报 (device.state.update)

- **事件类型**：`device.state.update`
- **事件说明**：
  - **核心事件**，用于设备主动向接入服务（`S_Self`模块）同步其动态变化的物理状态。
  - 设备可周期性上报（如10秒一次），或在状态发生重要变化时（如连接充电器、电量低于阈值）主动上报。
- **事件结构**：

| 参数              | 类型    | 是否必选 | 说明                                                    |
| :---------------- | :------ | :------- | :------------------------------------------------------ |
| event_type        | String  | 必选     | 固定为 `device.state.update`。                        |
| timestamp         | int     | 必选     | Unix 时间戳，单位秒                                     |
| data              | Object  | 必选     | 包含设备当前状态的快照。                                |
| data.energy_level | Float   | 可选     | 归一化的电量值 `[0.0, 1.0]`。                         |
| data.is_charging  | Boolean | 可选     | 是否正在充电。                                          |
| data.posture      | String  | 可选     | 当前姿态枚举 (`STANDING`, `MOVING`, `DOCKED`等)。 |
| data.errors       | Array   | 可选     | 当前生效的硬件错误列表。                                |

- **事件示例**：

  ```JSON
  {
    "event_type": "device.state.update",
    "timestamp": 1767579484,
    "data": {
      "EnergyLevel": 0.85,
      "IsCharging": false
    }
  }
  ```

### 二进制流上报 (Framed Binary Streaming)

此机制用于上传如音频、图片等二进制数据。

#### 开始二进制流 (up_stream.start)

- **事件类型**：`up_stream.start`
- **事件说明**：在发送任何二进制数据前**必须**发送此事件，用以声明流的类型和元数据。
- **事件结构**:

| 参数           | 类型   | 是否必选 | 说明                                                                        |
| :------------- | :----- | :------- | :-------------------------------------------------------------------------- |
| event_type     | String | 必选     | 固定为 `up_stream.start`。                                                |
| timestamp      | int    | 必选     | Unix 时间戳，单位秒                                                         |
| data           | Object | 必选     | 流的元数据。                                                                |
| data.type      | String | 必选     | 流类型，枚举值：`audio`  ~~image~~（流式只传输音频，图片应该走文件上传） |
| data.metadata  | Object | 必选     | 与类型相关的具体参数。                                                      |
| data.stream_id | String | 必选     | 格式年月日时分秒：20251224100020                                            |

- **事件示例 (开始上传音频)**:

  ```JSON
  {
    "event_type": "up_stream.start",
    "timestamp": 1767579484,
    "data": {
      "type": "audio",
      "stream_id":"20251224100020"
    }
  }
  ```

#### 二进制DATA帧传输

在 `up_stream.start` 事件发送后，设备端即可开始通过 WebSocket 的 **Binary Frame** 发送连续的二进制数据。

#### 停止二进制流 (up_stream.stop)

- **事件类型**：`up_stream.stop`
- **事件说明**：在二进制数据全部发送完毕后**必须**发送此事件，标记流的结束。
- **事件结构**:

| 参数           | 类型   | 是否必选 | 说明                                       |
| :------------- | :----- | :------- | :----------------------------------------- |
| event_type     | String | 必选     | 固定为 `up_stream.stop`。                |
| timestamp      | int    | 必选     | Unix 时间戳，单位秒                        |
| data           | Object | 必选     | 负载。                                     |
| data.stream_id | String | 可选     | 对应 `up_stream.start` 事件中的 `id`。 |

- **事件示例 (停止音频流)**:

  ```JSON
  {
    "event_type": "up_stream.stop",
    "timestamp": 1767579484,
    "data": {
      "stream_id": "20251224100020"
    }
  }
  ```

### 中断当前对话 `conversation.cancel`

- **事件类型**：`conversation.cancel`
- **事件说明**：发送此事件可取消正在进行的对话。
- **客户端约束**：
  - 当客户端只是要开始一轮新的输入时，**不要**先发送 `conversation.cancel`。
  - `conversation.cancel` 只用于“停止当前轮次，且不立即开启新轮次”的场景，例如设备上的“停止回答”按钮。
- **事件结构**：

| **参数** | **类型** | **是否必选** | **说明**                   |
| :------------- | :------------- | :----------------- | :------------------------------- |
| event_type     | String         | 必选               | 固定为 `conversation.cancel`。 |
| timestamp      | int            | 必选               | Unix 时间戳，单位秒              |

- **事件示例**：

```JSON
{
  "event_type": "conversation.cancel",
  "timestamp": 1767579484
}
```

### 工具执行回执 (成功/失败)

#### 工具执行成功 `tool.execute.failed`

- **事件类型**：`tool.execute.completed`
- **事件说明**：设备侧成功执行完接入服务下发的 `tool.execute.request` 指令后，上报此事件。
- **事件结构**：

| **参数** | **类型** | **是否必选** | **说明**                                              |
| :------------- | :------------- | :----------------- | :---------------------------------------------------------- |
| event_type     | String         | 必选               | 固定为 `tool.execute.completed`。                         |
| timestamp      | int            | 必选               | Unix 时间戳，单位秒                                         |
| data           | Object         | 必选               | 事件数据。                                                  |
| data.cmd_id    | String         | 必选               | 对应已成功执行的 `tool.execute.request` 指令中的 `id`。 |

- 事件样例

```JSON
{
  "event_type": "tool.execute.completed",
  "timestamp": 1767579484,
  "data": {
    "cmd_id": "20251224093010"
  }
}
```

#### 工具执行失败 `tool.execute.failed`

- **事件类型**：`tool.execute.failed`
- **事件说明**：当设备侧无法执行或执行 `tool.execute.request` 指令失败时，上报此事件。
- **事件结构**：

| **参数** | **类型** | **是否必选** | **说明**                                                                                     |
| :------------- | :------------- | :----------------- | :------------------------------------------------------------------------------------------------- |
| event_type     | String         | 必选               | 固定为 `tool.execute.failed`。                                                                   |
| timestamp      | int            | 必选               | Unix 时间戳，单位秒                                                                                |
| data           | Object         | 必选               | 事件数据。                                                                                         |
| data.id        | String         | 必选               | 客户端自行生成的事件 ID。                                                                          |
| data.cmd_id    | String         | 必选               | 对应执行失败的 `tool.execute.request` 指令中的 `id`。                                          |
| data.reason    | String         | 必选               | 预定义的失败原因枚举，如 `hardware_fault`, `invalid_params`, `permission_denied`, `busy`。 |
| data.message   | String         | 可选               | 供调试使用的详细错误信息。                                                                         |

- 事件样例

```JSON
{
  "event_type": "tool.execute.failed",
  "timestamp": 1767579484,
  "data": {
    "cmd_id": "20251224100020",
    "reason": "hardware_fault",
    "message": "Light bulb not responding to signals."
  }
}
```

# 5. 下行事件说明

接入服务侧发送事件给设备侧

### 会话连接成功 (session.connected)

- **事件类型**：`session.connected`
- **事件说明**：流式对话接口成功建立连接后，服务端发送的第一个事件，表示WebSocket会话已就绪。
- **事件结构**：

| **参数** | **类型** | **是否必选** | **说明**                 |
| :------------- | :------------- | :----------------- | :----------------------------- |
| event_type     | String         | 必选               | 固定为 `session.connected`。 |
| timestamp      | int            | 必选               | Unix 时间戳，单位秒            |

- 事件示例

```JSON
{
    "event_type": "session.connected",
    "timestamp": 1767579484
}
```

### 对话开始 (conversation.started)

- **事件类型**：`conversation.started`
- **事件说明**：创建新一轮对话的事件，紧随 `device.profile.report`之后发送，表示接入服务就绪，可以开始语音交互。
- **事件结构**：

| **参数** | **类型** | **是否必选** | **说明**                    |
| -------------- | -------------- | ------------------ | --------------------------------- |
| event_type     | String         | 必选               | 固定为 `conversation.started`。 |
| timestamp      | int            | 必选               | Unix 时间戳，单位秒               |
| data           | Object         | 必选               | 事件数据，包含对话的详细信息。    |

- **事件示例**：

```plaintext
{
  "event_type": "conversation.started",
  "timestamp": 1767579484
}
```

### 工具执行请求 (tool.execute.request)

- **事件类型**：`tool.execute.request`
- **事件说明**：**[核心变更]** 此事件用于接入服务向设备下发控制指令。为了实现协议的统一、可扩展和可维护性，而是直接采用 [AIOS控制协议](./AIOS语义控制协议 (ASCP).md)的标准JSON结构。WebSocket协议在此扮演ASCP指令的透明传输通道角色。
- **事件结构**：

| **参数** | **类型**   | **是否必选** | **说明**                       |
| :------------- | :--------------- | :----------------- | :----------------------------------- |
| event_type     | String           | 必选               | 固定为 `tool.execute.request`。    |
| timestamp      | int              | 必选               | Unix 时间戳，单位秒                  |
| **data** | **Object** | **必选**     | **完整的 `ASCP` 指令对象。** |

#### ASCP指令载荷说明

`data` 字段的内容就是一条标准的 `ASCP` 指令，其核心参数如下：

| **ASCP参数** | **类型**   | **说明**                                                     |
| :----------------- | :--------------- | :----------------------------------------------------------------- |
| **version**  | **String** | ASCP协议版本，如 "1.0"。                                           |
| **cmd_id**   | **String** | 年月日时分秒：20251224100020                                       |
| **target**   | **String** | **控制目标**，采用 `命名空间.模块`格式，如 `iot.light`。 |
| **action**   | **String** | **具体动作**，如 `set_power`。                             |
| **payload**  | **Object** | **动作参数**，一个包含具体参数的JSON对象。                   |

- **事件示例 (开灯)**:

```JSON
{
  "event_type": "tool.execute.request",
  "timestamp": 1767579484,
  "data": {
    "version": "1.0",
    "cmd_id": "20251224093010",
    "target": "iot.light",
    "action": "set_power",
    "payload": {
      "state": "on"
    }
  }
}
```

- **事件示例 (设置闹钟)**:

```JSON
{
  "event_type": "tool.execute.request",
  "timestamp": 1767579484,
  "data": {
    "version": "1.0",
    "id": "20251224100020",
    "target": "app.scheduler",
    "action": "set_alarm",
    "payload": {
      "datetime": "2025-12-25T08:00:00",
      "label": "起床",
      "repeat": "daily"
    }
  }
}
```

### ASR 识别完成 (asr.text.completed)

- **事件类型**：`asr.text.completed`
- **事件说明**：服务端完成对用户语音的识别后，发送此事件返回最终识别文本。
- **事件结构**：

| **参数** | **类型** | **是否必选** | **说明**                  |
| :------------- | :------------- | :----------------- | :------------------------------ |
| event_type     | String         | 必选               | 固定为 `asr.text.completed`。 |
| timestamp      | int            | 必选               | Unix 时间戳，单位秒             |
| data           | Object         | 必选               | 事件数据。                      |
| data.text      | String         | 必选               | 语音识别的最终文本结果。        |

- **事件示例**：

```JSON
{
  "event_type": "asr.text.completed",
  "timestamp": 1767579484,
  "data": {
    "text": "人工智能是未来科技的核心方向。"
  }
}
```

### PAD 事件发送(pad.event.send)

- **事件类型**：`pad.event.send`
- **事件说明**：服务端向设备推送pad参数，发送此事件用于设备展示对应表情。
- **事件结构**：

| **参数** | **类型** | **是否必选** | **说明**              |
| :------------- | :------------- | :----------------- | :-------------------------- |
| event_type     | String         | 必选               | 固定为 `pad.event.send`。 |
| timestamp      | int            | 必选               | Unix 时间戳，单位秒         |
| data           | Object         | 必选               | 事件数据。                  |

- **事件示例**：

```JSON
{
  "event_type": "pad.event.send",
  "timestamp": 1767579484,
  "data": {
    "p":3.0,
    "a":3.0,
    "d":3.0,
// 以下值作为保留拓展值，暂无实际传参
    "gain_p": 3.0,
    "gain_a": 3.0,
    "gain_d": 3.0,
    "tau_p": 3.0,
    "tau_a": 3.0,
    "tau_d": 3.0,
  }
}
```

### LLM 文本流 (llm.text.delta)

- **事件类型**：`llm.text.delta`
- **事件说明**：接入服务生成文本回复时的流式事件，每个事件包含一个文本片段。
- **事件结构**：

| **参数** | **类型** | **是否必选** | **说明**              |
| :------------- | :------------- | :----------------- | :-------------------------- |
| event_type     | String         | 必选               | 固定为 `llm.text.delta`。 |
| timestamp      | int            | 必选               | Unix 时间戳，单位秒         |
| data           | Object         | 必选               | 事件数据。                  |
| data.delta     | String         | 必选               | 本次流式传输的文本片段。    |

- **事件示例**：

```JSON
{
  "event_type": "llm.text.delta",
  "timestamp": 1767579484,
  "data": {
    "delta": "哇，"
  }
}
```

### LLM 文本完成 (llm.text.completed)

- **事件类型**：`llm.text.completed`
- **事件说明**：接入服务完成一次完整的文本回复。
- **事件结构**：

| **参数** | **类型** | **是否必选** | **说明**                  |
| :------------- | :------------- | :----------------- | :------------------------------ |
| event_type     | String         | 必选               | 固定为 `llm.text.completed`。 |
| timestamp      | int            | 必选               | Unix 时间戳，单位秒             |
| data           | Object         | 必选               | 事件数据。                      |
| data.text      | String         | 必选               | 本次回复的完整拼接文本。        |

- **事件示例**：

```JSON
{
  "event_type": "llm.text.completed",
  "timestamp": 1767579484,
  "data": {
    "text": "哇，你这么说的话，我是不是也要变成未来科技的一部分啦？"
  }
}
```

### TTS 语音流开始 (tts.audio.start)

- **事件类型**：`tts.audio.start`
- **事件说明**：表示流式语音数据开始发送。
- **事件结构**：

| **参数** | **类型** | **是否必选** | **说明**               |
| :------------- | :------------- | :----------------- | :--------------------------- |
| event_type     | String         | 必选               | 固定为 `tts.audio.start`。 |
| timestamp      | int            | 必选               | Unix 时间戳，单位秒          |

- **事件示例**：

```JSON
{
  "event_type": "tts.audio.start",
  "timestamp": 1767579484,
}
```

### TTS 语音流文本格式 (tts.audio.delta)

当客户端要求使用 base64 的编码来传输 TTS 音频流的时候，使用文本消息 tts.audio.delta

- **事件类型**：`tts.audio.delta`
- **事件说明**：此事件用于流式返回Base64编码的音频片段。
- **事件结构**：

| **参数** | **类型** | **是否必选** | **说明**               |
| :------------- | :------------- | :----------------- | :--------------------------- |
| event_type     | String         | 必选               | 固定为 `tts.audio.delta`。 |
| timestamp      | int            | 必选               | Unix 时间戳，单位秒          |
| data           | Object         | 必选               | 事件数据。                   |
| data.chunk     | String         | 必选               | Base64编码的音频数据片段。   |

- **事件示例**：

```JSON
{
  "event_type": "tts.audio.delta",
  "timestamp": 1767579484,
  "data": {
      "chunk": "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACAB...",
  }
}
```

### TTS 语音流完成 (tts.audio.completed)

- **事件类型**：`tts.audio.completed`
- **事件说明**：表示与 `llm.text.completed`文本对应的所有语音数据已全部发送完毕。
- **事件结构**：

| **参数** | **类型** | **是否必选** | **说明**                   |
| :------------- | :------------- | :----------------- | :------------------------------- |
| event_type     | String         | 必选               | 固定为 `tts.audio.completed`。 |
| timestamp      | int            | 必选               | Unix 时间戳，单位秒              |

- **事件示例**：

```JSON
{
  "event_type": "tts.audio.completed",
  "timestamp": 1767579484,
}
```

### 当前轮次被打断 (turn.interrupt)

- **事件类型**：`turn.interrupt`
- **事件说明**：表示当前轮次被非正常结束，例如被用户新输入打断、被新的轮次替换，或被显式取消。客户端收到该事件后，必须立即停止当前 TTS 播放，并清空本地尚未播放的 TTS 缓冲。
- **事件结构**：

| **参数** | **类型** | **是否必选** | **说明** |
| :------------- | :------------- | :----------------- | :------------------------------- |
| event_type     | String         | 必选               | 固定为 `turn.interrupt`。 |
| timestamp      | int            | 必选               | Unix 时间戳，单位秒              |
| data           | Object         | 可选               | 事件数据。                       |
| data.reason    | String         | 可选               | 打断原因。建议值：`interrupt`、`replaced`、`cancelled`。 |

- **客户端处理要求**：
  - 必须立即停止当前播放中的 TTS。
  - 必须清空本地尚未播放的 TTS 队列和缓冲。
  - 不应等待 `tts.audio.completed` 后再停播。

- **事件示例**：

```JSON
{
  "event_type": "turn.interrupt",
  "timestamp": 1767579484,
  "data": {
    "reason": "barge_in"
  }
}
```

### 对话完成 (conversation.completed)

- **事件类型**：`conversation.completed`
- **事件说明**：表示一轮完整的对话（从用户输入到接入服务最终响应）已经结束。
- **事件结构**：

| **参数**    | **类型** | **是否必选** | **说明**                      |
| :---------------- | :------------- | :----------------- | :---------------------------------- |
| event_type        | String         | 必选               | 固定为 `conversation.completed`。 |
| timestamp         | int            | 必选               | Unix 时间戳，单位秒                 |
| data              | Object         | 可选               | 事件数据。                          |
| data.completed_at | Integer        | 可选               | 对话结束的Unix时间戳（秒）。        |

- **事件示例**：

```JSON
{
  "event_type": "conversation.completed",
  "timestamp": 1767579484,
}
```

### 对话失败 (conversation.failed)

**事件类型**：`conversation.failed`
**事件说明**：此事件用于标识整轮对话处理失败。
**事件结构**：

| 参数             | 类型    | 是否必选 | 说明                                                       |
| :--------------- | :------ | :------- | :--------------------------------------------------------- |
| event_type       | String  | 必选     | 固定为 `conversation.failed`。                           |
| timestamp        | int     | 必选     | Unix 时间戳，单位秒                                        |
| data             | Object  | 必选     | 事件数据。                                                 |
| data.code        | Integer | 必选     | 错误码 (详情见编码表)。                                    |
| data.message     | String  | 可选     | 调试用错误信息 (如 "ASR service timeout")。                |
| data.display_msg | String  | 可选     | **建议新增**：面向用户的友善提示语 (如 "我没听清")。 |

**事件示例**：

```json
{
  "event_type": "conversation.failed",
  "timestamp": 1767579484,
  "data": {
    "code": 4101,
    "message": "VAD detection returned silence.",
    "display_msg": "刚才没听清，请再说一次"
  }
}
```

### 通用错误 (error)

- **定义**：**“对话流程外”**或**“协议/系统级”**的异常。
- **触发时机**：连接层、鉴权层、协议格式解析层、或者严重的系统崩溃。
- **端侧行为**：通常意味着**严重错误**。如果是 4xxx/5xxx 可能需要丢弃当前包；如果是 6xxx（如 Auth 失败），通常需要**断开连接**并触发重新登录。

**事件类型**：`error`
**事件说明**：在无法归类到特定对话或流程中的通用或意外错误发生时发送（如协议解析失败、鉴权失败、限流等）。
**事件结构**：

| 参数         | 类型    | 是否必选 | 说明                    |
| :----------- | :------ | :------- | :---------------------- |
| event_type   | String  | 必选     | 固定为 `error`。      |
| timestamp    | int     | 必选     | Unix 时间戳，单位秒     |
| data         | Object  | 必选     | 事件数据。              |
| data.code    | Integer | 必选     | 错误码 (详情见编码表)。 |
| data.message | String  | 必选     | 错误信息。              |

**事件示例**：

```json
{
  "event_type": "error",
  "timestamp": 1767579484,
  "data": {
    "code": 6001,
    "message": "Invalid authentication token."
  }
}
```

### 状态码划分与事件映射表

这张表格是核心。它指导后端开发者**“这个错误应该发哪个事件”**，同时指导端侧开发者**“收到这个码该怎么处理”**。

| **编码 (Code)**                | **标识符 (Enum)** | **推荐事件类型 (Event Type)** | **说明**                    | **端侧建议行为**       |
| ------------------------------------ | ----------------------- | ----------------------------------- | --------------------------------- | ---------------------------- |
| **4xxx：客户端/输入/协议错误** |                         |                                     |                                   |                              |
| **4000**                       | `INVALID_REQUEST`     | `error`                           | 通用协议格式错误 (JSON不对)       | 检查发包逻辑                 |
| **4001**                       | `AUDIO_FORMAT_ERR`    | `conversation.failed` / `error` | 音频编码头错误                    | 检查麦克风配置               |
| **4003**                       | `SEQUENCE_ERROR`      | `error`                           | 二进制流缺 start/stop 信令        | 重置发送状态                 |
| **4005**                       | `RATE_LIMITED`        | `error`                           | 发送频率过快                      | **休眠 5秒**           |
| **4101**                       | `VAD_SILENCE`         | `conversation.failed`             | **VAD拦截**：没听到说话     | 提示用户并重置监听           |
| **4102**                       | `VAD_NOISY`           | `conversation.failed`             | **VAD拦截**：太吵           | 提示“环境嘈杂”             |
| **4105**                       | `LANG_NOT_SUPPORTED`  | `conversation.failed`             | 语言不支持                        | 提示“不支持该语言”         |
| **4200**                       | `SENSITIVE_INPUT`     | `conversation.failed`             | 内容敏感/违规                     | 提示“话题敏感”             |
|                                      |                         |                                     |                                   |                              |
| **5xxx：服务端/AI 错误**       |                         |                                     |                                   |                              |
| **5000**                       | `INTERNAL_ERROR`      | `error`                           | 服务端未捕获的异常                | 重试                         |
| **5001**                       | `SERVER_BUSY`         | `error`                           | 网关限流/排队溢出                 | 随机退避重试                 |
| **5101**                       | `ASR_TIMEOUT`         | `conversation.failed`             | ASR 识别超时                      | 提示“语音服务超时”         |
| **5102**                       | `ASR_FAILED`          | `conversation.failed`             | ASR 识别失败                      | 提示“语音服务返回空文本”   |
| **5201**                       | `LLM_TIMEOUT`         | `conversation.failed`             | 大模型生成超时                    | 提示“思考超时”             |
| **5203**                       | `CONTEXT_OVERFLOW`    | `conversation.failed`             | 上下文超限                        | **建议自动清空历史**   |
| **5301**                       | `TTS_TIMEOUT`         | `conversation.failed`             | TTS 合成超时                      | 降级为文本显示               |
| **5400**                       | `TOOL_FAIL`           | `conversation.failed`             | 工具执行失败 (通用)               | 播报错误                     |
| **5404**                       | `DEVICE_OFFLINE`      | `conversation.failed`             | 要控制的 IoT 设备离线             | 提示“设备离线”             |
|                                      |                         |                                     |                                   |                              |
| **6xxx：账户/权限错误**        |                         |                                     |                                   |                              |
| **6001**                       | `AUTH_FAILED`         | `error`                           | **Token 无效/过期**         | **断开连接，重新登录** |
| **6002**                       | `NO_BALANCE`          | `conversation.failed`             | **余额不足** (对话中途发现) | 提示充值                     |
| **6003**                       | `TRIAL_END`           | `conversation.failed`             | **试用耗尽**                | 提示订阅                     |
| **6004**                       | `CONCURRENT_LIMIT`    | `error`                           | **被挤线** (多端登录)       | **断开连接，不再重连** |
| **6005**                       | `REGION_RESTRICTED`   | `error`                           | IP 地区限制                       | 停止服务                     |

### 上行事件回执 (ack.event_succeeded，未来使用)

- **事件类型**：`ack.event_succeeded`
- **事件说明**：服务端用于确认已成功接收并处理某个需要回执的上行事件。这是一个通用回执事件。
- **事件结构**：

| **参数** | **类型** | **是否必选** | **说明**                   |
| :------------- | :------------- | :----------------- | :------------------------------- |
| event_type     | String         | 必选               | 固定为 `ack.event_succeeded`。 |
| timestamp      | int            | 必选               | Unix 时间戳，单位秒              |

- **事件示例 (确认收到音频)**：

```JSON
{
  "event_type": "ack.event_succeeded",
  "timestamp": 1767579484,
}
```

# 5、图像处理/识图功能

协议3.3 版本的图像处理，设计的是走 websocket 通道。

结合场景的分析：

| 需求               | 实时语音交互                              | 图像处理/识别                                      |
| ------------------ | ----------------------------------------- | -------------------------------------------------- |
| **延迟要求** | **极低**（< 300ms 端到端）          | 容忍高延迟（秒级~分钟级）                          |
| **数据特征** | 连续小包（音频流）、有序、丢包敏感        | 大文件（MB 级）、可分块、可重传                    |
| **连接模式** | **长连接 + 流式**                   | **短连接 + 请求/响应** 或 **异步任务** |
| **错误容忍** | 丢包可接受（用 FEC/Opus），但不能重传卡顿 | **必须可靠传输**，需重传机制                 |
| **典型协议** | WebSocket / gRPC-Stream / 自定义 TCP 流   | HTTP/HTTPS / gRPC / MQTT（带 QoS2）                |

考虑到我们已经有了对象存储的标准接口（上传和下载文件）。而且 websocket 服务需要支持大规模设备长连接和高并发。如果维护一套私有协议传输图片，并对接到对象存储，从维护和优化的角度来说这个设计不好。

AI图片处理方案：

- 当有一个图片需要处理的时候，上传文件到对象存储中，并返回一个 objectKey。
- 客户端拿着 objectkey 调用相关 HTTP 接口来处理图片。
- 后端会使用异步任务来处理图片。处理完成之后会标记状态。
- 客户端轮询（间隔 3 秒）来获取处理结果，解析得到 ObjectKey。
- 客户端下载文件展示给用户。

AI 识图方案：

- 当有一个图片需要处理的时候，上传文件到对象存储中，并返回一个 objectKey。
- 客户端通过 websocket 通道，上报消息： event_type 是图片处理， 携带文件的 objectkey 。
- websocket 服务将消息转给 LLM。得到 LLM 返回的识图结果。
- websocket 服务将结果通过 TTS 服务转为语音下发给客户端。
