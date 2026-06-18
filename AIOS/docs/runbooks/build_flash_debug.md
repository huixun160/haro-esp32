# ARCS SDK 编译、烧录与调试

## 编译

官方示例的标准编译方式如下：

```bash
./build.sh -C -S samples/helloworld -DBOARD=arcs_evb
```

参数说明：

- `-S`：示例或工程源码路径
- `-DBOARD`：目标板型，常见为 `arcs_evb` 或 `arcs_mini`
- `-C`：清理构建目录

编译成功后，常见产物包括：

- `build/<name>.bin`：烧录文件
- `build/<name>.elf`：调试文件

## 烧录准备

### 手动进入烧录模式

- 开发板 TX 接串口板 RX
- 开发板 RX 接串口板 TX
- 开发板 GND 接串口板 GND
- 按住 `BOOT` 后复位开发板

官网说明，每次重新烧录前通常都要重新进入烧录模式。

### 自动烧录接线

如果希望工具自动拉起烧录模式，可将：

- `BOOT` 接串口板 `RTS`
- `RESET` 接串口板 `DTR`

## 基本烧录命令

```bash
./tools/burn/cskburn -s /dev/ttyUSB0 -b 3000000 0x0 build/helloworld.bin -C arcs
```

重点参数：

- `-s`：串口设备
- `-b`：波特率，官网推荐 3000000
- `0x0`：烧录偏移地址
- `-C arcs`：芯片类型

## cskburn 的补充能力

在公开文档中，`cskburn` 还支持：

- `--verify-all`：烧录后整体验证
- `--erase-all`：全擦除
- `--erase <addr:size>`：按区间擦除
- `--verify <addr:size>`：按区间校验
- `--chip-id`：读取芯片 ID
- `--emmc`：通过 SDIO 对 eMMC / TF 卡介质烧录

对于生产流程，建议优先把 `--verify-all` 作为默认动作。

## 串口验证

以 `helloworld` 为例，烧录完成后复位开发板，应在串口看到类似输出：

```text
Running on hart-id: 1
Hello, world!
```

## GDB 调试

### 依赖

- Nuclei RISC-V GDB
- SEGGER J-Link，官网推荐 V7.98 及以上
- ARCS J-Link 设备配置文件

### 安装 J-Link 设备配置

```bash
curl -L -o /tmp/JLinkDevices.zip \
  http://listenai-firmware-delivery.oss-cn-beijing.aliyuncs.com/ARCS/tools/JLinkDevices.zip && \
  unzip -o /tmp/JLinkDevices.zip -d $HOME/.config/SEGGER
```

### 启动 GDB Server

```bash
JLinkGDBServerCLExe -device ARCS -if cJTAG -speed 4000 -port 2331 \
  -jlinkscriptfile $HOME/.config/SEGGER/JLinkDevices/scripts/arcs/jtagscan1.JLinkScript
```

官网说明：

- `jtagscan0.JLinkScript`：连接 core0（AP 核）
- `jtagscan1.JLinkScript`：连接 core1（CP 核）
- 官方示例默认通常运行在 core1

### 常见调试入口

- 使用 `.elf` 做符号加载
- 通过 GDB 下断点、单步、看变量
- 结合 UART 日志定位启动与运行阶段问题

## 相关资源打包

如果项目需要本地文件系统资源，可使用 `mkfatfs.py` 打包 FAT 镜像：

```bash
./mkfatfs.py -o disk.img -s 32M -d resources -l SD -v
```

该工具依赖 `mtools`。

## 资料来源

- 快速入门：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/get_started.html>
- GDB 调试指南：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/gdb.html>
- cskburn：<https://docs2.listenai.com/arcs-sdk/v0.1.3/zh/html/tools/burn/README.html>
- FAT32 镜像工具：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/tools/fatfs_package/README.html>
