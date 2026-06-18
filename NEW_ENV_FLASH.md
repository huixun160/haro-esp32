# 新环境编译与烧录指南

本文档整理了在一个全新环境中，将 `arcs-voiceassistant-evk` 项目编译并烧录到开发板的实际可复用流程。

适用场景：

- 新机器首次搭建环境
- 工具链和 ListenAI 工具尚未准备好
- 需要重新编译 `apps/arcs-evb`
- 通过串口进入 boot 模式后烧录开发板

本文档基于当前仓库的实际成功流程整理，默认目标应用为 `apps/arcs-evb`。

## 1. 前提条件

开始前请确认：

- 仓库已经拉取到本地
- 当前目录为仓库根目录
- 开发板可以通过 USB 连接到主机
- 如果走串口烧录，开发板已经进入 boot 模式
- 串口设备可见，例如 `/dev/ttyACM0`

进入仓库根目录：

```bash
cd /path/to/arcs-voiceassistant-evk
```

## 2. 新环境准备工具

如果当前环境没有 `listenai-tools` 和 Nuclei GCC 工具链，先执行：

```bash
./arcs-sdk/prepare_listenai_tools.sh
./arcs-sdk/prepare_toolchain.sh
```

这两步会在仓库根目录生成：

- `listenai-dev-tools/listenai-tools`
- `listenai-dev-tools/gcc`

说明：

- `listenai-tools` 内包含 `cmake`、`ninja`、`adb`、`cskburn` 等工具
- `gcc` 内包含 `riscv64-unknown-elf-gcc`

## 3. 编译应用

编译 `apps/arcs-evb`：

```bash
./build.sh -S ./apps/arcs-evb -C
```

说明：

- `-S ./apps/arcs-evb` 指定应用目录
- `-C` 表示清理后重新编译

编译成功后，主要产物位于：

- `build/arcs-evb.bin`
- `build/arcs-evb`
- `build/arcs-evb.hex`
- `build/arcs-evb.lst`

可用以下命令检查：

```bash
ls -lh build/arcs-evb build/arcs-evb.bin build/arcs-evb.hex build/arcs-evb.lst
```

## 4. 选择烧录方式

当前仓库文档里有两条路线：

### 方式一：ADB recovery 烧录

适用于：

- 开发板当前系统还能正常启动
- 设备能被 `adb devices` 识别

仓库文档推荐对已有 boot 的板子优先走这条路线。

### 方式二：串口 cskburn 烧录

适用于：

- 开发板已经进入 boot 模式
- 或开发板当前不能通过 ADB 连接
- 或需要直接从串口写入分区

本次实际成功烧录使用的是这一条。

## 5. 本次实际使用的分区方案

本次使用的是“资源分散方式”，不是 ROMFS 方式。

对应分区如下，来源见 `res/arcs-evb/res-info.md`：

- `0x40000` -> `./res/arcs-evb/ap.bin`
- `0x100000` -> `./res/arcs-evb/tone.bin`
- `0x200000` -> `./res/arcs-evb/algo/algo.bin`
- `0x4d0000` -> `./res/arcs-evb/algo/wrap.json`
- `0x800000` -> `./build/arcs-evb.bin`

说明：

- `boot.bin` 不在这次命令里烧录
- 这套流程默认 boot 已经可用，只烧应用与资源分区

## 6. 串口烧录步骤

先确认串口设备存在：

```bash
ls /dev/ttyACM0
```

然后执行烧录：

```bash
../cskburn_linux_amd64 -C arcs -s /dev/ttyACM0 -b 3000000 --verify-all \
  0x40000 ./res/arcs-evb/ap.bin \
  0x100000 ./res/arcs-evb/tone.bin \
  0x200000 ./res/arcs-evb/algo/algo.bin \
  0x4d0000 ./res/arcs-evb/algo/wrap.json \
  0x800000 ./build/arcs-evb.bin
```

如果使用仓库内下载的 cskburn，也可以尝试：

```bash
./listenai-dev-tools/listenai-tools/cskburn/cskburn -C arcs -s /dev/ttyACM0 -b 3000000 --verify-all \
  0x40000 ./res/arcs-evb/ap.bin \
  0x100000 ./res/arcs-evb/tone.bin \
  0x200000 ./res/arcs-evb/algo/algo.bin \
  0x4d0000 ./res/arcs-evb/algo/wrap.json \
  0x800000 ./build/arcs-evb.bin
```

本次实际成功使用的是仓库上一级目录中的：

```bash
../cskburn_linux_amd64
```

## 7. 烧录成功时的典型输出

成功时通常会看到类似输出：

- `Entering update mode...`
- `Detected flash size: 16 MB`
- `Erasing region ...`
- `Burning partition 1/5...`
- `Burning partition 2/5...`
- `Burning partition 3/5...`
- `Burning partition 4/5...`
- `Burning partition 5/5...`
- 每个分区后输出对应 `md5`
- 最后出现：

```text
Resetting...
Finished
```

其中 `Finished` 可作为本次烧录成功的最终标志。

## 8. ADB recovery 方式参考

如果开发板系统还能正常启动，并且 `adb devices` 能识别到设备，可以按文档走 ADB：

```bash
./listenai-dev-tools/listenai-tools/adb/adb devices
./listenai-dev-tools/listenai-tools/adb/adb shell recovery
./listenai-dev-tools/listenai-tools/adb/adb push res/arcs-evb/ap.bin /RAW/NAND/40000
./listenai-dev-tools/listenai-tools/adb/adb push res/arcs-evb/tone.bin /RAW/NAND/100000
./listenai-dev-tools/listenai-tools/adb/adb push res/arcs-evb/algo/algo.bin /RAW/NAND/200000
./listenai-dev-tools/listenai-tools/adb/adb push res/arcs-evb/algo/wrap.json /RAW/NAND/4d0000
./listenai-dev-tools/listenai-tools/adb/adb push build/arcs-evb.bin /RAW/NAND/800000
./listenai-dev-tools/listenai-tools/adb/adb reboot
```

如果 `adb devices` 为空，就不要继续走 ADB 路线，应切回串口 boot 模式烧录。

## 9. 本次流程中的注意事项

### 9.1 ROMFS 没有自动生成

本次编译期间出现过提示：

```text
genromfs not found in PATH, romfs.image will not be generated automatically
```

这意味着：

- 本次没有自动生成 `romfs.image` 或 `romfs.bin`
- 因此应使用“资源分散方式”烧录
- 不要误用 ROMFS 分区表

### 9.2 编译阶段的链接告警

本次链接阶段出现过类似告警：

```text
warning: _unlink is not implemented and will always fail
```

在本次流程里，该告警没有阻止 `build/arcs-evb.bin` 生成，也没有影响后续烧录成功。

### 9.3 boot 模式与 ADB 模式不要混用

经验上建议：

- 板子正常启动且 ADB 可见：优先 ADB recovery
- 板子已进入 boot 模式：直接使用 `cskburn`

不要在设备没有被 ADB 识别时反复执行 `adb shell recovery`，这样只会浪费时间。

## 10. 一条可交给 Codex 的指令

如果你要在新环境里直接让 Codex 复现整套流程，可以给它这段指令：

```text
请在当前仓库里完成以下工作：
1. 编译 apps/arcs-evb，使用 clean build
2. 如果缺少 listenai-tools 或 Nuclei GCC 工具链，就自动下载并配置
3. 编译成功后确认生成 build/arcs-evb.bin
4. 使用串口 /dev/ttyACM0，按 res/arcs-evb/res-info.md 的“资源分散方式”烧录到开发板
5. 使用 cskburn 并开启 --verify-all
6. 烧录地址如下：
   0x40000 -> ./res/arcs-evb/ap.bin
   0x100000 -> ./res/arcs-evb/tone.bin
   0x200000 -> ./res/arcs-evb/algo/algo.bin
   0x4d0000 -> ./res/arcs-evb/algo/wrap.json
   0x800000 -> ./build/arcs-evb.bin
7. 烧录前默认开发板已经进入 boot 模式
8. 最后把编译结果、烧录结果和任何告警总结给我
```

## 11. 参考文件

建议同时参考以下文件：

- `README.MD`
- `apps/arcs-evb/README.MD`
- `res/arcs-evb/res-info.md`
- `arcs-sdk/tools/burn/README.md`

## 12. 最短复用流程

如果你只需要一套最短命令，直接执行：

```bash
./arcs-sdk/prepare_listenai_tools.sh
./arcs-sdk/prepare_toolchain.sh
./build.sh -S ./apps/arcs-evb -C
../cskburn_linux_amd64 -C arcs -s /dev/ttyACM0 -b 3000000 --verify-all \
  0x40000 ./res/arcs-evb/ap.bin \
  0x100000 ./res/arcs-evb/tone.bin \
  0x200000 ./res/arcs-evb/algo/algo.bin \
  0x4d0000 ./res/arcs-evb/algo/wrap.json \
  0x800000 ./build/arcs-evb.bin
```
