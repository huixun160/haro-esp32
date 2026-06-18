# Feedback — TM-029-2: Voice Assistant Asset Migration

**Date:** 2026-03-15
**Memo:** Technical_Memo_29-2
**Outcome:** SUCCESS
**Author:** KaiwenZheng

---

## Execution Summary

按 TM29-1 白名单成功将语音助手 APP 全部资产迁入可信主线。编译通过，设备验证 APP 加载、API 注册、WebSocket 连接均成功。TM28-R 安全基线未被破坏。

## Completed Work

- [x] 白名单资产迁移 (5 直接复制 + 3 替换 + 3 手动合并)
- [x] PAC 固件编译成功
- [x] voice_chat.bin 编译成功
- [x] 设备加载验证 (API 注册 + WebSocket 连通)
- [x] DSP 蓝屏根因分析 + AMR 模式修复

## Incomplete Work

- [ ] DSP 蓝屏修复待重编译验证 (BS_AUDIO_USE_AMR=1)
- [ ] CJK 字库配置 (需 James git 参考)
- [ ] SSL 间歇失败优化 (mbedTLS 配置)

## Key Decisions

1. `dap_audio_bridge.c/h` 采用直接替换策略 — 分析确认为纯追加超集
2. SDK 文件仅 `lvgl_api.h` 需更新（其余 byte-identical）
3. DSP 崩溃疑似 PCM 格式不兼容，改为 AMR-NB 模式

## Risk Assessment

- TM28-R 安全基线: ✅ 无回退
- dap.mk: ✅ 手动合并，安全入口完整

## Next Actions

1. 用户重编译验证 AMR 录音是否消除蓝屏
2. 获取 James git 参考解决字库和 SSL
3. 开 TM29-3: 完整语音链路调通
