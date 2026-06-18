# Technical Memo 23 — Offline Device Binding with `.bind` File

**Title:** Offline Device Binding Mechanism for BIN2 Using Bindfile
**Project:** AIOS Feature Phone Platform
**Subsystem:** DAP / Security / BIN2 Loader / Toolchain
**Author:** AIOS Core Architecture
**Priority:** HIGH
**Date:** 2026-03-11

---

# Background

TM15–TM22 完成了 **BIN2 Phase-0 的安全链路调通**：

* `test_original.bin` 正常执行
* `test_valid.bin2` 正常执行
* `test_tampered.bin2` 被拒绝
* `test_badsig.bin2` 被拒绝
* Ed25519 signature verification 成功

这意味着当前系统已经实现：

```
Integrity Protection
```

即：

```
未签名 → 不运行
篡改 → 不运行
```

但是仍然存在一个核心安全问题：

```
BIN2 可跨设备复制运行
```

例如：

```
device A 下载 app
device B 拷贝 BIN2
device B 也能运行
```

这会导致未来：

* App Store 收费机制失效
* 应用授权失效
* 应用生态被复制

因此必须进入 **BIN2 Phase-1：Device Binding**。

---

# Current Constraints

当前系统存在几个现实限制：

1. **APP Store 尚未开发**
2. **云端设备数据库尚未实现**
3. **应用分发仍通过 PC → USB 拷贝 BIN**
4. **DeviceSecret 已经存在设备端 NV 中**

因此目前不适合直接实施：

```
Online Device Binding
```

解决方案是实现一个 **Offline Device Binding 过渡架构**。

---

# Objective

实现以下目标：

```
BIN2 只能在指定设备运行
```

同时满足：

1. DeviceSecret **永远不离开设备**
2. PC / packer **不需要知道 DeviceSecret**
3. 当前 **PC sideload 工作流不改变**
4. 未来 **可以平滑升级到云端 App Store**

---

# Core Concept

## DeviceSecret

设备内部生成：

```
DeviceSecret = 256-bit random
```

存储位置：

```
User NV
```

例如：

```
uint8_t DeviceSecret[32];
```

DeviceSecret **绝不导出设备**。

---

## BindingID

设备从 DeviceSecret 派生：

```
BindingID = SHA256("AIOS-BIND-V1" || DeviceSecret)[0..15]
```

即：

```
128-bit identifier
```

长度：

```
16 bytes
```

十六进制表示：

```
32 hex characters
```

示例：

```
9f2a7c41e3d1b2a4c8b7d9e1f0a12345
```

BindingID **允许导出设备**。

---

# `.bind` File

设备导出一个 **bindfile**。

文件名建议：

```
device.bind
```

格式：

```json
{
  "version": 1,
  "binding_alg": "SHA256-128",
  "binding_id": "9f2a7c41e3d1b2a4c8b7d9e1f0a12345",
  "device_model": "ums9117_240X320BAR_64MB_ML"
}
```

作用：

```
让 PC packer 知道设备 BindingID
```

注意：

```
.bind 文件不包含 DeviceSecret
```

---

# Execution Flow

## Step 1 — Device First Boot

设备首次启动：

```
generate DeviceSecret
store to NV
```

然后计算：

```
BindingID
```

---

## Step 2 — Export Bindfile

设备生成：

```
/device/device.bind
```

用户通过 USB 拷贝到 PC。

---

## Step 3 — PC Packer

packer 读取：

```
device.bind
```

获得：

```
binding_id
```

然后构建：

```
BIN2 header
```

新增字段：

```
binding_mode
binding_id
```

例如：

```
binding_mode = DEVICE_BOUND
binding_id = 16 bytes
```

随后：

```
sign(header + payload)
```

---

## Step 4 — Device Loader

加载 BIN2 时：

设备计算：

```
BindingID_local = SHA256("AIOS-BIND-V1" || DeviceSecret)[0..15]
```

然后：

```
BindingID_local == binding_id ?
```

如果：

```
true → execute
false → reject
```

---

# BIN2 Header Update

新增字段：

```
uint8 binding_mode
uint8 binding_id[16]
```

binding_mode：

```
0 = UNBOUND
1 = DEVICE_BOUND
```

验证顺序：

```
verify signature
verify device binding
execute payload
```

---

# Required Deliverables

工程师需要实现：

### 1 Device Side

新增模块：

```
device_binding.c
```

功能：

```
generate DeviceSecret
derive BindingID
export bindfile
verify binding
```

---

### 2 Loader Update

在 BIN2 verify 后增加：

```
binding verification
```

位置：

```
verify signature
→ verify binding
→ relocate
→ execute
```

---

### 3 Packer Update

Python packer 支持：

```
--bind-file device.bind
```

读取：

```
binding_id
```

并写入 BIN2 header。

---

### 4 Tests

必须通过：

```
test_original.bin → pass
test_valid.bin2 (same device) → pass
test_valid.bin2 (different device) → reject
test_tampered.bin2 → reject
test_badsig.bin2 → reject
```

---

# Collision Consideration

BindingID 长度：

```
128-bit
```

支持：

```
10M+ devices
```

碰撞概率：

```
~10^-24
```

工程上可忽略。

---

# Logging Requirement

所有新代码必须保留：

```
Logel trace
```

示例：

```
[BIND] mode=DEVICE_BOUND
[BIND] header_id=...
[BIND] local_id=...
[BIND] result=PASS/FAIL
```

严禁：

```
关闭现有 trace
```

---

# Engineering Pitfalls to Avoid

必须避免过去出现的问题：

### 1 dap.mk 修改

曾导致：

```
link error
missing object
```

所有新增文件必须：

```
正确加入 dap.mk
```

---

### 2 Logel trace

过去 debug 成功依赖：

```
SCI_TRACE_LOW
```

新代码必须：

```
保持 trace 可追踪
```

---

### 3 Memory Ownership

之前 BIN2 loader 出现：

```
offset pointer free
heap corruption
```

要求：

```
明确 buffer ownership
```

---

### 4 Header Offset

必须保证：

```
payload pointer
header offset
BSS pointer
```

一致。

---

# Architecture Documentation

同时需要新增文档：

路径：

```
AIOS/docs/architecture/
```

新增文件：

```
device_binding.md
bin2_security_model.md
```

内容包括：

* DeviceSecret lifecycle
* BindingID derivation
* Offline binding workflow
* Future App Store integration

目的：

```
为未来云端架构提供参考
```

---

# Future Architecture Roadmap

当前实现：

```
Offline Device Binding
```

未来升级：

```
Device → App Store registration
App Store stores BindingID
App Store signs BIN2 per device
```

最终架构：

```
Developer → App Store → Device
```

---

# Out of Scope

本 memo 不包括：

```
App Store backend
account system
license server
DAP runtime obfuscation
```

---

# Verification Checklist

必须确认：

```
DeviceSecret stored in NV
.bind file exported
packer supports bindfile
loader verifies binding
cross-device copy rejected
trace visible in logel
```

---

# Final Note

TM15-TM22 解决的是：

```
BIN2 integrity
```

TM23 要解决的是：

```
BIN2 ownership
```

这是 AIOS 应用生态安全的关键步骤。

---
