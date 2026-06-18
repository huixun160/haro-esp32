# TM-032-3 Feedback — External Artifact Hardening (Post-Build)

**Outcome:** SUCCESS
**Date:** 2026-03-21
**Engineer:** KaiwenZheng

---

## Completed Work

### WS1: Strip Debug Info ✅
- `fromelf --strip=debug` on Entry.o (-1,360B) and Start.o (-542B)
- Integrated into `export_zkw_output.py` with full `FROMELF_PATH`

### WS2: Strings Scan ✅
- Built-in watchlist (12 patterns) + file-based watchlist support
- Report output: `zkw_output/reports/strings_report.txt`
- Scan passed: zero sensitive strings in exported binaries

### WS3: Trace Codebook ✅
- 165 trace lines modified across 15 source files
- 33 prefix mappings (DAP→P7, DeviceSecret→K9, tm15→v15, etc.)
- Codebook: `AIOS/docs/runbooks/trace_codebook.md`
- Python replacement script: `C:\tmp\trace_replace.py`

### WS4: Export Pipeline ✅
- Enhanced `export_zkw_output.py`: FROMELF_PATH, extract_strings, report file

### Bonus: Debug Log File Suppression ✅
- `DAP_RunDebug.Log` renamed to `P7_rd.log`
- External build (`EXTERNAL_BUILD`): file write completely gated out

## Verification Results

| Test | Result |
|------|--------|
| BIN execution | ✅ OK |
| BIN2 execution (device-bound) | ✅ OK |
| BIN3 execution (encrypted + bound) | ✅ OK |
| Logel `[P7]` prefix | ✅ Visible |
| Logel `v15_BIN2` verify | ✅ Visible |
| Strip Entry.o/Start.o | ✅ Size reduced |
| strings_report.txt | ✅ Generated, passed |

## Remaining (acceptable)

- `__FILE__` macro outputs source filenames (e.g., `DAP_Loader_unisoc.c`) — cannot change without renaming files
- `InterfaceRegister` API names (`DAP_MemAlloc`, `DAP_TracePrint`) — ABI contract, cannot change
- `k9s` trace not yet verified on device (requires recompile + reflash)

## Next Actions
- Recompile and verify `k9s` in Logel
- TM-033: 接口/错误码/文档收口
- TM-032-4 (optional): deeper obfuscation after system stable
