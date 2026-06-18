# Technical Memo

**Title:** Robot AIOS Stage0-02 控制链路实现：hello-world 动作 / driver adapter / SDK 预留

**Project:** robot_aios

**Subsystem:** Robot Control / Driver Adapter / MCP Tool / Shell

**Author:** hepinzhen

**Priority:** HIGH

**Date:** 2026-04-15

---

## Background

白板的第 2 项是控制链路，能辨认出的关键词包括“控制/驱动”、“hello-world”、“algo python?”、“script / SDK”。这说明控制链路的要求不是一步到位做复杂运动，而是先实现一条分阶段的动作执行通路：

1. 先有最小动作 hello-world
2. 再把控制逻辑和底层驱动解耦
3. 再为脚本/SDK/算法接入预留适配层

本任务说明书用于指导大模型先完成控制链路代码骨架，供后续 runtime、UI、语音或视觉模块统一调用。

## Objective

完成机器人控制链路的 Stage0 骨架，满足以下要求：

1. 新建统一的 `robot_ctrl_*` 服务接口，不允许 UI、MCP、Shell 直接操作底层驱动
2. 支持至少 4 个 Stage0 mock 动作：`hello`、`nod`、`wave`、`stop`
3. 增加一个 adapter 层，允许未来接真实执行器 SDK
4. 增加 shell 触发入口和 MCP 工具入口
5. 动作状态必须通过 `voice_msg` 回流，供 UI/runtime 观察

## Current State

当前仓库中还没有成型的机器人控制服务，但有可复用位置：

- 板级/设备扩展目录：`src/category/evb/`
- 现有 MCP 工具目录：`src/category/evb/mcp-tools/`
- Shell 命令目录：`src/shell/cmd/`
- 事件总线：`src/framework/voice_msg.h`

现状问题：

- 没有统一的 robot control service
- 没有控制命令与驱动/SDK 的边界
- 没有最小动作命令供联调使用

## Scope

本任务按以下顺序实现：

### A. 新建控制服务层

新增目录：

- `src/server/robot_ctrl/`

至少创建以下文件：

- `src/server/robot_ctrl/robot_ctrl.h`
- `src/server/robot_ctrl/robot_ctrl.c`
- `src/server/robot_ctrl/robot_ctrl_adapter.h`
- `src/server/robot_ctrl/robot_ctrl_mock_adapter.c`
- `src/server/robot_ctrl/CMakeLists.txt`

接口要求：

- `int robot_ctrl_init(void);`
- `int robot_ctrl_execute(const char *action, const char *payload_json);`
- `int robot_ctrl_stop(void);`
- `const char *robot_ctrl_state_name_get(int state);`

### B. 添加动作状态事件

修改：

- `src/framework/voice_msg.h`

新增 robot control 事件域，建议新增：

- `VOICE_DOMAIN_ROBOT_CTRL`
- `VOICE_MSG_ROBOT_CTRL_EXECUTING`
- `VOICE_MSG_ROBOT_CTRL_DONE`
- `VOICE_MSG_ROBOT_CTRL_FAILED`
- `VOICE_MSG_ROBOT_CTRL_STOPPED`

要求：

- 所有动作执行结果都必须通过事件回流
- 事件 data 至少包含 action 名称、错误码、执行结果字符串

### C. mock adapter 先打通 hello-world

`robot_ctrl_mock_adapter.c` 先实现 mock 版本：

- `hello`：仅打印日志并发布 done
- `nod`：打印两次状态切换日志
- `wave`：打印一次动作序列日志
- `stop`：中止当前动作并发布 stopped

说明：

- Stage0 不接真实硬件
- 但 adapter 头文件必须设计成未来可替换为真实 SDK

### D. 增加 shell 调试入口

在 `src/shell/cmd/` 下新增命令文件，建议文件名：

- `shell_robot_ctrl.c`

要求支持：

- `robot_action hello`
- `robot_action nod`
- `robot_action wave`
- `robot_action stop`
- `robot_action exec <action> <json>`

### E. 增加 MCP 工具入口

在 `src/category/evb/mcp-tools/` 下新增：

- `mcp_tool_robot_action.c`

要求：

- MCP 工具内部只能调用 `robot_ctrl_execute()`
- 不允许 MCP 工具直接操作 mock adapter 或未来 SDK

### F. 为 script / SDK 接入预留扩展位

在 `robot_ctrl_adapter.h` 里预留：

- `execute`
- `stop`
- `set_param`
- `load_script`

说明：

- 本任务不实现 Python runtime
- 也不实现真实脚本引擎
- 只预留 adapter 接口和空实现

## Out of Scope

以下内容本任务不做：

- 不做真实舵机/电机控制
- 不做运动学和轨迹规划
- 不做 Python 解释器集成
- 不做复杂动作编排
- 不做 UI 页面

## Constraints

1. 所有上层入口统一走 `robot_ctrl_execute()`，不能直接调 adapter
2. mock adapter 必须可替换，不能把 mock 逻辑写死在 service 层
3. 事件总线仍然统一使用 `voice_msg`
4. shell 和 MCP 只能复用 service，不得各自重复实现控制逻辑

## Expected Deliverables

1. 新增 `src/server/robot_ctrl/` 控制服务层
2. `voice_msg.h` 新增 robot control 事件域
3. mock adapter 打通 `hello/nod/wave/stop`
4. shell 调试命令 `robot_action`
5. MCP 工具 `mcp_tool_robot_action.c`
6. adapter 层预留 script / SDK 扩展位

## Verification Method

- [ ] Build verification: `cmake --build /home/shiro/project-haro/build --parallel 8` 成功
- [ ] Shell verification: 执行 `robot_action hello` / `robot_action nod` / `robot_action wave` / `robot_action stop` 均有明确日志
- [ ] Event verification: 每个动作均发布对应 `VOICE_MSG_ROBOT_CTRL_*` 事件
- [ ] Architecture verification: shell 与 MCP 工具都只依赖 `robot_ctrl.h`
- [ ] Log verification: 日志至少包含 `robot_ctrl execute`, `adapter execute`, `robot_ctrl done/failed`

## Potential Risks

- 若 service 和 adapter 没分层，后面一接真实 SDK 就得整体重构
- 若 shell/MCP 直接调底层，后面不同入口行为会不一致
- 若没有事件回流，UI 和 runtime 无法观察动作进度

## References

- `AIOS/workflow/templates/technical_memo_template.md`
- `src/framework/voice_msg.h`
- `src/category/evb/mcp-tools/`
- `src/shell/cmd/`
- `src/category/evb/`
