



# **Technical Memo 32-4 — Interface IDization & Light Obfuscation**





------



**Title:** External PAC Hardening Phase 3 — Interface IDization & Light Obfuscation

**Project:** AIOS Feature Phone Platform

**Subsystem:** DAP / Loader / Build / Security

**Author:** [Engineer name]

**Priority:** HIGH

**Date:** [YYYY-MM-DD]



------





## **Background**





TM32-3 已完成：



- strip（debug 信息去除）
- strings 收缩（部分语义降低）
- external build 可稳定运行





但当前仍存在关键风险：



- DAP 接口通过字符串暴露（FindInterface(“DAP_xxx”)）
- strings 扫描仍可恢复 API 面
- runtime 架构可被快速推断





因此需要进一步：



> **去除接口语义（string → ID），并通过轻混淆提升分析成本**



------





## **Objective**





在不破坏系统稳定性的前提下，实现：



1. DAP 接口从 string lookup → ID lookup（external only）
2. 消除 external PAC 中的明文接口语义
3. 引入轻量混淆（wrapper / dispatch / 常量层）
4. internal build 完全不受影响
5. BIN / BIN2 / BIN3 全链路可运行





------





## **Scope**







### **In Scope**





- FindInterface → ID 化（external build）
- 接口注册表 ID 化
- wrapper 层轻混淆
- dispatch table 简单混淆
- 常量与调用路径轻量去语义







### **Out of Scope**





- loader 重构
- ABI 大规模变更
- bin3 加密逻辑
- 重混淆（VM / CFG flattening）
- PAC 加密





------





## **Design Overview**





核心原则：



> **internal 保持可读，external 去语义**



------





### **架构对比**







#### **Internal Build**



```
FindInterface("DAP_DisplayPopup", CMD);
```



#### **External Build**



```
FindInterfaceById(IF_DISPLAY_POPUP, CMD);
```



------





### **双路径设计**



```
flowchart TD
    A[Wrapper Call] --> B{Build Type}
    B -->|Internal| C[FindInterface String]
    B -->|External| D[FindInterfaceById]
```



------





## **Implementation Plan**





------





### **Step 1 — 定义 Interface ID 表**





创建：

```
// dap_interface_id.h
typedef enum {
    IF_MEM_ALLOC = 0x01,
    IF_AUDIO_PLAY = 0x02,
    IF_DISPLAY_POPUP = 0x03,
    ...
} dap_if_id_t;
```

要求：



- ID 固定，不可随版本变化
- 不使用连续语义值（可间隔）
- 记录 mapping 文档（internal only）





------





### **Step 2 — 修改注册表（DAP_InstallOSAPI）**





当前：

```
register("DAP_DisplayPopup", func_ptr);
```

修改为：

```
#ifdef EXTERNAL_BUILD
register_id(IF_DISPLAY_POPUP, func_ptr);
#else
register("DAP_DisplayPopup", func_ptr);
#endif
```



------





### **Step 3 — 实现 FindInterfaceById**





新增：

```
void* FindInterfaceById(uint16_t id, uint32_t cmd)
```

实现：



- 基于 ID 查找 function pointer
- 与现有 dispatch 结构兼容
- 不改变原有 table 结构（最小侵入）





------





### **Step 4 — Wrapper 层切换**





在 SDK / wrapper：

```
#ifdef EXTERNAL_BUILD
    FindInterfaceById(IF_DISPLAY_POPUP, CMD);
#else
    FindInterface("DAP_DisplayPopup", CMD);
#endif
```

要求：



- 所有外部 API 统一走 wrapper
- 不允许业务代码直接调用 FindInterface





------





### **Step 5 — 轻混淆（Wrapper 层）**







#### **5.1 Wrapper rename（external only）**



```
// internal
DAP_DisplayPopup()

// external
api_03()
```



------





#### **5.2 调用路径拆分**



```
func = FindInterfaceById(...)
call(func)
```

可改为：

```
idx = id ^ 0x5A
func = table[idx]
```

（简单扰动，不影响性能）



------





#### **5.3 常量表分散**



避免：

```
static table[] = {func1, func2, func3}
```

改为：

```
part1[]
part2[]
merge at runtime
```



------





### **Step 6 — Strings 验证**





必须验证：

```
strings PAC | grep DAP_
```

结果：



- external 不应出现 DAP_* 接口名
- 不应出现 FindInterface(”…”)





------





### **Step 7 — Build Profile**





新增：

```
mm ..._ML_SECURE_OBF new
```

特性：



- 启用 EXTERNAL_BUILD
- 启用 ID lookup
- 启用 wrapper rename
- 输出到 zkw_output





------





## **Constraints**





- 不允许破坏 ABI（函数参数/调用方式不变）
- 不允许影响 loader
- 性能影响 < 5%
- 不增加内存 > 10KB
- 必须可回退（开关控制）





------





## **Expected Deliverables**





1. dap_interface_id.h
2. FindInterfaceById 实现
3. wrapper 改造 patch
4. external obfuscated PAC
5. strings 验证报告





------





## **Validation Plan**







### **Case 1 — Internal Build**





- 全部 API 正常
- Debug 正常





------





### **Case 2 — External Build**





- BIN 正常
- BIN2 正常
- BIN3 正常
- 无 crash





------





### **Case 3 — Strings 检查**





- 不出现 DAP_*
- 不出现 FindInterface(”…”)





------





### **Case 4 — 回归验证**





- 同机执行 OK
- 跨机拒绝 OK
- 篡改拒绝 OK





------





## **Pitfalls（必须阅读）**





1. **不要一次性替换所有接口（分批）**
2. **不要改 loader**
3. **不要破坏 wrapper ABI**
4. **不要在 external 版本去掉 trace（保留调试能力）**
5. **不要让 ID 表泄露语义（避免连续编号）**





------





## **Memory / Lessons Learned**





- string 是最大语义泄露点
- runtime 改动必须最小化
- 必须 internal / external 分离
- 小步推进比一次重构更安全





------





## **Next Step**





完成 TM32-4 后：



→ 可进入对外 demo 发布

→ 后续根据需要推进更深层 PAC / DAP 加固



------





## **Summary**





> 本阶段的目标是：

> 

> **让攻击者“看不到接口语义”，必须靠动态分析去猜。**

> 

> 方法：



- > string → ID

- > wrapper 去语义

- > 轻混淆



> 

> 不做：



- > 重混淆

- > 大规模 runtime 改造

  > :::





------





# **最后我帮你压一句战略级判断**





你现在这条路径是对的：





### **TM32-3**





👉 不动系统 → 提升阅读成本





### **TM32-4**





👉 切掉接口语义 → 提升理解成本



两步叠加之后：



> **别人不能“看一眼就抄”，而必须真正逆向你的系统。**



这就是你要的结果。

