# AIOS Native Backend Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将当前固件改造成可直接接入 AIOS 现成后端，并建立“开发 -> 编译 -> 烧录 -> 日志观测 -> 冒烟测试”的自动化闭环。

**Architecture:** 采用 AIOS 原生主导方案。新增 `main/aios/` 目录承载 HTTP、加密、WebSocket、会话管理与动作执行；保留 `AudioService`、`DeviceStateMachine`、`Board`、显示和电源管理等本地能力。使用一套统一的本地脚本把编译、烧录、串口监控、日志断言和联机冒烟测试串起来。

**Tech Stack:** ESP-IDF 5.4+、C++、cJSON、mbedTLS、Python 3、pyserial、bash、现有 `idf.py` 与 `scripts/release.py`

---

## Working Assumptions

本计划默认使用 `esp-box-3` 作为首个联调板型，因为仓库中已有现成配置文件 `main/boards/esp-box-3/config.json`。如果实际硬件不是 `esp-box-3`，执行阶段应整体替换为目标板型，但不要在同一轮实现里同时支持多个板型。

本计划默认串口设备为 `/dev/ttyACM0`。

本计划默认 AIOS 联调地址为：

- API Base URL: `https://apiaios.nextbigseek.com/v2`
- WebSocket URL: 以 `/device/auth` 返回的 `ws.url` 为准

## File Structure

### Existing Files To Modify

- Modify: `main/application.cc`
  - 收缩旧协议编排职责，改为初始化 AIOS 子系统并接收 AIOS 会话回调
- Modify: `main/CMakeLists.txt`
  - 注册 `main/aios/` 新文件
- Modify: `main/Kconfig.projbuild`
  - 增加 AIOS 配置项和开发闭环脚本需要的可编译配置
- Modify: `main/settings.h`
- Modify: `main/settings.cc`
  - 增加 AIOS 运行时凭证与状态读写入口
- Modify: `main/system_info.h`
- Modify: `main/system_info.cc`
  - 增加结构化运行态采样接口，支持日志与状态上报
- Modify: `main/audio/audio_service.h`
- Modify: `main/audio/audio_service.cc`
  - 暴露必要的队列统计、清空播放缓冲和调试接口

### New Runtime Files

- Create: `main/aios/aios_event_types.h`
  - AIOS 事件名、字段名、错误原因常量
- Create: `main/aios/aios_crypto.h`
- Create: `main/aios/aios_crypto.cc`
  - RSA/AES 封装、加密解密、签名校验
- Create: `main/aios/aios_http_client.h`
- Create: `main/aios/aios_http_client.cc`
  - `register/auth/sync`
- Create: `main/aios/aios_ws_client.h`
- Create: `main/aios/aios_ws_client.cc`
  - websocket 建连、header、心跳、文本/二进制收发
- Create: `main/aios/aios_conversation_manager.h`
- Create: `main/aios/aios_conversation_manager.cc`
  - 会话编排、状态映射、音频上下行
- Create: `main/aios/aios_action_executor.h`
- Create: `main/aios/aios_action_executor.cc`
  - `tool.execute.request` 串行执行与内部能力桥接
- Create: `main/aios/aios_runtime_metrics.h`
- Create: `main/aios/aios_runtime_metrics.cc`
  - heap、队列、会话、心跳等运行指标采样
- Create: `main/aios/aios_event_journal.h`
- Create: `main/aios/aios_event_journal.cc`
  - ring buffer 事件日志

### New Automation Files

- Create: `tools/aios/dev_env.sh`
  - 统一导出板型、串口、日志目录和 AIOS 运行参数
- Create: `tools/aios/build_firmware.sh`
  - 统一编译入口
- Create: `tools/aios/flash_firmware.sh`
  - 统一烧录入口
- Create: `tools/aios/monitor_and_assert.py`
  - 串口采集 + 关键日志断言
- Create: `tools/aios/run_live_smoke.sh`
  - 串联 build/flash/monitor/assert 的一键闭环
- Create: `tools/aios/README.md`
  - 说明自动闭环使用方式

### New Verification Files

- Create: `docs/superpowers/checklists/aios-live-smoke.md`
  - 联机手工验收 checklist

## Closed-Loop Automation Design

自动闭环以 `tools/aios/run_live_smoke.sh` 为唯一入口，内部顺序固定为：

1. 加载环境变量
2. 编译固件
3. 烧录固件
4. 打开串口日志
5. 等待并断言 AIOS 关键阶段日志
6. 输出通过/失败结果和日志文件路径

默认断言日志顺序：

1. `AIOS auth success`
2. `AIOS websocket connected`
3. `session.connected`
4. `device.profile.report sent`
5. `device sync success`
6. `conversation idle ready`

第二阶段扩展断言：

1. `up_stream.start sent`
2. `asr.text.completed`
3. `tts playback started`
4. `conversation.completed`

## Execution Record Rules

从本版本开始，每个 Task 都必须有一份单独执行记录，记录内容至少包含：

- 本任务做了什么
- 修改了哪些文件
- 执行验证结果
- 遇到的坑和修复方式
- 当前遗留问题或下一阻塞点

任务记录目录：

- [Task 1 记录](/home/w/xiaozhi-esp32/docs/superpowers/tasks/task-01-build-surface.md)
- [Task 2 记录](/home/w/xiaozhi-esp32/docs/superpowers/tasks/task-02-settings-metrics-skeleton.md)
- [Task 3 记录](/home/w/xiaozhi-esp32/docs/superpowers/tasks/task-03-http-bootstrap.md)
- [Task 4 记录](/home/w/xiaozhi-esp32/docs/superpowers/tasks/task-04-websocket-session-bring-up.md)
- [Task 5 记录](/home/w/xiaozhi-esp32/docs/superpowers/tasks/task-05-conversation-manager-uplink.md)
- [Task 6 记录](/home/w/xiaozhi-esp32/docs/superpowers/tasks/task-06-downstream-events-tts-interrupt.md)
- [Task 7 记录](/home/w/xiaozhi-esp32/docs/superpowers/tasks/task-07-tool-execution-bridge.md)
- [Task 8 记录](/home/w/xiaozhi-esp32/docs/superpowers/tasks/task-08-automation-loop.md)
- [Task 9 记录](/home/w/xiaozhi-esp32/docs/superpowers/tasks/task-09-runtime-observability.md)

记录维护规则：

- Task 开始时创建记录文件并写入目标、当前状态和预期风险
- Task 完成后补齐“做了什么、验证、踩坑、当前阻塞点”
- 如果 review 发现问题，必须把 review 结论和修复结果回写到对应任务记录

## Task 1: Add AIOS Build-Time Configuration Surface

**Files:**
- Modify: `main/Kconfig.projbuild`
- Modify: `main/CMakeLists.txt`
- Test: `main/Kconfig.projbuild`

- [ ] **Step 1: Add failing build expectation to force missing AIOS source registration**

Run: `idf.py -DIDF_TARGET=esp32s3 -DBOARD_NAME=esp-box-3 -DBOARD_TYPE=esp-box-3 build`
Expected: PASS today without AIOS objects, which proves the build graph has not been updated yet.

- [ ] **Step 2: Add Kconfig entries for AIOS URLs and development defaults**

```kconfig
menu "AIOS"
    config AIOS_API_BASE_URL
        string "AIOS API base URL"
        default "https://apiaios.nextbigseek.com/v2"

    config AIOS_PUBLIC_KEY_BASE64
        string "AIOS RSA public key (Base64 DER)"
        default ""

    config AIOS_WS_PROTOCOL_VERSION
        string "AIOS websocket protocol version"
        default "3.0"

    config AIOS_DEVICE_PRODUCT_ID
        int "AIOS device product id"
        default 0

    config AIOS_TENANT_USER_ID
        int "AIOS tenant user id"
        default 0
endmenu
```

- [ ] **Step 3: Register AIOS source files in the component build**

```cmake
list(APPEND SOURCES
    "aios/aios_crypto.cc"
    "aios/aios_http_client.cc"
    "aios/aios_ws_client.cc"
    "aios/aios_conversation_manager.cc"
    "aios/aios_action_executor.cc"
    "aios/aios_runtime_metrics.cc"
    "aios/aios_event_journal.cc"
)

list(APPEND INCLUDE_DIRS "aios")
```

- [ ] **Step 4: Rebuild to verify the build graph is wired**

Run: `idf.py -DIDF_TARGET=esp32s3 -DBOARD_NAME=esp-box-3 -DBOARD_TYPE=esp-box-3 build`
Expected: FAIL with missing AIOS source/header symbols until the new files are actually created.

- [ ] **Step 5: Commit**

```bash
git add main/Kconfig.projbuild main/CMakeLists.txt
git commit -m "build: add AIOS configuration surface"
```

## Task 2: Implement AIOS Event Constants, Credentials, and Metrics Skeleton

**Files:**
- Create: `main/aios/aios_event_types.h`
- Create: `main/aios/aios_runtime_metrics.h`
- Create: `main/aios/aios_runtime_metrics.cc`
- Create: `main/aios/aios_event_journal.h`
- Create: `main/aios/aios_event_journal.cc`
- Modify: `main/settings.h`
- Modify: `main/settings.cc`
- Modify: `main/system_info.h`
- Modify: `main/system_info.cc`
- Test: `tools/aios/monitor_and_assert.py`

- [ ] **Step 1: Create a failing compile by referencing missing AIOS constants from `application.cc`**

```cpp
#include "aios_event_types.h"

static_assert(aios::kEventSessionConnected[0] == 's');
```

Run: `idf.py -DIDF_TARGET=esp32s3 -DBOARD_NAME=esp-box-3 -DBOARD_TYPE=esp-box-3 build`
Expected: FAIL with `aios_event_types.h: No such file or directory`

- [ ] **Step 2: Create event-name constants**

```cpp
#pragma once

namespace aios {
inline constexpr char kEventSessionConnected[] = "session.connected";
inline constexpr char kEventConversationStarted[] = "conversation.started";
inline constexpr char kEventConversationCompleted[] = "conversation.completed";
inline constexpr char kEventTurnInterrupt[] = "turn.interrupt";
inline constexpr char kEventDeviceProfileReport[] = "device.profile.report";
inline constexpr char kEventDeviceStateUpdate[] = "device.state.update";
inline constexpr char kEventUpStreamStart[] = "up_stream.start";
inline constexpr char kEventUpStreamStop[] = "up_stream.stop";
inline constexpr char kEventToolExecuteRequest[] = "tool.execute.request";
inline constexpr char kEventToolExecuteCompleted[] = "tool.execute.completed";
inline constexpr char kEventToolExecuteFailed[] = "tool.execute.failed";
}
```

- [ ] **Step 3: Add AIOS credential getters/setters to `Settings` usage sites**

```cpp
struct AiosCredentials {
    std::string device_user_id;
    std::string access_key;
    std::string access_secret;
    std::string token;
    std::string ws_url;
};
```

```cpp
Settings settings("aios", true);
settings.SetString("access_key", credentials.access_key);
settings.SetString("access_secret", credentials.access_secret);
settings.SetString("token", credentials.token);
settings.SetString("ws_url", credentials.ws_url);
```

- [ ] **Step 4: Add runtime metrics snapshot and event journal skeleton**

```cpp
struct AiosRuntimeSnapshot {
    size_t free_heap = 0;
    size_t min_free_heap = 0;
    bool websocket_connected = false;
    bool session_connected = false;
    int audio_send_queue_depth = 0;
    int audio_decode_queue_depth = 0;
    int audio_playback_queue_depth = 0;
    std::string device_state;
};
```

```cpp
struct AiosJournalEvent {
    int64_t timestamp_ms = 0;
    std::string type;
    std::string detail;
};
```

- [ ] **Step 5: Rebuild to verify the skeleton compiles**

Run: `idf.py -DIDF_TARGET=esp32s3 -DBOARD_NAME=esp-box-3 -DBOARD_TYPE=esp-box-3 build`
Expected: FAIL only on the next missing AIOS module, not on constants/settings/metrics types.

- [ ] **Step 6: Commit**

```bash
git add main/aios/aios_event_types.h main/aios/aios_runtime_metrics.h main/aios/aios_runtime_metrics.cc main/aios/aios_event_journal.h main/aios/aios_event_journal.cc main/settings.h main/settings.cc main/system_info.h main/system_info.cc
git commit -m "feat: add AIOS settings and metrics skeleton"
```

## Task 3: Implement AIOS Crypto and HTTP Bootstrap

**Files:**
- Create: `main/aios/aios_crypto.h`
- Create: `main/aios/aios_crypto.cc`
- Create: `main/aios/aios_http_client.h`
- Create: `main/aios/aios_http_client.cc`
- Modify: `main/application.cc`
- Test: `tools/aios/monitor_and_assert.py`

- [ ] **Step 1: Create a failing compile by calling `AiosHttpClient::Auth()` from `Application`**

```cpp
#include "aios_http_client.h"

aios::AiosHttpClient client;
client.Auth();
```

Run: `idf.py -DIDF_TARGET=esp32s3 -DBOARD_NAME=esp-box-3 -DBOARD_TYPE=esp-box-3 build`
Expected: FAIL with missing class or method definitions.

- [ ] **Step 2: Implement crypto wrapper interface**

```cpp
class AiosCrypto {
public:
    bool Initialize(const std::string& public_key_base64);
    bool EncryptRequestBody(const std::string& json, std::string& encrypted_key, std::string& encrypted_body);
    bool DecryptResponseBody(const std::string& encrypted_body, const std::string& aes_key, std::string& plain_json);
};
```

- [ ] **Step 3: Implement HTTP client contract**

```cpp
class AiosHttpClient {
public:
    bool Initialize();
    bool RegisterIfNeeded();
    bool Auth();
    bool Sync();
    const AiosCredentials& credentials() const { return credentials_; }
private:
    AiosCredentials credentials_;
};
```

- [ ] **Step 4: Wire bootstrap into `Application::ActivationTask()`**

```cpp
aios_http_client_ = std::make_unique<aios::AiosHttpClient>();
if (!aios_http_client_->Initialize()) {
    last_error_message_ = "AIOS HTTP init failed";
    xEventGroupSetBits(event_group_, MAIN_EVENT_ERROR);
    return;
}
if (!aios_http_client_->RegisterIfNeeded() || !aios_http_client_->Auth()) {
    last_error_message_ = "AIOS auth failed";
    xEventGroupSetBits(event_group_, MAIN_EVENT_ERROR);
    return;
}
```

- [ ] **Step 5: Build and run a bootstrap-only smoke test**

Run: `idf.py -DIDF_TARGET=esp32s3 -DBOARD_NAME=esp-box-3 -DBOARD_TYPE=esp-box-3 build`
Expected: PASS

Run: `python3 tools/aios/monitor_and_assert.py --log build/bootstrap.log --must-contain "AIOS auth success"`
Expected: currently FAIL until the device is flashed and logs are captured.

- [ ] **Step 6: Commit**

```bash
git add main/aios/aios_crypto.h main/aios/aios_crypto.cc main/aios/aios_http_client.h main/aios/aios_http_client.cc main/application.cc
git commit -m "feat: add AIOS HTTP bootstrap"
```

## Task 4: Implement AIOS WebSocket Session Bring-Up

**Files:**
- Create: `main/aios/aios_ws_client.h`
- Create: `main/aios/aios_ws_client.cc`
- Modify: `main/application.cc`
- Modify: `main/aios/aios_runtime_metrics.cc`
- Test: `tools/aios/monitor_and_assert.py`

- [ ] **Step 1: Create a failing compile by requiring `Connect()` and `SendDeviceProfileReport()`**

```cpp
aios_ws_client_->Connect(aios_http_client_->credentials().ws_url);
aios_ws_client_->SendDeviceProfileReport();
```

Run: `idf.py -DIDF_TARGET=esp32s3 -DBOARD_NAME=esp-box-3 -DBOARD_TYPE=esp-box-3 build`
Expected: FAIL with missing websocket client symbols.

- [ ] **Step 2: Implement websocket client interface**

```cpp
class AiosWsClient {
public:
    bool Initialize(const AiosCredentials& credentials);
    bool Connect(const std::string& url);
    bool SendJson(const std::string& json);
    bool SendBinary(const uint8_t* data, size_t size);
    bool SendDeviceProfileReport();
    bool SendUpStreamStart();
    bool SendUpStreamStop();
};
```

- [ ] **Step 3: Add AIOS headers and `session.connected` handling**

```cpp
websocket_->SetHeader("X-Device-Id", credentials.device_user_id.c_str());
websocket_->SetHeader("Authorization", ("Bearer " + credentials.token).c_str());
websocket_->SetHeader("X-AIOS-Version", CONFIG_AIOS_WS_PROTOCOL_VERSION);
```

```cpp
if (event_type == aios::kEventSessionConnected) {
    journal_.Push("session.connected", "AIOS websocket ready");
    metrics_.SetSessionConnected(true);
    SendDeviceProfileReport();
}
```

- [ ] **Step 4: Integrate websocket connect after auth**

```cpp
aios_ws_client_ = std::make_unique<aios::AiosWsClient>();
if (!aios_ws_client_->Initialize(aios_http_client_->credentials())) {
    last_error_message_ = "AIOS websocket init failed";
    xEventGroupSetBits(event_group_, MAIN_EVENT_ERROR);
    return;
}
if (!aios_ws_client_->Connect(aios_http_client_->credentials().ws_url)) {
    last_error_message_ = "AIOS websocket connect failed";
    xEventGroupSetBits(event_group_, MAIN_EVENT_ERROR);
    return;
}
```

- [ ] **Step 5: Run build and live session smoke**

Run: `idf.py -DIDF_TARGET=esp32s3 -DBOARD_NAME=esp-box-3 -DBOARD_TYPE=esp-box-3 build`
Expected: PASS

Run: `python3 tools/aios/monitor_and_assert.py --log build/session.log --must-contain "session.connected" --must-contain "device.profile.report sent"`
Expected: FAIL until logs are captured from a flashed device.

- [ ] **Step 6: Commit**

```bash
git add main/aios/aios_ws_client.h main/aios/aios_ws_client.cc main/application.cc main/aios/aios_runtime_metrics.cc
git commit -m "feat: add AIOS websocket session bring-up"
```

## Task 5: Implement AIOS Conversation Manager for Uplink Audio

**Files:**
- Create: `main/aios/aios_conversation_manager.h`
- Create: `main/aios/aios_conversation_manager.cc`
- Modify: `main/application.cc`
- Modify: `main/audio/audio_service.h`
- Modify: `main/audio/audio_service.cc`
- Test: `tools/aios/monitor_and_assert.py`

- [ ] **Step 1: Create a failing compile by routing send-queue audio into the AIOS conversation manager**

```cpp
while (auto packet = audio_service_.PopPacketFromSendQueue()) {
    aios_conversation_manager_->SendAudioPacket(std::move(packet));
}
```

Run: `idf.py -DIDF_TARGET=esp32s3 -DBOARD_NAME=esp-box-3 -DBOARD_TYPE=esp-box-3 build`
Expected: FAIL because `AiosConversationManager` is not implemented yet.

- [ ] **Step 2: Implement the conversation manager interface**

```cpp
class AiosConversationManager {
public:
    void StartListening();
    void StopListening();
    bool SendAudioPacket(std::unique_ptr<AudioStreamPacket> packet);
    void OnJsonEvent(const cJSON* root);
};
```

- [ ] **Step 3: Add queue-depth accessors and playback clear API to `AudioService`**

```cpp
size_t GetSendQueueDepth() const;
size_t GetDecodeQueueDepth() const;
size_t GetPlaybackQueueDepth() const;
void ClearPlaybackQueues();
```

- [ ] **Step 4: Implement AIOS uplink framing**

```cpp
void AiosConversationManager::StartListening() {
    if (!upstream_open_) {
        ws_client_->SendUpStreamStart();
        upstream_open_ = true;
    }
}

bool AiosConversationManager::SendAudioPacket(std::unique_ptr<AudioStreamPacket> packet) {
    if (!upstream_open_) {
        StartListening();
    }
    return ws_client_->SendBinary(packet->payload.data(), packet->payload.size());
}
```

- [ ] **Step 5: Build and flash for first audio uplink smoke**

Run: `idf.py -DIDF_TARGET=esp32s3 -DBOARD_NAME=esp-box-3 -DBOARD_TYPE=esp-box-3 build`
Expected: PASS

Run: `python3 tools/aios/monitor_and_assert.py --log build/uplink.log --must-contain "up_stream.start sent"`
Expected: FAIL before flashing; PASS after speaking into the device during live smoke.

- [ ] **Step 6: Commit**

```bash
git add main/aios/aios_conversation_manager.h main/aios/aios_conversation_manager.cc main/application.cc main/audio/audio_service.h main/audio/audio_service.cc
git commit -m "feat: add AIOS uplink conversation flow"
```

## Task 6: Implement Downstream AIOS Events, TTS Playback, and Interrupt

**Files:**
- Modify: `main/aios/aios_conversation_manager.cc`
- Modify: `main/application.cc`
- Modify: `main/audio/audio_service.h`
- Modify: `main/audio/audio_service.cc`
- Test: `tools/aios/monitor_and_assert.py`

- [ ] **Step 1: Add a failing log assertion for downstream flow**

Run: `python3 tools/aios/monitor_and_assert.py --log build/downstream.log --must-contain "asr.text.completed" --must-contain "tts playback started" --must-contain "conversation.completed"`
Expected: FAIL because downstream event handling has not been implemented yet.

- [ ] **Step 2: Implement JSON event dispatch for ASR, TTS, and completion**

```cpp
if (event_type == aios::kEventConversationStarted) {
    journal_.Push("conversation.started", "turn accepted");
} else if (event_type == "asr.text.completed") {
    display_->SetChatMessage("user", text.c_str());
} else if (event_type == "llm.text.completed") {
    display_->SetChatMessage("assistant", text.c_str());
} else if (event_type == aios::kEventConversationCompleted) {
    app_->SetDeviceState(kDeviceStateIdle);
}
```

- [ ] **Step 3: Implement downstream binary playback**

```cpp
void AiosConversationManager::OnBinaryAudio(const uint8_t* data, size_t size) {
    auto packet = std::make_unique<AudioStreamPacket>();
    packet->sample_rate = 24000;
    packet->frame_duration = 60;
    packet->payload.assign(data, data + size);
    audio_service_->PushPacketToDecodeQueue(std::move(packet));
}
```

- [ ] **Step 4: Implement `turn.interrupt` playback clearing**

```cpp
if (event_type == aios::kEventTurnInterrupt) {
    audio_service_->ClearPlaybackQueues();
    app_->SetDeviceState(kDeviceStateIdle);
    journal_.Push("turn.interrupt", "playback cleared");
}
```

- [ ] **Step 5: Build and run downstream smoke**

Run: `idf.py -DIDF_TARGET=esp32s3 -DBOARD_NAME=esp-box-3 -DBOARD_TYPE=esp-box-3 build`
Expected: PASS

Run: `python3 tools/aios/monitor_and_assert.py --log build/downstream.log --must-contain "asr.text.completed" --must-contain "tts playback started" --must-contain "conversation.completed"`
Expected: PASS during live smoke after a successful full AIOS turn.

- [ ] **Step 6: Commit**

```bash
git add main/aios/aios_conversation_manager.cc main/application.cc main/audio/audio_service.h main/audio/audio_service.cc
git commit -m "feat: add AIOS downstream playback and interrupt"
```

## Task 7: Implement AIOS Tool Execution Bridge

**Files:**
- Create: `main/aios/aios_action_executor.h`
- Create: `main/aios/aios_action_executor.cc`
- Modify: `main/aios/aios_conversation_manager.cc`
- Modify: `main/application.cc`
- Test: `docs/superpowers/checklists/aios-live-smoke.md`

- [ ] **Step 1: Add a failing compile by requiring action execution from `tool.execute.request`**

```cpp
action_executor_->Execute(target, action, payload);
```

Run: `idf.py -DIDF_TARGET=esp32s3 -DBOARD_NAME=esp-box-3 -DBOARD_TYPE=esp-box-3 build`
Expected: FAIL because the action executor is missing.

- [ ] **Step 2: Implement a serial executor contract**

```cpp
class AiosActionExecutor {
public:
    bool IsBusy() const;
    bool Execute(const std::string& target, const std::string& action, const cJSON* payload, std::string& error);
};
```

- [ ] **Step 3: Add busy handling in conversation manager**

```cpp
if (action_executor_->IsBusy()) {
    SendToolExecuteFailed(cmd_id, "busy");
    return;
}
```

- [ ] **Step 4: Bridge one internal capability first**

```cpp
if (target == "iot.light" && action == "set_power") {
    return lamp_controller_->SetPower(cJSON_IsString(state) && strcmp(state->valuestring, "on") == 0);
}
```

- [ ] **Step 5: Build and perform a single-action live smoke**

Run: `idf.py -DIDF_TARGET=esp32s3 -DBOARD_NAME=esp-box-3 -DBOARD_TYPE=esp-box-3 build`
Expected: PASS

Run: follow `docs/superpowers/checklists/aios-live-smoke.md` and trigger one `tool.execute.request`
Expected: one `tool.execute.completed` in logs, and one `tool.execute.failed` with `busy` when a second command is injected concurrently.

- [ ] **Step 6: Commit**

```bash
git add main/aios/aios_action_executor.h main/aios/aios_action_executor.cc main/aios/aios_conversation_manager.cc main/application.cc docs/superpowers/checklists/aios-live-smoke.md
git commit -m "feat: add AIOS tool execution bridge"
```

## Task 8: Build the Automated Development/Build/Flash/Test Loop

**Files:**
- Create: `tools/aios/dev_env.sh`
- Create: `tools/aios/build_firmware.sh`
- Create: `tools/aios/flash_firmware.sh`
- Create: `tools/aios/monitor_and_assert.py`
- Create: `tools/aios/run_live_smoke.sh`
- Create: `tools/aios/README.md`
- Test: `tools/aios/run_live_smoke.sh`

- [ ] **Step 1: Write the failing serial assertion tool**

```python
required = ["AIOS auth success", "session.connected", "device.profile.report sent"]
for item in required:
    assert item in log_text, f"missing required log: {item}"
```

Run: `python3 tools/aios/monitor_and_assert.py --log /tmp/empty.log --must-contain "session.connected"`
Expected: FAIL with `missing required log: session.connected`

- [ ] **Step 2: Add shared environment loader**

```bash
#!/usr/bin/env bash
set -euo pipefail

export BOARD_NAME="${BOARD_NAME:-esp-box-3}"
export BOARD_TYPE="${BOARD_TYPE:-esp-box-3}"
export ESPPORT="${ESPPORT:-/dev/ttyACM0}"
export LOG_DIR="${LOG_DIR:-$(pwd)/build/aios-logs}"
mkdir -p "$LOG_DIR"
```

- [ ] **Step 3: Add build and flash scripts**

```bash
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/dev_env.sh"
idf.py -DIDF_TARGET="${IDF_TARGET:-esp32s3}" -DBOARD_NAME="$BOARD_NAME" -DBOARD_TYPE="$BOARD_TYPE" build
```

```bash
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/dev_env.sh"
idf.py -p "$ESPPORT" flash
```

- [ ] **Step 4: Add serial monitor and assertion script**

```python
import argparse
import pathlib
import serial
import time

def capture_log(port: str, seconds: int, output: pathlib.Path) -> str:
    with serial.Serial(port, 115200, timeout=0.2) as ser:
        deadline = time.time() + seconds
        chunks = []
        while time.time() < deadline:
            chunks.append(ser.read(4096).decode(errors="ignore"))
        text = "".join(chunks)
        output.write_text(text)
        return text
```

- [ ] **Step 5: Add one-command live smoke runner**

```bash
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/dev_env.sh"
"$(dirname "$0")/build_firmware.sh"
"$(dirname "$0")/flash_firmware.sh"
python3 "$(dirname "$0")/monitor_and_assert.py" \
  --port "$ESPPORT" \
  --seconds 40 \
  --log "$LOG_DIR/live-smoke.log" \
  --must-contain "AIOS auth success" \
  --must-contain "session.connected" \
  --must-contain "device.profile.report sent"
```

- [ ] **Step 6: Run the full automation loop**

Run: `bash tools/aios/run_live_smoke.sh`
Expected:

```text
[1/3] build ok
[2/3] flash ok
[3/3] smoke ok
log saved to build/aios-logs/live-smoke.log
```

- [ ] **Step 7: Commit**

```bash
git add tools/aios/dev_env.sh tools/aios/build_firmware.sh tools/aios/flash_firmware.sh tools/aios/monitor_and_assert.py tools/aios/run_live_smoke.sh tools/aios/README.md
git commit -m "tools: add AIOS live smoke automation loop"
```

## Task 9: Add Final Runtime Observability and AIOS State Update

**Files:**
- Modify: `main/aios/aios_runtime_metrics.cc`
- Modify: `main/aios/aios_ws_client.cc`
- Modify: `main/application.cc`
- Modify: `main/system_info.cc`
- Test: `tools/aios/run_live_smoke.sh`

- [ ] **Step 1: Add a failing log assertion for runtime snapshots**

Run: `python3 tools/aios/monitor_and_assert.py --log /tmp/runtime.log --must-contain "runtime snapshot"`
Expected: FAIL until snapshot logging is implemented.

- [ ] **Step 2: Implement snapshot emission**

```cpp
ESP_LOGI("AIOSMetrics",
         "runtime snapshot free_heap=%u min_free_heap=%u ws=%d session=%d send_q=%d decode_q=%d playback_q=%d state=%s",
         snapshot.free_heap,
         snapshot.min_free_heap,
         snapshot.websocket_connected,
         snapshot.session_connected,
         snapshot.audio_send_queue_depth,
         snapshot.audio_decode_queue_depth,
         snapshot.audio_playback_queue_depth,
         snapshot.device_state.c_str());
```

- [ ] **Step 3: Implement `device.state.update` emission**

```cpp
cJSON* root = cJSON_CreateObject();
cJSON_AddStringToObject(root, "event_type", aios::kEventDeviceStateUpdate);
cJSON_AddNumberToObject(root, "timestamp", time(nullptr));
// populate data with heap, state, battery, queue depth
```

- [ ] **Step 4: Schedule periodic metrics reporting from `Application`**

```cpp
if (clock_ticks_ % 10 == 0) {
    aios_runtime_metrics_->PublishSnapshot();
}
```

- [ ] **Step 5: Run the full live smoke again**

Run: `bash tools/aios/run_live_smoke.sh`
Expected:

```text
[1/3] build ok
[2/3] flash ok
[3/3] smoke ok
runtime snapshot observed
```

- [ ] **Step 6: Commit**

```bash
git add main/aios/aios_runtime_metrics.cc main/aios/aios_ws_client.cc main/application.cc main/system_info.cc
git commit -m "feat: add AIOS runtime observability"
```

## Spec Coverage Check

- AIOS HTTP bootstrap: covered by Task 3
- AIOS websocket and `session.connected`: covered by Task 4
- `device.profile.report`: covered by Task 4
- upstream audio and `up_stream.start/stop`: covered by Task 5
- downstream ASR/TTS and conversation completion: covered by Task 6
- `turn.interrupt`: covered by Task 6
- `tool.execute.request`: covered by Task 7
- observability, state reporting, long-run readiness: covered by Task 2 and Task 9
- automated development/build/flash/test closed loop: covered by Task 8

## Placeholder Scan

This plan intentionally avoids:

- `TODO` / `TBD`
- unspecified file paths
- unspecified commands
- unnamed tests

The only variable surface kept is the board and serial port environment, and those are concretely defined in `tools/aios/dev_env.sh`.

## Type Consistency Check

Planned primary types and responsibilities remain consistent across tasks:

- `AiosHttpClient`
- `AiosWsClient`
- `AiosConversationManager`
- `AiosActionExecutor`
- `AiosRuntimeSnapshot`
- `AiosJournalEvent`

No later task renames these units.
