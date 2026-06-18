# Frozen Specification — TM-15 BIN2 Secure Loader Phase 0

## Background

The current DAP loader (`DAP_ExecuteAP()`) executes any BIN file without authentication. Phase-0 introduces a BIN2 format with Ed25519 digital signatures so that only authorized BIN2 files can execute, while BIN1 files continue to work in dev mode.

### BIN2 File Layout
```
[BIN2 Header (48 bytes)] [Ed25519 Signature (64 bytes)] [Original BIN1 Data]
```

The BIN2 header is **prepended** to the original BIN1 data. The original `TApplication` structure is NOT modified.

---

## MUST

- [ ] **M1**: Define `BIN2_Header` struct in `bin2_format.h` (magic "BIN2", version, header_size, payload_size, key_id=0, binding_mode=0, reserved, payload_hash[32])
- [ ] **M2**: Implement `bin2_detect()` — check 4-byte magic "BIN2" at buffer start, return BIN2 or BIN1
- [ ] **M3**: Implement `bin2_verify_signature()` — Ed25519 verify over (header_without_signature + payload)
- [ ] **M4**: Implement `bin2_verify_hash()` — SHA256(payload) == header.payload_hash
- [ ] **M5**: Implement `bin2_verify()` — orchestrate: parse header → verify_signature → verify_hash
- [ ] **M6**: Integrate early BIN2 detection in `DAP_ExecuteAP()` Step 3 (after TApplication header read — check first 4 bytes for "BIN2" magic)
- [ ] **M7**: Integrate full BIN2 verification in `DAP_ExecuteAP()` Step 5 (after full file read to RAM — call `bin2_verify()`)
- [ ] **M8**: On BIN2 verify success, strip BIN2 header+signature so downstream code sees a normal BIN1 in memory
- [ ] **M9**: On BIN2 verify failure, set `*Result = DAP_ERR_SECURITY` or `DAP_ERR_SIGNATURE` / `DAP_ERR_HASH` and goto error_exit
- [ ] **M10**: BIN1 files continue to execute without any security checks (dev mode backward compatibility)
- [ ] **M11**: Add error codes: `DAP_ERR_SECURITY (-9)`, `DAP_ERR_SIGNATURE (-10)`, `DAP_ERR_HASH (-11)` to `DAP_Loader_unisoc.h`
- [ ] **M12**: Update `DAP_FMM_Integration.c` switch statement to handle new error codes with GUI messages
- [ ] **M13**: Hardcode Ed25519 public key (32 bytes) in `bin2_crypto.c`
- [ ] **M14**: Include minimal Ed25519 verify + SHA256 pure-C implementation (ed25519-donna verify subset or TweetNaCl minimal)
- [ ] **M15**: Add debug logs: "BIN2 detected", "BIN2 verify success", "BIN2 verify failed: signature", "BIN2 verify failed: hash"
- [ ] **M16**: Create Python `tools/bin2_packer/bin2_pack.py` — takes BIN1 input, produces BIN2 output (sign + hash + prepend header)
- [ ] **M17**: Generate test BIN2 sample files (valid, tampered payload, wrong signature)

## SHOULD

- [ ] **S1**: Verify BIN2 header field consistency (version, header_size, payload_size match expectations)
- [ ] **S2**: Guard `bin2_detect()` against files smaller than `sizeof(BIN2_Header)` — treat as BIN1
- [ ] **S3**: Constant-time signature comparison (avoid timing side-channels)

## MAY

- [ ] **Y1**: Print BIN2 header metadata in debug log (version, payload_size, key_id)
- [ ] **Y2**: Add `--verbose` flag to Python packer

## OUT OF SCOPE

- Device binding (DeviceSecret / `binding_mode = 1`)
- AES-CTR payload encryption
- Key rotation / revocation
- App Store / remote download
- Modification of `TApplication` structure

---

## Proposed Changes

### Component 1: BIN2 Security Module (`Third-party/DAP/security/`)

#### [NEW] [bin2_format.h](file:///c:/zkwwork/featurephoneosreconstruction/Third-party/DAP/security/bin2_format.h)
- `BIN2_Header` struct, magic constant, `BIN2_HEADER_SIZE`, `BIN2_SIGNATURE_SIZE`
- Return codes: `BIN2_OK`, `BIN2_ERR_*`

#### [NEW] [bin2_loader.h](file:///c:/zkwwork/featurephoneosreconstruction/Third-party/DAP/security/bin2_loader.h)
- Function declarations: `bin2_detect()`, `bin2_verify()`, `bin2_get_payload_offset()`

#### [NEW] [bin2_loader.c](file:///c:/zkwwork/featurephoneosreconstruction/Third-party/DAP/security/bin2_loader.c)
- `bin2_detect()` — 4-byte magic check
- `bin2_verify()` — orchestrate signature + hash verify
- `bin2_get_payload_offset()` — return `sizeof(BIN2_Header) + 64` (header + signature)

#### [NEW] [bin2_crypto.h](file:///c:/zkwwork/featurephoneosreconstruction/Third-party/DAP/security/bin2_crypto.h)
- `bin2_verify_signature()`, `bin2_verify_hash()` declarations

#### [NEW] [bin2_crypto.c](file:///c:/zkwwork/featurephoneosreconstruction/Third-party/DAP/security/bin2_crypto.c)
- Hardcoded Ed25519 public key
- `bin2_verify_signature()` — calls ed25519 verify on (header + payload) against signature
- `bin2_verify_hash()` — SHA256 of payload vs header.payload_hash

#### [NEW] [ed25519/](file:///c:/zkwwork/featurephoneosreconstruction/Third-party/DAP/security/ed25519/)
- Minimal ed25519-donna verify-only subset (pure C, no dependencies)

#### [NEW] [sha256.c](file:///c:/zkwwork/featurephoneosreconstruction/Third-party/DAP/security/sha256.c) / [sha256.h](file:///c:/zkwwork/featurephoneosreconstruction/Third-party/DAP/security/sha256.h)
- Lightweight SHA256 pure-C implementation

---

### Component 2: DAP Loader Integration

#### [MODIFY] [DAP_Loader_unisoc.h](file:///c:/zkwwork/featurephoneosreconstruction/Third-party/DAP/platform/unisoc/DAP_Loader_unisoc.h)
- Add `DAP_ERR_SECURITY (-9)`, `DAP_ERR_SIGNATURE (-10)`, `DAP_ERR_HASH (-11)`

#### [MODIFY] [DAP_Loader_unisoc.c](file:///c:/zkwwork/featurephoneosreconstruction/Third-party/DAP/platform/unisoc/DAP_Loader_unisoc.c)
- Add `#include "../../security/bin2_loader.h"`
- **Step 3 modification**: After reading TApplication header (L286-293), check if first 4 bytes == "BIN2" magic. If yes, set `is_bin2 = TRUE` flag.
- **Step 5 modification**: After full file is loaded (L334), if `is_bin2`, call `bin2_verify()`. On failure, set error code and goto error_exit. On success, adjust `Running_AP` pointer and `file_size` to skip BIN2 header+signature, so downstream (Step 6+) sees raw BIN1.

#### [MODIFY] [DAP_FMM_Integration.c](file:///c:/zkwwork/featurephoneosreconstruction/Third-party/DAP/platform/unisoc/DAP_FMM_Integration.c)
- Add 3 new cases in error switch (L168-196): `DAP_ERR_SECURITY`, `DAP_ERR_SIGNATURE`, `DAP_ERR_HASH`

---

### Component 3: PC Packer Tool

#### [NEW] [bin2_pack.py](file:///c:/zkwwork/featurephoneosreconstruction/tools/bin2_packer/bin2_pack.py)
- CLI tool: `python bin2_pack.py input.bin output.bin2 --key private_key.bin`
- Generates Ed25519 keypair (if not exists), signs, creates BIN2

#### [NEW] [generate_test_bins.py](file:///c:/zkwwork/featurephoneosreconstruction/tools/bin2_packer/generate_test_bins.py)
- Generates test samples: valid BIN2, tampered payload, wrong signature, original BIN1

#### [NEW] [README.md](file:///c:/zkwwork/featurephoneosreconstruction/tools/bin2_packer/README.md)
- Usage instructions

---

## Risk Areas

1. **Ed25519 code size** — Verify the minimal implementation fits within firmware code budget. Mitigation: use ed25519-donna verify-only (no keygen/sign), strip unused functions.
2. **Memory for verification** — BIN2 verify requires the full file in RAM (already true in current loader). Additional stack usage for SHA256 context (~104 bytes) is minimal.
3. **Endianness** — ARM Cortex on Mocor is little-endian. Ensure BIN2 header fields are stored little-endian. Python packer must match.
4. **Pointer arithmetic for BIN1 extraction** — After stripping BIN2 header+signature, the `Running_AP` pointer offset must be exact. Off-by-one would corrupt the TApplication structure. Mitigation: `bin2_get_payload_offset()` returns a tested constant.

## Verification Plan

### On-Device Testing (Real Device — Primary)

The engineer will flash the firmware and test with 4 sample files generated by the Python packer:

| Test | File | Expected Result | Expected Log |
|------|------|----------------|--------------|
| Case 1 | `test_valid.bin2` | App runs, shows "execute success" | `BIN2 detected`, `BIN2 verify success` |
| Case 2 | `test_tampered.bin2` | Rejected, GUI shows ERR | `BIN2 verify failed: hash` |
| Case 3 | `test_original.bin` | App runs (BIN1 dev mode) | No BIN2 logs |
| Case 4 | `test_badsig.bin2` | Rejected, GUI shows ERR | `BIN2 verify failed: signature` |

### Python Packer Verification (PC — Local)

```bash
cd tools/bin2_packer
python bin2_pack.py --generate-keys
python bin2_pack.py test_app.bin test_valid.bin2 --key private_key.bin
python generate_test_bins.py test_app.bin  # produces all 4 test files
```

Verify output file sizes and header magic manually with hex editor or:
```bash
python -c "f=open('test_valid.bin2','rb'); print(f.read(4)); f.close()"
# Should print: b'BIN2'
```

---

Approved by: _______________
Date: _______________
