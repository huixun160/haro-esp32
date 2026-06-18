# AIOS — Project Memory

Living document for accumulated project knowledge. Updated as tasks are completed.

---

## Resolved Pitfalls

### 2026-03-09 — Windows GBK Console Unicode Encoding
- **Symptom:** `UnicodeEncodeError: 'gbk' codec can't encode character` when printing ✓/✗ symbols
- **Root Cause:** Windows PowerShell uses GBK encoding, cannot render Unicode checkmarks
- **Fix:** Replace Unicode symbols with ASCII alternatives (`[OK]`, `[FAIL]`)
- **Affected Module:** `hooks/install_hooks.py`

### 2026-03-10 — SHA-256 Symbol Collision (TM-15)
- **Symptom:** Linker errors: `Symbol sha256_init multiply defined (by sha256.o and ssv_sha256-internal.o)`
- **Root Cause:** SSV WiFi module already defines SHA-256 symbols
- **Fix:** Prefix all DAP SHA-256 symbols with `dap_` (e.g. `dap_sha256_init`)
- **Affected Module:** `sha256.h`, `sha256.c`, `bin2_crypto.c`

### 2026-03-10 — SCI_TRACE_LOW Not Available in DAP Security Files (TM-15)
- **Symptom:** Linker error `Undefined symbol SCI_TRACE_LOW` or silent no-op
- **Root Cause:** `SCI_TRACE_LOW` macro requires `os_api.h` which is not in DAP security file include chain
- **Fix:** Use `DAP_DBG`/`DAP_DBG_ERR` macros → calls `DAP_TracePrint()` → `SCI_TRACE_LOW` in the correct compilation unit
- **Affected Module:** All DAP security `.c` files

### 2026-03-10 — DAP_TracePrint Ignored Varargs (TM-15)
- **Symptom:** Log output shows `%d`, `%02x` literally instead of formatted values
- **Root Cause:** `DAP_TracePrint()` passed format string via `%s`, ignoring `...` varargs
- **Fix:** Use `va_list` + `vsnprintf` to format before output
- **Affected Module:** `DAP_OSAssociated_unisoc.c`

### 2026-03-10 — DAP_FMM_IsBinFile Extension Filtering (TM-15)
- **Symptom:** `.bin2` files show "unsupported format" despite BIN2 loader being compiled
- **Root Cause:** `DAP_FMM_IsBinFile()` only checks `.bin` extension
- **Fix:** Added `.bin2` extension check before `.bin` check
- **Affected Module:** `DAP_FMM_Integration.c`

### 2026-03-10 — SCI_TRACE_MODE 未定义导致全部 Trace 为空 (TM-19)
- **Symptom:** DAP 所有 trace 在 Logel 中完全不可见
- **Root Cause:** `dap.mk` 缺少 `-DSCI_TRACE_MODE`，`os_api.h` 将 `SCI_TRACE_LOW` 编译为 no-op
- **Fix:** 在 `dap.mk` 的 `MCFLAG_OPT` 中添加 `-DSCI_TRACE_MODE`
- **Affected Module:** `make/dap/dap.mk`

### ⚠️ 反复踩坑：dap.mk 编译开关遗漏（TM-15/19/20，共 3 次）
- **规律：** 每次修改 DAP 代码后都可能忘记同步 `dap.mk`
- **后果：** 编译通过但功能静默失效（最危险的 bug 类型）
- **预防：** 每次 TM 实施后执行 `AIOS/docs/runbooks/dap_mk_checklist.md`
- **必查项：** `MCFLAG_OPT` 是否有 `-DSCI_TRACE_MODE`，`MSRCPATH` 是否包含新 `.c` 文件

### 2026-03-11 — 内存泄漏阻断功能验证 (TM-21)
- **触发：** TM-21 BIN2 签名诊断代码就绪，准备设备测试时发现内存泄漏
- **教训：** 内存泄漏会污染所有后续验证结果，必须优先于功能开发
- **预防：** 遇到内存/资源 bug 立即暂停当前 TM，开新 TM 专项解决

### 2026-03-11 — Running_AP 指针偏移导致 heap 损坏 (TM-22)
- **Symptom:** BIN2 文件运行后 `SCI_Release_Buffer` assert / 内存泄漏
- **Root Cause:** BIN2 unwrap 后 `Running_AP` 前移 112 字节，`DAP_MemFree` 释放偏移指针（非原始分配基地址）
- **Fix:** 新增 `alloc_base` 变量追踪原始 `DAP_MemAlloc` 返回值，所有 free 操作使用 `alloc_base`
- **Affected Module:** `DAP_Loader_unisoc.c`

### 2026-03-12 — device_binding.c include 不存在的 dap_sha256.h (TM-25)
- **Symptom:** 编译报错 `cannot open source input file "dap_sha256.h"`，导致 `dap.a` 无法生成
- **Root Cause:** SHA-256 **函数名**有 `dap_` 前缀（如 `dap_sha256_hash`）但**文件名**是 `sha256.h`，代码误写为 `dap_sha256.h`
- **Fix:** `#include "dap_sha256.h"` → `#include "sha256.h"`
- **Affected Module:** `device_binding.c`

### ⚠️ 反复踩坑：SFS extern 声明导致常量和类型全错 (TM-26, 共 4 次调试)
- **Symptom:** `SFS_CreateFile` 返回 `0`（失败），但代码误判为有效句柄，后续写入 0 字节
- **Root Cause:** security 模块用 `extern` 自行声明 SFS 函数和常量，`SFS_INVALID_HANDLE` 定义为 `0xFFFFFFFF`，实际平台定义为 `0`
- **Fix:** 删除所有 extern SFS 声明，改为 `#include "../platform/unisoc/DAP_OSAssociated_unisoc.h"`
- **Affected Module:** `device_binding.c`, `device_bindfile.c`
- **预防规则：** DAP security 模块禁止 extern 声明平台 API，必须 include 平台头文件

### 2026-03-12 — Filearray 路径 SFS 无法访问 (TM-26)
- **Symptom:** `SFS_CreateFile("D:\Filearray\device.bind")` 返回 0（失败）
- **Root Cause:** `Filearray` 不是 SFS 可直接操作的真实目录，需使用 `D:\DAP\`
- **Fix:** 路径改为 `D:\DAP\device.bind`（DAP_DebugLog.c 已验证可写）
- **Affected Module:** `device_bindfile.c`

### 2026-03-13 — bin2_crypto.c 硬编码 BIN2_HEADER_SIZE (TM-28)
- **Symptom:** TM-28 将 `BIN2_HEADER_SIZE` 从 64 改为 96 后，所有 v2 `.bin2` 签名验证失败
- **Root Cause:** `bin2_crypto.c` 签名验证函数使用硬编码常量 `BIN2_HEADER_SIZE`（3处），未读取 `header->header_size`
- **Fix:** 全部改为 `header->header_size` 动态读取
- **Affected Module:** `bin2_crypto.c`
- **⚠️ 预防：** 修改 `bin2_format.h` 常量后，必须 `grep -rn` 搜索所有使用点确认

### 2026-03-13 — 加密 BIN2 BSS 重分配从磁盘重读密文 (TM-28)
- **Symptom:** 加密 `.bin3` 验证通过（签名/hash/解密 OK）但执行时 Prefetch Abort 蓝屏
- **Root Cause:** BSS 重分配释放含解密数据的缓冲区后从文件重读 → 读回密文 → CPU 执行密文崩溃
- **Fix:** 加密 BIN2 跳过文件重读，先 `DAP_MemAlloc` 新缓冲区，`memcpy` 解密数据，再 `DAP_MemFree` 旧缓冲区
- **Affected Module:** `DAP_Loader_unisoc.c`
- **⚠️ 预防：** 涉及「原地解密 → 释放 → 重分配」的流程，必须确认重分配后数据来源是明文非密文

### 2026-03-15 — DSP Assert on PCM Buffer Recording (TM-029-2)
- **Symptom:** 长按语音键蓝屏 `dspintisr.c:587 PASSERT`
- **Root Cause:** `DAP_AudioRecordStreamStart()` 使用 `MMISRVAUD_RECORD_FMT_PCM`(format=0），Unisoc DSP 缓冲区录音可能不支持 PCM 直录
- **Fix:** 改 `BS_AUDIO_USE_AMR=1`（AMR-NB 模式，format=1, sr=8000）
- **⚠️ 预防：** `dap_audio_bridge.c` 中手动复制的 `DAP_SRVAUD_TYPE_T` struct 布局必须与真实 `MMISRVAUD_TYPE_T` 完全一致
- **Affected Module:** `bs_core_config.h`, `dap_audio_bridge.c`

### 2026-03-15 — WiFi Status Enum 跨 SDK 版本不匹配 (TM-029-2.5)
- **Symptom:** WiFi 已连接但 `BS_IsWifiConnected()` 永远返回 FALSE，所有网络操作失败
- **Root Cause:** `bs_network.c` 硬编码 `BS_WIFI_STATUS_CONNECTED=4`（后期快照）或 `3`（Ouyang git），实际 `mmiwifi_export.h` 定义 `MMIWIFI_STATUS_CONNECTED=2`
- **Fix:** 改为 `#define BS_WIFI_STATUS_CONNECTED 2`（Logel 实证）
- **⚠️ 预防：** 不要猜测平台枚举值，必须 `#include` 官方头文件或通过 Logel trace 验证
- **Affected Module:** `bs_network.c`

### 2026-03-16 — SCI_Sleep 阻塞 MMI 线程导致 Enqueue Assert (TM-029-2.5)
- **Symptom:** 连 WiFi 后打开语音助手蓝屏 `sdi_msg_iram.c:82 Enqueue failed`
- **Root Cause:** `BS_HttpTaskCreate()` 中 `SCI_Sleep(10)` 循环最多 500ms 阻塞 MMI 线程，系统消息队列溢出
- **Fix:** 移除 SCI_Sleep 等待循环，HTTP worker 自行启动
- **⚠️ 预防：** **MMI 线程中绝对不能调用 SCI_Sleep** — 会阻塞系统消息泵
- **Affected Module:** `bs_task.c`

---

## Key Decisions

### 2026-03-20 — External Binary Hardening Phase 1 (TM-032-1)
- **操作:** SECURE build profile (`project_*_SECURE.mk` + `dap.mk` EXTERNAL_BUILD gating)
- **编译命令:** `mm ums9117_240X320BAR_64MB_ML_SECURE new` (external) / `mm ums9117_240X320BAR_64MB_ML new` (internal)
- **关键发现 1:** Unisoc build 按项目名查找 `lib/<project>/` → 需要 junction
- **关键发现 2:** `SCI_TRACE_LOW` 不受 `SCI_TRACE_MODE` 宏控制 → trace 未被禁用
- **关键发现 3:** device.bind 不含 device_secret → 无法在 PC 生成 BIN3
- **Pitfall:** `sprd_macro_check.pl` 用 `return` outside subroutine; `findstr` 匹配注释
- **后续:** TM-032-2 (DeviceSecret 导出), TM-032-3 (trace hardening + strip + 混淆)

### 2026-03-21 — PowerShell 编码腐蚀源码 (TM-032-2)
- **Symptom:** armcc 编译出现数百个语法错误 (expected identifier / expected ')')
- **Root Cause:** PowerShell `Set-Content` 强制 UTF-8 编码，破坏 GB2312 中文注释 + 去除 \r (CRLF→LF)
- **Fix:** 使用 Latin-1 (ISO-8859-1) 字节透明替换，或 `git checkout` 恢复后用编辑器工具替换
- **⚠️ 预防：** **DAP 源码禁止使用 PowerShell Set-Content**，必须用 replace_file_content 编辑器工具
- **详见:** `AIOS/docs/pitfalls/powershell-encoding-corruption.md`

### 2026-03-21 — EXTERNAL_BUILD 去 trace 后无法 debug BIN2 崩溃 (TM-032-2)
- **Symptom:** BIN2 Prefetch Abort 蓝屏，但 SECURE 版本 Logel 零 trace 无法调试
- **Root Cause:** 编译时去除 trace + BIN2 执行崩溃 = 无法定位问题
- **决策:** 回退 TM-032-2，改用混淆方案 (TM-032-3)
- **⚠️ 教训：** 去 trace 操作必须在 BIN 加载流程完全稳定后才能启用

### 2026-03-21 — Post-Build Hardening + Trace Codebook (TM-032-3)
- **操作:** post-build strip + strings scan + trace 前缀混淆
- **Strip:** `fromelf --strip=debug` — Entry.o -1360B, Start.o -542B
- **Trace Codebook:** 165 行 / 15 文件，33 个映射（`[DAP]`→`[P7]`, `DeviceSecret`→`K9` 等）
- **密码本:** `AIOS/docs/runbooks/trace_codebook.md`
- **Log 文件:** `DAP_RunDebug.Log` → `P7_rd.log`，对外版本完全不生成
- **关键发现:** `__FILE__` 宏和 `InterfaceRegister` ABI 名无法混淆
- **⚠️ 预防:** 修改 trace 字符串只能改引号内内容，不能用 broad `.Replace()` 否则会破坏函数名

### 2026-03-19 — External Deliverable Packaging (TM-031)
- **操作:** 创建 `export_zkw_output.py` 导出脚本, 生成 `zkw_output_pac_code/`
- **架构:** 一套 DAP 源码 + 两套 build mode (internal/external)
- **关键发现:** Entry.c 依赖 core/DAP_Application.h → 不能导出源码 → 改为预编译 .o
- **导出内容:** PAC (53MB) + SDK (dap_api.h) + lib (Entry.o, Start.o) + demo APP
- **安全扫描:** PASSED — 零 Class A 内容 (core/platform/security/loader 全部不在 zkw_output)
- **开发者模型:** APP 开发者只编译 main.c，链接预编译 Entry.o + Start.o
- **Runbook:** `docs/runbooks/dap_app_developer_guide.md`

### 2026-03-19 — DAP SDK v0 ABI 冻结 (TM-030)
- **操作:** 创建 `sdk/dap_api.h` (宏封装), `dap_abi_v0.md`, build.bat 边界检查
- **关键发现:** DAP loader 不做 RW 数据重定位 — APP 中任何 `static` 变量会导致蓝屏
- **结果:** BIN/BIN2/BIN3 全链路验证通过, Logel trace 确认 `dap_api.h v0 OK`
- **Pitfall:** `static` 变量 forbidden (记录在 `dap_abi_v0.md`, `pitfalls/dap_loader_no_rw_reloc.md`)

#### 核心架构决策
| 决策 | 选择 | 要点 |
|------|------|------|
| core/ 访问 | APP 禁止访问 core/ | `DAP_Application.h` 为 loader 内部专用 |
| FindInterface | 宏封装保留 FindInterface | ABI 不变, 不重写运行时 |
| 旧 APP | 只迁移 hello_bigseek | 8 个旧 APP → `apps/_legacy/` |
| 类型系统 | SDK 标准 C, 内部保留历史 | `_DWORD` 等不进入 sdk/ |
| v0 范围 | lifecycle+memory+log+timer+popup | LVGL/Audio → v1/v2 |

#### DAP 重定位架构
- **Loader 重定位:** 只设置 `LoadAddr`, `OSAPI`, `Register`, `DelAPI` 四字段
- **代码重定位:** ARM `-reloc` 链接器生成 reloc entries, loader 不额外处理
- **RO 数据:** 字符串字面量通过 PC-relative 寻址, 安全
- **RW 数据:** ⚠️ **不重定位** — `static`/全局变量绝对禁止

#### SDK 演进路线图
- **v0 (TM-030):** runtime + minimal feedback ABI (当前)
- **v1 (TM-030.x):** LVGL minimal surface
- **v2 (TM-030.x):** Audio minimal surface
- **TM-031:** 对外裁剪 (内外版本分离)
- **TM-032:** 混淆 (FindInterface 名称混淆)
- **长期:** `def.h` 降级, 全面标准 C 类型, loader RW 重定位支持

### 2026-03-19 — TM28-R 基线恢复验证通过 (TM-029-3)
- **操作:** git checkout `a989891e` 回退 8 文件 + 删除 30 VA 文件 + 移动 legacy 目录
- **结果:** BIN2 (4 cases) + BIN3 (1 case) 全部通过设备验证
- **当前基线:** TM28-R clean baseline, 无语音助手污染

### 2026-03-16 — Contaminated Snapshot 不可维护，需要回退 (TM-029-2.5, ADR-016)
- **Context:** Ouyang 的代码快照有多处 SDK 版本不匹配的 bug（WiFi 常量、DSP 兼容性）
- **Decision:** 停止在 contaminated snapshot 上逐点修补，考虑版本回退或重新实现
- **Alternatives Considered:** 继续逐 bug 修复（风险：未知 bug 数量不可预估）
- **Consequence:** 创建了完整架构文档 `AIOS/docs/architecture/voice_assistant_architecture.md` 作为未来重新实现的参考
- **Context:** 快照版 60KB vs 主线 28KB，Memo 建议逐函数合并
- **Decision:** 分析确认快照版是纯追加超集（原有 21 函数未修改），直接替换
- **Alternatives Considered:** 逐函数合并（30KB 差异易出错）
- **Consequence:** 减少合并风险，成功保留所有原有功能 + 新增 VA 音频功能


### 2026-03-09 — Cross-Platform Python Hooks (TM-17)
- **Context:** Memo 17 specified bash hooks, but project runs on Windows
- **Decision:** Use Python scripts as hook entry points instead of bash; create `install_hooks.py` for cross-platform installation
- **Alternatives Considered:** Bash-only (requires Git Bash), dual bash+Python
- **Consequence:** Hooks work identically on Windows and Mac/Linux

### 2026-03-09 — TM Reference Format (TM-17)
- **Context:** Needed standardized memo reference in commit messages
- **Decision:** Format: `TM-<number>-<short_name>` (e.g. `TM-17-workflowhook`)
- **Alternatives Considered:** `Technical_Memo_XX_*` (too verbose), `TM-XXX` (no description)
- **Consequence:** Commit messages are concise and grep-friendly

### 2026-03-10 — SHA-256 Symbol Namespacing (TM-15, ADR-001)
- **Decision:** All DAP crypto symbols must use `dap_` prefix to avoid collisions with platform libraries
- **Consequence:** New crypto code must follow naming convention: `dap_<algorithm>_<function>`

### 2026-03-10 — BIN2 Signature Message Construction (TM-15, ADR-002)
- **Decision:** message = header(48) + zeros(64) + payload — signature area zeroed, rest of file intact
- **Consequence:** Packer and verifier must use identical construction; verifier does in-place zero + restore

### 2026-03-10 — DAP Logging Architecture (TM-15, ADR-003)
- **Decision:** All DAP modules use `DAP_DBG`/`DAP_DBG_ERR` → `DAP_TracePrint` → `SCI_TRACE_LOW`
- **Consequence:** Never call `SCI_TRACE_LOW` or `SCI_TraceLow` directly from DAP `.c` files

### 2026-03-11 — BIN2 Loader alloc_base 模式 (TM-22, ADR-004)
- **Decision:** 任何对 `DAP_MemAlloc` 返回指针做偏移的场景，必须保留原始基地址 (`alloc_base`) 用于 free
- **Consequence:** `DAP_ExecuteAP` 返回 `alloc_base` 作为 handle；`DAP_ReleaseAP` 通过 `bin2_detect` 区分 BIN1/BIN2

### 2026-03-11 — BIN2 BSS 重读必须从 payload 偏移开始 (TM-22, ADR-005)
- **Decision:** BSS 重分配路径中，BIN2 文件必须从 `bin2_payload_off`(112) 开始重读，不能从 0 开始
- **Consequence:** 所有涉及 `DAP_FileSeek + DAP_FileRead` 的路径必须检查 `is_bin2` 标记

### 2026-03-11 — Ed25519 PyNaCl ↔ TweetNaCl 兼容性确认 (TM-21/22)
- **Decision:** PC 端 PyNaCl(libsodium) 与设备端 TweetNaCl-derived C 实现完全兼容，`ed25519_verify ret=0`
- **Consequence:** 签名链已闭环；未来无需更换 Ed25519 实现

### 2026-03-12 — 设备绑定分阶段实现 (TM-23, ADR-006)
- **Decision:** BIN2 设备绑定拆为 3 阶段：(1) BindingID Logel 可观测 (2) .bind 文件导出 (3) BIN2 header 绑定集成
- **Consequence:** 不一次修改 BIN2 header 格式；每阶段独立验证后才进入下一阶段

### 2026-03-10 — SCI_TRACE_LOW 是平台标准 Trace API (TM-19)
- **Decision:** `SCI_TRACE_LOW` 是 Mocor 平台唯一的标准 trace 输出 API（1145+ 调用点）
- **Consequence:** DAP 编译单元必须定义 `SCI_TRACE_MODE`；DAP security 文件不含 `os_api.h`，需通过 `DAP_DBG` 间接调用

### 2026-03-12 — DAP_LoaderInit 是 lazy init，安全诊断需双路径触发 (TM-25, ADR-008)
- **Decision:** `DAP_LoaderInit()` 仅在用户运行 .bin 时从 FMM 调用，不在开机时执行
- **Consequence:** 安全诊断函数（如 `device_binding_log_id`）需同时集成到 `DAP_LoaderInit` 和 `*#3472#` debug menu 中

### 2026-03-12 — Antigravity 命令发现机制 (TM-24, ADR-007)
- **Decision:** Antigravity 通过 `.agents/workflows/` 目录 + YAML frontmatter `description` 字段发现 slash 命令
- **Consequence:** 新增 AIOS 命令只需在 `.agents/workflows/` 下创建 `.md` 文件，无需额外的 manifest 或注册配置
- **验证工具:** `python AIOS/scripts/verify_workflow_paths.py` — 扫描所有工作流文件交叉引用

### 2026-03-12 — Bindfile 导出路径为 D:\DAP\device.bind (TM-26, ADR-009)
- **Decision:** device.bind 文件写入 `D:\DAP\device.bind`（SFS 可写路径，USB 连接后在 DAP 文件夹可见）
- **Consequence:** PC packer 可直接读取 JSON 格式的 bindfile；触发方式包括 `DAP_LoaderInit`、`*#3472#` debug menu、BIN2 执行时自动生成
- **⚠️ 禁止：** 不可写入 `Filearray/` — SFS 无法直接操作该路径（TM-26 踩坑记录）

### 2026-03-12 — TM-27 Binding Trace 使用 tm27_ 前缀 (TM-27, ADR-010)
- **Decision:** `bin2_loader.c` 中 binding check 的 trace 使用 `tm27_` 前缀
- **Consequence:** 在 Logel 中搜索 `tm27_` 可快速定位设备绑定验证结果

### 2026-03-13 — UI 层错误码映射 (TM-27, ADR-011)
- **Decision:** BIN2 验证失败时 UI 显示的错误码与内部码的映射关系已确认
- **映射：** `Err-9` = `BIN2_ERR_BINDING (-6)` 绑定不匹配；`Err-10` = `BIN2_ERR_SIGNATURE (-2)` 签名/hash 失败
- **Consequence:** 调试时 Logel 看内部码，用户看 UI 错误码；两者对应关系已记录

### 2026-03-13 — AES-128-CTR 使用自包含 tiny-AES-c 实现 (TM-28, ADR-012)
- **Decision:** 不使用平台 mbedTLS/硬件 AES API，而是移植 tiny-AES-c 为 `dap_aes.c`（CTR-only, `dap_aes_` 前缀）
- **Consequence:** 无外部链接依赖；约 170 行 C 代码；CTR counter 使用 128-bit 大端递增（与 pycryptodome 一致）

### 2026-03-13 — Payload KDF 独立 Salt (TM-28, ADR-013)
- **Decision:** Payload 加密密钥 KDF 使用 `"AIOS-PAYLOAD-V1"` salt，区别于 Binding KDF 的 `"AIOS-BIND-V1"`
- **Consequence:** 同一 DeviceSecret 派生出不同的 binding_id 和 payload_key，防止密钥重用

### 2026-03-13 — Sign-after-Encrypt, Hash-on-Plaintext (TM-28, ADR-014)
- **Decision:** v3 BIN2 签名覆盖加密后的 payload（sign-after-encrypt），hash 覆盖明文 payload（hash-after-decrypt）
- **Consequence:** 设备端验证顺序：签名 → 绑定 → 解密 → hash；签名验证在解密前即可拒绝篡改

### 2026-03-13 — 加密 BIN2 BSS 重分配用 memcpy 替代文件重读 (TM-28, ADR-015)
- **Decision:** 加密 BIN2 在 BSS 重分配时使用 `memcpy` 保留已解密数据，不从磁盘重读
- **Consequence:** 需要短暂同时持有两份缓冲区（对 572B payload 影响可忽略）；非加密 BIN2 和 BIN1 仍走原路径

---

## Working Configuration

<!-- Add known-good configuration snapshots -->
### 2026-03-10 — BIN2 Integration Build
- **Build Target:** ums9117_240X320BAR_64MB_ML
- **Build Command:** `DAP make\make_cmd\make -r -R MAKESHELL=CMD p=ums9117_240X320BAR_64MB_ML new`
- **Module Build:** `DAP make\make_cmd\make -r -R MAKESHELL=CMD p=ums9117_240X320BAR_64MB_ML MODULES=dap JOB=16`
- **Notes:** Full build passes with BIN2 integration

---

## Frequently Referenced Facts

- **UserNV DeviceSecret ID:** 0x0001 (EFS_NvitemRead/Write)
- **BIN2 v2 header size:** 64 bytes（TM-23）; **v3 header size:** 96 bytes（TM-28，+enc_mode/IV/reserved）
- **BIN2 signature size:** 64 bytes (Ed25519)
- **BIN2 v2 payload offset:** 128 bytes (= 64 + 64); **v3 payload offset:** 160 bytes (= 96 + 64)
- **BindingID 算法:** SHA256("AIOS-BIND-V1" || DeviceSecret)[0..15] = 128-bit
- **Payload KDF:** SHA256("AIOS-PAYLOAD-V1" || DeviceSecret || binding_id)[0..15] = 128-bit AES key
- **BIN2 magic:** `B`, `I`, `N`, `2` (0x42, 0x49, 0x4E, 0x32)
- **BIN2 加密:** AES-128-CTR, 128-bit 大端 counter, 随机 IV 存于 header.payload_iv
- **BIN2 file extensions:** `.bin2`(v2 plaintext), `.bin3`(v3 encrypted)
- **Ed25519 public key location:** `bin2_crypto.c` → `BIN2_PUBLIC_KEY[32]` (compiled into firmware)
- **Private key location:** PC only — `AIOS/tools/bin2_packer/private_key.bin` (never enters device)
- **DAP SHA-256 prefix:** `dap_` (e.g. `dap_sha256_hash`, `DAP_SHA256_CTX`)
- **DAP logging API:** `DAP_DBG("...")` → `DAP_TracePrint()` → `SCI_TRACE_LOW`
- **File extension gate:** `DAP_FMM_IsBinFile()` — must be updated for new DAP file formats
- **Logel trace filter:** Search `SCI_TRACE_LOW` or `SCI_TraceLow` in `trace_define.txt` (lines 202-203)
- **Bindfile 路径:** `D:\DAP\device.bind` (JSON 格式, USB 连接后在 DAP 文件夹可见)

### TM-032-4: Interface IDization (2026-03-21)
- **Decision:** Bootstrap FindById via InterfaceRegister_Add("__FB", FindById) -- no TApplication struct change
- **ID registry:** flat array s_id_table[256] in firmware BSS, O(1) lookup
- **APP build:** build.bat must add -DEXTERNAL_BUILD -I%CORE_DIR%
- **Pitfall:** cross-module type mismatch (uint16/_INT32 unavailable) -- use unsigned short/int
- **Pitfall:** APP missing -DEXTERNAL_BUILD -- dap_popup silently fails
- **Known Issue:** BIN2 repeated execution crash (~5 runs), BIN/BIN3 not affected, pre-existing

### TM-035: API 资产梳理与 YAML 注册 (2026-03-23)
- **API 总数:** 66 个 API，10 模块，36 个 Unisoc 底层 API
- **存储:** 双位置 — `AIOS/registry/apis.yaml` (YAML) + `AIOS/docs/api/` (markdown)
- **Schema:** `AIOS/registry/schema/api_schema.yaml`，`abi` 字段 optional
- **验证:** yamllint + `AIOS/scripts/validate_api_schema.py`
- **关键缺口:** Input/键盘 API（🔴）、LCD/自定义 UI API（🔴）、Network API（🟡）
- **主要风险:** MMIPUB_* 直接暴露 Unisoc 内部（应封装）、Audio 13 API 但 0 通过 SDK

### TM-36: 平台能力全量普查 (2026-03-23)
- **API 总数:** ~750 个 API，12 模块，79 能力
- **DAP 覆盖:** ~11% (核心 Mocor API ~6%, LVGL 100%)
- **存储:** `docs/api/modules/*.md` (15 Markdown) + `registry/capabilities/*.yaml` (12 YAML)
- **PDF 工具:** `scripts/pdf_extract.py` (pdfplumber), 处理 104/114 PDF
- **LVGL:** 38 API 已通过 `dap_lvgl_bridge.c` 100% 桥接, 推荐作为 APP UI 方案
- **关键缺口:** Network 0% DAP, GUI/MMI 8% DAP, Telephony 0% DAP
- **后续:** TM-37 LVGL 控件扩展 + Network 桥接 + 源码深度扫描

### TM-37: 模块收口与源码深扫 (2026-03-23)
- **源码 API 总数:** ~6,306 个 API，9 模块 6/6 completion
- **TM-36→TM-37 扩展:** 750→6,306 (8.4×)，文档覆盖仅 12%
- **COAPI 发现:** `MS_MMI_Main/source/coai_app_pool/` — 已有 OTA/Download/DeviceBind 框架
- **App Store 评估:** COAPI + DAP Loader 覆盖 70% 核心能力
- **UI 结论:** LVGL (38 API, 100% DAP) 替代 MMI (2,895 API, 0.6% DAP) 做 APP UI
- **关键缺口:** Network 0% DAP (442 API)，是 App Store 前置条件
- **架构师待决策:** UI 路线 / Network 优先级 / App Store 架构方案

### TM-38: Runtime Memory & App Lifecycle 架构设计 (2026-03-23)
- **现状确认:** DAP = 同步单任务 Loader，`Running_AP` 局部变量，无生命周期/资源追踪
- **设计方案:** 单前台 APP + 后台任务，共享 heap + OOM 检测，完整资源回收
- **生命周期:** INIT → RUNNING → PAUSED → DESTROYED（4 状态）
- **资源回收:** APP 退出时自动释放 memory + LVGL + timer + socket
- **BIN 扩展:** v4 header 添加 `memory_required` + `supports_background`
- **实施路线:** TM-39 (Resource Tracker) → TM-40 (Lifecycle) → TM-41 (Background+OOM) → TM-42 (BIN v4)
- **设计文档:** `docs/architecture/runtime_memory_lifecycle.md`

### TM-39: AIOS Workflow System Audit (2026-03-24)
- **审计范围:** 6 agents, 13 skills, 8 rules, 3 hooks (4 guards), 5 Antigravity commands
- **全部组件存在且结构良好:** 每个 agent/skill/rule 都是独立 .md 文件，格式统一
- **Git Hooks:** 3 个全部安装 ✅，warn-only fail-open (v1)，4 个 guard 脚本正常
- **Antigravity 命令路由:** `.agents/workflows/` + YAML frontmatter — 全部可发现 ✅
- **关键发现:** Agent 执行无强制保证（依赖 AI attention），无组件 manifest
- **建议 (HIGH):** 创建 `AIOS/workflow/manifest.yaml` 组件清单 + agent 执行日志
- **基线报告:** `docs/architecture/aios_workflow_baseline.md`



### TM-40: Multi-Engineer Multi-Project Workflow Upgrade (2026-03-24)
- **Author:** KaiwenZheng | **Project:** featurephone_secure
- **升级内容:** 单工程师工作流 → 多工程师多项目协作
- **目录重构:** `engineers/` + `projects/featurephone_secure/` 新结构
- **迁移:** 145 文件迁移到项目目录（TMs, feedback, session logs, specs, plans, pitfalls）
- **新组件:** 5 skills (register-engineer, register-project, sync-shared-knowledge, log-execution, session-login) + 2 agents (assignment-reviewer, knowledge-curator)
- **manifest.yaml:** 创建组件清单 — 8 agents, 18 skills, 8 rules, 3 hooks, 6 commands
- **登录系统:** `/aios-login` 命令，session-only 上下文，所有工作命令需登录
- **Hook 重命名:** `hooks/` → `AIOShooks/`，`memo_guard.py` 加命名校验
- **文档:** `README_WORKFLOW.md` 中文指南，旧 README.md 已废弃
- **关键决策:** 登录不持久化（session-only），onboard 含项目创建，单人也要登录
- **踩坑体系:** 三层（全局 docs/pitfalls/ + 项目 projects/*/pitfalls/ + knowledge-curator 晋升）

### TM-02: Parallelization & State-Driven Execution Milestone 1 (2026-03-25)
- **Author:** KaiwenZheng | **Project:** aios_workflow_meta → fpreconstruction
- **核心决策:** 从 "纯对话系统" 升级为 "弱状态系统" — 没有持久化状态就没有并行系统
- **状态机:** B+A — `module_states.yaml` 持久化 + `manifest.yaml` 声明式
- **Planner:** V1 只读，集成到 `/aios-workflow` 自动触发，输出 ready/blocked 模块
- **并行模型:** 多工程师多对话共享 `module_states.yaml`
- **架构外化:** `architecture_constitution.md` (5 rule), `service_contracts/`, `acceptance_tests.yaml`, `agent_permissions.yaml`
- **新项目:** `fpreconstruction` — 17 模块 (8 services + 6 adapters + ABI + Runtime + App)
- **Planner 测试:** abi_v1 CLOSED → 8 services 并行解锁
- **后续:** Week 2 = 状态机接入 workflow + Human Gate; Week 3 = Integration + Agent self-review

### TM-01: Clone James GitLab Repository (2026-03-26)
- **Author:** KaiwenZheng | **Project:** demo_merge
- **操作:** HTTP clone `UMS9117_BSP` 仓库到隔离目录 `zkw_legacy_code/james_demo_20260326/`
- **Branch:** `main` | **Commit:** `f1592ec0`
- **安全验证:** 主线 .git 无变化，zkw_legacy_code 为 untracked
- **后续:** TM-02 系统分析 James 代码资产

### TM-02: James Legacy Code System Analysis (2026-03-26)
- **Author:** KaiwenZheng | **Project:** demo_merge
- **分析范围:** James UMS9117_BSP 仓库 — 12 DAP Apps, LVGL 9.5.0, 5 Bridge 模块
- **核心发现:** TApplication ABI 兼容 (352B), FindInterface 兼容, BIN 格式兼容
- **识别 9 个兼容性 Gap:** LVGL API 未注册, LVGL 源码缺失, KeyCallback/ScanApps 缺失, Audio/T9/VA/DL Bridge 缺失, 注册容量可能不足
- **Merge 策略:** 4 Tier — LVGL Runtime → Bridge → Apps → Download; 禁止覆盖 Loader/Register/Security
- **交付物:** 5 份 (architecture, modules, api_list, merge_plan, core_compatibility)### TM-03: James Demo Feature Integration (2026-03-26)
- **Author:** KaiwenZheng | **Project:** demo_merge
- **操作:** 将 James 的 DAP 演示功能（LVGL 9.5.0 + palm_menu 启动器 + Bazar 下载器 + Bridge 模块）整合到主线 internal build
- **迁移文件:** ~60 个文件（11 app 目录, 18 bigseek_core, 9 bridge, 4 SDK headers, 3 MMI, 7 build files）
- **关键修复 1:** dap.mk 是 "merge-only" 文件 — 不能直接替换，必须合并主线 security 模块 + James 新功能
- **关键修复 2:** preload_udisk 目录缺少预编译 BIN 文件 → palm_menu 不出现
- **关键修复 3:** LVGL src/ 目录不同版本 → CJK 字体乱码 → 整目录替换
- **安全护栏:** DAP_InterfaceRegister.c + DAP_Loader_unisoc.c 保持主线版本，使用 shim headers 兼容 James 代码
- **Flash 分区:** OSA 16MB→18MB (Nand_PartTable_64k/128k.c), 烧录需全量
- **Pitfalls:** PF-TM03-01 (LVGL CJK font), PF-TM03-02 (dap.mk merge), PF-TM03-03 (preload BINs)

### ⚠️ 反复踩坑：LVGL 字库/编译问题（TM-03, 已发生多次）
- **规律：** LVGL 版本号相同但 src/ 内容不同; lv_conf.h 相同不等于字体数据相同
- **后果：** CJK 中文显示为乱码，图标标签不可读
- **预防：** 
  1. 合并 LVGL 代码时，必须比对 `src/font/lv_font_source_han_sans_sc_*` 文件大小
  2. CJK 字库文件（16_cjk.c）应至少 1.9MB；如果只有 1.2MB 则缺少大量字形
  3. 整目录替换 `lvgl-9.5.0/src/` 是最安全的方式
- **关联决策：** 编译通过 ≠ 功能正确（字体是运行时才能验证的）

### ⚠️ 反复踩坑：编译相关配置遗漏（TM-03/15/19/20, 共 5+ 次）
- **新增模式：** 替换 .mk 文件时丢失主线安全模块（12 个 .c 文件 + security 路径）
- **后果：** 17 个链接错误（bin2_*, device_*, OS_* 符号全部丢失）
- **预防：**
  1. dap.mk 禁止直接替换，只能 merge
  2. 替换前必须 `diff` 并确认不丢失 `Third-party/DAP/security/` 相关内容
  3. 检查清单：security paths, EXTERNAL_BUILD gating, DAP_UNISOC_OSAssociated.c



