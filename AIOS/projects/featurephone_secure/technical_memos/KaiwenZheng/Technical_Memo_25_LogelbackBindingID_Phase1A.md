---

# Technical Memo 25 — Logel 返回 BindingID（Phase 1A）

**Title:** BindingID Logel Exposure Pilot for Offline Device Binding

**Project:** AIOS Feature Phone Platform

**Subsystem:** DAP / Security / Build

**Author:** AIOS Core Architecture

**Priority:** HIGH

**Date:** 2026-03-11

---

## Background

BIN2 Phase-0 已经完成：

* `test_original.bin` 可运行
* `test_valid.bin2` 可运行
* `test_tampered.bin2` 被拒绝
* `test_badsig.bin2` 被拒绝

这说明当前系统已经具备：

* 签名验证
* 篡改拒绝
* BIN1 / BIN2 双栈兼容

但当前仍然缺少：

```text
跨设备不可复制
```

我们原本想一步完成 BIN2 设备绑定，但这不现实。
正确做法是拆成多个可验证阶段：

### 阶段拆解

1. **功能机通过 Logel 返回 BindingID**
2. **功能机在文件系统中生成 `.bind` 文件**
3. **将 `.bind` 文件拷贝到 PC，模拟 packer 打包新的 BIN2 并验证**

本 memo 只做第 1 步：

> **让设备本机稳定计算并通过 Logel 输出 BindingID。**

这一步的意义不是最终交付，而是验证：

* DeviceSecret → BindingID 派生逻辑正确
* DAP / Security 新代码可稳定编译进 dap.a
* Logel trace 对安全模块可持续追踪

---

## Objective

本任务必须完成以下目标：

1. 在设备端基于现有 DeviceSecret 派生出 BindingID
2. 通过 Logel 稳定输出 BindingID（或其分段十六进制表示）
3. 确保不会泄露 DeviceSecret 明文
4. 修复当前编译错误，确保 DAP 安全模块重新可编译
5. 明确后续 `.bind` 文件导出所需的数据结构与接口雏形

---

## Current State

当前已知状态：

### 已完成

* DeviceSecret 已能生成、持久化、重启读取
* BIN2 secure loader 已打通
* Logel trace 已经打通，可用于调试安全模块
* 之前已经验证过 `SCI_TRACE_LOW` 这条路径是平台标准 trace 输出路径

### 当前阻塞

当前工程编译失败：

```text
[dap] "Third-party/DAP/security/device_binding.c", line 16: Error:  #5: cannot open source input file "dap_sha256.h": No such file or directory
[link] Fatal error: L6002U: Could not open file build/ums9117_240X320BAR_64MB_ML_builddir/lib/dap.a: No such file or directory
```

这说明两个问题：

1. `device_binding.c` 依赖头文件路径错误或文件不存在
2. DAP 静态库 `dap.a` 没生成，说明 **DAP 模块编译链已经中断**

---

## Scope

本任务包括：

1. 修复 `dap_sha256.h` 缺失/路径错误导致的编译失败
2. 修复 `dap.a` 未生成问题
3. 在 `device_binding.c` 中实现 BindingID 派生
4. 在设备端通过 Logel 输出 BindingID
5. 保留后续 `.bind` 文件导出接口的最小结构设计

---

## Out of Scope

本任务**不包括**：

* `.bind` 文件真正写入文件系统
* PC 端读取 `.bind` 文件
* Packer 接入 `--bind-file`
* BIN2 header 接入 `binding_mode`
* Device-bound BIN2 真正验证
* 云端 App Store / 账户系统 / 设备注册

---

## Constraints

1. **不能踩以前的坑**

   * `dap.mk` 漏加文件
   * 日志宏未定义导致 link error
   * 释放 offset 指针导致 heap 损坏
   * 修改后 Logel trace 消失
   * 安全模块直接乱用底层 API，导致编译或运行不一致

2. **Logel trace 必须继续可追踪**

   * 新增日志必须走已验证过的路径
   * 不允许再引入不稳定的私有 trace 宏
   * 原则上继续使用 DAP 已验证通过的 trace 包装链

3. **禁止输出 DeviceSecret 明文**

   * 只允许输出 BindingID
   * 或输出 BindingID 的前 8/16 字节十六进制
   * 不允许日志里直接打印 32-byte DeviceSecret

4. **编译链必须恢复**

   * `dap.a` 必须重新产出
   * 保持当前构建命令可用

---

## Expected Deliverables

1. 修复后的 `device_binding.c` / `device_binding.h`
2. 修复后的 `dap.mk` 或等价构建配置
3. 一份 `docs/architecture/device_binding_phase1a.md`
4. 一份设备端 Logel 截图/文本，证明：

   * `BindingID` 已派生
   * Logel 可见
5. 一份简短反馈文档：

   * BindingID 算法
   * 输出格式
   * 下一步 `.bind` 文件导出建议

---

## Verification Method

* [ ] **Build verification:**
  使用当前 DAP 构建命令编译通过，`dap.a` 成功生成

* [ ] **Module build verification:**
  `device_binding.c` 被编译进 DAP，不再报 `dap_sha256.h` 缺失

* [ ] **Device test:**
  开机或进入工程菜单时，触发 BindingID 派生并输出日志

* [ ] **Log verification:**
  在 Logel 中能检索到：

  * `tm25_`
  * `[bind]`
  * `binding_id`

* [ ] **Security verification:**
  Logel 中看不到 DeviceSecret 明文

---

## Potential Risks

* **Risk 1 — `dap_sha256.h` 不存在或路径错**
  可能是：

  * 文件名与现有 SHA256 头文件不一致
  * include path 未加入 `security/`
  * 代码错误引用了尚未创建的头文件
    **缓解：** 先确认现有 SHA256 头文件的真实名字和路径，不要拍脑袋 include。

* **Risk 2 — `dap.mk` 再次漏改**
  之前已经踩过这类坑。
  **缓解：** 明确检查：

  * `device_binding.c`
  * `dap_sha256.c`（如果存在）
  * 对应 include path
    是否都进入 DAP 构建。

* **Risk 3 — Logel trace 路径被新代码破坏**
  **缓解：** 不直接在 security 文件里乱写底层 trace，沿用已验证的 DAP trace 包装链。

* **Risk 4 — BindingID 输出过长被截断**
  **缓解：** 每条日志只打印一小段，例如：

  * 前 8 字节
  * 或分两条打印 16 字节 hex

* **Risk 5 — 工程师误把 DeviceSecret 直接输出到日志**
  **缓解：** 明确禁止，只能输出 BindingID。

---

## References

* TM15 Phase-0 BIN2 Secure Loader
* TM20 Logel trace fix
* TM21 / TM22 debug and feedback chain
* `Third-party/DAP/security/`
* `DAP_DebugLog.h`
* `DAP_OSAssociated_unisoc.c`
* `AIOS/docs/architecture/`

---

## Implementation Plan

### Step 1 — 先修编译链，不修这个后面全是空的

#### 1.1 确认 `dap_sha256.h` 的真实来源

工程师必须先检查：

* 当前仓库里是否真的存在 `dap_sha256.h`
* 如果不存在，现有 SHA256 头文件叫什么
* 它的真实路径在哪

可能情况：

* 文件名其实是 `sha256.h`
* 文件在 `Third-party/DAP/security/`
* 或者文件在别的目录，但 include path 没加

#### 1.2 修正 include

不要硬写不存在的文件名。
按真实文件名修正：

```c
#include "sha256.h"
```

或者如果文件确实应该叫 `dap_sha256.h`，那就补全该头文件并统一实现。

#### 1.3 修复 `dap.mk`

必须明确检查并修正：

* `device_binding.c` 是否加入 `SOURCES`
* `sha256.c` / `dap_sha256.c` 是否加入 `SOURCES`
* `security/` 是否加入 `INCLUDES`

**不要再犯“头文件写了、源文件没进 dap.mk”这种低级错误。**

#### 1.4 验证 `dap.a`

修复后先只验证一件事：

> `dap.a` 是否重新生成

如果 `dap.a` 没生成，后面所有运行时验证都没有意义。

---

### Step 2 — 定义 BindingID 算法（Phase 1A 固化）

本阶段只需要一个稳定、简单、可追踪的 BindingID。

建议算法：

```text
BindingID = SHA256("AIOS-BIND-V1" || DeviceSecret)[0..15]
```

说明：

* `DeviceSecret`：32 bytes
* 常量前缀：避免未来算法升级混淆
* 取前 16 bytes，得到 128-bit BindingID

这样可以保证：

* 足够短，适合日志和未来 `.bind` 文件
* 冲突概率对千万级设备可忽略
* 与未来云端存储兼容

---

### Step 3 — 实现 `device_binding.c`

建议新增最小 API：

```c
BOOLEAN device_binding_init(void);
BOOLEAN device_binding_get_id(uint8 *out16);
void device_binding_log_id(void);
```

逻辑：

1. 调用现有 DeviceSecret 读取接口
2. 用 SHA256 计算 BindingID
3. 缓存到静态内存（如有必要）
4. 通过日志输出

注意：

* 不要修改 DeviceSecret 本体逻辑
* 不要重新生成 DeviceSecret
* 只是“读取 + 派生 + 输出”

---

### Step 4 — Logel 输出策略

#### 4.1 日志前缀

统一使用：

```text
[bind]
tm25_
```

例如：

```text
[bind] tm25_init ok
[bind] tm25_id[0..7]=9f 2a 7c 41 e3 d1 b2 a4
[bind] tm25_id[8..15]=c8 b7 d9 e1 f0 a1 23 45
```

#### 4.2 输出内容

只输出：

* BindingID 前 16 字节（分段）
* 初始化状态
* 是否成功读取 DeviceSecret

严禁输出：

* DeviceSecret 明文
* SHA256 内部中间态

#### 4.3 Trace 路径

沿用已经验证可用的 DAP trace 路径。
**不要直接在 `device_binding.c` 里裸调一个未经验证的新宏。**
避免重演之前 `BIN2_LOG` 未定义和 Logel 不可观测的问题。

---

### Step 5 — 触发时机

本阶段建议用两种方式之一：

#### 方式 A（推荐）

在 DAP 初始化后、工程调试路径中主动调用 `device_binding_log_id()`

#### 方式 B

在已有工程菜单/工程码页中增加“显示 BindingID”

本 memo 更偏向 A，因为：

* 更快
* 不需要 UI 先改完
* 更适合先验证 Logel

---

### Step 6 — 文档沉淀到架构目录

必须新增并提交：

```text
AIOS/docs/architecture/device_binding_phase1a.md
```

内容至少包括：

1. DeviceSecret 与 BindingID 的关系
2. BindingID 算法
3. Phase 1A（Logel 输出）目标
4. Phase 1B（`.bind` 文件导出）目标
5. Future：云端 App Store 如何存储和识别 BindingID

目的：

> **让架构路线不再只存在聊天记录里，而是沉淀到 AIOS 文档树下。**

---

## Step-by-step Execution Order

### Day 1

1. 修正 `dap_sha256.h` 问题
2. 修正 `dap.mk`
3. 重新生成 `dap.a`
4. 确认构建通过

### Day 2

1. 实现 `device_binding.c` 最小 API
2. 实现 BindingID 派生
3. 加入 Logel trace
4. 真机验证 Logel 输出

### Day 3

1. 整理反馈文档
2. 提交 `AIOS/docs/architecture/device_binding_phase1a.md`
3. 给出下一步 `.bind` 文件导出建议

---

## Success Criteria

本任务完成的标准不是“代码写了”，而是：

1. **编译通过**

   * 不再报 `dap_sha256.h` 缺失
   * `dap.a` 成功生成

2. **设备端可见**

   * Logel 中能看到 `[bind] tm25_...`

3. **输出正确**

   * 能看到 BindingID
   * 看不到 DeviceSecret 明文

4. **架构沉淀**

   * `AIOS/docs/architecture/device_binding_phase1a.md` 已存在

---

## Final Note

TM25 不是最终 device binding。
TM25 的目标只是：

> **先证明设备可以稳定地产生、记录并输出一个未来可用于绑定的 BindingID。**

只有这一步跑通，TM26 才值得去做：

```text
.bind 文件导出
```

然后再进入：

```text
PC packer 读取 .bind
```

这才是一个现实、不会再次发散的推进路径。
