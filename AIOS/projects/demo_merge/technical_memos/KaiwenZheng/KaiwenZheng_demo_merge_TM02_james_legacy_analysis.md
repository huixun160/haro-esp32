

# **Technical Memo 2 — James Legacy Code System Analysis & Integration Mapping**





------



**Title:** Systematic Analysis of James Legacy Code & Integration Mapping

**Project:** AIOS Feature Phone Platform

**Subsystem:** DAP / APP / UI / Integration / Architecture

**Author:** [Engineer name]

**Priority:** HIGH

**Date:** [YYYY-MM-DD]



------





## **Background**





TM1 已完成：



- 已成功从 GitLab clone James 工程
- 已隔离在 zkw_legacy_code 目录
- 当前主线未受污染





当前进入关键阶段：



> **理解 James 做了什么，并决定哪些“可以 merge”，哪些“绝对不能 merge”。**



------





## **Problem Statement**





James 的工程具有以下特点：



1. **UI 架构变化**

   

   - 基于 LVGL9 + PalmOS 风格 UI
   - 试图替代原 MMI 体系（部分替代）

   

2. **双系统共存**

   

   - MMI：用于系统入口（拨号、短信等）
   - LVGL：用于 DAP App（语音助手、游戏）

   

3. **功能链路复杂**

   

   - MMI → Bazar → 下载 bin → DAP → LVGL App

   

4. **代码不稳定**

   

   - 存在随机蓝屏
   - 不可复现 bug
   - 不可直接用于生产

   





------





## **Objective**





本阶段目标不是“理解全部代码”，而是：



1. 建立 **系统级架构模型**
2. 梳理 **功能模块与依赖关系**
3. 明确 **哪些模块需要 merge**
4. 明确 **哪些模块禁止 merge**
5. 输出 **接口清单（为后续 ABI 冻结做准备）**
6. 输出 **架构图谱（用于后续工程决策）**





------





## **Scope**







### **In Scope**





- LVGL UI 系统分析
- PalmOS UI 架构梳理
- Bazar 下载链路分析
- DAP bin 调用链分析
- 应用模块清单
- 接口依赖梳理







### **Out of Scope**





- 不修 bug
- 不编译优化
- 不做性能分析
- 不直接 merge 代码
- 不修改主线





------





## **System Architecture (Target Understanding)**



```
flowchart TD
    A[MMI System] --> B[System Apps]
    B --> B1[Dialer]
    B --> B2[SMS]
    B --> B3[Contacts]
    B --> B4[Settings]
    B --> B5[WiFi/4G]

    B --> C[Bazar]

    C --> D[DAP Loader]

    D --> E[LVGL Runtime]

    E --> F1[Voice Assistant]
    E --> F2[Snake]
    E --> F3[Tetris]
```



------





## **Key Architecture Insight**





> **James 并没有替换 MMI，而是“叠加了一层 LVGL App Runtime”。**



核心逻辑：



- MMI：系统入口（稳定）
- Bazar：应用分发
- DAP：执行引擎
- LVGL：UI runtime





------





## **Implementation Plan**





------





### **Step 1 — 目录结构梳理（必须）**





工程师需要输出：

```
zkw_legacy_code/UMS9117_BSP/
    ├── MMI/
    ├── DAP/
    ├── LVGL/
    ├── APP/
    ├── BAZAR/
    ├── DOCS_MAIN/
```

要求：



- 标注每个目录作用
- 标注新增/修改模块（相对于主线）





------





### **Step 2 — Git Diff 分析（核心）**





利用：

```
git diff --name-only
git diff --stat
```

对比：



- James 的 agit
- 当前主线 git





输出：

```
新增文件列表
修改文件列表
删除文件列表
```



------





### **Step 3 — 模块分类（非常关键）**





所有改动必须归类到以下类别：





### **A — UI 层（LVGL）**





- LVGL 初始化
- UI 组件
- 页面管理







### **B — 应用层**





- 语音助手
- 贪吃蛇
- 俄罗斯方块







### **C — 分发系统**





- Bazar
- 下载逻辑
- 安装逻辑







### **D — 系统适配层**





- DAP 调用
- Timer / Input / Display







### **E — MMI 修改**





- 是否改动原有界面？
- 是否 hook 入口？





------





### **Step 4 — 功能清单（必须输出）**





工程师必须列出：

| **模块**        | **功能** | **是否稳定** | **是否需要 merge** |
| --------------- | -------- | ------------ | ------------------ |
| Dialer          | MMI原生  | 稳定         | ❌                  |
| Bazar           | 下载APP  | 可用         | ✅                  |
| Voice Assistant | LVGL App | 不稳定       | ✅                  |
| Snake           | LVGL App | 稳定         | ✅                  |



------





### **Step 5 — 接口清单（最重要）**





必须输出：

```
DAP API 使用列表
LVGL 调用接口
系统调用（Timer / Network / Input）
```

示例：

```
DAP_DisplayInit
DAP_MemAlloc
DAP_AudioPlay
DAP_NetConnect
```

并标记：



- 是否新增接口
- 是否修改接口
- 是否依赖 MMI





------





### **Step 6 — 调用链分析（必须）**





至少输出一条完整链路：

```
MMI → Bazar → 下载 bin → DAP_Load → LVGL → App
```

以及：

```
按键 → MMI → 启动 → LVGL App
```



------





### **Step 7 — Merge 策略定义（核心输出）**







#### **可以 merge**





- LVGL runtime
- Bazar 下载逻辑
- DAP App（语音助手、游戏）







#### **禁止 merge**





- 覆盖 DAP loader
- 覆盖现有安全逻辑
- 覆盖 MMI 核心模块
- 替换系统初始化流程





------





## **Expected Deliverables**







### **Deliverable 1 — 架构文档**





文件：

```
AIOS/analysis/TM02_architecture.md
```

内容：



- 系统架构图
- 模块说明
- 调用链





------





### **Deliverable 2 — 模块清单**



```
AIOS/analysis/TM02_modules.md
```



------





### **Deliverable 3 — 接口清单**



```
AIOS/analysis/TM02_api_list.md
```

（用于后续 ABI 冻结）



------





### **Deliverable 4 — Merge 建议**



```
AIOS/analysis/TM02_merge_plan.md
```



------





## **Validation Criteria**





必须满足：



- 能画出完整系统架构图
- 能解释 Bazar → DAP → LVGL 流程
- 能列出所有关键接口
- 能明确哪些模块 merge / 禁止 merge
- 未修改任何主线代码





------





## **Pitfalls（必须阅读）**





1. **不要直接 copy 文件**
2. **不要一边分析一边 merge**
3. **不要相信 DOCS_MAIN（以代码为准）**
4. **不要低估 MMI 依赖**
5. **不要让 LVGL 覆盖现有 UI 系统**





------





## **Memory / Lessons Learned**





- James 的系统是“叠加”，不是“替代”
- Bazar 是关键入口
- DAP 是唯一执行引擎（必须保护）
- UI 可以换，但执行机制不能动





------





## **Next Step**





TM3：



→ 开始 selective merge（只 merge 允许模块）

→ 同步进入 secure pipeline（bin2 / 混淆 / ID）



------





## **Summary**





> 本阶段的目标不是读代码，而是：

> 

> **建立系统认知 + 画出边界 + 决定什么可以进入主线。**

> 

> 如果这一步做错：

> 

> 👉 后面 merge 会直接炸系统。

> :::



------





# **最后我直接讲一句最关键的（别忽略）**





你现在这个阶段的本质不是“整合代码”，而是：



> **控制边界**



James 的工程 = 一个“功能爆炸但结构不稳”的系统

你现在的工程 = 一个“结构稳定但功能较少”的系统



你要做的不是融合，而是：



> **把他的能力“嫁接”到你的结构上**



------

