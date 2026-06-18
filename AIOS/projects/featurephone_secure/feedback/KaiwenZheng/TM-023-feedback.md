# TM-023 Feedback — Offline Device Binding

**Date:** 2026-03-12
**Memo:** Technical_Memo_23_bin2bindingdevice.md
**Outcome:** PARTIAL — 编译未通过，范围过大需拆分
**Author:** AIOS Founding Team

---

## 已完成工作

### 设备端代码（已编写，未编译通过）
- `bin2_format.h` — Header 48→64 bytes, version 1→2, 新增 `binding_id[16]`, `BIN2_ERR_BINDING`
- `device_binding.h/.c` — BindingID 派生 + 验证 + `.bind` 文件导出
- `bin2_loader.c` — 新增 binding 校验步骤（step 6）
- `DAP_Loader_unisoc.c` — `.bind` 自动导出到 `D:\DAP\device.bind`
- `dap.mk` — 添加 `device_binding.c`

### PC 端工具
- `bin2_packer_v2/bin2_pack.py` — v2 header + `--bind-file` 支持
- `bin2_packer_legacy/` — 旧版 packer 备份（原目录编辑器锁定未删除）

---

## 编译错误

```
[dap] "Third-party/DAP/security/device_binding.c", line 16: Error: #5: 
      cannot open source input file "dap_sha256.h": No such file or directory
```

**根因：** SHA-256 头文件名不匹配。实际文件可能是 `sha256.h` 或通过 `dap_sha256.h` wrapper 导出，需要确认实际文件名。

---

## 阻塞原因

TM-23 范围过大，一次性实现全部功能风险高：
1. device_binding 模块需要逐步验证
2. BIN2 header 格式变更影响全链路
3. 新 packer 工具需要与设备端协同验证

---

## 建议拆分为 3 个阶段

### Phase 1 — BindingID 可观测（建议 TM-24）
**目标：** 设备开机后，Logel 中能搜到 BindingID

**工作范围：**
- 修复 `device_binding.c` 的 `#include` 问题
- 实现 `binding_derive_id()` — SHA256("AIOS-BIND-V1" || DeviceSecret)[0..15]
- 在 `DAP_LoaderInit` 中调用并输出到 Logel
- **不改 BIN2 header**，**不改 packer**，**不改 loader 验证链**

**验证标准：**
```
Logel 搜 [BIND] → 看到 BindingID[0..7]=xx xx xx xx xx xx xx xx
```

---

### Phase 2 — .bind 文件导出（建议 TM-25）
**目标：** 设备自动生成 `D:\DAP\device.bind`，用户可通过 USB 拷贝

**工作范围：**
- 实现 `binding_export_bindfile()` — SFS 文件写入 JSON
- 用户拷贝 `.bind` 到 PC 验证 JSON 内容正确
- **不改 BIN2 header**，**不改 packer**，**不改 loader 验证链**

**验证标准：**
```
USB 连接 → 找到 D:\DAP\device.bind → JSON 内容包含 binding_id
```

---

### Phase 3 — BIN2 设备绑定（建议 TM-26）
**目标：** BIN2 文件只能在指定设备运行

**工作范围：**
- `bin2_format.h` header 扩展 48→64
- `bin2_loader.c` 新增 binding 校验
- `bin2_packer_v2` 支持 `--bind-file`
- 全链路测试（UNBOUND / DEVICE_BOUND / 跨设备拒绝）

**验证标准：**
```
test_valid_bound.bin2 (同设备) → 执行成功
test_valid_bound.bin2 (异设备) → ERR-11 BIND FAIL
test_valid_unbound.bin2 → 执行成功（兼容）
```

---

## 当前代码状态

> [!WARNING]
> 当前代码有编译错误，不可直接使用。需先还原或修复后再编译。

建议 git 操作：
```bash
# 暂存当前工作（保留代码供后续 memo 使用）
git stash -m "TM-23 partial: device binding (compile error, needs phased approach)"

# 或者提交到单独分支
git checkout -b tm23-partial
git add -A
git commit -m "TM-23: Partial device binding implementation (compile error)

Work items completed but not verified:
- bin2_format.h: v2 header (48->64 bytes)  
- device_binding.h/.c: BindingID module
- bin2_loader.c: binding check
- DAP_Loader_unisoc.c: .bind auto-export
- dap.mk: +device_binding.c
- bin2_packer_v2: v2 packer tool

Compile error: dap_sha256.h not found
Plan: split into TM-24 (BindingID trace), TM-25 (.bind export), TM-26 (BIN2 binding)"
git checkout master
```

---

## 修改文件清单

| 文件 | 操作 | 状态 |
|------|------|------|
| `bin2_format.h` | MODIFIED | ⚠️ 未验证 |
| `device_binding.h` | NEW | ⚠️ 编译错误 |
| `device_binding.c` | NEW | ⚠️ 编译错误 |
| `bin2_loader.c` | MODIFIED | ⚠️ 未验证 |
| `DAP_Loader_unisoc.c` | MODIFIED | ⚠️ 未验证 |
| `dap.mk` | MODIFIED | ✅ 语法正确 |
| `bin2_packer_v2/bin2_pack.py` | NEW | ✅ Python 语法正确 |
| `bin2_packer_legacy/` | COPIED | ✅ 完成 |
