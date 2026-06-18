# ARCS SDK 日志能力

## 组件定位

`lisa_log` 是 ARCS SDK 当前公开得最完整的基础组件之一，用来统一日志输出、级别过滤和异步打印。

## 主要特性

- 基于 EasyLogger
- UART 串口输出
- 支持异步模式
- 支持 `ERROR/WARN/INFO/DEBUG/VERBOSE`
- 支持带 `LOG_TAG` 的模块化日志
- 支持十六进制转储

## 最小配置

```conf
CONFIG_LOG=y
CONFIG_LOG_LEVEL_INFO=y
```

如需统一管理 `printf/printk`，可再打开：

```conf
CONFIG_SYSLOG_PRINTF_REDIRECT=y
CONFIG_SYSLOG_PRINTK_REDIRECT=y
```

## 最小使用

```c
#define LOG_TAG "MyApp"
#include "lisa_log.h"

void app_main(void) {
    LOGI("Application started");
}
```

## 使用约束

- `LOG_TAG` 必须写在 `#include "lisa_log.h"` 前面
- 异步模式下，休眠前或关键节点建议调用 `log_flush()`
- 如果串口乱码，优先检查 `CONFIG_SYSLOG_UART_BAUDRATE`

## 资料来源

- Logger：<https://docs2.listenai.com/arcs-sdk/v0.1.1/zh/html/components/lisa_log/README.html>
