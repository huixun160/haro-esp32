# **Technical Memo**





**Title:** TM29-2.5 — Voice Assistant Stabilization and Migration Repair Before BIN2/BIN3 Validation



**Project:** AIOS Feature Phone Platform



**Subsystem:** App Integration / Voice Assistant / LVGL / Audio / Network / Build



**Author:** AIOS Core Architecture



**Priority:** CRITICAL



**Date:** 2026-03-15



------





## **Background**





TM29-2 已完成语音助手 APP 资产迁移，并成功实现：



- 白名单资产迁移
- PAC 固件编译成功
- voice_chat.bin 编译成功
- 设备端 APP 加载成功
- API 注册成功
- WebSocket 连通成功
- DSP 蓝屏问题已完成初步根因分析，怀疑与 PCM 格式不兼容有关，已提出切换到 BS_AUDIO_USE_AMR=1 的修复方向。 





但当前仍存在阻塞 TM29-3 的问题：



1. **字库 / CJK 显示异常**

   当前界面存在明显的中文显示异常，说明语音助手 UI 所依赖的字库配置或字体资源迁移不完整。

2. **长按语音键蓝屏死机**

   当前语音交互主路径仍然不稳定，反馈中虽已对 DSP 蓝屏给出初步修复方向，但尚未完成重编译验证。 

3. **迁移仍不完全可信**

   James 已明确建议参考他本地 git。

   这说明 contaminated snapshot 并不足以保证语音助手相关迁移完全正确，至少在：

   

   - 字库

   - 录音/编码

   - SSL/mbedTLS

     等路径上，当前主线可能缺少正确变更。

   





因此，在进入 TM29-3 前，必须插入一个稳定化阶段：



> **TM29-2.5：先把语音助手 APP 迁移修顺、跑稳定，再谈 bin2/bin3 封装验证。**



------





## **Objective**





本任务必须完成以下目标：



1. 解决或明确定位 **CJK 字库显示异常**
2. 解决或明确定位 **长按语音键蓝屏死机**
3. 以 James 本地 git 为参考源，重新审计语音助手迁移是否缺失关键文件或配置
4. 产出一个“可稳定运行的初始 .bin 语音助手版本”
5. 为 TM29-3 提供稳定基线





------





## **Scope**





本任务包括：



1. 审计 James 本地 git 中与语音助手相关的：

   

   - 字库
   - 录音/音频
   - 网络/SSL
   - 资源/配置
   - 批处理/构建

   

2. 与当前主线做差异比对

3. 只对语音助手稳定性相关问题进行最小修复

4. 验证：

   

   - UI 中文显示
   - 长按语音键
   - 最小语音链路稳定性

   





------





## **Out of Scope**





本任务明确 **不包括**：



1. .bin2 打包验证
2. .bin3 打包验证
3. payload encryption 调整
4. binding / bindfile 调整
5. DAP / Loader 安全逻辑改动
6. 内部 SDK 资产梳理（TM30）
7. 对外 SDK / 抗逆向 / 混淆
8. App Store 下载链路整合
9. PAC/DAP 本体保护





TM29-2.5 只解决：



> **语音助手 APP 作为初始 .bin 的迁移修复和稳定性调通。**



------





## **Current State**





根据 TM29-2 feedback，当前状态是：





### **已完成**





- 白名单迁移成功
- 编译成功
- APP 加载成功
- API 注册成功
- WebSocket 连通成功
- 安全基线未被破坏 







### **未完成 / 待验证**





- BS_AUDIO_USE_AMR=1 修复 DSP 蓝屏后尚未重编译验证
- CJK 字库配置需要参考 James git
- SSL 间歇失败仍待优化 





------





## **Required Inputs**





工程师开工前必须准备：



1. **James 本地 git 可读参考副本**

   

   - 只用于 diff / 审计
   - 禁止整目录覆盖当前主线

   

2. **当前 TM29-2 主线工作目录**

   

   - 作为可信主线

   

3. **设备与现象记录**

   

   - 乱码界面照片
   - 蓝屏触发步骤
   - Logel trace
   - 编译参数 / 宏开关

   





------





## **Expected Deliverables**







### **Deliverable 1 — 差异审计文档**





文件建议：

```
AIOS/feedback/TM-029-2.5-james-git-diff.md
```

内容至少包括：



- James git 与当前主线在语音助手相关目录的差异
- 哪些差异与字库有关
- 哪些差异与录音/蓝屏有关
- 哪些差异与 SSL/网络有关





------





### **Deliverable 2 — 稳定性修复记录**





文件建议：

```
AIOS/feedback/TM-029-2.5-fix-log.md
```

内容至少包括：



- 修了哪些点
- 改了哪些文件
- 为什么改
- 是直接复制、手工合并，还是仅修改配置





------





### **Deliverable 3 — 设备验证报告**





文件建议：

```
AIOS/feedback/TM-029-2.5-device-validation.md
```

内容至少包括：



- 中文显示是否恢复
- 长按语音键是否仍蓝屏
- 最小语音交互是否稳定
- SSL 是否仍偶发失败





------





## **Verification Method**







### **UI Verification**





- 中文 / CJK 显示正常
- 不再出现大面积方框 / 错字 / 缺字







### **Audio Verification**





- 长按语音键不再蓝屏
- 录音路径可进入
- 至少完成一次最小语音采集流程







### **Build Verification**





- 主线仍可编译
- voice_chat.bin 仍可生成
- 没有破坏 TM29-2 已经跑通的 API 注册 / WebSocket 基础链路







### **Safety Verification**





- TM28-R / TM29-2 的安全主线未被覆盖
- dap.mk 未被 James 旧版整文件替换
- Logel trace 仍可追踪





------





## **Potential Risks**







### **Risk 1 — 再次发生“目录级覆盖”**





James 本地 git 只能作为参考源，不能直接覆盖当前主线。

否则你们会第二次重演 repo 污染事故。



**Mitigation:**

所有修改必须：



- 先 diff
- 再文件级挑选
- 高风险文件人工合并





------





### **Risk 2 — 字库问题根源不在 APP，而在系统配置**





CJK 显示异常可能不是 voice_chat 自身问题，而是：



- 字库资源没迁入
- 字体映射配置缺失
- MMI / resource 配置未同步





**Mitigation:**

不要只查 voice_chat/。必须同时检查：



- 资源目录
- font / language / resource 配置
- James git 中与 CJK 显示有关的构建差异





------





### **Risk 3 — 蓝屏问题不只在 PCM/AMR**





TM29-2 反馈中对 DSP 蓝屏的修复方向是 BS_AUDIO_USE_AMR=1，但这只是根因假设，不是最终证明。 



**Mitigation:**

必须重编译 + 真机验证，不允许把“分析结论”当成“已修复”。



------





### **Risk 4 — 误伤当前安全主线**





为了修语音助手稳定性，如果去动：



- Third-party/DAP/security/

- bin2_loader.*

- device_binding.*

- bin2_pack.py

  就会把 TM28 / TM27 主线再拖进不确定状态。





**Mitigation:**

本阶段严格禁止触碰这些安全文件。



------





### **Risk 5 — Logel trace 缺失导致无法 debug**





当前问题高度依赖 trace，尤其是：



- 语音键长按触发路径
- DSP / audio mode
- font / resource load path
- SSL 握手失败点





**Mitigation:**

所有新加日志必须继续走已验证可见的 SCI_TRACE_LOW / DAP trace 链路。



------





## **References**





- TM29-2 Feedback — 语音助手迁移成功但仍有稳定性问题 
- pitfall.md
- memory.md
- TM29-1 输出
- James 本地 git（仅作参考源）





------





## **Execution Plan**







### **Step 0 — 开工前复习历史坑（必须做）**





工程师开工前必须重新阅读：



- pitfall.md
- memory.md
- TM29-2 feedback
- TM29-1 风险清单





特别注意：



1. dap.mk 不能整文件覆盖
2. trace 链不能丢
3. contaminated snapshot / James git 只能做参考，不是主线覆盖源
4. 不要把语音 APP 稳定性问题扩展成系统大重构





------





### **Step 1 — 获取 James 本地 git 并做差异审计**





只聚焦和语音助手相关的路径，优先检查：



- voice_chat/
- bigseek_core/
- dap_va_bridge.*
- dap_audio_bridge.*
- 字体 / 资源 / 语言配置
- 录音 / AMR / PCM 相关配置
- SSL / mbedTLS 相关配置
- build.bat / 构建脚本





输出一份差异审计，不允许一边 diff 一边直接改主线。



------





### **Step 2 — 优先解决字库 / CJK 显示问题**





工程师必须明确回答：



1. 当前乱码/方框问题，是缺少：

   

   - 字库资源？
   - 语言表？
   - 字体映射？
   - 编译宏？
   - 资源打包步骤？

   

2. James git 中有没有对应配置或资源文件？

3. 当前主线缺的是资源，还是配置，还是构建步骤？





修复顺序建议：



- 先恢复最小 CJK 显示
- 再优化字体效果





本阶段目标是“能正确显示”，不是“字体最好看”。



------





### **Step 3 — 重新验证蓝屏问题（AMR 修复方向）**





按照 TM29-2 的分析，优先验证：

```
BS_AUDIO_USE_AMR=1
```

是否真的解决了长按语音键蓝屏问题。 



必须完成：



1. 修改并记录配置
2. 重新编译
3. 真机长按语音键反复测试
4. 抓取 Logel





如果仍然蓝屏，必须继续定位：



- 是音频格式问题
- 还是线程/消息问题
- 还是 buffer / DSP 调用问题





------





### **Step 4 — 最小 SSL/网络稳定性检查**





本阶段不要求彻底修完 SSL，但必须至少判断：



- SSL 间歇失败是否会阻塞 TM29-3
- 是配置问题还是偶发问题
- James git 中是否有与 mbedTLS 相关的关键差异





如果 SSL 偶发失败不影响本地录音/UI稳定性，可以标记为“TM29-3 或后续继续处理”。



------





### **Step 5 — 保持主线最小改动**





只允许对以下类别做修复：



- 语音助手 APP 相关代码
- 资源/字体/语言配置
- 音频桥接的必要最小变更
- 构建脚本 / 配置的必要最小变更





禁止：



- 重新迁移整个系统
- 重做 DAP
- 修改安全 loader
- 修改 BIN2/BIN3 协议





------





## **Success Criteria**





TM29-2.5 完成的标准：



1. 中文 / CJK 显示恢复到可用状态
2. 长按语音键不再蓝屏
3. voice_chat.bin 仍可生成并运行
4. 主线安全基线不被破坏
5. 可以进入 TM29-3（bin2/bin3 语音助手验证）





------





## **Final Note**





TM29-2.5 的本质不是“继续开发新功能”。

而是：

```
把语音助手 APP 从“能启动”修到“能稳定跑”
```

只有这一步完成，TM29-3 才有意义。

否则你只是在把一个不稳定的初始 .bin 再封装成 .bin2/.bin3，问题只会更难 debug。