# TM-031 Session Log

**Date:** 2026-03-19
**Memo:** TM31 — External Deliverable Packaging

---

## Changes Made

### New Files
| File | Purpose |
|------|---------|
| `AIOS/tools/export_zkw_output.py` | 6-step export pipeline (PAC + SDK + lib + demo + MANIFEST + security scan) |
| `AIOS/docs/security/export_inventory.md` | Asset classification (Class A/B/C) |
| `AIOS/docs/runbooks/dap_app_developer_guide.md` | APP 开发者手册 |
| `AIOS/feedback/TM-031-clarification.md` | 5 clarification Q&A |
| `AIOS/feedback/TM-031-feedback.md` | Feedback artifact |
| `zkw_output_pac_code/` | Exported deliverable (PAC + SDK + lib + demo) |

### Key Design Decisions
- **Q1=C:** PAC from internal, no libdap.a
- **Q2=Custom:** OEM gets pac/img, AI IDE for devs
- **Q3:** One source tree + two build modes
- **Q4=B:** Manual export script execution
- **Q5=A:** No dap.mk in zkw_output

### Bugs Fixed
- **build.bat path issue:** Relative paths broke in zkw_output → generate standalone build.bat
- **Entry.c dependency:** Entry.c needs core/DAP_Application.h → ship pre-compiled Entry.o + Start.o
- **Unicode encoding:** Windows GBK console can't print emojis → replaced with ASCII

## Verification Results
- [x] Export script runs clean
- [x] Security scan: zero Class A content in zkw_output
- [x] Demo APP compiles from zkw_output
- [ ] Device flash + BIN execution (deferred — same PAC already verified in TM-030)
