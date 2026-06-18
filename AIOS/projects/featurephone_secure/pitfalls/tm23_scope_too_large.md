# Pitfall: TM-23 scope too large — device binding needs phased approach

**发现时间：** 2026-03-12
**来源：** TM-23 实现过程

---

## 症状

一次性实现 BIN2 设备绑定（修改 header 格式 + 新模块 + packer 工具），编译失败且无法逐步验证。

## 根因

1. **BIN2 header 格式变更（48→64）**影响全链路：loader、packer、测试文件全部需要同步更新
2. 新模块 `device_binding.c` 引用了 `dap_sha256.h`（文件名不匹配），编译失败
3. 无法单独验证绑定逻辑的正确性

## 教训

嵌入式安全功能必须**分阶段递增实现**：

1. **先可观测** — 新功能的核心计算结果先输出到 Logel trace
2. **再可导出** — 确认计算正确后，再实现文件导出
3. **最后集成** — 确认所有前置条件就绪后，才修改格式和验证链

## 预防

- 新安全功能的 Technical Memo 应拆为 ≤3 个文件修改的小步骤
- 每步必须有独立的 Logel 验证标准
- 格式变更（header 结构体修改）应作为最后一步
