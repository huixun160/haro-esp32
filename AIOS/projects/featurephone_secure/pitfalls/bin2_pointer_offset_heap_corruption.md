# Pitfall: BIN2 Unwrap 后指针偏移导致 Heap 损坏

**Date:** 2026-03-11
**Memo:** TM-22
**Severity:** Critical（heap 损坏 / SCI_Release_Buffer assert）

## Symptom

BIN2 文件在设备端运行后出现：
- `SCI_Release_Buffer` assert
- 内存泄漏
- 蓝屏 / 系统崩溃

BIN1 文件不受影响。

## Root Cause

`DAP_Loader_unisoc.c` 中 BIN2 验证成功后，`Running_AP` 指针前移 112 字节剥离 BIN2 头部：

```c
Running_AP = (void *)((uint32)Running_AP + bin2_payload_off);  // 原始基地址丢失！
```

后续 `DAP_MemFree(Running_AP)` 释放的是偏移后的指针，而非 `DAP_MemAlloc` 返回的原始基地址。大多数 heap 实现会因此 assert 或损坏。

## Fix

新增 `alloc_base` 变量追踪原始分配基地址：

```c
void *alloc_base = PNULL;
Running_AP = DAP_MemAlloc(size);
alloc_base = Running_AP;  // 保存原始基地址

// BIN2 前移 Running_AP 时，alloc_base 不变
// 所有 DAP_MemFree 使用 alloc_base
```

## Prevention

**任何模块中对 `DAP_MemAlloc` 返回指针做偏移操作时，必须保留原始基地址用于 free：**

1. 新增指针偏移逻辑时，检查同函数内所有 free 路径
2. 检查 error_exit 路径是否使用正确的基地址
3. 检查返回值（handle）后续是否被 free，确保用原始基地址

## 参考

- Root Cause 文档：`docs/tm22_memoryleak_trace_analysis.md`
- 修复文件：`Third-party/DAP/platform/unisoc/DAP_Loader_unisoc.c`
