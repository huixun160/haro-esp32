------



**Title:** BIN2 Payload Encryption — Phase-2 Minimum Viable Design and Integration



**Project:** AIOS Feature Phone Platform



**Subsystem:** DAP / Security / BIN2 Loader



**Author:** AIOS Core Architecture



**Priority:** HIGH



**Date:** 2026-03-12



------





## **Background**





TM15–TM27 已经把 BIN2 的基础安全链路跑通，当前系统已经具备：



- BIN1 / BIN2 双栈兼容
- BIN2 签名验证
- 篡改拒绝
- 坏签名拒绝
- Device Binding（绑定到指定设备）
- .bind 文件导出与 PC packer 对接





也就是说，你们现在已经解决了两类问题：



1. **完整性**

   未签名、被篡改的 BIN2 不能运行。

2. **所有权**

   绑定给设备 A 的 BIN2，复制到设备 B 不能运行。





但还没有解决第三类问题：



1. **机密性**

   攻击者仍然可以从 .bin2 文件中提取 payload，做静态分析和逆向工程。





因此，TM28 的目标不是重新设计 BIN2，而是在现有“签名 + 绑定”基础上，增加：

```
payload encryption
```

即把：

```
BIN2 = Signed + Bound
```

升级为：

```
BIN2 = Signed + Bound + Encrypted Payload
```

本阶段必须采用最小可行方案，不碰云端，不做 App Store 集成，不大改 DAP 本体，不引入不必要的协议扩展。



------





## **Objective**





实现 BIN2 payload 加密的最小闭环，并满足以下目标：



1. .bin2 文件中的 payload 不再是明文机器码，不能被直接提取后用 IDA/Ghidra 静态分析。

2. 设备端 loader 在：

   

   - 签名验证通过

   - binding 验证通过

     之后，能够正确解密 payload 并继续执行。

   

3. 对于同设备的合法 device-bound BIN2：

   

   - 能正常解密并运行

   

4. 对于跨设备复制的 BIN2：

   

   - 在 binding check 处拒绝，不进入解密执行

   

5. 对于 tampered / badsig：

   

   - 仍然继续按现有逻辑拒绝

   

6. 加密集成不能破坏当前 Phase-0 / Phase-1 已经跑通的路径。





------





## **Current State**





当前系统已知状态：





### **已完成**





- DeviceSecret 已生成、持久化、可读

- BindingID 已派生、可输出、可导出 .bind

- PC packer 已可读取 .bind

- Loader 已支持：

  

  - BIN2 detect
  - 签名验证
  - binding check
  - payload 执行

  







### **当前缺口**





- BIN2 payload 仍是明文
- 静态提取 .bin2 后，仍然可以对 payload 做反编译分析
- 当前没有 payload 级别的保密性







### **设计前提**





本阶段继续坚持：



- DeviceSecret 不出设备
- .bind 不包含 DeviceSecret
- PC packer 可读取 .bind
- 云端系统暂不参与





------





## **Scope**





本任务包括：



1. 设计并实现 BIN2 payload 加密方案
2. 修改 PC packer，使其在生成 BIN2 时对 payload 加密
3. 修改 device-side loader，使其在验签、验绑通过后解密 payload
4. 设计并实现最小 KDF / key derivation 路径
5. 保持现有 Logel trace 可追踪
6. 完成同设备通过 / 跨设备拒绝 / tamper 拒绝 / badsig 拒绝的验证





------





## **Out of Scope**





本阶段**明确不包括**以下内容：



1. **App Store 云端签名或密钥下发**
2. **云端设备注册 / 账户系统**
3. **DAP 本体混淆、字符串清理、接口 ID 化**
4. **PAC / DAP core blob 保护**
5. **Key rotation / revocation**
6. **文件系统 / 分区隔离**
7. **内部 SDK 暴露面分层**
8. **对外 SDK 自动化裁剪流水线**
9. **新的 bindfile 格式设计**
10. **BIN1 支持移除**





TM28 只解决：



> **如何让 BIN2 payload 在文件中加密，并在设备端正确解密执行。**



------





## **Constraints**





1. **尽量少改协议**

   

   - 不重新翻 BIN2 协议桌子
   - 只做最小增量字段扩展
   - 不破坏现有 header 基础语义

   

2. **不踩历史坑**

   

   - dap.mk 漏加文件
   - SCI_TRACE_LOW / Logel trace 丢失
   - free offset pointer
   - payload offset / BSS / entry 指针错位
   - 签名覆盖范围不一致
   - device_binding.c 与 bin2_loader.c 职责混乱

   

3. **加密顺序必须正确**

   

   - 先构造最终 header / encrypted payload

   - 再按既定规则签名

     不允许“签明文、运行时解密”的混乱路径

   

4. **优先 correctness，不优先性能**

   

   - 可接受增加几十毫秒
   - 不接受协议和执行链不稳定

   

5. **Trace 必须保留**

   

   - payload encryption 相关关键节点必须可在 Logel 中追踪

   





------





## **Expected Deliverables**





1. 更新后的 BIN2 header 定义（最小增量）

2. 更新后的 Python bin2_packer

3. 更新后的 device-side bin2_loader.c

4. 必要时新增 bin2_crypto_payload.c/.h 或等价实现文件

5. 更新后的 dap.mk

6. 一份 AIOS/docs/architecture/bin2_payload_encryption.md

7. 一份验证报告，包含：

   

   - valid encrypted BIN2 on same device → PASS
   - bound encrypted BIN2 on other device → FAIL
   - tampered encrypted BIN2 → FAIL
   - badsig encrypted BIN2 → FAIL

   





------





## **Verification Method**





- **Build verification:**

  DAP 模块编译通过，dap.a 正常生成，无新增 link error

- **Packer verification:**

  bin2_packer 能正确生成带加密 payload 的 BIN2，并能打印 debug/info

- **Device test:**

  

  1. 同机运行 test_valid_bound_enc.bin2 → 成功
  2. 异机运行 test_valid_bound_enc.bin2 → ERR-11 或等价 binding fail
  3. 运行 test_tampered_bound_enc.bin2 → ERR-10 或等价 verify fail
  4. 运行 test_badsig_bound_enc.bin2 → ERR-10

  

- **Log verification:**

  Logel 中必须能看到：

  

  - [bin2] encrypt mode
  - [bin2] verify ok
  - [bind] match ok/fail
  - [bin2] decrypt start
  - [bin2] decrypt ok
  - [bin2] execute

  

- **Regression verification:**

  原有 Phase-0 / Phase-1 样本行为不被破坏





------





## **Potential Risks**





- **Risk 1 — 把签名和加密顺序做反**

  会导致 packer / loader 对 signed region 理解错位。

  **Mitigation:** 先冻结规则，再实现。

- **Risk 2 — 加密后 payload offset 处理错**

  可能导致：

  

  - GetBSSSpace 读取错位

  - TApplication 起点错位

  - entry 跳转非法

    **Mitigation:** 保持“解密后得到标准 BIN1 payload 起点”的原则，不改老 loader 输入语义。

  

- **Risk 3 — 使用 DeviceSecret 直接做不透明加密，导致调试困难**

  **Mitigation:** 先设计明确的 KDF 和 trace，仅打印非敏感摘要。

- **Risk 4 — 内存所有权再次混乱**

  设备端如果解密后引入新的临时 buffer，很容易再次触发 free/assert 问题。

  **Mitigation:** 明确 buffer ownership，优先用单一 full_buf + 就地或明确的新 buffer 模型。

- **Risk 5 — trace 再次失效**

  **Mitigation:** 所有新增日志继续走已验证过的 DAP_DBG → DAP_TracePrint → SCI_TRACE_LOW 路径。





------





## **References**





- TM15 — BIN2 Phase-0 Secure Loader
- TM20 — Logel Trace Fix
- TM21 / TM22 — 签名链与内存问题调试
- TM25 — BindingID Logel Exposure
- TM26 — Bindfile Export
- TM27 — Device-Bound BIN2
- pitfall.md
- memory.md
- Third-party/DAP/security/bin2_loader.c
- Third-party/DAP/security/device_binding.c
- Third-party/DAP/dap.mk





------





## **Design Proposal**







### **1. 加密目标**





加密对象仅为：

```
original BIN1 payload
```

即：

```
[TApplication + code + data + relocation info ...]
```

不加密：



- BIN2 外层 header
- signature
- binding_id





原因：



- loader 必须先读取 header 才能知道如何处理文件
- signature/binding 必须在解密前能校验





------





### **2. 推荐最小方案**







#### **Payload encryption key**



采用设备本地派生密钥。



建议：

```
payload_key = SHA256("AIOS-PAYLOAD-V1" || DeviceSecret || binding_id)[0..15]
```

即：



- 基础材料来自本机 DeviceSecret
- 再混入 binding_id，避免不同协议路径复用同一 key
- 输出 16 bytes，适配最小 AES-128







#### **加密算法**



本阶段建议使用：

```
AES-CTR
```

原因：



- 实现相对简单
- 不需要 padding
- 明文长度保持不变
- 更容易在旧 loader 结构里集成





**注意：**

完整性仍由签名负责，不依赖 CTR 本身提供完整性。



------





### **3. 签名与加密顺序**





必须固定为：





#### **packer 端**





1. 生成原始 BIN1 payload

2. 加密 payload → encrypted_payload

3. 组装完整 BIN2 文件：

   

   - header
   - signature slot（零）
   - encrypted_payload

   

4. 对“完整文件，但 signature 区域清零”做签名

5. 写回 signature







#### **loader 端**





1. detect BIN2
2. verify signature
3. verify binding
4. derive payload_key
5. decrypt payload
6. 将解密后的 payload 当作标准 BIN1 继续走旧路径





------





## **Implementation File Ownership**







### **File A —** 

### **Third-party/DAP/security/bin2_loader.c**





负责：



- header 解析
- signature verify 调度
- binding verify 调度
- decrypt 调度
- 最终把“解密后的 payload”交给老 BIN1 执行链





不负责：



- DeviceSecret 派生细节
- KDF 细节
- payload crypto primitive 实现







### **File B —** 

### **Third-party/DAP/security/device_binding.c**





负责：



- 读取 DeviceSecret
- 派生 BindingID
- 为 payload encryption 提供必要的本机身份材料接口（如果设计需要）





不负责：



- BIN2 header 解析
- payload decrypt 调度







### **File C —** 

### **Third-party/DAP/security/bin2_crypto_payload.c**

### **（建议新增）**





负责：



- payload_key derivation
- AES-CTR encrypt/decrypt primitive 包装
- 只提供简洁接口给 loader







### **File D —** 

### **bin2_format.h**





负责：



- header 结构定义
- binding_mode
- payload_enc_mode
- 偏移和长度常量





------





## **Step-by-Step Execution Plan**







### **Step 1 — 冻结协议最小增量**





在现有 BIN2 header 基础上，只新增加密相关最小字段，例如：



- payload_enc_mode
- payload_iv 或 nonce（如需要）
- 必要时新增 payload_enc_flags





**禁止**顺手重构其它字段。



------





### **Step 2 — 更新 PC packer**





修改 bin2_packer：



1. 支持生成 encrypted payload

2. 支持 --bind-file

3. 在 info --debug 模式下输出：

   

   - binding_mode
   - binding_id
   - payload_enc_mode
   - payload_size
   - header_size
   - signed_region_len

   





------





### **Step 3 — 更新 device loader**





在当前流程中新增：

```
verify signature
→ verify binding
→ decrypt payload
→ execute
```

必须在解密成功后，继续把 payload 作为标准 BIN1 使用。



------





### **Step 4 — 加 trace**





最少新增以下日志：

```
[bin2] tm28_enc_mode=...
[bin2] tm28_verify_ok
[bind] tm28_match_ok
[bin2] tm28_decrypt_start
[bin2] tm28_decrypt_ok
[bin2] tm28_execute
```

禁止输出：



- DeviceSecret
- payload_key 明文
- 完整 payload dump





------





### **Step 5 — 回归测试**





每次改动必须跑：



1. test_original.bin
2. test_valid.bin2
3. test_tampered.bin2
4. test_badsig.bin2





再加新的 encrypted bound 样本。



不要跳过老样本。



------





## **Pitfalls to Review Before Starting**





工程师开工前必须重新阅读：



- pitfall.md
- memory.md





特别回顾以下已发生过的问题：





### **1.** 

### **dap.mk**





新增源文件后未进 dap.mk，会导致：



- dap.a 不生成
- link error
- 伪“代码没问题但系统跑不起来”







### **2. Logel trace 丢失**





之前已经证明：



- 只有走 SCI_TRACE_LOW 那条链，Logel 才稳定可见

  不要重新引入未定义宏或私有 trace 路径。







### **3. free offset pointer**





BIN2 有 full_buf 和 payload_ptr 两个概念。

任何时候只能 free 原始分配的指针。





### **4. Header / payload offset**





不要再次把：



- header_size

- payload_offset

- BSS pointer

- Running_AP

  搞乱。

  加密后尤其容易在这一步重蹈 Phase-0 的坑。







### **5. 过度设计**





本阶段不要引入：



- 云端密钥下发
- 多设备授权
- payload encryption + obfuscation 一起做
- 新 bindfile 格式





------





## **Architecture Documentation Requirement**





必须新增：

```
AIOS/docs/architecture/bin2_payload_encryption.md
```

至少包含：



1. payload encryption 的目标
2. key derivation 规则
3. packer 端顺序
4. loader 端顺序
5. 与 binding 的关系
6. 未来与 App Store 的关系
7. 明确的 Out-of-Scope





------





## **Success Criteria**





本任务完成标准：



1. **功能正确**

   

   - 同设备 test_valid_bound_enc.bin2 可运行
   - 异设备拒绝
   - tampered / badsig 拒绝

   

2. **协议稳定**

   

   - 不破坏现有 BIN2 / bind 流程
   - 不引入新的 header 混乱

   

3. **调试可观测**

   

   - Logel 可见关键 trace

   

4. **工程可持续**

   

   - 文档补齐
   - dap.mk、memory ownership、trace 路径不再踩坑

   





------





## **Final Note**





TM28 是整个安全路线的下一个真正拐点。



TM27 解决的是：

```
谁能运行
```

TM28 解决的是：

```
别人能不能直接看懂
```

做完 TM28 后，你们的 BIN2 才从：

```
Signed + Bound executable
```

进化为：

```
Signed + Bound + Encrypted executable
```

这会显著提高普通攻击者和厂商的静态逆向成本。