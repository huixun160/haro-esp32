# Session Log — TM02: James Legacy Code System Analysis

**Date:** 2026-03-26
**Author:** KaiwenZheng
**Project:** demo_merge
**Memo:** TM-02
**Duration:** ~30 min

## Summary

对 James 的 UMS9117_BSP 仓库进行系统级分析，建立架构模型、模块清单、API 清单和 Merge 策略。额外完成了核心兼容性深度对比（Loader/Register/OSAssociated）。

## Files Created

| 文件 | 说明 |
|------|------|
| `analysis/TM02_architecture.md` | 架构文档（系统模型 + 调用链 + 目录对比） |
| `analysis/TM02_modules.md` | 模块清单（40+ 模块，7 类别） |
| `analysis/TM02_api_list.md` | API 清单（38 LVGL + Audio/VA/T9/DL） |
| `analysis/TM02_merge_plan.md` | Merge 策略（4 Tier + 禁止列表） |
| `analysis/TM02_core_compatibility.md` | 核心兼容性分析（9 个 Gap） |

## Key Decisions

1. DAP Core (Loader/Register) 不 merge — ABI 兼容，仅需补注册 API
2. 识别 9 个必须解决的兼容性 Gap（LVGL/T9/VA/DL/KeyCallback/ScanApps 等）
3. Merge 按 4 Tier 优先级执行：LVGL Runtime → Bridge → Apps → Download
4. 分析产物放在 `projects/demo_merge/analysis/`

## Key Findings

- James 有 12 个 DAP App（vs 主线 2 个）
- `DAP_UNISOC_OSAssociated.c` 632KB 巨型文件 = 主线多个文件的合并
- `TApplication` 352 bytes 两边一致 — ABI 完全兼容
- James 的动态扩容 Register (v4) vs 主线固定容量 — 容量可能不足

## Deviations from Spec

- 加入了原 Memo 未要求的核心兼容性分析（用户额外要求）
