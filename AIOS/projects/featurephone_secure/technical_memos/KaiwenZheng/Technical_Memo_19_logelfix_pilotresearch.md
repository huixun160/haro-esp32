下面这份 **Technical Memo 19 — Logel Fix Pilot Research** 是给工程师直接执行的版本。
目标不是“顺手修一下日志”，而是把 **Mocor/Unisoc 平台上 DAP 模块接入 Logel/Trace 的机制彻底摸清楚**，为后续 TM15 的 Ed25519 调试、BIN2 验签和安全模块调试提供稳定观测能力。

先说结论：
TM15 现在真正的阻塞点不是 BIN2 结构本身，而是 **设备端 Ed25519 验签失败且 Logel trace 尚未验证通路**。当前反馈已经明确指出：

* `.bin2` 已能被识别
* 固件可正常编译
* `test_original.bin` 可运行
* `DAP_TracePrint` 已修正 varargs，但**Logel trace 还没在设备上验证**
* Ed25519 在设备端全部返回 `ERR-10: SIG FAIL`，推测是 32-bit ARM 上 64 位算术实现问题 

所以现在最正确的下一步，不是继续瞎改 Ed25519，而是：

> **先把日志链路打通，搞清楚别的模块怎么在 Logel 输出、怎么加前缀、怎么分类、怎么在设备端稳定看到。**

---

# Technical Memo 19

## Logel Fix Pilot Research — DAP Trace/Prefix Mechanism Investigation

**Project**
AIOS Secure Execution / DAP Security

**Phase**
Debug Infrastructure Recovery

**Owner**
AIOS Founding Team

**Assigned To**
Feature Phone Embedded Engineer

**Priority**
P0 — Debugging Infrastructure

**Related Work**
TM-015 BIN2 Secure Loader Integration

---

# 1. 背景

TM-015 已完成以下工作：

* BIN2 安全加载链已接入 DAP 固件
* `.bin2` 文件能被文件管理器识别
* 固件编译通过
* Python 打包工具已建立
* `test_original.bin` 能在设备上正常运行
* `DAP_TracePrint` 已修复 varargs 问题

但当前存在两个关键阻塞：

1. **Ed25519 验签在设备端全部失败**
2. **Logel trace 尚未确认真正输出成功**

反馈中已明确写出：

* `DAP_TracePrint` fix 已部署，但 **“not verified on device yet”**
* 下一步动作之一就是 **“Verify Logel traces”**，确认 `tm15_` 诊断日志是否真正出现 

这意味着：

> **我们现在没有可靠的设备端观测能力。**

没有稳定 trace，就无法分辨：

* 是 BIN2 header 解析错了
* 还是 payload hash 错了
* 还是 Ed25519 实现错了
* 还是签名输入范围错了
* 还是 packer 生成错了

所以必须先做一轮 **Logel/Trace 机制摸底研究**。

---

# 2. 本任务目标

本任务不是直接修复 Ed25519。
本任务目标是：

## 目标 A：搞清楚其它模块如何稳定输出 Logel trace

需要回答：

* 平台里哪些模块已经在 Logel 正常输出
* 它们通过什么宏/API 输出
* 输出前缀是怎么加的
* 输出等级/分类/tag 是怎么配置的
* 最终为什么能被 Logel 正确看到

## 目标 B：搞清楚 DAP 模块为什么当前看不到/不稳定

需要确认：

* `DAP_TracePrint` 当前实际链路是否通
* 是格式化问题、宏问题、编译开关问题，还是 trace 通道/注册问题
* DAP 模块是否天然不走某些标准 trace 路径

## 目标 C：形成一个最小、可复用的 DAP Trace 接入规范

产出一个后续工程师可复用的规范：

* 如何输出 trace
* 如何加统一前缀
* 如何做十六进制 dump
* 如何避免 varargs、宏展开、符号冲突等坑

---

# 3. 任务范围

重点研究对象：

### A. DAP 当前 trace 路径

至少包括：

* `DAP_TracePrint`
* `DAP_DBG`
* `DAP_DBG_ERR`
* `DAP_OSAssociated_unisoc.c`
* 与 trace/SCI/log 相关的适配层

### B. 平台中“已经能稳定输出 Logel”的其它模块

至少选 3 个正常工作的模块做对照分析，优先选择：

* 文件系统/FS 相关
* 网络/TCPIP 相关
* MMI/APP 相关
* 或底层 driver/HAL 中确认可见 trace 的模块

原则：

> **不要只看 DAP。一定要找“成功样本”。**

---

# 4. 工程师需要回答的核心问题

## Q1. 平台标准 trace 输出链路是什么？

必须回答：

* 最终输出到 Logel 的底层 API 是什么
  例如是否是 `SCI_TRACE_LOW`、`SCI_TRACE_ID`、其他变体
* 这些 API 的调用链是什么
* DAP 当前是否走在这条主链上

---

## Q2. 其它模块如何实现前缀？

必须梳理：

* 前缀是字符串拼接？
* 宏包装？
* trace group/module id？
* 编译期自动加前缀还是运行时手工加？

并回答：

> **如果我们想稳定输出 `tm19_` 或 `bin2_` 这类前缀，最标准的实现方式是什么？**

---

## Q3. DAP 为什么当前看不到稳定 trace？

需要定位是以下哪一类问题：

* varargs 格式化链断了
* 宏包装层丢参
* DAP 走的是不同 trace 通道
* 编译宏导致 release/feature build 下日志被裁掉
* trace 长度/格式不符合 Logel 解析要求
* DAP 模块没被归类到可见 trace 组

---

## Q4. 十六进制 dump 如何实现才可靠？

TM15 的下一个动作是看 Ed25519 输入输出。
所以必须回答：

> **如何在设备端可靠输出定长 hex dump，并被 Logel 正确接收？**

需要明确：

* 单条日志最大长度
* 是否需要分片
* 分片格式如何定义
* 是否会因为 `%02x` 大量展开导致格式化失败/截断

---

# 5. 交付物

工程师必须提交以下文档和样例。

## Deliverable 1

### `docs/logel_fix_pilot_research.md`

必须包含以下章节：

### 1. 平台 trace 机制总览

* 平台主 trace API 列表
* Logel 最终接收链路
* DAP 当前走的链路 vs 正常模块走的链路

### 2. 成功样本分析（至少 3 个模块）

每个模块写清：

* 代码位置
* 输出 API
* 前缀机制
* 输出样例
* 为什么能在 Logel 出现

### 3. DAP trace 现状分析

* 当前 `DAP_TracePrint` 的实现
* 已修复的 varargs 问题是什么
* 修复后仍未验证/未出现的原因猜测与证据

### 4. DAP 接入标准方案

必须给出一个明确方案：

* 使用哪个底层 API
* 如何封装 `DAP_LOGI / DAP_LOGE / DAP_HEXDUMP`
* 如何统一前缀
* 如何在 release/debug 下控制

### 5. 风险清单

例如：

* 日志过长被截断
* hex dump 破坏格式
* 宏冲突
* 其它模块符号冲突（TM15 里已有 SHA256 符号冲突案例）

---

## Deliverable 2

### `docs/logel_trace_feedback.md`

一页纸总结，必须能回答：

* DAP 当前是否已经能在 Logel 输出
* 如果不能，根因是什么
* 最小修复动作是什么
* 未来所有安全模块应该统一怎么打日志

---

## Deliverable 3

### 最小 PoC 代码

新增一个最小测试模块或在 DAP 中加一个最小 trace 测试点，验证三件事：

1. 固定字符串能否输出
   例如：`tm19_trace_alive`

2. 带参数格式化能否输出
   例如：`tm19_val=%d`

3. 十六进制 dump 能否输出
   例如：16 字节测试数组

必须在反馈文档里附：

* 代码位置
* 构建方式
* Logel 截图/文本结果

---

# 6. 执行步骤

## Step 1：找“成功样本”

不要先盯着 DAP。
先在全平台搜索：

* `SCI_TRACE_LOW`
* `SCI_TRACE_ID`
* `TRACE_`
* 其它显然会进入 Logel 的日志 API

找出 3 个“已知能在 Logel 出现”的模块，记录：

* 文件路径
* 宏/API
* 调用模式
* 典型前缀写法

---

## Step 2：梳理 DAP trace 当前链路

分析：

* `DAP_DBG`
* `DAP_DBG_ERR`
* `DAP_TracePrint`
* `DAP_OSAssociated_unisoc.c`

必须画出一条调用链：

```text
DAP_DBG
  ↓
DAP_TracePrint
  ↓
?
  ↓
SCI_TRACE_?
  ↓
Logel
```

如果中间断了，要指出断点在哪一层。

---

## Step 3：验证最小输出

先不要上 Ed25519 hex dump。
先做最小三条日志：

* 固定字符串
* 一个整数参数
* 一段 16 字节 hex

如果这三条都看不见，就说明不是 Ed25519 的问题，而是 trace 主链没通。

---

## Step 4：实现统一前缀 PoC

实现一个临时宏，例如：

```c
DAP_LOGI("tm19_xxx ...");
DAP_LOGE("tm19_err ...");
DAP_HEXDUMP("tm19_sig", buf, len);
```

验证：

* 前缀是否稳定出现
* 多模块是否会混淆
* 长日志是否截断

---

# 7. 验收标准

本任务完成的标准不是“写了一堆分析”，而是：

## 必须满足以下 4 条

### 1. 在 Logel 中至少能看到一条来自 DAP 的固定字符串日志

例如：

```text
tm19_trace_alive
```

### 2. 在 Logel 中至少能看到一条来自 DAP 的格式化参数日志

例如：

```text
tm19_val=1234
```

### 3. 在 Logel 中至少能看到一条来自 DAP 的十六进制 dump 日志

长度至少 16 字节，格式清晰、可读。

### 4. 文档能明确告诉后续工程师：

> “以后 DAP/安全模块统一怎么打日志，怎么加前缀，怎么做 hex dump。”

---

# 8. 不要做的事情

本阶段**不要**继续在 Ed25519 算法上深挖。
因为当前阻塞不是“算法一定错”，而是：

> **你没有可靠证据链。**

没有 Logel trace，继续改算法等于盲人修表。

本阶段也**不要**扩展到：

* DeviceSecret 新功能
* BIN2 绑定
* PAC 保护
* App Store 后端

这些都会分散注意力。

---

# 9. 时间要求

建议时间盒：

```text
2 working days
```

Day 1：

* 成功样本摸底
* DAP trace 调用链梳理

Day 2：

* 最小 PoC
* Logel 截图/结果
* 反馈文档

---

# 10. 第一性原理总结

现在不是缺“更多安全代码”。

缺的是：

> **一个可信的、可观测的调试通道。**

没有这个，后面：

* BIN2
* Ed25519
* DeviceSecret binding
* DAP core blob

全部都会变成黑箱。

所以 TM19 的目标非常明确：

> **先打通 DAP → Logel 的 trace 主链，再谈下一步安全实现。**

