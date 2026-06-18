# AIOS 公网链路反馈

日期：2026-04-16

## 本轮结论

AIOS 设备接入的公网主链路已经打通，当前可确认以下事实：

- `POST /device/register` 可成功返回 `access_key/access_secret`
- `POST /device/auth` 可成功返回 `token`、`user.id`、`config_agentic_id` 和 `ws.url`
- 使用 auth 返回值建立 WebSocket 后，已收到 `101 Switching Protocols`
- 连接建立后已收到 `session.connected`

这说明设备端接入策略应正式调整为：

- 以 `https://apiaios.nextbigseek.com/v2` 作为默认 API base
- 以 `/device/auth` 返回的 `ws.url` 作为 WebSocket 最终目标
- 以 `user.id` 作为 `X-Device-Id`
- 以 `config_agentic_id` 作为 `X-Bot-ID`

## 对接反馈

本轮联调里有几个对设备端实现影响较大的确认点：

1. `/device/register` 与 `/device/auth` 需要加密，不可直接明文请求
2. `Authorization: Bearer <encryptedAesKey>` 是通过安全层的关键头
3. `sn` 可以作为设备标识参与注册与认证
4. `device_product_id=0`、`tenant_user_id=0` 在当前公网环境下可用于测试
5. WebSocket 不建议写死历史地址，应优先用 auth 动态返回值

## 当前不足

尽管公网主链路已打通，仍有以下问题需要继续跟进：

- 内网环境返回 `System busy` 或 `Authentication failed`
- 公网 `/device/auth` 偶发超时或 DNS 抖动
- token 生命周期和正式环境参数仍需与后端进一步确认

## 建议

1. 设备端保留 auth 重试能力
2. 增强 `register/auth/websocket` 失败日志
3. 正式环境接入前补齐真实 `device_product_id` 与 `tenant_user_id`
4. 后续所有联调优先以公网结果为准，避免内外网数据混用
