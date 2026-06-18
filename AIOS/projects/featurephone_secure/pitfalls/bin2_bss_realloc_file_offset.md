# Pitfall: BIN2 BSS 重分配路径文件读取偏移错误

**Date:** 2026-03-11
**Memo:** TM-22
**Severity:** Critical（跳入无效地址导致蓝屏 ASSERT）

## Symptom

BIN2 文件签名验证通过后，跳转到 `entry_func` 时蓝屏：
```
Exception at 0x83f2dfa8 ASSERT(Undefined exception handler!)
```

Logel trace 显示 `TagCheckSum=0x00000000, VersionMark=0x00000000` — Application 结构体数据全部错误。

## Root Cause

`DAP_Loader_unisoc.c` 的 BSS 重分配路径（sdk_version ≥ 1）中：

```c
// 重分配后重新读取文件
DAP_FileSeek(file_handle, 0, SFS_SEEK_BEGIN);  // ⚠️ 从文件开头读！
DAP_FileRead(file_handle, Running_AP, file_size, &bytes_read);
```

- BIN2 文件开头是 BIN2 header(48字节) + signature(64字节)
- `file_size` 已被减小为 payload 大小（572字节）
- 结果读到的前 112 字节是 BIN2 头部，不是 BIN1 的 TApplication 头部
- `Application->Entry` 等字段是 BIN2 格式的二进制数据 → 跳转到垃圾地址

## Fix

```c
if (is_bin2) {
    DAP_FileSeek(file_handle, bin2_payload_off, SFS_SEEK_BEGIN);  // 跳过 BIN2 头部
} else {
    DAP_FileSeek(file_handle, 0, SFS_SEEK_BEGIN);
}
```

## Prevention

**BIN2 集成时，任何涉及文件重读的路径都必须考虑 BIN2 偏移：**

1. 重读文件前检查 `is_bin2` 标记
2. BIN2 文件的有效数据从 `BIN2_PAYLOAD_OFFSET`（112）开始
3. `file_size` 在 BIN2 unwrap 后已被调整为 payload 大小，不是原始文件大小
4. 盘点所有 `DAP_FileSeek` + `DAP_FileRead` 调用点，确认 BIN2 兼容性

## 参考

- 修复文件：`Third-party/DAP/platform/unisoc/DAP_Loader_unisoc.c`
- 关联 Pitfall：`bin2_pointer_offset_heap_corruption.md`
