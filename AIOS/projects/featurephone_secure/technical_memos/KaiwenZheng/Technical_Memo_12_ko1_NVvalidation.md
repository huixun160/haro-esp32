

# **Technical Memo**







## **AIOS Device Identity Root-of-Trust Validation**





**Project**

AIOS Secure Execution



**Phase**

Phase 0 – Device Identity Validation



**Owner**

AIOS Founding Team



**Assigned To**

Embedded System Engineer



**Priority**

P0 – Security Architecture Foundation



------





# **1 背景**





AIOS 在 Unisoc Mocor 功能机平台实现：

```
Firmware (PAC)
   └─ DAP Runtime
        └─ BIN Applications
```

DAP 已经支持：



- 动态加载 .bin
- relocation loader
- LVGL UI





未来支持：

```
App Store
```

远程分发应用。



------





## **当前安全风险**





目前系统：

```
BIN → 反编译 → 恢复 C 级逻辑
```

攻击者可以：



1 获取 BIN

2 反编译

3 拷贝运行



这意味着：

```
APP 可以被复制
```

商业模型无法成立。



------





# **2 安全模型目标**





我们必须实现：





### **未授权 APP 不运行**



```
没有签名 → 不运行
```



### **APP 不可复制**



```
复制到另一台设备 → 无法运行
```



### **APP 不可篡改**



```
修改任意字节 → 不运行
```



------





# **3 Root of Trust 问题**





设备需要一个：

```
唯一设备密钥
```

但现实约束：

```
IMEI 不可靠
```

原因：



- 回收 SoC
- IMEI 可重复
- IMEI 可修改





因此必须建立：

```
DeviceSecret
```



------





# **4 DeviceSecret 设计**





设备第一次开机：

```
生成 256-bit 随机 DeviceSecret
```

并存储到：

```
NV 存储
```

后续：

```
只读
```

DeviceSecret 将用于：

```
BIN 解密
```

以及：

```
APP 绑定
```



------





# **5 本阶段目标**





验证两个关键问题：





### **NV 是否可靠**



```
NV 是否可读写
NV 是否持久
NV 是否稳定
```



------





### **DeviceSecret 是否可实现**



```
首次开机生成
设备唯一
重启不变
```



------





# **6 设备信息**





当前开发设备：

```
Unisoc UMS9117
```

编译方式：

```
make\make_cmd\make -r -R MAKESHELL=CMD p=ums9117_240X320BAR_64MB_ML MODULES=dap JOB=16
```

模块编译：

```
mm ums9117_240X320BAR_64MB_ML new
```



------





# **7 任务一**







## **NV 存储调研**





工程师需要确认：





### **NV API**





是否存在：

```
NV_Read()
NV_Write()
```

或类似接口。



------





### **NV 区域信息**





确认：

```
NV partition
size
location
```



------





### **NV 特性**





必须测试：

| **测试** | **目标**     |
| -------- | ------------ |
| 重启测试 | 数据是否保留 |
| 断电测试 | 数据是否损坏 |
| 多次写入 | 是否稳定     |



------





# **8 任务二**







## **DeviceSecret 生成验证**





实现测试代码：

```
device_secret_init()
```

逻辑：

```
if (NV中不存在secret)
{
    random_generate(secret,32);
    NV_Write(secret);
}
else
{
    NV_Read(secret);
}
```



------





# **9 随机数来源验证**





必须确认：



系统是否提供：

```
TRNG
```

若没有：



使用：

```
timer jitter
ADC noise
```

生成熵源。



------





# **10 设备唯一性测试**





准备：

```
5~10 台设备
```

记录：

```
DeviceSecret hash
```

确认：

```
每台设备不同
```



------





# **11 稳定性测试**





测试流程：



1 开机

2 读取 DeviceSecret

3 记录 hash



重复：

```
100 次 reboot
```

必须保证：

```
DeviceSecret 不变化
```



------





# **12 恶意删除测试**





测试：



删除 NV 数据后：



设备是否：

```
重新生成 DeviceSecret
```

并记录行为。



------





# **13 数据结构**





建议：

```
struct device_secret
{
    uint8 secret[32];
    uint32 crc;
    uint32 version;
};
```



------





# **14 日志输出**





允许输出：

```
DeviceSecret hash
```

禁止输出：

```
DeviceSecret 明文
```



------





# **15 输出文档**





工程师需要提交：

```
docs/device_identity_report.md
```

内容包括：





### **NV 结构**





NV 分区位置

NV API



------





### **DeviceSecret 结果**





设备数量

hash 列表



------





### **稳定性测试**





reboot 次数

成功率



------





### **风险评估**





NV 是否适合作为：

```
Root of Trust
```



------





# **16 成功标准**





满足：

```
DeviceSecret
稳定
唯一
持久
```



------





# **17 时间计划**





预计：

```
1 天
```

完成验证。



------





# **18 下一阶段**





验证成功后：



进入：

```
Phase 1
```

实现：

```
BIN2
签名
加密
设备绑定
```



------





# **19 第一性原理总结**





真正的安全来自：

```
设备身份
签名体系
```

不是：

```
代码混淆
```



------



