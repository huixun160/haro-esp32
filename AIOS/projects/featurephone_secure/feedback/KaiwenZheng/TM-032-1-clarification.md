# TM-032 Clarification Questions

**Memo:** TM32 — External Binary Hardening
**Date:** 2026-03-20

---

## Q1. FindInterface 去语义化的实现层级

**现状：**
- APP 侧：`dap_api.h` 宏调用 `FindInterface("OS_DisplayPopup", cmd)`
- 固件侧：`InterfaceRegister` 是字符串哈希表，`InterfaceRegister_Find(name)` 按字符串查找

**Memo 要求：** `FindInterface("xxx")` → `FindInterfaceById(0x0213)`

**问题：** 这需要**同时改两侧**：

| 侧 | 改动 |
|----|------|
| APP 侧 | `dap_api.h` 宏中的字符串替换为 ID |
| 固件侧 | `InterfaceRegister` 增加 ID→函数指针 映射表 |
| 固件侧 | `DAP_InstallOSAPI_unisoc.c` 注册时同时注册 ID |

- **(A)** 两侧都改：固件增加 `FindInterfaceById()`，APP 用 ID 调用。**需要重新编译 PAC + 重新烧录**
- **(B)** 只改 APP 侧：APP 中字符串 → compile-time hash，固件侧仍用字符串匹配但用 hash 比较。**不改固件**
- **(C)** 先不做此项（TM-032 只做 strip + strings 扫描），接口去语义化留给 TM-033

**你选哪个？**

---

## Q2. Strip 策略对 Entry.o 的处理

**现状：**
- `Entry.o` (7KB) 包含符号：`Entry`, `FindInterface`, `GetBSSSpace`, `GetApplication`, `Main` (extern)
- `armlink` 需要 `Entry` 符号定位入口
- `armlink -first Entry.o(.constdata)` 需要 section 名

**问题：** ARM ADS 的 `fromelf` 工具可以做选择性 strip：
- `fromelf --strip=debug` — 去除调试信息（安全，不影响链接）
- `fromelf --strip=symbols` — 去除符号表（**会破坏链接**）

- **(A)** 只做 `fromelf --strip=debug`（保守安全，保留链接能力）
- **(B)** 做 `fromelf --strip=debug` + 手动 rename 无意义符号名（如 `FindInterface` → `_fi`）
- **(C)** 不 strip Entry.o，只做 strings 扫描验证

**你选哪个？**

---

## Q3. PAC 的 strings 扫描范围

**现状：** PAC 是 53MB 完整固件，包含 OS + MMI + 通信协议栈 + DAP。`strings` 会命中大量无关字符串。

**问题：** strings 扫描的目标是什么？

- **(A)** 只扫描 `Entry.o` 和 APP `.bin` 文件（可控范围）
- **(B)** 扫描 PAC 中 DAP 相关的 `.o` 文件（需要从编译中间产物提取）
- **(C)** 不扫描 PAC（PAC 是齐全固件，不可能去掉所有 DAP 字符串，因为 Logel trace 需要它们）

**你选哪个？**

---

## Q4. EXTERNAL_BUILD 宏的实现方式

**Memo 要求：** 通过 `#ifdef EXTERNAL_BUILD` 区分 internal/external。

**问题：** 这个宏在哪里定义？

- **(A)** 在 `dap.mk` 中增加 `MCFLAG_OPT += -DEXTERNAL_BUILD`，编译 external PAC 时开启
- **(B)** 在 `export_zkw_output.py` 导出时，用脚本替换 zkw_output 中的代码（sed/replace）
- **(C)** 当前阶段不引入 EXTERNAL_BUILD 宏，只做 strip + strings 扫描

**你选哪个？**

---

## Q5. TM-032 的优先级裁剪

**Memo 包含 5 项工作。** 考虑到当前阶段的成本效益，建议分期：

**Phase 1（本次实施）：**
- Layer B strip：`fromelf --strip=debug` 对 Entry.o
- Layer C strings 扫描：验证 .bin 和 Entry.o 中无 DAP 语义字符串
- 升级 `export_zkw_output.py` 加入 strip + strings 校验

**Phase 2（后续）：**
- FindInterface → ID 替换（需改固件）
- 字符串 XOR 加密
- EXTERNAL_BUILD 宏体系
- 轻量混淆

- **(A)** 同意分期：Phase 1 先做 strip + strings，Phase 2 再做去语义化
- **(B)** 全部在 TM-032 一次性完成
- **(C)** 自定义分期（请说明）

**你选哪个？**
