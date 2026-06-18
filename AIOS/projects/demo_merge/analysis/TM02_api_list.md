# TM02 API Inventory — James Legacy

**Author:** KaiwenZheng | **Project:** demo_merge | **Date:** 2026-03-26

---

## 1. LVGL API (38 个) — from `sdk/lvgl_api.h`

| 类别 | API | 是否新增 | 依赖 MMI |
|------|-----|----------|----------|
| **窗口 (2)** | `lv_open_window`, `lv_close_window` | ✅ 新增 | ❌ |
| **屏幕 (2)** | `lv_scr_act`, `lv_obj_clean` | ✅ 新增 | ❌ |
| **对象 (8)** | `lv_obj_create/delete/set_size/set_pos/set_width/set_height/align/add_flag` | ✅ 新增 | ❌ |
| **样式 (9)** | `lv_obj_set_style_bg_color/_opa/_grad_color/text_color/text_font/border_width/border_color/pad_all/radius` | ✅ 新增 | ❌ |
| **Label (3)** | `lv_label_create/set_text/set_long_mode` | ✅ 新增 | ❌ |
| **Button (1)** | `lv_btn_create` | ✅ 新增 | ❌ |
| **List (3)** | `lv_list_create/add_text/add_btn` | ✅ 新增 | ❌ |
| **焦点 (2)** | `lv_group_get_default/add_obj` | ✅ 新增 | ❌ |
| **事件 (4)** | `lv_obj_add_event_cb/event_get_code/get_target/get_user_data` | ✅ 新增 | ❌ |
| **定时器 (2)** | `lv_timer_create/delete` | ✅ 新增 | ❌ |
| **图片 (2)** | `lv_img_create/set_src` | ✅ 新增 | ❌ |
| **字体 (1)** | `dap_font_get_builtin` | ✅ 新增 | ❌ |

### DAP 专用扩展 API
| API | 功能 | 是否新增 |
|-----|------|----------|
| `DAP_LVGL_SetKeyCallback` | 直接按键回调（绕过焦点组） | ✅ 新增 |
| `DAP_ScanApps` | 扫描 D:\DAP 目录列出 app | ✅ 新增 |

---

## 2. Audio API — from `sdk/dap_audio_api.h`

| API | 功能 | 是否新增 |
|-----|------|----------|
| 音频录制/播放/停止 | 完整音频链路 | 部分新增 |
| 需从 `dap_audio_bridge.c` (60KB) 提取详细列表 | — | — |

---

## 3. VA (Voice Assistant) API — from `sdk/dap_va_api.h`

| API | 功能 | 是否新增 |
|-----|------|----------|
| 语音识别/合成/HTTP 通信 | 云端 AI 对接 | ✅ 新增 |
| 需从 `dap_va_bridge.c` (9KB) 提取详细列表 | — | — |

---

## 4. T9 输入法 API — from `sdk/dap_t9_api.h`

| API | 功能 | 是否新增 |
|-----|------|----------|
| T9 拼音输入/候选词/选词 | 中文输入支持 | ✅ 新增 |
| 需从 `dap_t9_engine.c` (34KB) 提取详细列表 | — | — |

---

## 5. Downloader API — from `DL_InstallDownloaderAPI.c`

| API | 功能 | 是否新增 |
|-----|------|----------|
| HTTP 下载 BIN 文件 | App 分发 | ✅ 新增 |
| 下载进度/状态/错误处理 | UI 反馈 | ✅ 新增 |
| 需从 `DAP_Downloader.c` (57KB platform + 480KB SDK) 提取 | — | — |

---

## 6. 已有 API (主线已实现)

| API | 来源 | James 是否修改 |
|-----|------|---------------|
| `FindInterface()` | DAP Core | ❌ 未修改 ABI |
| `DAP_MemAlloc/Free` | 内存管理 | ❌ |
| `DAP_TracePrint` → `SCI_TRACE_LOW` | 日志 | ❌ |
| `DAP_FileOpen/Read/Write/Close` | 文件操作 | ❌ |
| `DAP_TimerCreate/Delete` | 定时器 | ❌ |
| `DAP_DisplayPopup` | UI 弹窗 | ❌ |

---

## 7. API ABI 兼容性评估

| 维度 | 结论 |
|------|------|
| FindInterface ABI | ✅ 兼容 — James 使用相同的字符串查找机制 |
| LVGL API | ✅ 全部通过 `FindInterface("lv_xxx")` — 不影响现有 ABI |
| 新增 API 注册 | ⚠️ James 在 `DAP_Register.c` 中注册 — 我们需要在 `DAP_InterfaceRegister.c` 中同步注册 |
| 基础 API | ✅ 兼容 — 基础 API 相同 |
