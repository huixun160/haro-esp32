# TM02 Core Compatibility Analysis — James vs Mainline

**Author:** KaiwenZheng | **Project:** demo_merge | **Date:** 2026-03-26

> **目的：** 识别 James 的 DAP Core 与我们主线之间的差异，判断哪些差异会导致 James 的 App 无法在我们的系统上运行。

---

## 1. DAP_Register.c (James) vs DAP_InterfaceRegister.c (主线)

### 1.1 文件基本信息

| 维度 | James (`DAP_Register.c`) | 主线 (`DAP_InterfaceRegister.c`) |
|------|--------------------------|----------------------------------|
| 行数 | 850 | 570 |
| 容量模型 | **动态链表**（v4, 初始 128, 每次 +64, 无上限） | **固定容量**（`OS_GetRegMaxItemCount()`） |
| 扩容 | ✅ `InterfaceRegister_GrowChunk()` 自动扩容 | ❌ 满则失败 |
| ID 化查找 | ❌ 无 | ✅ `InterfaceRegister_AddById/FindById` + `s_id_table[256]` |
| 额外依赖 | `dap_unisoc_shim.h` | `dap_interface_id.h` |

### 1.2 API 兼容性对比

| 公共函数 | James | 主线 | 签名兼容 |
|----------|-------|------|----------|
| `InterfaceRegister_Init()` | ✅ | ✅ | ✅ 完全兼容 |
| `InterfaceRegister_Active()` | ✅ (动态) | ✅ (固定) | ✅ 签名兼容，内部不同 |
| `InterfaceRegister_Free()` | ✅ (链表释放) | ✅ (单块释放) | ✅ 签名兼容 |
| `InterfaceRegister_Add(name, func)` | ✅ | ✅ | ✅ **完全兼容** |
| `InterfaceRegister_Find(name)` | ✅ | ✅ | ✅ **完全兼容** |
| `InterfaceRegister_Del(name)` | ✅ | ✅ | ✅ 完全兼容 |
| `GetInterfaceRegisterActived()` | ✅ | ✅ | ✅ 完全兼容 |
| `InterfaceRegister_GetCapacity()` | ✅ James 新增 | ❌ 不存在 | ⚠️ 仅内核调用 |
| `InterfaceRegister_GetCount()` | ✅ James 新增 | ❌ 不存在 | ⚠️ 仅内核调用 |
| `InterfaceRegister_AddById()` | ❌ 不存在 | ✅ 主线新增 | N/A — APP 不直接调用 |
| `InterfaceRegister_FindById()` | ❌ 不存在 | ✅ 主线新增 | N/A — 仅 EXTERNAL_BUILD |

### 1.3 Hash 算法兼容性

| 维度 | James | 主线 | 兼容 |
|------|-------|------|------|
| `CaclKey` 哈希函数 | 相同算法 | 相同算法 | ✅ |
| `Compare` 比较函数 | 区分大小写 | 区分大小写 | ✅ |
| Max name len | 48 | 48 | ✅ |
| `OS_GetRegMaxCalculateLen()` | 相同 | 相同 | ✅ |

### 1.4 ⚠️ 兼容性风险

| 风险 | 说明 | 影响 | 解决方案 |
|------|------|------|----------|
| **容量不足** | James 的 App 数量多（12 个 App + 大量新 API），注册的 API 可能超过主线的固定容量 | 🔴 **HIGH** — 超容量会导致 `InterfaceRegister_Add` 失败，App 无法获取 API | 增大 `OS_GetRegMaxItemCount()` 或移植 James 的动态扩容 |
| **新增 API 未注册** | James 在 `DAP_InstallOSAPI_UNISOC` 中注册了 LVGL/Audio/T9/VA/Download 等新 API，主线没有 | 🔴 **HIGH** — App 调用 `FindInterface("lv_label_create")` 会返回 NULL | 必须在主线的 `DAP_InstallOSAPI_unisoc.c` 中注册这些新 API |
| `dap_unisoc_shim.h` 缺失 | James 新增的 shim 头文件，提供 `OS_MemMalloc/Free` 宏映射 | 🟡 仅影响内核编译，不影响 App | 如果移植 Register → 需要一起移植 |

---

## 2. DAP_Loader.c (James) vs DAP_Loader_unisoc.c (主线)

### 2.1 文件基本信息

| 维度 | James (`DAP_Loader.c`) | 主线 (`DAP_Loader_unisoc.c`) |
|------|------------------------|------------------------------|
| 行数 | 558 | ~800+ (含 BIN2/BIN3) |
| 文件格式支持 | **BIN only** (v0/v1/v2) | BIN + **BIN2** + **BIN3** |
| 安全特性 | ❌ 无 | ✅ Ed25519 签名 + AES-CTR 加密 + 设备绑定 |
| `TApplication` 大小 | 352 bytes (编译期检查) | 352 bytes (相同) |
| `alloc_base` 模式 | ❌ 直接返回 `BinHeader_AP` | ✅ 追踪原始分配基地址 |
| `DAP_ExecuteAP` 返回 | `BinHeader_AP` 指针 | `alloc_base` (原始分配) |
| BSS 重分配 | 从文件重读 | BIN3: memcpy 保留解密数据 |

### 2.2 Loader 初始化流程对比

| 步骤 | James | 主线 |
|------|-------|------|
| 1. `InterfaceRegister_Init()` | ✅ | ✅ |
| 1.5. `InterfaceRegister_Active()` | ✅ | ✅ |
| 2. `Install_InterfaceRegister_API()` | ✅ | ✅ |
| 3. `DAP_InstallOSAPI_UNISOC()` | ✅ (James 版, 含 LVGL/Audio/T9/VA/DL) | ✅ (主线版, 含安全 API + ID 化) |
| 4. 安全初始化 | ❌ | ✅ `device_secret_init` + `device_binding_log_id` |

### 2.3 `DAP_ExecuteAP` 流程对比

| 步骤 | James | 主线 | 兼容 |
|------|-------|------|------|
| 打开文件 | DAP_FileOpen | 相同 | ✅ |
| 获取大小 | DAP_FileGetSize | 相同 | ✅ |
| 头部校验 | `DAP_GetSDKVersion` (BIN only) | ✅ + **BIN2 magic 检测** | ✅ 超集 |
| 分配内存 | DAP_MemAlloc | 相同 | ✅ |
| **BIN2 签名验证** | ❌ 无 | ✅ Ed25519 | ✅ 主线是超集 |
| **BIN3 设备绑定** | ❌ 无 | ✅ BindingID 检查 | ✅ 主线是超集 |
| **BIN3 解密** | ❌ 无 | ✅ AES-CTR | ✅ 主线是超集 |
| BSS 处理 | 从文件重读 | BIN: 重读 / BIN3: memcpy | ✅ |
| 地址重定位 | 4 字段 (LoadAddr/OSAPI/Register/DelAPI) | **相同 4 字段** | ✅ **完全兼容** |
| 入口调用 | `Bin_EntryToMain(PNULL, 0, CMD)` | 相同签名 | ✅ |
| 释放 (`ReleaseAP`) | 直接 `DAP_MemFree(APHandle)` | 通过 `alloc_base` 释放 | ⚠️ 见下 |

### 2.4 ⚠️ 兼容性风险

| 风险 | 说明 | 影响 | 解决方案 |
|------|------|------|----------|
| **重定位 ABI 兼容** | 两边都设置相同 4 字段（LoadAddr/OSAPI/Register/DelAPI），且 `TApplication` 均为 352 bytes | 🟢 **无风险** — 完全兼容 | 无需修改 |
| **BIN 格式兼容** | James 的 App 全部是 `.bin` (v0/v1)，主线 Loader 同样支持 BIN 加载 | 🟢 **无风险** | 无需修改 |
| **FindInterface 兼容** | James App 使用 `FindInterface("lv_xxx")` 查找 API，主线的 `InterfaceRegister_Find` 是同一个函数 | 🟢 **ABI 兼容** | 仅需注册对应 API |
| **SN 校验** | James 的 `DAP_GETUserSN` 永远返回 TRUE（stub），主线无此函数 | 🟢 无风险 | 无需处理 |

---

## 3. DAP_UNISOC_OSAssociated.c — James (632KB) vs 主线 (~25KB)

### 3.1 文件角色

James 的 `DAP_UNISOC_OSAssociated.c` 是一个 **632KB 的超级巨型文件**，实质上是主线多个文件的合并版本。

### 3.2 功能对比

| 功能区域 | James (单文件 632KB) | 主线 (多文件分离) |
|----------|---------------------|-------------------|
| 基础 OS API (Memory/File/Timer) | ✅ 在此文件中 | `DAP_OSAssociated_unisoc.c` (25KB) |
| GUI/Display API | ✅ 在此文件中 | `dap_gui_unisoc.c` (19KB) |
| Audio API | ✅ 在此文件中 | `dap_audio_bridge.c` (60KB) |
| LVGL Bridge | ✅ 在此文件中 | 独立 `make/dap/` 中的 LVGL 桥 |
| T9 Input | ✅ 在此文件中 | `dap_t9_engine.c` (34KB) |
| VA Bridge | ✅ 在此文件中 | `dap_va_bridge.c` (9KB) |
| Downloader | ✅ 在此文件中 | 不存在于主线 |
| Debug/Trace | ✅ 在此文件中 | `DAP_DebugLog.c` (11KB) |

### 3.3 ⚠️ 兼容性风险

| 风险 | 说明 | 影响 | 解决方案 |
|------|------|------|----------|
| **LVGL API 未注册** | James 的巨型文件中注册了 38+ LVGL API 到 InterfaceRegister，主线完全没有 | 🔴 **CRITICAL** — 所有 LVGL App 调用 FindInterface 都会返回 NULL | 必须在主线 `DAP_InstallOSAPI_unisoc.c` 中新增 LVGL API 注册 |
| **Audio API 差异** | James 的 audio bridge 是超集（60KB vs 主线 28KB），可能注册了更多 API | 🟡 **MEDIUM** — voice_chat 等 App 可能需要额外 Audio API | 对比后移植缺失 API |
| **T9 API 未注册** | 主线没有 T9 输入法 | 🔴 **HIGH** — notepad 等需要输入的 App 无法工作 | 移植 `dap_t9_engine.c` 并注册 |
| **VA API 未注册** | 主线没有 VA bridge | 🔴 **HIGH** — voice_chat 无法工作 | 移植 `dap_va_bridge.c` 并注册 |
| **Downloader API 未注册** | 主线没有下载功能 | 🔴 **HIGH** — Download_Bin App 无法工作 | 移植下载器模块并注册 |
| **DAP_SetKeyCallback 未注册** | 直接按键回调，游戏需要 | 🔴 **HIGH** — snake/tetris 无法接收按键 | 注册此 API |
| **DAP_ScanApps 未注册** | palm_menu 扫描 D:\DAP 目录列出 App | 🔴 **HIGH** — palm_menu 启动器无法列出 App | 注册此 API |

---

## 4. 总结：兼容性 Gap 清单

### 🟢 无风险（已兼容）
- `TApplication` 结构体 (352 bytes) — 完全一致
- 重定位 ABI (4 字段) — 完全一致
- `InterfaceRegister_Add/Find/Del` 签名 — 完全一致
- `FindInterface()` 查找机制 — 完全一致
- BIN 文件格式 (v0/v1) — 主线 Loader 支持

### 🔴 必须解决（否则 James App 无法运行）

| # | Gap | 原因 | 解决方案 | 优先级 |
|---|-----|------|----------|--------|
| 1 | **LVGL API 未注册** (38+) | 主线没有注册任何 LVGL API | 在 `DAP_InstallOSAPI_unisoc.c` 中注册 | P0 |
| 2 | **LVGL Runtime 缺失** | 主线没有 LVGL 9.5.0 源码 | 移植 `Third-party/lvgl-9.5.0/` + `make/lvgl/lvgl.mk` | P0 |
| 3 | **DAP_SetKeyCallback 未注册** | 游戏按键回调 | 移植实现 + 注册 | P0 |
| 4 | **DAP_ScanApps 未注册** | palm_menu 扫描 App 列表 | 移植实现 + 注册 | P0 |
| 5 | **Audio Bridge 差异** | 主线版本小于 James 版本 | 对比后补充缺失 API | P1 |
| 6 | **T9 引擎缺失** | notepad 需要输入法 | 移植 `dap_t9_engine.c` + 注册 | P1 |
| 7 | **VA Bridge 缺失** | voice_chat 需要 | 移植 `dap_va_bridge.c` + 注册 | P1 |
| 8 | **Downloader 缺失** | Download_Bin 需要 | 移植下载器模块 + 注册 | P2 |
| 9 | **注册容量可能不足** | James 注册 200+ API，主线固定容量可能不够 | 增大 `OS_GetRegMaxItemCount()` | P1 |

### 🟡 注意事项（不阻塞但需关注）
- James 的 `DAP_Register.c` 有动态扩容——如果主线容量够大则无需移植
- James 的 `DAP_GETUserSN` 是 stub——不影响
- James 的 632KB 巨型文件**不应整体移植**——应从中提取所需 API 注册代码
