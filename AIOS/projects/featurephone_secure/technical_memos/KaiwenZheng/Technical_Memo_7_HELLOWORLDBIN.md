

------



# **Technical Memo #7**



## **Hello World 独立 .bin 模块 — 编译脚本与工程结构设计**



**版本**：Draft v1

**日期**：2026-02-09

**对象**：NBS 工程师

**目标**：基于 MTKcompilebin 参考工程，设计并实现一个最小化的 Hello World 独立 .bin 文件，验证 DAP 独立编译链路在 UNISOC 平台上的可行性

**编译器**：ARM armcc（ADS1.2 兼容模式）



------



## **0. 背景与动机**



### **0.1 为什么需要独立 .bin**

DAP（Dynamic Application Platform）的核心机制是：应用程序以独立的 `.bin` 文件形式存在，由手机 OS 在运行时加载并执行。这个 `.bin` 文件：

- **不链接进主固件**，独立于 OS 编译
- 使用 **位置无关代码（ROPI/RWPI）** 以便在任意地址加载
- 通过 OS 注入的 **函数指针表** 访问系统 API（非静态链接）
- 头部包含固定结构的 **TApplication 描述符**，供 OS 识别和加载



### **0.2 参考工程：MTKcompilebin**

过去在 MTK 平台上，DAP 独立 .bin 通过 ARM ADS1.2 IDE 的 `.mcp` 项目文件编译。参考工程位于：

```
MTKcompilebin/
├── MTK_APP.mcp          ← ARM ADS1.2 项目文件（含编译/链接选项）
├── inc/
│   ├── def.h            ← 平台无关类型定义
│   ├── OSInterface.h    ← OS 接口函数指针类型
│   ├── OSAPILists.h     ← OS API 列表结构
│   ├── GlobalDefs.h     ← 全局资源枚举
│   ├── MainForm.h       ← 窗体结构
│   └── GBK_Uncode.h     ← 编码转换
└── src/
    ├── Start.s          ← BSS 地址辅助（汇编）
    ├── Entry.c          ← TApplication 头 + 入口分发
    ├── Main.c           ← 用户主函数
    ├── OSAPILists.c     ← OS API 动态绑定
    ├── MainForm.c       ← 窗体逻辑
    └── GBK_Uncode.c     ← 编码表
```



### **0.3 从 .mcp 中完整提取的编译选项与预处理宏**

> [!IMPORTANT]
> `MTK_APP.mcp` 是 ARM ADS1.2 的二进制项目文件，内含两个 Build Target：
> 1. **"Flash_Hex"** — 44B0 BIOS 配置（与 DAP 无关，忽略）
> 2. **"MTK_APP"** — **DAP 独立 .bin 配置（本节所述，全部来自此 target）**
>
> 以下选项通过解析 `.mcp` 二进制中的可读字符串完整提取，已逐项核实。



#### **A. ARM C Compiler（armcc）选项**

| 选项 | .mcp 原始表示 | 含义 |
|------|--------------|------|
| `-O1` | `-O.level=1` | 优化等级 1（**注意：不是 -O2**） |
| `-cpu ARM7EJ-S` | `-cpu#ARM7EJ-S` | 目标 CPU 核心 |
| `-apcs /ropi` | `-apcs.ropi#/ropi` | **RO 段位置无关**（代码可加载到任意地址） |
| `-apcs /norwpi` | `-apcs.rwpi#/norwpi` | **RW 段不启用 RWPI**（编译器层面；链接器层面另行处理） |
| `-zc` | `.schar=-zc` | **强制 `char` 为 `signed char`**（ADS1.2 兼容性关键） |
| `-zo` | `.areaperfn=-zo` | **每个函数独立段**（area per function，便于 linker 死代码消除） |
| `-fy` | `.fy=-fy` | 兼容老版本 armcc 的浮点行为 |
| `-split_ldm` | `-split_ldm^=1` | **拆分 LDM/STM 指令**（避免中断延迟过长） |
| `-auto_float_constants` | `-auto_float_constants^=1` | 自动浮点常量提升 |
| `-g+` | `-g=+` | **生成调试信息**（开发阶段；发布版可改 `-g-`） |

> **?? 编译器层面只开了 `-apcs /ropi`（RO 位置无关），没有开 `/rwpi`（RW 位置无关）！**
> 这意味着 RW 数据的位置无关性是由 **linker 的 `-rwpi` 选项** 和 **代码中手动使用 `AddrRelocation()`** 来实现的。
> 这是 MTK DAP 设计的一个关键特征——不依赖编译器自动生成的 RWPI 寻址（SB 寄存器），而是自己管理 RW 数据的重定位。



#### **B. 预处理器宏（-D 定义）**

从 `.mcp` 中提取的所有 `-D` 宏定义：

| 宏 | 值/状态 | 含义 |
|----|---------|------|
| `__S3C44B0X__` | 已定义（无值） | 原始目标板标识（Samsung S3C44B0X 开发板，在 Hello World 中可移除或替换） |
| `__OPTIMISE_LEVEL` | `=1` | 优化等级宏（与 `-O1` 对应，供代码中条件编译使用） |
| `__FEATURE_SIGNED_CHAR` | 已定义 | 标记 `char` 为 signed（与 `-zc` 对应） |
| `__TARGET_ARCH_5TE` | 已定义 | ARM 架构版本 = ARMv5TE |
| `__TARGET_CPU_ARM7EJ_S` | 已定义 | 目标 CPU = ARM7EJ-S |
| `__TARGET_FEATURE_DSPMUL` | 已定义 | 支持 DSP 乘法扩展指令 |
| `__TARGET_FEATURE_DOUBLEWORD` | 已定义 | 支持双字（64-bit）数据操作 |
| `__APCS_ROPI` | 已定义 | 标记使用 ROPI 模式（供代码中条件编译使用） |
| `__TARGET_CPU_ARM7TDMI` | **已清除**（`=`） | **未启用**（原 BIOS target 使用，DAP target 已禁用） |
| `__TARGET_ARCH_4T` | **已清除**（`=`） | **未启用**（ARMv4T 已被 ARMv5TE 替代） |

> **宏分类说明**：
> - 带 `?` 后缀的项（如 `-D__S3C44B0X__?`）表示该宏在 ADS1.2 GUI 中为 "可选/条件" 状态
> - 带 `.` 后缀的项（如 `-D__APCS_ROPI?.`）表示该宏由 Target Settings 面板自动管理
> - 带 `=` 后缀无值的项（如 `-D__TARGET_CPU_ARM7TDMI=`）表示该宏被显式取消定义



#### **C. ARM Assembler（armasm）选项**

| 选项 | .mcp 原始表示 | 含义 |
|------|--------------|------|
| `-keep` | `.keep=-keep` | 保留本地符号（便于调试） |
| `-g` | `.debug=-g` | 生成调试信息 |

> **注意**：汇编器的 `-cpu` 和 `-apcs` 选项在 `.mcp` 中由 ARM Target 面板统一继承，与 C Compiler 共享。
> 实际命令行需显式传入：`armasm -cpu ARM7EJ-S -apcs /ropi`



#### **D. ARM Linker（armlink）选项**

| 选项 | .mcp 原始表示 | 含义 |
|------|--------------|------|
| `-entry Entry` | `-entry#Entry` | **入口符号** = `Entry` 函数 |
| `-ro-base 0x00000000` | `-ro-base#0x00000000` | **RO 基址 = 0**（运行时由 OS 重定位） |
| `-first Entry.o(.constdata)` | `-first#Entry.o(.constdata)` | **★ 关键：`TApplication` 结构体放在 .bin 开头** |
| `-ropi` | `.ropi=-ropi` | 链接器确认 RO 段位置无关 |
| `-rwpi` | `.rwpi=-rwpi` | **链接器确认 RW 段位置无关**（注意：编译器层面未开 /rwpi） |
| `-armlib` | `.armlib=-armlib` | **链接 ARM 标准 C 库**（提供 sprintf 等） |
| `-reloc` | `.reloc=-reloc` | **保留重定位信息**（OS 加载器可能需要） |
| `-nodebug` | `.debug=-nodebug` | **剥离调试信息**（减小 .bin 体积） |
| `-info totals` | `-info.total#totals` | 输出段总大小统计 |
| `-info unused` | `-info.unused#unused` | 输出未使用段信息 |
| `-info veneers` | `-info.veneers#veneers` | 输出 veneer（ARM/Thumb 桥接代码）信息 |
| `-info sizes` | `-info.size#sizes` | 输出各段大小信息 |
| `-map` | `.map=-map` | 生成内存映射 |
| `-symbols` | `.symbols=-symbols` | 输出符号表 |
| `-xref` | `.xref=-xref` | 输出交叉引用 |
| `-callgraph` | `.callgraph=-callgraph` | 生成调用图 |
| `-list .\MTK_APP.lst` | `-list#.\MTK_APP.lst` | 输出链接器列表文件 |

> **链接器层面特别注意的 "Remove" 选项**（从 `.mcp` 中发现但均为 **未启用** 状态）：
> ```
> -remove.zi#nozi     ← ZI 段不移除（保留 BSS）
> -remove.rw#norw     ← RW 段不移除（保留已初始化数据）
> -remove.ro#noro     ← RO 段不移除（保留代码和只读数据）
> ```
> 这些 `no*` 前缀表示 **不去除** 对应段，确保 .bin 包含完整的 RO+RW+ZI 信息。



#### **E. ARM fromELF 选项**

| 选项 | .mcp 原始表示 | 含义 |
|------|--------------|------|
| `-bin` | `.format=-bin` | **输出纯二进制格式**（非 Intel HEX） |
| `-c` | `.text.c=-c` | 输出 C 数组形式（备用，可选） |
| `-output SDK_*.bin` | `-output#SDK_*_BSS.EXE` | 输出文件名（原始命名含 BSS 标记） |

> **注意**：原项目输出名为 `SDK_*_BSS.EXE`，扩展名 `.EXE` 是历史命名习惯，实际是纯 binary 格式。
> Hello World 中建议改为 `.bin` 扩展名以避免混淆。



#### **F. 完整命令行还原（从 .mcp 推导）**

将以上选项还原为实际命令行：

```bat
REM === 编译 C 源文件 ===
armcc -c -O1 -cpu ARM7EJ-S -apcs /ropi ^
      -zc -zo -fy -split_ldm -auto_float_constants -g+ ^
      -D__S3C44B0X__ -D__OPTIMISE_LEVEL=1 ^
      -D__FEATURE_SIGNED_CHAR ^
      -D__TARGET_ARCH_5TE -D__TARGET_CPU_ARM7EJ_S ^
      -D__TARGET_FEATURE_DSPMUL -D__TARGET_FEATURE_DOUBLEWORD ^
      -D__APCS_ROPI ^
      -I inc ^
      -o out\Entry.o src\Entry.c

REM === 汇编 ===
armasm -cpu ARM7EJ-S -apcs /ropi -keep -g ^
       -o out\Start.o src\Start.s

REM === 链接 ===
armlink -entry Entry -ro-base 0x00000000 ^
        -first Entry.o(.constdata) ^
        -ropi -rwpi -armlib -reloc -nodebug ^
        -info totals,unused,veneers,sizes ^
        -map -symbols -xref -callgraph ^
        -list out\hello_world.lst ^
        -o out\hello_world.axf ^
        out\Entry.o out\Main.o out\Start.o

REM === 转换 ===
fromelf -bin -output out\hello_world.bin out\hello_world.axf
```



------



## **1. Hello World .bin 工程结构**



### **1.1 目录规划**

```
featurephoneosreconstruction-main/
└── DAP/
    └── sdk/
        └── hello_world/
            ├── build_hello.bat      ← 一键编译脚本
            ├── inc/
            │   ├── def.h            ← 平台无关类型（从 MTKcompilebin 适配）
            │   └── OSInterface.h    ← OS 接口类型（最小化）
            ├── src/
            │   ├── Start.s          ← BSS 地址辅助汇编
            │   ├── Entry.c          ← TApplication 头 + 入口
            │   └── Main.c           ← Hello World 主逻辑
            └── out/                 ← 编译输出目录
                ├── *.o
                ├── hello_world.axf
                ├── hello_world.bin
                └── hello_world.lst
```


### **1.2 设计原则**

1. **最小化**：不含 MainForm / GBK_Uncode / OSAPILists 等 UI 相关模块
2. **只验证链路**：Hello World 仅通过 OS 接口输出一条 trace 消息
3. **保留 TApplication 完整结构**：确保 OS 加载器能识别
4. **保留 Start.s**：BSS 地址计算是 DAP 框架的刚需



------



## **2. 源文件详细设计**



### **2.1 `inc/def.h` — 基础类型定义**

从 MTKcompilebin 的 `def.h` 精简，只保留 DAP 框架必须的类型：

```c
#ifndef _APP_DEF_H_
#define _APP_DEF_H_

/* ---- 基础类型 ---- */
typedef void            _VOID;
typedef char            _CHAR8;
typedef unsigned char   _UCHAR8;
typedef int             _INT32;
typedef unsigned int    _UINT32;
typedef unsigned long   _DWORD;
typedef _INT32          _BOOL;
typedef unsigned short  _U16;
typedef unsigned char   _U8;

/* ---- 常量 ---- */
#define NULL            ((_VOID *)0)
#define _FALSE          0
#define _TRUE           (!(_FALSE))
#define OS_OK           0L
#define OS_ERROR        0xFFFFFFFFL

#endif /* _APP_DEF_H_ */
```



### **2.2 `inc/OSInterface.h` — OS 接口类型**

最小化的 OS 接口，Hello World 只需要 `OS_TraceOutString`：

```c
#ifndef _OSAPI_H_
#define _OSAPI_H_

#include "def.h"

/* OS 接口的基础函数指针类型 */
typedef _VOID       (*TOSInterface)     (_VOID);
typedef TOSInterface(*TGetOSInterface)  (_CHAR8 *FunctionName);
typedef _INT32      (*TAddOSInterface)  (_CHAR8 *FunctionName, TOSInterface OSInterface);
typedef _INT32      (*TDelOSInterface)  (_CHAR8 *FunctionName);

/* Trace 输出 */
typedef _VOID       (*TCommOut)         (char *pString);

/* 全局函数声明 */
extern _U16*            GetApplicationName(_VOID);
extern _DWORD           AddrRelocation(_DWORD Data);
extern TOSInterface     FindInterface(_CHAR8 *FunctionName);
extern _BOOL            AddInterface(_CHAR8 *FunctionName, TOSInterface Interface);
extern _BOOL            DelInterface(_CHAR8 *FunctionName);
extern TGetOSInterface  GetOSInterface(_VOID);
extern TAddOSInterface  GetOSRegister(_VOID);

#endif /* _OSAPI_H_ */
```



### **2.3 `src/Start.s` — BSS 地址辅助**

直接沿用 MTKcompilebin 的 `Start.s`，无需修改：

```asm
    GBLL    THUMBCODE
    [ {CONFIG} = 16
THUMBCODE SETL  {TRUE}
    CODE32
    |
THUMBCODE SETL  {FALSE}
    ]

    [ THUMBCODE
    CODE32
    ]

    MACRO
    MOV_PC_LR
    [ THUMBCODE
        bx lr
    |
        mov pc, lr
    ]
    MEND

    AREA    get_bss_addr, CODE, READONLY

    EXPORT GetBssStartAddr
GetBssStartAddr
    ldr     r0, BaseOfZero
    MOV_PC_LR

    EXPORT GetBssEndAddr
GetBssEndAddr
    ldr     r0, EndOfBSS
    MOV_PC_LR

    IMPORT  |Image$$RO$$Base|
    IMPORT  |Image$$RO$$Limit|
    IMPORT  |Image$$RW$$Base|
    IMPORT  |Image$$ZI$$Base|
    IMPORT  |Image$$ZI$$Limit|

BaseOfROM   DCD |Image$$RO$$Base|
TopOfROM    DCD |Image$$RO$$Limit|
BaseOfBSS   DCD |Image$$RW$$Base|
BaseOfZero  DCD |Image$$ZI$$Base|
EndOfBSS    DCD |Image$$ZI$$Limit|

    END
```



### **2.4 `src/Entry.c` — TApplication 描述符 + 入口**

这是 .bin 文件的核心框架。`TApplication` const 结构体会被 `-first Entry.o(.constdata)` 放在文件最开头：

```c
#include "OSInterface.h"

/* ---- 函数指针类型 ---- */
typedef int (*TAP_Entry)       (_VOID *Data, _DWORD Params, _CHAR8 *CMD);
typedef int (*TAP_GetBSSSpace) (void);

/* ---- 外部声明 ---- */
extern _CHAR8  UserInputSN[];
extern int     Main(_VOID *Data, _DWORD Params, _CHAR8 *String);
extern int     GetBssEndAddr(_VOID);
extern int     GetBssStartAddr(_VOID);

/* ---- 前向声明 ---- */
int Entry(_VOID *Data, _DWORD Params, _CHAR8 *String);
int GetBSSSpace(void);

/* ---- TApplication 描述符 ---- */
typedef struct Tag_Application
{
    _CHAR8          MTKExeTag[8];       // DAP 文件识别标识
    TAP_Entry       Entry;              // 应用入口
    _DWORD          TagCheckSum;        // 标识校验和
    TOSInterface    OSAPI;              // API 查找接口
    TOSInterface    Register;           // API 注册接口
    TOSInterface    DelAPI;             // API 删除接口
    _DWORD          LoadAddr;           // 加载地址（运行时填充）
    _CHAR8          Name[256];          // 应用名（Unicode）
    _CHAR8          Data[32];           // 命令字符串
    TAP_GetBSSSpace GetBSSSpace;        // BSS 空间大小查询
    _DWORD          VersionMark;        // 版本标识（高位 0x55AA）
    _CHAR8          InLineSN[8];        // 内建序列号
    _CHAR8*         InputSN;            // 用户序列号
} TApplication;

/* ---- const 实例（放在 .constdata，被 -first 置于文件首） ---- */
const TApplication Application[] =
{
    "MTK_Exe",
    (TAP_Entry)Entry,
    (_DWORD)((_DWORD)'M'+(_DWORD)'T'+(_DWORD)'K'+(_DWORD)'_'
            +(_DWORD)'E'+(_DWORD)'x'+(_DWORD)'e'),
    NULL,       // OSAPI  — OS 在加载时填入
    NULL,       // Register — OS 在加载时填入
    NULL,       // DelAPI — OS 在加载时填入
    0,          // LoadAddr — OS 在加载时填入
    "",         // Name
    "",         // Data
    (TAP_GetBSSSpace)GetBSSSpace,
    (_DWORD)0x55AA0001,     // 版本 = 0x0001
    {0x00},
    UserInputSN
};

/* ---- 入口函数 ---- */
int Entry(_VOID *Data, _DWORD Params, _CHAR8 *CMD)
{
    return Main(NULL, Params, CMD);
}

/* ---- BSS 空间大小 ---- */
int GetBSSSpace(void)
{
    return GetBssEndAddr() - GetBssStartAddr();
}

/* ---- 获取 TApplication 描述符指针 ---- */
TApplication *GetApplication(_VOID)
{
    return ((TApplication *)(&Application));
}

/* ---- 获取加载地址 ---- */
_DWORD GetApplicationEntry(_VOID)
{
    return (_DWORD)(((TApplication *)(&Application))->LoadAddr);
}

/* ---- 获取应用名 ---- */
_U16 *GetApplicationName(_VOID)
{
    return (_U16*)(((TApplication *)(&Application))->Name);
}

/* ---- 获取 OS API 查找接口 ---- */
TGetOSInterface GetOSInterface(_VOID)
{
    return (TGetOSInterface)(((TApplication *)(&Application))->OSAPI);
}

/* ---- 获取 OS API 注册接口 ---- */
TAddOSInterface GetOSRegister(_VOID)
{
    return (TAddOSInterface)(((TApplication *)(&Application))->Register);
}

/* ---- 通过名称查找 OS API ---- */
TOSInterface FindInterface(_CHAR8 *FunctionName)
{
    TGetOSInterface find = (TGetOSInterface)(((TApplication *)(&Application))->OSAPI);
    if (FunctionName == NULL) return NULL;
    return find(FunctionName);
}

/* ---- 注册一个接口 ---- */
_BOOL AddInterface(_CHAR8 *FunctionName, TOSInterface Interface)
{
    TAddOSInterface add = (TAddOSInterface)(((TApplication *)(&Application))->Register);
    if (FunctionName == NULL) return _FALSE;
    if (add(FunctionName, Interface) == OS_ERROR) return _FALSE;
    return _TRUE;
}

/* ---- 删除一个接口 ---- */
_BOOL DelInterface(_CHAR8 *FunctionName)
{
    TDelOSInterface del = (TDelOSInterface)(((TApplication *)(&Application))->DelAPI);
    if (FunctionName == NULL) return _FALSE;
    if (del(FunctionName) == OS_ERROR) return _FALSE;
    return _TRUE;
}

/* ---- 地址重定位 ---- */
_DWORD AddrRelocation(_DWORD Data)
{
    return (_DWORD)((_DWORD)GetApplicationEntry() + (_DWORD)Data);
}
```



### **2.5 `src/Main.c` — Hello World 主逻辑**

这是唯一的 **用户业务文件**，保持最简：

```c
#include "OSInterface.h"

const _CHAR8 UserInputSN[8] = "0000";

int Main(_VOID *Data, _DWORD Params, _CHAR8 *CMD)
{
    /* 通过 OS 接口获取 trace 输出函数 */
    TCommOut trace = (TCommOut)FindInterface("OS_TraceOutString");

    if (trace != NULL)
    {
        trace("=== Hello World from DAP .bin! ===\r\n");
        trace("DAP standalone binary is running.\r\n");
    }

    return 1;
}
```



### **2.6 `src/Main.c` — Hello World 主逻辑**

这是唯一的 **用户业务文件**，保持最简：

```c
#include "OSInterface.h"

const _CHAR8 UserInputSN[8] = "0000";

int Main(_VOID *Data, _DWORD Params, _CHAR8 *CMD)
{
    /* 通过 OS 接口获取 trace 输出函数 */
    TCommOut trace = (TCommOut)FindInterface("OS_TraceOutString");

    if (trace != NULL)
    {
        trace("=== Hello World from DAP .bin! ===\r\n");
        trace("DAP standalone binary is running.\r\n");
    }

    return 1;
}
```



------



## **2.7 输出文件命名策略**



### **2.7.1 MTK 原命名规范分析**

从 `.mcp` 中提取的 fromELF 输出文件名：

```
-output#SDK_主应用_BSS.EXE
```

命名语义拆解：

| 组成部分 | 含义 | 技术作用 |
|----------|------|----------|
| `SDK_` | MTK SDK 标准前缀 | 标识这是 MTK SDK 工具链生成的应用，可能被某些工具或加载器用于识别 |
| `主应用` (或项目名) | 应用标识 | 人类可读的应用名称 |
| `_BSS` | BSS 段元数据标记 | **关键**：标识此 .bin 文件包含 BSS 段信息，OS 加载器需调用 `GetBSSSpace()` 来分配 ZI 内存 |
| `.EXE` | 可执行文件扩展名 | ADS1.2 时代的默认扩展名（非 Windows PE 格式，实际是纯 binary） |



### **2.7.2 命名规范的技术重要性**

> [!WARNING]
> **文件名可能不仅仅是"标识"，而是加载协议的一部分！**

**可能的技术依赖**：

1. **扩展名检查**：
   - 某些文件系统浏览器（如 FMM）可能只列出特定扩展名的文件
   - UNISOC 平台的 DAP 加载器可能硬编码检查 `.EXE` 或 `.bin`

2. **`_BSS` 后缀语义**：
   - 加载器可能根据 `_BSS` 后缀判断是否需要为 BSS 分配独立内存
   - 如果缺失，可能导致：
     - BSS 段不被清零
     - `GetBSSSpace()` 返回值被忽略
     - 全局变量初始化异常

3. **`SDK_` 前缀**：
   - 可能被 MTK 特定工具链（如烧录工具、升级工具）识别
   - UNISOC 平台可能不依赖此前缀（非 MTK 生态）



### **2.7.3 Hello World 的三种命名方案**

> [!NOTE]
> **以下方案 A/B/C 仅是常见场景的参考示例，不是限定选项。**
> 
> `PROJ_NAME` 和 `OUT_EXT` 是完全可配置的变量，开发者可根据实际加载器要求自由修改。
> 例如：如果测试发现加载器必须识别 `.dap` 扩展名，直接改 `SET OUT_EXT=.dap` 即可。



#### **方案 A：完全兼容 MTK 命名（推荐首次测试）**

```bat
SET PROJ_NAME=SDK_HelloWorld_BSS
SET OUT_EXT=.EXE
```

**优点**：
- ? 与 MTK 原工程完全一致
- ? 最大化兼容性（如果 UNISOC 加载器继承了 MTK 的命名检查逻辑）
- ? `_BSS` 后缀语义清晰

**缺点**：
- ?? `.EXE` 扩展名可能引起混淆（不是 Windows 可执行文件）
- ?? `SDK_` 前缀可能不适用于非 MTK 平台



#### **方案 B：保留语义，现代化扩展名（推荐）**

```bat
SET PROJ_NAME=hello_world_BSS
SET OUT_EXT=.bin
```

**优点**：
- ? 保留 `_BSS` 后缀语义（关键！）
- ? `.bin` 扩展名更直观
- ? 去掉 `SDK_` 前缀（UNISOC 平台可能不需要）

**缺点**：
- ?? 如果加载器严格检查扩展名为 `.EXE`，会失败

**适用场景**：UNISOC 平台的 DAP 加载器已经过验证，不依赖 MTK 特定命名



#### **方案 C：完全简化（仅验证编译链路）**

```bat
SET PROJ_NAME=hello_world
SET OUT_EXT=.bin
```

**优点**：
- ? 命名清晰简洁
- ? 便于本地开发调试

**缺点**：
- ? **丢失 `_BSS` 语义标记**，可能导致：
  - 加载器忽略 BSS 段分配
  - 全局变量初始化失败
- ? 不符合 DAP 生态规范

**适用场景**：**仅用于验证编译工具链是否正常工作，不用于实际加载测试**



### **2.7.4 本 Memo 采用的方案**

**默认使用方案 B**（`hello_world_BSS.bin`），理由：

1. **保守起见保留 `_BSS` 后缀**：这是 DAP 框架的关键语义，不应随意丢弃
2. **现代化扩展名**：`.bin` 更符合业界惯例
3. **去掉 `SDK_` 前缀**：UNISOC 平台可能不依赖 MTK 特定标识

**但在 `build_hello.bat` 脚本中提供三种方案的注释选项**，便于根据实际测试结果切换。



### **2.7.5 验证步骤**

**首次测试时建议：**

1. **同时生成两个版本**：
   ```bat
   fromelf -bin -output out\hello_world_BSS.bin out\hello_world.axf
   fromelf -bin -output out\SDK_HelloWorld_BSS.EXE out\hello_world.axf
   ```

2. **分别推送到手机并测试**，观察：
   - FMM 文件列表是否显示
   - DAP Execute 是否能识别
   - 加载后 trace 输出是否正常
   - 全局变量是否正确初始化

3. **根据测试结果确定最终命名规范**，并在后续 SDK 开发中统一使用。



------



## **3. 编译脚本 `build_hello.bat`**



### **3.1 完整批处理脚本**

> [!IMPORTANT]
> 此脚本假设 ARM ADS1.2 或 RVCT 工具链已安装且 `armcc`、`armasm`、`armlink`、`fromelf` 在 PATH 中。
> 如实际使用 RVCT 2.x/3.x/4.x，命令相同，仅需确认路径。

```bat
@echo off
REM ============================================================================
REM  build_hello.bat — Hello World DAP 独立 .bin 编译脚本（支持命令行参数）
REM
REM  用法:
REM    build_hello.bat [输出文件名] [扩展名] [clean]
REM
REM  参数说明:
REM    [输出文件名]  可选，指定输出文件名（不含扩展名），默认 hello_world_BSS
REM    [扩展名]      可选，指定输出文件扩展名（含 .），默认 .bin
REM    clean         清除输出目录
REM
REM  示例:
REM    build_hello.bat
REM      → 使用默认配置: out\hello_world_BSS.bin
REM
REM    build_hello.bat my_app_BSS
REM      → 自定义文件名: out\my_app_BSS.bin (扩展名仍用默认)
REM
REM    build_hello.bat SDK_Test_BSS .EXE
REM      → 完全自定义: out\SDK_Test_BSS.EXE
REM
REM    build_hello.bat clean
REM      → 清除 out\ 目录
REM
REM    build_hello.bat my_app .bin clean
REM      → 先清除，再编译为 out\my_app.bin
REM
REM  编译器: armcc  (ARM ADS1.2 / RVCT)
REM  编译选项来源: MTKcompilebin/MTK_APP.mcp (完整提取)
REM ============================================================================

REM ==================== 项目配置区 ====================

REM ---- 命令行参数解析 ----
REM 支持通过命令行参数动态指定输出文件名和扩展名，避免每次都要编辑脚本
REM
REM 参数映射:
REM   %1 = 输出文件名（不含扩展名），如 "my_app_BSS"
REM   %2 = 输出文件扩展名（含 .），如 ".bin" 或 ".EXE"
REM   任意参数为 "clean" = 触发清除模式
REM
REM 如果不提供参数，使用下面的默认值

REM ---- 默认输出文件名配置 ----==================

REM ---- 输出文件命名策略 ----
REM 【核心设计】PROJ_NAME 和 OUT_EXT 是完全可配置的变量
REM           开发者可根据实际加载器要求自由修改，不限于下面的方案 A/B/C
REM           这三个方案只是常见场景的参考，不是限定选项
REM
REM 【重要】文件名不仅是标识，可能是加载协议的一部分！
REM
REM 【MTK 原命名规范】SDK_主应用_BSS.EXE
REM   - SDK_       : MTK SDK 标识（UNISOC 平台可能不需要）
REM   - _BSS       : ★关键★ 标识包含 BSS 段元数据，OS 加载器据此调用 GetBSSSpace()
REM   - .EXE       : ADS1.2 历史遗留扩展名（实际是 binary，非 Windows PE）
REM
REM 【三种命名方案】选择一个，注释掉其他两个：
REM
REM 方案 A：完全兼容 MTK（推荐首次测试）
REM SET PROJ_NAME=SDK_HelloWorld_BSS
REM SET OUT_EXT=.EXE
REM
REM 方案 B：保留语义 + 现代化扩展名（默认推荐）
SET DEFAULT_PROJ_NAME=hello_world_BSS
SET DEFAULT_OUT_EXT=.bin
REM
REM 方案 C：完全简化（仅验证编译链路，不用于加载测试）
REM SET DEFAULT_PROJ_NAME=hello_world
REM SET DEFAULT_OUT_EXT=.bin
REM
REM 风险提示：
REM   - 如果丢失 _BSS 后缀，加载器可能不为 BSS 段分配内存
REM   - 如果加载器硬编码检查 .EXE 扩展名，改用 .bin 会失败
REM   - 建议首次测试时生成两个版本对比验证

REM ---- 应用命令行参数（如果提供）----
REM 优先级：命令行参数 > 默认值
SET PROJ_NAME=%DEFAULT_PROJ_NAME%
SET OUT_EXT=%DEFAULT_OUT_EXT%

REM 检查 %1 是否为 clean
IF /I "%1"=="clean" GOTO :PARSE_CLEAN
REM 检查 %2 是否为 clean
IF /I "%2"=="clean" GOTO :PARSE_CLEAN
REM 检查 %3 是否为 clean
IF /I "%3"=="clean" GOTO :PARSE_CLEAN

REM 如果 %1 非空且不是 clean，用作文件名
IF NOT "%1"=="" (
    IF /I NOT "%1"=="clean" SET PROJ_NAME=%1
)

REM 如果 %2 非空且不是 clean，用作扩展名
IF NOT "%2"=="" (
    IF /I NOT "%2"=="clean" SET OUT_EXT=%2
)

REM 跳过清除模式标记，继续正常编译流程
GOTO :AFTER_PARAM_PARSE

:PARSE_CLEAN
SET DO_CLEAN=1
REM 如果 %1 不是 clean，仍然用作文件名
IF /I NOT "%1"=="clean" (
    IF NOT "%1"=="" SET PROJ_NAME=%1
)
REM 如果 %2 不是 clean，仍然用作扩展名
IF /I NOT "%2"=="clean" (
    IF NOT "%2"=="" SET OUT_EXT=%2
)

:AFTER_PARAM_PARSE

REM ---- 其他配置 ----

SET SRC_DIR=src
SET INC_DIR=inc
SET OUT_DIR=out
SET TARGET_CPU=ARM7EJ-S

echo ============================================================
echo  Building DAP Hello World .bin
echo  Output   : %OUT_DIR%\%PROJ_NAME%%OUT_EXT%
echo  Compiler : %CC%
echo  CPU      : %TARGET_CPU%
echo ============================================================
echo.

REM ---- 编译器标志（完整来自 ADS1.2 MTK_APP.mcp 项目文件 MTK_APP target） ----
REM
REM  【armcc 选项说明】
REM  -O1                : 优化等级 1（.mcp 原文 -O.level=1）
REM  -cpu ARM7EJ-S      : 目标处理器（ARMv5TEJ）
REM  -apcs /ropi        : RO 段位置无关（仅 RO，编译器不开 RWPI）
REM  -zc                : char 强制为 signed（ADS1.2 兼容关键）
REM  -zo                : 每个函数独立代码段（便于 linker 死代码消除）
REM  -fy                : 兼容老版本浮点行为
REM  -split_ldm         : 拆分 LDM/STM 指令（减少中断延迟）
REM  -auto_float_constants : 自动浮点常量提升
REM  -g+                : 生成调试信息（发布版改 -g-）
REM
REM  【预处理宏（全部来自 .mcp）】
REM  -D__S3C44B0X__                  : 原始目标板标识（可按需替换）
REM  -D__OPTIMISE_LEVEL=1            : 优化等级宏
REM  -D__FEATURE_SIGNED_CHAR         : signed char 标记
REM  -D__TARGET_ARCH_5TE             : 架构 = ARMv5TE
REM  -D__TARGET_CPU_ARM7EJ_S         : CPU = ARM7EJ-S
REM  -D__TARGET_FEATURE_DSPMUL       : DSP 乘法扩展
REM  -D__TARGET_FEATURE_DOUBLEWORD   : 双字操作支持
REM  -D__APCS_ROPI                   : ROPI 模式标记
REM
REM  【armlink 选项说明】
REM  -armlib    : 链接 ARM 标准 C 库（sprintf 等）
REM  -reloc     : 保留重定位信息
REM  -nodebug   : 剥离调试信息（减小 .bin）
REM  -rwpi      : 链接器层面启用 RWPI（编译器层面未开）
REM
REM  【注意 - ADS1.2 迁移风险】
REM    1. 结构体对齐：ADS1.2 默认可能与 RVCT 不同，需要 #pragma pack
REM    2. 编译器预定义宏：__ARMCC_VERSION 值不同
REM    3. 隐式函数声明：ADS1.2 更宽容，armcc 可能报 warning/error
REM    4. char 的符号：已通过 -zc 强制 signed，但需验证一致性
REM    5. RWPI 行为：编译器不开 /rwpi，RW 重定位靠代码中 AddrRelocation()

SET CC=armcc
SET AS=armasm
SET LD=armlink
SET ELF2BIN=fromelf

REM ---- armcc 编译标志 ----
SET CFLAGS=-c -O1 -cpu %TARGET_CPU% -apcs /ropi -zc -zo -fy -split_ldm -auto_float_constants -g+ -I %INC_DIR% -D__S3C44B0X__ -D__OPTIMISE_LEVEL=1 -D__FEATURE_SIGNED_CHAR -D__TARGET_ARCH_5TE -D__TARGET_CPU_ARM7EJ_S -D__TARGET_FEATURE_DSPMUL -D__TARGET_FEATURE_DOUBLEWORD -D__APCS_ROPI

REM ---- armasm 汇编标志 ----
SET ASFLAGS=-cpu %TARGET_CPU% -apcs /ropi -keep -g

REM ---- armlink 链接标志 ----
SET LDFLAGS=-entry Entry -ro-base 0x00000000 -first Entry.o(.constdata) -ropi -rwpi -armlib -reloc -nodebug -info totals,unused,veneers,sizes -map -symbols -xref -callgraph -list %OUT_DIR%\%PROJ_NAME%.lst

REM ---- fromelf 转换标志 ----
SET ELFFLAGS=-bin -output %OUT_DIR%\%PROJ_NAME%%OUT_EXT%

REM ---- 清除命令 ----
IF "%DO_CLEAN%"=="1" (
    echo [CLEAN] Removing output directory...
    if exist %OUT_DIR% rd /s /q %OUT_DIR%
    echo [CLEAN] Done.
    REM 如果只是清除（没有其他参数），退出
    IF "%1"=="clean" IF "%2"=="" goto :EOF
)

REM ---- 创建输出目录 ----
if not exist %OUT_DIR% mkdir %OUT_DIR%

echo ============================================================
echo  Building DAP Hello World .bin
echo  Compiler : %CC%
echo  CPU      : %TARGET_CPU%
echo  Flags    : %CFLAGS%
echo ============================================================
echo.

REM ---- Step 1: 汇编 Start.s ----
echo [ASM ] %SRC_DIR%\Start.s
%AS% %ASFLAGS% -o %OUT_DIR%\Start.o %SRC_DIR%\Start.s
if errorlevel 1 (
    echo [FAIL] Assembly of Start.s failed!
    goto :ERROR
)

REM ---- Step 2: 编译 C 源文件 ----
echo [CC  ] %SRC_DIR%\Entry.c
%CC% %CFLAGS% -o %OUT_DIR%\Entry.o %SRC_DIR%\Entry.c
if errorlevel 1 (
    echo [FAIL] Compilation of Entry.c failed!
    goto :ERROR
)

echo [CC  ] %SRC_DIR%\Main.c
%CC% %CFLAGS% -o %OUT_DIR%\Main.o %SRC_DIR%\Main.c
if errorlevel 1 (
    echo [FAIL] Compilation of Main.c failed!
    goto :ERROR
)

REM ---- Step 3: 链接 ----
echo [LINK] Linking %PROJ_NAME%.axf ...
%LD% %LDFLAGS% -o %OUT_DIR%\%PROJ_NAME%.axf %OUT_DIR%\Entry.o %OUT_DIR%\Main.o %OUT_DIR%\Start.o
if errorlevel 1 (
    echo [FAIL] Linking failed!
    goto :ERROR
)

REM ---- Step 4: 转换为 .bin ----
echo [BIN ] Converting to %PROJ_NAME%.bin ...
%ELF2BIN% %ELFFLAGS% %OUT_DIR%\%PROJ_NAME%.axf
if errorlevel 1 (
    echo [FAIL] fromelf conversion failed!
    goto :ERROR
)

echo ============================================================
echo  BUILD SUCCESS
echo  Output: %OUT_DIR%\%PROJ_NAME%%OUT_EXT%
echo  List  : %OUT_DIR%\%PROJ_NAME%.lst
echo ============================================================
goto :EOF

:ERROR
echo.
echo ============================================================
echo  BUILD FAILED — See errors above
echo ============================================================
exit /b 1
------



### **3.2 命令行参数使用示例**

脚本支持通过命令行参数动态指定输出文件名和扩展名，**无需每次都编辑脚本内容**。


#### **示例 1：使用默认配置**

```cmd
build_hello.bat
```

**效果**：
- 输出文件：`out\hello_world_BSS.bin`
- 使用脚本中 `DEFAULT_PROJ_NAME` 和 `DEFAULT_OUT_EXT` 的默认值


#### **示例 2：自定义输出文件名（扩展名用默认）**

```cmd
build_hello.bat my_custom_app_BSS
```

**效果**：
- 输出文件：`out\my_custom_app_BSS.bin`
- `PROJ_NAME` = `my_custom_app_BSS`（来自 %1）
- `OUT_EXT` = `.bin`（默认值）


#### **示例 3：完全自定义文件名和扩展名**

```cmd
build_hello.bat SDK_HelloWorld_BSS .EXE
```

**效果**：
- 输出文件：`out\SDK_HelloWorld_BSS.EXE`
- `PROJ_NAME` = `SDK_HelloWorld_BSS`（来自 %1）
- `OUT_EXT` = `.EXE`（来自 %2）


#### **示例 4：清除输出目录**

```cmd
build_hello.bat clean
```

**效果**：
- 删除整个 `out\` 目录
- **不执行编译**


#### **示例 5：清除 + 重新编译（自定义文件名）**

```cmd
build_hello.bat test_app .bin clean
```

**效果**：
- 先删除 `out\` 目录
- 再编译为 `out\test_app.bin`

**参数顺序灵活**：`clean` 可以放在任意位置（%1、%2、%3），脚本会自动识别


#### **示例 6：测试时同时生成多个版本**

```bat
REM 生成 .bin 版本
build_hello.bat hello_world_BSS .bin

REM 生成 .EXE 版本（兼容测试）
build_hello.bat SDK_HelloWorld_BSS .EXE

REM 生成简化版本（仅验证编译链路）
build_hello.bat hello_world .bin
```

**效果**：
- `out\hello_world_BSS.bin`
- `out\SDK_HelloWorld_BSS.EXE`（后续编译会覆盖前一个的 `.axf` 和 `.lst`，但 `.bin/.EXE` 同时存在）
- `out\hello_world.bin`



------



### **3.3 脚本执行步骤总结**

| 步骤 | 命令 | 输入 | 输出 |
|------|------|------|------|
| 1. ASM | `armasm -cpu ARM7EJ-S -apcs /ropi -keep -g` | `Start.s` | `Start.o` |
| 2. CC | `armcc -c -O1 -cpu ARM7EJ-S -apcs /ropi -zc -zo -fy -split_ldm ...` + 全部 `-D` 宏 | `Entry.c` | `Entry.o` |
| 3. CC | 同上 | `Main.c` | `Main.o` |
| 4. LINK | `armlink -entry Entry -ro-base 0x00000000 -first Entry.o(.constdata) -ropi -rwpi -armlib -reloc -nodebug ...` | `*.o` | `hello_world.axf` |
| 5. BIN | `fromelf -bin` | `.axf` | `hello_world.bin` |



------



## **4. 关键技术点与已知风险**



### **4.1 从 ADS1.2 迁移到 armcc/RVCT 的已知问题**

> [!WARNING]
> 以下问题在过去 DAP 从 MTK 移植时已经遇到过，必须在 Hello World 阶段验证并解决。

| # | 问题 | 表现 | 解决方案 |
|---|------|------|----------|
| 1 | **结构体对齐差异** | `sizeof(TApplication)` 在 ADS1.2 和 RVCT 中不同，导致 OS 加载器读取字段偏移错误 | 在 `TApplication` 定义前后加 `#pragma pack(1)` / `#pragma pack()`，或使用 `__packed` 属性 |
| 2 | **编译器预定义宏** | ADS1.2 定义 `__ARMCC_VERSION` 值较低，某些条件编译分支可能走错 | 在 `def.h` 中显式定义 `#define DAP_COMPILER_ARMCC`，不依赖版本号 |
| 3 | **char 默认符号** | ADS1.2 中 `char` 可能为 `signed`，RVCT 中可能为 `unsigned`，影响字符串比较 | 编译时加 `-zc` 强制 `signed char`，或显式使用 `_CHAR8` / `_UCHAR8` |
| 4 | **隐式函数声明** | ADS1.2 容忍隐式声明，RVCT 默认 warning，更严格模式下 error | 确保所有函数有显式原型声明 |
| 5 | **Veneer 生成** | ARM/Thumb interworking 时 linker 自动插 veneer，可能改变代码段大小 | 关注 `.lst` 文件中 veneer 信息，确认不影响 TApplication 偏移 |



### **4.2 .bin 文件内存布局**

```
+0x0000  ┌──────────────────────────────┐
         │  TApplication 描述符 (const) │  ← -first Entry.o(.constdata)
         │  - MTKExeTag "MTK_Exe"       │
         │  - Entry 函数指针            │
         │  - TagCheckSum               │
         │  - OSAPI / Register / DelAPI │  ← OS 加载时填入
         │  - LoadAddr                  │  ← OS 加载时填入实际地址
         │  - Name / Data              │
         │  - GetBSSSpace              │
         │  - VersionMark 0x55AA0001   │
         ├──────────────────────────────┤
         │  .text (代码段)              │  ← RO, 位置无关
         │  - Entry()                   │
         │  - Main()                    │
         │  - GetBssStartAddr()         │
         │  - GetBssEndAddr()           │
         │  - FindInterface() 等       │
         ├──────────────────────────────┤
         │  .data (已初始化数据)         │  ← RW, 需要重定位
         │  - UserInputSN              │
         ├──────────────────────────────┤
         │  .bss (未初始化数据)          │  ← ZI, 运行时清零
         └──────────────────────────────┘
```

> [!IMPORTANT]
> **地址重定位**：因为使用 ROPI/RWPI，代码中所有对全局变量的访问必须通过 `AddrRelocation()` 函数。
> 这是 DAP 框架的核心约束——直接取全局变量地址会得到链接时地址（基于 0x0），而非运行时实际地址。



### **4.3 OS 加载器的预期行为**

1. OS 从文件系统读取 `.bin` 文件到预分配的内存区域
2. 读取偏移 0x0 处的 `TApplication` 结构体
3. 验证 `MTKExeTag` == "MTK_Exe" 且 `TagCheckSum` 正确
4. 将实际加载地址写入 `LoadAddr` 字段
5. 将 OS API 查找/注册/删除函数指针写入 `OSAPI` / `Register` / `DelAPI` 字段
6. 为 BSS 段分配 `GetBSSSpace()` 返回的大小的内存
7. 调用 `Entry(Data, Params, CMD)` 启动应用



------



## **5. 验证计划**



### **5.1 编译验证（首要目标）**

| # | 验证项 | 预期结果 | 判定标准 |
|---|--------|----------|----------|
| 1 | `build_hello.bat` 执行无 error | 生成 `hello_world.bin` | 脚本返回 0 |
| 2 | `.lst` 文件中 `TApplication` 在 offset 0x0 | `Entry.o(.constdata)` 起始于 `0x00000000` | 查看 lst 中 Image Symbol Table |
| 3 | 无 veneer 警告或 veneer 不影响头部布局 | veneer 仅出现在 .text 段 | 查看 lst 中 veneers info |
| 4 | `.bin` 文件大小合理 | < 4KB（Hello World 应极小） | `dir out\hello_world.bin` |
| 5 | `.bin` 文件头部 8 字节为 "MTK_Exe\0" | 二进制验证 | `xxd` 或十六进制查看器 |



### **5.2 运行验证（后续目标）**

- 将 `hello_world.bin` 推送到手机文件系统
- 通过 FMM → 选择 .bin → DAP Execute 触发加载
- 在串口 trace 中观察输出：`=== Hello World from DAP .bin! ===`



------



## **6. 后续扩展路线**

| 阶段 | 内容 | 依赖 |
|------|------|------|
| **Phase 1** (本 memo) | Hello World: trace 输出验证编译链路 | armcc 环境可用 |
| **Phase 2** | 加入 OSAPILists：动态绑定 OS API 表 | Phase 1 通过 |
| **Phase 3** | 加入 MainForm：显示一个简单列表界面 | Phase 2 通过 + OS 端 API 注册完成 |
| **Phase 4** | 完整 SDK 模板：包含 GBK 编码、资源引用 | Phase 3 通过 |



------



## **7. 待确认事项（提问清单）**

> [!CAUTION]
> 以下事项需要工程师确认后才能开始执行。

1. **armcc 工具链路径**：当前开发环境中 `armcc` / `armasm` / `armlink` / `fromelf` 的安装路径是什么？是否已在 PATH 中？是 ADS1.2 原版还是 RVCT？

2. **目标 CPU**：Hello World .bin 的 `-cpu` 参数应设为什么？UNISOC T127 使用的是什么 ARM 核心？（如 ARM926EJ-S、Cortex-A5 等）

3. **TApplication 结构体兼容性**：当前 UNISOC 平台的 DAP 加载器（`DAP_Core_Loader` / FMM 集成）是否已实现了对 TApplication 头部的解析？如果尚未实现，Hello World 验证将仅限于编译链路，运行验证需等待加载器就绪。

4. **BSS/RW 处理**：在 UNISOC 上，OS 加载 .bin 后是否会为 BSS 段分配独立内存？还是加载器需要修改？

5. **输出文件命名规范**：UNISOC 平台的 DAP 加载器对 .bin 文件的命名是否有要求？
   - 是否必须使用 `.EXE` 扩展名（如 MTK 原工程）？还是 `.bin` 也可接受？
   - `_BSS` 后缀是否必需？（加载器是否据此判断需要调用 `GetBSSSpace()` 分配 ZI 内存）
   - `SDK_` 前缀是否有技术含义？（UNISOC 平台是否沿用 MTK 的命名检查逻辑）
   - 建议首次测试时生成 `hello_world_BSS.bin` 和 `SDK_HelloWorld_BSS.EXE` 两个版本对比验证

6. **输出位置确认**：`hello_world_BSS.bin` 最终应推送到手机文件系统的哪个路径？（如 `D:/DAP/` 或其他）



------



### **一句话总结**

> **本轮目标是一个 "能编译、能输出 .bin、头部结构正确" 的最小 Hello World，用来验证整条 armcc 独立编译链路在脱离 ADS1.2 IDE 后仍然可行。**



