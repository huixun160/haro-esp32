# 聆思 ARCS SDK 知识库索引

本索引替代原有展锐 PDF 资产清单，只保留当前与聆思 ARCS SDK 直接相关的官网入口。

## 入口文档

| 主题 | 说明 | 链接 |
|---|---|---|
| 快速入门 | 环境搭建、编译、烧录、常见问题 | <https://docs2.listenai.com/arcs-sdk/latest/zh/html/get_started.html> |
| GDB 调试指南 | J-Link、GDB Server、脚本选择 | <https://docs2.listenai.com/arcs-sdk/latest/zh/html/gdb.html> |
| SDK API 参考 | doxygen 结构体、头文件、全局符号索引 | <https://docs2.listenai.com/arcs-sdk/latest/zh/html/_static/api_doc/html/annotated.html> |
| ARCS EVB | 评估板接口与引脚 | <https://docs2.listenai.com/arcs-sdk/latest/zh/html/boards/arcs_evb/README.html> |
| ARCS Mini | Mini 板接口与引脚 | <https://docs2.listenai.com/arcs-sdk/latest/zh/html/boards/arcs_mini/README.html> |

## 核心组件

| 主题 | 说明 | 链接 |
|---|---|---|
| API 参考总览 | 本地整理版，按驱动家族和阅读路径归纳 | `AIOS/docs/api/api_reference_overview.md` |
| 文件系统 | LVFS / LSFS / SubFS 分层 | <https://docs2.listenai.com/arcs-sdk/latest/zh/html/modules/fs/README.html> |
| LISA Modem | ML307 4G/LTE 组件 | <https://docs2.listenai.com/arcs-sdk/latest/zh/html/components/lisa_modem/README.html> |
| Logger | 串口日志、级别过滤、异步输出 | <https://docs2.listenai.com/arcs-sdk/v0.1.1/zh/html/components/lisa_log/README.html> |
| 蓝牙音频框架 | A2DP / HFP、Sink / Source | <https://docs2.listenai.com/arcs-sdk/latest/zh/html/components/lisa_bt_audio_framework/README.html> |

## 示例

| 主题 | 说明 | 链接 |
|---|---|---|
| 组件模块示例总览 | Player、Logger、LVGL、FS、mbedTLS 等 | <https://docs2.listenai.com/arcs-sdk/latest/zh/html/samples/modules/index_zh.html> |
| 文件系统示例 | LSFS / LVFS 示例集合 | <https://docs2.listenai.com/arcs-sdk/latest/zh/html/samples/modules/fs/index_zh.html> |
| LSFS 示例 | SD 卡挂载、读写、目录遍历 | <https://docs2.listenai.com/arcs-sdk/latest/zh/html/samples/modules/fs/lsfs/README.html> |
| 本地文件系统音频播放 | SD 卡 + 播放器示例 | <https://docs2.listenai.com/arcs-sdk/latest/zh/html/samples/modules/app_player/local_fs/README.html> |
| LVGL 示例 | Benchmark / Widgets | <https://docs2.listenai.com/arcs-sdk/latest/zh/html/samples/modules/lvgl/index_zh.html> |
| 算法组件示例 | 单麦 / 双麦唤醒 | <https://docs2.listenai.com/arcs-sdk/v0.1.1/zh/html/samples/algorithms/index_zh.html> |

## API 参考里可直接确认的驱动家族

- `lisa_device`
- `lisa_adc`
- `lisa_audio`
- `lisa_camera`
- `lisa_display`
- `lisa_dvp`
- `lisa_flash`
- `lisa_gpio`
- `lisa_hwtimer`
- `lisa_i2c`
- `lisa_pwm`
- `lisa_qspilcd`
- `lisa_rgb`
- `lisa_rtc`
- `lisa_sdmmc`
- `lisa_spi`
- `lisa_touch`
- `lisa_uart`
- `lisa_wdt`

参考：<https://docs2.listenai.com/arcs-sdk/v0.1.2/zh/html/_static/api_doc/html/files.html>

## 工具

| 主题 | 说明 | 链接 |
|---|---|---|
| cskburn | 串口烧录、校验、擦除、eMMC/TF | <https://docs2.listenai.com/arcs-sdk/v0.1.3/zh/html/tools/burn/README.html> |
| FAT32 镜像工具 | 目录打包为 FAT32 镜像 | <https://docs2.listenai.com/arcs-sdk/latest/zh/html/tools/fatfs_package/README.html> |
| Tone 工具 | 本地音频资源打包 | <https://docs2.listenai.com/arcs-sdk/latest/zh/html/tools/tone_tool/README.html> |

## 第三方库

公开文档列出的集成方向包括：

- FreeRTOS / FreeRTOS-CPP11 / rtos_al
- LVGL / LVGL8
- coreHTTP / coreSNTP / libcurl / nopoll
- EasyLogger
- SQLite3
- Unity / CppUTest / GoogleTest / FFF

参考：<https://docs2.listenai.com/arcs-sdk/v0.1.0/zh/html/thirds.html>
