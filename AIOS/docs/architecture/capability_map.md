# 聆思 ARCS SDK 能力地图

## 总览

按官方文档现有公开内容，ARCS SDK 可优先按下面的能力域理解：

| 能力域 | 公开重点 | 典型对象 |
|---|---|---|
| 开发工具链 | 环境准备、构建、烧录、调试 | `env.sh`、`build.sh`、`cskburn`、GDB |
| 板型与驱动 | 板级引脚、串口、SPI、I2C、SDIO、DVP | `arcs_evb`、`arcs_mini` |
| 存储与文件系统 | POSIX 接口、LSFS 抽象、FatFS 资源镜像 | LVFS、LSFS、SubFS、`mkfatfs.py` |
| 日志与诊断 | UART 日志、异步输出、级别过滤 | `lisa_log` |
| 网络连接 | 4G Modem、Socket/SSL、DNS、NetDev/SAL | `lisa_modem` |
| 音频 | 本地播放器、Tone 资源、蓝牙音频 | `app_player`、`lisa_bt_audio_framework` |
| 图形界面 | GUI 与控件样例 | LVGL 7/8 |
| 算法 | 唤醒类算法示例 | 单麦/双麦 wakeup |

## 推荐阅读顺序

### 对新项目

1. 快速入门
2. 板型文档
3. 环境与编译/烧录手册
4. 目标组件文档
5. 对应 `samples/` 示例

### 对资源型项目

优先阅读：

- 文件系统
- FatFS 镜像打包工具
- 本地文件系统音频播放示例

### 对联网型项目

优先阅读：

- LISA Modem 组件
- 网络示例
- Logger 组件

### 对蓝牙音频项目

优先阅读：

- Lisa BT Audio Framework
- Bluetooth / network 相关示例

## 能力边界

本次整理只保留官网已公开且可直接指向聆思 ARCS SDK 的内容，不包含：

- 原先 `AIOS/docs` 中基于展锐平台做的能力普查
- 与 UMS9117 / Mocor / MN / DAP 相关的非聆思资料
- 无法从当前官网入口验证的推断性接口列表

## 资料来源

- 快速入门：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/get_started.html>
- 文件系统：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/modules/fs/README.html>
- LISA Modem：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/components/lisa_modem/README.html>
- Logger：<https://docs2.listenai.com/arcs-sdk/v0.1.1/zh/html/components/lisa_log/README.html>
- 蓝牙音频框架：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/components/lisa_bt_audio_framework/README.html>
