# TM-032 Phase 1 Session Log

**Date:** 2026-03-20
**Memo:** TM-032 Phase 1 — External Binary Hardening (Strip + Strings Scan + SECURE Build)

---

## Changes Made

### New Files
| File | Purpose |
|------|---------|
| `project_ums9117_240X320BAR_64MB_ML_SECURE.mk` | SECURE build profile (继承 ML.mk + EXTERNAL_BUILD=TRUE) |
| `AIOS/docs/security/strings_watchlist.txt` | 22 个敏感 strings 扫描模式 |
| `AIOS/docs/runbooks/secure_build_guide.md` | SECURE build 操作手册 |
| `lib/ums9117_240X320BAR_64MB_ML_SECURE` | Junction → 原始 lib 目录 |

### Modified Files
| File | Change |
|------|--------|
| `make/dap/dap.mk` | `ifeq EXTERNAL_BUILD` 条件分支：external 禁用 trace + debug |
| `AIOS/tools/export_zkw_output.py` | SECURE PAC 优先、fromelf strip、strings 扫描 |
| `make/perl_script/sprd_macro_check.pl` | `return 1` → `exit 0` (Perl bug fix) |
| `Third-party/DAP/apps/hello_bigseek/build.bat` | 修复 SDK boundary check 误判 |

## Bugs Fixed
1. **sprd_macro_check.pl**: `return` outside subroutine → `exit 0`
2. **lib/ junction**: Unisoc 按项目名查找 200+ vendor .a → junction 解决
3. **build.bat findstr**: 注释中 `core/` 触发误判 → 改为只检查 `#include` 行

## Verification Results
- [x] SECURE build: `mm ums9117_240X320BAR_64MB_ML_SECURE new` 编译通过
- [x] Internal build: `mm ums9117_240X320BAR_64MB_ML new` 编译通过（不受影响）
- [x] SECURE PAC: BIN 执行正常
- [x] SECURE PAC: BIN2 执行正常 (签名+绑定验证通过)
- [x] Internal PAC: BIN 执行正常
- [x] Internal PAC: BIN2 执行正常 (签名+绑定验证通过)
- [x] Export pipeline: 安全扫描 PASS + strings 扫描 PASS
- [ ] SECURE PAC: BIN3 — 需要 device_secret（defer to TM-032-2）
- [ ] Trace hardening — SCI_TRACE_MODE 移除未生效（defer to TM-032-3）
