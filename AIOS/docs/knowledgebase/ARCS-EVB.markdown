# Arcs-EVB 开发板

## 概述

Arcs-EVB 是一款基于聆思设计的大模型语音交互开发板，并默认接入小聆AI大模型链路，方便用户快速搭建大模型智能硬件原型。

![](https://docs2.listenai.com/zz/11098.png?shortId=cWWqDKaBN)

## 功能与特性

### 主要特性

* 使用聆思 LS26系 AI芯片(`LS2684L0U`)，支持WIFI+BLE/BT无线连接，内置NPU
* 板载 16MB Flash，集成 摄像头、(单)麦克风、扬声器、2.4寸屏幕 等丰富外设
* 云端接入全新 小聆AI，大模型应用、MCP服务轻松调用
* 尺寸小巧，支持传感器扩展与配件外引，方便 AI 玩具 DIY

### 规格参数

| 产品参数 | Arcs-Mini                                                      |
| -------- | -------------------------------------------------------------- |
| 外观尺寸 | 100*80mm                                                       |
| 屏幕     | TP-LCM模组，全贴合，2.40inch，GFF，320X240，65.05X47.85X3.33mm |
| 摄像头   | 像素：30W``型号：GC0328                                 |
| 喇叭     | 8Ω 2W                                                         |
| 麦克风   | 信噪比：65dB``灵敏度：-32dB                             |
| 按键     | 主功能按键 + RST + BOOT                                        |
| USB      | TypeC接口，支持充电/烧录/数据传输                              |

## 开发板硬件说明

### 按键说明

| 按键               | 功能描述                 |
| ------------------ | ------------------------ |
| **BOOT按键** | 长按上电进入芯片烧录模式 |
| **RST按键**  | 复位按键                 |
| **K1按键**   | 模拟唤醒按键             |
| **K2按键**   | 短按进入配网模式         |
| **K3按键**   | 连续3次短按恢复出厂设置  |

### 开发板硬件资源说明

以下按照顺时针顺序依次介绍开发板上正面的主要组件：

| 主要组件        | 说明                                                                  |
| --------------- | --------------------------------------------------------------------- |
| LS26 AI 芯片    | 主控芯片，型号为 LS2684L0U，支持WIFI/BLE&BT，内置 16MB PSRAM 与 NPU。 |
| Flash           | 16MB Flash，用于存储固件镜像与相关资源。                              |
| IO 扩展接口     | 引出30个IO口和多组电源                                                |
| 主功能按键      | 用于对开发板进行开关机、复位、交互触发等操作。                        |
| USB接口         | TypeC 接口，具备供/充电与固件烧录功能(需已烧录过boot固件)。           |
| 可编程 LED      | 支持通过编程进行控制的 LED，使用引脚为 B09。                          |
| RST 按键        | Reset按键，短按该按键可对开发板进行复位运行操作。                     |
| 预留烧录串口    | 引出可用于烧录 boot 固件、日志查看的引脚。                            |
| 屏幕 SPI 接口   | 屏幕连接器，用于连接开发板默认配套的显示屏。                          |
| 摄像头 DVP 接口 | 摄像头FPC连接器，用于连接开发板默认配套的摄像头。                     |
| 功放 IC         | 音频功率放大器芯片，用于放大音频信号以驱动扬声器。                    |
| 扬声器接口      | 用于连接开发板默认配套的扬声器，方便用户更换或外引扬声器。            |
| 麦克风接口      | 用于连接开发板默认配套的驻极体麦克风，方便用户更换或外引麦克风。      |

### 其他配件说明

#### LCD屏幕

Arcs-EVB 默认配套一款 2.4 寸的屏幕，相关参数如下：

| 项目                       | 规格                                                             |
| -------------------------- | ---------------------------------------------------------------- |
| 液晶面板尺寸               | 2.4 inch (对角线)                                                |
| 颜色                       | 262K（262,144色）                                                |
| 驱动IC                     | ST7789P3                                                         |
| 接口类型                   | 支持命令/数据选择的串行接口 (常称为 3线SPI + D/C 或 4线串行接口) |
| LCD Size 液晶面板尺寸      | 2.4 inch                                                         |
| Panel Active Area 可视区域 | 36.72 (H) × 48.96 (V) mm                                        |
| Resolution 分辨率          | 240 (H) x 320 (V) pixels                                         |

屏幕模组尺寸与排线线序：
![](https://docs2.listenai.com/zz/10166.png?shortId=cWWqDKaBN)
屏幕模组规格书：

[TFT024B423产品规格书.pdf](https://docs2.listenai.com/zz/11668.pdf?shortId=cWWqDKaBN)

#### 摄像头

Arcs-EVB 默认配套一款 30W 像素摄像头，相关参数如下：
![](https://docs2.listenai.com/zz/10165.png?shortId=cWWqDKaBN)

### GPIO 与外设引脚分配表

下表为 LS26 芯片在 Arcs-Mini 开发板上的 GPIO 分配使用列表：

| 引脚/端口              | 主功能           | 复用功能     | 说明/连接外设     | 分类          |
| ---------------------- | ---------------- | ------------ | ----------------- | ------------- |
| **GPIOA_00**     | LCD_PWM          | CJTAG_TCK    | LCM模组背光控制   | 显示          |
| **GPIOA_01**     | LCD RST          | CJTAG_TMS    | LCM模组复位       | 显示          |
| **GPIOA_02**     | UART0 RX         |              | LOAD&打印CP日志   | 烧录&日志     |
| **GPIOA_03**     | UART0 TX         |              | LOAD&打印CP日志   | 烧录&日志     |
| **GPIOA_04**     | SD DAT1          |              | TF CARD           | 存储          |
| **GPIOA_05**     | SD DAT0          |              | TF CARD           | 存储          |
| **GPIOA_06**     | SD CLK           |              | TF CARD           | 存储          |
| **GPIOA_07**     | SD CMD           |              | TF CARD           | 存储          |
| **GPIOA_08**     | SD DAT3          |              | TF CARD           | 存储          |
| **GPIOA_09**     | SD DAT2          |              | TF CARD           | 存储          |
| **GPIOA_10**     | vic_h_sync       |              | DVP摄像头         | 兼容SPI摄像头 |
| **GPIOA_11**     | vic_v_sync       |              | DVP摄像头         | 兼容SPI摄像头 |
| **GPIOA_12**     | vic_pixel_clk    |              | DVP摄像头         | 兼容SPI摄像头 |
| **GPIOA_13**     | vic_pixel_data4  |              | DVP摄像头         | 兼容SPI摄像头 |
| **GPIOA_14**     | vic_pixel_data5  |              | DVP摄像头         | 兼容SPI摄像头 |
| **GPIOA_15**     | vic_pixel_data6  |              | DVP摄像头         | 兼容SPI摄像头 |
| **GPIOA_16**     | vic_pixel_data7  |              | DVP摄像头         | 兼容SPI摄像头 |
| **GPIOA_17**     | vic_pixel_data8  |              | DVP摄像头         | 兼容SPI摄像头 |
| **GPIOA_18**     | vic_pixel_data9  |              | DVP摄像头         | 兼容SPI摄像头 |
| **GPIOA_19**     | vic_pixel_data10 |              | DVP摄像头         | 兼容SPI摄像头 |
| **GPIOA_20**     | vic_pixel_data11 |              | DVP摄像头         | 兼容SPI摄像头 |
| **GPIOA_21**     | UART1_TX         |              | 打印AP日志        | 调试          |
| **GPIOA_22**     | I2C0 SDA         |              | 摄像头和TP复用    | LCM模组       |
| **GPIOA_23**     | I2C0 SCL         |              | 摄像头和TP复用    | LCM模组       |
| **GPIOA_24**     | TP INT           |              | 触摸中断          | LCM模组       |
| **GPIOA_25**     | TP RST           |              | 触摸复位          | LCM模组       |
| **GPIOA_26**     | VIC_CLK_OUT      |              | MCLK (主时钟)     | 摄像头        |
| **GPIOA_27**     | PA_EN            |              | 功放MUTE          | 音频          |
| **GPIOA_28**     | MIC1 INP         |              | 硅麦              | 音频          |
| **GPIOA_29**     | MIC1 INN         |              | 硅麦              | 音频          |
| **GPIOA_30**     | MIC0 INP         |              | 硅麦              | 音频          |
| **GPIOA_31**     | MIC0 INN         |              | 硅麦              | 音频          |
| **GPIOB_00**     | LCD SPI MISO     | D1           | LCM模组 (数据线1) | 显示 (SPI)    |
| **GPIOB_01**     | LCD SPI MOSI     | D0           | LCM模组 (数据线0) | 显示 (SPI)    |
| **GPIOB_02**     | LCD SPI HOLD     | D3           | LCM模组 (数据线3) | 显示 (SPI)    |
| **GPIOB_03**     | LCD SPI CLK      | CLK          | LCM模组 (时钟线)  | 显示 (SPI)    |
| **GPIOB_04**     | LCD SPI WP       | D2           | LCM模组 (数据线2) | 显示 (SPI)    |
| **GPIOB_05**     | LCD_SPI CS       | CS           | LCM模组 (片选)    | 显示 (SPI)    |
| **GPIOB_06**     | KEY1             |              | ADC按键           | 输入/控制     |
| **GPIOB_07**     | KEY2             |              | 触摸按键          | 输入/控制     |
| **GPIOB_08**     | LCD_TE           |              | LCD TE中断        | 显示/中断     |
| **GPIOB_09**     | LED              |              | 单色指示灯        | GPIO          |
| **FLASH_CS_N**   | FLASH_CS_N       | FLASH_CS_N   | Boot Flash        | 存储 (Flash)  |
| **FLASH_MISO**   | FLASH_MISO       | FLASH_MISO   | Boot Flash        | 存储 (Flash)  |
| **FLASH_WP_N**   | FLASH_WP_N       | FLASH_WP_N   | Boot Flash        | 存储 (Flash)  |
| **FLASH_HOLD_N** | FLASH_HOLD_N     | FLASH_HOLD_N | Boot Flash        | 存储 (Flash)  |
| **FLASH_CLK**    | FLASH_CLK        | FLASH_CLK    | Boot Flash        | 存储 (Flash)  |
| **FLASH_MOSI**   | FLASH_MOSI       | FLASH_MOSI   | Boot Flash        | 存储 (Flash)  |
| **USB_DP**       | USB_DP           |              | USB口             | 通信 (USB)    |
| **USB_DM**       | USB_DM           |              | USB口             | 通信 (USB)    |
| **LIN_OUTP**     | LIN_OUTP         |              | 差分输出 正       | 音频          |
| **LIN_OUTN**     | LIN_OUTN         |              | 差分输出 反       | 音频          |

## ARCS-EVB开发板硬件资料

### 一、ARCS核心模块硬件资料

| 类型           | 文件描述                                     | 文件链接                                                                                                 |
| -------------- | -------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| 原理图         | ARCS_D_QFN76模块测试点VDD核心原理图(DSN格式) | [ARCS_D_QFN76_Module_TestPad_VDD_CORE.DSN](https://docs2.listenai.com/zz/11106.dsn?shortId=cWWqDKaBN)       |
| 原理图         | ARCS_D_QFN76模块测试点VDD核心原理图(PDF格式) | [ARCS_D_QFN76_Module_TestPad_VDD_CORE.pdf](https://docs2.listenai.com/zz/9873.pdf?shortId=cWWqDKaBN)        |
| 模组引脚丝印图 | ARCS_D_QFN76模块引脚丝印图                   | [ARCS_D_QFN76 模组引脚丝印图.pdf](https://docs2.listenai.com/zz/11107.pdf?shortId=cWWqDKaBN)                |
| PCB文件        | ARCS_D_QFN76核心PCB文件                      | [ARCS_D_QFN76_Module_TestPad_VDD_CORE.brd](https://docs2.listenai.com/zz/11105.brd?shortId=cWWqDKaBN)       |
| 生产Gerber文件 | ARCS Module硬件生产资料-已经过生产验证4-11   | [ARCS Module硬件生产资料-已经过生产验证4-11.rar](https://docs2.listenai.com/zz/11104.rar?shortId=cWWqDKaBN) |

### 上述图纸是使用Allegro画的图纸，如果对Allegro不熟悉可以使用以下办法来解决

我们提供了AD版本的PCB和PADS版本的原理图（因为是从Allegro转换过来的，所以仅供封装调用使用）

以下是AD版本的PCB(可以直接导入LCEDA）
[ARCS_D_QFN76_Module_TestPad_VDD_CORE.PcbDoc](https://docs2.listenai.com/zz/11099.pcbdoc?shortId=cWWqDKaBN)
以下是PADS版本的SCH
[ARCS_D_QFN76_Module_TestPad_VDD_CORE.sch](https://docs2.listenai.com/zz/11100.sch?shortId=cWWqDKaBN)

### 二、ARCS-EVB底板硬件资料

#### V03硬件版本（最新）

| 类型    | 文件描述                    | 文件链接                                                                        |
| ------- | --------------------------- | ------------------------------------------------------------------------------- |
| 原理图  | LS2684L0U_EVB_IV03(DSN格式) | [LS2684L0U_EVB_IV03.DSN](https://docs2.listenai.com/zz/9893.dsn?shortId=cWWqDKaBN) |
| 原理图  | LS2684L0U_EVB_IV03(PDF格式) | [LS2684L0U_EVB_IV03.pdf](https://docs2.listenai.com/zz/9894.pdf?shortId=cWWqDKaBN) |
| PCB文件 | LS2684L0U_EVB_IV03(PCB格式) | [LS2684L0U_EVB_IV03.pcb](https://docs2.listenai.com/zz/9879.pcb?shortId=cWWqDKaBN) |

### 三、ARCS-EVB开发板PIN-MAP资料

| 类型     | 文件描述                | 文件链接                                                                         |
| -------- | ----------------------- | -------------------------------------------------------------------------------- |
| 引脚映射 | ARCS-EVB开发板PIN映射表 | [ARCS开发板PIN MAP.xlsx](https://docs2.listenai.com/zz/9711.xlsx?shortId=cWWqDKaBN) |

## 四、芯片资料

| 类型      | 型号 | 下载链接                                                                                    |
| --------- | ---- | ------------------------------------------------------------------------------------------- |
| Datasheet | LS26 | [ls26seriesaisoc_datasheet_v1.0.pdf](https://docs2.listenai.com/zz/9601.pdf?shortId=cWWqDKaBN) |
