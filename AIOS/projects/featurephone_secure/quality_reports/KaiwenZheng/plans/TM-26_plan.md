# Implementation Plan — TM-26 Bindfile Export to Device Filesystem

## Background

TM-25 completed BindingID derivation and Logel output. TM-26 adds the ability to **export BindingID as a JSON `device.bind` file** to the device filesystem, enabling PC tools to read the file for device-bound BIN2 packaging.

> [!IMPORTANT]
> **Key Finding:** `binding_export_bindfile()` already exists in `device_binding.c` and is already called from `DAP_LoaderInit()`. The current implementation writes to `D:\DAP\device.bind`. TM-26 requires migrating to `FileArray/device.bind` and adding proper wrapper module + trigger integration.

> [!WARNING]
> **Memo Discrepancy:** TM-26 references `*#3271#` as the debug code, but the existing codebase uses `*#3472#` (DISC = Device Identity Security Check). We will use the **existing `*#3472#`** debug code and its `MMIAPIENG_OpenSecurityDebugWin()` entry point, adding the bindfile generation call there.

---

## File Changes

| Action | File | Module | Description |
|--------|------|--------|-------------|
| CREATE | `Third-party/DAP/security/device_bindfile.h` | Security | Header: `device_bindfile_generate()`, `device_bindfile_exists()`, path constant |
| CREATE | `Third-party/DAP/security/device_bindfile.c` | Security | Wrapper: calls `binding_export_bindfile()` with correct path, adds TM26 traces |
| MODIFY | `Third-party/DAP/security/device_identity_debug.c` | Security | Add bindfile generation call in `MMIAPIENG_OpenSecurityDebugWin()` |
| MODIFY | `Third-party/DAP/platform/unisoc/DAP_Loader_unisoc.c` | Loader | Update bind path from `D:\DAP\` to `FileArray/`, add auto-gen check |
| MODIFY | `make/dap/dap.mk` | Build | Add `device_bindfile.c` to SOURCES |
| CREATE | `AIOS/docs/architecture/device_binding_phase1b.md` | Docs | Architecture documentation |
| MODIFY | `AIOS/MEMORY.md` | Docs | Add TM-26 key decisions |
| MODIFY | `AIOS/registry/apis.yaml` | Registry | Register new APIs |

---

## Proposed Changes

### Security Module — New Bindfile Wrapper

#### [NEW] [device_bindfile.h](file:///c:/zkwwork/featurephoneosreconstruction/Third-party/DAP/security/device_bindfile.h)

Define the TM-26 public API:
- `BOOLEAN device_bindfile_generate(void)` — derives BindingID and writes JSON to `FileArray/device.bind`
- `BOOLEAN device_bindfile_exists(void)` — checks if bindfile already exists on filesystem
- `BINDFILE_PATH` constant — the Unicode filepath for `FileArray/device.bind`

#### [NEW] [device_bindfile.c](file:///c:/zkwwork/featurephoneosreconstruction/Third-party/DAP/security/device_bindfile.c)

Implementation:
- `device_bindfile_generate()` calls existing `binding_export_bindfile()` with the FileArray path, adds TM26 trace output (`[bind] tm26_generate_bindfile`, `[bind] tm26_binding_id=...`, `[bind] tm26_file_written=FileArray/device.bind`)
- `device_bindfile_exists()` uses `SFS_CreateFile` with read-only mode to check existence (or `SFS_GetAttr`)
- No dynamic memory allocation (matches existing patterns)

---

### Debug Menu Integration

#### [MODIFY] [device_identity_debug.c](file:///c:/zkwwork/featurephoneosreconstruction/Third-party/DAP/security/device_identity_debug.c)

Add in `MMIAPIENG_OpenSecurityDebugWin()` after the existing `device_binding_log_id()` call:
```c
// TM-26: Generate bindfile from debug menu
device_bindfile_generate();
```

Also add BindingID hex to the debug info string (lines appended in `device_identity_debug_get_info_string()`).

---

### Loader Integration

#### [MODIFY] [DAP_Loader_unisoc.c](file:///c:/zkwwork/featurephoneosreconstruction/Third-party/DAP/platform/unisoc/DAP_Loader_unisoc.c)

1. Replace the existing `D:\DAP\device.bind` path block (lines 209-222) with a call to `device_bindfile_generate()`
2. In `DAP_ExecuteAP()` BIN2 path: add auto-generate check:
   ```c
   if (is_bin2 && !device_bindfile_exists()) {
       device_bindfile_generate();
   }
   ```

---

### Build System

#### [MODIFY] [dap.mk](file:///c:/zkwwork/featurephoneosreconstruction/make/dap/dap.mk)

Add `device_bindfile.c` to SOURCES after `device_binding.c`.

---

## Module Impact
- **device_binding.c** — No changes needed; existing `binding_export_bindfile()` is reused as-is
- **device_bindfile.c (NEW)** — Thin wrapper over `binding_export_bindfile()` with correct path and TM26 traces
- **device_identity_debug.c** — Minor addition (one function call + info string extension)
- **DAP_Loader_unisoc.c** — Replace inline path with wrapper call; add auto-gen in BIN2 path
- **dap.mk** — One line addition

## Risk Areas
- **FileArray path existence** — Must verify `FileArray/` directory exists on device (Pitfall 4)
- **`SFS_CreateFile` with correct Unicode path encoding** — must match existing patterns exactly

---

## ⚠️ Pitfall Briefing

### Matched Pitfalls (5 items)

| # | Pitfall | Relevance | Prevention |
|---|---------|-----------|------------|
| 1 | **dap.mk 编译开关遗漏（反复踩坑 ×3）** | New `.c` file (`device_bindfile.c`) must be added to SOURCES | Add to `SOURCES` immediately after creating file |
| 2 | SCI_TRACE_MODE missing | TM26 adds new traces | Already present in `dap.mk` — verify after changes |
| 3 | SCI_TRACE_LOW unavailable in security files | New file uses `DAP_DBG` | Use `DAP_DBG` via `dap_security_log.h` — never call `SCI_TRACE_LOW` directly |
| 4 | 内存释放 (offset pointer) | No dynamic memory in this TM | No risk — uses stack-only pattern |
| 5 | FileArray 路径必须存在 | TM26 writes to `FileArray/` which may or may not exist | Check existence; if not writable, fallback with error log |

### Applicable Runbooks
- [ ] `dap_mk_checklist.md` — Execute after all code changes, before build

### Key Decisions to Respect
- **ADR-003:** All DAP modules use `DAP_DBG` → `DAP_TracePrint` → `SCI_TRACE_LOW` (never call directly)
- **ADR-006:** Device binding is phased; TM-26 is Phase 1B (export only, no BIN2 header changes)
- **ADR-008:** `DAP_LoaderInit` is lazy init; security functions need dual-path triggers (Loader + debug menu)

---

## Execution Order

1. Create `device_bindfile.h` — define API surface
2. Create `device_bindfile.c` — implement wrapper + exists check
3. Update `dap.mk` — add `device_bindfile.c` to SOURCES
4. Update `device_identity_debug.c` — add bindfile gen to debug menu
5. Update `DAP_Loader_unisoc.c` — replace inline path, add auto-gen
6. Create architecture doc
7. Update `MEMORY.md` & registries
8. Execute `dap_mk_checklist.md` runbook

---

## Verification Plan

### Manual Verification (Engineer on Device)
1. Build firmware with `make -r -R MAKESHELL=CMD p=ums9117_240X320BAR_64MB_ML MODULES=dap JOB=16`
2. Flash to device
3. Dial `*#3472#` → verify Logel shows `[bind] tm26_generate_bindfile` and `[bind] tm26_file_written=FileArray/device.bind`
4. Connect USB → navigate to `FileArray/` → verify `device.bind` exists
5. Open `device.bind` in text editor → verify valid JSON with `version`, `binding_alg`, `binding_id`, `device_model`
6. Verify `binding_id` matches Logel TM-25 `tm25_id` output
7. Verify no DeviceSecret in the file
8. Run a BIN2 file → verify auto-generation if bindfile was deleted

### Build Verification (Automated)
- Verify `dap.mk` includes `device_bindfile.c` in SOURCES
- Verify no compilation errors with `MODULES=dap` build
