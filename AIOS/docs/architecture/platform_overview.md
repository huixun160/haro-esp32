# 聆思 ARCS SDK 平台概览

## 平台定位

ARCS SDK 是聆思面向 ARCS 平台提供的软件开发包，文档主线围绕以下几件事展开：

- Linux 主机上的开发环境搭建
- `arcs_evb`、`arcs_mini` 两类开发板适配
- 基于 `build.sh` 的工程构建
- 基于 `cskburn` 的串口烧录
- 基于 UART 日志和 GDB/J-Link 的调试
- 基于组件与示例的应用扩展

官方快速入门明确说明，目前仅支持 Linux，推荐 Ubuntu 18.04 及以上版本。

## 分层理解

结合官网“快速入门”“组件”“文件系统”“蓝牙音频框架”“LISA Modem”等页面，可以把公开能力归纳为 4 层：

### 1. 板级与驱动层

- 开发板：`arcs_evb`、`arcs_mini`
- 常见硬件接口：UART、I2C、SPI、GPIO、PWM、SDIO、DVP、ADC
- 典型外设：LCD、摄像头、TF/SD 卡、按键、LED、麦克风、扬声器

### 2. 系统与工具层

- 工具链环境：`env.sh`
- 构建脚本：`build.sh`
- 烧录工具：`tools/burn/cskburn`
- 调试工具：Nuclei GDB、SEGGER J-Link
- 资源工具：`tools/fatfs_package/mkfatfs.py`

### 3. 基础组件层

- 日志：`lisa_log`
- 文件系统：LVFS / LSFS / SubFS / Disk 分层
- 网络：LISA Modem、WebSocket、HTTP、SNTP、WiFi、Net
- 音频：播放器、本地音频资源、蓝牙音频框架
- 图形：LVGL

### 4. 应用与示例层

- `samples/modules`：文件系统、Logger、LVGL、播放器、mbedTLS、Shell 等
- `samples/network`：网络、蓝牙音频等
- `samples/algorithms`：单麦/双麦唤醒算法

## 板型对比

### `arcs_evb`

适合完整原型验证，接口更丰富，公开文档提到：

- 双 Type-C，其中一个承担供电/充电，一个承担日志与烧录
- 30 个 IO 扩展
- TF 卡槽
- LCD 连接器
- 摄像头 SPI 接口
- 麦克风、扬声器、ADC 按键、BOOT / RESET

### `arcs_mini`

适合快速原型和教学演示，体积更紧凑，公开文档提到：

- Type-C 供电/充电/烧录
- 6 个可编程 GPIO 扩展
- DVP 摄像头接口
- SPI LCD 接口
- 麦克风、扬声器、电池接口、LED、RESET

## 开发主路径

1. `source env.sh`
2. `./build.sh -C -S <sample-path> -DBOARD=<board>`
3. `./tools/burn/cskburn -s <serial> -b 3000000 0x0 build/<image>.bin -C arcs`
4. 串口查看启动日志
5. 必要时接入 J-Link + GDB 做断点调试

## 资料来源

- 快速入门：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/get_started.html>
- GDB 调试：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/gdb.html>
- ARCS EVB：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/boards/arcs_evb/README.html>
- ARCS Mini：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/boards/arcs_mini/README.html>
