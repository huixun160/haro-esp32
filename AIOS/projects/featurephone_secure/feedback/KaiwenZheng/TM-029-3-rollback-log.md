# TM-029-3 Rollback Log

**Date:** 2026-03-19
**Baseline Commit:** `a989891e` ([TM-28R] Security baseline recovery)
**Rollback From:** `f3fc1a68` (after-tm-29-2.5)

---

## Directories Moved to `legacy_code/`

| Source | Destination |
|--------|-------------|
| `oywork/` | `legacy_code/oywork/` |
| `zkwwork_contaminated_snapshot/` | `legacy_code/zkwwork_contaminated_snapshot/` |

## Files Reverted (git checkout a989891e)

| # | File | Change Reverted |
|---|------|----------------|
| 1 | `mmi_lvgl_win.c` | 2-param DispatchKey, KEY_UP, ESC close |
| 2 | `DAP_InstallOSAPI_unisoc.c` | VA API registrations |
| 3 | `dap_audio_bridge.c` | VA recording/streaming/volume (60→28KB) |
| 4 | `dap_audio_bridge.h` | VA function declarations |
| 5 | `lvgl_api.h` | VA LVGL API additions |
| 6 | `dap_lvgl_bridge.c` | 2-param callback + CJK font |
| 7 | `lv_font_source_han_sans_sc_16_cjk.c` | Extended CJK font (3.9→1.2MB) |
| 8 | `dap.mk` | bigseek_core + VA bridge entries |

## Files Deleted

| # | Path | Type |
|---|------|------|
| 1-14 | `Third-party/bigseek_core/` (entire) | 14 source + 4 header |
| 15-24 | `Third-party/DAP/apps/voice_chat/` (entire) | Main.c + build artifacts |
| 25 | `dap_va_bridge.c` | VA bridge |
| 26 | `dap_va_bridge.h` | VA bridge header |
| 27 | `dap_va_api.h` | VA SDK API |
