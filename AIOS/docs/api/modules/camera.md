# ARCS SDK 摄像头能力

## API 参考补充结论

结合官网组件文档和 API 参考索引，`lisa_camera` 是当前公开深度比较高的驱动模块之一。

它至少包含 4 层内容：

- `lisa_camera.h`：摄像头对外接口
- `lisa_camera_bus.*`：摄像头总线层
- `sensor.h` / `sensor.c`：统一 sensor 抽象层
- 各型号 sensor 驱动、寄存器定义与初始化表

## 总线层

API 参考中已明确出现：

- `lisa_camera_bus_dvp.c`
- `lisa_camera_bus_spi.c`

这意味着当前公开的摄像头接入至少覆盖：

- DVP 摄像头总线
- SPI 摄像头总线

## 统一 sensor 抽象

`sensor.h` 页面显示，摄像头抽象层至少公开了：

- `camera_sensor_info_t`
- `ratio_settings_t`
- `resolution_info_t`
- `sensor_id_t`
- `camera_status_t`
- `sensor_s`

以及一组常用寄存器访问接口：

- `sensor_twi_read_reg8`
- `sensor_twi_read_reg16`
- `sensor_twi_write_reg8`
- `sensor_twi_write_reg16`
- `sensor_twi_write_raw8`
- `camera_sensor_get_info`
- `sensor_twi_init`

这说明 ARCS SDK 对 camera 的抽象并不是“只给一个高层 API”，而是同时公开了 sensor 发现、寄存器读写和型号信息查询能力。

## 已公开的 sensor 型号

API 参考索引当前可确认下列型号：

- `bf20a6`
- `bf3005`
- `bf3901`
- `gc0308`
- `gc0310`
- `gc0328`
- `gc032a`
- `gc2145`
- `nt99141`
- `ov2640`
- `ov3660`
- `ov5640`
- `ov7670`
- `ov7725`
- `ov9655`
- `sc030iot`
- `sc031gs`
- `sc101iot`

## 从 API 参考可见的典型能力

以 `gc032a` 为例，文档中能直接看到的能力包括：

- `gc032a_detect`
- `gc032a_init`
- `set_pixformat`
- `get_pixformat`
- `set_hmirror`
- `set_vflip`
- `set_colorbar`
- `set_window`
- `get_window`
- `get_reg`
- `set_reg`

这反映出公开驱动通常会覆盖：

- 设备探测
- 初始化
- 像素格式切换
- 镜像/翻转
- colorbar 测试
- 窗口裁剪
- 寄存器级调试

## 对项目的实际意义

- 做摄像头选型时，可先对照 API 参考确认是否已有现成 sensor 适配
- 做 bring-up 时，可直接围绕 `sensor.h` 的寄存器接口与 `*_detect`、`*_init` 入口排查
- 如果板上使用 DVP 或 SPI camera，总线层已经有明确分层，不需要从零设计抽象

## 资料来源

- API 参考入口：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/_static/api_doc/html/annotated.html>
- File List：<https://docs2.listenai.com/arcs-sdk/v0.1.2/zh/html/_static/api_doc/html/files.html>
- `sensor.h`：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/_static/api_doc/html/sensor_8h.html>
- `gc032a.h`：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/_static/api_doc/html/gc032a_8h.html>
- `gc032a.c`：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/_static/api_doc/html/gc032a_8c.html>
