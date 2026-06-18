# TM-029-1 — 迁移白名单 / 黑名单 (Migration Whitelist)

**Date:** 2026-03-15

---

## ✅ 白名单 — 可从 contaminated snapshot 迁移

### 直接复制（APP 新增）
| 路径 | 操作 | 说明 |
|------|------|------|
| `Third-party/DAP/apps/voice_chat/` | COPY 整目录 | 语音助手 APP (2 files) |
| `Third-party/bigseek_core/` | COPY 整目录 | BigSeek 引擎 (18 files) |
| `Third-party/DAP/platform/unisoc/dap_va_bridge.c` | COPY | VA API 桥接 |
| `Third-party/DAP/platform/unisoc/dap_va_bridge.h` | COPY | VA bridge 头文件 |
| `Third-party/DAP/sdk/dap_va_api.h` | COPY | VA API 声明 |

### 需比对后决定（SDK 文件）
| 路径 | 操作 | 说明 |
|------|------|------|
| `Third-party/DAP/sdk/dap_audio_api.h` | DIFF → 决定 | 音频 API 可能有新增 |
| `Third-party/DAP/sdk/lvgl_api.h` | DIFF → 决定 | LVGL API 可能有新增 |
| `Third-party/DAP/sdk/Entry.c` | DIFF → 决定 | 入口代码可能有变化 |
| `Third-party/DAP/sdk/` 其余文件 | DIFF → 决定 | 逐文件比对 |

### 需人工合并（⚠️ 最危险）
| 路径 | 操作 | 说明 |
|------|------|------|
| `make/dap/dap.mk` | 🔧 手动合并 | 在已有 TM28-R 基础上添加 BIGSEEK_CORE_SUPPORT 块 |
| `Third-party/DAP/platform/unisoc/dap_audio_bridge.c` | 🔧 手动合并 | +31KB 变化，可能含安全无关的新功能 |
| `Third-party/DAP/platform/unisoc/dap_audio_bridge.h` | 🔧 手动合并 | +2KB 变化 |
| `Third-party/DAP/platform/unisoc/DAP_InstallOSAPI_unisoc.c` | 🔧 手动合并 | VA API 的 FindInterface 注册入口 |

### 外部库（需确认主线是否已有）
| 路径 | 操作 | 说明 |
|------|------|------|
| `Third-party/curl/` | 比对 | HTTP 库 |
| `Third-party/libwebsockets/` | 比对 | WebSocket + cJSON |
| `Third-party/mbedtls/` | 比对 | TLS |
| `Third-party/lvgl-9.5.0/` | 比对 | 主线已有同名目录 |

---

## 🚫 黑名单 — 禁止从 contaminated snapshot 覆盖

| 路径 | 原因 |
|------|------|
| `Third-party/DAP/security/*` | TM28-R 恢复的安全主线 |
| `Third-party/DAP/platform/unisoc/DAP_Loader_unisoc.c` | TM28-R 手动修改（加密 BSS memcpy 等） |
| `Third-party/DAP/platform/unisoc/DAP_FMM_Integration.c` | TM28-R 手动修改（.bin3 扩展名） |
| `Third-party/DAP/security/bin2_format.h` | v3 header (96B) |
| `Third-party/DAP/security/bin2_loader.c` | decrypt + I-cache flush |
| `Third-party/DAP/security/bin2_loader.h` | 动态 offset 声明 |
| `Third-party/DAP/security/bin2_crypto.c` | 动态 header_size |
| `Third-party/DAP/security/bin2_crypto_payload.c/h` | TM-28 payload 解密 |
| `Third-party/DAP/security/dap_aes.c/h` | TM-28 AES |
| `Third-party/DAP/security/device_binding.c` | TM-27 binding |
| `make/dap/dap.mk` | ⚠️ 不能直接覆盖，只能手动合并 |
| `AIOS/*` | 已完整合并，不需要从快照覆盖 |

> **核心原则：** 快照中的 `DAP_Loader_unisoc.c` (26KB) 是旧版，主线的 (34KB) 包含 TM28-R 安全修改——绝对不能被快照覆盖。

---

## 📋 迁移执行摘要

```
直接复制:    5 项 (voice_chat + bigseek_core + va_bridge)
需比对:      ~10 项 (SDK 文件 + 外部库)
需手动合并:  4 项 (dap.mk, audio_bridge, InstallOSAPI)
禁止覆盖:    12+ 项 (安全主线)
```
