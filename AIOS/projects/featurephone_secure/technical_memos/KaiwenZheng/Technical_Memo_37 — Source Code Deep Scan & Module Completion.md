



# **Technical Memo 37 — Source Code Deep Scan & Module Completion（模块收口与源码深扫）**





**Project:** AIOS Feature Phone Platform



**Subsystem:** DAP / Adapter / System Integration / Architecture



**Author:** [Engineer Name]



**Priority:** HIGH



**Date:** 2026-03-23



------





## **Background**





TM35 已完成：



- DAP API inventory + YAML registry + 报告





TM36 已完成：



- Unisoc 平台 capability 普查（约 750+ API）
- 12 个模块、79 个 capability
- 文档（PDF）为主导的模块建模





但当前存在关键缺口：



1. **源码未完成深扫**

   

   - headers / source 中仍存在未被识别的 API
   - 文档与代码未完全对齐

   

2. **模块尚未“收口”**

   

   - 多数模块仍停留在“轮廓级”
   - API 覆盖不完整
   - event / callback / dependency 不完整

   

3. **无法进入边界决策阶段**

   

   - 当前数据不足以支撑 DAP / Service / Adapter 分层决策

   





结论：



> TM36 完成了“广度”，TM37 必须完成“深度 + 收口”



------





## **Objective**





本任务目标：





# **完成模块级“决策就绪状态”（Decision-Ready Modules）**





必须达成：



1. 每个核心模块达到 **Module Completion**
2. 文档与源码双源对齐（Doc ↔ Code）
3. API / Event / Dependency 完整覆盖
4. 每个模块具备初步分层判断能力
5. 为 TM38（架构边界决策）提供直接输入





------





## **Scope**





本任务聚焦两个核心动作：



------





### **Part 1 — Source Code Deep Scan（源码深扫）**





扫描范围：



- Unisoc SDK headers（*.h）

- Mocor 源码：

  

  - MS_MMI_Main/source/
  - 相关模块目录（phone / tcpip / fs / audio / device）

  

- 当前 DAP wrapper 实现





必须提取：



- API函数
- struct / enum
- callback / event 定义
- 宏与配置接口
- 模块初始化流程





------





### **Part 2 — Module Completion（模块收口）**





基于 TM36 的 12 个模块，逐模块补齐：



优先模块（必须先完成）：



1. UI / MMI
2. Network（TCPIP / GPRS / socket）
3. Telephony（PHONE / SIM / SMS）
4. Storage（FS / NV / SD）
5. Device（电量 / 时间 / 输入 / 背光）
6. Audio





次优模块：



1. OS Core（thread / queue / timer）
2. Package / Download
3. Peripheral / HAL（SPI / I2C / SDIO 等）





------





## **Module Completion Criteria（必须满足）**





一个模块必须满足以下 6 条，才算完成：





### **1. 模块职责明确**





- 功能边界清晰
- 不与其他模块混淆







### **2. Capability 完整**





- 子能力划分完整（不是单一功能）







### **3. API 覆盖完整**





- 关键函数全部列出
- 不仅来自文档，也来自源码







### **4. Event / Callback 完整**





- 所有异步事件
- message / callback / notify机制







### **5. Dependency 明确**





- 依赖哪些模块
- 被哪些模块依赖







### **6. Layer Tag（预分层）**





每个 API / capability 必须标记：



- APP_CANDIDATE
- SERVICE_CANDIDATE
- ADAPTER_ONLY
- OS_INTERNAL
- UNKNOWN





⚠️ 仍然不做最终裁剪，只做预判断



------





## **Output Structure**





------





### **1. 更新 Capability Registry**



```
/aios-capability-registry/modules/*.yaml
```

新增字段：

```
completion_status: complete / partial
source_verified: true / false
```



------





### **2. API Registry（扩展）**



```
/aios-api-registry/registry/*.yaml
```

要求：



- 覆盖所有核心模块 API

- 每个 API 有 layer tag

- 标记来源：

  

  - doc_only
  - code_only
  - doc+code

  





------





### **3. Module Reports（升级）**



```
/module_reports/*.md
```

必须新增：



- API 覆盖率（doc vs code）
- 未覆盖区域
- 关键调用链（call flow）
- 模块成熟度评分（1–5）





------





### **4. Module Completion Dashboard（新增）**



```
/module_completion.md
```

格式：

| **Module** | **API Count** | **Capability** | **Coverage** | **Completion** | **Ready for Decision** |
| ---------- | ------------- | -------------- | ------------ | -------------- | ---------------------- |
|            |               |                |              |                |                        |



------





### **5. Master Report（升级）**



```
/master_report.md
```

新增内容：



- 模块成熟度排序
- 哪些模块已“决策就绪”
- 哪些模块仍需补充
- DAP 当前覆盖 vs 全平台能力





------





## **Verification Method**





- 每个核心模块满足 Completion Criteria（6 条）

- Doc 与 Code API 对齐率 > 80%

- 每个 API 有 layer tag

- 至少 1 条完整路径验证：

  

  - UI → Network → Storage → Device

  

- Module Completion Dashboard 完整





------





## **Constraints**





1. 必须以“模块完成度”为目标，不是 API 数量
2. 不允许无限扫描低优先级 HAL 细节
3. 必须文档 + 源码双源验证
4. 不做最终架构裁剪
5. YAML schema 必须通过 TM35 校验工具链





------





## **Potential Risks**







### **Risk 1 — 继续变成“API 收集”**





→ 必须以模块为单位推进



------





### **Risk 2 — 模块划分失控**





→ 新增模块必须满足独立性条件



------





### **Risk 3 — 过度扫描 HAL**





→ 优先核心模块，限制低层细节



------





### **Risk 4 — 文档与代码不一致**





→ 必须标记来源（doc_only / code_only）



------





## **References**





- TM35（API Registry）
- TM36（Capability Census）
- Unisoc SDK headers / Mocor source
- PDF 文档集合
- Technical Memo Template 





------





## **Final Instruction（最重要）**





> TM36 让我们“看见了系统的轮廓”。

> TM37 必须让我们“理解系统的结构”。



> 只有当模块达到 completion，

> 我们才能真正回答：





- 哪些能力必须 Service 化
- 哪些必须留在 Adapter
- 哪些可以开放给 APP





> 如果 TM37 做不好，TM38 的架构决策一定是错的。



------



:::



