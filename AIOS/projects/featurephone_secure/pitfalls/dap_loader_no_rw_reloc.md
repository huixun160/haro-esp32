# Pitfall: DAP Loader 不做 RW 数据重定位

**ID:** dap_loader_no_rw_reloc
**TM:** TM-030
**Severity:** CRITICAL
**Date:** 2026-03-19

## 现象
APP .bin 中包含 `static` 变量 → 设备执行时立即蓝屏 (SCI_PAssert)

## 根因
DAP loader (`DAP_Loader_unisoc.c` L549-552) 只做 4 个字段的重定位：
- `Application->LoadAddr`
- `Application->OSAPI`
- `Application->Register`
- `Application->DelAPI`

**不处理** `.data` 或 `.bss` 段的地址修正。ARM 编译器生成的 RW 数据访问指令引用未重定位的绝对地址 → Prefetch/Data Abort。

## 约束
APP 代码（main.c）**禁止** 使用：
- `static` 变量
- 全局变量
- 任何初始化的 RW 数据

**允许**：
- 栈局部变量
- RO 字符串字面量（const data, 通过 -reloc 重定位）
- `dap_api.h` 宏（展开为纯栈操作）

## 预防
- `dap_api.h` 使用纯宏实现，零 static 变量
- `build.bat` findstr 扫描检查
- `dap_abi_v0.md` 中明确记录此约束
