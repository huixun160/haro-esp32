

# **Technical Memo**





**Title:** TM31 — External Deliverable Packaging (zkw_output Blackbox Generation)



**Project:** AIOS Feature Phone Platform



**Subsystem:** Build / DAP / Security / Packaging



**Author:** AIOS Core Architecture



**Priority:** CRITICAL



**Date:** 2026-03-19



------





## **Background**





TM30 已完成：



- SDK ABI 冻结（dap_api.h）
- APP 调用边界收敛
- hello_bigseek 验证 BIN / BIN2 / BIN3
- APP 不再直接访问 core/





当前问题：

```
internal/ = 开发系统
但也是交付系统
```

导致：

```
PAC / BIN → 可被逆向
源码结构 → 可被直接理解
DAP 架构 → 可被复制
```



------





## **Objective**





本阶段目标：



> **构建一套“对外交付产物体系”（zkw_output），在不影响内部开发的前提下，实现 DAP 黑盒化交付。**



必须满足：



1. 不影响现有 internal 开发流程

2. zkw_output 仅包含对外交付所需最小内容

3. DAP 核心实现不以源码形式暴露

4. 支持未来自动化（AI skills）生成外部版本

5. 最终可产出：

   

   - pac
   - img
   - demo bin

   





------





## **核心原则（必须遵守）**







### **原则 1：zkw_output 是“产物”，不是“开发目录”**



```
❌ 不允许人工长期维护 zkw_output
✅ 必须由 internal 自动生成
```



------





### **原则 2：不复制系统，只导出必要部分**



```
zkw_output ≠ internal 副本
zkw_output = 裁剪 + 替换 + 产物
```



------





### **原则 3：DAP 核心必须黑盒化**



```
❌ 不允许 core/ loader/ security/ 源码出现在 zkw_output
✅ 必须替换为预编译库（.a / .o）
```



------





### **原则 4：允许依赖 internal 编译**



```
✅ zkw_output 不要求独立编译
```

（当前阶段不做完全隔离）



------





## **Scope**





本任务包括：



1. 设计 zkw_output 目录结构
2. 定义导出白名单（what to export）
3. 构建 DAP 预编译库
4. 实现 strip 策略
5. 构建导出脚本（pipeline）
6. 生成 pac/img/demo
7. 安全边界检查





------





## **Out of Scope**





本任务不包括：



- 混淆（TM32）
- FindInterface 重写
- bin 加密升级
- loader 重构
- SDK v1（LVGL/Audio）





------





## **关键任务 0（必须先做）**







### **🔴 资产梳理（Critical）**





在任何导出前，工程师必须完成：

```
列出所有可能泄露 DAP 核心能力的文件
```

输出：

```
AIOS/docs/security/export_inventory.md
```

分类：





### **Class A（必须禁止导出）**





- core/
- loader/
- security/
- platform/
- DAP 内部私有 .h
- bin2/bin3 crypto 实现
- device binding 实现





------





### **Class B（可导出）**





- sdk/
- apps/demo/
- build scripts（裁剪后）
- 必要第三方库





------





### **Class C（需评估）**





- glue code
- adapter
- 部分平台接口





------



👉 **没有这个清单，不允许进入后续步骤**



------





## **zkw_output 目录结构（目标形态）**



```
zkw_output/
├── sdk/                     ← 裁剪后的 dap_api.h
├── apps/
│   └── demo/
├── lib/
│   ├── libdap.a            ← strip 后
│   ├── libloader.a         ← strip 后（如需要）
│   └── libsecurity.a       ← strip 后（如需要）
│
├── build/
│   └── build_export.bat
│
├── out/
│   ├── bin/
│   ├── img/
│   └── pac/
│
└── README.md
```



------





## **执行步骤**





------





### **Step 1 — 创建导出脚本**



```
tools/export_zkw_output.py
```

职责：

```
internal → zkw_output
```



------





### **Step 2 — 构建 DAP 预编译库**





在 internal：

```
编译：
core/
loader/
security/
platform/
```

输出：

```
libdap.a
```



------





### **Step 3 — 执行 strip**



```
strip --strip-all libdap.a
```

目标：

```
删除：
- 符号名
- debug 信息
```



------





### **Step 4 — 导出 SDK**





复制：

```
internal/sdk/ → zkw_output/sdk/
```

要求：



- 无 internal include
- 无 core 引用
- 仅 dap_api.h





------





### **Step 5 — 导出 demo app**





复制：

```
hello_bigseek → zkw_output/apps/demo/
```

并：



- 替换 include → dap_api.h
- 移除所有 core include





------





### **Step 6 — 删除敏感源码**





确保：

```
❌ core/
❌ loader/
❌ security/
❌ platform/
```

不存在于 zkw_output



------





### **Step 7 — 构建产物**



```
build → bin → bin2 → bin3 → pac
```

输出到：

```
zkw_output/out/
```



------





## **验证标准（必须全部通过）**







### **功能验证**





- demo app 可运行
- BIN / BIN2 / BIN3 正常
- pac 可烧机





------





### **安全验证**





- zkw_output 无 core/loader/security 源码
- libdap.a 已 strip
- strings 检查无明显 DAP 符号





------





### **工程验证**





- zkw_output 可通过脚本自动生成
- 不允许人工手改





------





## **风险**





------





### **Risk 1 — 工程师偷复制 entire repo**





后果：

```
安全完全失效
```

解决：

```
必须使用 export 脚本
```



------





### **Risk 2 — SDK 泄露内部结构**





解决：

```
严格审查 dap_api.h
```



------





### **Risk 3 — strip 不彻底**





解决：

```
strings libdap.a | grep dap_
```



------





## **Deliverables**





1. tools/export_zkw_output.py
2. zkw_output/ 目录
3. libdap.a (strip)
4. demo pac
5. export_inventory.md





------





## **Final Note（必须理解）**





> **TM31 不是“让别人编译你的系统”，**

> **而是“让别人只能用你的系统”。**



------





## **一句话总结**





> **TM31 = internal（可开发） → zkw_output（不可理解但可运行）**

