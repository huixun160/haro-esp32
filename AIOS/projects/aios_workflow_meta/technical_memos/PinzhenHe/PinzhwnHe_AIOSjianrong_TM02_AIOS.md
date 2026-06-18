Title: AIOS 与 Codex / Cursor 兼容性分析与适配方案

Project: AIOS Feature Phone Platform

Subsystem: Adapter / System Integration / Build / Security

Author: [Engineer name]

Priority: HIGH

Date: 2026-04-13

Background

当前 AIOS（功能机平台）正在引入 AI 编程工具（如 Codex、Cursor）以提升开发效率、自动化代码生成能力和工程质量。

然而，这些工具主要面向 标准开发环境（Linux / macOS / 通用软件工程），而 AIOS 具有以下特点：

定制化工具链（Arm CC / 特定 Build 系统）
非标准工程结构（DAP / APP 分层）
功能机资源受限（内存 / 存储 / CPU）
编译与烧录流程特殊（ResearchDownload / bin 文件流程）

因此，直接使用 AI 编程工具存在兼容性问题，需要系统性分析并制定适配方案。

Objective
明确 AIOS 与 Codex、Cursor 在以下维度的兼容性：
工程结构理解能力
构建系统适配能力
工具链调用能力
调试与日志支持能力
识别至少 5 个关键不兼容点，并给出可落地的解决方案
设计一套 AIOS Adapter 层，使 AI 工具可以：
正确理解项目结构
自动生成符合规范的代码
支持编译 / 烧录 / 日志分析流程
Current State

当前 AIOS 工程现状：

代码结构
dap/：底层驱动与平台能力
app/：应用层逻辑
build/：编译系统
out/：输出 bin 文件
编译流程
使用 Arm CC 工具链
非标准 make/cmake
依赖批处理脚本生成 out.bin
烧录流程
使用 ResearchDownload
手动操作（拆电池 + 按键进入模式）
问题表现
AI 工具无法理解工程入口
无法正确生成可编译代码
无法调用 build / flash 流程
日志分析无法自动化
Scope

本任务包括：

AIOS 与 AI 编程工具的兼容性分析
工程结构标准化描述（供 AI 理解）
Adapter 层设计（核心）
编译 / 烧录 / 日志流程的 AI 接入方案
安全与权限控制策略（避免误操作设备）
Out of Scope
不涉及模型训练或微调
不修改底层芯片驱动逻辑
不重构整个 AIOS Build 系统
不实现完整 IDE（仅做适配层）
Constraints
资源限制
功能机内存、存储有限
不允许引入重量级运行时
工具链限制
必须兼容 Arm CC
不能破坏现有 build 脚本
安全限制
烧录操作必须受控（避免误刷机）
AI 生成代码必须经过校验
环境限制
Windows 为主开发环境
非标准 shell / CLI
Expected Deliverables
AIOS 与 Codex / Cursor 兼容性分析报告
AIOS 工程结构描述文件（如 aios_project.yaml）
Adapter 层设计与实现（CLI + 配置）
编译 / 烧录自动化脚本封装（供 AI 调用）
AI 代码生成规范（Prompt + 模板）
日志解析与反馈机制设计文档
Verification Method

Build verification:

command: aios build
expected: 成功生成 out.bin

Simulator test:

steps: 使用模拟器加载生成 bin
expected: APP 正常启动，无 crash

Device test:

steps:
执行 aios flash
使用 ResearchDownload 自动烧录
expected: 设备正常启动

Log verification:

expected patterns:
BUILD SUCCESS
FLASH OK
无严重 error log
Potential Risks
AI 生成代码不符合嵌入式规范
Mitigation: 引入代码模板 + lint 校验
误触发烧录导致设备异常
Mitigation: 增加确认机制 + 沙箱模式
AI 无法理解 legacy 工程结构
Mitigation: 提供结构描述文件 + prompt engineering
工具链兼容性问题（Arm CC）
Mitigation: 封装统一 build 接口
References
AIOS 内部 Build 文档
DAP / APP 架构说明
Codex API 文档
Cursor 使用文档
现有编译与烧录流程说明