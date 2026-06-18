# **Technical Memo：T127（Unisoc）/Mocor 功能机 BSP 遗留代码梳理与重构准备（工程执行版）**





**背景**

我们接手了一套“20 年无人维护”的功能机厂商代码：缺少 design doc、缺少模块说明、原作者不可追溯。代码本身不是最大问题；最大问题是**不可理解**导致**不可控**，后续任何改动都会以“引入随机故障/回归”为代价。

因此第一阶段目标不是“立刻重构”，而是把它变成一个**可被工程化理解、可被持续演进**的系统：能编译、能跑、能定位、能解释模块边界与依赖。



------





## **0. 总目标（必须交付）**





对基于 **展锐 T127 + Mocor 架构** 的 BSP 包（含编译脚本、ThreadX RTOS、驱动、应用）完成：



1. **系统架构图（可追溯到代码）**







- 以“启动链路 → OS/中间层 → 驱动 → 应用”为主干
- 明确每层：入口、职责、关键数据结构/接口、依赖关系、线程/任务模型、IPC、关键配置点
- 图必须能从仓库路径映射到模块（不是画给人看的 PPT 图）







1. **模块级 README.md 全覆盖（可用于新人上手）**







- 对每个一级模块（以及关键二级模块）生成 README.md：说明“它是什么/不是什么、入口在哪、怎么编译/怎么验证、对外 API/对内依赖、风险点、常见坑”







1. **依赖与调用关系清单（可自动更新）**







- 生成“模块依赖图 + 关键调用链（启动/音频/通信/输入/显示等）”
- 要求能用脚本复现（避免一次性手工梳理，后续又失效）





> 这些交付物的目的：让我们具备**做正确重构的前置条件**，而不是在黑箱里“凭感觉改代码”。



------





## **1. 工作范围（Scope）**







### **In-scope**





- 代码梳理、模块边界定义、依赖关系抽取、启动路径/线程模型/IPC/驱动栈理解
- 文档体系落地（系统级 + 模块级），以及生成脚本/工具链
- 为“后续重构”提出候选切割点与风险清单（不在本阶段做大改）







### **Out-of-scope（本阶段禁止做）**





- 大规模重写/大规模风格重构
- 引入新 OS / 替换 RTOS / 替换编译系统（除非为了“能稳定复现构建”必须最小改动）
- 大范围功能变更





------





## **2. 工程原则（第一性原理）**





1. **先可复现，再可理解，再可演进**

   构建不可复现 → 任何理解都是幻觉；理解不可验证 → 文档都是文学创作。

2. **一切结论必须能落到“路径 + 入口 + 证据”**

   “这个模块负责 XXX”必须附：源文件/符号/配置项/任务名/调用链证据。

3. **文档必须可持续更新（Docs-as-Code）**

   README/架构图与脚本一起进仓库，CI 能检查文档是否缺失、依赖图是否能生成。

4. **以 1e8 用户规模的工程标准约束重构**

   任何重构点都要回答：失败模式是什么？回滚方案是什么？如何做回归与灰度？（哪怕功能机不云端灰度，也要有版本策略与可定位性）





------





## **3. 交付物清单（Deliverables & 验收标准）**







### **D1. 构建与运行基线（Build Baseline）**





- docs/build/BUILD.md：从零到编译成功的**唯一权威步骤**
- tools/env/：环境脚本（Docker 优先；不行就脚本化依赖安装）
- 验收：新同事在干净机器上按文档能构建出目标产物（bin/pac/img 等），且能跑到已知启动点（串口日志/关键 UI/测试用例）







### **D2. 系统架构总图（System Architecture）**





- docs/arch/system_overview.md

- 至少包含 4 张图（Mermaid/PlantUML 任选，但必须可 diff）：

  

  1. Boot/启动链路图（从 bootloader 到 OS 到 app entry）
  2. ThreadX 任务/线程拓扑图（任务名、优先级、栈、消息队列/事件标志）
  3. Driver 栈分层图（HAL/抽象层/设备驱动/服务）
  4. App 框架图（应用生命周期、消息分发、关键服务调用）

  

- 验收：每张图的节点都能映射到**目录/源文件/符号**，并在文档中给出索引表







### **D3. 模块 README 全覆盖（Module READMEs）**





- 每个一级模块目录必须有 README.md
- 关键二级模块（例如：audio/radio/nv/config/pm/display/input/usb/diag 等）也必须有 README.md
- 验收：仓库根目录有 docs/MODULE_INDEX.md，列出模块、职责、owner、入口、依赖、测试方式







### **D4. 依赖图 & 调用链（Auto-generated）**





- docs/arch/deps/ 输出：

  

  - 模块依赖图（静态 include/链接依赖）
  - 关键调用链（启动/按键输入/拨号/短信/音频播放/网络注册等）

  

- tools/graph/：一键生成脚本

- 验收：在 CI 或本地运行脚本可重建同样输出；输出随代码变更可更新







### **D5. 风险与重构切割建议（Risk & Refactor Candidates）**





- docs/arch/RISKS.md：列出“高耦合/高风险/不可测/硬编码配置/时序敏感”模块
- docs/arch/REFACTOR_PLAN_CANDIDATES.md：给出 3–5 个“可落地、可回滚”的重构切入点（只提方案，不做大改）
- 验收：每条风险/候选点都给出证据与影响面





------





## **4. 执行步骤（工程师工作拆解）**





> 下面步骤按依赖关系排序，**不要跳**。





### **Phase A：仓库可读化（Readability Bootstrap）**





1. 建立文档与工具目录结构（示例）



```
/docs
  /arch
  /build
  MODULE_INDEX.md
/tools
  /env
  /graph
  /lint
```



1. 建立“代码导航能力”







- 生成 compile_commands.json（如果编译系统不支持，写 wrapper/bear 方案）
- 接入 clangd/ctags（至少能跳转定义、查找引用）
- 输出：docs/build/DEV_SETUP.md





**验收**：工程师能在 IDE 内跨模块跳转，不靠 grep 盲查。



------





### **Phase B：构建系统与产物链路梳理（Build Pipeline）**





1. 梳理编译入口脚本：构建命令、环境变量、目标产物类型
2. 输出构建产物清单：每个产物来自哪个工程/链接脚本/打包规则
3. 明确可重复构建：同 commit 产物 hash 可稳定（若做不到，说明原因：时间戳/路径注入等）





**输出**：docs/build/BUILD.md + docs/build/ARTIFACTS.md



------





### **Phase C：启动链路（Boot → Kernel → Services → Apps）**





1. 找到所有入口点（常见：bootloader entry、OS start、app main/task create）
2. 抽出“最小启动路径调用链”：







- 从 reset/启动到第一个用户态可观察行为（串口 log / UI）







1. 对每个阶段写：关键函数、关键数据结构、关键配置（nv/宏/编译开关）





**输出**：docs/arch/boot_flow.md + Mermaid 图



------





### **Phase D：ThreadX 任务模型与 IPC 拓扑**





1. 枚举所有任务创建点：任务名、优先级、栈大小、入口函数
2. 枚举 IPC：queue/event/semaphore/timer 的创建与使用位置
3. 形成“任务—消息—服务”拓扑图
4. 标出：时序敏感任务（音频/基带交互/电源管理/看门狗）





**输出**：docs/arch/threadx_tasks.md + 拓扑图 + 索引表



------





### **Phase E：模块边界与依赖（模块地图）**





按目录定义模块边界（先不争论对不对，先形成地图），每个模块至少写清：



- **Responsibility**：它负责什么/不负责什么
- **Entry Points**：初始化/线程入口/对外 API
- **Dependencies**：调用了谁、被谁调用
- **Configs**：宏、nv项、编译开关
- **Runtime**：任务/中断上下文/锁/队列
- **Test/Verify**：如何验证不坏（哪怕是最小手段：日志点/自检命令）





**输出**：每模块 README.md + docs/MODULE_INDEX.md



------





### **Phase F：自动化生成依赖图与调用链**





目标是“以后换人/迭代仍然可更新”，不是一次性人工画图。



建议最小实现：



- 静态依赖：基于 include 关系 + 链接输入（可先粗糙）
- 调用链：针对关键入口函数，用 cscope/clang 工具链或自写脚本做“符号引用追踪”
- 输出成 Mermaid/Graphviz dot





**输出**：tools/graph/ + docs/arch/deps/*



------





## **5. README.md 模板（工程师必须按这个写）**





每个模块目录下创建 README.md，至少包含以下结构（不允许缺项）：

```
# <Module Name>

## What it does
- ...

## What it does NOT do
- ...

## Key entry points
- init: <func/file>
- task: <func/file>
- irq: <func/file> (if any)

## Public interfaces
- <header>.h: functions / structs
- Notes: call context (task/irq), thread-safety

## Dependencies
- Depends on:
  - <module> (why)
- Used by:
  - <module> (why)

## Configuration knobs
- Build flags:
- NV items / runtime config:
- Default values & where defined:

## Runtime model
- ThreadX objects used:
- Locks/queues/timers:
- Timing constraints:

## Logging & debugging
- Key logs:
- How to enable verbose:

## Tests / verification
- Minimal sanity checks:
- Common failure modes & symptoms:
```



------





## **6. 系统架构图要求（别画“好看图”，要画“可定位图”）**





**必须用可版本控制的文本图**：Mermaid / PlantUML / Graphviz dot

每个图旁边必须有 “Code Index”：



- Node → 目录路径
- Node → 关键入口函数
- Node → 关键配置项





这样图才不会在两周后变成垃圾。



------





## **7. 风险点（工程上必须提前踩刹车）**





工程师在梳理时，看到以下现象必须在 RISKS.md 记录：



- 大量 #ifdef 导致“同一模块多种形态”，且无统一配置文档
- NV/校准/工厂配置分散在多处，且缺省值不明确
- ISR 里做重活、或者锁使用不规范（死锁/优先级反转风险）
- 电源管理/看门狗/时钟相关模块（最容易“改一点死机”）
- audio/radio/通信栈：时序敏感、回归成本高
- 手写内存池/自定义 malloc：泄漏与越界风险极高
- “魔法数字/硬编码地址/寄存器裸写”无注释





------





## **8. 最小协作机制（避免工程师做成“个人理解”）**





为了让输出可复用，需要这些硬规则：



1. **每个结论都要有证据链接**：文件路径 + 函数名 +（最好）行号范围
2. **每周合并一次文档**（PR 机制）：文档与脚本先合并，代码重构后面再说
3. **禁止口头知识**：任何“我觉得是这样”的内容，不写进 README 就等于不存在
4. **Owner 制**：每个模块 README 指定维护人





------





## **9. 你（工程师）开始工作的第一天 Checklist**





- 能在本地成功构建一次
- 能定位启动入口与第一条关键日志
- 能列出 10 个最关键任务/线程入口
- 能输出第一版 MODULE_INDEX.md（哪怕粗糙）
- 能生成第一版依赖图（哪怕不完整，但可复现）





------





## **10. 最终验收方式（我会怎么验收你）**





我不会看你“写了多少文档”，我只做 5 个抽查：



1. 随机点一个模块：你能在 60 秒内说清它的入口、依赖、验证方法吗？
2. 随机点一个功能（如按键输入到 UI 响应）：你能给出调用链证据吗？
3. 新同事按 BUILD.md 能从零构建成功吗？
4. 依赖图脚本能一键跑通并生成输出吗？
5. 你标记的 10 个风险点，是否都能对应到具体代码证据？





通过这 5 条，才算“这个系统开始可控”。



------

