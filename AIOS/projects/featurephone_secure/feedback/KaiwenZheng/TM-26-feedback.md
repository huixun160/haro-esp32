# TM-26 Feedback — Bindfile Export to Device Filesystem

**Date:** 2026-03-12
**Outcome:** SUCCESS

## Completed Work

- [x] `device_bindfile.c/h` — 新增 bindfile 生成/检测 API
- [x] `device_identity_debug.c` — `*#3472#` 菜单触发 + BindingID 显示
- [x] `DAP_Loader_unisoc.c` — DAP_LoaderInit 和 BIN2 执行时自动生成
- [x] `dap.mk` — 添加 device_bindfile.c
- [x] Architecture doc, API registry, MEMORY.md
- [x] PC 端备选工具 `extract_bindingid.py`

## Incomplete Work

无。

## Blocking Issues Encountered

**SFS extern 声明导致常量和类型全部错误** — 4 次迭代才定位：

| 迭代 | 尝试 | 结果 |
|------|------|------|
| 1 | `Filearray/device.bind` 相对路径 | `write incomplete 0/131` |
| 2 | `D:\Filearray\device.bind` 绝对路径 | `write incomplete 0/131` |
| 3 | `D:\DAP\device.bind` + `SFS_MODE_OPEN_ALWAYS` | `SFS_CreateFile FAILED fh=0` |
| 4 | `#include` 平台头文件替代 extern | ✅ **成功** |

**根因：** `SFS_INVALID_HANDLE` 平台定义为 `0`，我们定义为 `0xFFFFFFFF`。

## Verification Status

✅ **全部通过** — BindingID Logel trace 与 device.bind 文件内容一致。

## Next Actions

- TM-27: PC packer 读取 device.bind → 生成 device-bound BIN2
