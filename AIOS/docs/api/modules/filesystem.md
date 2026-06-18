# ARCS SDK 文件系统

## 定位

ARCS SDK 的文件系统组件提供从底层磁盘到上层 POSIX 接口的一整套分层能力，适合处理：

- SD / TF 卡文件读写
- Flash / RAM Disk 文件访问
- 本地媒体资源挂载
- 应用对 POSIX 风格文件接口的使用

## 架构

官网给出的数据路径可概括为：

`Application -> POSIX API / LSFS API -> LVFS -> LSFS -> SubFS -> Disk`

### 层次说明

- `POSIX API`：`open/read/write/close` 风格接口
- `LVFS`：POSIX 兼容层与文件描述符管理
- `LSFS`：统一文件系统抽象层，多挂载点管理
- `SubFS`：具体子文件系统实现
- `Disk`：底层存储介质

## 适用方式

### 1. 直接用 POSIX

适合希望代码迁移成本更低的应用。

### 2. 直接用 LSFS

适合在嵌入式场景中更明确地控制挂载、读写和存储介质行为。

## 典型示例

官网 `samples/modules/fs` 提供两类样例：

- `LSFS 文件系统操作示例`
- `LVFS POSIX 文件操作示例`

其中 `LSFS` 样例展示了：

1. 初始化 SD 卡和磁盘系统
2. 初始化 LSFS
3. 挂载文件系统
4. 写文件 `/SD:/sdmmc.txt`
5. 回读验证
6. 遍历根目录
7. 卸载文件系统

## 资源打包

如果项目要把目录内容打成 FAT32 镜像供设备挂载，可使用：

```bash
./mkfatfs.py -o disk.img -s 32M -d resources -l SD -v
```

建议：

- FAT32 镜像容量优先大于实际资源总量
- 音频、图片、字体资源统一用目录打包
- 先在 PC 上用 `mdir` 或挂载方式验证镜像内容

## 资料来源

- 文件系统组件：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/modules/fs/README.html>
- 文件系统示例：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/samples/modules/fs/index_zh.html>
- LSFS 示例：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/samples/modules/fs/lsfs/README.html>
- FAT32 打包工具：<https://docs2.listenai.com/arcs-sdk/latest/zh/html/tools/fatfs_package/README.html>
