# Pitfall: LVGL Version Mismatch Causes CJK Font Garbling

**ID**: PF-TM03-01
**Date**: 2026-03-26
**Author**: KaiwenZheng
**Project**: demo_merge
**Severity**: HIGH
**Category**: Build / Font

## Symptom
After integrating James's code, Chinese characters in LVGL UI display as garbled/mojibake. The palm_menu launcher shows icons correctly but all Chinese text labels are unreadable.

## Root Cause
Our mainline LVGL `src/` directory was a **different build** of LVGL 9.5.0 than James's. Key difference:
- `lv_font_source_han_sans_sc_16_cjk.c`: ours = **1.2 MB**, James = **1.9 MB** (738KB more glyphs)
- All 30+ font source files differed in size
- The LVGL core files (lv_font.c, lv_font.h, etc.) also differed

Even though both directories are "LVGL 9.5.0", the **generated font data files** are version-specific and must match.

## Fix
Replace the entire `Third-party/lvgl-9.5.0/src/` directory with James's version.

## Prevention
- When merging LVGL-dependent code, **always check the LVGL src/ directory hash**, not just the version number
- CJK font files are the FIRST thing to check when Chinese text displays incorrectly
- The `lv_conf.h` being identical does NOT mean the font data is identical
