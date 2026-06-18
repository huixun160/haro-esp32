

# **Technical Memo 38 — Runtime Memory & App Lifecycle 行为分析（现有平台策略反向梳理）**





**Project:** AIOS Feature Phone Platform



**Subsystem:** DAP / Runtime / System Behavior Analysis



**Author:** [Engineer Name]



**Priority:** HIGH



**Date:** 2026-03-23



------





## **Background**





当前平台已具备：



- DAP runtime（bin 重定位执行）
- LVGL UI（脱离 MMI）
- Network / Storage / 部分系统能力
- 多个 APP bin 可运行





但存在关键不确定性：



> **多个 APP 同时存在时，内存与生命周期行为不明确**



典型问题：



- 语音助手（Network + LVGL）运行中

- 启动电话 APP（Telephony + LVGL）

- 系统是否：

  

  - 保留语音助手后台？
  - 直接关闭语音助手？
  - 在内存不足时杀后台？

  





当前没有明确答案，也没有文档说明。



------





## **Objective**





本任务目标：





# **反向测量并定义当前平台的 Runtime Memory & Lifecycle 行为**





必须输出：



1. 多 APP 场景下的真实行为（前台/后台/被杀）
2. 内存冲突触发条件
3. DAP 是否参与内存/生命周期管理
4. Mocor 原生行为与 DAP 行为差异
5. 为 TM38 提供 Runtime Policy 输入





------





## **Scope**





本任务为 **行为分析 + 实验验证**，不修改代码逻辑。



------





### **场景 1 — 基础前后台切换**





步骤：



1. 启动 APP A（语音助手）

2. 记录：

   

   - 是否分配 heap
   - 当前内存占用

   

3. 启动 APP B（电话）





观察：



- APP A 是否：

  

  - 立即关闭
  - 进入后台（隐藏窗口）
  - 继续执行任务

  

- APP B 是否正常启动





------





### **场景 2 — 内存压力触发**





步骤：



1. 启动 APP A（语音助手）

2. 在 APP A 中：

   

   - 持续网络请求（HTTP）
   - 构造大 buffer（JSON / 音频 / UI对象）

   

3. 启动 APP B（电话）





观察：



- 是否触发：

  

  - 内存分配失败
  - APP A 被关闭
  - APP B 启动失败

  

- 系统是否打印：

  

  - mem conflict / OOM / error log

  





------





### **场景 3 — LVGL UI 占用验证**





步骤：



1. APP A 创建复杂 UI（多个 screen / image / list）
2. 切换到 APP B
3. 返回 APP A





观察：



- UI 是否保留
- 是否重新创建
- 内存是否释放





------





### **场景 4 — Network 任务后台行为**





步骤：



1. APP A 发起 HTTP 下载（长时间）
2. 切到 APP B
3. 等待 5~10 秒





观察：



- 网络是否继续
- callback 是否触发
- APP A 是否被杀





------





### **场景 5 — DAP 生命周期钩子验证**





检查：



- DAP 是否有：

  

  - onPause
  - onResume
  - onDestroy

  

- 是否被调用

- 是否由 DAP 控制还是 Mocor 控制





------





## **Data Collection**





必须记录：





### **1. 内存数据**





- 启动前/后 heap 使用
- 每个 APP 占用估算
- 内存失败日志







### **2. 状态数据**





- 前台/后台状态
- app 是否被 kill
- UI 状态







### **3. 日志**





- SCI / OS log
- DAP log
- 错误码





------





## **Output Structure**





------





### **1. 行为矩阵**



```
| 场景 | APP A 状态 | APP B 状态 | 内存变化 | 是否被杀 |
```



------





### **2. 生命周期模型**





输出当前真实模型：

```
RUNNING → BACKGROUND → (KEEP / KILL)
```

说明：



- 谁触发切换
- 谁触发 kill
- 是否可预测





------





### **3. 内存策略总结**





必须回答：



1. 是否存在 app 独立 heap
2. 是否有内存上限
3. 是否有 OOM 处理
4. 是否有 kill policy
5. 谁决定 kill（DAP / Mocor / OS）





------





### **4. DAP 角色分析**





明确：



- DAP 是否管理：

  

  - heap
  - app 生命周期
  - kill 行为

  

- 或仅作为 loader 存在





------





### **5. 差距分析（最关键）**





对比：



- 当前行为 vs 理想 AIOS Runtime Model





指出：



- 缺失：

  

  - memory domain
  - background policy
  - kill policy

  

- 风险：

  

  - app 随机 crash
  - 内存泄漏无法回收
  - 行为不可预测

  





------





## **Verification Criteria**





任务完成标准：



- 至少 5 个场景完整执行
- 每个场景有日志 + 结论
- 行为模型明确（不是猜测）
- DAP vs Mocor 责任边界明确
- 输出可直接用于 TM38





------





## **Constraints**





1. 不允许修改系统行为（只观察）
2. 必须在真实设备验证（模拟器仅辅助）
3. 不允许只写推测，必须有实验支撑





------





## **Expected Deliverables**





1. /runtime_analysis/memory_lifecycle_report.md
2. /runtime_analysis/test_logs/
3. 行为矩阵 + 生命周期图
4. DAP vs Mocor 分析结论





------





## **Final Instruction**





> 当前我们不是在设计系统，

> 而是在搞清楚系统“现在到底在做什么”。



> 如果不先测清楚当前行为，

> 后续 Runtime 设计（TM38）一定会错。



------



:::

