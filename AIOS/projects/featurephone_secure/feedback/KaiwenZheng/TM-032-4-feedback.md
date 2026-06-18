# TM-032-4 Feedback — Interface IDization

**Date:** 2026-03-21
**Outcome:** SUCCESS
**Engineer:** z1354

## Completed Work

### Interface IDization (40 APIs)
- Created `dap_interface_id.h` with non-sequential ID enum (0x11–0x5D)
- Added `InterfaceRegister_AddById`/`FindById` flat array (O(1)) in `DAP_InterfaceRegister.c`
- Bootstrap: firmware registers `FindById` as `"__FB"` — the **only** string remaining in EXTERNAL_BUILD
- All 40 APIs across 4 batches dual-pathed with `#ifdef EXTERNAL_BUILD`:
  - Batch 1: Memory (5) — `DAP_InstallOSAPI_unisoc.c`
  - Batch 2: File (10) — `DAP_InstallOSAPI_unisoc.c`
  - Batch 3: Timer/Debug/Time (9) — `DAP_InstallOSAPI_unisoc.c`
  - Batch 4: GUI (3) + Audio (13) — `dap_gui_unisoc.c`, `dap_audio_bridge.c`
- `dap_api.h` macros dual-pathed: `_FB(cmd)(IF_xxx)` for EXTERNAL_BUILD
- `build.bat` updated with `-DEXTERNAL_BUILD -I%CORE_DIR%`

### Key Design Decision
**Did NOT modify `TApplication` struct** (unlike TM-032-2 which crashed).
Used existing `InterfaceRegister_Add("__FB", FindById)` as bootstrap mechanism.
Zero ABI changes. Entry.c unchanged.

## Verification Results

| Test | Result |
|------|--------|
| SECURE build compiles | ✅ |
| BIN executes (`Hello AIOS v0`) | ✅ |
| BIN2 single execution | ✅ |
| BIN3 single + repeated | ✅ |
| Logel: `dap` search | ✅ Zero results |
| `DAP_MemAlloc` in Logel | ✅ Not found |
| BIN2 repeated execution | ⚠️ Crash after ~5 runs (pre-existing, see below) |

## Known Issue (Pre-existing)

**BIN2 repeated execution crash:** `Undefined exception handler` at APP memory after ~5 consecutive BIN2 runs. BIN and BIN3 do NOT crash. This is **not caused by TM-032-4** — same pattern in all builds. Likely BSS realloc / I-cache issue specific to BIN2 non-encrypted path. Track separately.

## Pitfalls Encountered

1. **`uint16` / `_INT32` undefined in cross-module code** — DAP core uses `def.h` types, platform files don't. Fix: use `unsigned short` / `int`.
2. **APP not compiled with `EXTERNAL_BUILD`** — `build.bat` lacked `-DEXTERNAL_BUILD`, causing APP to use string-based macros while firmware only registered IDs. `dap_popup` silently failed.

## Files Modified

| File | Change |
|------|--------|
| `core/dap_interface_id.h` | NEW — 40 API IDs |
| `core/DAP_InterfaceRegister.c` | +20 lines — AddById/FindById |
| `platform/unisoc/DAP_InstallOSAPI_unisoc.c` | Batch 1-3 dual-path + __FB bootstrap |
| `platform/unisoc/dap_gui_unisoc.c` | Batch 4 GUI dual-path |
| `platform/unisoc/dap_audio_bridge.c` | Batch 4 Audio dual-path |
| `sdk/dap_api.h` | All public macros dual-pathed |
| `apps/hello_bigseek/build.bat` | Added `-DEXTERNAL_BUILD` |

## Next Actions
- [ ] Investigate BIN2 repeated execution crash (separate TM)
- [ ] TM-032-5: Light obfuscation (wrapper rename, dispatch table, constant dispersion)
