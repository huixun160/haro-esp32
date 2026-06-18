# Frozen Specification - TM-01 ARCS SDK Robot AIOS Voice Platformization

Owner / Author: weizongquan
Execution Session: PinzhenHe
Approved Date: 2026-04-15

## MUST
- [ ] Keep `voice_cloud_*` as a narrow compatibility facade while moving implementation selection behind a provider boundary.
- [ ] Add an AIOS provider path that can be selected by configuration, even if TM01 only delivers a compileable/local-debuggable stub instead of a production cloud closure.
- [ ] Preserve existing upper-layer `voice_msg` semantics for connection/session/TTS/IAT events so current UI and message-driven flows keep working.
- [ ] Route `voice_platform.c` network-ready connect flow through provider selection instead of hard-binding the old LSChat runtime.
- [ ] Route wakeup uplink audio through an explicit sink boundary instead of calling a concrete cloud implementation directly from the wakeup path.
- [ ] Add an MCP transport boundary so async MCP responses no longer depend on a hard-coded runtime message path inside `mcp.c`.
- [ ] Extend runtime configuration/state to cover cloud provider, service-side segmentation, continuous dialogue mode, optional `X-Bot-ID`, UI version reservation, and TM01 debug flags.
- [ ] Freeze protocol handling as follows:
- [ ] `X-Bot-ID` is optional for TM01 handshake assembly. If configured, send it; if absent, do not fail solely because it is missing.
- [ ] Encrypted HTTP requests use `X-Encryption-Data` for the RSA-encrypted AES key envelope. `Authorization` remains reserved for bearer-token style auth.
- [ ] Treat continuous dialogue in TM01 as cloud/session behavior only. Do not implement local wakeup suppression or auto-reentry policy in this TM.
- [ ] Deliver software-level robot action validation via event publication plus shell/UI trigger paths and observable logs/callbacks.
- [ ] Reserve LVGL9 through configuration plus a minimal versioned entry/adapter skeleton, without performing a full LVGL9 migration.
- [ ] Add shell-side debug entrypoints for provider/status inspection, PAD/UI/robot validation triggers, and volume debugging.
- [ ] Add a UI-side debug entry that exposes the key TM01 observability controls and validation buttons.
- [ ] Archive a verification checklist that clearly separates local integration checks from real cloud / real device validation still pending.

## SHOULD
- [ ] Parse the new AIOS/platformization fields in both legacy app data loading and the JSON config parser so future runtime migration has a stable landing zone.
- [ ] Keep default behavior backward-safe when no AIOS-specific configuration is present.
- [ ] Add architecture / API documentation for the new provider, MCP transport, and wakeup sink boundaries.
- [ ] Register new public APIs introduced by the decoupling work in `AIOS/registry/apis.yaml`.

## MAY
- [ ] Expose additional provider/debug state in the UI model layer for later richer diagnostics.
- [ ] Emit extra protocol-oriented logs for future real AIOS auth / WebSocket bring-up.

## OUT OF SCOPE
- Keeping LSChat production-compatible as the long-term runtime contract.
- Full AIOS production protocol closure against real cloud services.
- Local wakeup suppression / auto-reentry policy for continuous dialogue.
- Full LVGL9 migration or presenter/view directory re-architecture.
- Real actuator / servo / mechanical closed-loop integration.
- Full robot motion planning, map/navigation, or advanced multimodal autonomy.

Approved by: weizongquan
Date: 2026-04-15
