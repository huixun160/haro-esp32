# TM-032-4 Clarification — Interface IDization & Light Obfuscation

**Date:** 2026-03-21
**Status:** DECIDED — 可执行

---

## 决策摘要

| 问题 | 决策 | 核心原则 |
|------|------|---------|
| Q1 崩溃处理 | **(b) 改方案绕过** — 独立全局变量替代 `Application->Free` | 不求学术还原，最小修正拉回可执行路径 |
| Q2 代码关系 | **(b) 恢复 TM-032-2 代码** — 作为起点，只修 crash 点 | 不归零已有验证成本 |
| Q3 混淆层 | **(b) 拆分** — TM-032-4 只做 ID 化，混淆放 TM-032-5 | 不一口气改太多 |
| Q4 Build Profile | **(a) 复用 `_SECURE`** — 不新建 profile | 先稳定，再细分 |
| Q5 分批策略 | **Batch 1→4** + 每批必须能单独回退 | 先切最便宜最稳定的接口 |

---

## Q1 — 崩溃处理：改方案绕过 (b)

**Rationale:** 当前最重要的不是学术上还原 Prefetch Abort 唯一真因，而是在不踩同一个坑的前提下把 ID 化拉回可执行路径。`Application->Free` 属于 ABI 锚点/关键字段，复用它风险高。

**工程师 Action:**
- [ ] 恢复 TM-032-2 代码到独立分支
- [ ] 去掉 `Application->Free` 复用
- [ ] 用独立全局变量承载 FindById 路径
- [ ] 验证: BIN / BIN2 / BIN3 / SECURE build
- [ ] 反馈中明确说明: crash 是否消失、是否仍有 I-cache 可疑点

---

## Q2 — 代码关系：恢复 TM-032-2 代码 (b)

**Rationale:** 从零实现只会把已付出的验证成本归零。正确做法：把 TM-032-2 当原型分支，修掉 crash 设计再推进。

**工程师 Action:**
- [ ] 用 git stash/分支恢复 TM-032-2 实现
- [ ] 只针对 crash 点做最小修正，不借机重写
- [ ] 提交: 恢复点、修正点、新旧差异说明

---

## Q3 — 混淆层：拆分到 TM-032-5 (b)

**Rationale:** TM-032-4 核心目标只有一个：切掉明文接口语义且不 crash。轻混淆是增强项、留到 TM-032-5 边界最清楚。

**TM-032-4 范围:**
- [x] ID 表
- [x] 注册表
- [x] FindInterfaceById
- [x] Dual path
- [x] External strings 验证

**TM-032-5 输入（不在本 TM）:**
- Wrapper rename
- Dispatch 扰动
- 常量表分散

---

## Q4 — Build Profile：复用 _SECURE (a)

**Rationale:** 当前阶段最重要的是让 external secure 版本稳定站住，不需要细分 profile。

**工程师 Action:**
- [ ] 复用 `_SECURE` profile，挂 ID lookup + strings 验证
- [ ] 反馈中记录: 如果后续加入轻混淆是否需要 profile 再拆分

---

## Q5 — 分批策略：Batch 1→4，每批可独立回退

| 批次 | API 组 | 数量 | 验证要求 |
|------|--------|------|---------|
| **Batch 1** | Memory (Alloc/Free/Set/Cpy/AllocZ) | 5 | BIN+BIN2+BIN3+SECURE+strings |
| **Batch 2** | File (Open/Read/Write/Size/Close/Seek/Delete) | 7 | 同上 |
| **Batch 3** | Timer + Debug + Time | 5 | 同上 |
| **Batch 4** | GUI (3) + Audio (13) | 16 | 同上，最后做 |

**约束:** 
- 每批保留 patch + 回退点 + 验证结果
- GUI/Audio **一定放最后，不得提前混入**
