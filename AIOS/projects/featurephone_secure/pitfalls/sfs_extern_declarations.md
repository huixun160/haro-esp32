# Pitfall: 安全模块不能用 extern 声明 SFS 函数

**Date:** 2026-03-12
**Memo:** TM-26
**Severity:** Critical（编译通过但 SFS 调用全部静默失败）
**Recurrence:** 1 次（4 次调试迭代才定位）

## Symptom

`SFS_CreateFile` 返回 `0`，但代码判断为有效句柄，后续写入全部失败。
多次修改路径和参数均无效。

## Root Cause

`device_binding.c`（security 模块）使用 `extern` 声明自行定义 SFS 函数和常量：

```c
// ❌ 错误做法 — extern 猜测
extern void* SFS_CreateFile(const uint16 *, uint32, uint32, uint32);
#define SFS_INVALID_HANDLE ((void*)0xFFFFFFFF)  // 实际是 0 !!
#define SFS_MODE_CREATE_ALWAYS 0x02              // 实际不存在!
```

而平台头文件 `DAP_OSAssociated_unisoc.h` 第 48 行定义：
```c
#define SFS_INVALID_HANDLE 0  // 无效句柄 = 0
```

导致：
1. SFS 返回 `0`（失败），但代码与 `0xFFFFFFFF` 比较 → 误判为成功
2. 后续 `SFS_WriteFile` 往句柄 0 写入 → 写入 0 字节
3. `SFS_MODE_*` 常量值全部错误

## 正确做法

```c
// ✅ 正确做法 — include 平台头文件链
#include "../platform/unisoc/DAP_OSAssociated_unisoc.h"
// 该头文件 include: os_api.h → sci_api.h → sfs.h
// 获得：正确的 SFS_HANDLE 类型、SFS_INVALID_HANDLE=0、SFS_MODE_* 常量
```

## Prevention

- DAP security 模块**禁止**使用 `extern` 声明平台 API
- **必须** `#include "../platform/unisoc/DAP_OSAssociated_unisoc.h"` 或等价头文件
- 参考 `DAP_DebugLog.c` 作为文件操作的标准模式
- 新增 SFS 调用时，对照 `DAP_OSAssociated_unisoc.c` 中已验证的实现

## Affected Files

- `device_binding.c` — 修复完成
- `device_bindfile.c` — 修复完成
