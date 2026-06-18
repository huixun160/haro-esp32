# TM-032-2 Clarification Questions

**Memo:** Technical Memo 32-2 — External Build Strip & Semantic Reduction
**Date:** 2026-03-21

---

## Q1 — Step 4 语义替换的作用范围

**答复：A + B + C 全部在本阶段范围内**

| 目标 | 方案 |
|------|------|
| A: trace 字符串 | external build 直接裁剪/关闭 DAP trace（不改成 api_01） |
| B: ELF 符号名 | 继续 strip，不需要改源码 |
| C: FindInterface 明文接口名 | **必须处理**：external 改为 `FindInterfaceById(IF_XXX)`，ID-based lookup |

**C 的关键要求：**
- internal build 保持 `FindInterface("...")` 字符串路径
- external build 改为 `FindInterfaceById(IF_XXX)` ID 路径
- 固件注册表在 `EXTERNAL_BUILD` 下走 ID 路径
- 需要列出所有接口名清单 → 分配稳定 ID 表

**Rationale:** 不做 C 则 external PAC 仍保留最危险的语义锚点，strings 即可重建 DAP API 面。

---

## Q2 — Step 5 路径清理

**答复：B 为主、C 为兜底**

- **主路径：** 裁剪 DAP trace → `__FILE__`/`__LINE__` 路径自然消失
- **兜底：** strings 扫描若仍发现路径残留 → 定点修复
- **不采用** 全局 `-D__FILE__=""`（风险高、收益有限）

---

## Q3 — SCI_TRACE_LOW 处理策略

**答复：**
- 对内：保留全部 SCI_TRACE_LOW
- 对外：剔除 DAP 核心信息相关的 SCI_TRACE_LOW，保留引入 DAP 之前的原始 trace

---

## Q4 — BIN3 验证

**答复：** 暂不验证 BIN3，留给未来阶段。
