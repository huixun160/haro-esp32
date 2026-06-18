# Sync Summary — TM-15: BIN2 Secure Loader Integration

**Generated:** 2026-03-10
**Memo:** Technical_Memo_15_ko3_bin2withnosecureid.md
**Status:** Partially Complete (Ed25519 verification pending)

---

## New APIs Added

| API | Layer | Status | Verified |
|---|---|---|---|
| `DAP_FMM_IsBinFile` | Adapter → DAP | beta | ✅ Yes |
| `DAP_TracePrint` | DAP → OS | beta | ✅ Yes (varargs fix) |

## Modified APIs

| API | Change |
|---|---|
| `sha256_hash` → `dap_sha256_hash` | Renamed with `dap_` prefix to avoid SSV WiFi collision |

## New Modules

| Module | Layer | Source |
|---|---|---|
| `bin2_loader` | dap_core | `Third-party/DAP/security/bin2_loader.c` |
| `bin2_crypto` | dap_core | `Third-party/DAP/security/bin2_crypto.c` |
| `ed25519_verify` | dap_core | `Third-party/DAP/security/ed25519/ed25519_verify.c` |
| `dap_sha256` | dap_core | `Third-party/DAP/security/sha256.c` |
| `bin2_packer` | tools | `AIOS/tools/bin2_packer/bin2_pack.py` |

## New Decisions (ADRs)

| ID | Title |
|---|---|
| ADR-001 | SHA-256 symbols prefixed with `dap_` |
| ADR-002 | BIN2 signature message = header + zeros(64) + payload |
| ADR-003 | DAP security modules use `DAP_DBG`, not `SCI_TRACE_LOW` |

## New Pitfalls

| Pitfall | Severity |
|---|---|
| SHA-256 symbol collision with SSV WiFi | High |
| `SCI_TRACE_LOW` macro unavailable in DAP security files | Medium |
| `DAP_TracePrint` varargs ignored | Medium |
| `DAP_FMM_IsBinFile` extension filtering blocks new formats | High |

## Open Issues for Next Memo

1. **Ed25519 signature verification fails on ARM** — TweetNaCl-derived implementation returns -1 for all inputs on device. Needs dedicated debugging (likely 64-bit arithmetic issue on 32-bit ARM).
2. **Logel trace visibility** — `DAP_TracePrint` fix deployed but not yet verified on device.
