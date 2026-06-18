

# **Technical Memo 3 — Controlled Integration of James Demo Features into Internal Build**





------



**Title:** Controlled Integration of James Demo Features into Internal Build

**Project:** AIOS Feature Phone Platform

**Subsystem:** Integration / DAP / MMI / LVGL / Build

**Author:** [Engineer name]

**Priority:** HIGH

**Date:** [YYYY-MM-DD]



------





## **Background**





TM1 与 TM2 已完成：



- TM1：James 仓库已安全隔离在 zkw_legacy_code

- TM2：已完成系统级分析，包括：

  

  - 架构模型（MMI → Bazar → DAP → LVGL）
  - 模块清单
  - API 依赖
  - merge 边界

  





当前进入关键阶段：



> **将 James 的 demo 功能引入当前工程，使其在“内部工程版本”下可以完整运行。**



注意：



- 本阶段不涉及任何 secure / 加密逻辑
- 本阶段目标是功能跑通，而不是稳定性或安全性





------





## **Objective**





本任务目标：



1. 将 James 的核心功能模块接入当前工程
2. 成功编译内部版本（non-secure）
3. 成功烧录到功能机
4. 能运行以下功能链：



```
MMI → Bazar → 下载 bin → DAP → LVGL → App
```



1. 以下 demo 功能必须可用：







- Bazar（下载）
- LVGL App（语音助手 / 游戏）
- 网络（WiFi / 4G）





------





## **Critical Principle（必须遵守）**





> **不允许破坏现有 DAP / Loader / 安全结构**



本阶段是：



- “嫁接功能”

  而不是：

- “替换系统”





------





## **Scope**







### **In Scope**





- LVGL runtime 接入
- Bazar 接入
- demo APP 接入
- 必要的 MMI 入口接入
- 必要的资源 / build / 配置同步







### **Out of Scope**





- 不引入任何 secure / 加密逻辑
- 不修改 DAP Loader 核心实现
- 不重构 MMI
- 不修复 James 的 bug
- 不优化代码结构





------





## **Integration Strategy（核心策略）**







### **分三层接入**





------





### **Layer 1 — 非侵入接入（优先）**





直接引入：



- LVGL 代码
- demo APP（语音助手 / 游戏）
- Bazar 模块





要求：



- 不修改现有模块
- 仅新增代码





------





### **Layer 2 — 桥接接入（必要）**





建立以下桥接：



- MMI → Bazar
- Bazar → DAP_Load
- DAP → LVGL runtime





------





### **Layer 3 — 最小侵入修改（谨慎）**





只允许：



- 注册接口
- 初始化调用
- menu hook





禁止：



- 覆盖已有模块
- 替换 DAP Loader
- 修改内存管理核心路径





------





## **Execution Plan**





------





### **Step 1 — 建立 Integration Workspace**





在主工程内创建：

```
integration/james/
```

用于承载：



- LVGL
- Bazar
- demo apps





**禁止直接覆盖原目录**



------





### **Step 2 — 模块迁移（按 TM02_merge_plan）**





逐模块迁入：





#### **必迁模块（第一批）**





- Bazar
- LVGL runtime
- demo apps







#### **可选模块（后续）**





- PalmOS UI（如果依赖明确）





------





### **Step 3 — Build 集成**





关键点：



1. 更新 .mk 文件（重点）
2. 注册新模块编译路径
3. 避免污染原有编译链





------





### **Step 4 — 入口接入（MMI Hook）**





目标：

```
MMI Menu → Bazar
```

实现：



- 添加 menu item
- 触发 Bazar 启动





------





### **Step 5 — DAP 调用链验证**





确保：

```
Bazar → 下载 bin → DAP_Load → 正常执行
```



------





### **Step 6 — LVGL Runtime 初始化**





确保：



- LVGL init 在正确生命周期执行
- Display / Input / Timer 已正确接入





------





### **Step 7 — 编译验证**





执行：

```
mm ums9117_240X320BAR_64MB_ML new
make image
```



------





### **Step 8 — 烧录验证**





验证：



- 正常开机
- 无 boot crash
- 无立即蓝屏





------





### **Step 9 — 功能验证**





必须验证：

| **功能** | **预期** |
| -------- | -------- |
| Bazar    | 可进入   |
| 下载 bin | 成功     |
| LVGL App | 能启动   |
| 网络     | 可用     |



------





## **Expected Deliverables**







### **Deliverable 1 — Integration Report**



```
AIOS/projects/demo_merge/feedback/TM03_integration.md
```

内容：



- 实际迁入模块
- 修改点
- 风险点





------





### **Deliverable 2 — Updated Build**





可成功编译的工程版本



------





### **Deliverable 3 — Demo 视频 / 日志**





证明：



- 功能链完整运行





------





## **Validation Criteria**





必须满足：



- 编译成功
- 烧录成功
- Bazar 可运行
- bin 下载成功
- LVGL App 可启动
- 不破坏原 DAP 机制





------





## **Pitfalls（必须阅读）**







### **1. dap.mk 问题（历史坑）**





- 路径错误 → 编译失败
- 重复注册 → link error





------





### **2. logel 依赖**





- 不要依赖 logel debug
- 以实际运行结果为准





------





### **3. 覆盖风险（极高）**





禁止：



- 覆盖 DAP_Loader
- 覆盖 MMI 核心
- 覆盖 build 系统





------





### **4. 内存问题**





- 不新增复杂 malloc/free 路径
- 不改变 buffer ownership





------





### **5. LVGL 初始化顺序**





- 错误顺序会直接蓝屏





------





## **Memory / Lessons Learned**





- James 的代码是“功能优先”，不是“结构优先”

- 我们的系统是“结构优先”

- 整合方式必须是：

  → 功能嵌入结构，而不是结构向功能妥协





------





## **Next Step**





TM4：



→ 在该版本基础上重新引入：



- BIN2 / BIN3
- 接口冻结
- 混淆 / strip





------





## **Summary**





> TM3 的目标只有一个：

> 

> **让 James 的功能在你的系统里跑起来，而不是让你的系统变成 James。**



任何试图“直接覆盖替换”的行为，都会再次导致工程崩溃。

:::



------





# 我再补一句最关键的





TM3 最容易犯的错误是：



> **“这个模块 James 已经写好了，我直接替换掉你原来的版本更快”**



这是错的。



你必须坚持：



> **只加，不替；只接，不改核心。**



------

# 风险提示

TM3 最容易炸的，不是“代码写错”，而是**整合方式错**。

我直接把风险拆给你，按“最可能导致工程崩掉”的顺序来讲。



# **1. 直接覆盖现有目录**





这是头号风险。



一旦工程师把 James 的：



- dap_loader

- mmi_app

- build

- resource

  直接拷进主线同路径，短期看起来省事，长期一定炸。





后果是：



- 你失去对差异的控制
- 以后不知道哪个行为来自 James，哪个来自你
- 一旦编译过不了或开机蓝屏，几乎无法定位





正确做法是：



- 先放进独立 integration/james/
- 只通过桥接、注册、编译入口把它接进来
- 不允许“整目录替换”







# **2. DAP Loader 被污染**





你现在最宝贵的是现有 DAP / Loader 能跑：



- bin
- bin2
- bin3
- 以及你后面安全版本的基础





James 的代码即便功能更多，也不值得用它去碰 Loader 主体。



后果是：



- 之前安全版本的行为基线失效
- 后面 TM4 重新加密时，所有问题都会混在一起
- 你会分不清是 merge 问题还是安全逻辑问题





正确做法是：



- TM3 明确禁止替换 DAP_Loader
- 只能在外围加调用链
- Loader 只接受“被调用”，不接受“被替换”







# **3. MMI 入口和菜单逻辑被大改**





James 的 demo 功能里，系统入口仍然基于 MMI：



- 拨号
- Bazar
- 短信
- 联系人
- 设定
- 互联网





这意味着你必须动 MMI，但**只能做最小 hook**。



风险是：



- 工程师顺手把菜单体系、窗口切换、事件分发改多了
- 结果不是某个 app 挂，而是整机导航逻辑挂





正确做法是：



- 只做最小入口接入
- 新增 menu item / launcher entry
- 不改原有菜单框架







# **4. LVGL 初始化顺序错误**





这类问题往往不是编译错误，而是：



- 开机后黑屏
- 进入 app 蓝屏
- 随机 crash
- 输入无响应





因为 LVGL 依赖：



- display
- input
- timer
- 资源
- 任务/消息循环





一旦初始化顺序不对，系统表面看起来“代码都在”，但运行就是不稳定。



正确做法是：



- 先找到 James 版本里 LVGL 的初始化入口
- 再映射到你当前主线的生命周期里
- 先保证“能起”，再谈 UI 完整性







# **5. 资源与字体系统不完整迁入**





James 的功能很可能不是只靠 .c 文件成立，还依赖：



- 图片
- 字体
- 多语言资源
- 配置表
- resource 编译规则





风险是：



- 编译能过
- 功能能打开
- 但 UI 乱码、图标缺失、布局崩坏





这类问题最容易被低估。



正确做法是：



- TM3 不只是代码 merge
- 还要梳理资源和编译依赖
- 资源文件必须作为一等公民来处理







# **6. 网络链路不是 Bazar 一家在用**





你现在目标里 Bazar 是关键，但别忘了：



- WiFi/4G 设置入口

- 下载链路

- 可能的 DNS / socket / TLS / 存储路径

  都可能跨多个目录。





风险是：



- 你以为只迁 Bazar
- 实际漏了网络 glue
- 最后表现为“Bazar 能开，但下载就是不通”





正确做法是：



- 把“Bazar 下载链路”当成系统链路，不是单模块

- 至少梳理：

  

  - 入口
  - 网络初始化
  - 下载保存
  - DAP loader 接收点

  







# **7. 编译系统污染**





这是功能机工程里非常高频的坑。



包括：



- dap.mk
- project mk
- include path
- 资源编译脚本
- 条件宏
- 重复对象
- 链接顺序





James 的版本能编，不代表它在你主线里能编。

一旦工程师为了“快点过编译”去全局改 mk，很容易把当前基线编译系统污染掉。



正确做法是：



- 所有 build 改动都要最小化
- 优先新增，不优先改已有路径
- 每一次 mk 修改都要记录原因







# **8. 把“不稳定 app”误当成“系统整合失败”**





你已经说得很清楚：



- 语音助手本身可能不稳定
- 现在先不修





这很重要。因为 TM3 的目标不是“所有 app 稳定”，而是：



- 能编译
- 能烧录
- 功能链能跑起来





风险是：



- 工程师看到语音助手偶发蓝屏
- 就开始全局修改系统
- 结果把 TM3 变成 bug fixing swamp





正确做法是：



- 区分“整合失败”与“app 本身遗留 bug”
- TM3 只证明集成成功，不证明每个 app 已经产品化稳定







# **9. 把 TM3 做成“功能整合 + 安全整合”二合一**





这是非常危险的诱惑。



你现在已经明确：



- TM3 只做内部工程版
- secure / 混淆 / bin2 / bin3 回到后续 TM4+





如果工程师在 TM3 顺手把 secure 逻辑也并回来，后果就是：



- 变量太多
- 一旦出问题完全无法定位
- 后续 TM4 的意义被打掉





正确做法是：



- TM3 只整合功能
- TM4 再重新走安全流程







# **10. 没有分批接入**





TM3 最稳的方式不是“一次性全部并入”，而是分批：



第一批：



- Bazar
- demo app 基础目录
- 必要 LVGL runtime





第二批：



- MMI 入口 hook
- 下载链路





第三批：



- 语音助手 / 游戏等具体 app 验证





这样一旦炸，你知道是哪一批炸的。



------





# **我给你的管理建议**





你要明确告诉工程师，TM3 的验收标准不是“所有功能完美”，而是：



1. 工程能编译
2. 能烧录
3. 能开机
4. 能进入 Bazar
5. 能下载并启动至少一个 LVGL app
6. 没有破坏现有 DAP 主体





只要做到这六条，TM3 就算成功。



------





# **一句话总结**





TM3 不是代码 merge 问题，

TM3 是**系统边界控制问题**。



谁试图用“覆盖替换”来省时间，谁就在给你埋下一次大的工程事故。



把 TM3 做对，后面 TM4 的安全重建才有基础。