# Session Log — TM-032-2

**Date:** 2026-03-21
**Duration:** ~4 hours (11:20 – 14:37)
**Task:** External Build Strip & Semantic Reduction

## Summary

Implemented two workstreams for EXTERNAL_BUILD hardening:
1. **WS1 (Trace Gating):** All DAP debug macros (DAP_DBG, BIN2_LOG, DAP_SEC_LOG, DAP_TRACE_LOW) become noop under EXTERNAL_BUILD. DAP_DebugLog.c entirely excluded. DAP_RunDebug.Log suppressed.
2. **WS2 (FindInterface→ID):** Created dap_interface_ids.h (44 IDs), InterfaceRegister_AddById/FindById, FindInterfaceById in Entry.c, dual-path dap_api.h.

Trace gating verified: SECURE Logel shows zero DAP traces.
BIN2 execution crashes with Prefetch Abort — blocked.

## Key Decisions

- User decided to **roll back** and defer trace stripping to TM-032-3 via obfuscation
- EXTERNAL_BUILD approach has fundamental debuggability issue: can't debug crashes with all traces removed
- I-cache flush in loader is a separate concern to address

## Bugs Encountered

1. **PowerShell encoding corruption** — `Set-Content` converted file encoding, breaking armcc compilation. Fix: use Latin-1 byte-transparent replacement.
2. **CRLF→LF conversion** — PowerShell stripped \r from line endings. armcc requires CRLF.
3. **Missing include paths** — DAP/sdk not in MINCPATH in dap.mk.
4. **DAP_TRACE_LOW inside ENABLE_DAP guard** — macro was unreachable by files without ENABLE_DAP.
5. **DAP_DebugOutput linker error** — dap_gui_unisoc.c called it directly; gating DAP_DebugLog.c removed the symbol.
6. **Prefetch Abort** — suspected I-cache coherency in loader.

## Deviations from Spec

- WS3 (Strip) and WS4 (Strings Scan) not started due to BIN2 execution blocker.
