

------





# **Technical Memo**







## **DAP-on-UNISOC（T127 / Mocor）— ENABLE_DAP=TRUE 编译验证与问题收敛**





**版本**：Verification v1

**对象**：Windows 11 工程师（已完成上一轮修复）

**目标**：验证「DAP Shim + Loader + FMM 集成」在 **开启 DAP 宏** 情况下是否 **可完整编译、可链接、行为可解释**

**原则**：



- 本轮 **只验证、不扩展功能**
- **DAP 开关必须开启**
- 不允许“边验证边大改设计”，所有问题先记录、分类、再决策





------





## **0. 当前状态确认（执行前必须对齐）**





在你开始之前，请逐条确认并在 README 中写明结果：



1. 使用 **Windows 11 + cmd.exe**（不是 PowerShell）

2. 构建脚本状态：

   

   - mm.bat 为 **CRLF**
   - .gitattributes 已约束 .bat/.cmd 为 CRLF

   

3. **DAP 宏开启**：



```
ENABLE_DAP = TRUE
```



1. 位于：project_ums9117_240X320BAR_64MB_ML.mk

2. 当前 DAP 结构版本为 **v2.1**（含 shim / gui 封装 / dap.mk）

3. 上一轮已知结论：

   

   - 不开 DAP：全工程可稳定编译（baseline OK）
   - 开 DAP：**DAP library 是唯一剩余不确定模块**

   





> 如果以上任意一条不成立，**不要开始本轮验证**。



------





## **1. 本轮验证目标（非常具体）**







### **1.1 核心目标**





在 ENABLE_DAP=TRUE 情况下：



- ? DAP module 被编译进固件

- ? DAP core + platform/unisoc **能完整编译并链接**

- ? 允许存在 *运行期风险*（例如 API 未覆盖），但：

  

  - **不允许存在未定义符号**
  - **不允许存在编译期错误**

  







### **1.2 非目标（本轮不要做）**





- ? 不新增 API
- ? 不扩展 DAP 功能
- ? 不重构 DAP core
- ? 不修改非 DAP 业务代码





------





## **2. 执行方式（严格按顺序）**







### **Step 1 — 干净构建（DAP=ON）**



```
mm ums9117_240X320BAR_64MB_ML new
```

**目的**：



- 验证 ENABLE_DAP=TRUE 情况下，project / module / dap.mk 的整体拼装是否正确





**你要记录**：



- 是否成功生成 project_*.mk
- 是否进入 dap.mk 编译分支
- 是否开始编译 DAP/core 与 DAP/platform/unisoc





**产出 log**：

step1_mm_new_dap_on.log



------





### **Step 2 — 模块级编译（聚焦 DAP library）**



```
make\make_cmd\make -r -R MAKESHELL=CMD ^
  p=ums9117_240X320BAR_64MB_ML ^
  MODULES=app_main ^
  update JOB=16
```

**目的**：



- 这是 **DAP library 最容易暴露问题的一步**

- 关注点只有一个：

  ?? **DAP 是否能作为一个 library 被 app_main 正常链接**





**重点关注**：



- Undefined reference
- Multiple definition
- Missing type / macro
- Include 顺序问题





**产出 log**：

step2_make_update_dap_on.log



------





### **Step 3 — 资源编译（确认 DAP 不再污染资源链）**



```
make p=ums9117_240X320BAR_64MB_ML m=resource_main job=16
```

**目的**：



- 验证 DAP 引入的宏 / include **没有破坏原有资源系统**
- 确认 tidy_xrm / 字体 / 图片链路稳定





**产出 log**：

step3_resource_main_dap_on.log



------





### **Step 4 — 模拟器构建（验证 verify + 宏一致性）**



```
mm ums9117_240X320BAR_64MB_ML msm vs
```

**目的**：



- 这是 **宏一致性与 verify 最容易暴露问题的一步**

- 特别关注：

  

  - FONT_TYPE_SUPPORT
  - VECTOR_FONT_SUPPORT
  - 是否仍有 verify stop

  





**产出 log**：

step4_msm_vs_dap_on.log



------





### **Step 5 — 镜像打包（最终闭环）**



```
make\make_cmd\make -r -R MAKESHELL=CMD ^
  p=ums9117_240X320BAR_64MB_ML image
```

**目的**：



- 验证 DAP 能被完整打进最终固件
- 不要求功能可用，但要求 **打包成功**





**产出 log**：

step5_make_image_dap_on.log



------





## **3. Bug 记录与分类规范（非常重要）**







### **3.1 你必须使用** 

### **dap.log**





- 若出现 DAP 相关错误，请：

  

  - **优先看 dap.log**

  - 记录：

    

    - 文件名
    - 行号
    - 缺失符号 / 冲突类型

    

  







### **3.2 Bug 分类（按这个来，不要混）**





在 README 中，每个问题必须归类为以下之一：

| **类别**      | **含义**                       |
| ------------- | ------------------------------ |
| HAL 缺失      | OS 常量 / typedef / 基础能力缺 |
| Shim 映射错误 | shim.h/c 映射不完整或语义不符  |
| Include 污染  | 头文件顺序 / 重复 typedef      |
| Link 缺失     | 文件未编进库 / 宏裁剪错误      |
| 级联错误      | 由前置失败引发的假错误         |

> **不要直接“顺手修”**

> 先记录 → 分类 → 再决定是否进入下一轮修复



------





## **4. 交付物（强制）**





在仓库中新增：

```
docs/dap_verify/2026-02-XX_win11_<yourname>/
├── README.md
├── dap.log
└── logs/
    ├── step1_mm_new_dap_on.log
    ├── step2_make_update_dap_on.log
    ├── step3_resource_main_dap_on.log
    ├── step4_msm_vs_dap_on.log
    └── step5_make_image_dap_on.log
```



### **README.md 必须包含：**





1. **环境信息**

   

   - OS / ARMCC / Perl / 路径

   

2. **DAP 开关状态证明**

   

   - project_*.mk 中 ENABLE_DAP=TRUE 的截图或摘录

   

3. **五步执行结果表**



| **Step** | **Command** | **PASS / FAIL** | **First Error** |
| -------- | ----------- | --------------- | --------------- |
|          |             |                 |                 |



1. **问题清单**

   

   - 每个问题：文件 + 行号 + 错误信息 + 分类

   

2. **结论**

   

   - DAP 是否已达到：

     

     - 可编译
     - 可链接
     - 可打包
     - 仍阻塞在哪一层

     

   





------





## **5. 验收标准（本轮）**





- ? ENABLE_DAP=TRUE 情况下，**DAP library 不再是“编译期黑箱”**

- ? 所有失败点都有：

  

  - 明确 log
  - 明确文件/行号
  - 明确分类

  

- ? 不要求 DAP 运行成功

- ? 不要求 API 全覆盖





------





## **6. 下一步（你不用现在做）**





等你提交本轮验证结果后，我们再决定：



- 是继续 **补齐 Shim（Option A 深化）**
- 还是对 **DAP core 做结构性调整（Option B）**





这一步 **现在不要提前做判断**。



------





### **一句话总结给工程师**





> **这轮不是“修到能跑功能”，而是“修到问题可枚举、可解释、可收敛”。**

> **DAP 开关必须开着，所有失败都要留下证据，而不是被修掉。**




