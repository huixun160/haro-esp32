# ARCS SDK 板型与设备能力

## 支持板型

官网快速入门和示例编译页面中反复出现的目标板型主要是：

- `arcs_evb`
- `arcs_mini`

## API 参考中的设备框架

SDK API 参考进一步说明，底层设备能力是围绕 `lisa_device` 框架组织的：

- `lisa_device.h`：设备基类定义
- `lisa_device.c`：设备管理核心实现
- `lisa_device_debug.h`：调试维测接口
- `lisa_device_debug.c`：调试维测实现

可以把它理解为大部分 `lisa_xxx.h` 驱动族的共通基础。

## `arcs_evb`

更适合完整方案验证，公开资料中可确认的接口包括：

- UART
- I2C
- SPI
- GPIO
- PWM
- SDIO
- DVP
- ADC
- LCD 连接器
- TF 卡槽
- 摄像头接口

## `arcs_mini`

更适合紧凑原型和教学验证，公开资料中可确认的接口包括：

- UART
- I2C
- SPI
- GPIO 扩展
- DVP 摄像头接口
- LCD SPI 接口
- 麦克风 / 扬声器 / 电池接口

## 开发建议

- 资源型项目优先 `arcs_evb`
- 紧凑型展示或功能验证可优先 `arcs_mini`
- 编译、引脚、外设接线都要和目标板型保持一致

## 资料来源

- ARCS EVB：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/boards/arcs_evb/README.html>
- ARCS Mini：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/boards/arcs_mini/README.html>
- File List：<https://docs2.listenai.com/arcs-sdk/v0.1.2/zh/html/_static/api_doc/html/files.html>
