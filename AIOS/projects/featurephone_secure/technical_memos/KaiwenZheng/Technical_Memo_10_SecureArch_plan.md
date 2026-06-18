# **Technical Memo**





**Subject:** Security Architecture Design for AIOS DAP & Application Distribution

**From:** AIOS Founding Team

**To:** Security Architecture Lead (New Hire)

**Priority:** P0 – Critical Infrastructure

**Scope:** Unisoc Mocor Feature Phone Platform



------





# **1. 任务背景（必须理解）**





AIOS 在 Unisoc Mocor 功能机平台上实现了一个 **DAP (Dynamic Application Platform)**：



核心能力：



- 允许设备 **运行独立** **.bin** **应用**
- .bin 通过 **重定位机制 (relocation loader)** 加载
- UI 使用 **LVGL9**，不依赖 Mocor MMI
- 未来支持 **App Store 分发**





因此我们拥有：

```
Device
  └─ Firmware (PAC)
        └─ DAP runtime
             └─ Load BIN apps
```

这在传统 feature phone 上 **20 年没有人做过**。



------





# **2. 当前安全问题（必须解决）**





最近的内部逆向工程表明：



**攻击者可以：**



1. 拿到 .bin

2. 反编译

3. 直接恢复接近 C 级逻辑

4. 获取：

   

   - API
   - 架构
   - 商业逻辑

   





如果我们：

```
把 DAP 以 .a / .o / Third Party 方式交付
```

OEM 可以：

```
反编译 → 重构 → 直接复制 DAP
```

后果：



- App Store 被复制
- BIN 生态被复制
- 商业模式失效





**结论**



当前架构 **完全没有 IP 防护能力**。



------





# **3. 本项目目标**





设计一套 **可工程落地的安全体系**：



必须同时保护：





### **A. DAP runtime**





DAP 在 firmware PAC 中。



要求：

```
不能被轻易反编译出完整逻辑
```



------





### **B. BIN App**





APP Store 分发 .bin



要求：

```
BIN 无法在非授权设备运行
BIN 被复制后无法使用
BIN 被篡改无法运行
```



------





# **4. 系统约束**





安全方案必须满足：





### **编译**





不能破坏：

```
Unisoc Mocor 原始 build system
PAC build
烧录流程
```



------





### **运行**





允许：

```
加载延迟增加几十毫秒
```

不能接受：

```
秒级延迟
```



------





### **设备现实**





一些设备：

```
没有 IMEI
可能是回收 SoC
```

因此：

```
IMEI 不能作为 Root of Trust
```



------





# **5. 你的角色（安全架构师）**





你不是写报告的人。



你是：

```
System Security Architect
```

你必须：



1️⃣ 理解整个 runtime 架构

2️⃣ 建立 threat model

3️⃣ 设计 **可实现的安全架构**



------





# **6. 你的第一阶段任务（两周）**





你必须交付以下 4 个文档。



------





# **Deliverable 1**







# **Threat Model**





文件：

```
docs/security/threat_model.md
```

必须回答：





### **攻击者能力**





攻击者可以：

```
获取 PAC firmware
获取 BIN
获取 Third Party SDK
反编译 ARM binary
```

但不一定可以：

```
访问服务器
访问私钥
```



------





### **攻击路径**





至少分析：

```
Attack A
PAC → DAP reverse → clone runtime

Attack B
BIN reverse → steal logic

Attack C
BIN copy → run on other device

Attack D
OEM rebuild firmware → remove protections
```



------





# **Deliverable 2**







# **Security Architecture Proposal**





文件：

```
docs/security/security_architecture.md
```

必须设计完整架构：



核心组件：

```
Secure Loader
App Signature
App Encryption
Device Binding
Key Management
Revocation
```

需要包含：





### **Architecture Diagram**





必须使用 mermaid：

```
Device Boot
     │
Firmware
     │
DAP Runtime
     │
Secure Loader
     │
Verify Signature
     │
Decrypt BIN
     │
Relocate
     │
Execute
```



------





# **Deliverable 3**







# **BIN Secure Format Design**





文件：

```
docs/security/bin_format.md
```

需要设计新的：

```
BIN2 format
```

包含：

```
Header
Signature
Encrypted payload
Metadata
```

必须定义：

```
magic
version
signature
key_id
device_binding_mode
payload
```



------





# **Deliverable 4**







# **Implementation Roadmap**





文件：

```
docs/security/implementation_plan.md
```

必须拆解成工程任务：



例如：

```
Task 1
Implement BIN2 packer

Task 2
Implement signature verification

Task 3
Implement device binding

Task 4
Modify loader
```

每个任务：

```
复杂度
工程量
风险
```



------





# **7. 第二阶段任务**





完成架构后，你需要：



设计 **密钥体系**：



必须明确：

```
Root key
Publisher key
Device key
```

并设计：

```
Key rotation
Key revocation
Offline provisioning
```



------





# **8. 技术深度要求**





你必须理解：

```
ARM reverse engineering
loader design
cryptography primitives
embedded systems
secure boot concepts
```

如果你的方案只是：

```
加壳
代码混淆
```

那是 **不合格方案**。



------





# **9. 我们期望的最终安全能力**





最终系统必须实现：





### **App 不可伪造**



```
只有签名 APP 才能运行
```



------





### **App 不可复制**



```
BIN 复制到别的设备无法运行
```



------





### **App 不可篡改**



```
修改任何字节 → 无法执行
```



------





### **Runtime 难以复制**





DAP 不能被简单复刻。



------





# **10. 成功标准**





如果安全体系正确：



攻击者想复制生态，需要：

```
重写 runtime
破解签名体系
伪造设备绑定
```

成本将从：

```
1 天
```

提升到：

```
数月
```

这就是我们需要的防护。



------





# **11. 第一性原理结论**





不要幻想：

```
代码不可逆
```

这是不可能的。



真正的安全来自：

```
签名体系
设备绑定
分发控制
```

而不是：

```
代码混淆
```



------





# **12. 交付时间**





第一阶段：

```
1 周
```

必须交付：

```
Threat model
Security architecture 
BIN format
Implementation plan
```

之后我们开始工程实现。



------



