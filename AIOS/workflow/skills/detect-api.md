# Skill: Detect API

## Purpose
Scan source code to detect API function signatures for registration.

## Input
- Source file path(s) or directory to scan
- Optional: specific API pattern to search for

## Procedure

1. **Scan for API patterns** in C/H files:
   - Functions with `DAP_` prefix
   - Functions with `DAPS_` prefix
   - Functions exported via function pointer tables
   - Functions registered in dispatch/handler arrays
   - Functions declared with `PUBLIC` or `MMIPUB` visibility

2. **Extract metadata** for each detected API:
   - Function name
   - Return type
   - Parameter types and names
   - Source file and line number
   - Layer (infer from directory: `Third-party/DAP/` → DAP, `MS_MMI_Main/` → APP, etc.)

3. **Check against registry** — Compare with `AIOS/registry/apis.yaml`:
   - Identify unregistered APIs
   - Identify APIs with outdated metadata

4. **Report findings** to the engineer:
   - List of newly detected APIs
   - List of APIs needing metadata updates
   - Suggest registration using `record-api` skill

## Script Support
For batch scanning, use `AIOS/scripts/api_scanner.py`:
```bash
python AIOS/scripts/api_scanner.py --path <source_path> --pattern "DAP_*"
```

## Output
List of detected APIs with extracted metadata, cross-referenced with registry.
