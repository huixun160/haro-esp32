# Feedback — TM-021: BIN2 Signature Verification Failure Root Cause Isolation

**Date:** 2026-03-11
**Memo:** Technical_Memo_21_bin2tm15bugcause.md
**Outcome:** RESOLVED ✅ (TM-22 修复后设备端确认 `ed25519_verify ret=0`，签名链闭环)
**Author:** AIOS Founding Team

---

## Execution Summary

完成 TM-21 的诊断代码部署和根因分析（Steps 1-5）。在准备设备测试阶段发现内存泄漏 bug，需优先处理，暂停 TM-21。

---

## Completed Work

- [x] **Step 1 — 固化日志规则**：确认 `DAP_DBG`/`DAP_DBG_ERR` → `DAP_TracePrint` → `SCI_TRACE_LOW` 链路可用，统一 `[bin2]` 和 `tm15_` 前缀
- [x] **Step 2 — 设备端诊断 trace**：在 `bin2_crypto.c` 中添加完整的 signed region 分析
  - `tm15_sig_verify: total/hdr/sig/pay`
  - `tm15_sig_verify: payload_off/signed_region_len`
  - `tm15_sig[0..7]`, `tm15_pubkey[0..7]`, `tm15_hdr[0..7]`, `tm15_payload[0..7]`
  - `tm15_msg_hash[0..7]` — SHA-256 of signed region（诊断用，非验签逻辑）
- [x] **Step 3 — PC 端对照输出**：在 `bin2_pack.py` 添加 `--debug` 模式，输出与设备端完全对齐的诊断格式
- [x] **Step 4 — 代码分析**：确认 PC↔设备 signed region 构造逻辑一致（ADR-002: `header(48) + zeros(64) + payload`）
- [x] **Step 5 — 根因分析**：完成根因文档 `docs/tm15_sigfail_rootcause.md`，定位最可能原因为 Ed25519 C 实现（TweetNaCl-derived SHA-512 增量哈希）
- [x] **验证模板**：创建 `docs/tm15_sigfix_validation.md`，含 PC 端参考值和设备端对比模板

---

## Incomplete Work

- [ ] **Step 6 — 设备测试**：编译烧录后在 Logel 抓取 `tm15_msg_hash` 与 PC 端对比，判定结论 A/B
- [ ] **Step 7 — 修复验证**：`test_valid.bin2` 通过 / `test_tampered.bin2` 拒绝 / `test_badsig.bin2` 拒绝
- [ ] **结论确认**：给出明确的"结论 A"（signed region 不一致）或"结论 B"（Ed25519 实现bug）

---

## Blocking Issues

| Issue | Symptom | Root Cause | Status |
|---|---|---|---|
| **内存泄漏** | 设备运行中出现内存泄漏 | 待排查（可能与 DAP 模块相关） | ⛔ 需优先处理 |

---

## Verification Status

| Test | Result | Notes |
|---|---|---|
| `bin2_crypto.c` 诊断代码添加 | ✅ PASS | SHA-256 diagnostic + 全套 trace 输出 |
| `bin2_pack.py` --debug 模式 | ✅ PASS | 与设备端 tm15_ 格式完全对齐 |
| `docs/tm15_sigfail_rootcause.md` | ✅ PASS | 根因分析完成，含 PC 端参考值 |
| `docs/tm15_sigfix_validation.md` | ✅ PASS | 验证模板已创建，PC 端值已填入 |
| 编译验证 | ⏳ PENDING | 因内存泄漏暂停 |
| 设备 Logel 验证 | ⏳ PENDING | 因内存泄漏暂停 |
| PC↔设备 msg_hash 对比 | ⏳ PENDING | 因内存泄漏暂停 |

---

## 根因分析要点总结

### 1. Signed Region 构造（已排除逻辑问题）

- PC 端：`message = header + b'\x00'*64 + payload` (bin2_pack.py L149)
- 设备端：in-place 清零 signature 区域，传入完整 buffer (bin2_crypto.c L196-211)
- **结论：逻辑一致，均符合 ADR-002**

### 2. 公钥匹配

- 设备端 `BIN2_PUBLIC_KEY[32]` 首 8 字节：`eb e2 1c 44 2e 0c f7 ad`
- PC 端 `public_key.bin` 首 8 字节：`eb e2 1c 44 2e 0c f7 ad`
- **结论：匹配**

### 3. 最可能根因（待设备验证确认）

**Hypothesis A（最可能）：Ed25519 C 实现中 SHA-512 增量哈希 bug**
- `ed25519_verify.c` 是 TweetNaCl-derived，676 行
- 手写 SHA-512 增量哈希（L562-614），128字节分块处理
- 对 748 字节输入（R||A||M = 64+684），分块边界和 padding 逻辑有 off-by-one 风险
- PyNaCl 使用 libsodium，被广泛验证

**Hypothesis B：PyNaCl vs TweetNaCl Ed25519 内部格式差异**

**Hypothesis C：32-bit ARM 64-bit 整数运算问题**

### 4. 验证判定逻辑（恢复 TM-21 时使用）

```
if device.tm15_msg_hash == pc.tm15_msg_hash:
    # Signed region 一致 → 问题在 Ed25519 实现 → Step 6
    # 用 RFC 8032 标准测试向量验证 ed25519_verify.c
else:
    # Signed region 不一致 → 问题在 message 拼接 → 检查字节级 dump
```

PC 端参考值（`test_valid.bin2`）：
```
tm15_msg_hash[0..7] = fd f1 03 cc 1d a4 0d 42
```

---

## 新增/修改文件清单

| File | Action | Description |
|---|---|---|
| `Third-party/DAP/security/bin2_crypto.c` | MODIFIED | 添加 TM-21 诊断 SHA-256 hash + trace 输出 |
| `AIOS/tools/bin2_packer/bin2_pack.py` | MODIFIED | 添加 `--debug` TM-21 诊断模式 |
| `docs/tm15_sigfail_rootcause.md` | CREATED | 根因分析文档 |
| `docs/tm15_sigfix_validation.md` | CREATED | 设备验证模板 |

---

## Pitfall（本次新增）

### 内存泄漏排查优先级高于功能开发

- **触发时机：** TM-21 设备测试阶段
- **教训：** 内存泄漏会影响所有后续功能的验证可靠性，必须优先解决
- **建议：** 下一个 TM 专门处理内存泄漏，确定泄漏源再恢复 TM-21

---

## Next Actions

1. **🔴 优先：** 排查并修复内存泄漏 bug — 建议开新 Technical Memo (TM-22)
2. **恢复 TM-21**：内存泄漏修复后：
   - 编译烧录
   - 在 Logel 抓取 `tm15_msg_hash[0..7]`
   - 与 PC 端 `fd f1 03 cc 1d a4 0d 42` 对比
   - 判定结论 A 或 B
3. **如果是结论 B**：用 RFC 8032 Ed25519 标准测试向量验证 `ed25519_verify.c`

---

## Git Guidance

当准备提交当前 TM-21 的工作时：

```bash
git add Third-party/DAP/security/bin2_crypto.c
git add AIOS/tools/bin2_packer/bin2_pack.py
git add docs/tm15_sigfail_rootcause.md
git add docs/tm15_sigfix_validation.md
git add AIOS/technical_memos/Technical_Memo_21_bin2tm15bugcause.md
git add AIOS/quality_reports/plans/TM-21_plan.md
git add AIOS/feedback/TM-021-feedback.md

git commit -m "TM-21: BIN2 sig verify root cause diagnostic (partial - paused for memory leak)

- Add SHA-256 diagnostic hash in bin2_crypto.c for PC<->device comparison
- Add --debug mode to bin2_pack.py with matching tm15_ trace format
- Document root cause analysis: Ed25519 TweetNaCl SHA-512 impl most likely
- Create device validation template with PC reference values
- Status: diagnostic code ready, device test pending memory leak fix"
```

> ⚠️ 请手动在终端执行以上命令。如果还未 `git init`，请先运行 `git init`。

---

## References

- Memo: `AIOS/technical_memos/Technical_Memo_21_bin2tm15bugcause.md`
- Plan: `AIOS/quality_reports/plans/TM-21_plan.md`
- Root Cause: `docs/tm15_sigfail_rootcause.md`
- Validation: `docs/tm15_sigfix_validation.md`
- Previous: `AIOS/feedback/TM-020-feedback.md`
