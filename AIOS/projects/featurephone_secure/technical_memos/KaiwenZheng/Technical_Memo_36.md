

# **Technical Memo 36 — Unisoc平台API/Capability全量普查与分层决策报告**





**Project:** AIOS Feature Phone Platform



**Subsystem:** DAP / Adapter / System Integration / Architecture



**Author:** [Engineer Name]



**Priority:** HIGH



**Date:** 2026-03-23



------





## **Background**





当前AIOS平台已经完成：



- DAP runtime（支持bin重定位执行）
- 基础APP开发能力
- TM35：已完成“DAP已接入API”的inventory、YAML注册与报告





但存在关键问题：



> 当前我们只知道“DAP里有什么”，但不知道“Unisoc整个平台有什么”。



具体表现：



1. API认知不完整

   

   - TM35仅覆盖已接入DAP的API
   - Unisoc SDK / headers / 文档中的大量能力未被系统梳理

   

2. 无法进行架构决策

   

   - 哪些能力应迁入DAP？
   - 哪些应做成Service？
   - 哪些必须留在Adapter/HAL？
   - 哪些应完全禁止APP访问？

   

3. DAP存在方向风险

   

   - 有退化为“Unisoc API wrapper集合”的风险
   - 缺乏明确层级边界

   





结论：



> 当前缺失的是**全平台能力地图（Capability Map）与分层认知**



------





## **Objective**





本任务目标：



构建AIOS第一版：





# **Unisoc Platform Capability Census（能力普查）**





必须输出：



1. 全平台模块地图（Module Map）
2. 全量API/能力清单（含文档+代码）
3. 能力分层标签（不做最终决策，但做预分类）
4. 模块级分析报告（支持后续决策）
5. 决策支撑总报告（给架构层使用）





------





## **Current State**





当前状态：



- DAP API已部分整理（TM35）
- Unisoc SDK未系统扫描
- PDF文档（MMI / PHONE / TCPIP / HAL等）未结构化利用
- 无模块级统一视图





现状本质：



> 我们在“局部开发系统”，而不是“基于全局认知设计系统”



------





## **Scope**





本任务包括三大来源的统一梳理：



------





### **Part 1 — Code扫描（必须）**





扫描：



- Unisoc SDK headers（*.h）
- Mocor源码中相关模块
- 当前DAP wrapper代码





提取：



- API函数
- struct定义
- enum/宏
- callback/event接口





------





### **Part 2 — 文档解析（关键）**





必须系统解析以下类型文档：



- MMI开发指南
- PHONE模块接口
- TCPIP / GPRS接口
- AUDIO / MEDIA接口
- HAL接口（SPI / I2C / SDIO / INT等）
- 设备规格文档





提取：



- 模块划分
- API列表
- 事件模型
- 调用流程（非常重要）
- 模块依赖关系





------





### **Part 3 — Capability建模（核心）**





将 code + 文档信息统一建模为：





#### **1. 模块（Module）**





#### **2. 能力（Capability）**





#### **3. API（Function）**





------





## **Output Structure**







### **1. Capability Registry（新增核心）**



```
/aios-capability-registry/
  modules/
    ui.yaml
    telephony.yaml
    network.yaml
    storage.yaml
    device.yaml
    media.yaml
    hal.yaml
```



------





### **YAML结构（模块级）**



```
module: telephony
source:
  - PHONE_doc
  - sdk_headers

description: SIM / network / call / SMS / 4G / IMS

capabilities:
  - name: sim_management
  - name: network_registration
  - name: call_control
  - name: sms
  - name: cell_broadcast

apis:
  - MNPHONE_GetSimStatus
  - MNPHONE_Dial
  - MNPHONE_SendSMS

events:
  - SIM_STATUS_CHANGED
  - NETWORK_ATTACH
  - INCOMING_CALL

dependency:
  - device
  - timer
```



------





### **2. API Registry（延续TM35）**





继续使用：

```
/aios-api-registry/registry/*.yaml
```

但新增字段：

```
capability: call_control
module: telephony
layer: SERVICE_CANDIDATE
```



------





### **3. 模块报告（必须）**



```
/module_reports/
  telephony.md
  network.md
  ui.md
  storage.md
```

每个报告必须包含：



- 模块职责
- 子能力划分
- API分类
- 调用流程（流程图/文字）
- 与其他模块依赖
- 初步分层判断（不做最终决策）





------





### **4. 总报告（最重要）**



```
/master_report.md
```

必须回答：



1. Unisoc平台有哪些模块（完整列表）
2. 每个模块的复杂度与重要性
3. 哪些模块最影响APP架构
4. 哪些模块应优先Service化
5. 哪些模块明显属于HAL/Adapter
6. 当前DAP覆盖率（%）





------





## **Layer Tagging（预分层，必须）**





每个API/Capability必须标记：

| **标签**          | **含义**          |
| ----------------- | ----------------- |
| APP_CANDIDATE     | 可直接给APP       |
| SERVICE_CANDIDATE | 应通过Service封装 |
| ADAPTER_ONLY      | 仅Adapter使用     |
| OS_INTERNAL       | 系统内部          |
| UNKNOWN           | 未判断            |

⚠️ 本阶段不做最终决策，只做预标记



------





## **Constraints**





1. 必须覆盖“文档 + 代码”，不能只做一侧
2. 不允许只输出文档，必须YAML结构化
3. 不允许只列API，必须包含模块与能力
4. 不做废接口判断（避免误判）
5. 不允许将HAL直接定义为APP接口





------





## **Expected Deliverables**





1. /aios-capability-registry/modules/*.yaml
2. /aios-api-registry/registry/*.yaml（扩展）
3. /module_reports/*.md
4. /master_report.md





------





## **Verification Method**





- 覆盖所有核心模块（UI/PHONE/Network/Storage等）

- 每个模块有YAML + 报告

- 每个API有layer标签

- 文档与代码来源一致

- 至少选取1个APP路径验证：

  

  - UI → Network → Storage → Device

  





------





## **Potential Risks**







### **Risk 1 — 只扫代码，不看文档**





导致丢失模块结构与调用流程



→ 必须双源验证（code + PDF）



------





### **Risk 2 — 变成“API列表收集”**





无能力建模



→ 必须引入 capability 层



------





### **Risk 3 — 过早做架构决策**





导致错误抽象



→ 本阶段只做“标记”，不做“裁剪”



------





### **Risk 4 — YAML失控**





结构不统一



→ 必须使用TM35 schema校验



------





## **References**





- TM35 输出（API registry / reports）
- Unisoc SDK headers
- MMI / PHONE / TCPIP / HAL 文档
- Technical Memo Template 





------





## **Final Instruction（最关键）**





> 本任务不是“整理资料”，

> 而是建立AIOS的**世界模型（World Model of Platform Capabilities）**。



> 只有当我们知道“整个平台有什么”，

> 才能决定“DAP应该是什么”。



> 在这一步之前，所有API设计都是盲人摸象。



------



::