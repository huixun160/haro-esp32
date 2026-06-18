#!/usr/bin/env python3
"""
export_zkw_output.py — TM-031 External Deliverable Export Pipeline

Usage:
    python export_zkw_output.py [--clean]

Exports internal DAP build products to zkw_output_pac_code/.
No DAP core/platform/security source code is exported.
"""

import os
import sys
import shutil
import hashlib
import datetime
import subprocess

# ─── Configuration ───────────────────────────────────────────────────────────

PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# PROJ_ROOT = c:\zkwwork\kz_fp_tm28r

OUTPUT_DIR = os.path.join(PROJ_ROOT, "zkw_output_pac_code")

# PAC location — from SECURE build (TM-032)
PAC_GLOB_DIR_SECURE = os.path.join(PROJ_ROOT, "build", "ums9117_240X320BAR_64MB_ML_SECURE_builddir", "img")
PAC_GLOB_DIR_INTERNAL = os.path.join(PROJ_ROOT, "build", "ums9117_240X320BAR_64MB_ML_builddir", "img")

# ARM DS-5 fromelf tool (TM-032-3)
FROMELF_PATH = r"C:\Program Files\DS-5 v5.26.0\sw\ARMCompiler5.06u4\bin\fromelf.exe"

# Strings watchlist (TM-032)
WATCHLIST_FILE = os.path.join(PROJ_ROOT, "AIOS", "docs", "security", "strings_watchlist.txt")

# SDK source (Class B — allowed, public API only)
SDK_DIR = os.path.join(PROJ_ROOT, "Third-party", "DAP", "sdk")
SDK_FILES = ["dap_api.h"]

# Pre-compiled bootstrap objects (Entry.c depends on core/ which is Class A)
PREBUILT_DIR = os.path.join(PROJ_ROOT, "Third-party", "DAP", "apps", "hello_bigseek", "out")
PREBUILT_FILES = ["Entry.o", "Start.o"]

# Demo APP source
DEMO_SRC = os.path.join(PROJ_ROOT, "Third-party", "DAP", "apps", "hello_bigseek")
DEMO_FILES = ["main.c", "build.bat"]

# ─── Forbidden patterns (Class A security check) ────────────────────────────

FORBIDDEN_PATTERNS = [
    "DAP_InterfaceRegister", "DAP_Loader_unisoc", "DAP_InstallOSAPI",
    "device_identity", "device_binding", "bin2_loader", "bin2_crypto",
    "sha256.c", "ed25519", "dap_aes", "DeviceSecret", "DAP_Application.h",
    "dap_audio_bridge", "DAP_FMM_Integration", "DAP_DebugLog",
]

FORBIDDEN_DIRS = ["core/", "platform/", "security/", "loader/"]

# ─── Helpers ─────────────────────────────────────────────────────────────────

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def get_git_commit():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=PROJ_ROOT, capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except:
        return "unknown"

def copy_file(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print("  [COPY] %s -> %s" % (os.path.relpath(src, PROJ_ROOT), os.path.relpath(dst, PROJ_ROOT)))

# ─── Steps ───────────────────────────────────────────────────────────────────

def step_clean():
    """Clean output directory"""
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
        print("[CLEAN] Removed %s" % OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def step_copy_pac():
    """Copy PAC firmware to output — prefer SECURE build, fallback to internal"""
    print("\n[STEP 1] Copying PAC...")
    pac_dir = os.path.join(OUTPUT_DIR, "out", "pac")
    os.makedirs(pac_dir, exist_ok=True)

    # Prefer SECURE builddir, fallback to internal
    pac_src = PAC_GLOB_DIR_SECURE
    label = "SECURE"
    if not os.path.exists(pac_src):
        pac_src = PAC_GLOB_DIR_INTERNAL
        label = "INTERNAL (fallback)"
        print("  [WARN] SECURE builddir not found, using internal PAC")
        print("         Run: mm ums9117_240X320BAR_64MB_ML_SECURE new")

    found = False
    if os.path.exists(pac_src):
        for f in os.listdir(pac_src):
            if f.endswith(".pac"):
                copy_file(os.path.join(pac_src, f), os.path.join(pac_dir, f))
                found = True
                print("  [INFO] PAC source: %s" % label)
    
    if not found:
        print("  [WARN] No .pac file found! Build first.")
        return False
    return True

def step_copy_sdk():
    """Copy SDK files (public API only) + pre-compiled bootstrap objects"""
    print("\n[STEP 2] Copying SDK...")
    sdk_out = os.path.join(OUTPUT_DIR, "sdk")
    os.makedirs(sdk_out, exist_ok=True)

    for fname in SDK_FILES:
        src = os.path.join(SDK_DIR, fname)
        if os.path.exists(src):
            copy_file(src, os.path.join(sdk_out, fname))

    # Copy pre-compiled bootstrap .o files
    lib_out = os.path.join(OUTPUT_DIR, "lib")
    os.makedirs(lib_out, exist_ok=True)
    for fname in PREBUILT_FILES:
        src = os.path.join(PREBUILT_DIR, fname)
        if os.path.exists(src):
            copy_file(src, os.path.join(lib_out, fname))
        else:
            print("  [WARN] Pre-compiled %s not found! Run internal build first." % fname)

def step_copy_demo():
    """Copy demo APP and generate standalone build.bat"""
    print("\n[STEP 3] Copying demo APP...")
    demo_out = os.path.join(OUTPUT_DIR, "apps", "demo")
    os.makedirs(demo_out, exist_ok=True)

    # Copy main.c
    src = os.path.join(DEMO_SRC, "main.c")
    if os.path.exists(src):
        copy_file(src, os.path.join(demo_out, "main.c"))

    # Generate standalone build.bat for zkw_output layout
    # Uses pre-compiled Entry.o + Start.o from lib/ (no source compilation needed)
    build_bat = r"""@echo off
set PATH=C:\Program Files\DS-5 v5.26.0\sw\ARMCompiler5.06u4\bin;%PATH%
set PROJ_NAME=hello_bigseek
set OUT_EXT=.bin
set SDK_DIR=%~dp0..\..\sdk
set LIB_DIR=%~dp0..\..\lib
set OUT_DIR=%~dp0out
set CPU=ARM7EJ-S
set APCS=/ropi/interwork

if not exist %OUT_DIR% mkdir %OUT_DIR%

echo [CC] main.c (SDK only)
armcc -c -O1 -cpu %CPU% -apcs %APCS% -zc -zo -fy -I%SDK_DIR% main.c -o %OUT_DIR%\main.o

echo [LINK] hello_bigseek.axf
armlink -entry Entry -ro-base 0x00000000 -first Entry.o(.constdata) -ropi -rwpi -reloc -nodebug %LIB_DIR%\Entry.o %OUT_DIR%\main.o %LIB_DIR%\Start.o -o %OUT_DIR%\%PROJ_NAME%.axf
echo [BIN] hello_bigseek.bin
fromelf -bin %OUT_DIR%\%PROJ_NAME%.axf -output %OUT_DIR%\%PROJ_NAME%%OUT_EXT%

echo DONE.
"""
    bat_path = os.path.join(demo_out, "build.bat")
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(build_bat)
    print("  [GEN ] build.bat (standalone for zkw_output)")

def step_generate_readme():
    """Generate README.md"""
    print("\n[STEP 4] Generating README...")
    commit = get_git_commit()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    readme = f"""# zkw_output — External Deliverable Package

**Generated:** {now}
**Source commit:** {commit}
**Generator:** export_zkw_output.py (TM-031)

## Contents

- `out/pac/` — Compiled PAC firmware (flash to device)
- `sdk/` — DAP SDK v0 (dap_api.h + bootstrap files)
- `apps/demo/` — Hello AIOS demo APP

## Usage

### Flash PAC
Use ResearchDownload to flash `out/pac/*.pac` to device.

### Build Demo APP
```
cd apps/demo
build.bat
```
Copy `out/hello_bigseek.bin` to device `D:\\DAP\\` and execute.

## Security Notice

This package does NOT contain DAP internal source code.
DAP core, loader, and security modules are compiled into the PAC firmware.
"""
    path = os.path.join(OUTPUT_DIR, "README.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(readme)
    print(f"  [GEN ] README.md")

def step_generate_manifest():
    """Generate MANIFEST.md with file hashes"""
    print("\n[STEP 5] Generating MANIFEST...")
    lines = ["# Export Manifest\n", f"Generated: {datetime.datetime.now().isoformat()}\n",
             f"Commit: {get_git_commit()}\n", "\n| File | SHA-256 | Size |\n|------|---------|------|\n"]

    for root, dirs, files in os.walk(OUTPUT_DIR):
        for fname in sorted(files):
            if fname in ("MANIFEST.md",):
                continue
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, OUTPUT_DIR)
            size = os.path.getsize(fpath)
            h = sha256_file(fpath)
            lines.append(f"| `{rel}` | `{h[:16]}...` | {size:,} |\n")

    path = os.path.join(OUTPUT_DIR, "MANIFEST.md")
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"  [GEN ] MANIFEST.md")

def step_security_scan():
    """Verify no Class A content leaked into output"""
    print("\n[STEP 6] Security scan...")
    violations = []

    # Files that legitimately reference internal names (bootstrap code)
    EXEMPT_FILES = {"Entry.c", "OSInterface.h", "dap_api.h", "build.bat"}

    for root, dirs, files in os.walk(OUTPUT_DIR):
        for fname in files:
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, OUTPUT_DIR)

            # Check forbidden directory references in path
            for d in FORBIDDEN_DIRS:
                if d in rel.replace("\\", "/"):
                    violations.append("Path contains '%s': %s" % (d, rel))

            # Check file content for forbidden patterns (skip exempt files)
            if fname in EXEMPT_FILES:
                continue
            if fname.endswith((".c", ".h", ".md", ".bat", ".mk", ".py")):
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    for pattern in FORBIDDEN_PATTERNS:
                        if pattern in content:
                            violations.append("'%s' found in %s" % (pattern, rel))
                except:
                    pass

    if violations:
        print("  [FAIL] Security violations detected:")
        for v in violations:
            print("    [X] %s" % v)
        return False
    else:
        print("  [PASS] No Class A content in zkw_output")
        return True

# ─── Strip (TM-032) ─────────────────────────────────────────────────────────

def step_strip_debug():
    """Strip debug info from exported .o files using fromelf"""
    print("\n[STEP 7] Stripping debug info...")
    lib_dir = os.path.join(OUTPUT_DIR, "lib")
    if not os.path.exists(lib_dir):
        print("  [SKIP] No lib/ directory")
        return

    for fname in ["Entry.o", "Start.o"]:
        fpath = os.path.join(lib_dir, fname)
        if not os.path.exists(fpath):
            continue
        size_before = os.path.getsize(fpath)
        try:
            fromelf_cmd = FROMELF_PATH if os.path.exists(FROMELF_PATH) else "fromelf"
            result = subprocess.run(
                [fromelf_cmd, "--strip=debug", "--output=" + fpath + ".stripped", fpath],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and os.path.exists(fpath + ".stripped"):
                os.replace(fpath + ".stripped", fpath)
                size_after = os.path.getsize(fpath)
                print("  [STRIP] %s: %d -> %d bytes (-%d)" % (fname, size_before, size_after, size_before - size_after))
            else:
                print("  [WARN] fromelf failed for %s: %s" % (fname, result.stderr.strip()))
        except FileNotFoundError:
            print("  [WARN] fromelf not found at %s" % FROMELF_PATH)
            break
        except Exception as e:
            print("  [WARN] Strip failed for %s: %s" % (fname, str(e)))

# ─── Strings Scan (TM-032) ──────────────────────────────────────────────────

def load_watchlist():
    """Load sensitive patterns from watchlist file"""
    patterns = []
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    return patterns

def step_strings_scan():
    """Scan exported binaries for semantic leakage and generate report (TM-032-3)"""
    print("\n[STEP 8] Strings scan (TM-032-3)...")

    # Default watchlist patterns if file doesn't exist
    watchlist = load_watchlist()
    if not watchlist:
        watchlist = [
            "DAP_", "FindInterface", "InterfaceRegister", "binding",
            "loader", "DeviceSecret", "LVGL", "/home", ".c:",
            "DAP_RunDebug", "device_identity", "bin2_",
        ]
        print("  Using built-in watchlist (%d patterns)" % len(watchlist))
    else:
        print("  Watchlist: %d patterns loaded" % len(watchlist))

    hits = []
    all_strings_data = []  # For report file

    # Scan .o files in lib/
    lib_dir = os.path.join(OUTPUT_DIR, "lib")
    if os.path.exists(lib_dir):
        for fname in os.listdir(lib_dir):
            if fname.endswith(".o"):
                fpath = os.path.join(lib_dir, fname)
                file_strings = extract_strings(fpath)
                all_strings_data.append((fname, file_strings))
                check_watchlist(fname, file_strings, watchlist, hits)

    # Scan .bin files in apps/demo/out/
    demo_out = os.path.join(OUTPUT_DIR, "apps", "demo", "out")
    if os.path.exists(demo_out):
        for fname in os.listdir(demo_out):
            if fname.endswith(".bin"):
                fpath = os.path.join(demo_out, fname)
                file_strings = extract_strings(fpath)
                all_strings_data.append((fname, file_strings))
                check_watchlist(fname, file_strings, watchlist, hits)

    # Generate strings report file (TM-032-3)
    report_dir = os.path.join(OUTPUT_DIR, "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "strings_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Strings Report — TM-032-3\n")
        f.write("# Generated: %s\n\n" % datetime.datetime.now().isoformat())
        for fname, strings_list in all_strings_data:
            f.write("=== %s (%d strings) ===\n" % (fname, len(strings_list)))
            for s in strings_list:
                f.write("  %s\n" % s)
            f.write("\n")
        if hits:
            f.write("=== WATCHLIST HITS ===\n")
            for h in hits:
                f.write("  [!] %s\n" % h)
    print("  [GEN ] %s" % os.path.relpath(report_path, PROJ_ROOT))

    if hits:
        print("  [WARN] Strings scan found %d hit(s):" % len(hits))
        for h in hits[:10]:  # Show first 10
            print("    [!] %s" % h)
        if len(hits) > 10:
            print("    ... and %d more (see report)" % (len(hits) - 10))
        return False
    else:
        print("  [PASS] No sensitive strings found in exported binaries")
        return True

def extract_strings(fpath, min_len=4):
    """Extract printable ASCII strings from binary file"""
    strings_found = []
    try:
        with open(fpath, "rb") as f:
            data = f.read()
        current = []
        for byte in data:
            if 32 <= byte < 127:
                current.append(chr(byte))
            else:
                if len(current) >= min_len:
                    strings_found.append("".join(current))
                current = []
        if len(current) >= min_len:
            strings_found.append("".join(current))
    except Exception as e:
        print("  [WARN] Could not read %s: %s" % (fpath, str(e)))
    return strings_found

def check_watchlist(label, strings_list, watchlist, hits):
    """Check extracted strings against watchlist patterns"""
    all_text = " ".join(strings_list)
    for pattern in watchlist:
        if pattern in all_text:
            hits.append("'%s' found in %s" % (pattern, label))

# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  TM-032 External Deliverable Export Pipeline")
    print("=" * 60)
    print("  Source:  %s" % PROJ_ROOT)
    print("  Output:  %s" % OUTPUT_DIR)

    if "--clean" in sys.argv:
        step_clean()
    else:
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    step_copy_pac()
    step_copy_sdk()
    step_copy_demo()
    step_generate_readme()
    step_generate_manifest()
    ok1 = step_security_scan()

    # TM-032 additions
    step_strip_debug()
    ok2 = step_strings_scan()

    ok = ok1 and ok2

    print("\n" + "=" * 60)
    if ok:
        print("  [OK] Export complete. zkw_output_pac_code/ ready.")
    else:
        print("  [FAIL] Export had warnings or failures!")
    print("=" * 60)

    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
