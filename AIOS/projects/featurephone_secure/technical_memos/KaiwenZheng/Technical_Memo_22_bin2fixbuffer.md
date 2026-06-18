---

**Title:** Logel Trace Collection and Memory Leak Root Cause Isolation for BIN2/DAP

**Project:** AIOS Feature Phone Platform

**Subsystem:** DAP / Security / Build

**Author:** AIOS Core Architecture

**Priority:** HIGH

**Date:** 2026-03-11

---

## Background

TM-21 已完成大部分诊断代码与根因分析准备工作，但在进入设备验证阶段时被 **内存泄漏问题**阻断，当前状态为 **PARTIAL — 暂停（内存泄漏 bug 阻断）**。反馈中已经明确：

* `DAP_DBG / DAP_DBG_ERR → DAP_TracePrint → SCI_TRACE_LOW` 链路可用
* `bin2_crypto.c` 已加入完整的 `tm15_` 诊断 trace
* `bin2_pack.py` 已加入 `--debug` 模式，PC 端输出与设备端格式对齐
* TM-21 尚未完成设备侧 `tm15_msg_hash` 抓取与 PC 对比
* 当前优先阻塞是 **内存泄漏**，需先处理，再恢复 TM-21 的签名链验证工作 

因此，TM-22 的任务不是直接“修完内存泄漏”，而是先建立一个**最小、可复盘、可比较**的 Logel trace 采集规范，让工程师先告诉我们应该在 Logel 中检索哪些关键字，并按固定格式返回截图/日志，再逐步定位内存泄漏根因。

同时必须保持一个明确立场：

> **对“签名链已通”暂不下结论。**
> 只有在恢复 TM-21 并完成 `tm15_msg_hash` 设备/PC 对比后，才能判断签名链是否真的成立。当前阶段只能说：拒绝路径存在、诊断链存在，但签名链最终闭环尚未验证。 

---

## Objective

本任务目标分两阶段：

### 阶段 A：先定义 Logel trace 采集规范

让工程师先明确：

1. 运行 `test_valid.bin2` 时，Logel 应该检索哪些关键字
2. 运行 `test_original.bin` 时，Logel 应该检索哪些关键字
3. 运行失败到蓝屏/ASSERT 前后，需要截取哪一段 trace
4. 返回截图时应包含哪些字段，避免无效截图

### 阶段 B：基于返回 trace 再定位内存泄漏

在收到工程师提供的 Logel 关键截图/导出文本后，再进行：

* 内存分配/释放路径分析
* BIN1/BIN2 差异路径分析
* `SCI_Release_Buffer` assert 根因定位
* 修复计划制定

---

## Current State

当前已知状态如下：

1. **TM-21 被内存泄漏阻断**
   反馈明确写明：设备运行中出现内存泄漏，必须优先处理，否则所有后续验证结果不可靠。

2. **签名链只完成到“诊断准备”阶段**
   当前已完成：

   * 设备端 `tm15_sig_verify` 相关 trace
   * 设备端 `tm15_msg_hash[0..7]`
   * PC 端 `--debug` 对照输出
   * `signed region` 构造逻辑分析
     但尚未完成设备实测比对，也尚未形成最终“结论 A/B”。

3. **TM-22 需要先要 trace，再谈修复**
   目前如果直接改代码，很容易再次进入“黑箱修 bug”的错误路径。
   必须先固定 Logel 采集关键词和截图范围。

---

## Scope

本任务包括：

1. 定义 Logel 检索关键词列表
2. 定义截图/日志返回格式
3. 指导工程师抓取 `test_valid.bin2` 与 `test_original.bin` 的关键 trace
4. 基于 trace 判断内存泄漏最可能发生的阶段
5. 制定后续内存泄漏修复路线

---

## Out of Scope

本任务不包括：

* 立即修改 Ed25519 实现
* 立即修改 DeviceSecret 模块
* 立即修改 BIN2 协议
* 立即修复 PAC 中 DAP 反逆向机制
* App Store / 后端 / 设备绑定

TM-22 只解决：

> **如何先把 Logel trace 采对，然后用这些 trace 去定位 BIN2/内存泄漏问题。**

---

## Constraints

1. 所有结论必须建立在 Logel trace 证据之上。
2. 不允许再引入新的未定义日志宏或破坏现有 trace 链。
3. 不能因为“怀疑内存泄漏”就放弃对签名链的怀疑；两者需要并行区分。
4. 需要兼容当前编译/烧录流程，不增加过大调试开销。

---

## Expected Deliverables

1. 一份工程师返回的 **Logel 检索关键词说明**
2. 一组 `test_valid.bin2` 的 Logel 截图/文本
3. 一组 `test_original.bin` 的 Logel 截图/文本
4. 一份 `docs/tm22_memoryleak_trace_analysis.md`，总结：

   * 哪些 trace 已经抓到
   * 哪些 trace 缺失
   * 内存泄漏最可疑阶段
   * 签名链是否仍需继续怀疑

---

## Verification Method

* [ ] **Build verification:** 当前版本可正常编译并烧录
* [ ] **Device test:**

  1. 运行 `test_original.bin`，抓取正常路径 Logel
  2. 运行 `test_valid.bin2`，抓取失败路径 Logel
* [ ] **Log verification:** 返回的截图/文本必须包含本 memo 定义的关键词
* [ ] **Comparison verification:** 能够直接比较 BIN1 正常路径与 BIN2 异常路径的分叉点

---

## Potential Risks

* **Risk 1 — 返回截图不完整，无法定位问题**
  缓解：先定义关键词和截图范围，禁止“随手截一点”。

* **Risk 2 — 误把内存泄漏当成签名链问题，或反之**
  缓解：强制同时抓 BIN1 和 BIN2 两条路径做对照。

* **Risk 3 — 调试日志被截断或遗漏关键行**
  缓解：优先返回文本导出；若只能截图，必须保证覆盖“失败前后连续 30～50 行”。

* **Risk 4 — 工程师改代码时破坏现有 Logel trace 链**
  缓解：TM-22 第一阶段原则上先不改逻辑，只补充 trace 和采集证据。

---

## References

* TM-021 Feedback — BIN2 Signature Verification Failure Root Cause Isolation 
* TM-020 Feedback — Logel Trace 已打通（对话上下文）
* `Third-party/DAP/security/bin2_crypto.c`
* `AIOS/tools/bin2_packer/bin2_pack.py`
* `DAP_DebugLog.h`
* `DAP_OSAssociated_unisoc.c`

---

## Execution Plan

### Step 1 — 先让工程师返回 Logel 检索关键词

工程师必须先明确，并回传给你一个简短说明文档，内容包括：

#### A. 运行 `test_valid.bin2` 时建议检索的关键词

至少包含：

```text
tm15_
[bin2]
verify
payload
hash
sig
pubkey
hdr
msg_hash
ERR-10
ASSERT
free
alloc
Release_Buffer
Running_AP
GetBSSSpace
```

#### B. 运行 `test_original.bin` 时建议检索的关键词

至少包含：

```text
DAP_ExecuteAP
FileRead
GetBSSSpace
entry
alloc
free
Running_AP
```

#### C. 如果内存问题是 SCI buffer / heap 问题，再额外检索：

```text
SCI_Release_Buffer
SCI_ALLOC
SCI_FREE
threadx_mem
free_ptr
```

**输出要求：**
工程师先不用修逻辑，只需要告诉我们：

> “在当前代码和当前日志前缀下，Logel 中应该搜哪些关键字最容易抓到问题。”

---

### Step 2 — 让工程师返回两组最小必要 trace

#### Trace Set 1 — `test_original.bin`

目的是建立“正常路径基线”。

必须返回：

* 从点击执行开始，到应用正常进入/退出为止
* 至少包含：文件读取、BSS、入口执行、释放路径
* 建议覆盖连续 30～50 行

#### Trace Set 2 — `test_valid.bin2`

目的是建立“异常路径”。

必须返回：

* 从点击执行开始，到蓝屏/ASSERT/错误返回前结束
* 至少包含：BIN2 detect、header parse、verify start、msg_hash、以及最后失败前 30～50 行

**关键原则：**

> 两组 trace 必须可对照，才能看出 BIN2 路径在哪一步和 BIN1 正常路径分叉。

---

### Step 3 — 让工程师按固定格式截图/导出

要求工程师返回：

#### 方案 A（优先）

Logel 文本导出或复制文本

#### 方案 B（备选）

截图，但必须满足：

1. 有时间顺序
2. 有关键词上下文
3. 至少覆盖失败前后连续日志
4. 不要只截单条 `ERR-10` 或单条 `ASSERT`

**禁止无效返回：**

* 只给一张蓝屏照片
* 只给最后一条 assert
* 只给一条 `tm15_msg_hash`

---

### Step 4 — 基于 trace 判断问题先归类，而不是先修代码

拿到 trace 后，优先判断是哪一类问题：

#### 类别 A：签名链仍未通

表现为：

* `verify` 仍失败
* `tm15_msg_hash` 与 PC 不一致
* 还没进入 BIN2 成功路径

#### 类别 B：签名链可能已通，但成功路径后内存异常

表现为：

* 已经看到 `verify ok`
* 随后在 `GetBSSSpace / relocate / entry / free` 附近崩溃
* 或出现 `SCI_Release_Buffer` / `threadx_mem` assert

#### 类别 C：日志不足，无法判断

表现为：

* 关键关键词缺失
* 没有失败前后连续日志
* 没有 BIN1 对照组

只有完成归类之后，才进入真正的修复。

---

### Step 5 — 内存泄漏/内存错误后续定位方向（先定义，不立刻开工）

在拿到 trace 前，先告诉工程师，后续最可能检查的点会是：

1. **BIN2 unwrap 后的 buffer 所有权**

   * `full file buffer`
   * `payload pointer`
   * `Running_AP`
   * 退出路径最终 free 的到底是哪一个

2. **verify 成功路径和失败路径的 cleanup 差异**

   * 是否双重释放
   * 是否 free 了偏移后的 pointer
   * 是否在 error path 和 success path 各 free 一次

3. **BIN1 和 BIN2 在 `GetBSSSpace` / `entry` 前后内存布局是否一致**

   * BIN1 正常而 BIN2 异常，说明分叉点就在 BIN2 unwrap 之后

---

## Required Engineer Feedback Format

工程师返回给你的反馈，至少应包含以下 5 项：

1. **Logel 检索关键词列表**
2. **`test_original.bin` trace**
3. **`test_valid.bin2` trace**
4. **他自己基于 trace 的初步判断：**

   * 更像签名链问题
   * 更像内存问题
   * 还是证据不足
5. **他认为下一步最该加的 3 条日志是什么**

---

## Decision Rule After Feedback

收到工程师返回的 trace 后，按以下规则推进：

### 如果看到：

```text
verify fail
tm15_msg_hash 与 PC 不一致
```

则优先恢复 TM-21，继续签名链诊断。

### 如果看到：

```text
verify ok
随后进入 BIN2 成功路径
最后在 free / ASSERT / threadx_mem 附近崩溃
```

则正式进入 TM-22 第二阶段，按内存所有权/释放路径修复。

### 如果看不到关键节点

则先补 trace，不进入修复。

---

## Final Note

TM-22 的第一步不是修 bug，而是：

> **先让工程师告诉我们在 Logel 里该搜什么，并按固定格式把证据拿回来。**

没有这一步，后面的内存泄漏修复只会重复 TM-21 之前“黑箱调试”的老路。

