# Task 8 记录：开发/编译/烧录/测试闭环

- 状态：`未开始`
- 对应任务：`Task 8: Build the Automated Development/Build/Flash/Test Loop`

## 当前目标

- 增加 `tools/aios/` 下的 build、flash、monitor、smoke 脚本
- 建立一键闭环入口

## 当前预期风险

- ESP-IDF 版本、shell 环境变量和串口路径容易导致脚本不稳定
- 日志断言如果绑定过死，实际联调会出现很多误报

## 待补记录

- 本任务做了什么
- 修改文件
- 验证结果
- 遇到的坑
- 下一阻塞点
