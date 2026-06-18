# TM-031 Clarification Questions

**Memo:** TM31 — External Deliverable Packaging (zkw_output Blackbox Generation)
**Date:** 2026-03-19
**Output Dir:** `zkw_output_pac_code/` (已存在)

> 以下问题基于 Memo 内容 + `dap.mk` 分析 + TM-030 经验。请逐条回答。

---

## Q1. DAP 内部编译方式：预编译库 vs 直接源码编译

**现状：** `dap.mk` 将 DAP 所有 `.c` 文件（20+ 个）直接编入 PAC 固件。没有中间 `.a` 库。

**Memo 要求：** 生成 `libdap.a`（预编译库）并 strip 符号。

**问题：** 当前 PAC 编译走的是 Unisoc 的 `mm.bat` 系统，它用的是 Unisoc 自带的 ARM 编译器（不是 DS-5）。生成 `libdap.a` 有两种方式：

- **(A)** 在 PAC 编译流程中拦截 DAP 的 `.o` 文件，用 `armar` 打包成 `.a`，然后在 `zkw_output` 中用 `.a` 替代 `.c` 源码
- **(B)** 不做 `.a`：直接在 `zkw_output` 的 `dap.mk` 中删除 SOURCES 行（即不编译 DAP 源码），因为 DAP 代码已经编进 PAC 了。`zkw_output` 只需要包含 PAC + SDK + demo APP 构建脚本
- **(C)** 不改变 PAC 编译流程，只确保 `zkw_output` 中不存在 DAP 源码。PAC 从 internal 编译后直接复制过来

**你选哪个？**

---

## Q2. `zkw_output_pac_code` 的用途

**关键问题：** `zkw_output_pac_code` 是给谁用的？

- **(A)** 给**外部开发者**（第三方 APP 开发者）— 他们拿到后只需要 `sdk/dap_api.h` + `build.bat` 来编写自己的 APP
- **(B)** 给**合作方 / OEM**  — 他们需要能编译出完整 PAC 固件（但看不到 DAP 实现）
- **(C)** 给**内部归档** — 存放对外发布的产物快照（PAC + bin + bin2 + bin3），不需要任何编译能力

**你选哪个？** 这直接决定 `zkw_output` 里需要包含什么。

---

## Q3. PAC 产物来源

**Memo Step 7：** `build → bin → bin2 → bin3 → pac`
**你的修正：** `PAC → flash → binding ID → bin2 → bin3`

**问题：** PAC 是从 internal 用 `mm.bat` 编译后**直接复制** `.pac` 文件到 `zkw_output/out/pac/` 吗？还是需要 `zkw_output` 自身能编译出 PAC？

- **(A)** 从 internal 编译好的 `.pac` 直接复制到 `zkw_output/out/pac/`
- **(B)** `zkw_output` 需要包含裁剪后的构建系统，能独立编译 PAC

**你选哪个？**

---

## Q4. 导出脚本 `export_zkw_output.py` 的执行时机

**问题：** 这个脚本什么时候执行？

- **(A)** 每次编译完 PAC 后自动执行（CI/CD 风格）
- **(B)** 手动执行 — 当需要对外发布时，工程师跑一次脚本生成 `zkw_output`
- **(C)** 只在重大版本发布时执行

**你选哪个？**

---

## Q5. `zkw_output` 中 DAP .c 文件的处理

**现状 `dap.mk` 中的 20+ 个源文件：**

| 模块 | 文件数 | 安全分类 |
|------|--------|---------|
| core/ | 1 (`DAP_InterfaceRegister.c`) | Class A — 禁止 |
| platform/ | 8 (`DAP_Loader_unisoc.c`, `DAP_InstallOSAPI_unisoc.c` 等) | Class A — 禁止 |
| security/ | 9 (`device_identity.c`, `bin2_loader.c`, `sha256.c` 等) | Class A — 禁止 |
| security/ed25519/ | 1 (`ed25519_verify.c`) | Class A — 禁止 |

**问题：** 如果 Q1 选 B 或 C（不做 libdap.a），`zkw_output` 的 `dap.mk` 应该如何处理？

- **(A)** `zkw_output` 中 `dap.mk` 直接删除（DAP 代码已在 PAC 中，外部开发者不需要编译它）
- **(B)** `zkw_output` 中保留一个精简版 `dap.mk`，只包含外部开发者需要的路径和宏定义

---

> 回复完毕后，我基于你的决策制定实施方案。
