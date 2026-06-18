# ARCS SDK 蓝牙能力

## 当前公开重点

当前官网公开信息里，蓝牙方向最完整的是 `Lisa BT Audio Framework`，重点不是传统 GAP/GATT 文档，而是蓝牙音频场景框架。

## 框架特点

- 支持 `A2DP` / `HFP`
- 支持 `Sink` / `Source`
- 通过 session 机制解耦业务与硬件
- 提供 codec、缓冲、线程调度
- 可接 `lisa_audio` 或虚拟音频接口

## 典型模式

### Sink

手机推送音乐到设备，设备本地播放。

### Source

设备采集音频并发送到蓝牙耳机或其他终端。

## 典型性能信息

官网公开了大致量级：

- 启动延迟约 `60-100ms`
- 内存占用约 `50-100KB`
- SBC 解码 CPU 占用约 `5-15%`

## 对项目的意义

如果你的目标是做“音箱、耳机、通话、蓝牙音频转发”类功能，这套框架比单纯查 API 更值得先读，因为它已经给出模块划分和推荐接法。

## 资料来源

- 蓝牙音频框架：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/components/lisa_bt_audio_framework/README.html>
