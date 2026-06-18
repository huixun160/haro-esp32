# Technical Memo 27 — Device-Bound BIN2 via Bindfile

**Title:** Device-Bound BIN2 Implementation (Bindfile → Packer → Loader Check)

**Project:** AIOS Feature Phone Platform

**Subsystem:** DAP / BIN2 Loader / Security

**Author:** AIOS Core Architecture

**Priority:** HIGH

**Date:** 2026-03-12

---

# Background

在 TM25 与 TM26 中，我们已经完成：

1️⃣ **DeviceSecret 生成并持久化**

2️⃣ **BindingID 派生**

```
BindingID = SHA256("AIOS-BIND-V1" || DeviceSecret)[0..15]
```

3️⃣ **Logel 成功输出 BindingID**

4️⃣ **设备成功导出 bind 文件**

```
FileArray/device.bind
```

示例：

```json
{
  "version":1,
  "binding_alg":"SHA256-128",
  "binding_id":"9f2a7c41e3d1b2a4c8b7d9e1f0a12345",
  "device_model":"ums9117_240X320BAR_64MB_ML"
}
```

这意味着：

```
DeviceSecret → BindingID → bindfile
```

链路已经稳定。

下一阶段必须完成：

```
bindfile → PC packer → device-bound BIN2 → loader verify
```

即 **设备绑定闭环**。

---

# Objective

实现 **device-bound BIN2**。

确保：

```
A设备打包 → A设备运行成功
A设备打包 → B设备运行失败
```

同时保持：

* 旧 BIN2 仍然兼容
* 原有签名机制不被破坏
* Loader 改动最小

---

# System Architecture

最终执行链：

```
device
 └─ generate bindfile
      ↓
PC
 └─ packer reads bindfile
      ↓
device-bound BIN2
      ↓
device loader verify
      ↓
payload execute
```

---

# Step 1 — 定义 bindfile 与 BIN2 header 契约

必须冻结协议。

### bindfile 字段

```
version
binding_alg
binding_id
device_model
```

仅允许包含：

```
binding_id
```

绝不允许：

```
DeviceSecret
```

bindfile 是 **公开设备描述文件**，不是密钥。

---

### BIN2 header 新增字段

仅新增两个字段：

```
binding_mode
binding_id[16]
```

定义：

```
binding_mode = 0 → UNBOUND
binding_mode = 1 → DEVICE_BOUND
```

结构示例：

```
struct BIN2_Header {

    magic
    version
    header_size
    payload_size
    payload_hash

    signature[64]

    binding_mode
    binding_id[16]

}
```

注意：

```
binding_id 位于签名保护范围内
```

即签名覆盖：

```
header_without_signature + payload
```

---

# Step 2 — PC Packer 读取 bindfile

新增 packer 参数：

```
--bind-file device.bind
```

示例：

```
python bin2_pack.py pack \
    --in app.bin \
    --out app_bound.bin2 \
    --bind-file device.bind \
    --key private_key.bin
```

packer 执行流程：

1️⃣ 读取 bindfile

```
binding_id
binding_alg
```

2️⃣ 构造 BIN2 header

```
binding_mode = DEVICE_BOUND
binding_id = bindfile.binding_id
```

3️⃣ 计算 payload_hash

4️⃣ 生成签名

签名输入：

```
header_without_signature + payload
```

5️⃣ 输出新的 BIN2

---

### Python 读取 bindfile 示例

```python
import json

with open("device.bind") as f:
    data=json.load(f)

binding_id=data["binding_id"]
```

不需要单独 bind reader 工具。

直接嵌入 packer。

---

# Step 3 — Loader Binding Check

设备端 loader 在 **签名验证成功后** 增加 binding check。

执行流程：

```
verify signature
↓
if binding_mode == UNBOUND
    continue

if binding_mode == DEVICE_BOUND
    derive local BindingID
    compare header.binding_id
```

逻辑：

```
match → execute payload
mismatch → reject
```

新增错误码：

```
ERR-11 : BIN2 BIND FAIL
```

---

# Loader Pseudocode

```
verify_signature()

if header.binding_mode == UNBOUND
    goto EXECUTE

derive_binding_id(local)

if memcmp(local, header.binding_id) != 0
    return ERR-11

EXECUTE:
run payload
```

---

# Critical Engineering Pitfalls

工程师必须阅读。

## Pitfall 1 — 指针偏移错误

BIN2 payload 并不是文件起点。

真实 payload：

```
payload_ptr =
    full_buf
    + header_size
```

绝对不能把：

```
full_buf
```

当作：

```
TApplication*
```

否则会导致：

* relocation 错误
* BSS 错误
* entry point 偏移错误

---

## Pitfall 2 — 签名覆盖范围

签名必须覆盖：

```
header_without_signature + payload
```

绝不能包含：

```
signature 自身
```

否则 packer 与 loader 会不一致。

---

## Pitfall 3 — 内存释放错误

禁止：

```
SCI_FREE(payload_ptr)
```

必须：

```
SCI_FREE(full_buf)
```

否则会再次触发：

```
threadx_mem ASSERT
SCI_Release_Buffer
```

---

## Pitfall 4 — dap.mk

新增文件必须加入：

```
Third-party/DAP/dap.mk
```

否则：

```
dap.a 无法生成
```

---

## Pitfall 5 — trace 丢失

必须继续使用：

```
SCI_TRACE_LOW
```

示例：

```
[bind] header_binding_id=...
[bind] local_binding_id=...
[bind] binding_match=1
```

否则 Logel 无法追踪。

---

## Pitfall 6 — header 冻结

BIN2 header **不要再随意增加字段**。

本阶段只允许新增：

```
binding_mode
binding_id
```

否则：

```
payload_offset
header_size
签名范围
```

全部会被破坏。

---

# Verification Plan

必须完成以下测试。

---

### Case 1 — Unbound BIN2

```
test_unbound.bin2
```

A设备：成功
B设备：成功

---

### Case 2 — Bound BIN2

使用 A设备 bindfile 打包：

```
test_bound_A.bin2
```

A设备：成功

---

### Case 3 — Cross Device

```
test_bound_A.bin2
```

B设备执行：

```
ERR-11
```

---

### Case 4 — Tampered

```
test_tampered_bound.bin2
```

返回：

```
ERR-10
```

---

# Deliverables

工程师必须提交：

1️⃣ 修改后的 `bin2_pack.py`
2️⃣ 更新后的 `bin2_header.h`
3️⃣ loader binding check 代码
4️⃣ dap.mk 更新
5️⃣ Logel trace 截图
6️⃣ 4 个测试 BIN2 样本

---

# Success Criteria

本任务完成标准：

```
device.bind 可导出
packer 成功读取 bindfile
生成 device-bound BIN2
A设备运行成功
B设备运行失败
签名机制保持正常
```

---

# Roadmap

TM27 完成后：

下一阶段：

```
TM28
```

内容：

```
BIN2 payload encryption
DAP code obfuscation
```

最终目标：

```
DAP + BIN2
完全不可逆向
```
