

# **Technical Memo**







## **DAP Loader Architecture Analysis for BIN2 Secure Verification**





**Project**

AIOS Secure Execution



**Phase**

Phase 1 – Secure Loader Integration



**Owner**

AIOS Founding Team



**Assigned To**

Embedded System Engineer



**Priority**

P0 – Security Architecture



------





# **1. 任务背景**





AIOS 当前在 Unisoc Mocor 平台上实现了 **DAP (Dynamic Application Platform)**。



DAP 支持：



- 加载 .bin 应用
- relocation loader
- LVGL UI
- 不依赖 MMI





当前执行流程大致为：

```
User Launch App
     ↓
DAP Loader
     ↓
Load BIN File
     ↓
Parse Header
     ↓
Relocate Symbols
     ↓
Execute Entry
```



------





## **当前安全问题**





当前 .bin：

```
未签名
未加密
未绑定设备
```

攻击者可以：



1 获取 .bin

2 反编译

3 复制到其他设备运行



这意味着：

```
应用生态可以被复制
```



------





# **2. 本任务目标**





在实现 BIN2 Secure Execution 之前，必须 **完全理解 DAP Loader 的执行流程**。



核心问题：

```
BIN2 验签应该插入在哪里？
```

如果插错：



- 可以绕过验证
- 或破坏 loader





------





# **3. 任务目标**





工程师需要：

```
梳理 DAP Loader 执行路径
```

并确定：

```
BIN2 验签的唯一安全插入点
```



------





# **4. 分析范围**





重点代码目录：

```
Third-party/DAP/
```

重点文件：

```
DAP_Loader_unisoc.c
DAP_Loader.c
DAP_FileSystem.c
DAP_InterfaceRegister.c
```

尤其关注：

```
DAP_LoaderInit()
DAP_LoadApplication()
```



------





# **5. 需要回答的核心问题**





工程师必须回答以下问题：





### **1 BIN 加载入口**





找到：

```
DAP 应用加载入口函数
```

例如：

```
DAP_LoadApplication()
```

需要确认：

```
函数名
文件位置
调用链
```



------





### **2 BIN 文件读取流程**





分析：

```
文件读取函数
```

例如：

```
FS_Open
FS_Read
FS_Close
```

需要确认：

```
BIN 是否一次性读入 RAM
```



------





### **3 BIN Header 解析**





确认：

```
BIN header 在哪里解析
```

例如：

```
parse_bin_header()
```

需要记录：

```
header 结构
magic
entry offset
```



------





### **4 Relocation 执行位置**





找到：

```
relocation 函数
```

例如：

```
dap_relocate()
```

需要确认：

```
什么时候执行 relocation
```



------





### **5 Entry 执行位置**





确认：

```
应用入口函数调用
```

例如：

```
entry()
```



------





# **6 需要输出的架构图**





工程师必须输出一个 **完整执行链图**。



示例：

```
DAP_LoadApplication
      ↓
open file
      ↓
read bin
      ↓
parse header
      ↓
relocate
      ↓
resolve imports
      ↓
call entry
```



------





# **7 需要定位的安全插入点**





理论上正确位置是：

```
read bin
     ↓
VERIFY SIGNATURE
     ↓
decrypt payload
     ↓
parse header
     ↓
relocate
     ↓
execute
```

工程师需要确认：

```
真实代码是否符合此结构
```



------





# **8 输出文档**





工程师必须提交：

```
docs/dap_loader_analysis.md
```

必须包含：





### **1 Loader Call Graph**





列出：

```
函数调用顺序
```



------





### **2 Loader State Machine**





描述：

```
加载阶段
```

例如：

```
INIT
READ_FILE
PARSE_HEADER
RELOCATE
EXECUTE
```



------





### **3 BIN 内存布局**





确认：

```
BIN 在 RAM 中如何布局
```

例如：

```
[header]
[text]
[data]
[bss]
```



------





### **4 安全插入点**





明确指出：

```
BIN2 验签代码应该插入哪一行
```

例如：

```
DAP_Loader_unisoc.c: line XXX
```



------





# **9 需要特别注意的问题**





工程师必须检查：





### **是否存在绕过路径**





例如：

```
debug loader
direct jump
test interface
```



------





### **是否存在多种加载路径**





例如：

```
menu launch
script launch
internal API launch
```

如果存在：

```
所有路径必须统一经过验证
```



------





# **10 验证方法**





完成分析后：



工程师需要写一个 **最小 PoC**：

```
fake BIN2
```

验证：

```
loader 是否执行
```

如果执行：

```
说明验证位置错误
```



------





# **11 时间要求**





预计：

```
2–3 天
```

完成分析。



------





# **12 输出质量标准**





报告必须达到：

```
任何工程师看文档
即可知道
BIN2 验签插入位置
```



------





# **13 第一性原理**





安全执行链的唯一原则：

```
任何用户代码执行前
必须经过验证
```

如果验证发生在：

```
entry()
之后
```

那就是：

```
完全无效
```



------





# **14 任务完成标志**





工程师完成任务后，我们将获得：

```
DAP Loader 完整执行链
BIN2 验签插入点
```

然后进入：

```
Phase 2
```

实现：

```
BIN2 Secure Loader
```



------

