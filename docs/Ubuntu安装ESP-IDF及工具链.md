# Ubuntu 安装 ESP-IDF 及工具链

本文档面向本仓库的 Ubuntu 环境。由于仓库依赖要求 `ESP-IDF >= 5.5.2`，以下流程固定安装 `ESP-IDF v5.5.4`，而不是直接安装 EIM 当前默认的最新稳定版。

## 1. 适用范围

- 适用于 Ubuntu、Debian、Linux Mint 等 Debian 系发行版
- 默认使用 Espressif 当前推荐的安装方式：`EIM`（ESP-IDF Installation Manager）
- 本文固定安装 `ESP-IDF v5.5.4`

官方参考文档：

- ESP-IDF Installation Manager 总览：<https://docs.espressif.com/projects/idf-im-ui/en/latest/>
- Debian/Ubuntu 安装 EIM：<https://docs.espressif.com/projects/idf-im-ui/en/latest/general_info.html>
- EIM 先决条件：<https://docs.espressif.com/projects/idf-im-ui/en/latest/prerequisites.html>
- EIM CLI 配置：<https://docs.espressif.com/projects/idf-im-ui/en/latest/cli_configuration.html>
- Linux/macOS 命令行激活与构建：<https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/linux-macos-start-project.html>
- ESP-IDF v5.5.4 文档入口：<https://docs.espressif.com/projects/esp-idf/en/v5.5.4/esp32/get-started/index.html>

## 2. 前提条件

建议使用具备 `sudo` 权限的普通用户执行安装。

先确认系统信息：

```bash
cat /etc/os-release
uname -m
```

按官方 EIM 文档，Linux 上需要先具备 Git、Python 以及若干构建与运行时依赖。建议先执行：

```bash
sudo apt update
sudo apt install -y \
  git wget flex bison gperf ccache \
  libffi-dev libssl-dev dfu-util libusb-1.0-0 \
  libgcrypt20 libglib2.0-0 libpixman-1-0 libsdl2-2.0-0 libslirp0 \
  python3 python3-pip python3-venv
```

再确认 Python 可用：

```bash
python3 --version
python3 -m venv --help >/dev/null
```

说明：

- EIM 在 Linux 上会检查这些先决条件；如果缺失，安装可能不会继续
- ESP-IDF 当前支持 Python `3.10` 到 `3.14`
- 即使使用 `eim-cli`，Ubuntu 上也仍然建议先装好上面的系统包

## 3. 安装 EIM

### 3.1 添加 Espressif APT 源

```bash
sudo mkdir -p /etc/apt/sources.list.d
echo "deb [trusted=yes] https://dl.espressif.com/dl/eim/apt/ stable main" | sudo tee /etc/apt/sources.list.d/espressif.list
```

注意：

- `tee` 命令和目标路径必须写在同一行
- 如果命令被误拆成两行，`/etc/apt/sources.list.d/espressif.list` 会被当成新的 shell 命令，从而报错

### 3.2 安装 EIM CLI

```bash
sudo apt update
sudo apt install -y eim-cli
```

如果你需要图形界面，也可以安装：

```bash
sudo apt install -y eim
```

安装完成后检查版本：

```bash
eim --version
```

## 4. 安装 ESP-IDF v5.5.4 与工具链

本仓库固定安装 `v5.5.4`，命令如下：

```bash
eim install -i v5.5.4
```

说明：

- `-i` 是 EIM 的官方版本参数，`eim install -i v5.5.4` 写法正确
- 如果直接执行 `eim install`，EIM 会安装它当前默认的最新稳定版，这不一定符合本仓库要求
- 如果你更习惯交互式方式，也可以先执行 `eim wizard`，然后在向导里手动选择 `v5.5.4`

安装完成后，可以查看本机已安装的版本：

```bash
eim list
```

## 5. 激活 ESP-IDF 环境

安装成功后，`eim` 会输出激活命令。对于 `v5.5.4`，典型形式如下：

```bash
source ~/.espressif/tools/activate_idf_v5.5.4.sh
```

激活后，当前 shell 会获得：

- `IDF_PATH`
- `idf.py`
- 对应版本的 Python 虚拟环境
- 工具链相关 `PATH`

验证激活结果：

```bash
echo "$IDF_PATH"
idf.py --version
```

## 6. 可选：自动激活

如果你希望每次打开终端都自动进入 `ESP-IDF v5.5.4` 环境，可在 `~/.bashrc` 末尾加入：

```bash
# Auto-activate ESP-IDF when opening an interactive shell.
if [ -z "${IDF_PATH:-}" ] && [ -f "$HOME/.espressif/tools/activate_idf_v5.5.4.sh" ]; then
    . "$HOME/.espressif/tools/activate_idf_v5.5.4.sh" >/dev/null 2>&1
fi
```

保存后执行：

```bash
source ~/.bashrc
```

重新打开一个终端，再验证：

```bash
echo "$IDF_PATH"
idf.py --version
```

## 7. 构建验证

如果环境安装正确，最直接的验证方式是进入一个 ESP-IDF 项目后执行：

```bash
idf.py --version
idf.py build
```

对于本仓库，可在项目根目录执行：

```bash
cd /home/w/xiaozhi-esp32
idf.py build
```

如果只是先确认环境是否可用，检查 `idf.py --version` 即可；完整编译会额外验证工具链、Python 环境和工程配置是否匹配。

## 8. 常见问题

### 8.1 `tee` 报路径不存在

现象：

```text
bash: /etc/apt/sources.list.d/espressif.list: No such file or directory
```

处理方式：

```bash
sudo mkdir -p /etc/apt/sources.list.d
echo "deb [trusted=yes] https://dl.espressif.com/dl/eim/apt/ stable main" | sudo tee /etc/apt/sources.list.d/espressif.list
```

### 8.2 `idf.py: command not found`

说明当前 shell 还没有激活 ESP-IDF 环境。

执行：

```bash
source ~/.espressif/tools/activate_idf_v5.5.4.sh
```

### 8.3 装成了错误版本

如果你误执行了 `eim install`，可能会装到 EIM 当前默认的最新稳定版，而不是 `v5.5.4`。请重新执行：

```bash
eim install -i v5.5.4
eim list
```

确认 `v5.5.4` 已经出现在安装列表中后，再使用对应的激活脚本。

### 8.4 串口无权限

如果烧录时提示 `Permission denied`，将当前用户加入 `dialout` 组：

```bash
sudo usermod -aG dialout $USER
```

执行后重新登录，或重开桌面会话再试。

### 8.5 项目路径包含空格

ESP-IDF 官方文档明确说明，工程路径和 IDF 路径都不应包含空格。请将项目放到类似下面的路径中：

```bash
/home/w/xiaozhi-esp32
```

## 9. 当前机器已验证配置

以下信息来自当前机器 `2026-04-23` 的实际安装结果。

### 9.1 已验证版本

- EIM: `0.11.1`
- ESP-IDF: `v5.5.4`

### 9.2 已验证路径

- EIM 命令：`/usr/bin/eim`
- ESP-IDF 激活脚本：`/home/w/.espressif/tools/activate_idf_v5.5.4.sh`
- ESP-IDF 根目录：`/home/w/.espressif/v5.5.4/esp-idf`
- ESP-IDF Python 环境：`/home/w/.espressif/tools/python_env/idf5.5_py3.13_env`

### 9.3 当前机器环境入口

手动进入 ESP-IDF 环境：

```bash
source /home/w/.espressif/tools/activate_idf_v5.5.4.sh
```

### 9.4 当前机器自动激活状态

当前机器已经在 [`/home/w/.bashrc`](/home/w/.bashrc:145) 中加入自动激活配置。新开一个交互式 Bash 终端后，会自动加载 `ESP-IDF v5.5.4` 环境。

如果当前终端还未刷新，可执行：

```bash
source ~/.bashrc
```

### 9.5 当前机器验证命令

以下命令已经在当前机器验证通过：

```bash
eim --version
eim list
bash -ic 'idf.py --version'
```

期望输出类似：

```text
eim 0.11.1
Installed versions:
- v6.0 [/home/w/.espressif/v6.0/esp-idf]
- v5.4 [/home/w/.espressif/v5.4/esp-idf]
- v5.5.4 (selected) [/home/w/.espressif/v5.5.4/esp-idf]
ESP-IDF v5.5.4
```
