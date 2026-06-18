# ARCS SDK API 参考总览

## 说明

本页基于 ARCS SDK 官方 `SDK API 参考` 的 doxygen 索引整理，目的不是照抄全部符号，而是把公开 API 的组织方式、核心头文件和可直接选型的驱动家族梳理清楚。

官方入口：

- `annotated.html`：数据结构总览
- `files.html`：头文件、源文件与目录索引
- `globals_*.html`：按字母排列的宏、函数、变量、枚举与 typedef

## API 的主组织方式

从 `files.html` 可以看到，API 参考当前主要按 `drivers/` 组织，核心模式是：

1. `lisa_xxx.h`
2. `lisa_xxx_arcs.c`
3. 必要时再带 `port/arcs/`、`bus/`、`panels/`、`sensors/` 等子层

这说明 ARCS SDK 的公开接口风格很统一：

- `*.h` 负责对外设备接口
- `*_arcs.c` 负责 ARCS 平台适配
- 复杂模块会把“总线 / 面板 / 传感器 / 端口初始化”拆开

## 当前可确认的驱动家族

| 家族 | 对外头文件 | 说明 |
|---|---|---|
| 设备基类 | `lisa_device.h` | 设备框架基类与设备管理 |
| 调试维测 | `lisa_device_debug.h` | 设备框架调试接口 |
| ADC | `lisa_adc.h` | ADC 设备驱动接口 |
| Audio | `lisa_audio.h` | 音频设备驱动接口 |
| Camera | `lisa_camera.h` | 摄像头设备驱动接口 |
| Display | `lisa_display.h` | 显示设备驱动接口 |
| DVP | `lisa_dvp.h` | DVP 设备驱动接口 |
| Flash | `lisa_flash.h` | Flash 设备驱动接口 |
| GPIO | `lisa_gpio.h` | GPIO 设备驱动接口 |
| HWTimer | `lisa_hwtimer.h` | 硬件定时器接口 |
| I2C | `lisa_i2c.h` | I2C 设备驱动接口 |
| PWM | `lisa_pwm.h` | PWM 设备驱动接口 |
| QSPI LCD | `lisa_qspilcd.h` | QSPI LCD 接口 |
| RGB LCD | `lisa_rgb.h` | 并口 RGB LCD 接口 |
| RTC | `lisa_rtc.h` | 实时时钟接口 |
| SDMMC | `lisa_sdmmc.h` | SD / MMC 存储接口 |
| SPI | `lisa_spi.h` | SPI 设备接口 |
| Touch | `lisa_touch.h` | 触摸设备接口 |
| UART | `lisa_uart.h` | UART 设备接口 |
| Watchdog | `lisa_wdt.h` | 看门狗接口 |

## 复杂模块的分层特征

### Camera

`lisa_camera` 不只是一个头文件，它还包含：

- `lisa_camera_bus.h`
- `lisa_camera_bus_dvp.c`
- `lisa_camera_bus_spi.c`
- `sensor.h`
- `sensor.c`
- 多个 sensor 型号驱动与 `*_regs.h` / `*_settings.h`

这说明摄像头能力是 ARCS SDK 公开 API 中颗粒度比较深的一块。

### Display

`lisa_display` 继续拆为：

- bus 层：QSPI / RGB / 4-wire SPI / software SPI cmd bus
- panel 层：`panel_axs15231b.c`、`panel_st7701s.c`、`panel_st7789p3.c`
- 协议层：`mipi_dcs.h`

因此屏幕项目的文档阅读顺序建议是：

1. `lisa_display.h`
2. 对应 bus
3. 对应 panel
4. 板型页面与样例

### Audio

音频驱动被拆成：

- `lisa_audio.h`
- `lisa_audio_play.c`
- `lisa_audio_record.c`
- `audio_adc_init.*`
- `audio_dac_init.*`

这表明 SDK 在 API 参考里已经同时公开了播放、录音和底层初始化分工。

## Camera 传感器适配矩阵

API 参考里可直接确认的传感器适配头文件包括：

- `bf20a6`
- `bf3005`
- `bf3901`
- `gc0308`
- `gc0310`
- `gc0328`
- `gc032a`
- `gc2145`
- `nt99141`
- `ov2640`
- `ov3660`
- `ov5640`
- `ov7670`
- `ov7725`
- `ov9655`
- `sc030iot`
- `sc031gs`
- `sc101iot`

这部分信息很适合前期做选型对照，因为它至少说明 SDK 文档层已经给出了这些型号的驱动符号和寄存器/配置表结构。

## 如何使用这份 API 参考

### 看接口边界

先看 `files.html`，确认目标能力是一个单层驱动还是多层框架。

### 看结构体

再看 `annotated.html`，确认模块对外暴露的结构体、状态对象和配置对象。

### 看符号

最后按 `globals_*.html` 或具体 `*_8h.html` / `*_8c.html` 页面查函数、宏和变量。

## 资料来源

- API 参考入口：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/_static/api_doc/html/annotated.html>
- File List：<https://docs2.listenai.com/arcs-sdk/v0.1.2/zh/html/_static/api_doc/html/files.html>
