# Pitfall: WiFi Status Enum Mismatch Across SDK Versions

**Date:** 2026-03-15
**Task:** TM-029-2.5
**Severity:** Critical (silently breaks all network functionality)

## Symptom
`BS_IsWifiConnected()` always returns FALSE even though WiFi is connected. All network operations fail: token auth, WebSocket connect, voice response.

## Root Cause
`bs_network.c` hardcodes `BS_WIFI_STATUS_CONNECTED = 4` (later snapshot) or `3` (Ouyang git). The actual `MMIWIFI_STATUS_E` enum in `mmiwifi_export.h` defines `MMIWIFI_STATUS_CONNECTED = 2` (OFF=0, ON=1, CONNECTED=2).

Ouyang's code used `extern` declarations to avoid including `mmiwifi_export.h` and guessed the enum value wrong.

## Fix
```c
#define BS_WIFI_STATUS_CONNECTED  2  /* Logel verified: MMIAPIWIFI_GetStatus returns 2 */
```

## Prevention
- **Never guess platform enum values** — always `#include` the official header or verify via Logel trace
- When porting code across SDK versions, verify all hardcoded constants against the target SDK's headers
