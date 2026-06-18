# Session Log — TM-20: Logel Trace Fix & BIN2 Prefix Tracking

**Date:** 2026-03-11
**Memo:** Technical_Memo_20_logelfix
**Status:** SUCCESS ✅

---

## Summary

Fixed `BIN2_LOG` undefined symbol linker error. Created `dap_security_log.h` with direct `SCI_TRACE_LOW` calls (matching platform standard). Re-added `-DSCI_TRACE_MODE` to `dap.mk` (had been lost). Engineer verified Logel trace output on device — `[bin2]` and `tm20_` traces visible.

## Files Created

| File | Description |
|---|---|
| `Third-party/DAP/security/dap_security_log.h` | Unified security logging header |
| `AIOS/docs/pitfalls/dap_mk_flags_missing.md` | Recurring pitfall: dap.mk flags |
| `AIOS/docs/runbooks/dap_mk_checklist.md` | Post-TM dap.mk verification checklist |

## Files Modified

| File | Change |
|---|---|
| `make/dap/dap.mk` | Re-added `-DSCI_TRACE_MODE` |
| `Third-party/DAP/security/bin2_loader.c` | Include changed to `dap_security_log.h` |
| `Third-party/DAP/security/bin2_crypto.c` | Include changed to `dap_security_log.h` |
| `Third-party/DAP/security/device_identity.c` | Include changed, added tm20_ PoC traces |
| `AIOS/MEMORY.md` | Added recurring dap.mk pitfall warning |

## Key Decisions

- Use direct `SCI_TRACE_LOW` (via `os_api.h`) instead of indirect `DAP_DBG → DAP_TracePrint` chain
- `BIN2_LOG` prefix: `[bin2]` — matches platform convention (e.g. `[SIMLOCK]`, `[BS_PCM_DQ]`)
