下面这份 **Kickoff Technical Memo** 是给工程师直接执行的版本。

目标不是写论文，而是 **2–3 周内把“未签名 BIN 不能运行 + BIN 不能跨设备复制”做出来**，并且 **不破坏现有 Mocor build 和烧机流程**。



我会非常直白：**我们现在不是在做完美安全体系，而是在止血。**



------





# **Technical Memo**







## **AIOS DAP Secure Execution – Phase 0 Kickoff**





**Project**

AIOS Secure Execution MVP



**Owner**

AIOS Founding Team



**Assigned To**

Embedded Security Engineer



**Priority**

P0 – Ecosystem Protection



------





# **1. 背景（必须理解）**





当前 AIOS 在 Unisoc Mocor 功能机平台实现：



- DAP runtime
- 支持 .bin 应用
- 支持动态加载（relocation loader）
- LVGL UI 不依赖 MMI





系统结构：

```
Firmware (PAC)
   └─ DAP Runtime
        └─ BIN Application
```

DAP 已经证明可以运行第三方 APP。



------





## **当前重大风险**





已经确认：

```
BIN → 反编译 → 恢复 C 级逻辑
```

攻击者可以：



1. 拿到 .bin
2. 反编译
3. 获取 API / 架构 / 商业逻辑
4. 在自己系统上复刻 DAP





这意味着：



**我们的 App 生态可以被复制。**



------





# **2. 目标**





建立 **最小安全执行体系（MVP）**



必须实现三件事：





### **1 未签名 BIN 不运行**





任何 BIN：

```
没有合法签名 → loader 必须拒绝执行
```



------





### **2 BIN 不能跨设备复制**





复制 .bin 到另一台设备：

```
必须无法运行
```



------





### **3 BIN 篡改必定失败**





修改 1 byte：

```
必须无法运行
```



------





# **3. 约束**





必须满足：





### **编译**





不能破坏现有 build：

```
make\make_cmd\make -r -R MAKESHELL=CMD p=ums9117_240X320BAR_64MB_ML MODULES=dap JOB=16

mm ums9117_240X320BAR_64MB_ML new
```



------





### **烧机**





PAC 生成流程必须保持不变。



------





### **性能**





允许：

```
增加几十毫秒
```

不允许：

```
秒级延迟
```



------





# **4. Phase 0 任务目标**





本阶段只实现 **BIN2 Secure Execution MVP**



不涉及：



- App Store
- 网络
- OTA





只支持：

```
USB sideload
```



------





# **5. 架构设计（MVP）**





引入新的应用格式：

```
BIN2
```

结构：

```
BIN2
 ├─ Header
 ├─ Signature
 └─ Encrypted Payload
```

Payload 为：

```
原始 BIN
```



------





# **6. Loader 执行流程**





DAP loader 新流程：

```
Load file
   ↓
Check magic (BIN2)
   ↓
Verify signature
   ↓
Derive device key
   ↓
Decrypt payload
   ↓
Relocate
   ↓
Execute
```

重要原则：

```
必须先验签再解密
```



------





# **7. 设备绑定设计**





不能依赖：

```
IMEI
```

因为：



- 回收 SoC
- 不可靠





------





## **DeviceSecret 方案**





设备第一次上电：

```
生成 256-bit 随机数
```

保存到：

```
NV 参数区
```

后续：

```
只读
```



------





## **Key 派生**





设备密钥：

```
device_secret
```

APP 密钥：

```
app_key = HKDF(device_secret + app_id)
```



------





# **8. BIN2 Header 设计**





最小字段：

```
magic = "BIN2"
version
app_id
payload_size
signature
nonce
flags
```



------





# **9. 签名体系**





使用：

```
Ed25519
```

签名覆盖：

```
header + encrypted payload
```



------





# **10. 加密**





MVP 使用：

```
AES-CTR
```

加密对象：

```
payload
```



------





# **11. PC 工具开发**





新增工具：

```
bin2_packer
```

功能：





### **pack**



```
bin → bin2
```

步骤：

```
read bin
encrypt
sign
write bin2
```



------





### **verify**



```
验证 bin2
```



------





# **12. Loader 修改位置**





DAP loader 中：

```
DAP_LoadApplication()
```

插入流程：

```
if magic == BIN2
    verify_signature()
    decrypt_payload()
```



------





# **13. DeviceSecret 实现**





新增模块：

```
device_identity.c
```

API：

```
int device_secret_init()
int device_secret_load()
int device_secret_generate()
```

逻辑：

```
if NV 中不存在 secret
    generate random 256bit
    write NV
else
    load secret
```



------





# **14. NV 存储要求**





DeviceSecret：

```
256bit
```

需要：

```
CRC
version
```

结构：

```
struct device_secret {
    uint8 secret[32];
    uint32 crc;
}
```



------





# **15. 任务拆分**







## **Task 1**





BIN2 format



输出：

```
docs/bin2_format.md
```



------





## **Task 2**





PC tool

```
tools/bin2_packer
```



------





## **Task 3**





DeviceSecret

```
device_identity.c
```



------





## **Task 4**





Loader 修改

```
dap_loader_secure.c
```



------





# **16. 验收测试**





必须通过：





### **Test 1**





修改 bin2 任意 byte

```
必须执行失败
```



------





### **Test 2**





未签名 bin

```
拒绝执行
```



------





### **Test 3**





bin2 复制到另一台设备

```
必须解密失败
```



------





### **Test 4**





正常 bin2

```
正常运行
```



------





# **17. 日志要求**





日志不能泄露：

```
key
payload
secret
```

只输出：

```
SECURE_VERIFY_FAIL
SECURE_DECRYPT_FAIL
```



------





# **18. 时间计划**





Phase 0

```
2 周
```

目标：

```
USB sideload secure execution
```



------





# **19. 成功标准**





完成后：



攻击者：

```
复制 bin
```

将无法：

```
运行
```

并且：

```
修改 bin
```

将无法：

```
运行
```



------





# **20. 第一性原理总结**





你无法做到：

```
代码不可逆
```

但你可以做到：

```
未授权代码不可运行
```

这就是：



**iOS 安全模型。**



------



如果你愿意，我可以再给你一份 **Phase 1 memo（更关键）**：



那一阶段会解决：



- **DAP runtime 本身的反逆向设计**
- **API ID 化**
- **去字符串锚点**
- **代码混淆**
- **文件系统权限隔离**





那才是让 **OEM 逆向成本上升 10 倍的关键工程。**