



# **Technical Memo**





**Title:** TM32 — External Binary Hardening (De-Semanticization + Strip + Controlled Obfuscation)



**Project:** AIOS Feature Phone Platform



**Subsystem:** Security / DAP / Build / Export Pipeline



**Author:** AIOS Core Architecture



**Priority:** CRITICAL



**Date:** 2026-03-20



------





## **Background**





TM31 已完成：



- internal / external 分离（zkw_output）
- DAP 核心源码不进入交付目录
- PAC / IMG / BIN 通过 internal 构建
- export 脚本已建立





当前风险仍然存在：

```
external 产物（.pac / .bin / .o）仍然具备强语义信息
```

表现为：



- FindInterface("xxx") 明文存在
- 二进制中存在 DAP / LVGL / Audio 等字符串
- symbol / debug 信息未完全清理
- 接口调用路径可被快速定位





👉 结论：



> **TM31 防“源码泄露”，但不防“逆向理解”。**



------





## **Objective**





构建一套 **external-only 硬化体系**，使得：



1. 即使获取 .pac / .bin，也难以理解 DAP 架构
2. 无法通过字符串快速定位接口语义
3. 无法轻易构造恶意 bin
4. 不影响现有功能机运行（性能损耗 < ~50ms）
5. **internal 开发体验不受影响**





------





## **核心原则（必须遵守）**





------





### **原则 1：internal ≠ external**



```
internal = 可读 / 可调试 / 可定位问题
external = 不可读 / 去语义 / 黑盒
```

❌ 不允许在 internal 引入破坏可读性的混淆

❌ 不允许用 external 版本调试问题



------





### **原则 2：混淆是“最后一步”，不是开发基础**



```
开发 → 编译 → 验证 → export → strip → 混淆
```



------





### **原则 3：优先去语义，不是乱控制流**



```
先干掉“能看懂”
再考虑“难分析”
```



------





## **Scope**





本任务包括：



1. 接口调用去语义化（FindInterface 替换）
2. 字符串去语义化 / 加密
3. strip 策略正式化
4. external-only 混淆层
5. export pipeline 升级





------





## **Out of Scope**





- VM-based obfuscation
- 重度控制流混淆
- JIT / runtime 虚拟机
- 性能敏感路径大规模改写





------





# **核心设计**





------





## **1️⃣ 接口去语义化（最高优先级）**







### **当前问题**



```
FindInterface("DAP_AudioStart", CMD)
```

👉 任何逆向工程师第一步就是搜字符串。



------





### **目标**



```
FindInterfaceById(0x0213)
```



------





### **实现方式（推荐）**







#### **Step 1：建立接口映射表（internal）**



```
#define IF_AUDIO_START 0x0213
#define IF_LVGL_BTN_CREATE 0x0451
```



------





#### **Step 2：external build 替换**



```
#ifdef EXTERNAL_BUILD
FindInterfaceById(IF_AUDIO_START);
#else
FindInterface("DAP_AudioStart", CMD);
#endif
```



------





#### **Step 3：删除 external 中字符串表**



external 不应包含：

```
"DAP_AudioStart"
"DAP_LVGL_CreateBtn"
```



------





## **2️⃣ 字符串去语义化**





------





### **目标**





在 .bin / .pac 中：

```
❌ "AudioStart"
❌ "CreateBtn"
❌ "DisplayPopup"
```



------





### **方法（两级）**







#### **Level 1（必须）**





- 所有接口名 → ID / hash
- 删除 debug printf 字符串







#### **Level 2（可选）**





- 字符串简单加密（xor / table）
- runtime 解密（仅 external）





------





## **3️⃣ strip 策略（正式化）**





------





### **当前问题**





你已经察觉：



> strip 只是“做了一点”，没有形成体系



------





### **TM32 要做的**





定义三层 strip：



------





### **Layer A：编译阶段**



```
-fvisibility=hidden
```

限制符号导出



------





### **Layer B：对象文件**



```
strip --strip-all libdap.a
```

删除：



- symbol
- debug
- relocation hints（非必要）





------





### **Layer C：最终产物扫描（必须）**





执行：

```
strings xxx.bin | grep -E "DAP|LVGL|Audio"
```

如果命中：

```
→ build fail
```

👉 这是关键：**strip 必须有“验收标准”**



------





## **4️⃣ external-only 混淆（轻量）**





------





### **可以做**





- wrapper 函数 rename
- call dispatch table
- 常量表分散
- inline + macro 替换





------





### **不做（现在阶段）**





- CFG flattening
- VM obfuscation
- 大规模 basic block 重排





------





## **5️⃣ Export Pipeline 升级**





------





### **当前（TM31）**



```
internal build → export → zkw_output
```



------





### **TM32 后**



```
internal build
→ external build flag
→ strip
→ de-semanticize
→ export
→ zkw_output
```



------





### **新增步骤**





在 export_zkw_output.py 中加入：

```
1. 校验无敏感字符串
2. 校验无 core 符号
3. 校验接口名已替换
4. 校验 strip 已执行
```



------





## **验证标准（必须全部通过）**





------





### **安全验证**





- 无 FindInterface("xxx")
- 无 DAP/LVGL/Audio 字符串
- symbol 不可读
- strings 扫描通过





------





### **功能验证**





- hello demo 正常运行
- bin / bin2 / bin3 正常
- PAC 正常烧录





------





### **工程验证**





- internal build 不受影响
- external build 可重复生成
- debug 仅在 internal 可用





------





## **风险**





------





### **Risk 1：误伤 internal**





后果：

```
工程师无法 debug
```

解决：

```
所有混淆必须 gated by EXTERNAL_BUILD
```



------





### **Risk 2：字符串去掉导致功能异常**





解决：

```
逐模块验证（audio / lvgl / loader）
```



------





### **Risk 3：strip 过度导致崩溃**





解决：

```
分阶段 strip（.o → .a → pac）
```



------





## **Deliverables**





1. FindInterface → ID 替换方案
2. external-only 宏体系（EXTERNAL_BUILD）
3. strip 脚本 + 校验脚本
4. 升级版 export_zkw_output.py
5. hardened demo pac





------





# **Final Note**





> **TM31 是“不把源码给别人”，**

> **TM32 是“就算给了也看不懂”。**



------





# **一句话总结**





> **TM32 = 去语义（核心） + strip（基础） + 轻混淆（辅助）**



------



