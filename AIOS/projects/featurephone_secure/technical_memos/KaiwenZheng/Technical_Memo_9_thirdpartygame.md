# **Technical Memo — 逆向工程摸底：Third Party** 

# **od_game**

#  **静态库（.a/.o）可逆向性与架构复原**





**Owner（你）**：AIOS 联合创始人 / 工程合伙人

**Assignee（工程师）**：Antigravity

**Priority**：P0（直接决定 DAP 对外交付形式）

**目标交付日期**：按里程碑交付（M1/M2/M3），每个里程碑必须有可审阅产物

**范围**：Unisoc Mocor 平台 Third Party 库中的 od_game（重点：lib/ 下的 .a 与 .o/.obj）



------





## **0. 背景（工程师必须理解为什么要做）**





我们准备把自研 DAP 以类似 Third Party 的形式（静态库 .a + obj）交付给外部厂商集成。

但我们已经确认：二进制和库产物可被逆向到 C 级别逻辑，这会导致商业灾难（抄走 DAP + App 生态）。



od_game 是现成样本：它就是别人给 Unisoc 平台交付的 Third Party 库。

我们要用它回答一个现实问题：



> **如果把 DAP 做成 od_game 这种交付形态，外部拿到 pac/库之后，逆向成本到底有多低？我们能不能接受？**



------





## **1. 本次任务的最终输出（缺一不可）**





工程师最终交付一个文档包（建议放 repo：/docs/reverse_od_game/）：





### **1.1 《od_game 逆向工程报告 v1》（Markdown）**





必须包含以下章节：



1. **资产清单与构成（Inventory）**







- od_game 的目录树（含 lib/、include/、bin/ 或其他）
- .a 中包含的对象列表（每个 .o 的大小、符号数量、是否含调试段）
- 是否存在导出头文件（.h）/接口文档/示例代码（如果有，必须结合分析）







1. **构建与链接关系（Build & Linkage）**







- od_game 静态库被哪些工程模块引用（Makefile/mk/cfg）
- 链接参数（是否 strip、是否 LTO、是否保留符号）
- 最终产物落入 pac 的位置（在哪个 image、哪个分区）







1. **架构复原（Architecture Reconstruction）**







- 用一张 Mermaid 图画出 od_game 的模块划分（至少 6 个模块粒度）

  

  - Engine/Runtime（核心调度）
  - Resource（资源加载、文件系统）
  - Graphics/Audio/Input（如果有）
  - Script/VM（如果有）
  - IPC/Network（如果有）
  - Platform Adapter（对 OS/FS/Mocor 的适配层）

  

- 每个模块：列出关键函数/关键对象/关键数据结构（尽量恢复语义命名）







1. **接口面与关键能力（API Surface）**







- od_game 对外提供的接口函数列表（符号表 + 头文件对齐）
- 每个接口的“用途推断”（基于交叉引用 + 调用关系）
- 给出“最小可运行调用序列”（外部如何调用它跑起来）







1. **反编译可恢复程度评估（Decompilation Quality）**







- 选 10 个最核心函数：

  

  - 反编译结果（伪 C）质量评级：A/B/C（A=接近源码级）
  - 关键证据：控制流清晰度、结构体恢复、字符串/常量、函数边界准确性

  

- 必须给出“能否恢复出核心算法/状态机/协议”的结论







1. **安全性评估（Security Posture）**

   从攻击者视角给出两条路径：







- 路径 A：拿到 .a / .o（第三方交付包）→ 逆向 → 复刻

- 路径 B：拿到 pac（量产包）→ 提取 image → 定位 od_game → 逆向 → 复刻

  对每条路径：

- 成本评估：低/中/高（要用证据，不许空口）

- 关键突破点：符号/字符串/日志/表结构/魔数/固定 ABI

- 如果要让成本上升 10 倍，应该改哪些点（只写方向）







1. **对 DAP 的直接启示（Actionable Takeaways for DAP）**

   必须给出一页结论：







- “如果 DAP 按 od_game 方式交付，会被抄走到什么程度？”
- 最致命的 3 个泄露面是什么（比如字符串 API、导出符号、调试段）
- 建议的 5 个防护动作（按 ROI 排序）





------





## **2. 工程师执行步骤（按里程碑）**







### **Milestone 1：静态结构与符号层摸底（目标：搞清楚它由什么组成、接口在哪里）**





**任务**



1. 提取 .a 内所有 .o：生成对象清单（文件名、大小）

2. 对每个 .o 跑：

   

   - 符号表统计（全局/本地/弱符号）
   - 字符串统计（可见字符串数量、典型关键词）
   - 段信息（.text/.rodata/.debug* 是否存在）

   

3. 识别“对外 API”：全局导出函数 + 可能的头文件对应





**产出**



- objects_inventory.csv
- symbols_summary.csv
- strings_hotspots.txt（Top N 字符串/关键词）
- api_surface.md





------





### **Milestone 2：反编译与架构复原（目标：能画出模块图、讲清楚核心控制流）**





**任务**



1. 选择主分析工具（Ghidra/IDA/其他），建立工程并导入所有 .o

2. 先找“入口/调度核心”：

   

   - 初始化函数
   - 主循环/任务回调
   - 资源加载入口

   

3. 画调用图（call graph）并聚类成模块（至少 6 模块）

4. 反编译 10 个关键函数（必须包含：初始化、加载、调度、渲染/输出、事件分发）





**产出**



- architecture.mmd（Mermaid）
- callgraph_notes.md
- decompile_samples/（10 个函数伪 C + 解释）





------





### **Milestone 3：攻击链复现与可逆向性结论（目标：给出“被抄走”成本与 DAP 对策）**





**任务**



1. 复现“攻击者最短路径”：

   

   - 只用符号 + 字符串 + 反编译就能复原到什么程度？

   

2. 若 .a 中符号被 strip：再用交叉引用/模式匹配复原一次，评估成本

3. 给出量化指标（必须至少 5 个）：

   

   - 定位核心入口耗时（分钟）
   - 能还原的接口数量（%）
   - 能还原的数据结构数量（个）
   - 关键算法是否可复刻（是/否 + 理由）
   - 复刻一个“最小替代实现”的工作量估计（人天）

   





**产出**



- threat_walkthrough.md
- security_scorecard.md（量化表）
- dap_implications_1pager.md





------





## **3. 工具与规范（硬性要求）**





1. **所有推断必须有证据**







- 地址、函数签名、交叉引用截图、字符串命中、调用链路径
- 不允许“我感觉像是”这种话







1. **禁止输出敏感可滥用的逐步攻击教程**

   我们要的是安全评估与架构复原，不写“如何非法破解”的逐步操作手册。

   可以写工具类别与分析方法，但不要写可直接复制执行的侵入性步骤。

2. **产物必须可复现**







- 所有脚本/命令输出存 /attachments/
- 工程版本/commit hash/工具版本写清楚





------





## **4. 评审标准（你怎么才算干成了）**





你通过的标准只有四条：



1. 你能用一张图讲清楚 od_game 的模块边界和调用关系。
2. 你能列出它对外接口，并说明每个接口干什么（不是猜，是证据）。
3. 你能给出“反编译恢复到 C 级逻辑”的客观程度（A/B/C + 样例）。
4. 你能把结论映射到 DAP：**我们如果按这种方式交付，会被抄走到什么程度，以及最小代价的补救动作是什么。**





------





## **5. 我们希望你额外回答的 3 个尖锐问题（必须在结论里写）**





1. **od_game 是否做了任何防逆向？**（strip/混淆/加密/自校验/运行时解密）
2. **如果你是竞争对手，要抄 od_game，最快多久能做出“能跑的替代品”？**
3. **DAP 若以静态库交付，你认为“最现实的护城河”是什么？**（技术 vs 分发 vs 服务）





------





## **6. 交付结构（统一格式）**



```
/docs/reverse_od_game/
  od_game_reverse_report_v1.md
  api_surface.md
  architecture.mmd
  security_scorecard.md
  dap_implications_1pager.md
  /attachments/
    objects_inventory.csv
    symbols_summary.csv
    strings_hotspots.txt
    tool_versions.txt
    evidence_screenshots/
  /decompile_samples/
    func01_init.c
    func02_mainloop.c
    ...
```



------





## **7. 备注（为什么这件事是 P0）**





你现在纠结“DAP 要不要按第三方库交付”。

这件事不是靠想象决定的，只能靠 od_game 这种真实样本的逆向成本来决定。



如果 od_game 的逆向恢复率很高，那你把 DAP 交付出去等于送命。

如果 od_game 的保护足够强，我们就复制它的保护策略。



