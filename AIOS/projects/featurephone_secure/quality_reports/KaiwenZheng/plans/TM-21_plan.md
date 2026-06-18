# Implementation Plan — TM-21: BIN2 Signature Verification Failure Root Cause Isolation and Fix

## File Changes

| Action | File | Module | Description |
|--------|------|--------|-------------|
| MODIFY | `Third-party/DAP/security/bin2_crypto.c` | DAP/Security | Add SHA-256 message hash diagnostic, signed region analysis trace |
| MODIFY | `AIOS/tools/bin2_packer/bin2_pack.py` | Tools | Add `--debug` mode with same-caliber diagnostic output |
| CREATE | `docs/tm15_sigfail_rootcause.md` | Docs | Root cause analysis document |
| CREATE | `docs/tm15_sigfix_validation.md` | Docs | Device verification record (engineer fills in after device test) |

## Module Impact

- **DAP/Security (`bin2_crypto.c`)** — Added diagnostic SHA-256 hash of the signed region (`header + zeros + payload`) to enable PC↔device comparison without changing the verification logic itself.
- **Tools (`bin2_pack.py`)** — Added `--debug` flag that outputs diagnostic info matching device-side trace format for side-by-side comparison.
- **No changes to `ed25519_verify.c`** — We do NOT modify the Ed25519 implementation first. Per the memo's execution order: fix message first, then investigate crypto.

## Analysis Summary

### Code Review Findings

After thorough analysis of both PC-side and device-side code, the signed message construction appears **logically consistent** on both sides:

**PC side (`bin2_pack.py` line 130):**
```python
message = header + sig_placeholder + payload  # sig_placeholder = b'\x00' * 64
```

**Device side (`bin2_crypto.c` lines 186-194):**
```c
// 临时清零 signature 区域
for (i = 0; i < BIN2_SIGNATURE_SIZE; i++) { mut_sig_area[i] = 0; }
// Ed25519 验证：message = buffer[0..total_size-1]（signature 区域已清零）
result = ed25519_verify(saved_sig, (const uint8 *)header, total_size, BIN2_PUBLIC_KEY);
```

Both sides construct: `header(48) + zeros(64) + payload`, which matches ADR-002.

### Potential Root Causes (ranked by likelihood)

1. **Ed25519 C implementation bug** — The `ed25519_verify.c` is a custom TweetNaCl-derived implementation with a complex manual incremental SHA-512 hash. The padding / finalization logic in lines 562-614 is particularly complex and error-prone.
2. **Public key mismatch** — The hardcoded `BIN2_PUBLIC_KEY[32]` in `bin2_crypto.c` may not match the `public_key.bin` used by the packer.
3. **PyNaCl vs TweetNaCl Ed25519 incompatibility** — PyNaCl uses `libsodium` which prefixes the message internally (Ed25519 signs `R || A || M`), while the custom C implementation may have a different internal convention.

### Investigation Strategy

The code changes below follow the memo's mandated execution order:
1. **Keep trace alive** — don't break existing logging
2. **Add message hash comparison** — SHA-256 of the signed region on both sides
3. **Check if message matches** — this determines if root cause is A (message mismatch) or B (crypto impl issue)
4. **Only then investigate Ed25519** — if messages match but verify still fails

## Risk Areas

1. **Stack usage in `bin2_crypto.c`** — Adding SHA-256 hash computation increases stack usage. `dap_sha256_hash()` uses `DAP_SHA256_CTX` (about 100 bytes) plus a 32-byte output buffer. Total additional stack: ~140 bytes. Safe for Mocor task stacks.
2. **Log truncation** — Must keep each log line < 128 chars per constraints. The hash dump of 8 bytes = `tm15_msg_hash[0..7]=xx xx xx xx xx xx xx xx` (52 chars) — safe.
3. **Build regression** — No new `.c` files, so `dap.mk` doesn't need `MSRCPATH` changes. But must verify `dap.mk` checklist.

## ⚠️ Pitfall Briefing

### Matched Pitfalls (5 items)

| # | Pitfall | Relevance | Prevention |
|---|---------|-----------|------------|
| 1 | **⚠️ dap.mk 编译开关遗漏 (3次复发)** | TM-21 modifies `bin2_crypto.c` — must verify `-DSCI_TRACE_MODE` still present | Run `dap_mk_checklist.md` after all code changes |
| 2 | SCI_TRACE_LOW unavailable in DAP security | `bin2_crypto.c` uses `DAP_DBG` (correct) and `BIN2_LOG` (direct `SCI_TRACE_LOW` via `dap_security_log.h` which includes `os_api.h`). Both paths verified. | Use `DAP_DBG` or `BIN2_LOG` only, never raw `SCI_TRACE_LOW` |
| 3 | DAP_TracePrint varargs bug | Already fixed. But new `DAP_DBG` calls with `%02x` format must be validated. | Ensure format specifiers match argument types exactly |
| 4 | SHA-256 symbol collision | `dap_sha256_hash` already prefixed. Adding a new call is safe. | Use `dap_sha256_hash()` not `sha256_hash()` |
| 5 | SCI_TRACE_MODE missing | Must verify `-DSCI_TRACE_MODE` in `dap.mk` | Check `dap.mk` MCFLAG_OPT line |

### Applicable Runbooks

- [ ] `dap_mk_checklist.md` — Execute after all code changes, before build verification

### Key Decisions to Respect

- **ADR-002**: message = header(48) + zeros(64) + payload — signature area zeroed, rest of file intact
- **ADR-003**: All DAP modules use `DAP_DBG`/`DAP_DBG_ERR` → `DAP_TracePrint` → `SCI_TRACE_LOW`. Never call `SCI_TRACE_LOW` directly (note: `dap_security_log.h` BIN2_LOG macro does call it directly but includes `os_api.h`)
- **SHA-256 prefix**: All DAP SHA-256 symbols use `dap_` prefix

## Execution Order

1. **Add diagnostic SHA-256 hash in `bin2_crypto.c`** — Compute `dap_sha256_hash(signed_region, total_size, hash_buf)` and print first 8 bytes via `DAP_DBG`
2. **Add `--debug` mode in `bin2_pack.py`** — Print the same diagnostic info (signed region hash, offsets, hex dumps) for side-by-side comparison
3. **Review `dap.mk` checklist** — Verify no regression
4. **Create `docs/tm15_sigfail_rootcause.md`** — Document findings based on code analysis
5. **Create `docs/tm15_sigfix_validation.md`** — Template for engineer to fill in during device testing

## Verification Plan

### Automated Tests

**PC-side packer test** (can be run immediately):
```bash
cd c:\zkwwork\featurephoneosreconstruction\AIOS\tools\bin2_packer
python bin2_pack.py --verify test\test_valid.bin2 --pubkey public_key.bin --verbose --debug
python bin2_pack.py --verify test\test_tampered.bin2 --pubkey public_key.bin --verbose --debug
python bin2_pack.py --verify test\test_badsig.bin2 --pubkey public_key.bin --verbose --debug
```

Expected: `test_valid.bin2` → VERIFY OK; `test_tampered.bin2` → FAIL (hash); `test_badsig.bin2` → FAIL (signature). All should print diagnostic output.

### Manual Verification (Device — Engineer)

1. Build with `make\make_cmd\make -r -R MAKESHELL=CMD p=ums9117_240X320BAR_64MB_ML MODULES=dap JOB=16`
2. Verify 0 link errors, 0 undefined symbols
3. Flash firmware and deploy test files to device
4. Run each test file and capture Logel output:
   - `test_original.bin` → should execute normally (BIN1 mode)
   - `test_valid.bin2` → should show `tm15_BIN2 verify success` (if fix works) or `tm15_msg_hash` diagnostic info
   - `test_tampered.bin2` → should fail at signature or hash
   - `test_badsig.bin2` → should fail at signature
5. Compare `tm15_msg_hash[0..7]` from device with PC packer `--debug` output
6. Fill in `docs/tm15_sigfix_validation.md` with Logel excerpts
