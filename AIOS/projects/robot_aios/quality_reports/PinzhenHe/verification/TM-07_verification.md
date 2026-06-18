# TM-07 Verification

## Scope

验证 AIOS 设备公网接入链路是否满足以下闭环：

1. `/device/register`
2. `/device/auth`
3. WebSocket 握手
4. `session.connected`
5. 设备端最终配置策略是否与实测环境一致

## Environment

- Date: `2026-04-16`
- API base url: `https://apiaios.nextbigseek.com/v2`
- WebSocket url source: `/device/auth` response
- Returned WebSocket url: `wss://wapiaios.nnkit.cn/v2/chat`
- `device_product_id=0`
- `tenant_user_id=0`
- `sn=test_sn_2044311667671568384`

## Verification Items

### 1. Security Layer Verification

- [x] 明文请求会触发 `403 Invalid Security Header`
- [x] 使用 `RSA + AES-ECB + PKCS7` 可通过安全层
- [x] `Authorization: Bearer <encryptedAesKey>` 已验证有效
- [x] `X-Encryption-Data` 可作为兼容补充头同时发送

### 2. Register Verification

- [x] `POST /device/register` 已成功
- [x] 返回 `access_key`
- [x] 返回 `access_secret`
- [x] 返回 `user_id`

关键结果：

- `user_id = 2633`
- `access_key = gobE****LQo`
- `access_secret = 7a58****9f5e`

### 3. Auth Verification

- [x] `POST /device/auth` 已成功
- [x] 返回 `token`
- [x] 返回 `user.id`
- [x] 返回 `profile_device.config_agentic_id`
- [x] 返回 `ws.url`

关键结果：

- `user.id = 2633`
- `uid = A587853854`
- `token = 204d****910e`
- `config_agentic_id = AGT_2031608378022694912`
- `ws.url = wss://wapiaios.nnkit.cn/v2/chat`

### 4. WebSocket Verification

- [x] 按 auth 返回值建立 WebSocket
- [x] Upgrade 返回 `101 Switching Protocols`
- [x] 收到首个 `session.connected` 事件

关键结果：

```text
HTTP/1.1 101 Switching Protocols
```

```json
{"event_type":"session.connected","timestamp":1776256259}
```

### 5. Device Strategy Verification

- [x] 设备端改为优先使用 `/device/auth` 返回的 `ws.url`
- [x] `X-Device-Id` 使用 `user.id`
- [x] `X-Bot-ID` 使用 `config_agentic_id`
- [x] 默认 API base 已切到公网环境

## Conclusion

本轮验证已确认 AIOS 公网设备接入主链路可用：

`register -> auth -> websocket -> session.connected`

因此设备端可按此链路继续推进实际语音会话和 `/device/sync` 联调。

## Residual Risks

- 公网 `/device/auth` 存在偶发超时和 DNS 抖动
- 内网环境目前不能作为稳定联调依据
- `device_product_id=0`、`tenant_user_id=0` 仅适合作为当前测试值
