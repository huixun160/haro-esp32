# TM02 Merge Plan — James Legacy → Secure Mainline

**Author:** KaiwenZheng | **Project:** demo_merge | **Date:** 2026-03-26

---

## 核心原则

> **把 James 的能力"嫁接"到我们的结构上，不是融合两个系统。**

- 我们的 DAP Core（Loader + InterfaceRegister + Security）**绝对不动**
- James 的 App / Bridge / LVGL **选择性移植**
- 新增 API 注册到我们的 `DAP_InterfaceRegister.c`，而非覆盖为 `DAP_Register.c`

---

## ✅ 可以 Merge

### Tier 1: LVGL Runtime（最高优先级）
| 模块 | Merge 方式 | 风险 |
|------|-----------|------|
| `Third-party/lvgl-9.5.0/` | 整目录拷入 | 🟢 低 — 独立编译单元 |
| `make/lvgl/lvgl.mk` | 拷入 + 适配 dap.mk | 🟢 低 |
| `sdk/lvgl_api.h` | 拷入 SDK 目录 | 🟢 低 |

### Tier 2: Bridge 层（需审查后 merge）
| 模块 | Merge 方式 | 风险 |
|------|-----------|------|
| `dap_audio_bridge.c/h` (60KB) | **对比后合并** — 主线已有 28KB 版本 | 🟡 中 — 是超集 |
| `dap_gui_unisoc.c/h` | 对比后合并 | 🟡 中 |
| `dap_t9_engine.c/h` + `dap_t9_dict.c` | 新增拷入 | 🟢 低 — 全新模块 |
| `dap_va_bridge.c/h` | 新增拷入 | 🟢 低 — 全新模块 |
| `DL_InstallDownloaderAPI.c` | 新增拷入 | 🟡 中 |

### Tier 3: Apps（编译为 BIN，风险最低）
| 模块 | Merge 方式 | 风险 |
|------|-----------|------|
| `apps/palm_menu/` | 拷入 + 编译 BIN | 🟢 低 — 独立 app |
| `apps/snake/` | 拷入 + 编译 BIN | 🟢 低 |
| `apps/tetris/` | 拷入 + 编译 BIN | 🟢 低 |
| `apps/voice_chat/` | 拷入 + 编译 BIN（不修 bug） | 🟡 中 |
| `apps/voice_recorder/` | 拷入 + 编译 BIN | 🟢 低 |
| `apps/mp3_player/` | 拷入 + 编译 BIN | 🟢 低 |
| `apps/notepad/` | 拷入 + 编译 BIN | 🟢 低 |
| `apps/demo_ui/` | 拷入 + 编译 BIN | 🟢 低 |
| `apps/Download_Bin/` | 拷入 + 编译 BIN | 🟡 中 — 依赖 Downloader API |

### Tier 4: SDK 扩展
| 模块 | Merge 方式 | 风险 |
|------|-----------|------|
| `sdk/dap_audio_api.h` | 拷入 | 🟢 低 |
| `sdk/dap_va_api.h` | 拷入 | 🟢 低 |
| `sdk/dap_t9_api.h` | 拷入 | 🟢 低 |

---

## ❌ 禁止 Merge

| 模块 | 原因 |
|------|------|
| `core/DAP_Loader.c` | **我们的 Loader 已含 BIN2/BIN3 安全逻辑** — James 版本无安全特性 |
| `core/DAP_Register.c` | 我们已重构为 `DAP_InterfaceRegister.c` + ID 化 |
| `core/DAP_Application.h` | 两边相同，但以我们版本为准 |
| `platform/unisoc/DAP_UNISOC_OSAssociated.c` (632KB) | 超大文件，结构不稳定，不可盲目替换 |
| `platform/unisoc/DAP_OSAssociated_unisoc.c` | 我们的版本含 trace 混淆 + security 修改 |
| `platform/unisoc/DAP_InstallOSAPI_unisoc.c` | 我们的版本含 ID 化注册 |
| `sdk/OSAPILists.h/c` | Legacy 结构，不兼容我们的 SDK 架构 |
| `sdk/Entry.c` / `sdk/Start.s` | 我们的版本含安全入口 + ABI v0 |
| `agit/` | James 私有 git 数据 |
| `DOCS-main/` | 纯文档参考 |
| `NBS Technical Memo/` | James 专有 memo |
| 所有 BSP 基础目录 | 以我们的版本为准 |

---

## ⚠️ 需对比后决定

| 模块 | 对比内容 | 决策条件 |
|------|----------|----------|
| `platform/unisoc/DAP_FMM_Integration.c` | James 是否修改了文件管理入口 | 如有新入口点→merge |
| `platform/unisoc/DAP_DebugLog.c/h` | James 是否扩展了日志 | 如有有价值的功能→merge |
| `platform/unisoc/DAP_Downloader.c/h` (platform) | 下载功能 vs 安全风险 | 新增文件→merge，修改文件→审查 |
| `platform/unisoc/dap_unisoc_shim.h` | 是否含我们缺少的平台适配 | 按需 |
| `project_*.mk` 文件 | 编译配置差异 | 提取 James 新增编译目标 |

---

## Merge 执行顺序建议

1. **TM-03: LVGL Runtime 移植**（Tier 1）— 风险最低，价值最高
2. **TM-04: Bridge 层选择性合并**（Tier 2）— 需文件级 diff
3. **TM-05: App 移植 + 编译验证**（Tier 3）— 编译为 BIN 后烧录测试
4. **TM-06: API 注册同步**（跨 Tier）— 在 `DAP_InterfaceRegister.c` 中注册 James 新增 API
5. **TM-07: Download_Bin 集成**（Tier 3 + Tier 2）— 最复杂，最后做

---

## 安全约束

- 所有 merge 后的 BIN 文件必须通过 **BIN2 签名 + BIN3 加密** 链路
- 新增 API 必须同时在 `dap_interface_id.h` 中分配 ID（EXTERNAL_BUILD）
- 对外输出版本必须经过 `export_zkw_output.py` 安全扫描
- Voice Assistant 合并后不修 bug，标注 known issue
