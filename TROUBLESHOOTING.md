# 开发踩坑记录 (Troubleshooting Log)

以下记录了我们在调试和开发过程中遇到的几个主要“坑”及解决方法，避免后续重复踩坑。

> [!WARNING]
> **1. GPIO 管脚冲突问题 (GPIO Conflict)**
> **问题描述**：在适配 Otto 机器人的脚部舵机时，没有考虑到管脚的复用冲突，导致给舵机配置了与屏幕（如背光控制或复位）相同的 GPIO。这不仅使得舵机工作异常，还导致了屏幕背光能亮但正面无法显示画面，甚至在初始化阶段引发了开发板系统崩溃。
> **解决方案**：仔细比对开发板原理图，在 `main/boards/otto-robot/config.h` 等配置中排查冲突的引脚，将冲突的引脚置为 `GPIO_NUM_NC`（未连接）或重新分配为完全独立且未被占用的管脚。

> [!IMPORTANT]
> **2. AIOS WebSocket 认证失败 (WebSocket Authentication Failure)**
> **问题描述**：屏幕成功点亮后，设备连上了 WiFi，却一直在报错并无法连接到服务器。经过抓取日志发现是由于 `sdkconfig.defaults` 中丢失了 `CONFIG_AIOS_PUBLIC_KEY_BASE64` 这一关键配置，导致代码中的宏 `AIOS_PUBLIC_KEY_CONFIG` 为空。后端因接收不到正确的公钥认证信息，导致建连被拒绝。
> **解决方案**：在项目的 `sdkconfig.defaults` 基础配置中，重新加入并写死对应的公钥值，保证在执行 `idf.py build` 之前能正确读取，恢复了 WebSocket 的鉴权通信。

> [!CAUTION]
> **3. WSL 烧录操作时机不对 (Flashing Flow Interruption)**
> **问题描述**：在使用 WSL2 开发时，当固件编译或设备端口（`/dev/ttyACM0`）未能被正确通过 `usbipd` 挂载就盲目发起 `idf.py flash` 烧录，或者随意中断正常的构建烧录过程，给正常的操作流程带来了极大的干扰。
> **解决方案**：规范操作流，在确认固件构建 100% 完成并且端口挂载稳定的前提下，再稳妥地发起烧录指令。

> [!WARNING]
> **4. Kconfig 默认配置导致的配置覆盖 (Kconfig Default Override)**
> **问题描述**：在尝试将“分贝唤醒”改回“小冰小冰”模型时，仅仅在 `sdkconfig.defaults` 中删除了 `CONFIG_USE_VOLUME_WAKE_WORD=y` 并不能生效。因为底层 `Kconfig.projbuild` 里对 `USE_VOLUME_WAKE_WORD` 设定了 `default y`，所以在重新生成配置文件时它又自动变回了开启状态，覆盖了机器学习唤醒词。
> **解决方案**：针对底层写死了 `default y` 的选项，必须在 `sdkconfig.defaults` 中显式地声明并设定为 `n`（如：`CONFIG_USE_VOLUME_WAKE_WORD=n`），这样才能强制推翻底层的默认逻辑。

---

## 小冰小冰唤醒模型数据 (Wake Word Model Info)

为了替换掉体验不佳的分贝唤醒，我们已经将配置文件改回使用原本的“小冰小冰”模型。以下是该模型的相关开销数据：

- **模型名称**: `wn9_xiaobinxiaobin_tts` (基于乐鑫 WakeNet 9 架构)
- **存储空间占用 (Flash)**: 约 **284 KB** (精确大小为 290,895 bytes)
- **内存占用 (RAM)**:
  - **PSRAM (外部 RAM)**: 约消耗 **1.2 MB ~ 1.5 MB**（用于模型加载与大块缓冲区）
  - **SRAM (内部 RAM)**: 约消耗 **20 KB ~ 50 KB**（用于高频的数据运算上下文）
