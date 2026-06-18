# BIN2 加密 Payload BSS 重分配后从文件重读密文

- **TM:** TM-28 (BIN2 Payload Encryption)
- **日期:** 2026-03-13
- **严重度:** 🔴 致命 (Prefetch Abort / 蓝屏)

## Symptom

加密 `.bin3` 文件在设备上验证通过（签名 OK、解密 OK、hash OK），但执行时蓝屏：
`Prefetch fault (IFSR: 0x00000005)! Fault address: 0x9eb903c4`

## Root Cause

`DAP_Loader_unisoc.c` 中 BSS 重分配流程：
1. `bin2_verify()` → 原地解密成功（RAM 中 payload 变为明文）
2. `DAP_MemFree(alloc_base)` → **释放含解密数据的缓冲区**
3. `DAP_MemAlloc(file_size + bss_size)` → 分配新缓冲区
4. `DAP_FileRead()` → **从文件重读 → 读回的是磁盘上的密文！**

CPU 尝试执行密文字节 → Prefetch Abort。

非加密 BIN2 不受影响（文件中本来就是明文）。

## Fix

对加密 BIN2，跳过文件重读，改用 `memcpy` 保留解密数据：
```c
if (bin2_encrypted) {
    void *decrypted_payload = Running_AP;
    Running_AP = DAP_MemAlloc(file_size + bss_size);
    memcpy(Running_AP, decrypted_payload, file_size);
    DAP_MemFree(alloc_base);
    alloc_base = Running_AP;
}
```

## Prevention Rule

**任何涉及"原地解密 → 释放缓冲区 → 重分配"的流程，必须确认重分配后的数据来源是解密后的明文，而非磁盘上的密文。**
