下面是按你提供的 **template** 写好的 **Technical Memo 20 — Logel Trace Fix & BIN2 Prefix Tracking**。
我结合了工程师反馈里的关键结论：

* 平台标准 trace API 是 `SCI_TRACE_LOW` 
* SIMLOCK 等模块直接使用它并在 Logel 可见 
* DAP 目前通过 `DAP_TracePrint → SCI_TRACE_LOW` 的链路输出 
* 但 **DAP security 文件本身没有 `os_api.h`**，因此无法直接使用 `SCI_TRACE_LOW` 

以及你现在的实际问题：

```
L6218E: Undefined symbol BIN2_LOG (referred from bin2_loader.o)
```

这说明 **BIN2_LOG 宏没有在链接阶段解析**，需要统一日志宏实现。

下面是可以直接发给工程师执行的 **TM20**。

---

# Technical Memo 20 — Logel Trace Fix & BIN2 Prefix Tracking

**Project:** AIOS Feature Phone Platform

**Subsystem:** DAP / Security / BIN2 Loader

**Author:** AIOS Core Team

**Priority:** HIGH

**Date:** 2026-03-10

---

# Background

TM-15 引入 BIN2 secure loader 之后，需要通过 Logel trace 来诊断：

* BIN2 header 解析
* payload hash
* Ed25519 验签
* DeviceSecret

但当前存在两个问题：

### 1 Logel trace 机制不统一

平台其它模块直接使用：

```
SCI_TRACE_LOW(...)
```

并且在 Logel 中可见，例如：

```
SCI_TRACE_LOW("[SIMLOCK] ...")
SCI_TRACE_LOW("[USB] ...")
SCI_TRACE_LOW("[BS_PCM_DQ] ...")
```

这些模块均能稳定输出 trace。 

但 DAP security 文件：

```
bin2_loader.c
bin2_crypto.c
device_identity.c
```

**没有包含 `os_api.h`**，因此无法直接使用 `SCI_TRACE_LOW`。 

目前 DAP trace 链路为：

```
DAP_DBG
 ↓
DAP_TracePrint
 ↓
SCI_TRACE_LOW
 ↓
SCI_TraceLow
 ↓
Logel
```

理论上链路可行，但实际设备上尚未确认。

---

### 2 编译错误

当前编译错误：

```
Undefined symbol BIN2_LOG (referred from bin2_loader.o)
```

说明：

* BIN2 loader 使用了 `BIN2_LOG`
* 但该宏未在所有编译单元定义

需要统一实现。

---

# Objective

本任务目标：

1 统一 BIN2 loader 的 Logel trace 机制

2 建立稳定的 **BIN2 前缀日志**

例如：

```
[bin2] header ok
[bin2] payload hash ok
[bin2] verify start
[bin2] verify fail
```

3 修复 `BIN2_LOG` 未定义的编译问题

4 确保 TM-15 后续调试可以通过 Logel 观察到完整执行路径

---

# Current State

当前情况：

### Trace API

平台标准 API：

```
SCI_TRACE_LOW(...)
```

SIMLOCK 示例：

```
#define INF(fmt, x...) \
SCI_TRACE_LOW("[SIMLOCK] %s(%d): " fmt, __func__, __LINE__, ##x)
```



---

### DAP trace

DAP 当前 trace：

```
DAP_DBG(...)
 → DAP_TracePrint(...)
 → SCI_TRACE_LOW
```

但：

* DAP security 文件不包含 `os_api.h`
* 因此不能直接调用 `SCI_TRACE_LOW`

---

### BIN2_LOG

当前 BIN2 loader 使用：

```
BIN2_LOG(...)
```

但没有统一宏定义。

导致：

```
Undefined symbol BIN2_LOG
```

---

# Scope

本任务包括：

1 实现统一 BIN2_LOG 宏

2 将 BIN2 loader trace 前缀统一为

```
[bin2]
```

3 确保日志能在 Logel 输出

4 添加最小 BIN2 trace 路径

---

# Out of Scope

本任务不包括：

* Ed25519 算法修复
* BIN2 加密
* DeviceSecret binding
* App Store 逻辑

---

# Constraints

必须满足：

1 不破坏现有 DAP loader

2 不引入新的 RTOS 依赖

3 trace 不影响性能

4 BIN2 trace 可以通过宏关闭

---

# Implementation Plan

## Step 1 — 定义 BIN2_LOG

新增头文件：

```
dap_security_log.h
```

内容：

```c
#ifndef DAP_SECURITY_LOG_H
#define DAP_SECURITY_LOG_H

#include "DAP_DebugLog.h"

#define BIN2_LOG(fmt, ...) \
    DAP_DBG("[bin2] " fmt, ##__VA_ARGS__)

#endif
```

说明：

BIN2_LOG 只是 DAP_DBG 的封装。

最终 trace 路径：

```
BIN2_LOG
 ↓
DAP_DBG
 ↓
DAP_TracePrint
 ↓
SCI_TRACE_LOW
 ↓
Logel
```

无需在 security 文件中直接包含 `os_api.h`。

---

## Step 2 — 修复编译错误

在以下文件顶部加入：

```
#include "dap_security_log.h"
```

文件：

```
bin2_loader.c
bin2_crypto.c
device_identity.c
```

确保：

```
BIN2_LOG
```

宏已定义。

---

## Step 3 — 插入 BIN2 trace

在 `bin2_loader.c` 关键节点加入 trace：

### header parse

```
BIN2_LOG("header magic ok");
```

### payload size

```
BIN2_LOG("payload size=%u", payload_size);
```

### verify start

```
BIN2_LOG("verify start");
```

### verify success

```
BIN2_LOG("verify ok");
```

### verify fail

```
BIN2_LOG("verify fail");
```

---

## Step 4 — 最小 PoC trace

在 `device_secret_init()` 中加入：

```
BIN2_LOG("tm20_trace_alive");
BIN2_LOG("tm20_val=%d", 42);
```

用于确认 Logel trace。

---

# Expected Deliverables

1

新增文件：

```
dap_security_log.h
```

实现 BIN2_LOG。

---

2

修改：

```
bin2_loader.c
bin2_crypto.c
device_identity.c
```

加入日志。

---

3

修复编译错误：

```
Undefined symbol BIN2_LOG
```

---

4

设备端 Logel 输出：

```
[bin2] header magic ok
[bin2] verify start
```

---

# Verification Method

## Build verification

编译：

```
build ums9117_240X320BAR_64MB_ML
```

期望：

```
0 errors
```

---

## Device test

运行 `.bin2`：

观察 Logel：

```
[bin2] header magic ok
[bin2] verify start
```

---

## Log verification

确认出现：

```
tm20_trace_alive
tm20_val=42
```

---

# Potential Risks

### 1 Trace 未出现

原因：

```
SCI_TRACE_MODE 未启用
```

解决：

确认 `dap.mk` 添加：

```
-DSCI_TRACE_MODE
```

---

### 2 Trace 太长

Logel 可能截断。

建议：

单条日志 < 128 字符。

---

### 3 trace 影响性能

后续可加入：

```
#ifdef BIN2_TRACE_ENABLE
```

控制编译。

---

# References

TM-15 BIN2 Loader

TM-19 Logel Trace Pilot

Logel Trace Feedback 

Technical Memo Template 

---
