# Feedback — TM-37: Source Code Deep Scan & Module Completion

**Date:** 2026-03-23
**Memo:** Technical_Memo_37 — Source Code Deep Scan & Module Completion
**Outcome:** SUCCESS
**Author:** Antigravity AI

---

## Execution Summary

完成 9 个核心模块的源码深扫与 6/6 Completion 收口。从 PDF 文档估算的 ~750 API 扩展至源码验证的 **6,306 API**，文档覆盖率仅 12%。发现已有完整云端应用框架 COAPI（OTA/Download/DeviceBind），App Store 核心能力 70% 已覆盖。所有 9 个模块达到"Decision-Ready"状态。

---

## Completed Work

- [x] **TM-37a:** UI/MMI (2,895 APIs), Network (442 APIs), Telephony (731 APIs) — 全部 6/6
- [x] **TM-37b:** Storage (249 APIs), Audio (744 APIs), Device (463 APIs) — 全部 6/6
- [x] **TM-37c:** OS Core (445 APIs), Package/Download (337 APIs, **COAPI 发现**) — 全部 6/6
- [x] LVGL 9.5 已在 TM-36 完成 (38 APIs, 100% DAP)
- [x] Module Completion Dashboard
- [x] 9 份模块完成报告（含 Layer Tag 预分层）

---

## Incomplete Work

- [ ] Bluetooth 模块源码深扫（现为 partial，TM-36 已覆盖 136 API）
- [ ] Camera 模块源码深扫（现为 partial，dal_dcamera 39 API 已录入 Device 模块）
- [ ] E2E UI→Network→Storage→Device 调用链完整跟踪（需 Network 桥接后验证）
- [ ] 每个模块的详细 YAML API registry（目前仅 OS Core + FS 有 per-API YAML）

---

## Blocking Issues

无。所有计划内工作已完成。

---

## Verification Status

| Test | Result | Notes |
|---|---|---|
| UI/MMI 6/6 completion | PASS | 2,895 PUBLIC APIs across 205 headers |
| Network 6/6 completion | PASS | 442 APIs across 66 DAPS headers |
| Telephony 6/6 completion | PASS | 731 APIs in mn_api.h + mn_api_td.h |
| Storage 6/6 completion | PASS | SFS 82 + FMM 159 + NV 8 = 249 APIs |
| Audio 6/6 completion | PASS | 615 (MS_Ref) + 129 (MMI service) = 744 APIs |
| Device 6/6 completion | PASS | 463 APIs across 24 DAL/driver headers |
| OS Core 6/6 completion | PASS | 445 APIs in RTOS/export/inc |
| Package/Download 6/6 | PASS | 337 APIs in coai_app_pool (COAPI) |

---

# 📋 资深架构师决策必读

## 必读文档清单（3 份，阅读时间 ~15 分钟）

| # | 文档 | 路径 | 关键内容 |
|---|------|------|---------|
| 1 | **Module Completion Dashboard** | `docs/api/module_completion.md` | 9 模块全景、6,306 API 规模、DAP 2.4% 覆盖率 |
| 2 | **Package/Download 模块** | `docs/api/modules/package_download.md` | **COAPI 发现** — App Store 70% 能力已有 |
| 3 | **LVGL 模块** | `docs/api/modules/lvgl.md` | UI 方案选型证据 — 100% vs 0.6% DAP |

---

## 三大待决策问题

### 🔴 决策 1：UI 路线选型

**问题：** LVGL 全面替代 MMI 做 DAP APP UI，还是桥接 MMI 控件？

| 指标 | LVGL | MMI |
|------|------|-----|
| DAP 覆盖 | **100%** (38/38) | 0.6% (10/2,895) |
| 桥接新控件 | 1-3 wrapper (~50行) | 理解三层架构 + 主题 |
| 文档质量 | LVGL 官方文档 | Unisoc 内部中文 PDF |
| 可移植性 | ✅ 跨平台 | ❌ Unisoc 专有 |
| 已验证 | PalmOS + 俄罗斯方块 | DAP APP 从未使用 |
| 共存机制 | `DAP_LVGL_OpenWindow` 分时切换 | 系统级 UI，来电/短信仍走 MMI |

**建议：** LVGL 做 APP UI，MMI 保持系统 UI。不桥接 MMI 控件到 DAP。

---

### 🔴 决策 2：Network 桥接优先级

**问题：** Socket/HTTP/SSL 是否作为下一个 DAP 桥接重点？

| 事实 | 数据 |
|------|------|
| Network API 总数 | **442** (DAPS/export/inc) |
| SERVICE_CANDIDATE | ~167 (Socket 45 + HTTP 37 + SSL 17 + WiFi 22 + PDP 39 + FTP 5 + SNTP 2) |
| 当前 DAP 覆盖 | **0%** |
| App Store 依赖 | ✅ 必须 — 无网络无法下载 BIN |
| 最小桥接集 | ~15 API (socket/connect/send/recv/close + HTTP_CreateContext/GetUrl/Close + DNS) |

**建议：** P0 优先级。最小可用集 ~15 个 API wrapper，可在一个 TM 内完成。

---

### 🔴 决策 3：App Store 架构

**问题：** COAPI + DAP Loader 整合，还是从零自建？

**发现：** `MS_MMI_Main/source/coai_app_pool/` 已有完整云端 IoT 框架：

| 能力 | COAPI 现状 | DAP 现状 | 整合难度 |
|------|-----------|---------|---------|
| HTTP 下载 | ✅ cos_load (URL→file) | ❌ 无 | 低 — 复用 |
| OTA (URL + 分片) | ✅ coapi_ota (check/start/progress) | ❌ 无 | 低 — 复用 |
| 签名验证 | ❌ MD5 only | ✅ Ed25519 (bin2_crypto) | 中 — 替换 MD5→Ed25519 |
| 设备绑定 | ✅ coapi_devbind | ✅ device_binding.c | 低 — 对齐 |
| BIN 加载执行 | ❌ 无 | ✅ DAP Loader (BIN/BIN2/BIN3) | 低 — 直连 |
| 版本管理 | ⚠️ ota_info.version | ❌ 无 | 中 — 需设计 |
| App 列表 UI | ❌ 无 | ❌ 无 | 中 — LVGL 实现 |
| App 卸载 | ❌ 无 | ❌ 无 | 低 — SFS_DeleteFile |

**建议：** 整合 COAPI + DAP Loader，不从零自建。预估覆盖 70%，从零建至少 3× 工作量。

---

## 关键数据汇总

### 平台 API 规模（源码验证）

| Module | Total APIs | SERVICE_CANDIDATE | DAP Bridged | Gap |
|--------|-----------|------------------|-------------|-----|
| UI/MMI | 2,895 | ~1,800 | ~10 | 1,790 |
| Network | 442 | ~167 | 0 | 167 |
| Telephony | 731 | ~365 | 0 | 365 |
| Storage | 249 | ~230 | ~12 | 218 |
| Audio | 744 | ~231 | ~5 | 226 |
| Device | 463 | ~200 | 0 | 200 |
| OS Core | 445 | ~133 | ~14 | 119 |
| Package | 337 | ~193 | 0 | 193 |
| LVGL | 38 | 38 | **38** | **0** |
| **Total** | **6,344** | **~3,357** | **~79** | **3,278** |

> **DAP 覆盖率: 2.4%** — 但通过 LVGL (100%) 已解决最关键的 UI 问题

### 建议开发路线图

```
TM-38: 架构边界决策（基于本 TM-37 输出）
  ↓
TM-39: Network DAP 桥接（~15 核心 API → Socket/HTTP/DNS）
  ↓
TM-40: LVGL 控件扩展（+8 控件 → Slider/Image/Arc...）
  ↓
TM-41: COAPI + DAP Loader 整合（App Store v0）
  ↓
TM-42: App Store UI（LVGL 实现 App 列表/下载/安装界面）
```

---

## Files Changed

| File | Action | Description |
|---|---|---|
| `docs/api/modules/gui_mmi.md` | Modified | 升级：2,895 APIs, 6/6 completion |
| `docs/api/modules/network.md` | Modified | 升级：442 APIs, 6/6 completion |
| `docs/api/modules/telephony.md` | Modified | 升级：731 APIs, 6/6 completion |
| `docs/api/modules/filesystem.md` | Modified | 升级：249 APIs, 6/6 completion |
| `docs/api/modules/audio.md` | Modified | 升级：744 APIs, 6/6 completion |
| `docs/api/modules/device.md` | Modified | 升级：463 APIs, 6/6 completion |
| `docs/api/modules/os_core.md` | Modified | 升级：445 APIs, 6/6 completion |
| `docs/api/modules/package_download.md` | Created | **新模块** — COAPI 发现 (337 APIs) |
| `docs/api/module_completion.md` | Created | 9 模块完成 Dashboard |
| `quality_reports/specs/TM-37a_spec.md` | Created | 冻结规格 |

---

## References

- Related memos: TM-35 (API Registry), TM-36 (Capability Census)
- COAPI framework: `MS_MMI_Main/source/coai_app_pool/`
- LVGL integration: `Third-party/lvgl-9.5.0/dap_lvgl_bridge.c`
- DAP Loader: `DAP/core/DAP_Loader_unisoc.c`
