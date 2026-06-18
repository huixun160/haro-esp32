# **Technical Memo**





**Title:** TM29-1 — Voice Assistant App Asset Discovery and Dependency Mapping



**Project:** AIOS Feature Phone Platform



**Subsystem:** App Integration / DAP / Security / Build



**Author:** AIOS Core Architecture



**Priority:** HIGH



**Date:** 2026-03-15



------





## **Background**





TM28-R 已经完成，并成功从 TM27 clean baseline 恢复 TM28 全部功能。当前系统状态：



- TM27 基线可信
- TM28 payload encryption 已恢复
- v2 BIN2 回归验证通过
- v3 加密 BIN3 验证通过 





这意味着当前安全基线重新可用，可以继续推进 TM29：

```
引入语音助手并调通 bin2/bin3 执行
```

但当前存在一个现实问题：



- 同事的语音助手 APP 代码位于此前的 contaminated snapshot / 外部分支
- 根目录中的主线代码当前可信，但其中并不包含完整的语音助手应用资产
- contaminated snapshot 中关于 APP 的内容相对可信，但其中系统/安全目录不可信





因此不能直接“整目录合并”。

必须先进行一次严格的 **应用资产识别与依赖梳理**，明确：



1. 语音助手 APP 的源码文件有哪些
2. 它依赖哪些库、资源、脚本、配置
3. 它如何从 SDK / 工具链被打包为初始 .bin
4. 哪些资产需要迁入主线
5. 哪些目录绝对不能从 contaminated snapshot 回拷覆盖





------





## **Objective**





TM29-1 的目标只有一个：



> **找清楚语音助手 APP 的完整开发资产和依赖边界，为 TM29-2 的迁移与编译做准备。**



本 memo 不要求完成：



- 代码迁移
- 编译
- 烧录
- 运行
- bin2 / bin3 打包验证





TM29-1 只回答：

```
语音助手 APP 到底由哪些代码和依赖组成？
```



------





## **Current State**





当前可信状态如下：





### **可信**





- TM27 / TM28 / TM28-R 主线安全代码
- AIOS/ 下 technical memos / feedback / pitfall / memory / runbook 等文档资产
- TM27 clean baseline
- TM28 restored security baseline 







### **不可信 / 仅可参考**





- contaminated snapshot 中的系统级目录覆盖结果

- contaminated snapshot 中可能被旧版本覆盖的：

  

  - DAP/
  - MMI/
  - 其它公共模块

  







### **相对可信但需审计**





- contaminated snapshot 中由同事新增/维护的 **语音助手 APP 相关代码**
- 以及它的资源、脚本、构建说明、SDK 使用方式





------





## **Scope**





本任务包括：



1. 从 contaminated snapshot 中识别语音助手 APP 相关资产
2. 梳理其构建为初始 .bin 所需的依赖链
3. 梳理其运行时依赖（DAP / LVGL / MMI / 资源 / 音频 / 网络等）
4. 列出“迁移白名单”
5. 列出“禁止覆盖目录”
6. 输出迁移计划输入文档，供 TM29-2 使用





------





## **Out of Scope**





本任务明确 **不包括**：



1. 将语音助手代码真正迁入主线
2. 修改主线代码
3. 编译或烧录
4. 生成初始 .bin
5. 生成 .bin2 / .bin3
6. 做语音助手运行验证
7. 修改安全逻辑 / DAP loader / payload encryption 代码
8. 修复语音助手本身 bug





TM29-1 只是：

```
识别 + 梳理 + 形成迁移清单
```



------





## **Constraints**





1. **不允许整目录复制**

   

   - contaminated snapshot 不能整目录回拷
   - 必须文件级或模块级白名单方式识别

   

2. **不允许触碰当前安全基线**

   

   - TM28-R 恢复后的安全主线不能被覆盖

   - 尤其是：

     

     - Third-party/DAP/security/
     - DAP_Loader_unisoc.c
     - dap.mk
     - bin2_loader.*
     - device_binding.*
     - bin2_pack.py

     

   

3. **必须回顾历史坑**

   工程师在开工前必须回顾：

   

   - pitfall.md

   - memory.md

   - TM28-R feedback

     特别注意：

   - dap.mk 漏改

   - Logel trace 链丢失

   - payload offset / BSS memcpy 问题

   - free offset pointer / ownership 问题

   - contaminated snapshot 不可信系统目录混入主线的问题

   

4. **必须保持“资产发现”和“代码迁移”分离**

   TM29-1 不能顺手改代码。

   一旦边发现边迁移，就会再次失控。





------





## **Expected Deliverables**





工程师必须提交以下内容：





### **Deliverable 1 — 语音助手资产清单**





文件建议：

```
AIOS/feedback/TM-029-1-asset-inventory.md
```

内容至少包括：



- 源码文件列表
- 头文件列表
- 资源文件列表
- 配置文件列表
- 脚本/批处理列表
- 构建入口
- 输出物（初始 .bin）生成方式





------





### **Deliverable 2 — 依赖映射图**





文件建议：

```
AIOS/docs/architecture/voice_assistant_dependency_map.md
```

内容至少包括：



- 语音助手 APP → DAP 接口依赖
- 语音助手 APP → LVGL 依赖
- 语音助手 APP → 资源/音频/网络依赖
- 语音助手 APP → SDK/工具链/批处理依赖





------





### **Deliverable 3 — 迁移白名单**





文件建议：

```
AIOS/feedback/TM-029-1-migration-whitelist.md
```

必须明确：



- 哪些文件/目录可以迁移
- 哪些文件/目录禁止迁移
- 哪些文件需要人工合并而不是直接覆盖





------





### **Deliverable 4 — 风险清单**





文件建议：

```
AIOS/feedback/TM-029-1-risk-list.md
```

需要指出：



- 语音助手可能依赖的旧版 DAP / MMI 接口
- 与当前 TM28-R 安全主线冲突的目录
- 迁移时可能导致 build 失败的点
- 可能会破坏 Logel trace / dap.mk / header consistency 的点





------





## **Verification Method**





TM29-1 的验收不以“能跑起来”为标准，而以“资产和边界是否清楚”为标准。





### **必须满足**





- 能列出语音助手 APP 的主要源码目录
- 能说明初始 .bin 是通过什么 SDK / 批处理 / 工具链生成
- 能说明它依赖哪些 DAP / LVGL / MMI / 资源模块
- 能明确主线中哪些安全模块绝不能被 contaminated snapshot 覆盖
- 能给出 TM29-2 的最小迁移白名单





如果这些答不出来，就不允许进入 TM29-2。



------





## **Potential Risks**





- **Risk 1 — 把 contaminated snapshot 当成可直接合并的代码源**

  这是当前最大的风险。

  contaminated snapshot 只能作为“资产发现来源”，不能作为“系统主线覆盖来源”。

- **Risk 2 — 语音助手 APP 的构建依赖隐藏在脚本/批处理中**

  很多应用工程的关键依赖不在代码里，而在：

  

  - .bat

  - .mk

  - SDK 配置

  - 工具链参数

    必须把这些也识别出来。

  

- **Risk 3 — 语音助手 APP 依赖旧版接口名 / 旧版目录结构**

  如果 TM29-2 不先知道这些，迁进来后才会爆炸。

- **Risk 4 — 误迁移系统级目录**

  一旦 DAP/、MMI/ 或 build 配置被旧版本覆盖，会再次破坏安全基线。





------





## **References**





- TM28-R Feedback — Security Baseline Recovery 
- pitfall.md
- memory.md
- AIOS/technical_memos/
- contaminated snapshot
- TM27 / TM28 / TM28-R 相关文档与反馈





------





## **Execution Plan**







### **Step 1 — 冻结当前可信主线**





在开始前，工程师必须确认当前主线目录为：

```
TM28-R restored baseline
```

并且不得在 TM29-1 中对主线进行修改。



------





### **Step 2 — 仅从 contaminated snapshot 中做“资产发现”**





重点查找：



- 语音助手 APP 源码目录
- app entry / main 函数
- LVGL UI 代码
- 音频/语音相关模块
- 资源文件
- 批处理 / SDK 打包脚本
- .bin 生成流程说明





必须标记：



- 文件路径
- 文件类型
- 作用
- 是否疑似与主线冲突





------





### **Step 3 — 找出“初始** 

### **.bin**

###  **的生成链”**





工程师必须明确回答：



1. 语音助手 APP 从哪个入口开始编译？

2. 它是怎样使用 SDK / 批处理生成 .bin？

3. 生成 .bin 前是否依赖：

   

   - 特定目录结构
   - 特定资源打包
   - 特定头文件
   - 特定 DAP API

   





这一步是 TM29-1 的关键。



------





### **Step 4 — 梳理依赖层次**





建议至少把依赖分成三层：





#### **Level A — App 自身资产**



例如：



- voice_assistant_app.c
- voice_ui.c
- voice_prompt.c
- 资源文件







#### **Level B — App 直接依赖的内部 SDK / DAP 接口**



例如：



- UI 创建
- 文件读写
- 音频播放
- 网络请求
- 线程/消息机制







#### **Level C — 系统级公共依赖**



例如：



- MMI/
- DAP/
- LVGL/
- 资源管理
- build system





------





### **Step 5 — 形成白名单和黑名单**







#### **白名单**



这些是 TM29-2 可以迁移或人工拣回的内容：



- app 自身源码
- app 自身资源
- 明确属于同事新增的脚本/配置
- 直接相关且经过确认的头文件







#### **黑名单**



这些禁止直接覆盖：



- Third-party/DAP/security/
- DAP_Loader_unisoc.c
- bin2_loader.*
- device_binding.*
- dap.mk
- 与 TM28-R 已恢复安全逻辑直接相关的系统文件





------





### **Step 6 — 输出迁移计划输入**





TM29-1 的最后产出，必须让你能一眼看到：

```
哪些文件迁
哪些不迁
哪些要人工 merge
为什么
```

这会直接作为 TM29-2 的输入。



------





## **Pitfalls Review (Must Read Before Starting)**





工程师在开工前必须重新回顾：





### **1.** 

### **dap.mk**





过去已经多次踩坑。

TM29-1 虽然不改代码，但必须识别语音助手是否依赖新的：



- source file

- include path

- build entry

  否则 TM29-2 一上来就会编译失败。







### **2. Logel trace**





TM29-2 / TM29-3 迟早要看运行日志。

TM29-1 就要识别语音助手是否：



- 自己带 trace
- 依赖旧 trace 宏
- 与当前 SCI_TRACE_LOW 路径冲突







### **3. contaminated snapshot 的系统目录不可信**





这不是主线。

这只是“应用资产仓库”，不是“系统基线仓库”。





### **4. 安全主线不能被应用开发代码反向污染**





TM28-R 花了代价才恢复起来。

TM29-1 的职责就是避免 TM29-2 再次把它毁掉。



------





## **Success Criteria**





TM29-1 完成的标准是：



1. 语音助手 APP 相关代码资产已被识别
2. 初始 .bin 的生成链路已被说明清楚
3. 与主线的冲突边界已被识别
4. 已形成清晰的迁移白名单/黑名单
5. 可以安全地进入 TM29-2





------





## **Final Note**





TM29-1 不是开发任务。

TM29-1 是一次：

```
资产识别 + 依赖审计 + 迁移边界冻结
```

如果这一步做不好，TM29-2 会再次把：



- 安全主线
- build system
- DAP 接口边界





一起拖进混乱。



所以这一步必须克制、慢、清楚。