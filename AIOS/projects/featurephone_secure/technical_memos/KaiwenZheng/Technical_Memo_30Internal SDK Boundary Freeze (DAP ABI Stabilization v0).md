# **Technical Memo**





**Title:** TM30 — Internal SDK Boundary Freeze (DAP ABI Stabilization v0)



**Project:** AIOS Feature Phone Platform



**Subsystem:** DAP / SDK / Loader / Build



**Author:** AIOS Core Architecture



**Priority:** CRITICAL



**Date:** 2026-03-16



------





## **Background**





TM29-3 已恢复干净基线：



- BIN2 / BIN3 可执行
- binding / secret 链路正常
- DAP 重定位机制稳定
- 无语音助手污染





当前系统具备：

```
“可以跑”
但不具备
“不会被改坏”
```

问题是：



- SDK 接口没有边界
- APP 可以随意调用内部函数
- 不同工程师可能改接口签名
- bridge / loader / api 没有固定契约





这会导致：

```
每接一个 APP = 一次系统破坏风险
```



------





## **Objective**





本阶段目标：



> **冻结一套“最小可运行 ABI”，确保：**



- > hello world 永远可运行

- > BIN2 / BIN3 永远可运行

- > DAP 重定位不被破坏

- > 后续 APP 只能在这个边界内扩展





------





## **Scope**





本任务包括：



1. 定义最小 DAP API 集合
2. 固定函数签名（ABI）
3. 固定重定位契约
4. 固定 Loader → APP 调用协议
5. 固定 SDK 头文件边界
6. 禁止 APP 访问内部模块





------





## **Out of Scope**





本任务不包括：



- 混淆（TM32）
- 对外裁剪（TM31）
- 文档整理（TM33）
- release gate（TM34）
- 新功能开发（LVGL9扩展等）





------





## **核心原则（必须执行）**







### **原则 1：ABI 一旦定义，不允许随意修改**





不是“尽量不改”，是：

```
禁止修改
```

如果要改：

```
必须新增版本（v2），不能覆盖 v1
```



------





### **原则 2：APP 只能看到 SDK，看不到 DAP 内部**



```
APP → SDK API → DAP
```

禁止：

```
APP → 直接 include DAP 内部头文件
```



------





### **原则 3：最小接口原则**





不要设计未来接口。



只保留：

```
hello world + bin2/bin3 跑起来必须的接口
```



------





## **SDK 分层设计（本阶段最重要产出）**





必须形成以下结构：

```
Third-party/DAP/
├── sdk/              ← 唯一对 APP 可见
│   ├── dap_api.h
│   ├── dap_memory.h
│   ├── dap_log.h
│   ├── dap_event.h
│
├── core/             ← 禁止 APP 访问
├── loader/           ← 禁止 APP 访问
├── security/         ← 禁止 APP 访问
├── platform/         ← 禁止 APP 访问
```



------





## **最小 API 集合（v0）**





只允许这些类型存在：





### **1. 生命周期**



```
void dap_app_init(void);
void dap_app_loop(void);
void dap_app_exit(void);
```



------





### **2. 内存**



```
void* dap_malloc(size_t size);
void  dap_free(void* ptr);
```



------





### **3. 日志**



```
void dap_log(const char* fmt, ...);
```



------





### **4. 事件 / 输入**



```
typedef struct {
    int key;
    int event;
} dap_key_event_t;

void dap_register_key_callback(void (*cb)(dap_key_event_t* e));
```



------





### **5. 定时器（最简单版）**



```
void dap_set_timer(int ms, void (*cb)(void));
```



------





## **明确禁止（必须写进规范）**





APP 禁止调用：



- DAP_InstallOSAPI_*
- dap_loader_*
- device_binding_*
- bin2_loader_*
- security/*
- platform/unisoc/*





------





## **重定位契约冻结（关键）**





你们核心护城河之一在这里。



必须冻结：





### **1. entry point**



```
APP entry symbol 名字固定
```



### **2. relocation table 格式**



```
section 名
偏移格式
symbol 解析方式
```



### **3. loader 行为**



```
加载顺序
内存分配方式
跳转方式
```

这三件事：

```
不能改
```

否则：

```
所有历史 bin 全部失效
```



------





## **构建约束**





必须做到：





### **1. SDK 单一入口**





APP 只能 include：

```
#include "dap_api.h"
```



------





### **2. 编译隔离**





在编译阶段：

```
禁止 APP include 非 sdk 目录
```

可以通过：

```
include path 控制
```

实现。



------





### **3. 强制接口检查**





可以加一个简单检查：

```
grep APP 代码
如果出现 dap_internal / loader / security
直接 build fail
```



------





## **Expected Deliverables**







### **Deliverable 1 — SDK 头文件**



```
Third-party/DAP/sdk/*.h
```

必须是：



- 最小集合
- 不暴露内部结构





------





### **Deliverable 2 — ABI Freeze 文档**



```
AIOS/docs/sdk/dap_abi_v0.md
```

包括：



- API 列表
- 参数说明
- 不允许修改规则





------





### **Deliverable 3 — 构建约束**



```
make/dap/app_build_rules.mk
```

实现：



- include 限制
- 非法引用检测





------





### **Deliverable 4 — hello world 验证**





必须验证：

```
hello world
→ 编译
→ bin
→ bin2
→ bin3
→ 设备执行
```



------





## **Verification Criteria**





必须全部通过：



- APP 只能 include sdk/
- 修改内部 DAP 不影响 hello world
- BIN2/BIN3 正常
- relocation 不受影响
- APP 无法调用内部接口





------





## **Potential Risks**







### **Risk 1 — 工程师偷用内部 API**





这是最常见问题。



解决：

```
编译阶段禁止
```



------





### **Risk 2 — 未来 LVGL9 接入打破 ABI**





这是必然发生的。



解决方法不是：

```
改 v0
```

而是：

```
新增 v1
```



------





### **Risk 3 — SDK 设计过度**





很多人会想：

```
“顺便把未来 API 设计好”
```

这是错的。



现在只做：

```
能跑的最小集合
```



------





## **Final Note（最重要）**





你现在在做的不是“SDK”。



你在做的是：



> **AIOS 的“操作系统边界”**



这条边界一旦清晰：



- 你可以放心让别人开发 APP
- 你可以放心做混淆（TM32）
- 你可以放心对外交付（TM31）





如果这条边界不清晰：

```
每一个新工程师 = 一次系统风险
每一个新 APP = 一次架构崩溃
```



------





## **一句话总结**





> **TM30 = 把“现在能跑的系统”，变成“以后不会被随便改坏的系统”。**



