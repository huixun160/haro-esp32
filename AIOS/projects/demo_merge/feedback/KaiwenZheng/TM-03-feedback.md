# TM-03 Feedback — James Demo Feature Integration

**Date**: 2026-03-26
**Engineer**: KaiwenZheng
**Project**: demo_merge
**Memo**: TM-03

---

## Outcome
✅ **SUCCESS** — Palm Menu launcher boots on device, Chinese text renders correctly, all preloaded apps appear.

## What Went Well
1. **Source migration** — File-by-file copy approach ensured traceability; all mainline backups preserved
2. **Security guardrail** — Successfully kept our secure DAP core (InterfaceRegister + Loader) using shim headers instead of James's versions
3. **Build mode gating** — Properly merged EXTERNAL_BUILD / SECURITY_DEBUG_MENU flags

## What Went Wrong
1. **dap.mk overwrite** — Blindly replacing dap.mk with James's version dropped our entire security module (12 files, 3 paths). Should have merged, not replaced.
2. **Missing BIN files** — Didn't realize app BINs needed separate deployment in preload_udisk/. Resulted in a PAC that compiled perfectly but had no visible functionality.
3. **LVGL version mismatch** — Assumed same version = same content. CJK font data was 738KB smaller, causing widespread garbled text.

## Lessons Learned
- **"Compile success" ≠ "Integration success"** — Must verify runtime behavior on device
- **File size comparison is the fastest diff tool** — Would have caught the LVGL CJK issue in 10 seconds
- **.mk files are "merge-only"** — Never overwrite, always merge with diff
- **DAP apps are separately compiled BINs** — They're not part of the firmware build chain

## Time Breakdown
| Phase | Time | Notes |
|-------|------|-------|
| Source migration | 2h | A1-A9, copying and replacing files |
| Compile debugging | 1.5h | 3 rounds: headers → linker → PAC |
| BIN deployment | 0.5h | Finding and copying preload_udisk content |
| LVGL font fix | 0.5h | Comparing and replacing src/ directory |
| Closeout | 0.5h | Documentation |
