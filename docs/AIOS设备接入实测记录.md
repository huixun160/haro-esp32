# AIOS设备接入实测记录

## 目的

记录当前项目接入 AIOS 的实际连接过程、接口测试结果、已确认的配置项，以及接入过程中遇到的坑，方便后续联调和问题排查。

日期：2026-04-15
最后更新：2026-04-16

## 文档依据

- [AIOS设备注册认证流程.md](./AIOS设备注册认证流程.md)
- [AIOS服务通讯加密流程.md](./AIOS服务通讯加密流程.md)
- [AIOS-websocket协议.md](./AIOS-websocket协议.md)

## 当前项目改造结果

项目已补齐 AIOS 主链路，支持：

1. 首次无 `access_key/access_secret` 时自动调用 `/device/register`
2. 注册成功后保存 `device_user_id/access_key/access_secret`
3. 使用保存的凭证调用 `/device/auth`
4. 认证成功后携带 `token` 连接 WebSocket
5. WebSocket `session.connected` 后调用 `/device/sync`

已增加的配置项包括：

- `aios-api-base-url`
- `aios-register-url`
- `aios-auth-url`
- `aios-sync-url`
- `aios-device-product-id`
- `aios-tenant-user-id`
- `aios-device-user-id`
- `aios-imei`
- `aios-public-key`

## 关键前提

这次接入里，后端提供的 RSA 公钥是关键前提。

原因：

1. `/device/register` 和 `/device/auth` 所在环境启用了加密安全校验
2. 没有这个公钥时，设备端无法正确加密 AES key
3. 请求体也无法按协议加密
4. 最终会在进入业务层前直接返回 `403 Invalid Security Header`

本次联调使用的就是后端提供的公钥，并已验证它可以打通安全层。

## 当前默认接入配置

目前默认配置已切到“自动注册模式”：

```ini
[cloud]
provider=aios
aios-api-base-url=http://192.168.0.188:20000/v2
aios-ws-url=wss://api.apsets.com/agentTestWS/v3/chat
aios-device-product-id=0
aios-tenant-user-id=0
aios-public-key=<RSA公钥Base64 DER>
```

说明：

- `aios-device-product-id` 和 `aios-tenant-user-id` 只要非空，设备就会跳过默认 `pid/sid`，优先进入 `/device/register`
- 当前先填 `0` 作为占位值，便于接口联调

## 已验证可用的公网链路

截至 2026-04-16，已实测打通的公网链路为：

- API 基址：`https://apiaios.nextbigseek.com/v2`
- 认证返回的 WebSocket 地址：`wss://wapiaios.nnkit.cn/v2/chat`

说明：

- 代码里原先默认配置的 `aios-ws-url=wss://api.apsets.com/agentTestWS/v3/chat` 并不是这次公网认证返回的最终地址
- 更稳妥的做法是优先使用 `/device/auth` 响应里的 `ws.url`

## 标准连接流程

### 1. 设备注册

接口：

```text
POST /device/register
```

请求体：

```json
{
  "device_user_id": "uint64 | 设备用户ID（可选）",
  "device_product_id": "uint64 | 关联设备产品ID（可选）",
  "tenant_user_id": "uint64 | 关联租户用户ID（可选）",
  "imei": "string | 设备IMEI（可选）",
  "sn": "string | 设备序列号（可选）"
}
```

项目当前实际测试使用：

```json
{
  "device_product_id": 0,
  "tenant_user_id": 0,
  "sn": "test_sn_2044311667671568384"
}
```

### 2. 设备认证

接口：

```text
POST /device/auth
```

请求体：

```json
{
  "access_key": "string",
  "access_secret": "string",
  "imei": "string",
  "sn": "string",
  "region": "string",
  "language": "string"
}
```

作用：

- 获取 `token`
- 获取 `user.id`
- 获取 `profile_device`
- 获取 `ws.url`

### 3. WebSocket连接

文档要求：

- 握手头必须带 `X-Device-Id`
- 当前文档版本仍要求 `X-Bot-ID`
- 鉴权头带 `Authorization: Bearer <token>`

### 4. 设备同步

接口：

```text
POST /device/sync
```

说明：

- 在 WebSocket 连接成功后主动调用一次
- 请求体为空，使用 `Authorization: Bearer <token>` 即可

## 实测结果

### 一、明文请求会被安全层拦截

最初直接请求：

```text
POST https://apiaios.nextbigseek.com/v2/device/register
POST http://192.168.0.188:20000/v2/device/register
```

请求体为普通 JSON：

```json
{"sn":"test_sn_2044311667671568384"}
```

返回：

```text
HTTP/1.1 403 Forbidden
Invalid Security Header
```

结论：

- 不是 `sn` 格式问题
- 请求还没进入业务层
- 失败原因是没有按 AIOS 加密协议组织请求
- 后端提供的 RSA 公钥是解决这个问题的关键

### 二、加密请求方式确认有效

按文档要求，实际可用的请求方式为：

1. 生成随机 16 字节 AES key
2. 用服务端 RSA 公钥加密 AES key
3. 用 AES-ECB + PKCS7 加密请求体
4. 将加密后的 AES key 放到认证头中

实测可用的头部形式：

```text
Authorization: Bearer <RSA加密后的AES密钥>
X-Encryption-Data: {"key":"<RSA加密后的AES密钥>"}
Content-Type: application/json
```

其中：

- `Authorization` 是真正打通安全层的关键
- 只传 `X-Encryption-Data`，仍可能返回 `403 Invalid Security Header`
- 前提是必须使用后端提供的有效 RSA 公钥

### 三、内网 register 服务可达，但业务层异常

测试地址：

```text
POST http://192.168.0.188:20000/v2/device/register
```

请求已通过安全层，解密后返回：

```json
{"code":-1000,"msg":"System busy, please try again","data":null}
```

按文档建议等待 30 秒后再次重试，结果相同。

结论：

- 内网 `/device/register` 路由存在
- 安全层正常
- 但业务层当前处于异常状态

### 四、公网 register 成功

测试地址：

```text
POST https://apiaios.nextbigseek.com/v2/device/register
```

请求参数：

```json
{
  "device_product_id": 0,
  "tenant_user_id": 0,
  "sn": "test_sn_2044311667671568384"
}
```

返回解密后为：

```json
{
  "code": 200,
  "msg": "Success",
  "data": {
    "device": {
      "id": 1378,
      "user_id": 2633,
      "access_key": "gobETWzFSrPG8vyLWbTn6j1BLCeplLQo",
      "access_secret": "7a5815a649be6f45d35ef6c286d49f5e",
      "device_product_id": 0,
      "tenant_user_id": 0,
      "imei": "",
      "sn": "test_sn_2044311667671568384"
    }
  }
}
```

结论：

- 公网 `/device/register` 正常可用
- 即使传 `device_product_id=0`、`tenant_user_id=0`，当前公网环境也允许注册成功
- 已拿到后续 `/device/auth` 所需的 `access_key/access_secret`

### 五、公网 auth 初期不稳定，后续恢复成功

测试地址：

```text
POST https://apiaios.nextbigseek.com/v2/device/auth
```

请求使用公网注册返回的：

- `access_key`
- `access_secret`
- `sn`

结果：

```text
read timeout
```

之后再次重试时，还出现过一次：

```text
Temporary failure in name resolution
```

在后端确认服务恢复后继续重试，公网 `/device/auth` 已成功返回。

成功响应解密后为：

```json
{
  "code": 200,
  "msg": "Success",
  "data": {
    "user": {
      "id": 2633,
      "uid": "A587853854",
      "token": "<动态token>"
    },
    "profile_device": {
      "id": 1378,
      "user_id": 2633,
      "device_key": "gobETWzFSrPG8vyLWbTn6j1BLCeplLQo",
      "device_product_id": 0,
      "tenant_user_id": 0,
      "sn": "test_sn_2044311667671568384",
      "config_agentic_id": "AGT_2031608378022694912"
    },
    "ws": {
      "url": "wss://wapiaios.nnkit.cn/v2/chat"
    }
  }
}
```

结论：

- 公网 `/device/auth` 当前已经可用
- 返回了有效 `token`
- 返回了有效 `user.id`
- 返回了有效 `config_agentic_id`
- 返回了实际可用的 `ws.url`

### 六、公网 websocket 握手成功

使用公网 `/device/auth` 返回的数据：

- `ws.url = wss://wapiaios.nnkit.cn/v2/chat`
- `X-Device-Id = 2633`
- `Authorization: Bearer <token>`
- `X-Bot-ID = AGT_2031608378022694912`

实测 WebSocket 握手返回：

```text
HTTP/1.1 101 Switching Protocols
```

连接建立后收到首帧：

```json
{"event_type":"session.connected","timestamp":1776256259}
```

结论：

- WebSocket 已确认连接成功
- 当前公网“注册 -> 认证 -> WebSocket”主链路已打通

### 七、内网 auth 返回鉴权失败

测试地址：

```text
POST http://192.168.0.188:20000/v2/device/auth
```

使用公网 `/device/register` 返回的 `access_key/access_secret` 测试，返回：

```json
{"code":-13,"msg":"Authentication failed","data":null}
```

结论：

- 内外网环境明显不是同一套数据
- 公网注册出来的凭证不能直接拿去认证内网环境

## 当前连接状态

当前状态分两部分：

### 公网环境

1. `/device/register` 成功
2. `/device/auth` 成功
3. 已拿到 `token`
4. WebSocket 握手成功
5. 已收到 `session.connected`

结论：

- 公网主链路已完整打通

### 内网环境

1. `/device/register` 返回 `System busy`
2. `/device/auth` 返回 `Authentication failed`

结论：

- 内网环境仍不可用于完整联调
- 当前可用链路以公网为准

## 已确认的重试和 token 约定

根据文档可确认：

- 注册失败后，重试需等待 `30s` 以上
- `token` 有有效期，需要定期刷新
- `token` 无效或过期时，应断开连接并重新登录

备注：

- 本地仓库文档里没有找到“10天有效期”的明确描述
- 文档示例中可见配置为 `DEVICE_AUTH_TIMEOUT=3600`
- 如果后端口头约定为 10 天，应以服务端实际配置为准

## 本次接入遇到的坑

### 1. 看到 `403 Invalid Security Header` 时，容易误判成参数问题

真实原因通常不是业务参数错误，而是：

- 没带加密头
- AES key 没按要求加密
- body 没加密
- 请求头字段与服务端实现不匹配

### 2. 文档对安全头描述存在不一致

文档一处强调：

```text
Authorization: Bearer {encryptedAesKey}
```

另一处强调：

```text
X-Encryption-Data
```

实测结论是：

- `Authorization` 是关键头
- 同时带 `X-Encryption-Data` 更稳妥

### 3. 内网和公网环境行为不一致

内网：

- register 返回 `System busy`
- auth 返回 `Authentication failed`

公网：

- register 成功
- auth 已成功
- websocket 已成功握手并收到 `session.connected`

说明环境之间差异较大，不能混用凭证。

### 4. 公网链路存在短时网络抖动

公网 `/device/auth` 在联调过程中出现过两类临时异常：

- `read timeout`
- `Temporary failure in name resolution`

但重试后接口恢复成功。

说明：

- 需要对公网认证请求做好重试
- 不能因为单次超时就立即判断接口逻辑有问题

### 5. register 成功不代表 websocket 成功

注册成功只说明：

- 设备已拿到 `access_key/access_secret`

后面仍必须继续：

1. `/device/auth`
2. 获取 `token`
3. 连接 WebSocket
4. 处理 `session.connected`

本次联调也是在拿到 `token` 并收到 `session.connected` 之后，才确认公网链路真正打通。

### 6. `device_product_id` 和 `tenant_user_id` 来源于平台，不是设备本地产生

这两个值本质上是平台侧业务 ID。

虽然当前公网环境允许用 `0/0` 注册成功，但这更像联调用例，正式环境仍建议由后端提供真实值。

## 后续建议

### 设备侧

1. 将 `aios-api-base-url` 切到公网可用地址 `https://apiaios.nextbigseek.com/v2`
2. 保持自动注册逻辑
3. 正确配置后端提供的 `aios-public-key`
4. 注册成功后持久化保存 `access_key/access_secret/device_user_id`
5. 优先使用 `/device/auth` 响应返回的 `ws.url`
6. 优先使用 `/device/auth` 响应返回的 `config_agentic_id`
7. 对公网 `/device/auth` 做重试，处理短时 DNS/超时抖动

### 后端侧

建议后端确认：

1. 内外网是否属于同一套账号数据
2. `device_product_id=0`、`tenant_user_id=0` 是否只是测试环境容忍
3. 正式环境是否必须提供真实 `device_product_id` 和 `tenant_user_id`
4. `X-Bot-ID` 是否仍为必传字段
5. 公网 `auth` 偶发 DNS/超时抖动是否有已知原因

## 一句话结论

当前项目已经把 AIOS 设备接入改造成“自动注册 -> 认证 -> WebSocket -> 同步”的完整链路；截至 2026-04-16，公网“注册 -> 认证 -> WebSocket”已实测打通，主要遗留问题是内外网环境不一致以及公网认证链路存在偶发抖动。
