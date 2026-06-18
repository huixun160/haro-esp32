# Technical Memo 26 — Bindfile Export to Device Filesystem

**Title:** Bindfile Export for Offline Device Binding (Phase-1B)

**Project:** AIOS Feature Phone Platform

**Subsystem:** DAP / Security / Device Binding

**Author:** AIOS Core Architecture

**Priority:** HIGH

**Date:** 2026-03-12

---

# Background

在 **TM25** 中，设备已经成功完成：

* DeviceSecret 生成与持久化
* BindingID 派生
* Logel 输出 BindingID
* DeviceSecret 随机性基本验证

Logel 示例：

```
[bind] tm25_id[0..7] = ...
[bind] tm25_id[8..15] = ...
```

这说明：

```
DeviceSecret → BindingID
```

链路已经稳定。

但当前 BindingID 仍然只能通过 **Logel 调试工具读取**，这不适合：

* PC packer 使用
* App Store 设备识别
* 自动化测试

因此必须进入 **Phase-1B：Bindfile Export**。

---

# Objective

在设备文件系统中生成一个 **bind 文件**，包含设备 BindingID 等公开信息，使得：

```
PC 可以读取 bind 文件
→ packer 使用 binding_id
→ 生成 device-bound BIN2
```

该 bind 文件必须：

* 可被普通电脑直接打开
* 不包含 DeviceSecret
* 可稳定复制到 PC

---

# Core Concept

设备生成：

```
DeviceSecret (32 bytes)
```

派生：

```
BindingID = SHA256("AIOS-BIND-V1" || DeviceSecret)[0..15]
```

长度：

```
16 bytes
```

Bindfile 的作用：

```
公开 BindingID
但不泄露 DeviceSecret
```

---

# File Location

bind 文件必须写入：

```
FileArray/
```

完整路径示例：

```
FileArray/device.bind
```

原因：

* FileArray 已存在
* USB 可直接访问
* PC 可以直接拷贝

---

# Bindfile Format

建议使用 **JSON**。

原因：

* PC 无需额外工具
* 可直接查看
* 未来 App Store 解析简单

文件示例：

```json
{
  "version": 1,
  "binding_alg": "SHA256-128",
  "binding_id": "9f2a7c41e3d1b2a4c8b7d9e1f0a12345",
  "device_model": "ums9117_240X320BAR_64MB_ML"
}
```

字段说明：

| 字段           | 含义          |
| ------------ | ----------- |
| version      | bindfile版本  |
| binding_alg  | BindingID算法 |
| binding_id   | 设备唯一标识      |
| device_model | 设备型号        |

注意：

```
bindfile 不允许包含 DeviceSecret
```

---

# Trigger Conditions

bind 文件生成有两个触发方式：

## 1 调试界面

工程码：

```
*#3271#
```

进入 debug 菜单后：

```
Generate Bindfile
```

生成：

```
FileArray/device.bind
```

---

## 2 执行 BIN2 时自动生成

当执行 BIN2 时：

如果 bind 文件不存在：

```
auto generate bindfile
```

这样可以避免用户忘记生成。

---

# Device Side Implementation

新增模块：

```
device_bindfile.c
device_bindfile.h
```

核心 API：

```
BOOLEAN device_bindfile_generate(void)
BOOLEAN device_bindfile_exists(void)
```

逻辑：

```
read DeviceSecret
derive BindingID
build JSON text
write FileArray/device.bind
```

---

# File Writing

必须使用平台已有的文件系统 API。

伪代码：

```
open("FileArray/device.bind")
write(json)
close()
```

注意：

```
必须覆盖旧文件
```

避免多个 bind 文件。

---

# Logel Trace

bindfile 生成必须输出 trace：

```
[bind] tm26_generate_bindfile
[bind] binding_id=...
[bind] file_written=FileArray/device.bind
```

仍然使用：

```
SCI_TRACE_LOW
```

保证 Logel 可以追踪。

---

# Security Requirements

必须满足：

```
DeviceSecret 不出设备
```

bindfile 只能包含：

```
BindingID
```

禁止：

```
打印 DeviceSecret
写入 DeviceSecret
写入 SHA256 内部状态
```

---

# PC Compatibility

bind 文件设计必须满足：

```
无需额外工具
```

即：

```
PC 可以直接打开
```

未来 packer 可以：

```
read JSON
extract binding_id
```

因此：

```
不需要专门的 bind 读取工具
```

Python packer 只需：

```python
import json
data=json.load(open("device.bind"))
binding_id=data["binding_id"]
```

---

# Expected Deliverables

工程师必须交付：

1️⃣ `device_bindfile.c`
2️⃣ `device_bindfile.h`
3️⃣ 修改后的 `dap.mk`
4️⃣ Logel trace 截图
5️⃣ 设备生成的 `device.bind` 文件
6️⃣ 简短说明文档

---

# Verification Method

验证步骤：

1️⃣ 烧录新固件
2️⃣ 输入：

```
*#3271#
```

3️⃣ 生成 bindfile

4️⃣ PC 打开：

```
FileArray/device.bind
```

5️⃣ 验证 JSON 可读

---

# Pitfalls (必须阅读)

在开始之前，工程师必须复习：

```
pitfall.md
memory.md
```

特别注意以下历史问题：

---

## Pitfall 1 — dap.mk

新增源文件必须加入：

```
dap.mk
```

否则：

```
dap.a 不会生成
```

---

## Pitfall 2 — Trace 消失

所有日志必须使用：

```
SCI_TRACE_LOW
```

否则 Logel 无法看到。

---

## Pitfall 3 — 内存释放

不要：

```
free offset pointer
```

避免再次触发：

```
threadx_mem ASSERT
```

---

## Pitfall 4 — 文件路径

必须确保：

```
FileArray/
```

路径存在。

若不存在必须创建。

---

# Architecture Documentation

必须新增文档：

```
AIOS/docs/architecture/device_binding_phase1b.md
```

记录：

* bindfile 格式
* BindingID 算法
* 设备导出流程
* PC 读取流程
* 未来 App Store 设备注册

---

# Future Roadmap

完成 TM26 后：

下一阶段：

```
TM27
```

内容：

```
PC packer 读取 bindfile
生成 device-bound BIN2
```

最终目标：

```
Developer → App Store → Device
```

---

# Success Criteria

本任务成功标准：

```
设备生成 device.bind
PC 可读取 JSON
binding_id 与 Logel 输出一致
DeviceSecret 未泄露
Logel trace 可见
```

---

# Final Note

TM25 解决：

```
设备能产生 BindingID
```

TM26 解决：

```
设备能导出 BindingID
```

这两步完成后，设备绑定架构才真正开始具备工程落地能力。
