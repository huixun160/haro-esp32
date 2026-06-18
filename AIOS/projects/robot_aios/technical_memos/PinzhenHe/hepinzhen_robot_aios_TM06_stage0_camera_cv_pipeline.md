# Technical Memo

**Title:** Robot AIOS Stage0-06 Camera/CV 单帧识别链路实现

**Project:** robot_aios

**Subsystem:** Camera / CV / Image Recognition / Runtime Bridge

**Author:** hepinzhen

**Priority:** HIGH

**Date:** 2026-04-15

---

## Background

白板第 6 项是 `Camera`、`CV`、右侧还有 `Algo` 标注。结合整个顺序，它的含义不是先做本地复杂视觉算法，而是先把“拍一张图 -> 发给 runtime/云端识别 -> 回流结果”的单帧识别链路打通，并为后续本地 CV 算法或第三方视觉 SDK 预留插槽。

当前仓库已经有 camera model、camera service、video middleware 和图片上传/识别相关代码，可在这些基础上做最小闭环。

## Objective

完成 Stage0 camera/cv 单帧链路，满足以下目标：

1. 复用现有 `service_camera` / `video_camera` 能力完成单张抓拍
2. 新建 camera service facade，统一封装抓拍与识别入口
3. 通过 `ai_runtime_image_recognize()` 打通“拍照后发起识别”的主链路
4. 识别结果通过现有 `VOICE_MSG_CLOUD_MCP_IMAGE_RECOGNITION` 或新增结果事件回流
5. 提供 shell 调试命令与 UI 按钮入口可复用的统一接口

## Current State

当前相关文件：

- UI camera model：`apps-ui/apps/llm/models/model_camera.c`
- camera service：`apps/arcs-evb/services/service_camera.h`
- video middleware：`src/middleware/video/video_camera.h`
- 旧图像上传：`src/server/lschat_server/voice_img_upload.c`
- 旧云识别入口：`src/server/lschat_server/voice_cloud.h`

现状问题：

- 还没有统一的 camera service facade
- UI model 与 runtime 识别链路之间缺乏统一桥接
- 没有清晰的 Stage0 单帧识别入口

## Scope

本任务按以下顺序实现：

### A. 新建 camera service facade

新增文件：

- `src/server/camera_service/camera_service.h`
- `src/server/camera_service/camera_service.c`
- `src/server/camera_service/CMakeLists.txt`

接口至少包含：

- `int camera_service_init(void);`
- `int camera_service_capture(uint8_t *buf, uint32_t *len);`
- `int camera_service_capture_and_recognize(void);`
- `int camera_service_get_last_result(char *buf, uint32_t len);`

要求：

- service 内部复用 `service_camera_*`
- `capture_and_recognize()` 完成抓拍 + 调用 `ai_runtime_image_recognize()`

### B. 新建 camera runtime bridge

新增文件：

- `src/server/aios_runtime/ai_runtime_camera_bridge.c`
- `src/server/aios_runtime/ai_runtime_camera_bridge.h`

职责：

- 承接 camera service 发起的识别请求
- 统一处理识别结果事件回流
- 把结果转成 UI 和 shell 易消费的文本状态

### C. 对接 UI model

修改：

- `apps-ui/apps/llm/models/model_camera.c`

要求：

- `model_camera_capture()` 最终复用 `camera_service_capture()` 或 `camera_service_capture_and_recognize()`
- 不允许 UI model 直接拼装云请求逻辑

### D. 增加 shell 调试入口

在 `src/shell/cmd/` 下新增：

- `shell_camera_debug.c`

要求支持：

- `camera init`
- `camera snap`
- `camera recognize`
- `camera result`

### E. 结果事件

优先复用现有：

- `VOICE_MSG_CLOUD_MCP_IMAGE_RECOGNITION`

如果不够用，可补充 camera result 事件，但要求：

- UI、shell、runtime 三方使用统一结果源

## Out of Scope

以下内容本任务不做：

- 不做本地 CV 模型推理
- 不做连续视频流识别
- 不做复杂图像预处理
- 不做多相机支持

## Constraints

1. 先打通单帧识别，不做连续流
2. camera service 负责封装抓拍，runtime 负责识别请求，不要把两者混在 UI model
3. shell/UI 都必须复用 service，不允许各自直接调底层 camera
4. 识别结果必须有统一事件或统一缓存读取方式

## Expected Deliverables

1. `camera_service.*`
2. `ai_runtime_camera_bridge.*`
3. `model_camera.c` 改为复用 camera service
4. `shell_camera_debug.c`
5. 单帧抓拍 -> 识别 -> 结果回流闭环

## Verification Method

- [ ] Build verification: `cmake --build /home/shiro/project-haro/build --parallel 8` 成功
- [ ] Camera verification: `camera snap` 能拿到非空图像数据或明确错误码
- [ ] Recognize verification: `camera recognize` 会触发 `ai_runtime_image_recognize()`
- [ ] Result verification: shell 或 UI 能读取最近一次识别结果
- [ ] Layer verification: `model_camera.c` 不直接拼装 runtime 识别协议

## Potential Risks

- 相机 buffer 大小和内存管理不当时容易出现崩溃或截断
- 若 camera service 与 runtime bridge 混在一起，后续本地 CV 扩展会很难做
- 若结果回流没有统一来源，UI 和 shell 看到的状态会不一致

## References

- `AIOS/workflow/templates/technical_memo_template.md`
- `apps-ui/apps/llm/models/model_camera.c`
- `apps/arcs-evb/services/service_camera.h`
- `src/middleware/video/video_camera.h`
- `src/server/lschat_server/voice_img_upload.c`
- `src/server/lschat_server/voice_cloud.h`
- `src/framework/voice_msg.h`
