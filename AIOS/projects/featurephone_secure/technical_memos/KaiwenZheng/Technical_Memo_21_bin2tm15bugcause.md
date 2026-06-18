---

**Title:** BIN2 Signature Verification Failure Root Cause Isolation and Fix Plan

**Project:** AIOS Feature Phone Platform

**Subsystem:** DAP / Security

**Author:** AIOS Core Architecture

**Priority:** HIGH

**Date:** 2026-03-10

---

## Background

TM-15 已经将 BIN2 secure loader 主链接入 DAP，TM-20 已经打通了 DAP → Logel 的 trace 链路，当前系统已经具备观察 BIN2 执行路径的能力。

目前设备端的实际运行结果表明：

* `test_original.bin` 可以正常执行
* `test_valid.bin2`、`test_tampered.bin2`、`test_badsig.bin2` 全部在 Ed25519 验签阶段失败
* 日志中可见：

  * `tm15_BIN2 detected (early magic check)`
  * `tm15_BIN2 full verification starting...`
  * `[bin2] tm15_bin2_verify: version=1, payload_size=572, key_id=0, binding=0`
  * `[DAP] tm15_sig_verify: total_size=684, hdr_size=48, sig_size=64, payload_size=572`
  * `[DAP] tm15_sig_verify: ed25519_verify returned -1 (0=OK, -1=FAIL)`
  * `[DAP] tm15_BIN2 verify failed: signature`
  * `DAP_GUI_ShowAlertText: [ERR-10:BIN2 sig fail]`

这说明：

1. BIN2 检测成功
2. 文件完整读取成功
3. Header 解析成功
4. 验签输入阶段已经进入
5. 失败点集中在 **signature verification**

从这组证据看，当前最可能的问题不是 loader 主链、不是文件读取、不是 BIN2 基本结构，而是：

> **设备端参与验签的 message 与 PC 端签名时的 message 不一致。**

这是本 memo 要解决的核心问题。

---

## Objective

本任务目标如下：

1. 用最小实验集精确定位 BIN2 验签失败根因，明确是：

   * 签名覆盖范围不一致
   * Header/Signature/Payload 偏移错误
   * 设备端拼接 message 错误
   * Ed25519 实现/移植问题
2. 基于实验结果修复 BIN2 验签失败问题，使 `test_valid.bin2` 通过、`test_tampered.bin2` 和 `test_badsig.bin2` 拒绝执行。
3. 在整个修复过程中，**保证 Logel trace 持续可用**，所有关键路径都能被追踪到，避免再次出现“代码改了但设备端不可观测”的错误。

---

## Current State

当前已知状态如下：

### 1. BIN2 基本链路已经通

设备 trace 显示：

* `File size: 684 bytes`
* `FileRead OK: requested=352, actual=352`
* `FileRead OK: requested=684, actual=684`
* `Full file loaded: 684 bytes`
* `tm15_BIN2 detected (early magic check)`
* `tm15_BIN2 full verification starting...`

说明：

* 文件读取无误
* BIN2 格式识别无误
* Header 早期检测无误
* 完整文件进入 RAM 无误

### 2. Header 结构基本正确

设备 trace 中出现：

* `total_size=684`
* `hdr_size=48`
* `sig_size=64`
* `payload_size=572`

并满足：

```text
48 + 64 + 572 = 684
```

此外，Header dump 为：

```text
header[0..7] = 42 49 4e 32 01 00 30 00
```

可解释为：

* `42 49 4E 32` = `"BIN2"`
* `01 00` = version 1
* `30 00` = header size 48

说明 Header 本身没有明显格式错误。

### 3. 失败集中在 Ed25519 验签

设备 trace 中出现：

```text
ed25519_verify returned -1 (0=OK, -1=FAIL)
```

并且三类样本：

* `test_valid.bin2`
* `test_tampered.bin2`
* `test_badsig.bin2`

全部失败。

这是一条非常强的证据：如果连 `test_valid.bin2` 都失败，那么大概率不是 tamper 检测逻辑问题，而是：

> **valid 样本在设备端验证输入就已经不一致。**

### 4. Logel trace 当前已经打通

TM-020 反馈已经确认：

* 平台标准 trace API 是 `SCI_TRACE_LOW`
* DAP 当前 trace 链理论可通
* `[bin2]` 前缀和 `tm20_` PoC 已在设备端可见
* 当前阻塞不再是 trace 链，而是 TM-15 验签本身

因此，后续所有实验和修复必须建立在：

> **保持现有 Logel trace 可见、可复盘、可比较**

的前提上。

---

## Scope

本任务包括：

1. 复现实验并采集设备端 BIN2 验签 trace
2. 明确 PC 端签名输入与设备端验签输入是否一致
3. 添加 message/hash 级别的诊断日志
4. 修复签名输入拼接/偏移/覆盖范围错误
5. 验证 `valid / tampered / badsig` 三组样本行为正确
6. 保持并增强 Logel trace 规范，确保后续改动可追踪

---

## Out of Scope

本任务不包括：

* DeviceSecret 设备绑定
* BIN2 payload 加密
* PAC 中 DAP core 加密/运行时解密
* App Store 后端
* Key rotation / revocation
* 更换 BIN2 整体协议设计

本任务只解决：

> **Phase-0 中 BIN2 的签名验签失败问题。**

---

## Constraints

1. 不允许破坏现有 DAP loader 主链。
2. 不允许关闭或绕过 Logel trace 来“硬改通过”。
3. 任何修改都必须保留可观测日志，尤其是：

   * header 解析
   * signed region 长度
   * message/hash 对比
   * verify 返回值
4. 现有编译方式必须保持可用：

```bash
make\make_cmd\make -r -R MAKESHELL=CMD p=ums9117_240X320BAR_64MB_ML MODULES=dap JOB=16
mm ums9117_240X320BAR_64MB_ML new
```

5. 调试日志要控制长度，避免 Logel 截断；单条日志尽量小于 128 字符。

---

## Expected Deliverables

1. 修改后的 `bin2_loader.c` / `bin2_crypto.c`，增加签名输入和 hash 诊断逻辑。
2. 一份根因定位文档：`docs/tm15_sigfail_rootcause.md`
3. 一份设备验证记录：`docs/tm15_sigfix_validation.md`
4. 一组通过测试的 Logel 截图或导出的文本，包含：

   * `test_valid.bin2` 通过
   * `test_tampered.bin2` 失败
   * `test_badsig.bin2` 失败

---

## Verification Method

* [ ] **Build verification:** 使用现有命令编译通过，0 link error，0 undefined symbol
* [ ] **Device test:**

  1. 运行 `test_original.bin`，确认旧 BIN1 仍正常运行
  2. 运行 `test_valid.bin2`，应通过验签并进入执行
  3. 运行 `test_tampered.bin2`，应在验签或 payload_hash 处失败
  4. 运行 `test_badsig.bin2`，应在验签处失败
* [ ] **Log verification:** 必须能看到以下模式：

  * `tm15_BIN2 detected`
  * `tm15_BIN2 full verification starting`
  * `tm15_sig_verify`
  * `tm15_msg_hash`
  * `tm15_BIN2 verify ok` 或 `tm15_BIN2 verify failed:*`
* [ ] **Cross-check verification:** PC 端 packer 输出的 message/hash 与设备端日志中的对应值一致

---

## Potential Risks

* **Risk 1: 设备端签名输入仍不透明，继续盲改。**
  缓解：先加 message/hash 级别 trace，再改逻辑。

* **Risk 2: 修改代码后 Logel trace 再次丢失。**
  缓解：所有新增日志统一使用已验证过的 trace 宏路径，不允许再引入未定义宏或绕开 `SCI_TRACE_LOW` 的私有链路。

* **Risk 3: Ed25519 实现本身在 32-bit ARM 上存在兼容性问题。**
  缓解：先用 message/hash 对齐排除输入问题；若输入一致仍失败，再把问题收敛到 crypto 实现。

* **Risk 4: 日志过长导致 Logel 截断，误判数据。**
  缓解：只打印前 8 或 16 字节；长内容用多条短日志分片输出。

---

## References

* TM-015 BIN2 Secure Loader
* TM-019 Logel Trace Pilot
* TM-020 Logel Trace Fix Feedback
* `DAP_Loader_unisoc.c`
* `bin2_loader.c`
* `bin2_crypto.c`
* `DAP_DebugLog.h`
* `DAP_OSAssociated_unisoc.c`
* Technical Memo Template 

---

## Execution Plan

### Step 1 — 固化日志规则，禁止再次把 trace 搞丢

先统一规则：

1. 所有 BIN2 调试日志统一前缀：

   * `[bin2]` 用于 loader/协议层
   * `tm15_` 用于本次问题定位
2. 所有日志必须走已验证可用的链路：

   * `DAP_DBG(...)`
   * `DAP_DBG_ERR(...)`
   * 最终进入 `DAP_TracePrint → SCI_TRACE_LOW`
3. 不允许再引入未定义宏，例如之前的 `BIN2_LOG` 链接错误。
4. 如果新增宏，必须在单一头文件中定义，并确保所有使用文件都 include 到。
5. 任何代码修改前，先确认最小日志 still alive：

   * `tm15_trace_alive`
   * `tm15_val=42`

**验收点：**
设备端先看到最小 trace，再进入后续实验。

---

### Step 2 — 明确“签名覆盖范围”并打印设备端实际输入摘要

按当前 BIN2 协议，签名必须覆盖：

```text
header_without_signature + payload
```

不能只签 header，也不能把 signature 字段本身包含进去。

工程师必须在设备端打印以下信息：

1. `hdr_size`
2. `sig_size`
3. `payload_size`
4. `payload_offset`
5. `signed_region_len`

并打印：

* `header[0..15]`
* `signature[0..15]`
* `payload[0..15]`

**注意：**
只打印前 8～16 字节，不要整个 dump。

**推论：**
如果 signed region 长度或偏移有误，验签必然失败。

---

### Step 3 — 在 PC 端 packer 增加完全同口径的对照输出

修改 Python packer，新增 `--debug` 模式，输出：

1. `hdr_size`
2. `sig_size`
3. `payload_size`
4. `payload_offset`
5. `signed_region_len`
6. `header[0..15]`
7. `payload[0..15]`
8. `sha256(header_without_signature + payload)` 的前 8～16 字节

然后设备端做同样的 `sha256(signed_region)` 并打印：

```text
tm15_msg_hash[0..7] = ...
```

**目标：**
先不争论 Ed25519 对不对，先回答这个问题：

> **PC 签名时的 message 和设备验签时的 message，到底是不是同一块数据？**

---

### Step 4 — 先用 message hash 对齐排除 80% 问题

这是本次实验最关键的一步。

#### 预期结果 A：PC 和设备的 message hash 不一致

说明问题在：

* signed region 拼接错误
* header_size 理解不一致
* signature 字段未排除
* payload_offset 计算错误
* 设备端使用了 `total_size` 而不是 `header_without_signature + payload`

此时**不要继续碰 Ed25519 库**，先修 signed region。

#### 预期结果 B：PC 和设备的 message hash 一致，但 verify 仍失败

这时问题才收敛到：

* Ed25519 设备端实现不兼容
* 签名格式处理错误
* 公钥/签名字节序或长度处理错误

此时再转入 crypto 实现层排查。

---

### Step 5 — 检查最可能的 bug：设备端是否错误包含了 signature 自身

当前最可疑问题是：

设备端 verify 可能错误地对以下数据做了校验：

```text
header + signature + payload
```

而不是：

```text
header_without_signature + payload
```

工程师必须明确写出当前代码中的 signed region 构造方式，并与 packer 端完全对照。

**这是必须写进反馈文档里的核心内容。**

---

### Step 6 — 如果 signed region 已对齐，再验证 Ed25519 实现

只有在 Step 4 证明 PC/设备 message hash 一致之后，才进入这一步。

要检查：

1. 公钥字节是否与 PC 完全一致
2. 签名字节是否与 PC 完全一致
3. 设备端 verify 调用参数顺序是否正确
4. Ed25519 C 实现是否对 32-bit ARM 有特殊限制

此时可加最小实验：

* 在设备端对一组**固定测试向量**做 verify
* 测试向量来自 PC 端生成的最小 message/signature/pubkey 三元组
* 不依赖 BIN2 文件，仅验证 crypto 函数本身

如果固定测试向量都失败，问题就不在 BIN2，而在 Ed25519 实现。

---

### Step 7 — 修复后重新验证三类样本

修复后必须按顺序验证：

#### Case 1: `test_valid.bin2`

预期：

* detect ok
* verify ok
* 继续进入旧 BIN1 执行路径
* 应用正常运行

#### Case 2: `test_tampered.bin2`

预期：

* detect ok
* verify fail 或 payload_hash fail
* 拒绝执行

#### Case 3: `test_badsig.bin2`

预期：

* detect ok
* verify fail
* 拒绝执行

并保留完整 Logel 证据。

---

## Engineering Notes (Must Follow)

1. **任何代码修改都必须保留 Logel 可观测性。**
   不允许“为了简化先删掉日志”。这会让问题重新回到黑箱状态。

2. **不要再引入未定义日志宏。**
   所有新增日志要么复用现有 DAP trace 宏，要么在统一头文件里定义并全量 include。

3. **日志必须短小、结构化、可比对。**
   推荐格式：

   * `tm15_hdr sz=48 sig=64 payload=572`
   * `tm15_msg_hash[0..7]=xx xx xx xx xx xx xx xx`
   * `tm15_sig[0..7]=...`
   * `tm15_pubkey[0..7]=...`

4. **修复顺序必须是：**

   1. 保 trace
   2. 对齐 message
   3. 再查 Ed25519

   不允许反过来。

---

## Expected Final Output

本任务完成后，工程师必须给出一个明确结论：

### 结论格式必须是以下之一：

#### 结论 A

> 根因是 signed region 不一致，已修复；Ed25519 实现本身正常。

或

#### 结论 B

> PC/设备 signed region 一致，根因是设备端 Ed25519 实现问题；已通过替换/修正实现解决。

不能只给“现在能跑了”这种没有解释力的结果。

---


