# Feedback — TM-032-2: External Build Strip & Semantic Reduction

**Date:** 2026-03-21
**Memo:** Technical_Memo_32-2 — External Build Strip & Semantic Reduction.md
**Outcome:** PARTIAL
**Author:** kz & Antigravity

---

## Execution Summary

Implemented WS1 (trace gating) and WS2 (FindInterface→FindInterfaceById) for EXTERNAL_BUILD hardening. Trace gating verified working: SECURE Logel shows zero DAP-related traces. BIN2 execution crashes with Prefetch Abort on SECURE build — root cause suspected to be I-cache coherency issue in the loader. Decision: **roll back changes, keep Logel traces for now, defer trace stripping to TM-032-3 via obfuscation approach**.

---

## Completed Work

- [x] WS1: DAP_DBG/WARN/ERR → noop via `#ifdef EXTERNAL_BUILD` in `DAP_DebugLog.h`
- [x] WS1: BIN2_LOG/DAP_SEC_LOG → noop in `dap_security_log.h`
- [x] WS1: DAP_TRACE_LOW macro (gated SCI_TRACE_LOW) — 28 calls replaced in 7 files
- [x] WS1: DAP_DebugLog.c gated → DAP_RunDebug.Log not generated
- [x] WS2: `dap_interface_ids.h` — 44 interface ID constants
- [x] WS2: InterfaceRegister_AddById/FindById in core registry
- [x] WS2: FindInterfaceById() in Entry.c via App->Free
- [x] WS2: `dap_api.h` dual-path macros (EXTERNAL→ID, internal→string)
- [x] WS2: ID registration across 6 Install functions (44 APIs)
- [x] Verified: SECURE Logel has zero `[DAP]`, `[bin2]`, `tm15_BIN2` traces

---

## Incomplete Work

- [ ] BIN2 execution on SECURE build — crashes with Prefetch Abort
- [ ] BIN1 execution on SECURE build — untested
- [ ] WS3 (Strip verification) — not started
- [ ] WS4 (Strings scan) — not started

---

## Blocking Issues

| Issue | Symptom | Root Cause | Suggested Resolution |
|---|---|---|---|
| BIN2 Prefetch Abort | Prefetch fault (IFSR:0x00001008) at ~0x0c8c7294 on T_P_APP thread | Suspected I-cache coherency: file read via D-cache, CPU fetches via I-cache. TM-032-2 firmware layout changes exposed latent bug. Added cache flush but still crashes — deeper investigation needed | Defer to TM-032-3. Consider: (1) obfuscation instead of compile-time gating, (2) I-cache flush investigation as separate task |
| No debug on SECURE | Cannot debug SECURE build crashes via Logel since all traces are gated | By design (WS1) | Highlights need for staged rollout: implement trace stripping only after BIN loading is proven stable |

---

## Verification Status

| Test | Result | Notes |
|---|---|---|
| SECURE compile | PASS | After fixing encoding, include paths, linker errors |
| Internal compile | PASS | Unchanged behavior |
| SECURE Logel zero traces | PASS | Confirmed: no `[DAP]`, `[bin2]`, `tm15_BIN2` |
| SECURE BIN2 execution | FAIL | Prefetch Abort at 0x0c8c7294 |
| DAP_RunDebug.Log suppressed | PASS | File not generated on SECURE |
| Internal BIN2 execution | UNTESTED | User was compiling when session ended |

---

## Next Actions

1. **Roll back TM-032-2 changes** — `git checkout` to restore pre-TM-032-2 state
2. **TM-032-3: Obfuscation approach** — instead of compile-time gating, use post-build string obfuscation/stripping of the PAC binary. This avoids the I-cache/runtime issues of conditional compilation
3. **Investigate I-cache flush** — the loader's lack of general I-cache flush is a latent bug that should be fixed regardless of TM-032-2
4. **DeviceSecret workflow** — TM-032-2 memo also mentions need to decide DeviceSecret export approach (auto-send program vs auto-BIN3 mode)

---

## Files Changed

| File | Action | Description |
|---|---|---|
| `DAP_DebugLog.h` | Modified | EXTERNAL_BUILD noop macros + DAP_TRACE_LOW |
| `dap_security_log.h` | Modified | BIN2_LOG/DAP_SEC_LOG gating |
| `DAP_DebugLog.c` | Modified | #ifndef EXTERNAL_BUILD guard |
| `dap_interface_ids.h` | Created | 44 interface ID constants |
| `DAP_InterfaceRegister.h/.c` | Modified | AddById/FindById functions |
| `Entry.c` | Modified | FindInterfaceById via App->Free |
| `DAP_Loader_unisoc.c` | Modified | Free ptr injection + I-cache flush |
| `dap_api.h` | Modified | Dual-path macros |
| `DAP_InstallOSAPI_unisoc.c` | Modified | ID registration (24 APIs) |
| `dap_gui_unisoc.c` | Modified | DAP_DebugOutput→DAP_DBG |
| `dap_audio_bridge.c` | Modified | ID registration + include |
| `DAP_MTK_Stubs.c` | Modified | DAP_DebugLog.h include |
| `dap.mk` | Modified | SDK include path |
| 4 security/*.c files | Modified | SCI_TRACE_LOW→DAP_TRACE_LOW |

---

## References

- Related memos: TM-032, TM-028 (I-cache fix precedent), TM-032-3 (planned)
- Related pitfalls: `AIOS/docs/pitfalls/powershell-encoding-corruption.md`
