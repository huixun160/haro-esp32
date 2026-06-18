# Implementation Plan — TM-35 AIOS API 梳理、YAML 注册与决策报告生成

## Overview

This task is **documentation/data-only** — no C source code modifications. The goal is to survey all Unisoc bottom-layer APIs currently available in the codebase, register them in a structured YAML format, and produce analysis reports to support architectural decision-making.

---

## File Changes

| Action | File | Module | Description |
|--------|------|--------|-------------|
| CREATE | `AIOS/registry/schema/api_schema.yaml` | registry | API YAML schema definition (M3) |
| MODIFY | `AIOS/registry/apis.yaml` | registry | Extend with TM-35 fields + new Unisoc API entries (M2) |
| CREATE | `AIOS/docs/api/api_inventory.md` | docs | Human-readable full API inventory (M1) |
| CREATE | `AIOS/docs/api/reports/api_summary.md` | docs | Global statistics report (M4) |
| CREATE | `AIOS/docs/api/reports/api_gap_analysis.md` | docs | Capability gap analysis (M4) |
| CREATE | `AIOS/docs/api/reports/api_risk_analysis.md` | docs | Risk analysis report (M4) |
| CREATE | `AIOS/docs/api/aios_service_architecture.md` | docs | Service mapping + Mermaid diagram (S1) |
| CREATE | `AIOS/scripts/validate_api_schema.py` | scripts | Python schema validator (M5) |
| CREATE | `AIOS/registry/.yamllint.yml` | registry | yamllint config (M5) |

---

## Execution Order

### Phase 1 — Schema Definition (M3)
1. Create `AIOS/registry/schema/api_schema.yaml` defining all fields

### Phase 2 — API Source Scan (M1)
2. Scan DAP platform source files systematically
3. Output `AIOS/docs/api/api_inventory.md`

### Phase 3 — YAML Registry (M2)
4. Extend existing `AIOS/registry/apis.yaml` with new entries and fields

### Phase 4 — Analysis Reports (M4)
5. Generate 3 analysis reports from YAML data

### Phase 5 — Service Mapping (S1)
6. Group APIs into logical Services + Mermaid diagram

### Phase 6 — Verification Tooling (M5)
7. Create yamllint config + Python schema validator
8. Run both on registry

---

## ⚠️ Pitfall Briefing

### Matched Pitfalls (1 item)
| # | Pitfall | Relevance | Prevention |
|---|---------|-----------|------------|
| 1 | **PowerShell 编码腐蚀源码** | 创建/修改 YAML 和 markdown 文件时 | 所有文件编辑使用编辑器工具，**不使用 PowerShell 写文件** |

### Key Decisions to Respect
- YAML schema 中 `abi` 字段为 optional
- API 存储双位置: `AIOS/registry/apis.yaml` + `AIOS/docs/api/`
- 不修改现有 C 代码

---

## Verification Plan

### Automated Tests
```
yamllint -c AIOS/registry/.yamllint.yml AIOS/registry/apis.yaml
python AIOS/scripts/validate_api_schema.py
```

### Manual Verification
- Engineer reviews inventory for completeness
- Engineer reviews analysis reports for accuracy
