# ARCS SDK 驱动与 HAL 关注点

## 说明

官网导航中存在“设备驱动”章节，但当前公开入口里更容易直接确认的是板型页面和示例页面，因此本页只保留已经能够明确落到开发动作上的设备能力。

## 开发时最常见的底层接口

- UART：日志、烧录、AT 通信
- SPI：LCD、部分摄像头或外设
- I2C：摄像头与常见外设控制
- GPIO：LED、复位、功放使能、外设控制
- PWM：背光等
- SDIO：SD 卡 / eMMC / TF
- DVP：摄像头
- ADC：按键或模拟信号采样

## API 参考里已经明确公开的驱动头文件

根据 doxygen `files.html`，当前可直接查阅的底层驱动接口包括：

- `lisa_adc.h`
- `lisa_flash.h`
- `lisa_gpio.h`
- `lisa_hwtimer.h`
- `lisa_i2c.h`
- `lisa_pwm.h`
- `lisa_rtc.h`
- `lisa_sdmmc.h`
- `lisa_spi.h`
- `lisa_uart.h`
- `lisa_wdt.h`
- `lisa_dvp.h`

显示与摄像头、LCD 强相关的接口还有：

- `lisa_qspilcd.h`
- `lisa_rgb.h`
- `lisa_display.h`
- `lisa_touch.h`

这比单看板型页更重要，因为它直接说明了 SDK API 参考已经给出哪些驱动家族可查。

## 实际落地建议

- 烧录链路先确认 UART
- 调试链路先确认日志 UART 与 J-Link
- 资源链路优先确认 SDIO / 文件系统
- 多媒体链路优先确认 LCD、音频、摄像头

## 资料来源

- ARCS EVB：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/boards/arcs_evb/README.html>
- ARCS Mini：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/boards/arcs_mini/README.html>
- File List：<https://docs2.listenai.com/arcs-sdk/v0.1.2/zh/html/_static/api_doc/html/files.html>
