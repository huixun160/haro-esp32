# Feedback — TM-015: BIN2 Secure Loader Integration

**Date:** 2026-03-10
**Memo:** Technical_Memo_15_ko3_bin2withnosecureid.md
**Outcome:** PARTIAL
**Author:** DAP Security Team

---

## Execution Summary

Integrated the BIN2 secure loader into the DAP firmware. Compilation succeeds and `.bin2` files are recognized. However, Ed25519 signature verification fails on-device for all `.bin2` files, blocking full validation.

---

## Completed Work

- [x] BIN2 source files created (`bin2_loader.c`, `bin2_crypto.c`, `sha256.c`, `ed25519_verify.c`)
- [x] Build system updated (`dap.mk`)
- [x] `DAP_FMM_IsBinFile` extended to accept `.bin2`
- [x] `DAP_Loader_unisoc.c` extended with BIN2 detection, verification, payload stripping
- [x] SHA-256 symbols prefixed with `dap_` to avoid SSV WiFi collision
- [x] `DAP_TracePrint` fixed to properly format varargs
- [x] Python packer tool created (`bin2_pack.py`)
- [x] Test binaries generated (valid, tampered, badsig)
- [x] `test_original.bin` executes successfully on device

---

## Incomplete Work

- [ ] Ed25519 signature verification — fails with -1 for all inputs on device. TweetNaCl-derived implementation has suspected 64-bit arithmetic issue on 32-bit ARM.
- [ ] Logel trace verification — `DAP_TracePrint` fix deployed but not verified on device yet.

---

## Blocking Issues

| Issue | Symptom | Root Cause | Suggested Resolution |
|---|---|---|---|
| Ed25519 verify fails | All `.bin2` return ERR-10 (SIG FAIL), including valid ones | TweetNaCl Ed25519 implementation likely has 64-bit arithmetic bugs on 32-bit ARM | Debug with hex dump diagnostics; or replace with platform crypto API; or use HMAC-SHA256 as interim |

---

## Verification Status

| Test | Result | Notes |
|---|---|---|
| Full firmware compilation | ✅ PASS | |
| `test_original.bin` execution | ✅ PASS | Shows "Pass success" |
| `.bin2` file FMM recognition | ✅ PASS | Execute button enabled |
| `test_valid.bin2` verification | ❌ FAIL | ERR-10: SIG FAIL |
| `test_tampered.bin2` rejection | ⏭️ SKIP | Blocked by sig check |
| `test_badsig.bin2` rejection | ⚠️ PARTIAL | Fails at sig (expected), but valid also fails |

---

## Next Actions

1. **Debug Ed25519 on ARM** — Add hex dump diagnostics (already in code) and verify via Logel
2. **Consider HMAC-SHA256 alternative** — Simpler crypto, no 64-bit arithmetic, uses existing `dap_sha256`
3. **Verify Logel traces** — Confirm `tm15_` diagnostic logs appear after `DAP_TracePrint` fix
4. **Write dedicated debugging memo** — Focus on Ed25519 ARM implementation

---

## Files Changed

| File | Action | Description |
|---|---|---|
| `Third-party/DAP/security/bin2_loader.c` | Created | BIN2 detection and verification |
| `Third-party/DAP/security/bin2_crypto.c` | Created | Ed25519 + SHA-256 verification |
| `Third-party/DAP/security/sha256.c/h` | Created | SHA-256 (dap_ prefixed) |
| `Third-party/DAP/security/ed25519/` | Created | Ed25519 verify implementation |
| `make/dap/dap.mk` | Modified | Added BIN2 sources |
| `DAP_FMM_Integration.c` | Modified | Added .bin2 extension |
| `DAP_Loader_unisoc.c/h` | Modified | BIN2 pipeline integration |
| `DAP_OSAssociated_unisoc.c` | Modified | Fixed DAP_TracePrint |
| `AIOS/tools/bin2_packer/` | Created | Python packer + test bins |

---

## References

- Related pitfalls: `sha256_symbol_collision.md`, `sci_trace_low_unavailable.md`, `dap_traceprint_varargs_bug.md`, `dap_fmm_extension_filter.md`
- Related decisions: ADR-001, ADR-002, ADR-003
- Session log: `quality_reports/session_logs/TM-15_session.md`
