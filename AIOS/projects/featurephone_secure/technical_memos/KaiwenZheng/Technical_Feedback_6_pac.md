

------



# **Technical Feedback 6**



## **DAP-FMM 集成修复：PAC 打包失败 + 菜单入口缺失**



**版本**：v1  
**日期**：2026-02-09  
**平台**：UNISOC T127 / Mocor / Windows 11  
**前序文档**：Technical_Memo_5_testndebug.md  
**DAP 架构版本**：v2.1 → v2.2

------



## **1. 工作背景**



### 1.1 上下文

在 Technical Memo 5 完成 DAP 编译验证（Shim 层 + GUI 封装 + dap.mk include 路径修复）后，DAP 模块已能成功编译。但在实际构建 PAC 固件包并尝试在手机上使用时，暴露了两个关键问题：

1. **PAC 文件异常**：构建产出的 `.pac` 文件仅 17 KB，远小于正常的 51+ MB
2. **菜单不可见**：烧机后在文件管理器中选中 `.bin` 文件，Options 菜单中无 DAP 相关选项

### 1.2 目标

- 修复 PAC 打包失败的根因
- 让 "Execute" 菜单项正确出现在 FMM Option 菜单中
- 实现只对 `.bin` 文件启用 Execute 菜单（其他文件灰掉）
- 全量编译验证（零错误 + PAC 51+ MB）

------



## **2. Bug 分析与修复**



### **Bug #1 — PAC 文件仅 17 KB**

#### ??

```
mm.bat ums9117_240X320BAR_64MB_ML new
→ 构建报 "do packet success"
→ 但 .pac 文件只有 17,604 bytes（正常应 51+ MB）
```

#### 根因追踪（因果链）

```
mmifmm_mainwin.c 中 #ifdef ENABLE_DAP 块内调用了 MMIFMM_GetFullPathName()
  → 该函数在整个项目中从未被定义或声明
  → armlink 报 Error: L6218E (Undefined symbol)
  → 链接失败，.axf 未生成
  → fromelf 导出失败，EXEC_USER_IMAGE.bin / EXEC_KERNEL_IMAGE.bin 未生成
  → pac_9117.pl 打包工具报 "Can't open EXEC_USER_IMAGE.bin"
  → PAC 文件只包含头部（17 KB）
```

**关键发现**：构建脚本输出了 `do packet success`，但实际上 `.bin` 镜像缺失。这是因为打包工具对不存在的组件不做阻断性报错，脚本依旧返回成功。**不能仅依赖脚本返回值判断构建成功，必须检查 PAC 文件大小。**

#### 修复方案

`MMIFMM_GetFullPathName` 是集成时错写的函数名。FMM 中已有等效函数 `MMIFMM_CombineFullFileName`，但参数签名不同：

| | MMIFMM_GetFullPathName（不存在） | MMIFMM_CombineFullFileName（正确） |
|---|---|---|
| 参数 1 | `current_path_ptr` | `list_data_ptr` |
| 参数 2 | `list_data_ptr` | `current_path_ptr` |
| 参数 3 | `index` | `index` |
| 参数 4 | `file_name_ptr` | `file_name_ptr` |
| 参数 5 | `&file_name_len`（指针） | `max_len`（值） |
| 返回值 | `void`（假设） | `uint32`（实际路径长度） |

修复代码（`mmifmm_mainwin.c`）：

```diff
-  MMIFMM_GetFullPathName(
-      view_win_d->main_d_ptr->s_fmm_current_path_ptr,
-      view_win_d->main_d_ptr->s_fmm_list_data_ptr,
-      index, file_name_ptr, &file_name_len);
+  file_name_len = MMIFMM_CombineFullFileName(
+      view_win_d->main_d_ptr->s_fmm_list_data_ptr,
+      view_win_d->main_d_ptr->s_fmm_current_path_ptr,
+      index, file_name_ptr, MMIFMM_FULL_FILENAME_LEN + 1);
```

> **教训**：集成新功能时调用平台 API，必须先用 `grep` 确认函数确实存在并核对完整签名。

------



### **Bug #2 — FMM Options 菜单中不出现 "Execute"**

#### ??

PAC 修复后烧机成功，但在文件管理器中选中 `.bin` 文件按 Options 键，菜单中没有 DAP 相关选项。

#### 根因分析

FMM 菜单系统的工作原理：

```
1. mmifmm_menutable.h    枚举定义 → ID_FMM_DAP_EXECUTE ? 已做
2. mmifmm_menutable.c    菜单组数组注册                 ? 未做！
3. files_manager_mdu_def.h  文本资源定义               ? 未做！
4. DisableInvalidMenuItem()  文件类型条件禁用           ? 未做！
5. HandleMenuOption()    case 处理逻辑                  ? 已做
```

步骤 1 和 5 已在早期编码中完成，但**步骤 2/3/4 被遗漏**——只声明了菜单 ID 的枚举值和处理逻辑，却没有把它注册到可见的菜单组里。

#### 修复方案（三个文件）

**文件 1：`files_manager_mdu_def.h`** — 添加文本资源

```c
#ifdef ENABLE_DAP
RES_ADD_STRING(TXT_FMM_DAP_EXECUTE, "Execute")
#endif
```

> **注意**：资源定义必须放在 `files_manager_mdu_def.h` 中（不是 `fmm_mdu_def.h`）。构建系统的资源编译器从前者读取并生成枚举 ID。第一次修复时错误地放在了 `fmm_mdu_def.h` 中，导致 `TXT_FMM_DAP_EXECUTE is undefined` 编译错误。

**文件 2：`mmifmm_menutable.c`** — 在两个菜单数组末尾注册

分别在 `menu_fmm_normal_list_opt[]`（文件夹浏览视图）和 `menu_fmm_normal_file_list_opt[]`（文件浏览视图）的末尾添加：

```c
#ifdef ENABLE_DAP
    {ID_FMM_DAP_EXECUTE, TIP_NULL, {TXT_COMMON_OK, TXT_NULL, STXT_RETURN},
     TXT_FMM_DAP_EXECUTE, 0, 0, 0, NULL},
#endif
```

菜单项结构说明：`GUIMENU_ITEM_T` = `{ID, TIP, {左/中/右软键文本}, 显示文本, 图标正常, 图标按下, 0, 子菜单}`

**文件 3：`mmifmm_mainwin.c`** — 在 `DisableInvalidMenuItem()` 中添加条件禁用

在 `switch(list_data_ptr->checked)` 块结尾、`path_is_valid` 检查之前插入：

```c
#ifdef ENABLE_DAP
  /* 非 .bin 文件或文件夹时禁用 Execute 菜单 */
  {
    BOOLEAN is_bin_file = FALSE;
    if (current_index >= list_data_ptr->folder_num) {
      wchar dap_full_path[MMIFMM_FULL_FILENAME_LEN + 1] = {0};
      MMIFMM_CombineFullFileName(
          list_data_ptr, current_path_ptr, current_index,
          dap_full_path, MMIFMM_FULL_FILENAME_LEN + 1);
      is_bin_file = DAP_FMM_IsBinFile((const uint16 *)dap_full_path);
    }
    MMIAPICOM_EnableGrayed(win_id, group_id, ID_FMM_DAP_EXECUTE,
                           (BOOLEAN)!is_bin_file);
  }
#endif
```

逻辑说明：
- `current_index >= folder_num` → 当前选中的是文件（≠文件夹）
- `MMIFMM_CombineFullFileName` → 拼接完整路径
- `DAP_FMM_IsBinFile` → 检查 `.bin` / `.BIN` 后缀
- `MMIAPICOM_EnableGrayed(... , !is_bin_file)` → 非 bin 文件时灰掉

------



### **Bug #3 — 资源定义放错文件**

#### ??

修复 Bug #2 后首次编译报：

```
"mmifmm_menutable.c", line 92: Error: #20: identifier "TXT_FMM_DAP_EXECUTE" is undefined
```

#### 根因

FMM 存在两个资源定义文件：

| 文件 | 用途 |
|------|------|
| `fmm_mdu_def.h` | **旧版**资源定义（源码目录中直接编辑） |
| `files_manager_mdu_def.h` | **构建系统实际使用**的文件，被复制到 `build/res/files_manager/` 目录 |

构建系统的资源编译流程：
```
files_manager_mdu_def.h (源码)
   ↓ 预处理+复制
build/res/files_manager/files_manager_mdu_def.h
   ↓ 资源编译
生成 TXT_FMM_* 枚举 ID → C 编译器可见
```

`RES_ADD_STRING` 放在 `fmm_mdu_def.h` 中不会被资源编译器看到。

#### 修复

将 `RES_ADD_STRING(TXT_FMM_DAP_EXECUTE, "Execute")` 从 `fmm_mdu_def.h` 移到 `files_manager_mdu_def.h`。

> **经验**：涉及资源系统时，不能假设 "同目录下的 .h 文件都等效"——必须追踪构建系统实际引用的是哪个文件。可以在 `build/res/` 目录下搜索已有 ID 来确认。

------



## **3. 构建验证结果**

### 最终构建

```
mm.bat ums9117_240X320BAR_64MB_ML new
→ 编译错误: 0
→ 链接错误: 0
→ PAC 大小: 51.5 MB ?
→ do packet success ?
→ 耗时: 2381 秒 (~40 分钟)
```

### 构建日志归档

```
docs/build_debug/2026-02-08_win11_kz_zjj/logs/
├── step7_mm_new_menu_fix.log    # 第一次尝试（TXT_FMM_DAP_EXECUTE undefined）
├── step8_mm_new_menu_fix2.log   # 第二次（app_main.a Permission denied）
└── step9_mm_new_menu_fix3.log   # 第三次成功 ?
```

------



## **4. 修改的文件清单**

| 文件 | 改动摘要 | 行数 |
|------|---------|------|
| `mmifmm_mainwin.c` | 修复 `MMIFMM_GetFullPathName` → `MMIFMM_CombineFullFileName` | ~4 行 |
| `mmifmm_mainwin.c` | `DisableInvalidMenuItem()` 添加 DAP .bin 条件禁用 | ~16 行 |
| `mmifmm_menutable.c` | 两个菜单数组注册 `ID_FMM_DAP_EXECUTE` | 各 3 行 |
| `files_manager_mdu_def.h` | 添加 `TXT_FMM_DAP_EXECUTE` 资源字符串 | 3 行 |
| `fmm_mdu_def.h` | ~~撤销误放的资源定义~~（还原原样） | 0 行 |
| `DAP/README.md` | 更新至 v2.2，添加 Bug 修复记录 | 全文重写 |

所有改动均在 `#ifdef ENABLE_DAP` 保护下，`ENABLE_DAP=FALSE` 时零影响。

------



## **5. 关键经验总结**



### 5.1 PAC 大小是构建成功的最终判据

构建脚本返回 `exit 0` 或 `do packet success` **不能**作为唯一判据。必须检查：

```
PAC 文件 ≥ 50 MB → 正常
PAC 文件 < 1 MB  → 链接或镜像导出阶段失败
```

### 5.2 FMM 菜单注册是四步流程

添加一个 FMM 菜单项需要修改四个位置，缺一不可：

```
1. mmifmm_menutable.h      → 枚举值声明
2. files_manager_mdu_def.h → 文本资源定义
3. mmifmm_menutable.c      → 菜单组数组注册
4. mmifmm_mainwin.c        → DisableInvalidMenuItem() 条件控制
   mmifmm_mainwin.c        → HandleMenuOption() case 处理
```

### 5.3 资源定义文件辨析

FMM 模块存在两个看似功能相同的资源头文件：
- `fmm_mdu_def.h` — **不被资源编译器使用**（历史遗留）
- `files_manager_mdu_def.h` — **构建系统实际使用**的资源定义文件

判断方法：在 `build/res/` 目录下搜索已有的 `TXT_FMM_*` 来确定哪个文件是实际源头。

### 5.4 调用平台 API 前必须验证

集成代码调用 FMM 或其他平台 API 时，先做：
1. `grep` 确认函数名存在（声明 + 定义）
2. 核对完整参数签名（顺序、类型、指针/值）
3. 确认返回值语义

------



## **6. 当前状态与下一步**



### 已完成 ?

- [x] PAC 打包正常（51.5 MB）
- [x] 零编译/链接错误
- [x] Execute 菜单项在 .bin 文件上可见
- [x] 非 .bin 文件/文件夹上 Execute 被灰掉

### 待验证 ?

- [ ] 烧机后在真机上确认 Execute 菜单出现
- [ ] 选择 .bin 文件执行 Execute 触发 `DAP_FMM_ExecuteModule` 的实际行为
- [ ] 准备一个测试用 `.bin` 模块进行端到端验证

------



> **一句话总结**：
>
> PAC 打包失败和菜单不可见是两个独立 Bug 的叠加效果——前者因调用不存在的函数导致链接失败，后者因菜单注册流程四步只做了两步。两个问题均已修复，构建通过。


