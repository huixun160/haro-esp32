# AIOS Register/Auth/WebSocket 踩坑记录

日期：2026-04-16

## 1. `403 Invalid Security Header` 不是普通参数错误

最容易误判的点是把 `403 Invalid Security Header` 当成业务字段填错。

这类问题通常意味着：

- 请求体没有按协议加密
- AES key 没有用 RSA 公钥正确加密
- 关键安全头没带上
- 请求头名字与服务端实现不一致

排查顺序建议优先看：

1. 是否启用了 `RSA + AES-ECB + PKCS7`
2. 是否带了 `Authorization: Bearer <encryptedAesKey>`
3. 是否同时补了 `X-Encryption-Data`

## 2. 文档里的安全头描述并不完全一致

有的描述强调 `Authorization`，有的描述强调 `X-Encryption-Data`。

实测下来更稳的方式是两者同时发送，但真正能穿过安全层的关键是：

```text
Authorization: Bearer <RSA加密后的AES密钥>
```

## 3. 不要再把 WebSocket 地址写死成历史默认值

早期默认值或旧文档中的固定 WebSocket 地址，不一定是当前环境真正可用的目标。

这次联调中真正有效的做法是：

- 先调 `/device/auth`
- 再使用响应里的 `ws.url`

如果继续写死历史地址，很容易出现“register/auth 成功但 websocket 不通”的假象。

## 4. `register` 成功不代表主链路成功

`/device/register` 成功只说明已经拿到 `access_key/access_secret`。

要确认主链路真的打通，还必须继续看到：

- `/device/auth` 成功
- WebSocket 返回 `101 Switching Protocols`
- 收到 `session.connected`

少任意一步，都不能算真正完成设备接入。

## 5. 内外网环境不能混用凭证

本轮联调里已经明确看到：

- 内网 `register` 返回 `System busy`
- 内网 `auth` 返回 `Authentication failed`
- 公网 `register/auth/websocket` 则可完整打通

这说明内外网环境不是同一套稳定数据面，公网注册得到的凭证不能直接拿去认证内网。

## 6. `device_product_id=0` 和 `tenant_user_id=0` 只是联调占位值

当前公网环境允许用 `0/0` 跑通，不代表正式环境也会长期接受。

因此在报告、代码和联调口径里都应明确：

- 当前值仅用于测试
- 正式环境仍建议以后端下发真实业务 ID 为准

## 7. 公网认证链路要考虑瞬时抖动

本轮联调里出现过：

- `read timeout`
- `Temporary failure in name resolution`

后续重试后恢复成功，因此不能因为单次失败就认定接口逻辑错误。设备端应保留重试与诊断日志。

## 8. 构建缓存也会制造“像代码问题”的假象

工程构建阶段曾出现：

- `CMakeCache.txt directory ... is different ...`
- source path 仍指向旧的 `/home/wzq/...`

这不是 AIOS 协议问题，而是旧缓存污染。处理方式是重新 clean configure：

```bash
./build.sh -C -S ./apps/arcs-evb
```

## 一句话经验

AIOS 设备链路联调时，最容易把“安全层问题、环境问题、历史默认地址问题”误看成“设备端业务代码问题”；真正高效的排查顺序应该是先看加密头，再看 auth 返回的 `ws.url`，最后才看 websocket 业务收发。
