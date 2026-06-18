# Session Log: TM-26 — Bindfile Export to Device Filesystem

**Date:** 2026-03-12
**Memo:** TM-26 (Phase 1B)
**Outcome:** SUCCESS
**Duration:** ~4 hours (including 4 debug iterations)

---

## Summary

实现了 BindingID 以 JSON 格式导出到设备文件系统 (`D:\DAP\device.bind`)，PC 可通过 USB 直接读取。

## Files Created

| File | Type | Description |
|------|------|-------------|
| `Third-party/DAP/security/device_bindfile.h` | Header | `device_bindfile_generate()` / `device_bindfile_exists()` API |
| `Third-party/DAP/security/device_bindfile.c` | Source | 封装 bindfile 路径 + TM26 trace + exists 检查 |
| `AIOS/docs/architecture/device_binding_phase1b.md` | Doc | Phase 1B 架构文档 |
| `AIOS/docs/pitfalls/sfs_extern_declarations.md` | Pitfall | SFS extern 声明 vs 平台头文件 |
| `AIOS/tools/extract_bindingid.py` | Tool | PC 端从 Logel 提取 BindingID 备选工具 |
| `AIOS/quality_reports/specs/TM-26_spec.md` | Spec | 冻结规格 |

## Files Modified

| File | Changes |
|------|---------|
| `Third-party/DAP/security/device_binding.c` | `#include platform header` 替代 extern SFS 声明；SFS_HANDLE 类型修正 |
| `Third-party/DAP/security/device_identity_debug.c` | `*#3472#` 菜单触发 bindfile 生成 + BindingID/Bind 状态显示 |
| `Third-party/DAP/platform/unisoc/DAP_Loader_unisoc.c` | DAP_LoaderInit 和 BIN2 执行时调用 `device_bindfile_generate()` |
| `make/dap/dap.mk` | 添加 `device_bindfile.c` 到 SOURCES |
| `AIOS/MEMORY.md` | ADR-009 + bindfile 路径 + SFS pitfall |
| `AIOS/registry/apis.yaml` | 注册 `device_bindfile_generate`, `device_bindfile_exists` |

## Key Decisions

1. **ADR-009:** Bindfile 路径为 `D:\DAP\device.bind`（非 Filearray — SFS 无法直接访问 Filearray）
2. 安全模块必须 `#include` 平台头文件而非 `extern` 声明 SFS 函数

## Major Pitfall Encountered

**SFS extern 声明导致所有常量和类型错误**, 经历 4 次迭代才定位：
1. `SFS_INVALID_HANDLE` 定义为 `0xFFFFFFFF`，实际平台定义为 `0`
2. `SFS_MODE_CREATE_ALWAYS` 值错误，应使用 `SFS_MODE_OPEN_ALWAYS`
3. SFS 函数返回类型 `SFS_HANDLE`（非 `void*`）
4. `Filearray` 路径 SFS 无法访问，需使用 `D:\DAP\`

**修复：** `#include "../platform/unisoc/DAP_OSAssociated_unisoc.h"`

## Verification Results

- ✅ `*#3472#` 触发 → `D:\DAP\device.bind` 生成
- ✅ Logel trace: `tm26_generate_bindfile ENTER` → `.bind written OK (131 bytes)`
- ✅ BindingID 交叉验证：Logel `tm25_id` == `device.bind` `binding_id` == `f7bbf4ca226c852b92d67ad1fb4f3217`
- ✅ JSON 格式正确，字段完整
