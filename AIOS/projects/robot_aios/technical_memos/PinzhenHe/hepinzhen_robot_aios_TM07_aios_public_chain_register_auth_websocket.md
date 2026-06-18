# Technical Memo

**Title:** AIOS 公网设备注册、认证与 WebSocket 主链路打通记录

**Project:** robot_aios

**Subsystem:** AIOS / Device Register / Device Auth / WebSocket / Voice Runtime

**Author:** PinzhenHe

**Priority:** HIGH

**Date:** 2026-04-16

---

## Background

本阶段目标是将机器人设备从原有云链路切换到 AIOS 设备接入链路，并完成一条可真实联通的公网主路径：

`/device/register -> /device/auth -> websocket -> session.connected -> /device/sync`

前期联调中主要存在以下问题：

- 旧默认配置仍残留非当前可用的 WebSocket 地址
- `/device/register` 和 `/device/auth` 启用了加密安全层，明文请求会被直接拦截
- 内网与公网环境返回行为不一致，容易误判为设备端代码问题
- 认证成功后真正可用的 `ws.url` 来自 `/device/auth` 响应，而不是固定写死的本地默认值

## Objective

本次工作聚焦以下目标：

1. 明确 AIOS 公网可用 API base url 与 WebSocket 接入方式
2. 按文档落地设备端加密注册与认证逻辑
3. 实测打通公网 `register -> auth -> websocket`
4. 固化最终配置策略、关键请求头、字段来源和失败重试约定
5. 形成可复用的设备接入报告，供后续 TM01 和联调阶段直接引用

## Final Public Configuration

当前确认可用的公网环境如下：

- API base url: `https://apiaios.nextbigseek.com/v2`
- WebSocket url: 优先使用 `/device/auth` 返回的 `ws.url`
- 本次实测返回的 `ws.url`: `wss://wapiaios.nnkit.cn/v2/chat`
- `device_product_id`: `0`
- `tenant_user_id`: `0`
- `sn`: `test_sn_2044311667671568384`
- `X-Device-Id`: 使用 `/device/auth` 返回的 `user.id`
- `X-Bot-ID`: 使用 `/device/auth` 返回的 `profile_device.config_agentic_id`

设备侧当前采用的配置原则：

- 默认 `provider=aios`
- 默认 API 基址为 `https://apiaios.nextbigseek.com/v2`
- 默认不再强绑固定 `aios-ws-url`
- WebSocket 连接优先吃 `/device/auth` 返回值
- `device_product_id` 和 `tenant_user_id` 在当前测试环境下可先使用 `0`

## Security Protocol

`/device/register` 和 `/device/auth` 均启用了安全校验，必须按文档进行加密封装。

当前已验证可用的加密方式：

1. 生成随机 16 字节 AES key
2. 使用后端提供的 RSA 公钥加密该 AES key
3. 使用 `AES-ECB + PKCS7` 加密 JSON body
4. 同时携带以下头部

```text
Authorization: Bearer <RSA加密后的AES密钥>
X-Encryption-Data: {"key":"<RSA加密后的AES密钥>"}
Content-Type: application/json
```

实测结论：

- `Authorization` 是关键头
- 仅带 `X-Encryption-Data` 不够稳妥
- 明文请求会直接得到 `403 Invalid Security Header`

## End-to-End Flow

### 1. Device Register

请求地址：

```text
POST https://apiaios.nextbigseek.com/v2/device/register
```

实测请求体：

```json
{
  "device_product_id": 0,
  "tenant_user_id": 0,
  "sn": "test_sn_2044311667671568384"
}
```

解密后的成功响应摘要：

```json
{
  "code": 200,
  "msg": "Success",
  "data": {
    "device": {
      "id": 1378,
      "user_id": 2633,
      "access_key": "gobE****LQo",
      "access_secret": "7a58****9f5e"
    }
  }
}
```

结果：

- 注册成功
- 返回了可持久化的 `access_key/access_secret`
- 返回了后续 WebSocket 需要使用的设备用户标识 `user_id=2633`

### 2. Device Auth

请求地址：

```text
POST https://apiaios.nextbigseek.com/v2/device/auth
```

请求体字段来源：

- `access_key`: 来自 `/device/register`
- `access_secret`: 来自 `/device/register`
- `sn`: 设备序列号
- `region`: 设备区域配置
- `language`: 设备语言配置

解密后的成功响应摘要：

```json
{
  "code": 200,
  "msg": "Success",
  "data": {
    "user": {
      "id": 2633,
      "uid": "A587853854",
      "token": "204d****910e"
    },
    "profile_device": {
      "config_agentic_id": "AGT_2031608378022694912"
    },
    "ws": {
      "url": "wss://wapiaios.nnkit.cn/v2/chat"
    }
  }
}
```

结果：

- 认证成功
- 返回了 WebSocket 鉴权所需 `token`
- 返回了 `X-Device-Id` 使用值 `user.id=2633`
- 返回了 `X-Bot-ID` 使用值 `config_agentic_id=AGT_2031608378022694912`
- 返回了最终 WebSocket 地址

### 3. WebSocket Handshake

连接目标：

```text
wss://wapiaios.nnkit.cn/v2/chat
```

关键握手头：

```text
Authorization: Bearer <token>
X-Device-Id: 2633
X-Bot-ID: AGT_2031608378022694912
```

实测返回：

```text
HTTP/1.1 101 Switching Protocols
```

连接成功后收到首帧：

```json
{"event_type":"session.connected","timestamp":1776256259}
```

结论：

- WebSocket 主链路已建立
- 设备端可以将 `session.connected` 作为后续同步和会话启动前提

### 4. Device Sync

触发条件：

- WebSocket 建立成功
- 已收到 `session.connected`

请求地址：

```text
POST https://apiaios.nextbigseek.com/v2/device/sync
```

使用方式：

- 空 JSON body
- `Authorization: Bearer <token>`
- 仍建议沿用同一套加密封装

## Device-Side Implementation Decisions

本次改造后，设备端实现采用以下策略：

1. 若本地不存在 `access_key/access_secret`，先自动调用 `/device/register`
2. 注册成功后持久化保存 `access_key/access_secret/device_user_id`
3. 每次联网后调用 `/device/auth` 刷新 token
4. 优先使用 `/device/auth` 返回的 `ws.url`
5. WebSocket 握手时优先使用 `/device/auth` 返回的 `user.id` 作为 `X-Device-Id`
6. WebSocket 握手时优先使用 `/device/auth` 返回的 `config_agentic_id` 作为 `X-Bot-ID`
7. 收到 `session.connected` 后再进入同步与会话阶段

## Validation Result

截至 2026-04-16，本次 AIOS 公网主链路验证结果如下：

- `/device/register`: 成功
- `/device/auth`: 成功
- WebSocket upgrade: 成功
- WebSocket 首帧 `session.connected`: 成功收到

因此可以确认：

`AIOS 公网 register -> auth -> websocket` 主链路已实测打通。

## Risks And Follow-Ups

当前仍需关注以下风险：

- 公网 `/device/auth` 在联调期间出现过短时 `read timeout` 与 DNS 抖动
- 内网与公网环境行为不一致，不能混用凭证
- `device_product_id=0`、`tenant_user_id=0` 更像测试环境容忍值，正式环境应由后端提供真实值
- token 过期后仍需重新执行 `/device/auth`

后续建议：

1. 继续观察公网 auth 抖动，补充设备端重试与日志
2. 将 `/device/auth` 返回值作为 WebSocket 唯一可信来源
3. 联调时优先看 `register/auth/raw response` 与最终 `ws.url`
4. 在正式环境接入前确认真实 `device_product_id` 和 `tenant_user_id`

## References

- `AIOS/docs/knowledgebase/AIOS设备注册认证流程.md`
- `AIOS/docs/knowledgebase/AIOS服务通讯加密流程.md`
- `AIOS/docs/knowledgebase/AIOS-websocket协议.md`
- `AIOS/docs/knowledgebase/AIOS设备接入实测记录.md`
