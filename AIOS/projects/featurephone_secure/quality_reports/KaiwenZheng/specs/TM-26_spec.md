# Frozen Specification — TM-26 Bindfile Export to Device Filesystem (Phase-1B)

## MUST
- [ ] 设备生成 JSON 格式 `device.bind` 文件到 `FileArray/device.bind`
- [ ] JSON 包含 `version`, `binding_alg`, `binding_id`, `device_model` 字段
- [ ] `binding_id` 为 SHA256("AIOS-BIND-V1" || DeviceSecret)[0..15] 的 hex 字符串 (32 chars)
- [ ] bindfile 不包含 DeviceSecret（安全要求）
- [ ] `*#3472#` Debug Menu 提供 "Generate Bindfile" 功能并触发生成
- [ ] BIN2 执行时若 `device.bind` 不存在则自动生成
- [ ] 生成时输出 Logel trace（使用 `DAP_DBG`，前缀 `[bind] tm26_`）
- [ ] `dap.mk` 包含所有新增源文件
- [ ] 创建 `device_bindfile.c` / `device_bindfile.h` 封装导出逻辑
- [ ] 创建架构文档 `AIOS/docs/architecture/device_binding_phase1b.md`

## SHOULD
- [ ] 覆盖旧文件（避免多个 bind 文件）
- [ ] `device_model` 字段填充设备型号 `ums9117`
- [ ] 文件可被 PC 直接读取（JSON 纯文本）

## MAY
- [ ] 未来扩展 `device_model` 为完整型号字符串

## OUT OF SCOPE
- PC packer 读取 bindfile 集成（TM-27）
- App Store 设备注册
- BIN2 header 绑定集成

Approved by: [engineer name]
Date: 2026-03-12
