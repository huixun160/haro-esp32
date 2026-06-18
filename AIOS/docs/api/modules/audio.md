# ARCS SDK 音频能力

## 公开主线

从官网现有文档看，ARCS SDK 的音频开发主要围绕以下路径：

- 本地文件系统音频播放
- Tone 本地音频资源打包
- 蓝牙音频框架
- 与文件系统、日志、板级音频接口联动

## 本地播放

`samples/modules/app_player/local_fs` 演示了标准本地播放流程：

1. 挂载 FAT32 文件系统
2. 创建播放器实例
3. 注册事件回调
4. 播放本地 MP3
5. 执行暂停、恢复、停止等控制

默认挂载点示例为 `/SD:`。

## 资源准备

本地音频示例使用 `mkfatfs.py` 把资源目录打包为 FAT32 镜像，这通常是资源型项目的推荐做法。

## Tone 工具

官网还提供本地音频打包工具，可把多个音频文件打成：

- `tone.bin`
- `tone.h`

适合提示音、播报音、固化音频资源场景。

## 蓝牙音频框架

`lisa_bt_audio_framework` 的公开定位是：

- 支持 A2DP / HFP
- 支持 Sink / Source 两种模式
- 提供 session、codec、缓冲和线程调度框架
- 通过硬件抽象层接入 `lisa_audio` 或虚拟接口

已公开的编解码支持包括：

- SBC
- mSBC
- CVSD

典型场景：

- 蓝牙音箱
- 蓝牙电话
- 音频前处理 / AI 算法处理链路

## API 参考里的底层音频接口

SDK API 参考显示，音频驱动除了高层组件文档外，还公开了：

- `lisa_audio.h`
- `lisa_audio_play.c`
- `lisa_audio_record.c`
- `audio_adc_init.h`
- `audio_dac_init.h`
- `lisa_audio_arcs.c`

因此如果后续需要继续细化文档，建议把音频能力分成两层理解：

1. 组件层：播放器、音频资源、蓝牙音频框架
2. 驱动层：播放、录音、ADC/DAC 初始化与 ARCS 适配

## 资料来源

- 本地文件系统音频播放：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/samples/modules/app_player/local_fs/README.html>
- Tone 工具：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/tools/tone_tool/README.html>
- 蓝牙音频框架：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/components/lisa_bt_audio_framework/README.html>
- File List：<https://docs2.listenai.com/arcs-sdk/v0.1.2/zh/html/_static/api_doc/html/files.html>
