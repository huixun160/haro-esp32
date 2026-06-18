# ARCS SDK 网络能力

## 公开重点

从当前官网可直接确认的网络主线里，最清晰的是 `LISA Modem` 组件。它围绕 ML307 4G/LTE 模块提供蜂窝网络能力。

## LISA Modem 组件

### 功能摘要

- AT 命令收发与响应解析
- URC 处理
- TCP 连接
- UDP 通信
- SSL/TLS 连接
- DNS 解析
- 网络状态监控
- 电源管理
- 与 NetDev / SAL 集成

### 关键配置

```conf
CONFIG_LISA_MODEM=y
CONFIG_SAL_USING_POSIX=y
CONFIG_LISA_NETWORK=y
```

### 关键接口

```c
int lisa_modem_module_init(void);
ml307_tcp_t *ml307_tcp_create(at_uart_t *uart, int id);
int ml307_tcp_connect(ml307_tcp_t *tcp, const char *host, uint16_t port);
int ml307_tcp_send(ml307_tcp_t *tcp, const char *data, size_t len);
int ml307_dns_resolve(const char *hostname, char *ip_buf, size_t buf_len);
```

### 使用约束

- 初始化必须先于建连
- 连接 ID 使用 `0-5`
- 建连前确认网络已 ready
- 接收回调应尽快返回
- 大数据包由组件内部做分包处理

## 联网项目建议

对于联网项目，推荐最低组合是：

1. `lisa_log` 打开调试日志
2. `lisa_modem` 跑通入网和 DNS
3. 再接入 HTTP / WebSocket / 自定义协议

## 资料来源

- LISA Modem：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/components/lisa_modem/README.html>
