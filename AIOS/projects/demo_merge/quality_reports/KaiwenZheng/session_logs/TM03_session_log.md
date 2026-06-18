# TM03 Session Log — James Demo Feature Integration

**Date**: 2026-03-26
**Engineer**: KaiwenZheng
**Project**: demo_merge
**Memo**: TM-03
**Duration**: ~5 hours (17:00 - 22:25)
**Result**: ✅ SUCCESS — Palm Menu launcher boots, Chinese text renders correctly

---

## Summary

Integrated James's legacy feature phone demo code into the mainline `demo_merge` internal build. The integration covered source migration of ~60 files, build system reconfiguration, and device verification. Three major debugging cycles were required to resolve compile/link/runtime issues.

## Files Modified/Created

### Source Migration (A1-A5)
- `Third-party/lvgl-9.5.0/dap_lvgl_bridge.c` — replaced with James version (App callback stack)
- `Third-party/lvgl-9.5.0/src/` — **entire directory replaced** with James's LVGL build (fixes CJK fonts)
- `Third-party/DAP/platform/unisoc/` — 9 new bridge files (t9, va, downloader)
- `Third-party/DAP/bigseek_core/` — NEW: 18 files (voice assistant core)
- `Third-party/DAP/sdk/` — 4 new API headers
- `Third-party/DAP/apps/` — 11 app source directories

### API Registration & Platform (A6-A8)
- `DAP_InstallOSAPI_unisoc.c/h` — replaced with James superset (70+ APIs)
- `dap_audio_bridge.c/h` — replaced
- `dap_gui_unisoc.c` — replaced
- `DAP_DebugLog.c/h` — replaced
- `DAP_FMM_Integration.c/h` — replaced (has DAP_FMM_OpenDownloader)
- `dap_unisoc_shim.h` — replaced
- `DAP_OSAssociated_unisoc.h` — replaced
- `mmimain.c` — replaced (DAP init + palm_menu auto-launch)
- `mmi_lvgl_win.c` — replaced (LVGL window + ESC/RED key handling)
- `mmiphone_onoff.c` — replaced (skip boot animation)

### Build System (A9)
- `make/dap/dap.mk` — **rewritten**: merged mainline security + James features
- `make/lvgl/lvgl.mk` — replaced
- `make/bigseek_core/bigseek_core.mk` — NEW
- `make/app_main/app_main.mk` — replaced
- `make/preloadudisk_app/preloadudisk_app.mk` — NEW
- `make/preload_app/preload_app.mk` — NEW
- `project_ums9117_240X320BAR_64MB.mk` — PRELOAD_UDISK_SUPPORT + OSA partition
- `project_ums9117_240X320BAR_64MB_ML.mk` — DAP_DebugLog/DAP_Download/FUTURE_SUPPORT flags

### Flash Partition
- `Nand_PartTable_64k.c` — OSA 16MB → 18MB
- `Nand_PartTable_128k.c` — corresponding 128k block update

### Compatibility Shims
- `Third-party/DAP/core/DAP_Register.h` — NEW shim → DAP_InterfaceRegister.h
- `Third-party/DAP/platform/unisoc/DAP_Loader.h` — NEW shim → DAP_Loader_unisoc.h

### Stubs
- `DAP_MTK_Stubs.c` — added 3 PDP function stubs

### Preload Content
- `MS_MMI_Main/source/resource/mmi_res_240x320/preload_udisk/` — copied all BINs from James

## Key Decisions
1. **Keep our secure DAP core** — used shim headers instead of replacing DAP_InterfaceRegister.c/DAP_Loader_unisoc.c
2. **bigseek_core under DAP** — placed at `Third-party/DAP/bigseek_core/` per user decision
3. **FUTURE_SUPPORT = TRUE** — required for gettimeofday in timing.c
4. **Full LVGL src replacement** — James's LVGL has different CJK font coverage

## Debugging Cycles
1. **Compile errors** — missing headers (DAP_Register.h, DAP_Loader.h) → created shim headers
2. **17 linker errors** — missing security module, OS_* symbols, PDP functions → rewrote dap.mk, added stubs
3. **33KB PAC** — PRELOAD_UDISK_SUPPORT without preload content → disabled, then fixed properly
4. **Palm menu not appearing** — app BIN files not deployed → copied from James's preload_udisk
5. **Chinese garbled text** — different LVGL version with incomplete CJK font → replaced entire LVGL src
