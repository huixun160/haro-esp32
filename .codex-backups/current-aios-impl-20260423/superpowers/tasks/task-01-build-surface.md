# Task 1 记录：AIOS Build Surface

- 状态：`已完成`
- 对应任务：`Task 1: Add AIOS Build-Time Configuration Surface`

## 本任务做了什么

- 在 `main/Kconfig.projbuild` 中新增 `AIOS` 配置菜单
- 在 `main/CMakeLists.txt` 中注册后续将要落地的 `main/aios/` 源文件和 include 目录
- 修正 plan 中 `esp-box-3` 的构建命令，显式增加 `-DIDF_TARGET=esp32s3`

## 修改文件

- `main/Kconfig.projbuild`
- `main/CMakeLists.txt`
- `docs/superpowers/plans/2026-04-22-aios-native-backend-integration.md`

## 验证结果

- 在干净的 `ESP-IDF v5.5.4` 环境下：
  - 基线 worktree 可以完整 `build` 成功
  - 当前分支在接入 AIOS build surface 后按预期失败
- 最终确认的失败点：
  - 先是 `main/aios` 目录不存在
  - 这是本任务刻意建立的“下一缺失模块锚点”

## 遇到的坑

- 初始 shell 一直残留 `ESP-IDF v6.0` 环境变量，导致 `v5.5.4` 激活脚本没有真正生效
- `idf-component-manager` 需要访问远程组件仓库，沙箱默认会拦截，必须带网络提权验证
- `esp-box-3` 构建命令如果不显式指定 `IDF_TARGET`，验证结果不稳定

## 处理方式

- 构建前显式清理 `IDF_PATH`、`IDF_PYTHON_ENV_PATH` 等环境变量后再激活 `v5.5.4`
- build 验证统一改为：
  - `idf.py -DIDF_TARGET=esp32s3 -DBOARD_NAME=esp-box-3 -DBOARD_TYPE=esp-box-3 build`

## Review 结论

- review 指出 `main/CMakeLists.txt` 会因为 `main/aios` 不存在而直接打断构建
- 该问题在 Task 1 中属于预期失败，不单独修复，交由 Task 2 开始补目录和骨架

## 下一阻塞点

- `main/aios/` 目录及第一批骨架文件不存在
