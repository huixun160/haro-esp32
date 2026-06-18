# ARCS SDK 核心开发接口

本页不再沿用旧的展锐 OS Core API 普查口径，而是按 ARCS SDK 当前公开开发主线整理“实际最先会碰到的核心接口与脚本”。

## 核心入口

### 环境入口

- `env.sh`
- `source env.sh check`
- `source env.sh setup`
- `source env.sh submodule sync`
- `source env.sh info`

### 构建入口

- `build.sh`
- `-DBOARD=arcs_evb`
- `-DBOARD=arcs_mini`

### 调试入口

- `riscv64-unknown-elf-gdb`
- `JLinkGDBServerCLExe`

## 工程最小闭环

```bash
source env.sh
./build.sh -C -S samples/helloworld -DBOARD=arcs_evb
./tools/burn/cskburn -s /dev/ttyUSB0 -b 3000000 0x0 build/helloworld.bin -C arcs
```

## 使用建议

- 新工程先跑通 `samples/helloworld`
- 板型先固定，再接组件
- 调试优先保留 `.elf`
- 所有路径优先使用绝对路径

## 资料来源

- <https://docs2.listenai.com/arcs-sdk/latest/zh/html/get_started.html>
- <https://docs2.listenai.com/arcs-sdk/latest/zh/html/gdb.html>
