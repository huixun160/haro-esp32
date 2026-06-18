# Technical Memo**





**Title:** TM29-2 — Voice Assistant Asset Migration, Build, and Initial BIN Validation



**Project:** AIOS Feature Phone Platform



**Subsystem:** App Integration / DAP / Build / LVGL / Audio / Network



**Author:** AIOS Core Architecture



**Priority:** HIGH



**Date:** 2026-03-15



------





## **Background**





TM28-R 已恢复可信安全基线，TM28 payload encryption 已重新验证通过，当前主线可视为可信。 



TM29-1 已完成语音助手 APP 的资产识别、依赖映射、迁移白名单与风险清单，关键结论如下：



- 语音助手 APP 主体位于 Third-party/DAP/apps/voice_chat/，包含 Main.c 与 build.bat，并通过 ARM ADS 1.2 工具链生成初始 .bin。 

- 新增语音助手能力主要依赖：

  

  - Third-party/bigseek_core/ 整目录
  - dap_va_bridge.c/.h
  - dap_va_api.h
  - 若干 SDK 头文件与音频桥接扩展。

  

- dap.mk、dap_audio_bridge.c/.h、DAP_InstallOSAPI_unisoc.c 是高风险人工合并点，不能直接覆盖。

- contaminated snapshot 中的系统安全目录、loader、安全模块均不可信，禁止直接覆盖主线。 





因此，TM29-2 的任务不是“整合整个快照”，而是：



> **按白名单把语音助手 APP 所需资产迁入可信主线，在不破坏 TM28 安全基线的前提下，编译出语音助手初始 .bin 并在设备上验证。**



------





## **Objective**





本阶段必须完成以下目标：



1. 将语音助手 APP 的**最小必要资产**迁入当前可信主线
2. 手动合并 dap.mk、dap_audio_bridge.*、DAP_InstallOSAPI_unisoc.c 中与语音助手相关的必要变更
3. 保持当前 TM28 安全主线不被破坏
4. 成功编译并烧录固件
5. 使用 SDK / 批处理生成语音助手初始 .bin
6. 将初始 .bin 拷贝到功能机并验证 APP 可以运行





------





## **Scope**





本任务包括：



1. 按 TM29-1 白名单迁移语音助手相关资产
2. 手动合并必要的 DAP 平台与构建变更
3. 修复因迁移带来的编译错误
4. 构建语音助手初始 .bin
5. 设备侧运行验证
6. 补充必要的 Logel trace 以辅助调试





------





## **Out of Scope**





本任务明确 **不包括**：



1. .bin2 打包验证
2. .bin3（加密 payload）打包验证
3. 设备绑定 / bindfile / payload encryption 逻辑改造
4. DAP / Loader 抗逆向加固
5. 内部 SDK 边界冻结
6. 对外 SDK 裁剪
7. App Store 下载与分发
8. PAC / DAP 本体保护





TM29-2 只解决：



> **语音助手 APP 迁入主线并作为初始 .bin 正常运行。**



------





## **Current State**







### **已知 APP 资产**





根据 TM29-1 资产清单：



- Third-party/DAP/apps/voice_chat/

  

  - Main.c

  - build.bat

    用于 LVGL UI + PTT 逻辑和初始 .bin 构建。 

  

- Third-party/bigseek_core/

  

  - 14 个源码文件

  - 若干头文件

    为语音助手引擎核心。 

  

- Third-party/DAP/platform/unisoc/dap_va_bridge.c/.h

  

  - 语音助手 API 桥接层。

  

- Third-party/DAP/sdk/dap_va_api.h

  

  - 9 个 VA API 的 SDK 声明。

  







### **已知高风险点**





- make/dap/dap.mk

  contaminated snapshot 中新增了 BIGSEEK_CORE_SUPPORT 相关块，但不包含 TM28-R 安全文件，绝不能整文件覆盖。

- dap_audio_bridge.c/.h

  快照版比主线大很多，必须逐函数人工合并。

- DAP_InstallOSAPI_unisoc.c

  可能新增了 VA API 的 FindInterface 注册，必须 diff 后手工补齐。





------





## **Migration Source of Truth**





迁移源以 TM29-1 输出为准：



- 迁移白名单： 
- 风险清单： 
- 依赖映射： 
- 资产清单： 





任何不在白名单里的文件，默认**禁止迁入**。



------





## **Required Deliverables**





工程师必须提交以下内容：





### **Deliverable 1 — 迁移执行记录**





文件建议：

```
AIOS/feedback/TM-029-2-migration-log.md
```

必须记录：



- 迁移了哪些文件
- 哪些是直接复制
- 哪些是人工合并
- 哪些因冲突被放弃
- 每一步的原因





------





### **Deliverable 2 — 合并差异记录**





文件建议：

```
AIOS/feedback/TM-029-2-merge-notes.md
```

必须明确记录：



- dap.mk 增加了什么
- dap_audio_bridge.* 合并了哪些函数
- DAP_InstallOSAPI_unisoc.c 新增了哪些注册行





------





### **Deliverable 3 — 构建与烧录记录**





文件建议：

```
AIOS/feedback/TM-029-2-build-and-flash.md
```

必须包含：



- 编译命令
- 烧录命令
- 是否成功
- 编译告警/错误处理





------





### **Deliverable 4 — 初始** 

### **.bin**

###  **产物与验证记录**





文件建议：

```
AIOS/feedback/TM-029-2-initial-bin-validation.md
```

必须包含：



- 初始 .bin 生成方式
- .bin 文件名 / 版本
- 拷贝到设备的方法
- 设备验证结果
- Logel/界面结果截图





------





## **Verification Method**







### **Build Verification**





- 主线固件可完整编译
- dap.a 正常生成
- 没有因为迁移而破坏 TM28 安全模块构建







### **APP Build Verification**





- 语音助手可从 SDK / build.bat 生成初始 .bin







### **Device Verification**





- 初始 .bin 可拷贝到设备
- APP 能启动
- 至少有最小交互或界面可见
- Logel 能看到必要运行信息







### **Regression Safety Check**





- 迁移后不应破坏：

  

  - 现有 DAP loader 主线
  - 现有 Logel trace 路径
  - 现有安全模块编译入口

  





------





## **Potential Risks**







### **Risk 1 —** 

### **dap.mk**

###  **再次被错误覆盖**





这仍然是最高风险。快照中的 dap.mk 缺少 TM28-R 安全入口，直接覆盖会破坏当前安全构建。



**Mitigation:**

只能在当前可信主线 dap.mk 上**手动追加** BIGSEEK_CORE_SUPPORT 相关块。禁止覆盖。



------





### **Risk 2 —** 

### **dap_audio_bridge.c/.h**

###  **合并导致平台音频能力回退**





快照版变化巨大，说明里面不只是小修，而是新增了录音、播放、音量等功能。



**Mitigation:**

逐函数比对，只人工合并和语音助手直接相关的新功能。禁止整文件覆盖。



------





### **Risk 3 — VA API 已声明但未注册**





dap_va_api.h 和 dap_va_bridge.c 迁入后，如果 DAP_InstallOSAPI_unisoc.c 没同步注册，FindInterface 会失败。



**Mitigation:**

明确检查 9 个 VA 接口是否都被注册并可被检索。



------





### **Risk 4 — 语音助手依赖旧版网络栈/库版本**





bigseek_core 依赖 curl、libwebsockets、mbedtls、tcpip 等，主线和快照版本可能不一致。



**Mitigation:**

优先以主线已有版本为准；如果编译失败，再最小化调整 include/source path，不做整库覆盖。



------





### **Risk 5 — Logel trace 冲突或缺失**





bigseek_core 自带日志系统，可能和当前 DAP trace 链不一致。 



**Mitigation:**

优先保证最小可观测性；如果有必要，在桥接层统一接入 SCI_TRACE_LOW / DAP 已验证路径。



------





## **References**





- TM29-1 风险清单 
- TM29-1 迁移白名单 / 黑名单 
- TM29-1 依赖映射图 
- TM29-1 语音助手资产清单 
- TM28-R Feedback 
- pitfall.md
- memory.md





------





## **Execution Plan**







### **Step 0 — 开工前回顾历史坑（必须做）**





工程师开工前必须重新阅读：



- pitfall.md
- memory.md
- TM28-R feedback
- TM29-1 四份输出





必须明确记住以下历史坑：



1. dap.mk 不能整文件覆盖
2. SCI_TRACE_LOW / DAP trace 路径不能搞丢
3. full_buf / payload_ptr 内存所有权不能被应用迁移影响
4. contaminated snapshot 只可信 APP 相关资产，不可信系统安全目录





------





### **Step 1 — 先建立“迁移工作分支”**





基于当前可信主线，创建新的 TM29-2 集成分支或目录。



禁止在：



- contaminated snapshot
- 事故快照
- 临时测试目录





上直接开发。



------





### **Step 2 — 按白名单迁移“直接复制项”**





只允许首先复制以下明确白名单项： 



- Third-party/DAP/apps/voice_chat/
- Third-party/bigseek_core/
- Third-party/DAP/platform/unisoc/dap_va_bridge.c
- Third-party/DAP/platform/unisoc/dap_va_bridge.h
- Third-party/DAP/sdk/dap_va_api.h





复制后先不编译，先检查目录是否完整。



------





### **Step 3 — 手动合并** 

### **dap.mk**





根据 TM29-1 资产清单，快照里的 dap.mk 新增了：



- BIGSEEK_CORE_SUPPORT
- bigseek_core include/source
- dap_va_bridge.c
- cJSON.c
- 相关外部库 include path 





**必须做法：**



- 在当前主线 dap.mk 上**手动追加**
- 不得用快照版整文件覆盖
- 每加一组路径/源文件都要记录到 merge notes





------





### **Step 4 — 手动合并** 

### **DAP_InstallOSAPI_unisoc.c**





根据依赖映射，语音助手通过 FindInterface 查找 9 个 VA API。 



工程师必须：



- diff 主线与快照版
- 找出 VA API 注册行
- 只把这些注册行手动追加到当前主线





验收点：



- 9 个 VA 函数都能被 FindInterface 检索到





------





### **Step 5 — 手动合并** 

### **dap_audio_bridge.c/.h**





这是高风险区。快照版变化巨大，不能整文件覆盖。



工程师必须：



- 逐函数比对

- 识别与语音助手直接相关的新功能：

  

  - 录音
  - 播放
  - 音量
  - PCM 相关桥接

  

- 只把必要函数人工合入主线





这一步需要记录清楚：



- 合入了哪些函数
- 放弃了哪些函数
- 原因是什么





------





### **Step 6 — 处理 SDK 头文件差异**





根据白名单，这些文件不能盲拷，必须 diff：



- dap_audio_api.h
- lvgl_api.h
- Entry.c
- 其它 sdk/ 文件





目标不是“全同步”，而是：



- 只补足语音助手编译所需最小差异
- 避免污染当前 SDK 主线





------





### **Step 7 — 编译主线固件**





在完成上述合并后，先验证主线固件编译是否通过。



这里优先检查：



- bigseek_core 的 include path
- curl/libwebsockets/mbedtls 依赖
- bs_pdp_platform.c
- bs_network.c
- cJSON.c 是否正确纳入 build





如果编译失败，先修主线固件，不要急着去 build app .bin。



------





### **Step 8 — 生成语音助手初始** 

### **.bin**





根据资产清单，语音助手初始 .bin 生成链路是： 

```
voice_chat/Main.c
 + sdk/Entry.c + sdk/Start.s
 ↓ armcc (ARM ADS 1.2, ROPI/interwork)
 ↓ armlink
 ↓ fromelf -bin
 → voice_chat.bin
```

工程师必须：



- 跑通 build.bat 或等价构建步骤
- 生成语音助手初始 .bin
- 记录所有依赖与环境要求





------





### **Step 9 — 设备验证**





将 voice_chat.bin 拷贝到功能机，验证：



1. APP 能启动
2. UI 至少部分正常（LVGL 界面可见）
3. 必要时可看到按键/PTT 基础交互
4. Logel 中能看到最小可追踪日志





本阶段不要求：



- 网络闭环
- 完整语音链路
- .bin2/.bin3 验证





只要证明：



> 语音助手 APP 能以“初始 .bin”形态在可信主线上运行



就算完成。



------





## **Success Criteria**





TM29-2 完成的标准是：



1. 语音助手 APP 资产已按白名单迁入
2. 高风险文件只做了人工合并，没有被快照整文件覆盖
3. 主线固件编译成功
4. 初始 voice_chat.bin 成功生成
5. voice_chat.bin 在设备上可运行
6. 当前 TM28 安全主线未被破坏





------





## **Final Note**





TM29-2 的目标不是“把语音助手所有功能都调通”。

TM29-2 的目标是：

```
把语音助手 APP 安全地迁入可信主线，并证明它能以初始 .bin 形式运行
```

只有这一步稳了，TM29-3 才值得做：

```
voice_chat.bin
→ voice_chat.bin2
→ voice_chat.bin3
```