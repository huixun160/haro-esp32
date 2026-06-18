# TM-032 Phase 1 Feedback

**Outcome:** PARTIAL (Phase 1 goals met, trace hardening deferred)
**Date:** 2026-03-20

## 完成项
1. SECURE build profile (`project_*_SECURE.mk` + `dap.mk` EXTERNAL_BUILD gating)
2. Export pipeline 升级 (SECURE PAC 优先、strip step、strings scan)
3. BIN + BIN2 验证通过 (SECURE + internal PAC)
4. Strings watchlist + 扫描 PASS
5. Unisoc build system 兼容 (lib junction, Perl fix, findstr fix)

## 未完成项

### TM-032-2 (下一步优先)

> [!CRITICAL]
> **DeviceSecret 导出问题**: device.bind 不包含 device_secret → 无法在 PC 端生成 BIN3

需要讨论的方案：
- **(A)** 功能机自动发送 device_secret（安全风险：secret 明文传输）
- **(B)** 功能机执行 BIN2 后自动升级为 BIN3 模式（设备端加密）
- **(C)** 通过安全通道（如加密 USB/bindfile）导出 secret
- **(D)** 重新设计 BIN3 生成流程（设备端直接生成 BIN3，不需要 PC）

> 以上方案各有利弊，需要在 TM-032-2 memo 中明确讨论。

### TM-032-3 (后续)

> [!WARNING]
> **Logel trace 泄漏**: SECURE PAC 仍输出全部 DAP trace（148 条），包括 DeviceSecret 明文

trace 泄漏分析 (from `traceinfo.resd`):
| 严重级别 | 内容 | 出现次数 |
|---------|------|---------|
| CRITICAL | DeviceSecret 明文 | 16 次 |
| CRITICAL | BindingID 明文 | 5 次 |
| HIGH | Loader 内部地址 | 20+ 次 |
| HIGH | InterfaceRegister 明文接口名 | 4 次 |
| MEDIUM | BIN2 验签细节 | 15 次 |
| MEDIUM | 内部源文件名+行号 | 30+ 次 |

原因：`SCI_TRACE_LOW` 不受 `-DSCI_TRACE_MODE` 宏控制。需要用 `#ifdef EXTERNAL_BUILD` 包裹所有 DAP trace 调用。

> [!IMPORTANT]
> 不要直接删除 SCI_TRACE 调用 — internal 版本仍需保留完整 trace 用于 debug。
> 正确做法：`#ifndef EXTERNAL_BUILD` 保护。

### Phase 2 内容 (FindInterface 去语义化 + 混淆) — 安排在 TM-032-3 之后的独立 TM
