# Pitfall: DAP_FMM_IsBinFile Only Accepts .bin Extension

**Date:** 2026-03-10
**Memo:** TM-15
**Severity:** High (new file formats silently rejected)

## Symptom

`.bin2` files copied to the device show "unsupported format" when user tries to execute them, even though the BIN2 loader code is compiled into the firmware.

## Root Cause

`DAP_FMM_IsBinFile()` in `DAP_FMM_Integration.c` only checks for `.bin` extension (4 chars). It acts as a gate — files that don't pass this check never reach the DAP loader.

## Fix

Extended `DAP_FMM_IsBinFile` to check for `.bin2` (5 chars) first, then `.bin` (4 chars):

```c
// Check .bin2 (5 chars) first
if (name_len >= 5) {
    if ((suffix[-5] == '.' || suffix[-5] == '.') &&
        (suffix[-4] == 'b' || suffix[-4] == 'B') &&
        (suffix[-3] == 'i' || suffix[-3] == 'I') &&
        (suffix[-2] == 'n' || suffix[-2] == 'N') &&
        (suffix[-1] == '2')) {
        return TRUE;
    }
}
// Then check .bin (4 chars)
...
```

## Prevention

When adding new DAP file formats, **always update `DAP_FMM_IsBinFile`** in addition to the loader. This function is the file-type gatekeeper for the DAP file management module.
