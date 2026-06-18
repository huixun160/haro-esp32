# TM-030 Session Log

**Date:** 2026-03-19
**Engineer:** KaiwenZheng
**Memo:** TM30 — Internal SDK Boundary Freeze (DAP ABI Stabilization v0)

---

## Changes Made

### New Files
| File | Purpose |
|------|---------|
| `sdk/dap_api.h` | v0 frozen ABI — 7 macro wrappers over FindInterface |
| `AIOS/docs/sdk/dap_abi_v0.md` | ABI freeze specification + RWPI constraint |
| `AIOS/feedback/TM-030-clarification.md` | 5 clarification Q&A |

### Modified Files
| File | Change |
|------|--------|
| `apps/hello_bigseek/main.c` | Migrated to `dap_api.h` only (golden sample) |
| `apps/hello_bigseek/build.bat` | Added ARM PATH, SDK-only include, findstr boundary check |
| `AIOS/MEMORY.md` | TM-030 key decision + RWPI pitfall |

### Moved Files
| Source | Destination |
|--------|-------------|
| `apps/demo_ui/` | `apps/_legacy/demo_ui/` |
| `apps/hello_lvgl/` | `apps/_legacy/hello_lvgl/` |
| `apps/lvgl_template/` | `apps/_legacy/lvgl_template/` |
| `apps/mp3_player/` | `apps/_legacy/mp3_player/` |
| `apps/pass_success/` | `apps/_legacy/pass_success/` |
| `apps/snake/` | `apps/_legacy/snake/` |
| `apps/tetris/` | `apps/_legacy/tetris/` |
| `apps/voice_recorder/` | `apps/_legacy/voice_recorder/` |

### Unchanged (Critical)
- `sdk/Entry.c` — NOT modified (RWPI constraint prevents adding static vars)

---

## Bugs Encountered

### BUG-1: Static Variable Crash (SCI_PAssert)
- **Symptom:** BIN executes, jumps to Entry, immediately SCI_PAssert
- **Root Cause:** DAP loader does NOT relocate RW data. Static variables in APP code reference un-relocated addresses → crash
- **Fix:** Redesigned `dap_api.h` from static inline functions (with static vars) to pure macros (zero static vars). All API macros take `cmd` as parameter.
- **Iterations:** 3 attempts before root cause identified via loader source analysis

---

## Verification Results

| Test | Result |
|------|--------|
| hello_bigseek.bin (direct) | ✅ "Hello AIOS v0" popup |
| hello_sdk_v0.bin2 (signed) | ✅ Verified OK |
| hello_sdk_v0.bin3 (encrypted+bound) | ✅ BIND MATCH + decrypt OK |
| Logel trace `dap_api.h v0 OK` | ✅ Confirmed |
| `DAP_ExecuteAP result=0` | ✅ Success return |
| SDK boundary check (findstr) | ✅ PASS |
