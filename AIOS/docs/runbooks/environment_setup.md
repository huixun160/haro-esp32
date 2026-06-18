# ARCS SDK 环境搭建

## 适用范围

适用于聆思 ARCS SDK 官方推荐开发方式。官网明确说明当前仅支持 Linux 平台，推荐 Ubuntu 18.04 及以上版本。

## 推荐方式：自动搭建

在 SDK 根目录执行：

```bash
source env.sh
```

该脚本会自动完成：

- 检测工具链环境变量，已存在有效配置时直接复用
- 缺失时自动查找或下载安装工具链
- 设置 `NUCLEI_TOOLCHAIN_PATH`、`LISTENAI_TOOLS_PATH`、`PATH`
- 检查子模块状态并在异常时提示修复命令

## 常用排查命令

```bash
source env.sh check
source env.sh setup
source env.sh submodule sync
source env.sh info
```

## 手动搭建

当自动搭建失败时，可按下面顺序手动处理。

### 1. 准备工具链

可使用官网给出的工具链下载地址，或直接执行：

```bash
bash tools/scripts/prepare_toolchain.sh
```

### 2. 准备 ListenAI 开发工具包

可使用官网给出的工具包下载地址，或执行：

```bash
bash tools/scripts/prepare_listenai_tools.sh
```

### 3. 设置环境变量

```bash
export NUCLEI_TOOLCHAIN_PATH=$HOME/.listenai/gcc
export LISTENAI_TOOLS_PATH=$HOME/.listenai/listenai-tools
```

注意：

- 必须使用绝对路径
- 在非 shell 场景不要写 `~`
- IDE 中也应展开成绝对路径

## 环境验证

### 工具链验证

```bash
${NUCLEI_TOOLCHAIN_PATH}/bin/riscv64-unknown-elf-gdb --version
```

### J-Link 验证

```bash
JLinkGDBServerCLExe --version
```

## 常见问题

### 子模块异常

优先执行：

```bash
source env.sh submodule sync
```

### 环境变量异常

优先执行：

```bash
source env.sh check
```

### 串口权限不足

```bash
sudo usermod -a -G dialout $USER
```

执行后需要重新登录。

## 资料来源

- 快速入门：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/get_started.html>
- GDB 调试指南：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/gdb.html>
