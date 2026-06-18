# TM-030 Clarification Questions

**Memo:** TM30 — Internal SDK Boundary Freeze (DAP ABI Stabilization v0)
**Date:** 2026-03-19

> 以下问题基于对现有 9 个 DAP APP 源码和 SDK/core 结构的分析。请在每题下方写上你的选择和理由。

---

## Q1. `core/DAP_Application.h` 如何处理？

**现状：** 所有 9 个现有 APP 都 `#include "../core/DAP_Application.h"`，这个文件定义了：
- `TApplication` 结构体（352 字节，.bin 文件头格式）
- `TAP_Entry` 函数指针类型（`Main()` 签名）
- `TAP_GetBSSSpace` 类型

**Memo 要求：** APP 禁止访问 `core/`

**选项：**

- **(A)** 把 APP 需要的类型定义（`TAP_Entry`, `Main` 签名）**提取到 `sdk/dap_api.h`**，`core/DAP_Application.h` 变成 loader 内部专用。APP 不再 include `core/` 下的任何文件。
- **(B)** 直接把 `DAP_Application.h` **移到 `sdk/`**。简单但暴露了 loader 内部结构（`TApplication` 352 字节布局）。
- **(C)** APP 实际不需要知道 `TApplication` 的存在，只在 `sdk/dap_api.h` 里声明 `Main` 的原型即可。

**你的选择：**


---

## Q2. `FindInterface` 动态查找 vs 静态 API

**现状：** APP 通过 `FindInterface("函数名", CMD)` 动态获取函数指针：
```c
TOS_DisplayPopup ShowAlert = (TOS_DisplayPopup)FindInterface("OS_DisplayPopup", CMD);
ShowAlert("Hello");
```

**Memo 定义** 的 API 是静态调用风格：
```c
dap_log("Hello");
dap_malloc(1024);
```

**选项：**

- **(A)** `dap_api.h` 提供**宏/static inline 封装**，内部仍用 `FindInterface`。APP 代码写 `dap_log("Hello")`，编译时展开为 `FindInterface` 调用。ABI 不变，但 APP 代码更规范。
- **(B)** 彻底重构为**编译期链接**，废弃 `FindInterface` 机制。需要修改 loader 和整个 APP 构建流程。
- **(C)** 保持 `FindInterface` 原样，Memo 里的 `dap_log` / `dap_malloc` 等仅作为**文档约定**（推荐命名），不实际改代码。

**你的选择：**


---

## Q3. 现有 9 个 APP 的迁移策略

**现状：** 9 个 APP 的 include 路径不统一：

| APP | include 风格 |
|-----|-------------|
| demo_ui, hello_lvgl, snake, tetris, voice_recorder, mp3_player, lvgl_template | `#include "def.h"` + `"../core/DAP_Application.h"` |
| hello_bigseek, pass_success | `#include "../../sdk/def.h"` + `"../../core/DAP_Application.h"` |

**选项：**

- **(A)** 所有 9 个 APP **全部迁移**到 `#include "dap_api.h"` — 一次性断裂，但干净
- **(B)** 先做 `dap_api.h`，**新 APP 强制用它**，旧 APP 暂时保持兼容 — 渐进迁移
- **(C)** 只迁移 `hello_bigseek` 作为参考模板，其余旧 APP **不维护**

**你的选择：**


---

## Q4. 基础类型：自定义 vs 标准 C

**现状：** `def.h` 定义 `_DWORD`, `_VOID`, `_CHAR8`, `_BOOL`, `_U16` 等自定义类型

**Memo API** 用标准 C 类型：`void*`, `size_t`, `int`, `const char*`

**选项：**

- **(A)** `dap_api.h` 中统一用**标准 C 类型**（`void*`, `int`, `const char*`），`def.h` 降级为内部使用
- **(B)** 保持 `_DWORD` 系列类型，`dap_api.h` 沿用 DAP 历史约定
- **(C)** `dap_api.h` 用标准类型对外，内部用 typedef 映射到 `_DWORD` 系列

**你的选择：**


---

## Q5. v0 最小 API 集合覆盖范围

**Memo 定义** 5 类 API：lifecycle, memory, log, event, timer

**现有 APP 还用到以下 `FindInterface` API：**

| API | 使用者 |
|-----|--------|
| `OS_DisplayPopup` | hello_bigseek（弹框提示） |
| `DAP_LVGL_*` | 6 个 LVGL APP（UI 渲染） |
| `DAP_Audio*` | mp3_player, voice_recorder |

**选项：**

- **(A)** v0 只覆盖 `hello_bigseek` 需要的（log + popup），**LVGL 和 Audio 留给 v1**
- **(B)** v0 包含所有现有 APP 用到的 API（popup + LVGL + Audio）— 范围较大
- **(C)** v0 只包含 Memo 定义的 5 类（不含 popup/LVGL/Audio），`hello_bigseek` 中 popup 调用改为 `dap_log` 替代

**你的选择：**


---

> 回复完毕后，我将基于你的决策制定实施方案并进入 `/aios-workflow` 执行。
