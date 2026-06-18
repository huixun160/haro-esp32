# ARCS SDK GUI 能力

## 当前可见方向

官网公开材料中，GUI 能力主要通过 `LVGL` 和对应示例体现，而不是旧式 MMI/DAP 风格接口。

## 公开能力

- LVGL 7 Benchmark
- LVGL 7 Widgets
- LVGL 8 Benchmark
- LVGL 8 Widgets

这说明当前 ARCS SDK 对图形界面的公开实践更偏向：

- 以 LVGL 作为主要 GUI 框架
- 通过示例快速验证屏幕、控件和性能
- 与板级 LCD、输入设备、文件系统资源联动

## 使用建议

- 屏幕项目先跑 `Benchmark` 再跑 `Widgets`
- 资源图片、字体可结合文件系统和打包工具使用
- GUI 调试时优先同时打开串口日志

## 资料来源

- LVGL 示例：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/samples/modules/lvgl/index_zh.html>
- 组件模块示例总览：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/samples/modules/index_zh.html>
