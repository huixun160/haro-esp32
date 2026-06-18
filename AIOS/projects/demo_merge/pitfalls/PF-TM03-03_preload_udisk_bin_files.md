# Pitfall: PRELOAD_UDISK_SUPPORT Requires App BIN Files in preload_udisk/

**ID**: PF-TM03-03
**Date**: 2026-03-26
**Author**: KaiwenZheng
**Project**: demo_merge
**Severity**: CRITICAL
**Category**: Build / Deployment

## Symptom 1: 33KB PAC file
When `PRELOAD_UDISK_SUPPORT = TRUE` but `preload_udisk/` directory doesn't contain the app BIN files, `pac_9117.pl` fails at line 414 producing a 33KB PAC (should be ~25MB).

## Symptom 2: DAP apps don't launch on device
Even with a correctly sized PAC, if app BIN files (palm_menu.bin, Download_Bin.bin, icon BINs) are not in `preload_udisk/`, the device's D: partition is empty and `mmimain.c` auto-launch silently fails.

## Root Cause
DAP apps are **separately compiled BIN files** that run on the DAP runtime. They are NOT part of the main firmware build. They must be:
1. Pre-compiled using the DAP SDK toolchain (or obtained pre-compiled from James)
2. Placed in `MS_MMI_Main/source/resource/mmi_res_240x320/preload_udisk/apps/` and `/themes/`
3. Declared in `preloadudisk_def.h` (SFS_ADD_FOLDER entries)
4. Packaged into `preloadudisk_img.bin` by the build system when `PRELOAD_UDISK_SUPPORT = TRUE`

## Fix
Copy all pre-compiled BIN files from James's `preload_udisk/` directory:
- `palm_menu.bin` (16KB) — launcher
- `Download_Bin.bin` (40KB) — Bazar downloader
- 6x icon BINs (bazar, Browser, Contacts, dial, Settings, SMS)
- Fonts and images (DroidSansFallback.ttf, PNG icons)

## Prevention
- When adding DAP app support, ALWAYS verify `preload_udisk/` has the required BIN files
- Check PAC file size after build — anything under 15MB is suspicious
- The `mmimain.c` auto-launch code silently falls back to Idle Screen if BIN is missing — use Logel trace to debug
