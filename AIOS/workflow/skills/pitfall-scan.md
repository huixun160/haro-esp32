# Skill: Pitfall Scan

## Purpose
Scan accumulated project pitfalls, key decisions, and runbooks to produce a **Pitfall Briefing** that prevents the current task from repeating past mistakes.

## When to Invoke
- **Mandatory** during Task Planning (before producing the implementation plan).
- May also be invoked at any time if the engineer suspects a recurring issue.

## Input
- Current Technical Memo (parsed by `intake-memo`)
- List of affected modules and file paths (from spec or memo)

## Procedure

1. **Read project memory**
   - Read `AIOS/MEMORY.md` — extract the **Resolved Pitfalls** and **Key Decisions** sections in full.
   - Note any pitfalls marked with ⚠️ (recurring pattern).

2. **Scan all pitfall records**
   - List all `.md` files in `AIOS/docs/pitfalls/`.
   - Read each file. Extract: Symptom, Root Cause, Prevention, Affected Module.

3. **Scan all runbooks**
   - List all `.md` files in `AIOS/docs/runbooks/`.
   - Read each file. Note the checklist items.

4. **Match pitfalls to current task**
   For each pitfall / decision / runbook, check relevance:

   | Match Criteria | Example |
   |---|---|
   | `Affected Module` overlaps with TM scope | TM touches `dap.mk` → match `dap_mk_flags_missing.md` |
   | TM adds new `.c` files | → match pitfalls mentioning `MSRCPATH` |
   | TM modifies build flags | → match pitfalls mentioning `MCFLAG_OPT` |
   | TM touches crypto / security | → match SHA-256 symbol collision pitfall |
   | TM adds logging / trace | → match `SCI_TRACE_MODE` pitfalls |
   | Recurring pitfall (⚠️) | → always include regardless of module match |

5. **Match runbooks to current task**
   If the TM involves `make/dap/dap.mk`, attach `dap_mk_checklist.md` in full.

6. **Produce Pitfall Briefing**
   Output the following structured briefing for the `plan-task` skill to embed in the implementation plan:

   ```markdown
   ## ⚠️ Pitfall Briefing

   ### Matched Pitfalls (N items)
   | # | Pitfall | Relevance | Prevention |
   |---|---------|-----------|------------|
   | 1 | [title] | [why it matches] | [prevention action] |

   ### Applicable Runbooks
   - [ ] [runbook name] — [when to execute]

   ### Key Decisions to Respect
   - [decision] — [consequence]
   ```

## Output
A **Pitfall Briefing** block (markdown) to be embedded in the Implementation Plan.

## Notes
- If no pitfalls match, output: "✅ No matching pitfalls found. Proceed with standard caution."
- Recurring pitfalls (⚠️) should be highlighted with bold text.
- This skill is **read-only** — it does not modify any files.
