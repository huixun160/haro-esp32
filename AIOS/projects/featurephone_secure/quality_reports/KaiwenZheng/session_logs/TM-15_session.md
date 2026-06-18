# Session Log — TM-15: BIN2 Secure Loader Integration

**Date:** 2026-03-10
**Memo:** Technical_Memo_15_ko3_bin2withnosecureid.md
**Status:** Partially Complete (paused — Ed25519 signature verification failure on device)

---

## Summary

Integrated the BIN2 secure loader into the DAP firmware build system and runtime loader. BIN2 files are now detected and routed through the verification pipeline. Compilation succeeds and `.bin2` files are recognized by the DAP file manager. However, Ed25519 signature verification fails on-device for all `.bin2` files (including correctly signed ones), blocking full validation. SHA-256 hash verification code and the overall verification pipeline are in place but untestable until the signature issue is resolved.

## Files Created

| File | Description |
|---|---|
| `Third-party/DAP/security/bin2_loader.c` | BIN2 format detection and verification orchestration |
| `Third-party/DAP/security/bin2_loader.h` | BIN2 loader API header |
| `Third-party/DAP/security/bin2_crypto.c` | Ed25519 signature + SHA-256 hash verification |
| `Third-party/DAP/security/bin2_crypto.h` | Crypto API header |
| `Third-party/DAP/security/bin2_format.h` | BIN2 file format constants and structures |
| `Third-party/DAP/security/sha256.c` | SHA-256 implementation (dap_ prefixed) |
| `Third-party/DAP/security/sha256.h` | SHA-256 header (dap_ prefixed) |
| `Third-party/DAP/security/ed25519/ed25519_verify.c` | Ed25519 verify (TweetNaCl-derived) |
| `Third-party/DAP/security/ed25519/ed25519_verify.h` | Ed25519 verify header |
| `AIOS/tools/bin2_packer/bin2_pack.py` | Python packer: BIN1→BIN2 signing tool |
| `AIOS/tools/bin2_packer/generate_test_bins.py` | Test bin generator (valid/tampered/badsig) |
| `AIOS/tools/bin2_packer/test/test_*.bin*` | Test binary files |

## Files Modified

| File | Change |
|---|---|
| `make/dap/dap.mk` | Added BIN2 source files and ed25519 include path |
| `Third-party/DAP/platform/unisoc/DAP_FMM_Integration.c` | Extended `DAP_FMM_IsBinFile` to accept `.bin2` |
| `Third-party/DAP/platform/unisoc/DAP_Loader_unisoc.c` | Added BIN2 detection, verification, and payload stripping |
| `Third-party/DAP/platform/unisoc/DAP_Loader_unisoc.h` | Added BIN2 error codes |
| `Third-party/DAP/platform/unisoc/DAP_OSAssociated_unisoc.c` | Fixed `DAP_TracePrint` to use vsnprintf |

## Key Decisions

1. **SHA-256 symbol prefixing** — Prefixed all SHA-256 symbols with `dap_` to avoid linker collision with SSV WiFi module's `sha256.o`
2. **Signature message construction** — Message = `header(48) + zeros(64) + payload` (signature area zeroed), matching between packer and verifier
3. **BIN2 file extension recognition** — `DAP_FMM_IsBinFile` checks `.bin2` (5 chars) before `.bin` (4 chars)
4. **Logging via DAP_DBG** — BIN2 modules use `DAP_DBG` → `DAP_TracePrint` → `SCI_TRACE_LOW` to avoid `SCI_TRACE_LOW` macro unavailability in security compilation units

## Open Issues

1. **Ed25519 signature verification fails on-device** — All `.bin2` files return ERR-10 (SIG FAIL), including correctly signed ones. Root cause likely in TweetNaCl-derived Ed25519 implementation (64-bit arithmetic on 32-bit ARM). Needs dedicated debugging memo.
2. **Logel trace visibility** — Diagnostic logging via `DAP_DBG` confirmed to compile; awaiting device verification that `tm15_` logs appear in Logel.

## Verification Results

| Test | Result |
|---|---|
| Full firmware compilation | ✅ PASS |
| `test_original.bin` execution | ✅ PASS (shows "Pass success") |
| `.bin2` file recognition by DAP FMM | ✅ PASS (execute button enabled) |
| `test_valid.bin2` signature verification | ❌ FAIL (ERR-10: SIG FAIL) |
| `test_tampered.bin2` rejection | ❌ BLOCKED (signature check reached before hash check) |
| `test_badsig.bin2` rejection | ✅ EXPECTED failure, but for wrong reason |
