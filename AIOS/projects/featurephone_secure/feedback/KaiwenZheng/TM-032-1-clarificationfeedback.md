

## # 0 **补充前置问题：是否需要研究** 

## **ums9117_240X320BAR_64MB_ML.mk**

## **，并考虑新增 secure build profile？**







### **决策**





**需要研究。**

建议工程师评估是否可以在现有目标基础上新增一个 external/secure build profile，例如：ums9117_240X320BAR_64MB_ML_SECURE

而不是继续把 external hardening 全部堆在 export 脚本里。





### **rationale**





TM32 需要明确区分：



- **internal build**
- **external secure build**





如果没有 build profile，external/internal 差异会继续散落在脚本、手工步骤和约定里，不利于长期维护。

新增 secure build profile 的价值在于：



- 明确 external 版本入口
- 固化 EXTERNAL_BUILD 等宏
- 为 strip / strings / export 流程提供稳定触发点





但需要注意：



- 新增 .mk 目标只是**安全构建流程入口**
- 不是安全本身
- 真正的 hardening 仍然来自 TM31/TM32 的导出、strip、去语义化等措施







### **工程师需要做什么**

1. 研究 ums9117_240X320BAR_64MB_ML.mk 与当前 mm ums9117_240X320BAR_64MB_ML new 的 build 流程

2. 评估新增 ..._ML_SECURE 或 ..._ML_EXT 目标的可行性

3. 明确该 profile 能控制哪些：

   

   - 编译宏
   - trace 开关
   - DAP 源文件选择
   - export / hardening 流程

   

4. 提交一份简短设计说明，不要求本轮立即完全落地，但要明确路径



# **Q1 选择：C**





### **决策**





TM32 当前阶段不改 FindInterface 机制，不引入 FindInterfaceById()，也不做 APP 侧 compile-time hash 的半兼容方案。

接口去语义化保留到后续 **TM32 Phase 2**（不要写成“永远不做”）。





### **rationale**





- 选项 A 是最终正确方向，但它属于 runtime ABI 级改造，会同时动 APP、SDK、固件注册表和 PAC 构建链，当前阶段风险过高。
- 选项 B 看似便宜，实际上会形成一个脏的过渡 ABI，长期维护成本高，而且安全收益不彻底。
- 因此 TM32 Phase 1 先专注于低风险 hardening：strip、strings 扫描、export pipeline 升级、external build profile。
- 等这部分稳定后，再单独推进 FindInterface → ID/hash 的去语义化。







### **工程师当前需要做什么**





1. 保持现有 FindInterface("name", CMD) 机制不变

2. 梳理所有敏感接口字符串清单，作为后续 Phase 2 输入

3. 在本轮中记录：

   

   - 哪些字符串最敏感
   - 哪些模块未来最适合优先改成 ID/hash

   

4. 不在本轮修改固件查找表、DAP_InstallOSAPI_unisoc.c、SDK ABI



# **Q2 选择：A**





### **决策**





当前阶段对 Entry.o 只执行：fromelf --strip=debug

不做手工符号 rename，也不放弃 strip。





### **rationale**





Entry.o 是当前 APP ABI 与 loader 的关键锚点文件。

手工 rename FindInterface / Register / DelAPI 等符号虽然表面上能进一步降低可读性，但属于高风险改动，可能破坏链接、入口定位或运行时契约；而完全不 strip 又会放弃当前阶段最容易获得的一部分 hardening 收益。

因此 TM32 Phase 1 只做 --strip=debug，先移除调试信息，同时保持 ABI 和运行行为完全不变。





### **工程师当前需要做什么**





1. 对 Entry.o 执行 fromelf --strip=debug

2. 比较 strip 前后：

   

   - 文件大小
   - strings 输出
   - 可见调试痕迹

   

3. 验证 strip 后：

   

   - BIN 执行正常
   - BIN2 执行正常
   - BIN3 执行正常

   

4. 不在本轮中对 Entry.o 做任何手工 rename 或 ABI 改写



# **Q3 选择：A（并建议把 B 作为增强项）**





### **决策**





TM32 Phase 1 当前必须执行的 strings 扫描范围，限定为**可控、可归因的中间产物**，至少包括：



- Entry.o
- APP .bin





如果工程上容易稳定落地，可将 external 关键 .o/.a 的扫描作为增强项一起纳入。





### **rationale**





当前阶段不扫描整个 PAC。PAC 是整机固件包，噪声过大，难以归因，不适合作为 TM32 Phase 1 的主要验收对象。

TM32 当前阶段的目标是去掉最容易“一眼看懂”的语义信息，因此应优先扫描能够明确归因到 DAP / APP / export pipeline 的中间产物。

这样既能获得明确的 hardening 反馈，又不会被整机固件中的无关字符串淹没。





### **工程师当前需要做什么**





1. 建立一份 strings 扫描规则

   重点关注：

   

   - DAP
   - LVGL
   - Audio
   - binding
   - loader
   - security
   - FindInterface
   - 明显接口名 / 文件路径

   

2. 对以下对象执行扫描：

   

   - Entry.o
   - demo APP .bin

   

3. 如果 external 关键 .o/.a 容易获取且结果可归因，则将其作为增强项补充扫描

4. 输出一份扫描报告，区分：

   

   - 必须修复的敏感命中
   - 暂时可接受但需记录的命中

   

5. 当前阶段不要求扫描整个 PAC



# **Q4 选择：A**





### **决策**





TM32 当前阶段引入一个独立的 external/secure build profile，通过 .mk / build target 显式接入 EXTERNAL_BUILD。

建议工程师评估新增如下目标的可行性：ums9117_240X320BAR_64MB_ML_SECURE

其中：



- 现有 mm ums9117_240X320BAR_64MB_ML new 继续作为 internal 工程版本
- 新的 mm ums9117_240X320BAR_64MB_ML_SECURE new 作为 external secure 版本







### **输出约定**





- internal 版本继续输出到原始工程目录下的 build/.../img / pac
- secure 版本输出到 zkw_output 对应目录下的 img / pac







### **核心要求**





1. internal 版本不得 strip，不得做函数名去语义化，不得影响调试和 Logel 定位

2. external secure 版本才允许：

   

   - strip
   - strings 扫描
   - 后续 TM32/Phase 2 的去语义化和轻混淆

   

3. internal / external 的差异必须由 build profile 显式控制，不能依赖 export 脚本对源码做文本替换

4. export 脚本仍然保留，但它的角色应退化为：

   

   - 目录整理

   - 补充拷贝

   - 导出 manifest

     而不是承担主要的 build mode 切换职责

   







### **rationale**





TM32 的本质要求是：

**external 版本加强硬化，而 internal 版本保持可开发、可调试。**

最稳妥的工程实现方式，是通过独立 build target 明确区分 internal 与 external，而不是通过手工流程或脚本替换来隐式区分。

这样可以保证：



- internal 调试体验不受影响
- external hardening 可重复、可审计、可扩展
- 为后续 TM33/TM34 建立稳定的 release 基础







### **工程师当前需要做什么**





1. 研究 ums9117_240X320BAR_64MB_ML.mk 及其被 mm ... new 调用的路径

2. 评估新增 ..._ML_SECURE target 的最小改动方案

3. 明确：

   

   - EXTERNAL_BUILD 宏如何接入
   - secure 输出路径如何切换到 zkw_output
   - strip / strings 扫描如何只挂在 secure profile 上

   

4. 给出一个最小设计方案，不要求本轮立即把所有 hardening 都做完，但必须把 build profile 边界先立起来



# Q5 **决策结论**







## **选择：**

## **A**





> **TM32 分两阶段做。**

> 当前阶段先做 build-profile 级与产物级 hardening；

> 运行时级去语义化和更强混淆留到下一阶段。









### **决策**





TM32 采用分期实施策略。





#### **TM32 Phase 1（当前）**



只完成：



1. secure build profile / EXTERNAL_BUILD 接入
2. secure 输出路径进入 zkw_output
3. Entry.o --strip=debug
4. strings 扫描规则建立并接入 export pipeline
5. external 产物净化的最小闭环验证







#### **TM32 Phase 2（后续）**



再推进：



1. FindInterface 去语义化（ID/hash）
2. 字符串 XOR / hash
3. wrapper / dispatch 层轻混淆
4. 更深的 external-only 语义隐藏







### **rationale**





当前阶段最重要的是在不破坏现有稳定基线的前提下，先拿到低风险、可验证的 hardening 收益。

如果同时引入 build profile、strip、strings、runtime ABI 改造和轻混淆，会把 TM32 变成一次性重构，问题难以归因，风险过高。

因此 TM32 Phase 1 只做“build 层 + 产物层”的 hardening，Phase 2 再做“runtime 层”的去语义化和混淆。





### **工程师当前需要做什么**





1. 设计并验证 secure build target

2. 接入 EXTERNAL_BUILD

3. 将 secure 输出导向 zkw_output

4. 对 Entry.o 做 --strip=debug 并验证 BIN/BIN2/BIN3 不受影响

5. 建立 strings 扫描规则与报告

6. 将 strings 扫描接入 export pipeline

7. 在反馈中清楚区分：

   

   - Phase 1 完成项
   - Phase 2 候选项

   

8. 不在本轮修改 runtime ABI / FindInterface 机制