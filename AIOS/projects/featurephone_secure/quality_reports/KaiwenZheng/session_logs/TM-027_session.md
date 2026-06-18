# Session Log — TM-27: Device-Bound BIN2 via Bindfile

**Date:** 2026-03-12 ~ 2026-03-13
**Memo:** Technical_Memo_27_ko4_bin2withbindingid.md
**Engineer:** KaiwenZheng
**Outcome:** SUCCESS

---

## Summary

实现并验证了 device-bound BIN2 端到端闭环：`bindfile → PC packer → device-bound BIN2 → loader verify`。
两台设备交叉验证全部通过：绑定设备运行成功，非绑定设备拒绝执行。

---

## Files Created/Modified

| File | Action | Description |
|------|--------|-------------|
| `AIOS/tools/bin2_packer_v2/generate_test_bins_v2.py` | Created | v2 测试样本生成器，4 案例 |
| `AIOS/docs/runbooks/tm27_verification_runbook.md` | Created | 端到端验证运行手册 |
| `Third-party/DAP/security/bin2_loader.c` | Modified | binding check trace 增加 `tm27_` 前缀 |
| `AIOS/MEMORY.md` | Modified | 修正 header size、bindfile 路径、新增 ADR-010 |
| `AIOS/tools/bin2_packer_v2/test/phone1/` | Created | 设备 1 bindfile + 4 个测试 BIN2 |
| `AIOS/tools/bin2_packer_v2/test/phone2/` | Created | 设备 2 bindfile + 4 个测试 BIN2 |

---

## Key Decisions

- **ADR-010:** `bin2_loader.c` binding trace 使用 `tm27_` 前缀便于 Logel 定位
- **保持现有接口不变:** `binding_verify(const BIN2_Header*)` 接口延续 TM-23 设计，重构为 `device_binding_match(uint8[16])` 推迟到后续路线图
- **保持现有错误码不变:** `BIN2_ERR_BINDING = -6`，UI 层映射为 `Err-9`
- **签名覆盖方式确认等价:** `header + zeros(64) + payload` 与 memo 描述的 `header_without_signature + payload` 密码学等价，因嵌入式内存约束采用前者

---

## Verification Results

| Case | 文件 | 设备 | 预期 | 实际 |
|------|------|------|------|------|
| 1 | test_unbound.bin2 | 设备 1 | ✅ 成功 | ✅ 成功 |
| 2 | test_bound.bin2 (设备 1) | 设备 1 | ✅ 成功 | ✅ 成功 |
| 3 | test_tampered_bound.bin2 | 设备 1 | ❌ 拒绝 | ❌ Err-10: BIN2 SIG FAIL |
| 4 | test_crossdevice.bin2 | 设备 1 | ❌ 拒绝 | ❌ Err-9: Bin2 security |
| 5 | test_bound.bin2 (设备 1) | 设备 2 | ❌ 拒绝 | ❌ 交叉验证通过 |
| 6 | test_bound.bin2 (设备 2) | 设备 1 | ❌ 拒绝 | ❌ 交叉验证通过 |
| 7 | test_bound.bin2 (设备 2) | 设备 2 | ✅ 成功 | ✅ 成功 |

---

## 设备信息

| 设备 | Binding ID |
|------|-----------|
| 设备 1 | `71bc7b5e1734c74fb2dd2f6f3144c288` |
| 设备 2 | `c83d300f05a76484bf5947c5ab420971` |

---

## Deviations from Spec

- Memo 提到错误码 `ERR-11`，实际使用 `BIN2_ERR_BINDING = -6`（UI 显示 `Err-9`）— 保持现有编码不做修改
- 未新建代码文件（设备端代码已在 TM-23 中完成），仅增强 trace 和创建测试工具
