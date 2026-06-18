# **Technical Memo 35 — AIOS API梳理、YAML注册与决策报告生成（V2）**





**Project:** AIOS Feature Phone Platform



**Subsystem:** DAP / Adapter / System Integration



**Author:** [Engineer Name]



**Priority:** HIGH



**Date:** 2026-03-23



------





## **Background**





当前AIOS平台已经具备：



- DAP loader + bin重定位能力
- 初步APP开发能力
- 已迁入部分Unisoc API





但当前问题本质为：



> API处于“无结构增长状态”，无法支撑规模化APP开发与平台演进



具体表现：



1. API无统一注册机制（散落在代码中）

2. 无法回答：

   

   - 当前到底有多少API？
   - 哪些是稳定的？
   - 哪些可以开放？

   

3. 无法进行技术决策：

   

   - 是否可以开放SDK？
   - 哪些能力应该做Service？
   - 哪些必须封装？

   





结论：



> 当前缺的不是“更多API”，而是**API资产化与可分析能力**



------





## **Objective**





本任务目标：



构建AIOS第一版**API资产体系 + 决策支撑系统**



必须完成三件核心事情：





### **1. API Inventory（全量梳理）**





建立完整API清单





### **2. API YAML Registry（结构化注册）**





将所有API转化为**机器可读格式**





### **3. API Analysis Report（决策报告）**





输出可支持架构决策的分析结果



------





## **Current State**





当前API状态：



- 分散在：

  

  - DAP源码
  - Unisoc SDK
  - MMI / PHONE模块

  

- 无统一入口

- 无版本管理

- 无分类体系

- 无依赖关系记录





结果：



> 无法做系统性演进，只能“凭经验开发”



------





## **Scope**







### **Part 1 — API Inventory（梳理）**





对以下模块进行全量扫描：



- MMI
- PHONE
- 文件系统
- 网络
- 音频
- 输入设备
- 设备状态
- 定时器/系统能力





输出：

```
api_inventory.md
```

每个API必须包含：



- 名称
- 所属模块
- 参数列表
- 返回值
- 简要功能说明
- 来源（MMI/PHONE/自定义）





------





### **Part 2 — YAML Registry（核心）**





所有API必须注册为YAML结构：

```
api:
  name: api_download_file
  module: network
  level: L1   # L1/L2/L3
  stability: beta  # stable/beta/unstable
  source: unisoc_phone
  description: download file via http

  signature:
    return: int
    params:
      - name: url
        type: char*
      - name: timeout
        type: int

  abi:
    function_id: 12
    version: 1

  constraints:
    async: true
    max_block_time_ms: 50

  dependency:
    - network_stack
    - storage

  exposure:
    app_accessible: true
    sdk_exposed: false
```



------





### **YAML字段规范（必须遵守）**



| **字段**    | **含义**              |
| ----------- | --------------------- |
| name        | API名称               |
| module      | 所属Service模块       |
| level       | L1/L2/L3              |
| stability   | 稳定性                |
| source      | 来源（MMI/PHONE/DAP） |
| signature   | 参数定义              |
| abi         | ABI信息               |
| constraints | 调用限制              |
| dependency  | 依赖                  |
| exposure    | 是否开放              |



------





### **输出目录结构**



```
/aios-api-registry/
  registry/
    ui.yaml
    network.yaml
    storage.yaml
    phone.yaml
    device.yaml
    media.yaml

  schema/
    api_schema.yaml

  reports/
    api_summary.md
    api_gap_analysis.md
    api_risk_analysis.md
```



------





## **Part 3 — Analysis Report（决策核心）**





必须输出三份报告：



------





### **1. API Summary（全局视图）**





统计：



- API总数
- 各模块API数量
- L1/L2/L3分布
- stable/beta比例





输出：

```
api_summary.md
```



------





### **2. API Gap Analysis（能力缺口）**





分析：



- 哪些关键能力缺失（例如：

  

  - 下载管理

  - 文件缓存

  - UI组件

    ）

  

- 哪些能力重复实现

- 哪些API设计不合理





输出：

```
api_gap_analysis.md
```



------





### **3. API Risk Analysis（风险分析）**





识别：



- 直接暴露底层API（危险）
- ABI不稳定接口
- 强耦合接口
- 不可迁移接口





输出：

```
api_risk_analysis.md
```



------





## **Part 4 — Service Mapping（架构输出）**





基于YAML，生成：

```
aios_service_architecture.md
```

内容：



- Service划分（UI / Network / Storage 等）
- 每个Service API列表（来自registry）
- Mermaid架构图





------





## **Part 5 — ABI候选生成（自动化）**





从YAML中自动生成：

```
// abi_v1_draft.h
struct AIOS_API_TABLE {
    ...
};
```

规则：



- 按module分组
- function_id自动生成（不可重复）
- 顺序固定





------





## **Out of Scope**





不包括：



- 实际代码重构
- 性能优化
- UI开发
- SDK发布





------





## **Constraints**





1. 必须使用YAML（禁止只写文档）
2. 每个API必须唯一ID
3. ABI信息必须填写（即使是草案）
4. 不允许直接复制Unisoc API（必须抽象）
5. API数量 < API质量





------





## **Expected Deliverables**





1. /aios-api-registry/registry/*.yaml
2. /reports/api_summary.md
3. /reports/api_gap_analysis.md
4. /reports/api_risk_analysis.md
5. aios_service_architecture.md
6. abi_v1_draft.h





------





## **Verification Method**





- YAML可解析（lint通过）
- API无重复ID
- 每个API有level与module
- 报告与YAML一致
- 至少1个APP能完全映射到Service API





------





## **Potential Risks**







### **Risk 1 — 工程师只做“文档整理”**





**Mitigation：**

必须产出YAML + 报告



------





### **Risk 2 — YAML设计不规范**





**Mitigation：**

提供schema校验



------





### **Risk 3 — API分类随意**





**Mitigation：**

必须review（架构师审批）



------





### **Risk 4 — 过度抽象**





**Mitigation：**

以“APP开发可用性”为标准



------





## **References**





- DAP源码
- Unisoc SDK
- MMI开发指南
- PHONE模块接口文档
- Technical Memo Template 





------





## **Final Instruction**





> 本任务输出的不是“整理结果”，

> 而是AIOS未来所有工程的基础数据层。



> YAML = 你的“API数据库”

> 报告 = 你的“架构决策依据”



> 没有这一步，你永远只能靠经验开发。



------



:::



------





## **我帮你把这一步的本质讲清楚（很重要）**





你现在做的其实不是“梳理API”，而是在做三件更高级的事：





### **1. 把“代码能力”变成“数据资产”**





以前：

```
API = 写在C代码里
```

现在：

```
API = YAML数据库 + 可分析
```



------





### **2. 把“架构决策”变成“数据驱动”**





以后你可以回答：



- 我们现在开放SDK安全吗？
- 哪个模块最不稳定？
- 哪个模块最缺能力？
- 哪些API必须重构？





------





### **3. 为未来自动化打基础**





后面你可以：



- 自动生成 SDK
- 自动生成文档
- 自动生成 ABI header
- 自动检测 breaking change





------

