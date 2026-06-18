# Task 3 记录：AIOS Crypto 与 HTTP Bootstrap

- 状态：`已完成`
- 对应任务：`Task 3: Implement AIOS Crypto and HTTP Bootstrap`

## 本任务做了什么

- 新增 `AiosCrypto` 骨架
- 新增 `AiosHttpClient` 骨架
- 在 `Application::ActivationTask()` 中接入最小 AIOS HTTP bootstrap
- 让 AIOS bootstrap 在未配置时跳过，在已配置但初始化失败时走统一错误路径

## 修改文件

- `main/aios/aios_crypto.h`
- `main/aios/aios_crypto.cc`
- `main/aios/aios_http_client.h`
- `main/aios/aios_http_client.cc`
- `main/application.cc`
- `main/application.h`

## 验证结果

- `git diff --check` 通过
- 在 `ESP-IDF v5.5.4` 环境下重新 build 后，失败点从 `aios_crypto.cc` 前移到：
  - `main/aios/aios_ws_client.cc` 缺失

## 遇到的坑

- `aios_crypto.h` 最初不自包含，直接使用 `uint8_t` 却没有包含 `<cstdint>`
- `AiosHttpClient::SetupHttp()` 里没有检查 `GetNetwork()` 和 `CreateHttp()` 返回值，存在空指针风险
- `ActivationTask()` 最初把 `AiosHttpClient` 当栈上局部变量使用，生命周期不适合后续 Task 4/5 继续复用
- 最初版本会把空公钥当作初始化成功，等价于静默降级成明文透传
- `ws_url` 一度被错误地回填为 API Base URL，语义不对

## 处理方式

- 补 `<cstdint>`
- 为 `SetupHttp()` 增加 network/http 空指针保护
- 把 `AiosHttpClient` 提升为 `Application` 成员
- 改成：
  - 未配置 AIOS 时跳过 bootstrap
  - 已配置但公钥为空时初始化失败并上报错误
- 去掉把 `ws_url` 默认写成 `CONFIG_AIOS_API_BASE_URL` 的错误逻辑

## Review 结论

- reviewer 共指出 4 个问题
- 其中 3 个是明确 bug，已全部修复
- 另 1 个是空公钥策略问题，已改成“显式配置错误，而不是静默明文降级”

## 下一阻塞点

- `main/aios/aios_ws_client.cc` 缺失
