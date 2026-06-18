# TM-029-1 — 语音助手资产清单 (Asset Inventory)

**Date:** 2026-03-15
**Source:** `zkwwork_contaminated_snapshot/`

---

## 1. APP 层 — `Third-party/DAP/apps/voice_chat/`

| 文件 | 大小 | 说明 |
|------|------|------|
| `Main.c` | 19,757B | 语音助手 LVGL UI + PTT 逻辑 (477 行) |
| `build.bat` | 3,893B | ARM ADS 1.2 构建脚本 → .bin |

> **新增** — 主线 `DAP/apps/` 有 9 个 APP 目录，无 `voice_chat`

---

## 2. SDK 层 — `Third-party/DAP/sdk/`

| 文件 | 大小 | 说明 | 主线有？ |
|------|------|------|---------|
| `dap_va_api.h` | 3,573B | VA API 函数指针声明 (9 个) | ❌ 新增 |
| `dap_audio_api.h` | 3,710B | 音频 API 类型声明 | 需比对 |
| `lvgl_api.h` | 9,104B | LVGL API 函数指针声明 | 需比对 |
| `Entry.c` | 9,809B | APP 入口（链接器入口） | 需比对 |
| `Main.c` | 4,043B | SDK 主模板 | 需比对 |
| `MainForm.c/h` | 9,692B/1,351B | UI 表单模板 | 需比对 |
| `OSAPILists.c/h` | 3,652B/5,032B | OS API 列表 | 需比对 |
| `OSInterface.h` | 2,586B | OS 接口头文件 | 需比对 |
| `GlobalDefs.h` | 2,373B | 全局定义 | 需比对 |
| `def.h` | 2,740B | 类型定义 | 需比对 |
| `Start.s` | 1,460B | ARM 汇编启动代码 | 需比对 |
| `GBK_Uncode.c/h` | 430KB/655B | GBK-Unicode 转换表 | 需比对 |
| `format_entry.py` | 10,479B | 入口格式化脚本 | 需比对 |

---

## 3. VA Bridge 层 — `Third-party/DAP/platform/unisoc/` (新增)

| 文件 | 大小 | 说明 | 主线有？ |
|------|------|------|---------|
| `dap_va_bridge.c` | 7,769B | VA API → bigseek_core 桥接 | ❌ 新增 |
| `dap_va_bridge.h` | 993B | VA bridge 头文件 | ❌ 新增 |

---

## 4. BigSeek Core — `Third-party/bigseek_core/` (整目录新增)

### 头文件 (`inc/`)
| 文件 | 大小 | 说明 |
|------|------|------|
| `bs_core_api.h` | 4,319B | BigSeek 公共 API |
| `bs_core_config.h` | 6,612B | 配置 (URL/Token/超时) |
| `bs_core_types.h` | 6,621B | 类型定义 (状态/错误码) |

### 内部头文件 (`internal/`)
| 文件 | 大小 |
|------|------|
| `bs_core_internal.h` | 4,290B |

### 源码 (`src/`, 14 files)
| 文件 | 大小 | 功能 |
|------|------|------|
| `bs_task.c` | 14,367B | 后台任务管理 |
| `bs_ws.c` | 11,056B | WebSocket 会话管理 |
| `bs_ws_client.c` | 27,150B | WS 客户端实现 |
| `bs_ws_hooks.c` | 6,041B | WS 事件钩子 |
| `bs_aios_protocol.c` | 10,608B | AIOS 协议解析 |
| `bs_record.c` | 7,703B | 录音管理 |
| `bs_pcm_stream.c` | 7,712B | PCM 音频流 |
| `bs_http.c` | 28,709B | HTTP 请求 |
| `bs_token.c` | 15,930B | Token 认证 |
| `bs_balance.c` | 3,328B | 余额查询 |
| `bs_text_buffer.c` | 5,776B | 文本缓冲 (ASR/LLM) |
| `bs_network.c` | 8,656B | 网络管理 |
| `bs_pdp_platform.c` | 6,677B | PDP (蜂窝数据) 平台适配 |
| `bs_utils.c` | 5,744B | 工具函数 |

---

## 5. 音频桥 — 已有文件扩展

| 文件 | 主线大小 | 快照大小 | 说明 |
|------|---------|---------|------|
| `dap_audio_bridge.c` | 28,774B | 60,456B | ⚠️ 大量新增 (+31KB, 翻倍) |
| `dap_audio_bridge.h` | 8,946B | 11,188B | ⚠️ 新增 (+2KB) |

---

## 6. 外部库依赖 — `Third-party/`

| 目录 | 新增？ | 说明 |
|------|--------|------|
| `bigseek_core/` | ✅ 新增 | 语音助手核心 |
| `curl/` | 需确认 | HTTP 客户端库 |
| `libwebsockets/` | 需确认 | WebSocket + cJSON |
| `mbedtls/` | 需确认 | TLS 加密 |
| `ssv_wifi/` | 需确认 | WiFi 驱动 |
| `lvgl-9.5.0/` | 需确认 | LVGL UI 库 |

---

## 7. 构建系统差异 — `make/dap/dap.mk`

快照 `dap.mk` 新增（gated by `BIGSEEK_CORE_SUPPORT=TRUE`）：

```makefile
# +flag
MCFLAG_OPT += -DBIGSEEK_CORE_SUPPORT

# +include paths (6 条)
MINCPATH += Third-party/bigseek_core/inc
MINCPATH += Third-party/bigseek_core/internal
MINCPATH += external/libc{,/h,/h/arpa,/h/network,/h/sys}
MINCPATH += DAPS/export/inc/tcpip{,6}
MINCPATH += Third-party/curl/include{/curl,}
MINCPATH += Third-party/mbedtls/V{206,224}/include
MINCPATH += Third-party/libwebsockets/src/json_char/h

# +source path
MSRCPATH += Third-party/bigseek_core/src

# +sources (15 files)
SOURCES += bs_task.c bs_ws.c bs_ws_client.c bs_ws_hooks.c
SOURCES += bs_aios_protocol.c bs_record.c bs_pcm_stream.c
SOURCES += bs_http.c bs_token.c bs_balance.c bs_text_buffer.c
SOURCES += bs_network.c bs_pdp_platform.c bs_utils.c
SOURCES += dap_va_bridge.c

# +cJSON
MSRCPATH += Third-party/libwebsockets/src/json_char/c
SOURCES += cJSON.c
```

---

## 8. .bin 生成链路

```
voice_chat/Main.c
    + sdk/Entry.c + sdk/Start.s
    ↓ armcc (ARM ADS 1.2, CPU=ARM7EJ-S, ROPI/interwork)
    ↓ armlink (-entry Entry, -ro-base 0x00000000, -ropi -rwpi -reloc)
    → voice_chat.axf
    ↓ fromelf -bin
    → voice_chat.bin (初始 BIN1)
    ↓ bin2_pack.py [--bind-file] [--encrypt]
    → voice_chat.bin2 / voice_chat.bin3
```
