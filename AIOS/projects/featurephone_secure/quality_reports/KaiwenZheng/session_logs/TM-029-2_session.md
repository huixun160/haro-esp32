# Session Log — TM-029-2: Voice Assistant Asset Migration

**Date:** 2026-03-15
**Memo:** Technical_Memo_29-2 — Voice Assistant Asset Migration, Build, and Initial BIN Validation
**Engineer:** KaiwenZheng
**Outcome:** SUCCESS

---

## Summary

按 TM29-1 白名单将语音助手 APP 资产迁入可信主线，完成固件编译和设备验证。

## Timeline

| 时间 | 动作 |
|------|------|
| 20:06 | 开始执行 TM29-2 |
| 20:07 | Step 1-2: 复制新文件 + 替换 dap_audio_bridge.c/h |
| 20:09 | Step 3: 手动合并 DAP_InstallOSAPI_unisoc.c (+Install_VA_API) |
| 20:09 | Step 3: 比对 SDK 文件，仅 lvgl_api.h 有差异 (+151B PTT callback) |
| 20:10 | Step 4: 手动合并 dap.mk (+55 行 BIGSEEK_CORE_SUPPORT 块) |
| 20:11 | 添加 BIGSEEK_CORE_SUPPORT=TRUE 到 project_*.mk |
| 20:17 | 用户确认 PAC 编译通过，已烧录 |
| 20:25 | voice_chat.bin 编译成功 (修复 ARM ADS PATH) |
| 21:25 | 设备验证：APP 加载成功，VA API 注册，WebSocket 连通 |
| 21:41 | DSP 蓝屏问题分析：录音格式不兼容 |
| 21:51 | 修改 BS_AUDIO_USE_AMR=1，等待用户重编译验证 |

## 迁移清单

### 直接复制
- `Third-party/DAP/apps/voice_chat/` (Main.c + build.bat)
- `Third-party/bigseek_core/` (18 files)
- `Third-party/DAP/platform/unisoc/dap_va_bridge.c/h`
- `Third-party/DAP/sdk/dap_va_api.h`

### 直接替换
- `dap_audio_bridge.c` (28→60KB, 纯追加超集)
- `dap_audio_bridge.h` (8.9→11KB)
- `lvgl_api.h` (8.9→9.1KB, PTT callback)

### 手动合并
- `DAP_InstallOSAPI_unisoc.c`: +include, +Install_VA_API()
- `dap.mk`: +55 行 BIGSEEK_CORE_SUPPORT 块 (TM28-R 安全入口保留)
- `project_*.mk`: +BIGSEEK_CORE_SUPPORT=TRUE

### 未触碰 (黑名单)
- `DAP/security/*` ✅
- `DAP_Loader_unisoc.c` ✅
- `bin2_*`, `dap_aes.*`, `device_*` ✅

## 设备验证结果

| 项目 | 状态 |
|------|------|
| DAP API 注册 | ✅ 全部成功 |
| VA API 注册 | ✅ 9 个 API |
| APP 加载 | ✅ volume set to 9 |
| Token 认证 | ✅ auth ok |
| WebSocket 连接 | ✅ connected (retry 后) |
| 会话建立 | ✅ session.connected + conversation_started |
| 录音(语音键) | ❌ DSP assert (已切换 AMR 模式待验证) |
| 字库 | ❌ CJK 字体缺失 (待 James git 参考) |

## 遗留问题 (→ TM29-3)

1. DSP 蓝屏: 已改 `BS_AUDIO_USE_AMR=1`, 需重编译验证
2. SSL 握手间歇失败: mbedTLS 配置需参考 James git
3. CJK 字库: LVGL 字体资源配置
