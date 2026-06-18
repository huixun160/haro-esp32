

# **Technical Memo**





**Title:** TM29-3 — Rollback to TM28-R Clean Baseline and Removal of Contaminated Voice Assistant Integration



**Project:** AIOS Feature Phone Platform



**Subsystem:** System Integration / Security / DAP / Build



**Author:** AIOS Core Architecture



**Priority:** CRITICAL



**Date:** 2026-03-16



------





## **Background**





TM29-2 与 TM29-2.5 的执行过程中，系统出现以下不可控问题：



- 语音助手代码存在大量不稳定行为，且 bug **不可稳定复现**
- DSP 层出现 assert（dspintisr.c:587），属于平台级冲突，无法通过应用层修复 
- dap_audio_bridge.c（约 60KB）与当前 TM28-R SDK 存在结构/调用不兼容 
- UI 状态机、网络、录音链路均未形成稳定闭环 





本质问题：



> 当前主线已被 contaminated snapshot + 不完整迁移污染，系统行为不可预测。



这类系统有一个特点：

```
你无法证明它是“对的”
只能不断发现它是“错的”
```

这种状态不能进入：



- TM29-3（bin2/bin3）
- TM30（SDK整理）
- 更不用说量产





------





## **Objective**





本阶段目标非常简单且唯一：



> **恢复一个完全干净、可验证、无污染的 TM28-R 安全基线。**



并满足以下验收条件：



1. 不包含任何语音助手相关代码（来自 James / Ouyang）
2. 不包含 contaminated snapshot 引入的系统级变更
3. BIN2 / BIN3 加密链路完全可用
4. 可通过以下验证：



```
获取 binding_id
→ 生成 bin2
→ 下发 4 个 bin2 到设备
→ 成功执行

从 Logel 获取 secret
→ 构造 bin2
→ 成功执行
```



------





## **Scope**





本任务包括：



1. 基于 git 历史回退到 TM28-R
2. 删除所有语音助手相关代码（主线）
3. 清理 contaminated snapshot 引入的系统污染
4. 保留 legacy（仅存档，不参与构建）
5. 验证 BIN2 / BIN3 加密链路





------





## **Out of Scope**





本任务明确不包括：



1. 修复语音助手 bug
2. 继续语音助手开发
3. DSP / audio 问题分析
4. LVGL / UI 优化
5. 网络 / SSL 修复
6. SDK 整理（TM30）
7. App Store 集成
8. 抗逆向增强（TM31+）





一句话：



> **这一步是“清场”，不是“开发”。**



------





## **Rollback Strategy**







### **原则（必须严格执行）**





1. **只信任 TM28-R**
2. **不信任当前主线**
3. **不信任 contaminated snapshot**
4. **不做“修复式回退”，只做“确定性回退”**





------





## **Execution Plan**







### **Step 1 — 定位 TM28-R 基线**





工程师必须通过 git：

```
git log --oneline
```

找到：

```
TM28-R 完成时的 commit
```

并确认：



- BIN2 / BIN3 已验证通过
- DAP loader 正常
- device binding 正常





------





### **Step 2 — 创建 clean recovery 分支**



```
git checkout -b tm29-3-clean-baseline <TM28-R commit>
```

禁止在当前污染主线操作。



------





### **Step 3 — 删除语音助手相关代码**





删除（或从 build 中剔除）：

```
Third-party/DAP/apps/voice_chat/
Third-party/bigseek_core/
dap_va_bridge.*
dap_va_api.h
```

以及所有：

```
BIGSEEK_CORE_SUPPORT
voice assistant 宏
相关 include path
```



------





### **Step 4 — 清理 dap.mk**





重点检查：

```
make/dap/dap.mk
```

必须确保：



- 不包含 bigseek_core
- 不包含 dap_va_bridge.c
- 不包含任何 VA 相关 source





只保留 TM28-R 原始版本。



------





### **Step 5 — 清理 DAP platform 层**





重点检查：

```
DAP_InstallOSAPI_unisoc.c
dap_audio_bridge.c/.h
dap_lvgl_bridge.c
```

要求：



- 删除所有 VA API 注册
- 删除所有语音助手扩展接口
- 恢复 TM28-R 原始实现





------





### **Step 6 — 保留 legacy（但隔离）**





将 Ouyang / James 代码移动到：

```
AIOS/legacy/oywork/
```

要求：



- 不参与编译
- 不在 include path
- 不在 dap.mk 中出现





目的：

```
可参考，但绝不影响系统
```



------





### **Step 7 — 全量重新编译**





必须验证：



- 无编译错误
- 无新增 warning（关键路径）
- dap.a 正常生成





------





### **Step 8 — PAC 烧录验证**





烧录设备，验证：

```
系统正常启动
DAP 正常加载
```



------





### **Step 9 — BIN2 / BIN3 回归验证（核心）**





必须执行完整链路：





## **Case 1 — binding_id 流程**



```
设备获取 binding_id
→ 构造 4 个 bin2
→ 下发到设备
→ 成功执行
```



## **Case 2 — secret 流程**



```
Logel 获取 secret
→ 构造 bin2
→ 下发
→ 成功执行
```



------





## **Expected Deliverables**







### **Deliverable 1 — 回退记录**



```
AIOS/feedback/TM-029-3-rollback-log.md
```

包括：



- 回退 commit
- 删除内容列表
- 修改文件列表





------





### **Deliverable 2 — 清理确认清单**



```
AIOS/feedback/TM-029-3-clean-checklist.md
```

必须确认：



- 无 voice_chat
- 无 bigseek_core
- 无 VA API
- 无 contaminated snapshot 残留





------





### **Deliverable 3 — 验证报告**



```
AIOS/feedback/TM-029-3-verification.md
```

包括：



- binding_id 测试
- bin2 执行结果
- secret 测试
- Logel 输出





------





## **Verification Criteria (必须全部通过)**





- 无语音助手代码参与构建
- TM28-R 安全逻辑完整
- BIN2 正常执行
- BIN3 正常执行
- binding_id 流程成功
- secret 流程成功





------





## **Potential Risks**







### **Risk 1 — “看起来回退了，但其实没干净”**





典型表现：



- dap.mk 还残留 VA include
- 某个 .c 文件还在编译链里





解决方法：

```
grep -R "bigseek"
grep -R "voice"
grep -R "dap_va"
```



------





### **Risk 2 — 工程师做“部分回退”**





这是最危险的行为。

```
删一半
留一半
```

结果是：

```
系统进入第三种状态（既不是旧的，也不是新的）
```

必须禁止。



------





### **Risk 3 — legacy 代码误参与构建**





必须确保：

```
AIOS/legacy/oywork/
```

完全隔离。



------





## **Final Note**





我直接说你现在这个阶段最关键的一句话：



> **你不是在“开发 AIOS”，你是在“恢复 AIOS 的确定性”。**



没有确定性：



- 加密没有意义
- bin2/bin3 没意义
- App Store 没意义
- 商业模式更没意义





------



等 TM29-3 做完，你才真正回到：

```
可控系统
```

然后下一步才是：

```
TM30 → 接口冻结
TM31 → 安全加固
TM29（重做）→ 语音助手（这次用正确方式）
```