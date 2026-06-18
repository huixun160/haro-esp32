# TM02 Module Inventory — James Legacy

**Author:** KaiwenZheng | **Project:** demo_merge | **Date:** 2026-03-26

---

## A — UI 层 (LVGL)

| 模块 | 路径 | 大小 | 功能 | 稳定性 | 需要 merge |
|------|------|------|------|--------|-----------|
| LVGL 9.5.0 | `Third-party/lvgl-9.5.0/` | 大 | LVGL 核心运行时 | ✅ 稳定 | ✅ |
| LVGL Build | `make/lvgl/lvgl.mk` | 10KB | LVGL 编译集成 | ✅ | ✅ |
| LVGL Bridge | `platform/unisoc/` 中相关 | — | LVGL→平台桥接 | ✅ | ✅ |

## B — 应用层 (DAP Apps)

| 模块 | 路径 | 大小 | 功能 | 稳定性 | 需要 merge |
|------|------|------|------|--------|-----------|
| palm_menu | `apps/palm_menu/` | 64KB | PalmOS 风格启动器 | ✅ | ✅ |
| snake | `apps/snake/` | — | 贪吃蛇游戏 | ✅ | ✅ |
| tetris | `apps/tetris/` | — | 俄罗斯方块 | ✅ | ✅ |
| voice_chat | `apps/voice_chat/` | — | 语音助手 | ⚠️ 有 bug | ✅ (不修 bug) |
| voice_recorder | `apps/voice_recorder/` | — | 录音机 | ⚠️ | ✅ |
| mp3_player | `apps/mp3_player/` | — | MP3 播放器 | ⚠️ | ✅ |
| notepad | `apps/notepad/` | — | 记事本 | ⚠️ | ✅ |
| demo_ui | `apps/demo_ui/` | — | UI 演示 | ✅ | ✅ |
| hello_lvgl | `apps/hello_lvgl/` | — | LVGL Hello World | ✅ | ✅ |
| lvgl_template | `apps/lvgl_template/` | — | LVGL 模板 | ✅ | ✅ |
| hello_bigseek | `apps/hello_bigseek/` | — | BigSeek Demo | ✅ | ✅ (已有) |

## C — 分发系统 (Download)

| 模块 | 路径 | 大小 | 功能 | 稳定性 | 需要 merge |
|------|------|------|------|--------|-----------|
| Download_Bin (App) | `apps/Download_Bin/` | ~300KB | BIN 下载管理器 App | ⚠️ | ✅ |
| Downloader (Platform) | `platform/unisoc/DAP_Downloader.*` | ~113KB | 下载引擎 (HTTP) | ⚠️ | ✅ |
| DownloaderForm | `platform/unisoc/DAP_DownloaderForm.c` | 45KB | 下载 UI | ⚠️ | ✅ |
| DL_InstallDownloaderAPI | `platform/unisoc/DL_Install*.c` | 13KB | 下载器 API 注入 | ⚠️ | ✅ |

## D — 系统适配层 (Platform)

| 模块 | 路径 | 大小 | 功能 | 稳定性 | 需要 merge |
|------|------|------|------|--------|-----------|
| DAP_UNISOC_OSAssociated | `platform/unisoc/` | **632KB** | 超大平台适配 | ⚠️ | ⚠️ 需审查 |
| DAP_OSAssociated_unisoc | `platform/unisoc/` | 25KB | 平台桥接 | ✅ | ⚠️ 需比对 |
| DAP_InstallOSAPI | `platform/unisoc/` | 26KB | API 注入 | ✅ | ⚠️ 需比对 |
| dap_audio_bridge | `platform/unisoc/` | **60KB** | 音频完整桥接 | ⚠️ | ✅ |
| dap_t9_engine | `platform/unisoc/` | 34KB | T9 输入法引擎 | ✅ | ✅ |
| dap_va_bridge | `platform/unisoc/` | 9KB | VA 语音桥接 | ⚠️ | ✅ |
| dap_gui_unisoc | `platform/unisoc/` | 19KB | GUI 桥接 | ✅ | ⚠️ 需比对 |
| DAP_DebugLog | `platform/unisoc/` | 11KB | 日志 | ✅ | ⚠️ 需比对 |

## E — DAP Core

| 模块 | 路径 | 大小 | 功能 | 稳定性 | 需要 merge |
|------|------|------|------|--------|-----------|
| DAP_Loader | `core/DAP_Loader.c` | 27KB | 加载器 | ✅ James 版 | ❌ **禁止** |
| DAP_Register | `core/DAP_Register.c` | 29KB | API 注册 | ✅ James 版 | ❌ **禁止** |
| DAP_Application.h | `core/` | 5KB | 应用头 | — | ❌ |

## F — SDK

| 模块 | 路径 | 大小 | 功能 | 稳定性 | 需要 merge |
|------|------|------|------|--------|-----------|
| lvgl_api.h | `sdk/` | 11KB | LVGL API 声明 | ✅ | ✅ |
| dap_audio_api.h | `sdk/` | 4KB | 音频 API | ✅ | ✅ |
| dap_va_api.h | `sdk/` | 4KB | VA API | ✅ | ✅ |
| dap_t9_api.h | `sdk/` | 3KB | T9 API | ✅ | ✅ |
| DAP_Downloader.c | `sdk/` | **480KB** | SDK 级下载器 | ⚠️ | ⚠️ |
| OSAPILists.h | `sdk/` | 5KB | 旧 API 结构 | Legacy | ⚠️ |
| Entry.c / Start.s | `sdk/` | 10KB/5KB | BIN 入口 | ✅ | ⚠️ 需比对 |

## G — 文档 (DOCS-main)

| 模块 | 路径 | 功能 | 需要 merge |
|------|------|------|-----------|
| AI执行方案/ | `DOCS-main/` | LVGL/语音助手开发文档 | ❌ 参考用 |
| Bigseek协议/ | `DOCS-main/` | 协议文档 | ❌ 参考用 |
| DAP参考文档/ | `DOCS-main/` | DAP 开发指南 | ❌ 参考用 |
| NBS Technical Memo/ | 根目录 | James 技术备忘录 | ❌ 参考用 |
