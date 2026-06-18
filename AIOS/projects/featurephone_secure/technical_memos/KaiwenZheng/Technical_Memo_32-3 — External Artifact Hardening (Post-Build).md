# **Technical Memo 32-3 — External Artifact Hardening (Post-Build)**





------



**Title:** External PAC Hardening Phase 2 — Post-Build Strip & Light Obfuscation

**Project:** AIOS Feature Phone Platform

**Subsystem:** Build / DAP / Security

**Author:** [Engineer name]

**Priority:** HIGH

**Date:** [YYYY-MM-DD]



------





## **Background**





TM32-2 尝试通过 compile-time 修改（trace gating + FindInterface ID 化）实现去语义，但结果：



- SECURE build 出现 Prefetch Abort
- Logel trace 被完全移除 → 调试能力丧失
- runtime / loader 问题无法定位





结论：



> 当前阶段不适合继续在编译期和运行时路径做大规模改动。



因此本阶段策略调整为：



> **将 hardening 从“编译期/运行时”迁移到“产物后处理（post-build）”。**



------





## **Objective**





在不修改 runtime 行为的前提下，实现：



1. external PAC 去除 debug 信息（strip）
2. 显著减少 strings 可读语义（DAP / 路径 / 接口名）
3. 保留最小可调试能力（Logel trace 保留）
4. 不影响 BIN / BIN2 / BIN3 执行稳定性
5. 建立 external artifact hardening pipeline





------





## **Scope**







### **In Scope**





- post-build strip（Entry.o / Start.o / 外部产物）
- strings 扫描与报告
- 轻量字符串去语义（产物级）
- export pipeline（zkw_output）







### **Out of Scope**





- loader / runtime 修改
- FindInterface ABI 改造
- bin3 加密逻辑
- 重混淆（CFG / VM / 控制流）
- trace compile-time gating





------





## **Design Overview**





核心原则：



> **不改代码行为，只改最终产物的“可读性”。**



架构：

```
flowchart TD
    A[Internal Build] --> B[Standard Build Output]
    B --> C[Post-Build Hardening]
    C --> D[zkw_output Secure PAC]

    C --> C1[Strip Debug Info]
    C --> C2[Strings Scan]
    C --> C3[String Reduction]
```



------





## **Implementation Plan**





------





### **Step 1 — 保持现有 build 不变（重要）**





明确：



- 不修改 dap.mk
- 不引入 EXTERNAL_BUILD 宏
- 不修改 FindInterface
- 不修改 trace 行为





所有 hardening 在 build 之后进行。



------





### **Step 2 — Strip External Artifacts**





目标文件：



- Entry.o
- Start.o
- external 关键 .o / .a（如可获取）





执行：

```
fromelf --strip=debug Entry.o
fromelf --strip=debug Start.o
```

说明：



- 仅去 debug 信息
- 不允许改符号名
- 不允许破坏 ABI





输出到：

```
zkw_output/obj/
```



------





### **Step 3 — Strings 扫描（必须）**





扫描对象：



- Entry.o
- demo app .bin
- external .o/.a（如可访问）





命令：

```
strings file | grep -E "DAP_|LVGL|binding|loader|FindInterface|Audio|/home|\.c:"
```

输出：

```
zkw_output/reports/strings_report.txt
```



------





### **Step 4 — 产物级字符串收缩（轻量）**





⚠️ 本阶段**不修改源码字符串**，而是：



> **只处理“明显不该存在”的字符串来源**





#### **允许存在**





- Logel trace（用于调试）
- 必要运行字符串







#### **优先处理（若发现）**





- 编译路径（/home/…）
- 本地用户名
- 绝对路径
- 工程目录结构





处理方式：



- 若来自 debug → strip 已解决
- 若来自代码 → 标记来源，记录在 report（不强制立即改）





------





### **Step 5 — PAC 命名与暴露面收缩（轻量）**





检查并优化：



- 输出 PAC 文件名（避免暴露内部版本语义）
- demo bin 命名（避免直接体现功能模块）
- 不携带多余说明文件（如 XML / debug 文件，如可选）





⚠️ 本阶段不修改 PAC 结构，仅做命名与打包层控制。



------





### **Step 6 — Export Pipeline 建立**





新增 export 脚本：

```
tools/export_secure.sh
```

流程：

```
build → copy → strip → strings scan → output
```

输出目录：

```
zkw_output/
    ├── pac/
    ├── img/
    ├── obj/
    ├── reports/
```



------





## **Constraints**





- 不允许修改 runtime 行为
- 不允许影响 loader
- 不允许破坏 debug build
- 性能影响必须为 0
- 内存影响必须为 0





------





## **Expected Deliverables**





1. strip 后 Entry.o / Start.o
2. strings_report.txt
3. export_secure.sh
4. zkw_output PAC
5. strings 风险清单（需后续处理）





------





## **Validation Plan**







### **Case 1 — 功能验证**





- BIN 正常运行
- BIN2 正常
- BIN3 正常
- 无新增 crash





------





### **Case 2 — Debug 能力**





- Logel trace 可用
- 可定位 crash（不再黑箱）





------





### **Case 3 — Strings 检查**





- 不出现明显路径（/home/…）
- debug 信息显著减少
- DAP_* 字符串数量下降（非强制清零）





------





## **Pitfalls（必须阅读）**





1. **不要再次做 compile-time trace gating**
2. **不要修改 FindInterface**
3. **不要 rename ABI 符号**
4. **不要 strip internal build**
5. **不要直接编辑 PAC 二进制结构**
6. **strings 扫描要控制范围（避免噪声）**





------





## **Memory / Lessons Learned**





- compile-time hardening 风险极高（已导致 crash）
- strip 是最安全、最高 ROI 的第一步
- strings 是主要逆向入口之一
- debug 能力必须优先保留





------





## **Next Step**





完成 TM32-3 后：



→ TM33：接口/错误码/文档收口

→ TM32-4（可选）：逐步引入 interface ID / deeper obfuscation（在系统稳定后）



------





## **Summary**





> 本阶段的目标不是“彻底防逆向”，而是：

> 

> **在不破坏系统的前提下，显著提高阅读成本。**

> 

> 方法：



- > strip

- > 控制 strings

- > 收缩暴露面



> 

> 不做：



- > runtime 改造

- > ABI 改动

- > 重混淆

  > :::





------





# **最后我帮你把这一步的战略意义讲清楚**





你现在其实做了一次非常正确的转向：





### **错误路径（TM32-2之前）**





👉 一上来就动 runtime / ABI / loader

→ 系统直接炸

→ 安全没提升，工程瘫痪





### **正确路径（现在）**





👉 先做 **post-build hardening**

→ 不影响运行

→ 立刻提高逆向成本

→ 给后面真正的混淆留空间



------



