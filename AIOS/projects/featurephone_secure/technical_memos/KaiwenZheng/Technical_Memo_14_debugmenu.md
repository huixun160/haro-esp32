# **Technical Memo**







## **DeviceSecret Debug Menu – Dial Code Entry**





**Project:** AIOS / Mocor Platform

**Chipset:** Unisoc UMS9117

**OS:** Mocor RTOS

**Purpose:** DeviceSecret Root-of-Trust verification

**Priority:** High

**Author:** Architecture



------





# **1. 背景**





当前系统已经实现 DeviceSecret Root-of-Trust：

```
DeviceSecret (256-bit)
     ↓
首次开机生成
     ↓
写入 UserNV (item 0x0001)
     ↓
后续开机读取
     ↓
CRC 校验
```

DeviceSecret 将用于未来安全体系：

```
DeviceSecret
     ↓
BIN2 验签
     ↓
APP Store Device Binding
     ↓
License / DRM
```

当前验证方式依赖 **Logel 日志工具**，存在问题：



- 依赖 PC
- 工程调试效率低
- 现场无法快速验证
- 无法在设备端直接确认 Root-of-Trust 状态





因此需要实现 **设备端 Debug Menu**。



------





# **2. 目标**





通过 **拨号界面输入工程码** 进入 Security Debug 页面。



入口流程：

```
Dialer
  ↓
输入工程码
  ↓
*#3472#
  ↓
Security Debug Menu
  ↓
Device Identity Debug Page
```

该页面用于验证：



1. DeviceSecret 是否首次生成
2. DeviceSecret 是否成功写入 UserNV
3. 后续开机是否读取同一 Secret
4. CRC 校验是否成功
5. Fingerprint 是否稳定





注意：

```
禁止显示 DeviceSecret 明文
仅允许显示 Fingerprint
```



------





# **3. 工程码入口设计**







## **工程码**



```
*#3472#
```

说明：

```
3472 = D I A S
Device Identity And Security
```



------





# **4. 拨号界面 Hook**





需要在 **Dialer 输入处理逻辑**中增加检测。



典型实现位置：

```
mmi_dialer.c
或
mmi_idle.c
或
mmi_dialpad.c
```

当检测到输入序列：

```
*#3472#
```

触发：

```
LaunchSecurityDebugMenu()
```



------





# **5. 工程码检测逻辑**





示例伪代码：

```
BOOLEAN CheckSecurityDebugCode(char *input)
{
    if (strcmp(input, "*#3472#") == 0)
        return TRUE;

    return FALSE;
}
```

在 Dialer 输入处理流程中：

```
void Dialer_OnInput(char *input)
{
    if (CheckSecurityDebugCode(input))
    {
        LaunchSecurityDebugMenu();
        return;
    }

    NormalDialProcess(input);
}
```



------





# **6. Debug Menu 结构**





Debug Menu 页面结构：

```
Security Debug
 ├─ Device Identity
 ├─ NV Debug
 └─ System Security
```

当前只需要实现：

```
Device Identity
```



------





# **7. Device Identity Debug Page**





页面显示内容：

```
Device Identity Debug
--------------------------------

Init Called        : YES

Init Result        : GENERATED_NEW
                     LOADED_FROM_NV
                     CRC_FAIL_REGENERATED

UserNV Item        : 0x0001

NV Read Status     : OK / FAIL
NV Write Status    : OK / FAIL

CRC Status         : OK / FAIL

Fingerprint        : 12AB34CD-89EF5678

Generation Count   : 1

Last Action        : FIRST_BOOT_GEN
```



------





# **8. Debug API 设计**





新增只读 API：



文件：

```
device_identity_debug.h
```

接口：

```
BOOLEAN device_secret_is_initialized(void);

uint64 device_secret_get_fingerprint(void);

int device_secret_get_last_status(void);

BOOLEAN device_secret_get_last_crc_ok(void);

int device_secret_get_generation_count(void);

int device_secret_get_last_nv_read_ret(void);

int device_secret_get_last_nv_write_ret(void);
```



------





# **9. Fingerprint 算法**





Fingerprint 用于脱敏展示。



算法：

```
256-bit secret
   ↓
XOR folding
   ↓
64-bit fingerprint
```

示例：

```
uint64 fingerprint;

fp_hi = secret[0..7] XOR secret[8..15];
fp_lo = secret[16..23] XOR secret[24..31];

fingerprint = (fp_hi << 32) | fp_lo;
```

最终显示：

```
%016llX
```



------





# **10. Debug Page 示例代码**



```
void DeviceIdentityDebug_Show(void)
{
    uint64 fp = device_secret_get_fingerprint();
    BOOLEAN crc = device_secret_get_last_crc_ok();

    int status = device_secret_get_last_status();
    int gen_cnt = device_secret_get_generation_count();

    UI_Print("Init Result : %d", status);
    UI_Print("CRC Status  : %s", crc ? "OK" : "FAIL");
    UI_Print("Fingerprint : %016llX", fp);
    UI_Print("Gen Count   : %d", gen_cnt);
}
```



------





# **11. 安全规则（必须遵守）**





以下规则必须严格执行。





### **禁止输出 Secret 明文**





禁止：

```
printf(secret)
log(secret)
dump(secret)
```

仅允许输出：

```
fingerprint
```



------





### **禁止暴露 Secret Pointer**





禁止对 Debug Menu 或 DAP 注册：

```
device_secret_get_ptr()
```



------





### **Debug API 不允许注册到 DAP**





Debug API 仅供：

```
System / MMI
```

调用。



禁止注册：

```
InterfaceRegister
DAP SDK
Third Party Apps
```



------





# **12. 验证流程**





工程师必须验证以下三种情况。



------





## **Case 1 首次烧机**





步骤：

```
烧录 PAC
开机
输入 *#3472#
进入 Device Identity Debug
```

预期：

```
Init Result   = GENERATED_NEW
CRC Status    = OK
Gen Count     = 1
Fingerprint   = X
```



------





## **Case 2 正常重启**





步骤：

```
关机
开机
输入 *#3472#
```

预期：

```
Init Result   = LOADED_FROM_NV
Fingerprint   = X (必须相同)
Gen Count     = 1
CRC Status    = OK
```



------





## **Case 3 删除 NV**





删除：

```
UserNV item 0x0001
```

重新开机。



预期：

```
Init Result   = GENERATED_NEW
Fingerprint   = Y (必须不同)
Gen Count     = 2
```



------





# **13. 编译控制**





Debug Menu 仅在工程版本启用：

```
#define SECURITY_DEBUG_MENU 1
```

量产版本：

```
#define SECURITY_DEBUG_MENU 0
```



------





# **14. 预期影响**





性能：

```
Boot Delay < 1ms
```

Flash 占用：

```
< 5 KB
```

风险：

```
0 (仅工程版本)
```



------





# **15. 交付物**





工程师需提交：



1. Dial Code Hook 实现

2. Security Debug Menu 页面

3. Device Identity Debug Page

4. Debug API 实现

   





------





# **16. 成功标准**





系统必须满足：

```
✓ 首次开机生成 DeviceSecret
✓ 写入 UserNV
✓ 重启复用
✓ CRC 校验成功
✓ Fingerprint 稳定
✓ 工程码成功进入 Debug 页面
```



------





# **关键架构原则**





Root-of-Trust 的成立必须满足：

```
生成
↓
持久化
↓
稳定读取
↓
可验证
```

该 Debug Menu 的唯一作用：



**在设备本地验证 Root-of-Trust 是否正确建立。**



------



