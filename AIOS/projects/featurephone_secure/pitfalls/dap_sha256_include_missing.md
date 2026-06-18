# Pitfall: device_binding.c include 不存在的 dap_sha256.h

**Date:** 2026-03-12
**Memo:** TM-25
**Severity:** Critical（编译链中断，dap.a 无法生成）
**Recurrence:** 1 次

## Symptom

编译报错：
```
[dap] "Third-party/DAP/security/device_binding.c", line 16: Error:  #5: cannot open source input file "dap_sha256.h": No such file or directory
[link] Fatal error: L6002U: Could not open file build/.../lib/dap.a: No such file or directory
```

## Root Cause

SHA-256 **函数**使用 `dap_` 前缀（如 `dap_sha256_hash`、`DAP_SHA256_CTX`），但**头文件**名是 `sha256.h`（不带 `dap_` 前缀）。`device_binding.c` 误写为 `#include "dap_sha256.h"`。

## Prevention

1. 新增 include 前先确认文件是否真实存在
2. ADR-001 约定 `dap_` 前缀用于**符号名**（避免与平台库冲突），不要求文件名也带前缀
3. 编译报 `cannot open source input file` 时，第一步 `find` 确认文件名

## 参考

- ADR-001: SHA-256 Symbol Namespacing
- `Third-party/DAP/security/sha256.h`
