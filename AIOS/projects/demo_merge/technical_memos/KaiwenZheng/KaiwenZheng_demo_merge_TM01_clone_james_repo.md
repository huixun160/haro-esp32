# **Technical Memo 1 — Clone James GitLab Repository into Isolated Legacy Workspace**





**Title:** Clone James GitLab Repository into Isolated Legacy Workspace



**Project:** AIOS Feature Phone Platform



**Subsystem:** Build / Source Control / Legacy Integration



**Author:** [Engineer name]



**Priority:** HIGH



**Date:** [YYYY-MM-DD]



------





## **Background**





我们当前已经完成了功能机安全版本的主线工作，包括：



- BIN / BIN2 等可执行链路
- ABI 冻结
- 安全相关加固与对外交付版本构建能力





现在出现一个紧急业务需求：



> 需要将 James 开发的 demo 版本（不带 secure 相关 feature）整合进入我们的安全版本，最终输出一个可对外演示的 PAC 包。



但当前阶段**不做修 bug**，也**不做功能重构**。

本阶段唯一任务是：



> **安全地获取 James 的完整代码快照，放入隔离目录，供后续分析和合并使用。**



------





## **Problem Statement**





历史上已经发生过严重事故：



- 直接把 James 的项目“安全插入”到当前项目根目录
- 导致大量文件被覆盖
- 例如：dap_loader 被 James 版本覆盖
- 当前 git 信息也曾被覆盖和删除





这类事故的本质不是“操作失误”，而是：



> **没有把 legacy 代码与当前主线物理隔离。**



因此，这次必须遵守一个硬规则：



> **James 的代码必须单独 clone 到 zkw_legacy_code 目录，绝不进入当前工程根目录，也绝不覆盖当前 git。**



------





## **Objective**





本任务的目标是：



1. 从 James 的 GitLab 仓库完整拉取一份代码
2. 将其放在独立目录 zkw_legacy_code
3. 不覆盖、不修改、不污染当前项目
4. 保留 James 仓库自己的 .git
5. 不将 zkw_legacy_code 嵌入当前主线 git 管理
6. 为 TM2 的系统性分析与资产梳理提供输入





------





## **Scope**





本任务包括：



- 创建隔离目录
- 从 GitLab clone James 仓库
- 验证 clone 成功
- 验证当前主线未被影响
- 记录本次获取的 commit / branch / remote 信息





------





## **Out of Scope**





本任务明确不包括：



- 不分析 James 代码内容
- 不比较 James 与当前主线差异
- 不合并任何文件
- 不复制任何文件到当前工程目录
- 不修改当前项目 git
- 不修复 James 工程的任何 bug
- 不进行编译
- 不进行烧录





------





## **Source Repository**





参考地址：





### **SSH**



```
git@192.168.0.92:feature-phone/UMS9117_BSP.git
```



### **HTTP**



```
http://192.168.0.92/feature-phone/UMS9117_BSP.git
```

优先使用 SSH；如 SSH 不通，再使用 HTTP。



------





## **Directory Policy**





必须遵守以下目录规则：





### **当前主线目录**



```
[CURRENT_PROJECT_ROOT]
```



### **James legacy 目录**



```
[CURRENT_PROJECT_ROOT]/../zkw_legacy_code
```

或：

```
[SAFE_PARENT_DIR]/zkw_legacy_code
```

关键要求：



> **zkw_legacy_code 不能创建在当前项目根目录内部。**



也就是说：





### **允许**



```
/workspace/current_project
/workspace/zkw_legacy_code
```



### **禁止**



```
/workspace/current_project/zkw_legacy_code
```

原因：



- 防止误复制
- 防止 IDE / build 脚本误扫描
- 防止 git 误纳入
- 防止再次发生目录级覆盖事故





------





## **Constraints**





1. **绝不在当前工程根目录执行 clone**
2. **绝不把 James 代码 merge / copy 到当前项目**
3. **绝不删除或覆盖当前主线** **.git**
4. **绝不把** **zkw_legacy_code** **加入当前主线仓库**
5. **clone 完成后只做只读检查**
6. **如目录已存在，不允许直接覆盖，必须先备份或改名处理**





------





## **Pre-Execution Checklist**





执行前工程师必须确认：



- 当前主线工程路径已确认
- pwd 输出已截图/记录
- 当前主线 .git 存在且正常
- zkw_legacy_code 目标目录不在当前主线内部
- 没有在当前工程根目录执行任何 clone 命令





------





## **Execution Steps**







### **Step 1 — 确认当前工程根目录**





执行：

```
pwd
git rev-parse --show-toplevel
```

记录当前主线路径。



------





### **Step 2 — 在安全父目录创建隔离目录**





建议在当前工程同级目录创建：

```
mkdir -p ../zkw_legacy_code
cd ../zkw_legacy_code
```

再次执行：

```
pwd
```

确认当前目录不是主线目录内部。



------





### **Step 3 — 检查目录是否为空**





执行：

```
ls -la
```

如果目录非空：



- 不允许直接覆盖

- 必须先改名或新建新目录，例如：

  

  - zkw_legacy_code_james_YYYYMMDD

  





------





### **Step 4 — Clone James 仓库**





优先尝试 SSH：

```
git clone git@192.168.0.92:feature-phone/UMS9117_BSP.git
```

如果 SSH 失败，再尝试 HTTP：

```
git clone http://192.168.0.92/feature-phone/UMS9117_BSP.git
```



------





### **Step 5 — 进入 James 仓库并记录信息**





执行：

```
cd UMS9117_BSP
git remote -v
git branch
git rev-parse HEAD
```

记录：



- remote 地址
- 当前 branch
- 当前 commit hash





------





### **Step 6 — 验证当前主线未受影响**





回到当前主线目录，执行：

```
cd [CURRENT_PROJECT_ROOT]
git status
git rev-parse --show-toplevel
```

确认：



- 当前主线 git 正常
- 无异常覆盖
- 无新增 legacy 文件进入主线





------





## **Expected Deliverables**







### **Deliverable 1 — Legacy Workspace**





一个完整独立的目录：

```
zkw_legacy_code/UMS9117_BSP
```



### **Deliverable 2 — Retrieval Record**





文件建议：

```
AIOS/feedback/TM-001-james-clone-record.md
```

内容至少包括：



- 当前主线路径
- legacy 路径
- clone 使用的地址（SSH / HTTP）
- branch
- commit hash
- clone 是否成功
- 当前主线是否保持干净







### **Deliverable 3 — Safety Verification**





文件建议：

```
AIOS/feedback/TM-001-safety-check.md
```

内容包括：



- 当前主线 .git 是否仍正常
- 当前主线 git status 是否正常
- zkw_legacy_code 是否确实位于主线外部





------





## **Validation Criteria**





任务完成必须满足：



- James 仓库已成功 clone
- clone 在隔离目录完成
- 当前主线目录无任何覆盖
- 当前主线 .git 未受影响
- 已记录 branch / commit / remote
- 未发生任何 merge / copy / overwrite





------





## **Failure Conditions**





以下任一情况视为失败，必须立即停止并上报：



1. 在当前主线根目录执行了 clone
2. zkw_legacy_code 被创建在主线目录内部
3. 当前主线 .git 被改动或丢失
4. James 代码被复制进入主线
5. 当前主线出现大量异常文件变更





------





## **Rollback Plan**





如果误操作发生：



1. 立即停止所有复制/移动操作
2. 记录当前目录结构与 git status
3. 备份事故现场
4. 不允许继续手工修补
5. 先提交事故说明，再单独立项恢复





------





## **Notes**





本阶段只解决一个问题：



> **把 James 的代码安全地取下来，并且与当前主线物理隔离。**



不要在这一步“顺手”做任何分析、拷贝、对比、合并。

TM2 才是系统分析 James 代码资产的阶段。



------



