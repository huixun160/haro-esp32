# TM-029-1 — 依赖映射图 (Dependency Map)

**Date:** 2026-03-15

---

## 分层架构

```
┌─────────────────────────────────────────────────────┐
│  Level A: APP 自身资产                                │
│  voice_chat/Main.c (LVGL UI + PTT)                  │
│  build.bat (ARM ADS 1.2)                            │
├─────────────────────────────────────────────────────┤
│  Level B-1: DAP SDK API (FindInterface 动态链接)      │
│  dap_va_api.h → 9 VA functions                      │
│  lvgl_api.h   → LVGL widget API                     │
│  dap_audio_api.h → Volume API                       │
├─────────────────────────────────────────────────────┤
│  Level B-2: DAP 宿主端实现 (编入固件)                  │
│  dap_va_bridge.c/h → VA API 桥接到 bigseek_core     │
│  dap_audio_bridge.c/h → 录音+播放+音量               │
│  DAP_InstallOSAPI_unisoc.c → FindInterface 注册      │
├─────────────────────────────────────────────────────┤
│  Level B-3: bigseek_core (语音助手引擎)               │
│  14 源码: ws_client, http, token, record,            │
│           pcm_stream, aios_protocol, network, ...    │
├─────────────────────────────────────────────────────┤
│  Level C: 系统级公共依赖                               │
│  curl (HTTP), libwebsockets (WS+cJSON),              │
│  mbedtls (TLS), ssv_wifi (WiFi),                     │
│  lvgl-9.5.0 (UI), external/libc,                    │
│  DAPS/tcpip (TCP/IP stack)                           │
└─────────────────────────────────────────────────────┘
```

---

## voice_chat APP 的 API 调用链

```
voice_chat/Main.c
 ├── FindInterface("DAP_VA_Init", CMD)        → dap_va_bridge.c → bs_task.c
 ├── FindInterface("DAP_VA_Close", CMD)       → dap_va_bridge.c → bs_task.c
 ├── FindInterface("DAP_VA_StartRecord", CMD) → dap_va_bridge.c → bs_record.c
 ├── FindInterface("DAP_VA_StopRecord", CMD)  → dap_va_bridge.c → bs_record.c
 ├── FindInterface("DAP_VA_GetStatus", CMD)   → dap_va_bridge.c → bs_task.c
 ├── FindInterface("DAP_VA_GetAsrText", CMD)  → dap_va_bridge.c → bs_text_buffer.c
 ├── FindInterface("DAP_VA_GetLlmText", CMD)  → dap_va_bridge.c → bs_text_buffer.c
 ├── FindInterface("DAP_VA_ClearText", CMD)   → dap_va_bridge.c → bs_text_buffer.c
 ├── FindInterface("DAP_VA_GetNetType", CMD)  → dap_va_bridge.c → bs_network.c
 ├── FindInterface("DAP_AudioSetStreamVolume") → dap_audio_bridge.c
 ├── FindInterface("DAP_AudioGetStreamVolume") → dap_audio_bridge.c
 ├── FindInterface("DAP_LVGL_OpenWindow")     → dap_gui_unisoc.c / lvgl integration
 ├── FindInterface("lv_screen_active")        → lvgl-9.5.0
 ├── FindInterface("lv_label_create")         → lvgl-9.5.0
 ├── FindInterface("lv_label_set_text")       → lvgl-9.5.0
 ├── FindInterface("lv_obj_align")            → lvgl-9.5.0
 ├── FindInterface("lv_obj_set_size")         → lvgl-9.5.0
 ├── FindInterface("lv_obj_set_style_*")      → lvgl-9.5.0
 ├── FindInterface("dap_font_get_builtin")    → LVGL CJK font integration
 └── FindInterface("DAP_LVGL_SetKeyCallback") → key event dispatch
```

---

## bigseek_core 内部依赖链

```
bs_task.c (主控)
 ├── bs_token.c   → bs_http.c  → curl + mbedtls
 ├── bs_ws.c      → bs_ws_client.c → libwebsockets
 ├── bs_ws_hooks.c (WS 事件分发)
 ├── bs_aios_protocol.c → cJSON (JSON 解析)
 ├── bs_record.c  → dap_audio_bridge.c (PCM 采集)
 ├── bs_pcm_stream.c (PCM → WS 流传输)
 ├── bs_text_buffer.c (ASR/LLM 文本缓冲)
 ├── bs_network.c → bs_pdp_platform.c (PDP/WiFi 管理)
 ├── bs_balance.c → bs_http.c
 └── bs_utils.c
```

---

## 构建标志依赖

| Flag | 说明 | 影响范围 |
|------|------|---------|
| `BIGSEEK_CORE_SUPPORT=TRUE` | 启用 bigseek_core 编译 | dap.mk 条件编译块 |
| `FUTURE_LIBWEBSOCKET_SUPPORT=TRUE` | 启用 libwebsockets include | dap.mk 内层条件 |
| `IPVERSION_SUPPORT=V4_V6` | TCP/IP 栈版本 | tcpip6 vs tcpip |
| `MBEDTLS_VERSION=V206/V224` | mbedTLS 版本选择 | include path |
| `ENABLE_DAP` | DAP 总开关 | 已存在 |
