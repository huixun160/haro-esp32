

# **Technical Memo 32-2 — External Build Strip & Semantic Reduction**





------



**Title:** External PAC Hardening Phase 1 — Strip & Semantic Reduction

**Project:** AIOS Feature Phone Platform

**Subsystem:** Build / DAP / Security

**Author:** [Engineer name]

**Priority:** HIGH

**Date:** [YYYY-MM-DD]



------





## **Background**





Current PAC reverse engineering results show critical exposure:



- Entry.o / Start.o 未 strip，包含完整符号、路径、编译信息
- DAP API（如 FindInterface / DAP_*）以明文字符串存在
- strings 即可快速还原系统结构与接口
- PAC / bin 基本属于“可读状态”，攻击成本极低





本阶段目标不是“彻底防逆向”，而是：



> **消除最廉价、最直接的语义泄露入口（strings + debug symbols）**



------





## **Objective**





在不影响当前系统稳定性（BIN / BIN2 / BIN3）的前提下，实现：



1. External PAC 去除 debug 信息（strip）
2. 显著减少 strings 可读语义（DAP / 路径 / 接口名）
3. internal build 完全不受影响
4. external build 输出到 zkw_output
5. 建立 strings 扫描与报告机制





------





## **Scope**







### **In Scope**





- External build profile（SECURE）
- Entry.o / Start.o strip
- external 产物 strings 扫描
- 部分字符串语义替换（仅 wrapper 层）
- export pipeline 升级







### **Out of Scope**





- bin3 加密/绑定逻辑（TM32-2 后续处理）
- FindInterface ABI 修改（TM32-3）
- 混淆（控制流 / VM / CFG）
- loader / runtime 行为修改





------





## **Current State**





当前 external PAC：



- 未 strip debug 信息

- strings 可直接看到：

  

  - DAP_* API
  - binding / loader
  - 文件路径 / 工程路径

  

- Entry.o 暴露 ABI 结构





------





## **Design Overview**





本阶段采用：



> **“构建隔离 + strip + 语义收缩 + 可验证扫描”**





### **架构**



```
Internal Build (原始)
    ↓
保持不变（调试）

External Build (SECURE)
    ↓
strip
    ↓
strings 扫描
    ↓
输出 zkw_output PAC
```



------





## **Implementation Plan**





------





### **Step 1 — 建立 Secure Build Target**





新增 build target：

```
ums9117_240X320BAR_64MB_ML_SECURE
```

要求：



- 定义宏：



```
-DEXTERNAL_BUILD
```



- 
- 输出路径：



```
zkw_output/.../img
zkw_output/.../pac
```



- 
- 不影响原 build target





------





### **Step 2 — Entry.o / Start.o Strip**





执行：

```
fromelf --strip=debug Entry.o
fromelf --strip=debug Start.o
```

注意：



- 不允许 rename 符号
- 不允许修改 ABI
- 仅去除 debug 信息





验证：



- BIN 可运行
- BIN2 可运行
- BIN3 可运行





------





### **Step 3 — External 产物 Strings 扫描**





扫描对象：



- Entry.o
- demo app .bin
- external .o / .a（可获取时）





执行：

```
strings file | grep -E "DAP|LVGL|binding|loader|FindInterface|Audio"
```

输出：

```
zkw_output/reports/strings_report.txt
```



------





### **Step 4 — 语义收缩（仅 wrapper 层）**





在 #ifdef EXTERNAL_BUILD 下：



将明显语义字符串替换为中性名称，例如：

| **原名称**       | **替换** |
| ---------------- | -------- |
| DAP_MemAlloc     | api_01   |
| DAP_AudioPlay    | api_02   |
| DAP_DisplayPopup | api_03   |

注意：



- 不修改 FindInterface 机制
- 不修改 runtime dispatch
- 仅 wrapper / macro 层替换





------





### **Step 5 — 路径信息清理**





检查并移除：



- 编译路径（/home/…）
- 工程目录
- 本地用户名
- debug trace path





方式：



- 编译选项去路径
- 或宏替换





------





### **Step 6 — Export Pipeline 升级**





在 external build 中：



新增步骤：



1. strip
2. strings 扫描
3. 生成报告
4. 输出到：



```
zkw_output/
    ├── pac/
    ├── img/
    ├── reports/
```



------





## **Constraints**





- 不允许破坏 ABI
- 不允许影响 loader
- 不允许影响 debug build
- 内存增加必须 < 5KB
- 性能影响必须 < 10ms





------





## **Expected Deliverables**





1. 新 build target：..._ML_SECURE
2. strip 后 Entry.o / Start.o
3. strings_report.txt
4. external PAC（zkw_output）
5. wrapper 语义收缩 patch





------





## **Validation Plan**





必须通过：





### **Case 1 — Internal Build**





- BIN 正常运行
- Debug 正常







### **Case 2 — External Build**





- PAC 正常烧录
- BIN 正常运行
- BIN2 正常
- BIN3 正常







### **Case 3 — Strings 验证**





- 不出现：

  

  - DAP_*
  - FindInterface（可保留一部分）
  - binding / loader 关键字

  





------





## **Pitfalls (必须阅读)**





1. **不要改 dap.mk 导致编译缺文件**
2. **不要 strip internal build**
3. **不要 rename Entry ABI 符号**
4. **不要影响 SCI_TRACE_LOW**
5. **不要改 loader 行为**
6. **strings 扫描不要扫整个 PAC（噪声太大）**





------





## **Memory / Lessons Learned**





- 之前逆向主要依赖 strings → 本阶段优先消除
- Entry.o 是最大泄露点之一
- strip 是最低成本最高收益
- 不要在这一阶段做 runtime 改造





------





## **Next Step**





完成 TM32-2 后：



→ TM32-3：轻混淆（FindInterface → ID / hash）



------





## **Summary**





> 本阶段目标不是“防逆向”，而是：

> 

> **让对方第一眼看不懂。**

> 

> 做到：



- > 没 debug 信息

- > 没明显 API 名

- > 没工程路径



> 

> 但系统仍然稳定运行。

> :::



------





# **我再帮你用一句话总结 TM32-2 的本质**





> **把“肉眼可读的系统”变成“需要动脑分析的系统”。**



------

