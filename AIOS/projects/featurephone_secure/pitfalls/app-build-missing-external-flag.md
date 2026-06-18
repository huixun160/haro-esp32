# Pitfall: APP Build Missing EXTERNAL_BUILD Flag

**Date:** 2026-03-21
**Memo:** TM-032-4
**Severity:** HIGH

## Symptom

APP executes but `dap_popup` and `dap_log` silently fail. Only "OK: Module executed" shown (from loader), not "Hello AIOS v0" (from APP).

## Root Cause

`build.bat` compiles APP without `-DEXTERNAL_BUILD`. The `dap_api.h` macros use string-based `FindInterface("OS_DisplayPopup")`, but SECURE firmware only registers ID-based entries. Hash lookup returns NULL, `if(_fn)` guard skips the call.

## Fix

Add `-DEXTERNAL_BUILD -I%CORE_DIR%` to all `armcc` lines in `build.bat`:
```batch
armcc -c -O1 ... -DEXTERNAL_BUILD -I%CORE_DIR% -I%SDK_DIR% ...
```

## Prevention

- When adding `#ifdef EXTERNAL_BUILD` to SDK headers, **always update APP build scripts simultaneously**
- SDK header changes that affect APP compilation must be tested end-to-end (firmware + APP rebuild)
