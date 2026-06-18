# TM-029-1 — 风险清单 (Risk List)

**Date:** 2026-03-15

---

## Risk 1 — dap.mk 手动合并引爆 ⚠️ 高

**说明:** 快照 `dap.mk` 有 40 行新增（BIGSEEK_CORE_SUPPORT 块），但同时不含 TM28-R 的安全文件（`dap_aes.c`, `bin2_crypto_payload.c`）。直接覆盖会丢失安全编译入口。

**缓解:** 必须在主线 dap.mk 上手动追加 BIGSEEK_CORE_SUPPORT 块，不能反向覆盖。

**历史教训:** `dap_mk_flags_missing.md` 已记录 3 次复发。

---

## Risk 2 — dap_audio_bridge.c 合并冲突 ⚠️ 高

**说明:** 主线 28KB，快照 60KB (+31KB)。快照版本包含录音/播放/音量等大量新功能。但快照中的 `DAP_Loader_unisoc.c` 是旧版（无安全修改），说明快照的 DAP 平台代码整体未经 TM28-R 处理。

**缓解:** 需要逐函数比对 `dap_audio_bridge.c`，识别纯新增的音频功能函数，手动合并到主线。

---

## Risk 3 — DAP_InstallOSAPI_unisoc.c 注册缺失 ⚠️ 中

**说明:** VA API 的 9 个函数需要通过 `DAP_InstallOSAPI_unisoc.c` 注册为 FindInterface 可检索的接口。快照中该文件 13.8KB vs 主线 13.6KB (+200B)。差异可能就是 VA API 注册行。

**缓解:** diff 后识别新增注册行，手动追加。

---

## Risk 4 — bigseek_core 依赖旧版系统 API ⚠️ 中

**说明:** `bigseek_core` 的 `bs_pdp_platform.c` 和 `bs_network.c` 直接调用 UNISOC PDP/网络管理 API。如果主线的网络栈版本有变化，这些文件可能编译失败。

**缓解:** 编译时优先关注 `bs_pdp_platform.c` 和 `bs_network.c` 的头文件依赖。

---

## Risk 5 — 外部库版本不一致 ⚠️ 中

**说明:** `curl`, `libwebsockets`, `mbedtls` 在主线和快照中可能版本不同。快照的 `dap.mk` 有 `MBEDTLS_VERSION` 条件选择。

**缓解:** TM29-2 开始前需确认主线中这些库的版本和目录结构。

---

## Risk 6 — Logel trace 冲突 ⚠️ 低

**说明:** `bigseek_core` 自带日志系统（`bs_utils.c`），可能使用自己的 printf 或 SCI_TRACE_LOW。需确认不与当前 DAP_DBG 体系冲突。

**缓解:** 检查 `bs_core_config.h` 中的日志宏定义，确认是否使用 `SCI_TRACE_LOW`。

---

## Risk 7 — voice_chat APP 依赖特定 LVGL 版本 ⚠️ 低

**说明:** `voice_chat` 使用的 LVGL API（`lv_label_create`, `lv_obj_align` 等）需要 LVGL 9.x。主线有 `lvgl-9.5.0/` 目录，应该兼容。

**缓解:** 确认主线 `lvgl-9.5.0/` 与快照中的版本一致。

---

## 总结

| 风险等级 | 数量 | 关键项 |
|---------|------|--------|
| ⚠️ 高 | 2 | dap.mk 合并, audio_bridge 合并 |
| ⚠️ 中 | 3 | InstallOSAPI 注册, PDP API, 库版本 |
| ⚠️ 低 | 2 | Logel 冲突, LVGL 版本 |
