# Implementation Plan — TM-36 Unisoc 平台全量普查

## Overview
Documentation/data-only task. Build comprehensive capability map of Unisoc platform by combining PDF parsing with source code analysis.

## Output Structure
```
docs/api/modules/X.md          ← human-readable per-module
docs/architecture/*.md         ← platform overview, capability map
registry/capabilities/X.yaml   ← capability YAML per module
registry/apis/X.yaml            ← API YAML per module
```

## Execution Phases
| Phase | Module | Key Input |
|-------|--------|-----------|
| 0 | PDF Tooling + KB Index | all 116 PDFs |
| 1a | OS Core | OS接口使用指南 |
| 1b | FileSystem | SFS接口使用指南 |
| 2a | GUI/MMI | MMI开发指南 |
| 2b | Display + Keypad HAL | Display/Keypad guides |
| 3a | Network: Socket | Socket接口说明 |
| 3b | Network: HTTP/SSL | HTTP/SSL guides |
| 4 | Telephony | MNPHONE/MNSMS |
| 5 | Audio | AudioService 2.0 |
| 6 | BT + Camera (SHOULD) | BT/Camera guides |
| 7 | HAL (SHOULD) | HAL guides |
| 8 | Master Report | all phases |
