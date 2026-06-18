# **Technical Memo**

## **任务：Windows 11 环境复现构建、记录构建 Bug（禁止改代码）并输出** docs/Debug 报告





**执行人**：新工程师（Windows 11）

**项目**：NBS_FuturePhone — UNISOC T127 / Mocor BSP + DAP 集成

**目标**：在不修改任何工程代码的前提下，完成一轮全流程编译/打包/模拟器构建，记录所有潜在 bug 与环境问题，并在 docs/ 下产出可复用的 debug README。

**硬约束**：**暂时不要修改任何工程代码**（包括 .c/.h/.mk/.bat/.cmd/.pl/.py 等）。只允许：安装依赖、设置环境变量、执行命令、采集日志、整理文档。



------





## **0. 项目全貌（你必须先理解，避免盲跑）**







### **0.1 DAP 是什么（你在做的“系统能力”是什么）**





DAP（Dynamic App Platform / 动态应用平台）在我们项目里的定位是：



- 一套“**运行时动态加载二进制模块**”的机制（.bin 模块）

- 核心由三部分组成：

  

  1. **Loader**：从存储（内部 FS / 可选 T 卡）读入 .bin 到 RAM，然后执行
  2. **地址重定位（Relocation）**：将模块在编译期假定的地址修正为运行时实际加载地址（这是能否从 FS/SD 执行的生命线）
  3. **API Registry（OS API 注册/查找）**：模块通过字符串/表项找到系统能力（内存/文件/定时器/日志/最小 GUI 等）

  





**重要理解**：



- DAP **不是一个 task**、不是后台服务
- DAP 只有在“入口触发执行”时才工作
- 目前入口是 **FMM 文件管理器菜单**：用户选中 .bin，点“执行”，才会调用 DAP 执行接口







### **0.2 为什么我们要 DAP**





我们历史上直接把应用接在 Mocor BSP 上 bug 很多，且底层不熟导致难以定位。DAP 的目标是：



- 把“应用层”与“BSP/平台层”隔离出一个稳定边界（OSAL/API Registry）
- 让大量应用以 .bin 模块形式迭代（未来可支持热更新/扩展介质）
- 让 MTK / UNISOC / ASR / 自研 OS 具备同一套可复用的 DAP Core 思路







### **0.3 UNISOC T127 / Mocor 平台是什么**





- UNISOC T127 是功能机 SoC，Mocor 是其软件平台/工程体系（RTOS + MMI + 资源系统 + 构建工具链）
- 项目构建入口通常通过 mm <project> new 或 make_cmd\make ... 完成
- 关键特点：构建系统高度依赖 Windows 脚本链、ARMCC 工具链、以及工程自带 make/perl 脚本







### **0.4 DAP 在 UNISOC Mocor 的当前状态（你要验证什么）**





- DAP 已被集成进 Mocor 工程目录并纳入构建

- ENABLE_DAP 总宏用于保证：

  

  - 关闭宏：系统行为与原 Mocor 一致（无副作用）
  - 开启宏：仅在 FMM 菜单触发时，从内部 FS 读取 .bin，执行加载→重定位→BSS 清零→Entry 跳转

  

- 你现在的任务不是验证运行时功能，而是：

  **先确保 Windows 构建链可稳定跑通，并把构建阶段可能出现的 bug 全记录下来**





------





## **1. 你要做的事（任务清单）**







### **1.1 禁止事项（必须遵守）**





- 不要修改任何工程代码/脚本/Makefile（哪怕只改一个空格也不行）

- 不要“为了跑通”去改宏配置、字体配置、资源配置、模块列表等

- 你可以做的只有：

  

  - 安装/配置依赖
  - 执行构建命令
  - 采集日志与截图
  - 整理 debug 文档

  





> 如果你确实发现“必须改代码才能继续”，你也不能改——请把结论写进报告，交给我们评审后决定。





### **1.2 允许事项**





- 配置环境变量（PATH 等）
- 在 Windows 上安装/启用构建依赖（ARMCC、Perl、Python、Git 等，按 BUILD.md 指引）
- 选择一个干净的工作目录（避免路径含中文/空格带来额外噪音）
- 输出日志到 docs/ 下





------





## **2. 你需要准备的环境信息（先记录再开始）**





在开始执行命令前，请先收集并写入 debug 文档：



- Windows 版本（Win11 具体 build）
- CPU/内存
- 工程所在路径（建议：D:\work\NBS_FuturePhone_unisoc_mocor\ 这类无中文无空格路径）
- 当前 shell：**CMD** 还是 PowerShell（建议用 CMD 执行构建）
- ARMCC 版本与安装路径
- make_cmd\make 的实际路径是否存在
- 是否安装 perl（以及 perl -v 输出）
- Git 版本与换行配置（仅记录，不要动仓库文件）





> 这些信息用于区分“环境问题”与“工程问题”。



------





## **3. 执行步骤（必须严格按顺序）**





> 每一步都要：**把完整命令、控制台输出、成功/失败结论**记录到日志中。

> 如失败：记录“第一处错误（first error）”和“后续级联错误”。



------





### **Step 0：创建 debug 输出目录（只新增文件，不动工程）**





在工程根目录下确认/创建：

```
docs/
└── build_debug/
    └── 2026-02-06_win11_engineerX/
        ├── README.md
        ├── logs/
        └── screenshots/
```

> 目录命名规则：日期 + 环境 + 执行人，方便未来横向对比。



------





### **Step 1：重新编译（全量）**





执行：

```
mm ums9117_240X320BAR_64MB_ML new
```

要求记录：



- 命令执行所在目录（pwd）

- 开始/结束时间

- 最终结果（成功/失败）

- 若失败：

  

  - 第一处报错（复制 30~80 行上下文）
  - 常见乱码类报错是否出现（“xxx 不是内部或外部命令”）

  





> 经验：如果出现“乱码命令名”，优先怀疑脚本编码/换行/codepage，但本阶段你只记录，不修。



------





### **Step 2：编译模块（指定 MODULES=app_main）**





执行：

```
make\make_cmd\make -r -R MAKESHELL=CMD p=ums9117_240X320BAR_64MB_ML MODULES=app_main update JOB=16
```

要求记录：



- 是否能进入 make 流程
- project_*.mk 是否能被找到/生成
- 是否出现 “No such file or directory”
- 若失败：第一处错误





> 说明：你也可以把 MODULES=app_main 换成其他模块变量做对照测试，但必须记录你用了什么值、为什么用。



------





### **Step 3：编译资源**





执行：

```
make p=ums9117_240X320BAR_64MB_ML m=resource_main job=16
```

要求记录：



- 资源编译是否成功

- 若失败，记录是：

  

  - 工具缺失（python/perl/java 等）
  - 路径错误
  - 资源冲突（字体/矢量字体校验等）

  





------





### **Step 4：编译模拟器**





执行：

```
make\make_cmd\make ums9117_240X320BAR_64MB_ML msm vs
```

要求记录：



- 模拟器构建是否成功
- 若失败：是 MSVC/VS 环境缺失？还是工程配置错误？





------





### **Step 5：固件打包**





执行：

```
make\make_cmd\make -r -R MAKESHELL=CMD p=ums9117_240X320BAR_64MB_ML image
```

要求记录：



- 产物生成位置
- image 打包成功与否
- 若失败：第一处错误





------





## **4. 记录规范（你必须这样写 README，否则后面没人能复现）**





你最终必须在：



docs/build_debug/2026-02-06_win11_engineerX/README.md



写清楚以下结构（照模板写）：





### **4.1 README 模板（直接照抄填空）**





1. **环境信息**







- OS：
- 工程路径：
- Shell：
- ARMCC：
- Perl：
- 其他依赖：







1. **执行命令与结果总览（表格）**

   | Step | Command | Result | Time | First Error Summary |

   |——|———|––––|——|———————|

   | 1 | mm … new | PASS/FAIL | | |

   | 2 | make … MODULES=app_main update | PASS/FAIL | | |

   | 3 | make … resource_main | PASS/FAIL | | |

   | 4 | make … msm vs | PASS/FAIL | | |

   | 5 | make … image | PASS/FAIL | | |

2. **详细日志索引**







- logs/step1_mm_new.log
- logs/step2_make_update.log
- …







1. **错误分类（必须）**

   把错误按下面分类归档，每类列出证据（日志片段 + 你认为的可能原因）：







- A. 脚本/编码/换行/Codepage（例如“乱码命令名”）
- B. 路径/权限（找不到目录、路径包含空格/中文、访问拒绝）
- C. 依赖缺失（perl/make/ARMCC/VS 等）
- D. Makefile/工程配置（project_*.mk 缺失、变量未生成）
- E. Verify/宏冲突（例如字体 VECTOR 校验）
- F. 其他（单列）







1. **复现要点（给下一个工程师的建议）**







- 必须从哪个目录执行
- 必须用 CMD 还是 PowerShell
- 必须先跑哪条命令







1. **不做修改的原因说明**







- 哪些问题你判断需要改工程代码/脚本才能修，但你没有改（列出）





------





## **5. 你需要特别关注的“高频坑”（只记录，不动手修）**





> 下面这些是我们历史上已经遇到过/高度可疑的点。你看到它们要特别标注。





### **5.1 批处理乱码执行（编码/换行）**





症状：



- set/del/call 变成乱码命令
- 大量 “不是内部或外部命令”





高度怀疑：



- .bat/.cmd 编码（GB18030/GBK vs UTF-8 BOM vs UTF-16）
- CRLF 被改成 LF
- Git 自动换行导致脚本被重写





你需要做的：



- 在 README 的 “A 类” 里记录：出现在哪一步、哪条脚本疑似异常、日志证据







### **5.2** 

### **project_.mk**

###  **或 project 文件缺失**





症状：



- makefile:xx: project_.mk: No such file or directory





高度怀疑：



- 上一步脚本没生成变量/没拷贝模板（多为脚本层失败的级联）
- 工程路径/执行目录不对





你需要做的：



- 标注“是否是级联错误”，并定位第一处真正错误







### **5.3 verify 阶段宏冲突（字体/矢量字体）**





症状：



- Makefile.verify:*** FONT_TYPE_SUPPORT should be VECTOR while VECTOR_FONT_SUPPORT is not NONE





高度怀疑：



- project 配置宏冲突
- 工程默认 feature 配置不一致





你需要做的：



- 把报错原文贴进 README 的 “E 类”
- 记录发生在哪一步（通常 step1/step2/step3 的后段）





------





## **6. 你交付给我们的东西（必须交）**





提交以下内容到 repo（只新增 docs/ 文件，不改工程）：



- docs/build_debug/2026-02-06_win11_engineerX/README.md
- docs/build_debug/2026-02-06_win11_engineerX/logs/*.log
- docs/build_debug/2026-02-06_win11_engineerX/screenshots/*（如有）





------





## **7. 最后强调一次（别走歪）**





- 你现在不是来“修复工程”的，你是来**复现 + 定位 + 记录**
- 任何你认为“应该修改”的点，都先写进 debug README，给我们评审后再决定是否动工程





------





### **你可以现在就开始**





按 Step 1→Step 5 依次执行。每一步的日志都保存到 docs/build_debug/.../logs/ 中。

如果 Step 1 直接出现脚本乱码，先完整记录后再停在那一步，不要继续往下“硬跑”。


