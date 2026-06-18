# TM-030 Feedback

**Outcome:** ✅ SUCCESS
**Date:** 2026-03-19

## 完成项

### 交付物
1. ✅ `sdk/dap_api.h` — v0 冻结 ABI (7 个宏 API)
2. ✅ `AIOS/docs/sdk/dap_abi_v0.md` — ABI 冻结文档 + RWPI 约束
3. ✅ `build.bat` — 构建约束 (findstr + include 隔离)
4. ✅ `hello_bigseek` — 黄金样本 (BIN/BIN2/BIN3 验证)

### 核心决策 (Clarification Q1-Q5)

| 决策 | 选择 | 影响 |
|------|------|------|
| Q1: core/DAP_Application.h 处理 | A: 提取最小 ABI 到 sdk/ | APP 不访问 core/ |
| Q2: FindInterface 机制 | A: 宏封装保留 FindInterface | ABI 不变 |
| Q3: 旧 APP 迁移 | C: 只迁移 hello_bigseek | 8 个旧 APP → _legacy/ |
| Q4: 类型系统 | C: SDK 标准 C, 内部保留历史 | 分层隔离 |
| Q5: v0 范围 | A: lifecycle+memory+log+timer+popup | LVGL/Audio → v1 |

### 架构发现
- **DAP loader 不做 RW 重定位** — APP 禁止 static/global 变量
- **FindInterface 是运行时动态链接** — 不是编译期链接
- **Entry.c 是 ABI 锚点** — LoadAddr/OSAPI/Register/DelAPI 四字段重定位

## 路线图

```
TM-030 v0 (当前) ── runtime + minimal feedback ABI
    │
    ├── TM-030.x / v1 ── LVGL minimal surface
    │
    ├── TM-030.x / v2 ── Audio minimal surface
    │
    ├── TM-031 ── 对外裁剪 (内外版本分离)
    │
    ├── TM-032 ── 混淆 (FindInterface 名称混淆)
    │
    ├── TM-033 ── 文档整理
    │
    └── TM-034 ── Release Gate
```

### 长期演进
- `def.h` 降级/移除 → 全面标准 C 类型 (Q4 选项 A)
- APP 最终不需要知道 TApplication 存在 (Q1 选项 C)
- 需要 loader 重构支持 RW 重定位后，可用 static inline 替代宏

## 验证状态
- [x] BIN 直接执行 → "Hello AIOS v0"
- [x] BIN2 签名执行 → OK
- [x] BIN3 加密+绑定执行 → OK
- [x] Logel trace: `[hello] dap_api.h v0 OK`
- [x] SDK boundary findstr check → PASS
