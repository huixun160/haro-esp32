# Frozen Specification — TM-37a: Module Completion (UI/MMI + Network + Telephony)

**Phase:** TM-37a (of 37a/37b/37c)
**Date:** 2026-03-23
**Base:** TM-37 clarification feedback applied

---

## MUST

- [ ] **UI/MMI Module Completion (6/6):**
  - [ ] 职责边界（MMI vs LVGL vs GUIFORM vs IMGUI 划分）
  - [ ] Capability 完整（窗口/控件/消息/资源/输入法/动画）
  - [ ] API 覆盖（export/include 层 header 扫描 + TM-36 doc 对齐）
  - [ ] Event/Callback（MSG_* 消息、GUIWIN 回调、按键事件）
  - [ ] Dependency（→ Device/Display, → OS Core/Thread, ← APP）
  - [ ] Layer Tag 预分层

- [ ] **Network Module Completion (6/6):**
  - [ ] 职责边界（Socket/HTTP/SSL/DNS/GPRS/PDP）
  - [ ] Capability 完整
  - [ ] API 覆盖（sci_sock_*/HTTP_*/SSL_* export headers）
  - [ ] Event/Callback（网络连接/断开事件、异步数据回调）
  - [ ] Dependency（→ OS Core, → Telephony/GPRS, ← APP）
  - [ ] Layer Tag 预分层

- [ ] **Telephony Module Completion (6/6):**
  - [ ] 职责边界（MNPHONE/MNCALL/MNSMS/MNSS/MNGPRS/EngMode）
  - [ ] Capability 完整
  - [ ] API 覆盖（MN* export headers）
  - [ ] Event/Callback（来电/短信/注册状态回调）
  - [ ] Dependency（→ OS Core, ← Network/GPRS, ← APP）
  - [ ] Layer Tag 预分层

- [ ] **Scanning methodology:** Tier 1 (export/include) → Tier 2 (source only when needed)
- [ ] **API source marking:** doc_only / code_only / doc+code
- [ ] **Updated capability YAML** with `completion_status` + `source_verified` fields
- [ ] **Updated API registry YAML** with layer tags for all 3 modules

## SHOULD

- [ ] **E2E call-chain trace:** UI event → Network request → Storage write → Device feedback
- [ ] **Module maturity score** (1-5) per module
- [ ] **Doc↔Code alignment rate** >80% per module
- [ ] **Module Completion Dashboard** (partial — 3/12 modules)

## MAY

- [ ] Lightweight E2E runnable verification (demo/stub)
- [ ] Identify potential Service-layer APIs (preview for TM-38)

## OUT OF SCOPE

- Final architecture/boundary decisions (→ TM-38)
- Storage / Device / Audio modules (→ TM-37b)
- OS Core / HAL / Package modules (→ TM-37c)
- Deep HAL register-level scanning
- Production code implementation

---

Approved by: ___
Date: 2026-03-23
