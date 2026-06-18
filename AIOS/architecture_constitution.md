# AIOS Architecture Constitution
#
# These are **binding rules** — any violation is a design error.
# Used by agents and engineers to validate architecture compliance.
#
# Last updated: 2026-03-25

---

## RULE 1: APP Must Not Call Mocor APIs Directly

Applications (BIN2/BIN3) are **prohibited** from invoking any Mocor SDK API.

All system capability access must go through the ABI layer → Service layer → Adapter layer.

**Violation indicator:** APP source contains `#include` of any Mocor header, or calls any `SCI_*`, `SFS_*`, `MMI_*`, `GUIREF_*` function directly.

---

## RULE 2: DAP Must Not Contain Business Logic

The DAP runtime is a **platform layer** — it provides loading, lifecycle management, and ABI dispatch.

DAP must not implement application-level features (UI flows, game logic, data processing).

**Violation indicator:** DAP source contains conditional logic based on application content or state.

---

## RULE 3: Service Layer Owns All System Capability

Every system capability (UI, storage, network, audio, timer) must be implemented as a **Service**.

Services define the abstract interface; they do not touch hardware or Mocor APIs.

**Violation indicator:** Service source contains `#include` of Mocor headers or platform-specific code.

---

## RULE 4: Adapter Is the ONLY Layer Touching Mocor

All Mocor SDK interactions (SFS, SCI, GUIREF, MMI, audio, timer) must be isolated in **Adapter** modules.

If Mocor changes its API, only adapters need to change.

**Violation indicator:** Non-adapter source files contain Mocor API calls.

---

## RULE 5: ABI Is the ONLY Interface for APP

Applications interact with the platform exclusively through the **ABI** (Application Binary Interface).

The ABI is versioned (`abi_v1`). Apps compiled against ABI v1 must work on any platform that implements ABI v1.

**Violation indicator:** APP references internal DAP functions, service internals, or adapter functions directly.

---

## Enforcement

- `architecture-reviewer` agent validates these rules during implementation
- `agent_permissions.yaml` restricts which agents can modify which layers
- Violations are flagged as **ERROR** severity in code review
