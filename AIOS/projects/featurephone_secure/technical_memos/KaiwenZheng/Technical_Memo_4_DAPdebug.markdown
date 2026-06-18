## **Technical Memo — 修复 DAP-on-UNISOC：补齐 DAP Core 的 OS/HAL 适配层（在不影响“不开宏”构建的前提下）**





面向对象：Windows 11 新工程师（不熟悉 Unisoc/Mocor/MTK/DAP）

项目：NBS_FuturePhone_unisoc_mocor（UNISOC T127 / Mocor BSP + DAP 集成）

目标版本：v1.1（在 v1.0 可稳定构建基础上，推进 “开宏后 DAP core 可编译链接”）



------





### **0. 背景与结论（你先把这段看懂）**





1. **不开 DAP 宏时项目可稳定构建**：说明现有 Mocor BSP 工程链路 OK，构建系统问题已基本清完。
2. **开 DAP 宏后失败集中在 DAP/core**：这不是 Mocor 的问题，是 **DAP core 仍携带“旧平台 OS 抽象层假设”**（MTK/旧 SDK 的类型、常量、接口命名）。
3. 本轮选型：**走 Option A（补齐 shim layer / OS HAL 适配层）优先**，不做“重构 DAP core”。原因：第一性原理——要快速验证“模块→DAP→Adapter→Mocor GUI”链路通，不要把工程变成考古重写。
4. DAP Loader 的运行路径：**不是扫描固定目录启动**，而是通过 **FMM 把“用户选中的文件完整路径”传给 DAP**，再打开 .bin 读入、做 BSS、跳转入口。这个行为必须保持一致。 





> 你最终要做到：



- > **不开宏 = 系统行为完全不变**（零侵入、零副作用）

- > **开宏 = 固件里包含 DAP（Loader+Registry+Glue），并且从“文件管理器 FMM 的菜单入口”对选中的 .bin 执行** 





------





### **1. 本轮任务目标（必须达成）**







#### **1.1 目标**



在 **不修改任何非 DAP 业务模块**（MMI/驱动/BASE 等）的前提下，仅通过：



- DAP/platform/unisoc/（unisoc OS 适配层）
- 必要时 DAP/core/（增加平台兼容宏/typedef/常量，但不得破坏 MTK 版本逻辑）





使得 **ENABLE_DAP 打开后，DAP 库能够编译 + 链接通过**（先不追求运行时功能全量）。





#### **1.2 范围边界（重要）**





- ✅ 允许改：DAP/ 目录内任意文件（core/platform/sdk/README）
- ❌ 禁止改：Mocor 业务代码（除非是 DAP 接入点已有宏包裹且只改 include path/菜单挂载点；本轮原则上不动）
- ✅ 允许新增：docs/dap_debug/... 下的 debug 记录文档和日志





------





### **2. 你要先理解：DAP 是什么（最低理解到这里）**





- DAP 的 .bin 是一个可加载模块，有固定头结构（MTK 版本验证过），Loader 会把 OSAPI/Register 等函数表填进头里，再跳转入口。 
- 地址重定位/加载地址修正是 P0（没有它就无法从 FS/T 卡跑 .bin）。Loader 的执行流程（打开→读入→BSS→跳转）已在现有 README 固化。 
- UNISOC 侧文件映射策略已经明确：哪些复用 MTK，哪些需要新建 unisoc 文件。 





------





### **3. 当前失败点的“工程化解释”（你要用这个顺序逐个消灭）**





你收到的失败项（OS_OK/OS_ERROR/OS_NULLAPI、mmitheme_pubwin.h、TCaclKeyEvent 重定义、InterfaceRegister_Get 未定义引用、_LONG32 未定义）本质上分成三类：





#### **A 类：DAP core 自带的“旧平台基础类型/常量”缺失**





- OS_OK / OS_ERROR / OS_NULLAPI
- _LONG32 之类





**处理原则**：不要把这些散落在各处“临时补丁式”修，必须集中收敛成 **一个 UNISOC shim 头**，统一入口。





#### **B 类：DAP core 引入了“某个 MMI 主题/弹窗头文件”，但你工程里不一定存在**





- mmitheme_pubwin.h not found





**处理原则**：你不能强依赖“主题层头文件名”，必须通过 **“以函数为准”** 找到 Mocor 里真正提供弹窗 API 的头（例如你们之前选用的 MMIPUB_OpenAlertWinByTextId/MMIPUB_OpenAlertWinByTextPtr），把 DAP 的 GUI 能力收敛到一个 dap_gui_unisoc.h/.c 封装里。 





#### **C 类：符号/类型冲突或链接缺失（通常是“文件没编进库”或“头重复 typedef”）**





- TCaclKeyEvent redefinition（典型：两个头都 typedef 了一次）
- InterfaceRegister_Get undefined reference（典型：实现文件没参与编译，或宏条件把实现裁掉了）





**处理原则**：先证明 **对象文件是否进入 link line**，再讨论改代码。



------





### **4. 实施方案（按这个步骤做，不要跳）**







#### **Step 1 — 建立“唯一真源”的 UNISOC Shim 入口（P0）**



在 DAP/platform/unisoc/ 新增（或完善）：



1. dap_unisoc_shim.h（唯一入口头）

   内容包含：







- 基础 typedef（把 _LONG32 等映射到标准 int32/uint32）
- 常量映射：#define OS_OK ...、OS_ERROR ...、OS_NULLAPI ...（用最小语义满足 DAP core：成功/失败/空指针 API）
- 统一 include 顺序，避免 Mocor 头重复包含导致冲突（必要时在此处加 include guard 策略）







1. dap_unisoc_shim.c（如果需要放少量函数封装，也放这里；但更推荐下面分模块）





> 要求：



- > DAP/core 里只允许通过 #if defined(ENABLE_DAP) && defined(DAP_PLATFORM_UNISOC) 引入该头

- > 不允许在 core 各文件里到处 #define OS_OK 这种“撒胡椒面”补丁







#### **Step 2 — 把 GUI 依赖从“头文件名”改为“能力封装”（P0）**



你们已经确认 GUI 最小能力就是弹窗提示（用于验证链路）。 



在 DAP/platform/unisoc/ 新增：



- dap_gui_unisoc.h/.c





对外提供 DAP 侧统一接口，例如：



- DAP_GUI_AlertTextId(...)
- DAP_GUI_AlertTextPtr(...)





内部只 include “你在 Mocor 工程里实际能找到的头文件”。

**你要做的不是“找 mmitheme_pubwin.h”，而是：**



- 全仓搜索 MMIPUB_OpenAlertWinByTextId 的声明在哪个头里
- 只 include 那个“真实存在”的头
- 把 DAP core 中对 mmitheme_pubwin.h 的依赖替换为 include dap_gui_unisoc.h





> 注意：这一步必须保证“不开宏不受影响”，因此所有 include 都要在 #ifdef ENABLE_DAP 下。





#### **Step 3 — OSInterface / Registry 的符号完整性（P0）**



InterfaceRegister_Get undefined reference 的优先级很高，因为这属于“架构关键部件缺失”。



你需要做两件事：



1. **确认 DAP_InterfaceRegister.c 是否真的被编进 DAP library**







- 在工程的 DAP 模块 makefile/工程文件里打印/确认编译列表（不要猜）
- 如果没编进去：修 build 规则（这不算改业务代码）







1. 如果编进去了仍 undefined：







- 检查是否被宏裁掉（例如 #ifdef MTK 把实现包住了）
- 统一改成：实现不裁，平台差异通过 shim 提供底层能力（内存/锁/日志）





> 你们之前的“哪些文件复用/哪些新建”的 mapping 已经写清楚了，你照着对即可。 





#### **Step 4 — 解决** 

#### **TCaclKeyEvent redefinition**

#### **（P1）**



这个大概率是 “DAP core 的某个头里 typedef 了一遍，同时 Mocor 的输入法/按键头也 typedef 了一遍”。



处理顺序：



1. 先定位两个定义来源（文件+行号），写到你的 docs/.../README.md 里（必须可审计）。
2. 只允许采用两种修法之一（选侵入最小的）：







- **修法 A（推荐）**：在 DAP 的 typedef 处加 #ifndef TCaclKeyEvent 类似的 guard（或用项目里常见的 _TYPEDEF_XXX_ guard 宏风格）
- 修法 B：调整 include 顺序/删掉不需要的 include（但要非常小心级联）







#### **Step 5 — 补齐 OS 常量/错误码语义（P1）**



OS_OK/OS_ERROR/OS_NULLAPI 这类常量必须在 shim 中统一定义，语义建议：



- OS_OK：0
- OS_ERROR：-1（或 1，取决于 DAP core 判断方式；你必须用 dap.log 的报错点去看它怎么判断）
- OS_NULLAPI：0 或 NULL（取决于是“函数指针为空”还是“API id 为 0”；同样看 DAP core 怎么用）





------





### **5. 复测方法（你必须用“递进式”，并输出证据）**





你每解决一个类别，就复测一次，避免把错误叠加成噪音。





#### **5.1 复测命令（固定）**





- Step0：不开宏全量构建（你只需确认仍 PASS，证明你没污染系统）
- Step1：开宏只编 DAP library（最快定位）
- Step2：开宏跑到 make ... update（确保能链接到 app_main）
- Step3：开宏全链路（最后才做）







#### **5.2 交付物（强制）**



在仓库新增：



- docs/dap_debug/2026-02-XX_win11_<yourname>/README.md
- docs/dap_debug/2026-02-XX_win11_<yourname>/logs/（包含你每次编 DAP 的 log；dap.log 要保留，因为它能定位到文件行号）
- docs/dap_debug/2026-02-XX_win11_<yourname>/patch_list.md（每个 patch：文件、改动点、原因、回滚方式）





README 必须包含：



- 你新增的 shim 文件清单
- 你替换/移除的 include 依赖
- 每一个错误从“出现 → 定位 → 修复 → 复测通过”的证据链（文件+行号+关键 log）





------





### **6. 验收标准（这轮就按这个收）**





1. ✅ ENABLE_DAP 关闭：全工程 build 结果与 baseline 一致（行为完全不变）。
2. ✅ ENABLE_DAP 打开：DAP library 可编译并链接进固件（不要求运行时全部功能）。
3. ✅ FMM 入口仍是“用户选中文件 → 菜单执行 → 传完整路径给 DAP”（不是扫描固定目录）。 
4. ✅ 输出 docs 证据齐全，其他工程师能照 README 复现。





------





### **7. 你开工的第一件事（必须照做）**





- 先在你本机开 ENABLE_DAP，只编译 DAP library（最快暴露 core 问题），把第一批错误按上面 A/B/C 分类写进 docs/.../README.md。
- 然后从 **Step 1（shim 入口）** 开始做，不要从“改 DAP core 某个文件”开始乱补。





------






