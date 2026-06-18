# Session Log — TM-19: Logel Fix Pilot Research

**Date:** 2026-03-10
**Memo:** Technical_Memo_19_logelfix_pilotresearch.md
**Status:** Partial (awaiting device verification)

---

## Summary

Investigated why DAP trace never appears in Logel. Found root cause: `SCI_TRACE_MODE` compile flag controls whether `SCI_TRACE_LOW` is real or no-op. Added `-DSCI_TRACE_MODE` to `dap.mk`. Confirmed `SCI_TRACE_LOW` is the standard platform trace API (1145+ call sites in `MS_Ref`). Added 3 PoC test traces in `device_secret_init()`. Awaiting device verification.

## Files Created

| File | Description |
|---|---|
| `AIOS/docs/logel_fix_pilot_research.md` | Full trace mechanism research |
| `AIOS/docs/logel_trace_feedback.md` | One-page feedback summary |

## Files Modified

| File | Change |
|---|---|
| `make/dap/dap.mk` | Added `-DSCI_TRACE_MODE` to `MCFLAG_OPT` |
| `Third-party/DAP/security/device_identity.c` | Added 3 PoC trace test points (`tm19_*`) |

## Key Findings

1. `SCI_TRACE_LOW` is used by 1145+ platform modules — confirmed standard API
2. `os_api.h` line 361: `SCI_TRACE_MODE` must be defined for traces to work
3. DAP security files (`bin2_*.c`, `device_identity.c`) don't include `os_api.h`
4. DAP platform files (`DAP_OSAssociated_unisoc.c`) DO include `os_api.h`
5. `DAP_DBG` → `DAP_TracePrint` → `SCI_TRACE_LOW` chain should work

## Open Issues

- Device verification of PoC traces pending
