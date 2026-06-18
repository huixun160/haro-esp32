# **Technical Memo3 — Windows11 环境修复构建脚本/资源生成链路并完成复测（DAP-on-UNISOC 项目）**





**面向对象**：新工程师（Windows 11），负责“修复构建相关 Bug + 复测 + 产出可复现证据”

**项目**：NBS_FuturePhone_unisoc_mocor（UNISOC T127 / Mocor BSP + DAP 集成）

**核心约束（第一性原理）**：



- 现在系统无法稳定构建，不谈功能对错；先把**构建链路恢复为确定性、可复现、可审计**。
- 这轮只修复**构建系统/脚本/资源工具链问题**，不碰业务逻辑；DAP 功能验证放在构建稳定之后。
- 你必须产出：**修复点清单 + Patch/修改列表 + 新一轮 README + 全部 log**，让任何人按文档可复现。





------





## **0. 已知问题（来自现有 Debug Report 与日志）**





已知阻塞项如下（你要逐个清掉）：



1. **A 类（最高优先级）**：mm.bat 使用 LF 换行导致脚本被 CMD 解释成乱码、变量赋值失败、project_*.mk 生成失败，继而引发级联错误（如 project_.mk 缺失、verify 宏检查异常）。





> 该类问题会让 Step1/Step4 直接失效，且会污染后续所有结果（属于“根因级”）。【 】





1. **B 类（高优先级）**：tmp/config_nv/ 未创建，ARMCC 无法写 NV 预处理输出（cannot open preprocessing output file ... tmp/config_nv/app_main.nv）。





> 这是一个明确的“构建系统缺 mkdir”的问题，不是代码逻辑问题。





1. **C 类（中优先级）**：tidy_xrm.pl 第 279 行解析资源宏时报语法错，触发 Generate xrm file ... failed。





> 大概率是 Perl 解析规则对资源宏格式过于严格，或资源定义行存在不符合规范的写法（比如换行/逗号/括号/引号/路径）。Mocor 资源宏 RES_ADD_IMG(...) 的期望格式可参考开发指南示例。【 】





1. **E 类（低优先级，可能是级联）**：FONT_TYPE_SUPPORT / VECTOR_FONT_SUPPORT 宏冲突触发 verify stop。





> 在 mm.bat 修好之前不要“盲改宏”，因为变量/配置未正确生成时宏检查结果不可信。【 】



------





## **1. 你的任务目标（必须达成）**







### **1.1 目标**





- 修复构建系统 Bug，使下列命令能在 **cmd.exe** 下按顺序执行，且结果一致、可复现：



```
mm ums9117_240X320BAR_64MB_ML new

make\make_cmd\make -r -R MAKESHELL=CMD p=ums9117_240X320BAR_64MB_ML MODULES=app_main update JOB=16

make p=ums9117_240X320BAR_64MB_ML m=resource_main job=16

mm ums9117_240X320BAR_64MB_ML msm vs

make\make_cmd\make -r -R MAKESHELL=CMD p=ums9117_240X320BAR_64MB_ML image
```

> 注：BUILD.md 里说明了构建系统由 GNU Make + Perl + ARMCC 组成，并依赖 project_*.mk 等项目配置生成物。【 】





### **1.2 交付物（强制）**





在仓库 docs/ 下新增目录（按日期命名）：



- docs/build_debug/2026-02-XX_win11_<yourname>/README.md
- docs/build_debug/2026-02-XX_win11_<yourname>/logs/step1_*.log ... step5_*.log
- docs/build_debug/2026-02-XX_win11_<yourname>/patch_list.md（你改了哪些文件、每个改动的理由、回滚方式）





README 必须包含：



- 环境信息（OS、ARMCC、Perl、路径、shell）
- 执行命令原文（逐条）
- 每一步结果（PASS/FAIL）
- 若 FAIL：第一错误位置（文件+行号+关键报错）





------





## **2. 修复优先级与执行步骤（照做，不要自由发挥）**







### **Step A（必须先做）：修复** 

### **mm.bat**

###  **的 CRLF + 防止未来再次被改成 LF**





**目的**：先让 mm 可用、能生成正确的 project_*.mk，否则后面都是噪音。

mm.bat LF 会导致 CMD 解析出类似 new"=="new"、变量赋值失败、project_.mk 缺失等典型错误。【 】



**操作**（二选一，推荐 1）：



1）**直接把 mm.bat 转成 CRLF**



- 用 VSCode 打开 mm.bat
- 右下角将 LF 改为 CRLF
- 保存
- 再次打开确认仍为 CRLF





2）命令行方式（可选）



- 若你装了 Git Bash：unix2dos mm.bat
- 或用 PowerShell/工具批量修复（仅限脚本文件）





**防复发（必须做，否则下次又炸）**：



- 在 repo 根目录添加/更新 .gitattributes（只针对脚本类文件强制 CRLF）：

  

  - *.bat text eol=crlf
  - *.cmd text eol=crlf

  

- 在你的 README 里记录：本次修复包含 .gitattributes，并解释原因（Windows 构建依赖 CMD 解释）。





**验证**：



- 只跑：mm ums9117_240X320BAR_64MB_ML new
- 预期：不再出现“乱码 set/perl 变形/变量不生效”，并能生成 project_ums9117_240X320BAR_64MB_ML.mk 或等价项目配置文件。





------





### **Step B：修复** 

### **tmp/config_nv/**

###  **目录缺失导致 NV 预处理输出失败**





**现象**：armcc cannot open preprocessing output file ... tmp/config_nv/app_main.nv（目录不存在）。

这属于“构建系统未创建输出目录”。



**你要做的事**：找到“armcc 产生 NV 预处理输出文件”的那段 Makefile/Perl 脚本逻辑，在写入前插入 mkdir（若已存在则不报错）。



**建议定位法**：



- 全仓搜索：config_nv、app_main.nv、#2917、preprocessing output file
- 你会找到对应规则在某个 Makefile.* 或 make/perl_script/*.pl





**实现要求**：



- 必须是 Windows CMD 可用的创建目录方式（例如 if not exist "<dir>" mkdir "<dir>"）。
- 不允许把路径写死到某个人目录。
- 修改要最小化，不要顺手“重构构建系统”。





**验证**：



- 跑：make\make_cmd\make ... MODULES=app_main update JOB=16
- 预期：NV 预处理步骤不再因目录缺失失败，并能继续往下跑（即使后续还有别的错误）。





------





### **Step C：修复** 

### **tidy_xrm.pl**

###  **解析** 

### **RES_ADD_IMG(IMAGE_FMM_FILE_UDISK_ICON, ...)**

###  **语法错误**





**现象**：Perl 报 syntax error at tidy_xrm.pl line 279，并在解析 RES_ADD_IMG(IMAGE_FMM_FILE_UDISK_ICON, ... 时失败。

这通常是两类根因之一：



- **根因 1：资源定义文件写法不符合解析器期望**（例如：宏参数跨行、缺右括号、引号转义、逗号、路径中反斜杠写法异常）。
- **根因 2：tidy_xrm.pl 的正则/解析规则太脆弱**，遇到某些合法写法却 parse 不过去。





**先按“最小改动原则”排查顺序**：



1）**优先检查资源定义文件（不要先改 Perl）**



- 日志里提示 files_manager_mdu_def.h（或相邻文件）生成失败（从 log 定位实际路径）

- 打开对应 .h，找到 IMAGE_FMM_FILE_UDISK_ICON 那一行，检查是否满足 Mocor 资源宏常见格式（单行、括号配对、字符串路径带引号）。

  Mocor 开发指南里 RES_ADD_IMG 示例是单行完整宏调用，包含图片 ID、路径、压缩格式等参数。【 】





2）若资源定义看起来没问题，再改 tidy_xrm.pl



- 打开 make/perl_script/tidy_xrm.pl，定位第 279 行附近逻辑

- 把“触发语法错误的输入行”在 README 里摘出来（不要超过几行），说明它为什么会触发解析 bug

- 修改解析逻辑时遵守：

  

  - **兼容旧格式**（不能让别的资源宏解析坏）
  - 增量改动：只让这类 RES_ADD_IMG(...) 能过

  





**验证**：



- 跑：make p=ums9117_240X320BAR_64MB_ML m=resource_main job=16
- 预期：资源生成脚本通过，能继续生成资源产物（哪怕后面 verify 还会拦）。





------





### **Step D：处理** 

### **FONT_TYPE_SUPPORT / VECTOR_FONT_SUPPORT**

###  **宏冲突（最后做）**





**原因**：它可能是 mm.bat 失败导致 project_*.mk/配置没正确生成后的“假冲突”。【 】



**动作**：



- 在 A/B/C 都解决后，重新跑 mm ... new + mm ... msm vs 看是否仍报：

  

  - Makefile.verify:600: *** FONT_TYPE_SUPPORT should be VECTOR while VECTOR_FONT_SUPPORT is not NONE. Stop.【 】

  





若仍报错：



- 定位宏来源：通常在 project_*.mk、平台配置头文件或资源/字体配置文件

- 输出一个“宏链路证明”到 patch_list.md：

  

  - 宏在哪里被定义（文件+行号）
  - 为什么会冲突（期望值 vs 实际值）
  - 你准备如何修改（只改一个地方，避免多点定义）

  

- 修改后复测 Step1/Step4。





------





## **3. 复测流程（修完一个类别就复测一轮）**





你必须按以下“递进式”复测，避免一次跑五步导致看不清根因：



1. 只跑 Step1：mm ... new（验证 mm.bat）
2. 跑 Step2：make ... MODULES=app_main update（验证 config_nv）
3. 跑 Step3：make ... m=resource_main（验证 tidy_xrm）
4. 跑 Step4：mm ... msm vs（再次验证 mm + verify 宏）
5. 跑 Step5：make ... image（验证最终打包链路）





每一步都要保存 log（stdout+stderr），文件名固定：



- step1_mm_new.log
- step2_make_update.log
- step3_resource_main.log
- step4_msm_vs.log
- step5_make_image.log





并在 README 里对照写明：每一步“第一错误”的文件+行号+关键报错。



------





## **4. DAP 项目背景（你只需要知道到这个程度，避免跑偏）**





- DAP Loader 的运行路径是通过 **FMM 传入完整路径**来打开 .bin 并加载执行（不是凭空从某个固定路径扫出来）。README 里写明了“打开文件（使用 FMM 传入的完整路径）→ 读入内存 → BSS 清零 → 跳转入口”等流程。【 】
- 当前阶段你先别碰 DAP 功能；你这轮目标是让“构建系统可用”，否则连 DAP 都编不进去。





------





## **5. 你可以改哪些文件？不可以改哪些文件？**





**允许修改（本 memo 授权范围）**：



- 构建脚本：*.bat / *.cmd
- 构建系统：Makefile* / make/**
- 资源生成脚本：make/perl_script/*.pl
- 资源定义（若确认是资源定义格式问题）：*_mdu_def.h 等





**禁止修改**：



- 业务功能代码（MMI/DAP/驱动逻辑等），除非你的修改是“为了让它能编译通过”且你能证明这是构建输入错误（比如编码/换行导致的宏断行）。
- 任何“顺手重构”。





------





## **6. 最终验收标准（这轮就按这个收）**





1. cmd.exe 下 5 步都能跑完（允许有 warning，不允许 build 被 stop）。

2. docs/build_debug/2026-02-XX_win11_<yourname>/ 下有 README + 5 份 log + patch_list。

3. patch_list.md 能让另一个工程师在 30 分钟内复现你的修复（包括“为什么改、改哪里、怎么回滚”）。

4. 你在 README 里明确说明：

   

   - 哪些问题是根因（A/B/C）
   - 哪些是级联（如 verify 宏冲突可能级联）
   - 每个问题的“复现命令”与“修复后对比证据”。

   





------





## **7. 你开始干活前的“第一条命令”**





从项目根目录打开项目自带 cmd.exe（不是 PowerShell），然后：



1. 先把 mm.bat 修为 CRLF
2. 只跑：



```
mm ums9117_240X320BAR_64MB_ML new
```

**这一步过了，你再继续后面。**



------




