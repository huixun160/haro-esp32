# Task 7 记录：AIOS Tool Execution Bridge

- 状态：`未开始`
- 对应任务：`Task 7: Implement AIOS Tool Execution Bridge`

## 当前目标

- 新增 `AiosActionExecutor`
- 接入 `tool.execute.request`
- 保持串行执行和 busy 失败语义

## 当前预期风险

- 如果直接把 AIOS 指令散落到板级代码，后续维护会快速失控
- 如果工具执行和会话生命周期耦合过深，会影响中断和恢复语义

## 待补记录

- 本任务做了什么
- 修改文件
- 验证结果
- 遇到的坑
- 下一阻塞点
