# Pitfall: Build Chain File Copy Without dap.mk Merge

**ID**: PF-TM03-02
**Date**: 2026-03-26
**Author**: KaiwenZheng
**Project**: demo_merge
**Severity**: HIGH
**Category**: Build System

## Symptom
After copying James's `dap.mk` to mainline, compilation produces 17+ linker errors: undefined symbols for `bin2_detect`, `device_secret_init`, `OS_GetRegMaxItemCount`, `OS_MemMalloc`, etc.

## Root Cause
James's `dap.mk` is a **subset** of our mainline version. It does NOT include:
1. Security module files (12 .c files: crc32, device_identity, bin2_loader, ed25519, etc.)
2. Security include/source paths (`Third-party/DAP/security/`)
3. Build mode gating (`EXTERNAL_BUILD` / `SECURITY_DEBUG_MENU`)
4. OS compatibility layer (`DAP_UNISOC_OSAssociated.c`, `DAP_UNISOC_OSAPI_Register.c`)

Directly replacing our dap.mk with James's version **strips our security infrastructure**.

## Fix
**Never blindly replace dap.mk.** Instead, merge both versions:
- Keep mainline security section intact
- Add James's new entries (T9, VA, bigseek_core, downloader)
- Fix paths (e.g., `Third-party/bigseek_core/` → `Third-party/DAP/bigseek_core/`)
- Keep core file references (`DAP_InterfaceRegister.c`, `DAP_Loader_unisoc.c`)

## Prevention
- Before replacing any `.mk` file, always diff against the mainline backup first
- dap.mk is a "merge-only" file — never overwrite, always merge
- The security module files are the FIRST thing to check when link errors mention `bin2_*` or `device_*`
