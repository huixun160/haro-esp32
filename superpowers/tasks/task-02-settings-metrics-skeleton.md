# Task 2 记录：事件常量、凭据与指标骨架

- 状态：`已完成`
- 对应任务：`Task 2: Implement AIOS Event Constants, Credentials, and Metrics Skeleton`

## 本任务做了什么

- 创建 `main/aios/` 目录
- 新增 AIOS 事件常量头文件
- 新增运行时指标骨架 `AiosRuntimeMetrics`
- 新增事件日志骨架 `AiosEventJournal`
- 在 `Settings` 中增加 AIOS 凭据读写接口
- 在 `SystemInfo` 中增加 `GetUptimeMs()`

## 修改文件

- `main/aios/aios_event_types.h`
- `main/aios/aios_runtime_metrics.h`
- `main/aios/aios_runtime_metrics.cc`
- `main/aios/aios_event_journal.h`
- `main/aios/aios_event_journal.cc`
- `main/settings.h`
- `main/settings.cc`
- `main/system_info.h`
- `main/system_info.cc`

## 验证结果

- `git diff --check` 通过
- 构建失败点从 `main/aios` 目录不存在前移到：
  - `main/aios/aios_crypto.cc` 缺失

## 遇到的坑

- `Settings::EraseKey()` 和 `EraseAll()` 之前不会设置 `dirty_`
- 新增 `ClearAiosCredentials()` 后，如果只做删除不做写入，析构时不会 `nvs_commit()`，导致清理结果不落盘

## 处理方式

- 在 `EraseKey()` 和 `EraseAll()` 成功路径上补 `dirty_ = true`

## Review 结论

- reviewer 明确指出 `ClearAiosCredentials()` 在旧实现下不会真正持久化删除
- 问题已修复并回写到本任务代码中

## 下一阻塞点

- `main/aios/aios_crypto.cc` 缺失
