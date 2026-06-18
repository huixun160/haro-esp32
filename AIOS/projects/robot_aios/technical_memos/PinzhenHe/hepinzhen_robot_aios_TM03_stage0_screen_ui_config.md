# Technical Memo

**Title:** Robot AIOS Stage0-03 Screen/UI 配置与状态页实现

**Project:** robot_aios

**Subsystem:** UI / Presenter / Model / Settings

**Author:** hepinzhen

**Priority:** HIGH

**Date:** 2026-04-15

---

## Background

白板第 3 项是 `Screen` 与 `UI 配`。这里的要求不是做漂亮界面，而是做一个能承接 Stage0 各模块状态的屏幕入口，让开发者和后续大模型都能通过 UI 看到 runtime、control、mic、speaker、camera 的当前状态，并能触发关键测试动作。

当前仓库已有一套完整的 LLM UI 工程，可在其基础上直接扩展，而不是另起炉灶。

## Objective

完成一个 Stage0 UI 配置/调试入口，满足以下目标：

1. 不新建独立 UI 框架，直接复用 `apps-ui/apps/llm/`
2. 新增一个“Robot Debug / Stage0”设置页或二级页
3. 页面至少展示 runtime 连接状态、会话状态、robot action 状态、camera 状态
4. 页面至少提供 4 个操作入口：连接 runtime、启动会话、执行 hello 动作、抓拍图片
5. UI 只能调 model/presenter，不允许 view 直接调用 service 层

## Current State

当前 UI 相关代码已存在：

- 应用入口：`apps-ui/apps/llm/lisa_ui_app.c`
- 语音模型：`apps-ui/apps/llm/models/model_voice.c`
- 相机模型：`apps-ui/apps/llm/models/model_camera.c`
- 设置页 presenter：`apps-ui/apps/llm/presenters/setting_presenter.c`
- 设置页 view：`apps-ui/apps/llm/views/setting_view.c`
- 通用设置页面：`apps-ui/apps/llm/views/setting/setting_common_view.c`

问题：

- 当前没有面向 Stage0 联调的统一调试页
- runtime / robot control / camera 的跨模块状态没有被聚合到同一个页面

## Scope

本任务按以下顺序实现：

### A. 新增 Stage0 调试 model

新增文件：

- `apps-ui/apps/llm/models/model_robot_debug.h`
- `apps-ui/apps/llm/models/model_robot_debug.c`

职责：

- 聚合读取 `ai_runtime` 连接状态、会话状态
- 聚合读取 `robot_ctrl` 最近动作状态
- 聚合读取 `model_camera` 初始化状态
- 对外提供 UI 可调用接口：
  - `model_robot_debug_runtime_connect()`
  - `model_robot_debug_session_start()`
  - `model_robot_debug_robot_hello()`
  - `model_robot_debug_camera_capture()`

### B. 新增 presenter

新增文件：

- `apps-ui/apps/llm/presenters/setting_robot_debug_presenter.c`
- `apps-ui/apps/llm/presenters/setting_robot_debug_presenter.h`

要求：

- presenter 调 model
- view 不直接调用 service
- presenter 负责把按钮事件转换为 model 调用

### C. 新增 view

新增文件：

- `apps-ui/apps/llm/views/setting/setting_robot_debug_view.c`
- `apps-ui/apps/llm/views/setting/setting_robot_debug_view.h`

页面必须包含：

- runtime connected / disconnected 状态
- session idle / running 状态
- robot action last result
- camera ready / not ready 状态
- 4 个按钮：
  - Connect Runtime
  - Start Session
  - Robot Hello
  - Capture Photo

### D. 接入现有导航

修改以下文件完成页面接入：

- `apps-ui/apps/llm/lisa_ui_nav_scr_ids.h`
- `apps-ui/apps/llm/presenters/setting_presenter.c`
- `apps-ui/apps/llm/views/setting_view.c`
- `apps-ui/apps/llm/views/setting/CMakeLists.txt`
- `apps-ui/apps/llm/models/CMakeLists.txt`
- `apps-ui/apps/llm/presenters/CMakeLists.txt`

要求：

- 从现有设置页进入即可
- 不要新建完全独立的首页导航体系

### E. 订阅状态事件

`model_robot_debug.c` 必须订阅：

- `VOICE_MSG_CLOUD_CONNECTED`
- `VOICE_MSG_CLOUD_DISCONNECTED`
- `VOICE_MSG_CLOUD_SESSION_STARTING`
- `VOICE_MSG_CLOUD_SESSION_FINISHED`
- `VOICE_MSG_ROBOT_CTRL_DONE`
- `VOICE_MSG_ROBOT_CTRL_FAILED`
- 与 camera 相关的状态事件或本地状态

要求：

- 页面显示值必须来自真实状态，而不是点击按钮后本地假设成功

## Out of Scope

以下内容本任务不做：

- 不做产品化视觉设计
- 不做复杂动画
- 不做完整多模态会话页
- 不替换现有首页结构

## Constraints

1. 直接复用现有 `apps-ui/apps/llm/` 架构
2. view 不得直接 include `ai_runtime.h`、`robot_ctrl.h`、`service_camera.h`
3. 页面必须是调试页，不追求产品视觉，只追求状态可见与动作可触发
4. 事件驱动优先，避免按钮点击后直接假更新 UI

## Expected Deliverables

1. `model_robot_debug.*`
2. `setting_robot_debug_presenter.*`
3. `setting_robot_debug_view.*`
4. 设置页导航接入代码
5. 页面状态订阅与按钮动作打通

## Verification Method

- [ ] Build verification: `cmake --build /home/shiro/project-haro/build --parallel 8` 成功
- [ ] UI verification: 设置页可进入 `Robot Debug / Stage0` 页面
- [ ] State verification: runtime/session/action/camera 状态能随真实事件变化
- [ ] Action verification: 四个按钮触发后都有日志与状态反馈
- [ ] Layer verification: view 不直接依赖 service 头文件

## Potential Risks

- 若 UI 直接调 service，后续会导致 presenter/model 形同虚设
- 若页面状态不是事件驱动，联调时会出现“UI 显示已成功但后台没执行”
- 若改动导航过大，容易引入无关 UI 回归

## References

- `AIOS/workflow/templates/technical_memo_template.md`
- `apps-ui/apps/llm/lisa_ui_app.c`
- `apps-ui/apps/llm/lisa_ui_nav_scr_ids.h`
- `apps-ui/apps/llm/models/model_voice.c`
- `apps-ui/apps/llm/models/model_camera.c`
- `apps-ui/apps/llm/presenters/setting_presenter.c`
- `apps-ui/apps/llm/views/setting_view.c`
- `apps-ui/apps/llm/views/setting/setting_common_view.c`
