# Pitfall: SFS 文件写入需要 OPEN_ALWAYS + CreateDirectory

**Date:** 2026-03-12
**Memo:** TM-26
**Severity:** High（编译通过但文件写入 0 字节）
**Recurrence:** 1 次

## Symptom

`SFS_WriteFile` 返回 `written=0`，文件内容为空。
Logel trace: `[BIND] export: write incomplete 0/131`

## Root Cause

三个错误叠加：

| 错误 | 错误代码 | 正确代码（参考 DAP_DebugLog.c） |
|------|----------|-------------------------------|
| 1. 使用了错误的创建模式 | `SFS_MODE_CREATE_ALWAYS (0x02)` | `SFS_MODE_OPEN_ALWAYS (0x0040)` |
| 2. 未预先创建目录 | 无 | `SFS_CreateDirectory(dir_path)` |
| 3. handle 判空方式错误 | `== 0xFFFFFFFF` | `== 0` (DAP_DebugLog.c 的判断方式) |

## SFS 常量值（来自 MS_Ref/export/inc/sfs.h）

```c
#define SFS_MODE_READ           0x80000000
#define SFS_MODE_WRITE          0x40000000
#define SFS_MODE_OPEN_EXISTING  ((uint32)(0x3<<4))  // 0x30
#define SFS_MODE_OPEN_ALWAYS    ((uint32)(0x4<<4))  // 0x40
```

## 参考代码

`DAP_DebugLog.c` 第 168-173 行（已验证可正常写文件到 `D:\DAP\`）：

```c
SFS_CreateDirectory(DAP_LOG_ROOT);
log_handle = SFS_CreateFile(log_path, SFS_MODE_WRITE | SFS_MODE_OPEN_ALWAYS, 0, 0);
if (log_handle == 0) return;
```

## Prevention

- DAP 新模块写文件时，**必须**参考 `DAP_DebugLog.c` 的 SFS 调用模式
- 不要凭猜测定义 SFS 常量，查阅 `MS_Ref/export/inc/sfs.h`
- 写文件前必须 `SFS_CreateDirectory` 确保目录存在

## Affected Module

`device_binding.c`, `device_bindfile.c`
