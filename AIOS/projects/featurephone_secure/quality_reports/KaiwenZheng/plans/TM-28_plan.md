# Implementation Plan — TM-28 BIN2 Payload Encryption

## File Changes

| Action | File | Module | Description |
|--------|------|--------|-------------|
| MODIFY | [bin2_format.h](file:///c:/zkwwork/featurephoneosreconstruction/Third-party/DAP/security/bin2_format.h) | Security | Header 64→96B, v3, `payload_enc_mode`, `enc_reserved`, `payload_iv[16]`, `reserved2[14]`, new error codes |
| CREATE | `Third-party/DAP/security/dap_aes.h` | Security | AES-128 interface (dap_aes_ prefix), CTR-only |
| CREATE | `Third-party/DAP/security/dap_aes.c` | Security | tiny-AES-c port, stripped to AES-128-CTR, `dap_aes_` prefix |
| CREATE | `Third-party/DAP/security/bin2_crypto_payload.h` | Security | `bin2_payload_derive_key()`, `bin2_payload_decrypt()` interface |
| CREATE | `Third-party/DAP/security/bin2_crypto_payload.c` | Security | KDF implementation + AES-CTR wrapper |
| MODIFY | [bin2_loader.c](file:///c:/zkwwork/featurephoneosreconstruction/Third-party/DAP/security/bin2_loader.c) | Security | Add decrypt dispatch after binding verify, log `tm28_*` traces |
| MODIFY | [DAP_Loader_unisoc.c](file:///c:/zkwwork/featurephoneosreconstruction/Third-party/DAP/platform/unisoc/DAP_Loader_unisoc.c) | Loader | Update `bin2_payload_off` usage, add `BIN2_ERR_DECRYPT` mapping |
| MODIFY | [DAP_FMM_Integration.c](file:///c:/zkwwork/featurephoneosreconstruction/Third-party/DAP/platform/unisoc/DAP_FMM_Integration.c) | FMM | Add `.bin3` extension check, new DAP_ERR mapping |
| MODIFY | [dap.mk](file:///c:/zkwwork/featurephoneosreconstruction/make/dap/dap.mk) | Build | Add `dap_aes.c`, `bin2_crypto_payload.c` to SOURCES |
| MODIFY | [bin2_pack.py](file:///c:/zkwwork/featurephoneosreconstruction/AIOS/tools/bin2_packer_v2/bin2_pack.py) | Packer | v3 header, AES-CTR encrypt, `--encrypt` flag, random IV |
| MODIFY | [generate_test_bins_v2.py](file:///c:/zkwwork/featurephoneosreconstruction/AIOS/tools/bin2_packer_v2/generate_test_bins_v2.py) | Packer | Add encrypted bound test cases |
| CREATE | `AIOS/docs/architecture/bin2_payload_encryption.md` | Docs | Architecture document per TM-28 requirement |

## Module Impact

- **Security module** → 4 new files + 2 modified files; header size change cascades to all consumers
- **Loader** → offset constant change (`BIN2_PAYLOAD_OFFSET` 128→160); decrypt call insertion
- **FMM** → extension gate + error message mapping
- **Build** → 2 new `.c` files in SOURCES
- **PC tools** → packer format upgrade (must stay backward-compatible for `--verify` of v2 files)

## Risk Areas

1. **Payload offset desync** — Header size change from 64→96 means `BIN2_PAYLOAD_OFFSET` = 96+64 = 160. Must be consistent across `bin2_format.h`, `bin2_pack.py`, `generate_test_bins_v2.py`, `DAP_Loader_unisoc.c` BSS reread path
2. **AES-CTR counter parity** — Python `Crypto.Cipher.AES` CTR mode and tiny-AES-c must use identical counter increment. Need known-answer test
3. **Symbol collision** — `dap_aes_` prefix required (same pattern as SHA-256 collision fix)
4. **In-place decrypt buffer safety** — Must not introduce new malloc/free paths

## ⚠️ Pitfall Briefing

### Matched Pitfalls (8 items)

| # | Pitfall | Relevance | Prevention |
|---|---------|-----------|------------|
| 1 | **⚠️ dap.mk flags missing** (3x recurrence) | TM-28 adds 2 new `.c` files | Add `dap_aes.c`, `bin2_crypto_payload.c` to SOURCES; run dap_mk_checklist |
| 2 | **SHA-256 symbol collision** | TM-28 adds AES implementation | All AES symbols: `dap_aes_` prefix |
| 3 | **BIN2 pointer offset heap corruption** | Header size change alters all payload offsets | In-place decrypt only; no new malloc; verify `alloc_base` unaffected |
| 4 | **BSS realloc file offset** | `bin2_payload_off` changes from 128→160 | Update `DAP_Loader_unisoc.c` L466 seek offset |
| 5 | **FMM extension filter** | New `.bin3` extension | Add `.bin3` check in `DAP_FMM_IsBinFile` |
| 6 | **Signed region consistency** | Packer now encrypts before signing | Verify PC/device signed region hash match via `tm15_msg_hash` |
| 7 | **Signed region diagnostic format alignment** | New encryption fields in debug output | Add matching `tm28_*` debug output in both Python packer and C loader |
| 8 | **Ed25519 PC↔device compat** | Signature covers encrypted payload now | Verify with known-answer test: sign encrypted payload, verify on device |

### Applicable Runbooks
- [ ] [dap_mk_checklist](file:///c:/zkwwork/featurephoneosreconstruction/AIOS/docs/runbooks/dap_mk_checklist.md) — After adding new source files
- [ ] [bin2_migration_checklist](file:///c:/zkwwork/featurephoneosreconstruction/AIOS/docs/runbooks/bin2_migration_checklist.md) — Before device deployment

### Key Decisions to Respect
- **ADR-001**: All DAP crypto symbols use `dap_` prefix
- **ADR-002**: Signature message = header + zeros(sig_size) + payload (now encrypted payload)
- **ADR-003**: All DAP logging via `DAP_DBG` → `DAP_TracePrint` → `SCI_TRACE_LOW`
- **ADR-004**: `alloc_base` tracks original malloc pointer; all free uses `alloc_base`
- **ADR-005**: BSS reread must use `bin2_payload_off` for BIN2/BIN3 files

### Engineer-Specified Pitfalls (TM-28 Clarification Session)
- **Pitfall A**: All payload offset references must be synchronized across packer/loader/BSS/debug tools
- **Pitfall B**: AES-CTR counter byte order and increment rule must be identical Python↔C
- **Pitfall C**: Review Ed25519 pitfalls in `AIOS/docs/pitfalls/` before starting

## Execution Order

1. **bin2_format.h** — Header expansion to 96B, version 3, new constants (all downstream depends on this)
2. **dap_aes.h/c** — Port tiny-AES-c AES-128-CTR (no downstream dependency yet)
3. **bin2_crypto_payload.h/c** — KDF + AES-CTR wrapper (depends on 1+2)
4. **bin2_loader.c** — Add decrypt dispatch (depends on 1+3)
5. **DAP_Loader_unisoc.c** — Update offset, add decrypt error mapping (depends on 1+4)
6. **DAP_FMM_Integration.c** — `.bin3` extension + error messages (depends on 5)
7. **dap.mk** — Add new source files (depends on 2+3)
8. **bin2_pack.py** — v3 packer with encryption (depends on 1)
9. **generate_test_bins_v2.py** — Encrypted test case generation (depends on 8)
10. **Architecture doc** — `bin2_payload_encryption.md`

## Verification Plan

### Automated Tests (PC-side)
1. **Packer unit test**: `python bin2_pack.py test_input.bin test_enc.bin3 --bind-file device.bind --encrypt -v --debug` → verify output is valid v3 with encrypted payload
2. **Packer verify test**: `python bin2_pack.py --verify test_enc.bin3 --pubkey public_key.bin -v` → VERIFY OK
3. **Known-answer CTR test**: Create `AIOS/tools/bin2_packer_v2/test_aes_ctr_kat.py` — encrypt a fixed key+IV+plaintext, compare output against expected ciphertext (same expected values will be used in C unit test)

### Manual Device Verification (engineer performs)
1. Flash firmware with TM-28 changes compiled
2. Copy `.bin3` test files to device via USB
3. Run each test case, observe Logel traces:
   - `test_valid_bound_enc.bin3` on same device → **PASS**, Logel shows `tm28_decrypt_ok`
   - `test_valid_bound_enc.bin3` on different device → **FAIL** binding mismatch
   - `test_tampered_bound_enc.bin3` → **FAIL** signature fail
   - `test_badsig_bound_enc.bin3` → **FAIL** signature fail
4. Run old v2 test cases to confirm regression-free:
   - `test_unbound.bin2` → PASS
   - `test_bound.bin2` → PASS on bound device
   - `test_tampered.bin2` → FAIL
