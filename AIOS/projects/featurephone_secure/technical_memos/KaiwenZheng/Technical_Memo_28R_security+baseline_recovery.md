

# **Technical Memo**





**Title:** TM28-R — Security Baseline Recovery After Repository Overwrite



**Project:** AIOS Feature Phone Platform



**Subsystem:** Security / DAP / Build / System Integration



**Author:** AIOS Security Team



**Priority:** **CRITICAL**



**Date:** 2026-03-15



------





# **1 Background**





在 TM28（BIN2 Payload Encryption）完成后，代码库发生了一次**非安全覆盖事故**：



- 同事在拷贝工作目录时使用了**相同文件夹名称**
- 目录级覆盖导致部分模块被旧版本替换
- 当前仓库中存在 **安全版本与旧版本混杂的状态**





具体表现：



- security/ 目录部分文件仍然存在
- DAP/ 和 MMI/ 部分模块被旧版覆盖
- TM28 相关代码（AES、payload crypto、loader 修改等）可能部分丢失
- TM27 压缩包仍然存在
- technical memo、pitfall、feedback 文档仍然存在





当前代码库 **无法被视为可信基线**。



继续在该仓库上开发 TM29 将带来严重风险：



- 安全逻辑可能缺失
- header / loader 不一致
- build 成功但安全功能失效





因此必须执行 **TM28-R：安全基线恢复任务**。



------





# **2 Objectives**





本 memo 的目标：



1. **冻结事故现场**
2. **评估 TM28 代码损失**
3. **以 TM27 压缩包作为 clean baseline**
4. **重建 TM28 功能**
5. **重新验证 BIN3 加密执行能力**





最终结果：

```
TM27 baseline
     +
TM28 encryption
     =
可信代码基线
```

恢复完成后才能继续 TM29。



------





# **3 Recovery Strategy**





恢复原则：





### **1 不以当前仓库为基线**





当前仓库可能包含：



- 混合版本
- 覆盖代码
- 不一致 header





因此 **不可直接修补当前仓库**。



------





### **2 以 TM27 为可信基线**





TM27 压缩包是：

```
最后一个可信安全版本
```

恢复流程：

```
TM27 clean
   +
recover TM28 files
   =
TM28 restored
```



------





### **3 仅进行文件级恢复**





禁止：

```
整目录复制
```

必须：

```
文件级 cherry-pick
```

否则会再次污染代码库。



------





# **4 Phase A — 事故现场冻结**





工程师必须执行以下步骤：





### **Step 1**





复制当前工作目录：

```
zkwwork
```

到：

```
zkwwork_contaminated_snapshot
```

注意：



- 该目录 **只读**
- 不允许修改
- 用于后续差异分析





------





### **Step 2**





记录以下信息：



- 当前目录 commit / build 状态
- 最近一次成功编译时间
- 当前 loader 行为





------





# **5 Phase B — 建立 Clean Baseline**







### **Step 1**





解压 TM27 压缩包：

```
zkwwork_tm27_clean
```

该目录作为：

```
新的开发基线
```



------





### **Step 2**





验证 TM27 baseline：



工程师必须确认：



- 能正常编译
- loader 能运行 BIN2
- 所有 TM27 测试通过





若 TM27 baseline 无法 build，则必须先修复。



------





# **6 Phase C — TM28 功能识别**





根据 TM28 feedback，TM28 完成的功能包括： 





### **1 BIN2 v3 Header**





新增字段：

```
payload_enc_mode
payload_iv[16]
reserved2[16]
```

header size：

```
96 bytes
```



------





### **2 AES-128-CTR 加密实现**





新增文件：

```
dap_aes.c
dap_aes.h
```

来源：

```
tiny-AES-c port
```



------





### **3 Payload Crypto Wrapper**





新增模块：

```
bin2_crypto_payload.c
```

功能：

```
KDF
payload decrypt
```



------





### **4 Loader 更新**





文件：

```
bin2_loader.c
```

新增能力：

```
v2 / v3 backward compatibility
payload decrypt
```



------





### **5 Packer 更新**





工具：

```
bin2_pack.py
```

新增参数：

```
--encrypt
```



------





### **6 AES CTR Test**





测试文件：

```
test_aes_ctr_kat.py
```

用于验证：

```
NIST SP800-38A
```



------





# **7 Phase D — TM28 文件恢复**





工程师需要：



从

```
zkwwork_contaminated_snapshot
```

中逐个恢复 TM28 文件。



推荐恢复顺序：





### **Step 1**





恢复 crypto 模块：

```
security/dap_aes.c
security/dap_aes.h
security/bin2_crypto_payload.c
```



------





### **Step 2**





恢复 header 定义：

```
bin2_format.h
```

确认：

```
BIN2_HEADER_SIZE = 96
```



------





### **Step 3**





恢复 loader 更新：

```
bin2_loader.c
```

确认存在：

```
payload decrypt logic
```



------





### **Step 4**





恢复 packer：

```
tools/bin2_pack.py
```

确认存在：

```
--encrypt flag
```



------





### **Step 5**





恢复测试脚本：

```
test_aes_ctr_kat.py
```



------





### **Step 6**





每恢复一个模块必须：

```
build
run
verify
```

禁止一次性恢复全部代码。



------





# **8 Phase E — TM28 回归验证**





恢复完成后必须重新执行 TM28 测试。



至少包括：





### **Test 1**





普通 BIN

```
test_original.bin
```



------





### **Test 2**





普通 BIN2

```
test_valid.bin2
```



------





### **Test 3**





签名篡改

```
test_badsig.bin2
```



------





### **Test 4**





绑定 BIN2

```
test_valid_bound.bin2
```



------





### **Test 5**





加密 BIN3

```
test_valid_bound_enc.bin3
```

验证：

```
device decrypt → execute
```



------





# **9 Pitfalls**





工程师需要注意以下历史问题。



------





### **Pitfall 1**





之前存在：

```
BIN2_HEADER_SIZE hardcode
```

应改为：

```
header->header_size
```



------





### **Pitfall 2**





DAP_ReleaseAP 偏移问题



必须使用：

```
bin2_get_payload_offset_from_buffer()
```



------





### **Pitfall 3**





cache flush



ARM I-cache 需要 flush。



------





### **Pitfall 4**





debug trace



必须检查：

```
tm28_DEBUG_secret
```

该 trace 必须在后续阶段删除。 



------





# **10 Deliverables**





工程师需要提交：





### **1 Recovery Report**





内容包括：



- TM28 文件恢复列表
- 丢失模块
- 恢复来源





------





### **2 Diff Report**





比较：

```
TM27 baseline
vs
TM28 restored
```



------





### **3 Build Verification**





提交：

```
build log
test results
```



------





# **11 Success Criteria**





当满足以下条件时，TM28-R 完成：



1. TM27 baseline build 成功
2. TM28 crypto 功能恢复
3. .bin3 可以正常运行
4. 所有回归测试通过





------





# **12 Next Phase**





完成 TM28-R 后，项目继续：

```
TM29
Voice Assistant BIN3 Integration
```



