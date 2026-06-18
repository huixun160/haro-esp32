# 聆思 ARCS SDK 文档整理

本目录已按聆思 `ARCS SDK` 官方文档重新整理，只保留与 ListenAI 平台直接相关的内容。

## 文档结构

- `architecture/`：平台概览、板型能力、模块地图
- `runbooks/`：环境搭建、编译、烧录、调试操作手册
- `api/modules/`：按能力域整理的 ARCS SDK 模块说明
- `api/api_reference_overview.md`：基于 doxygen 的 SDK API 索引总览
- `knowledgebase/`：官网入口与重点资料索引

## 快速入口

- [平台概览](./architecture/platform_overview.md)
- [能力地图](./architecture/capability_map.md)
- [环境搭建](./runbooks/environment_setup.md)
- [编译、烧录与调试](./runbooks/build_flash_debug.md)
- [知识库索引](./knowledgebase/knowledgebase_index.md)
- [API 参考总览](./api/api_reference_overview.md)

## 结论

当前公开文档显示，ARCS SDK 的开发主线是：

1. 在 Linux 主机上完成环境初始化
2. 选择 `arcs_evb` 或 `arcs_mini` 作为目标板型
3. 通过 `build.sh` 编译 `samples/` 或自定义工程
4. 使用 `tools/burn/cskburn` 完成串口烧录
5. 使用 UART 日志与 GDB/J-Link 做联调
6. 基于组件层逐步接入日志、文件系统、播放器、Modem、蓝牙音频等能力

## 主要来源

- 官方快速入门：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/get_started.html>
- GDB 调试指南：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/gdb.html>
- 板型支持：`arcs_evb` / `arcs_mini`
- 组件与示例：文件系统、Logger、LISA Modem、蓝牙音频框架、FatFS 打包工具
