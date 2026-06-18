# TM-029-3 Clean Checklist

All items verified by automated grep scan on 2026-03-19.

## VA Code Removal

- [x] `Third-party/bigseek_core/` — **DELETED**
- [x] `Third-party/DAP/apps/voice_chat/` — **DELETED**
- [x] `dap_va_bridge.c` / `.h` — **DELETED**
- [x] `dap_va_api.h` — **DELETED**

## Build Path Clean

- [x] `grep "BIGSEEK_CORE_SUPPORT"` → **CLEAN** (0 matches)
- [x] `grep "bigseek"` → only pre-existing `hello_bigseek/` demo app (in TM28-R baseline)
- [x] `grep "voice_chat"` → only pre-existing `future_app_api_core.c` (unchanged since TM28-R)
- [x] `grep "dap_va"` → only `ldap_value_free_len` in curl/lib (false positive)

## File Integrity

- [x] `dap_audio_bridge.c` — reverted to TM28-R (28KB, 21 functions)
- [x] `dap_lvgl_bridge.c` — reverted to TM28-R
- [x] `mmi_lvgl_win.c` — reverted to TM28-R
- [x] `dap.mk` — reverted to TM28-R

## Contaminated Snapshot Isolation

- [x] `oywork/` → `legacy_code/oywork/` (not in build path)
- [x] `zkwwork_contaminated_snapshot/` → `legacy_code/zkwwork_contaminated_snapshot/` (not in build path)
