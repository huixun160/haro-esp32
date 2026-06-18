# Technical Memo**



## **BIN2 Secure Loader – Phase 0 Implementation Kickoff**





**Project**

AIOS Secure Execution



**Platform**

Unisoc Mocor (UMS9117)



**Subsystem**

DAP (Dynamic Application Platform)



**Priority**

P0 – Security Infrastructure



**Author**

AIOS Architecture



**Estimated Time**

```
4–6 engineering days
```



------





# **1 背景**





当前 DAP 运行流程：

```
User Launch App
     ↓
DAP_ExecuteAP()
     ↓
Load BIN
     ↓
Relocate
     ↓
Execute
```

问题：

```
任何 BIN 文件都可以运行
```

攻击者可以：

```
复制 BIN
反编译
重新部署
```

这会导致：

```
AIOS 应用生态可被复制
```



------





# **2 本阶段目标**





实现 **BIN2 Secure Loader (Phase-0)**。



目标：

```
只有合法签名的 BIN2 可以运行
```



------





# **3 Phase-0 范围**





本阶段 **不做设备绑定**。



仅实现：

```
签名验证
篡改检测
BIN1 / BIN2 分流
```



------





# **4 最终执行流程**





修改后的执行链：

```
DAP_ExecuteAP()
      ↓
Load BIN
      ↓
Detect BIN Format
      ↓
if BIN2
    verify_signature()
else
    allow BIN1 (dev mode)
      ↓
Relocate
      ↓
Execute
```



------





# **5 代码插入位置**





Loader 文件：

```
Third-party/DAP/DAP_Loader_unisoc.c
```

函数：

```
DAP_ExecuteAP()
```

插入点：

```
Step5: 完整 BIN 文件读入 RAM
Step6: GetBSSSpace() 之前
```

示例：

```
file_read_to_RAM()

// 新增
bin2_verify()

GetBSSSpace()
```



------





# **6 新增模块**





新增目录：

```
Third-party/DAP/security/
```

新增文件：

```
bin2_loader.c
bin2_loader.h

bin2_crypto.c
bin2_crypto.h

bin2_format.h
```



------





# **7 BIN2 文件结构**



```
+-------------------+
| BIN2 Header       |
+-------------------+
| Signature         |
+-------------------+
| Encrypted Payload |
+-------------------+
```



------





# **8 BIN2 Header**





定义：

```
typedef struct {

    char magic[4];         // "BIN2"

    uint16 version;
    uint16 header_size;

    uint32 payload_size;

    uint8  key_id;
    uint8  binding_mode;

    uint16 reserved;

    uint8  payload_hash[32];

} BIN2_Header;
```



------





# **9 binding_mode**





Phase-0：

```
0 = UNBOUND
```

未来：

```
1 = DEVICE_BOUND
```



------





# **10 新增函数**







## **BIN2 Detect**



```
int bin2_detect(uint8 *buffer)
```

逻辑：

```
if magic == "BIN2"
    return BIN2
else
    return BIN1
```



------





## **Signature Verify**





函数：

```
int bin2_verify_signature(uint8 *data, uint32 size)
```

算法：

```
Ed25519
```

验证内容：

```
header + encrypted_payload
```



------





## **Payload Hash**





算法：

```
SHA256
```

验证：

```
sha256(payload) == header.payload_hash
```



------





# **11 bin2_verify() 实现**





核心流程：

```
parse header
verify signature
hash payload
return OK / FAIL
```

示例：

```
int bin2_verify(uint8 *buf)
{
    BIN2_Header *hdr;

    hdr = parse_header(buf);

    if (!verify_signature(buf))
        return FAIL;

    if (!verify_hash(buf))
        return FAIL;

    return OK;
}
```



------





# **12 Loader 修改**





修改：

```
DAP_ExecuteAP()
```

新增逻辑：

```
if (bin2_detect(Running_AP) == BIN2)
{

    if (bin2_verify(Running_AP) != OK)
    {
        SCI_TRACE_LOW("BIN2 verify failed");

        return DAP_ERR_SECURITY;
    }

}
```



------





# **13 Public Key**





存储在：

```
bin2_crypto.c
```

示例：

```
static const uint8 PUBLIC_KEY[32] =
{
   0x12,0x34...
};
```



------





# **14 PC 打包工具**





新增：

```
tools/bin2_packer
```

输入：

```
app.bin
```

输出：

```
app.bin2
```

流程：

```
hash payload
sign payload
write header
append payload
```



------





# **15 Debug Log**





新增日志：

```
BIN2 detected
BIN2 verify success
BIN2 verify failed
```



------





# **16 错误码**





新增：

```
DAP_ERR_SECURITY
DAP_ERR_SIGNATURE
DAP_ERR_HASH
```



------





# **17 编译方式**





保持现有编译命令：

```
make\make_cmd\make -r -R MAKESHELL=CMD p=ums9117_240X320BAR_64MB_ML MODULES=dap JOB=16

mm ums9117_240X320BAR_64MB_ML new
```



------





# **18 测试用例**







### **Case1**





合法 BIN2

```
运行成功
```



------





### **Case2**





篡改 Payload

```
verify fail
拒绝执行
```



------





### **Case3**





旧 BIN1



开发模式：

```
允许执行
```



------





### **Case4**





错误签名

```
拒绝执行
```



------





# **19 Phase-0 完成标准**





满足：

```
合法 BIN2 可运行
篡改 BIN2 不可运行
```



------





# **20 Phase-1 预告**





下一阶段将增加：

```
DeviceSecret 设备绑定
AES 加密
Key rotation
Revocation
```



------





# **21 第一性原理**





AIOS 安全体系核心规则：

```
任何用户代码执行前
必须经过验证
```



------





# **22 执行计划**





Day 1

```
BIN2 format
bin2_detect()
```

Day 2

```
signature verify
hash verify
```

Day 3

```
loader integration
```

Day 4

```
PC packer
```

Day 5

```
测试
```



------





# **23 本阶段不做**





避免工程发散：

```
App Store
远程下载
设备绑定
密钥轮换
```



------





# **最终目标**





Phase-0 完成后将得到：

```
AIOS 第一个 Secure Execution Path
```

这一步完成后：

```
复制 BIN
将无法运行
```



------



