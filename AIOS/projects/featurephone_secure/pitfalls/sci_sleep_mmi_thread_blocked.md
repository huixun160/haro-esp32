# Pitfall: SCI_Sleep in MMI Thread Causes Enqueue Assert

**Date:** 2026-03-16
**Task:** TM-029-2.5
**Severity:** Critical (immediate blue screen crash)

## Symptom
`sdi_msg_iram.c Line:82 ASSERT (Enqueue failed)` — blue screen on opening voice assistant when WiFi is connected.

## Root Cause
`BS_HttpTaskCreate()` in `bs_task.c` contains a `while (!s_http_task_running) { SCI_Sleep(10); }` busy-wait loop, blocking the MMI thread for up to 500ms. During this time, all system messages (timer ticks, key events, WiFi notifications) pile up in the MMI message queue. When the queue overflows → assert.

This only triggers when WiFi is detected (fast init path), because the PDP path's blocking happens in the Core thread (not MMI thread).

## Fix
Remove the `SCI_Sleep` wait loop entirely. The HTTP worker thread starts on its own; no need to busy-wait.

## Prevention
- **Never call `SCI_Sleep()` in the MMI thread** — it blocks the system message pump
- All blocking operations in bigseek_core must run in T_BS_Core or T_BS_Http threads, never in the calling context (which may be MMI)
