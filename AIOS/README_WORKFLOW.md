# AIOS 工作流指南 —— 写给每一位工程师

> 这是你参与 AIOS 项目的**唯一操作手册**。
> 如果你是第一次使用，请从头到尾读一遍，大约 5 分钟。

---

## 什么是 AIOS 工作流？

简单来说：**你不能直接写代码。**

你必须先写一份"任务说明书"（我们叫 **Technical Memo**，简称 TM），然后 AI 会帮你：
1. 检查你的说明书有没有写清楚
2. 帮你做计划
3. 帮你写代码
4. 帮你做收尾文档

整个流程像流水线一样，一步一步走。

---

## 第 1 步：注册（只需要做一次）

打开 Antigravity，在对话框输入：

```
/aios-onboard
```

AI 会问你几个问题：
- **你叫什么名字？**（例如：`KaiwenZheng`）
- **你的职位是什么？**（例如：`软件工程师`）
- **你属于哪个组织？**（例如：`NextBigSeek`）
- **你主要负责什么？**（例如：`音频模块开发`）

然后 AI 会帮你创建个人档案，存在 `AIOS/engineers/你的名字/profile.yaml`。

AI 还会问你想加入哪个**项目**，或者新建一个项目。

注册完成后，AI 会自动帮你"登录"。

> 📌 **注册只需要一次。** 之后每次新开对话，只需要"登录"就行了。

---

## 第 2 步：登录（每次新开对话都要做）

**这是最重要的一步！不登录，AI 不允许你改任何代码。**

在对话框输入：

```
/aios-login
```

AI 会显示已注册的工程师列表，你选择自己的名字，再选择要做的项目。

登录之后你会看到类似这样的确认信息：

```
✅ 已登录：KaiwenZheng
📁 当前项目：featurephone_secure
📝 TM 路径：AIOS/projects/featurephone_secure/technical_memos/KaiwenZheng/
```

> ❗ **为什么要登录？** 因为同一个代码仓库可能有多个工程师在用。登录后 AI 才知道你是谁、在做什么项目，才能把文件存到正确的位置。

---

## 第 3 步：写 Technical Memo

Technical Memo 就是一份"任务说明书"，告诉 AI 你想做什么。

### 模板在哪？

```
AIOS/workflow/templates/technical_memo_template.md
```

### 文件名怎么起？

格式：`你的名字_项目名_TM编号_简短描述.md`

例如：
```
KaiwenZheng_featurephone_secure_TM41_audio_bridge.md
```

### 存到哪？

```
AIOS/projects/featurephone_secure/technical_memos/KaiwenZheng/
```

> 📌 **TM 编号在每个项目内独立递增。** 不同项目的 TM01 互不冲突。

---

## 第 4 步：运行工作流

在对话框输入：

```
/aios-workflow
```

然后把你的 TM 文件发给 AI（可以用 @ 符号引用文件路径）。

### AI 会自动做以下事情：

```
步骤 1：解析你的 Memo
         ↓
步骤 2：检查 Memo 有没有写漏
         ↓
步骤 3：有疑问的地方问你（你回答就行）
         ↓
步骤 4：生成冻结规格（你要确认同意）
         ↓
步骤 5：扫描历史踩坑记录 + 做实施计划
         ↓
步骤 6：开始改代码！
         ↓
步骤 7：生成验证清单
         ↓
步骤 8：⏸️ 停！轮到你了！你去测试
         ↓
步骤 9：你告诉 AI 测试结果
         ↓
步骤 10：AI 做收尾（session log + 反馈）
         ↓
步骤 11：AI 给你 git 命令，你在终端执行
```

> 📌 **AI 永远不会帮你执行 git commit。** 你必须自己在终端敲命令。

---

## 第 5 步：关闭任务

任务完成后，输入：

```
/aios-close
```

AI 会帮你做以下收尾工作：
- 生成 **session log**（本次工作的记录）
- 生成 **反馈报告**（结果是 SUCCESS / PARTIAL / BLOCKED）
- 更新 **MEMORY.md**（项目记忆）
- 检查是否有新的踩坑记录需要保存
- 提供 **git commit 命令**

---

## 所有命令速查表

| 命令 | 做什么 | 需要先登录吗？ |
|------|--------|:---:|
| `/aios-onboard` | 首次注册（只用一次） | ❌ |
| `/aios-login` | 登录（每次新对话） | ❌ |
| `/aios-workflow` | 完整工作流 | ✅ |
| `/aios-intake` | 只解析 Memo，不执行 | ✅ |
| `/aios-clarify` | 只做澄清问答 | ✅ |
| `/aios-close` | 关闭任务 | ✅ |

---

## 文件夹结构（你需要知道的）

```
AIOS/
│
├── 你的个人档案
│   └── engineers/KaiwenZheng/profile.yaml
│
├── 你的项目空间
│   └── projects/featurephone_secure/
│       ├── project.yaml              ← 项目信息
│       ├── technical_memos/          ← 你的 TM 文件
│       │   └── KaiwenZheng/
│       ├── feedback/                 ← 反馈报告
│       │   └── KaiwenZheng/
│       ├── quality_reports/          ← 质量报告（计划、规格、日志）
│       │   └── KaiwenZheng/
│       └── pitfalls/                 ← 项目级踩坑记录
│
├── 公共资源（所有项目共享）
│   ├── MEMORY.md                     ← 项目记忆
│   ├── docs/pitfalls/                ← 全局踩坑记录
│   ├── docs/architecture/            ← 架构文档
│   ├── docs/runbooks/                ← 操作手册
│   ├── registry/                     ← API、模块注册表
│   └── workflow/                     ← AI 的规则、技能、模板
│       └── manifest.yaml             ← 所有组件清单
│
└── 工具
    ├── scripts/                      ← 自动化脚本
    └── tools/                        ← 打包工具等
```

---

## 踩坑记录怎么用？

AIOS 有一个**三层踩坑知识体系**：

| 层级 | 存放位置 | 什么样的坑放这里 |
|------|---------|-----------------|
| **全局** | `AIOS/docs/pitfalls/` | 所有项目都可能遇到的坑（编译器、系统平台、工具链） |
| **项目级** | `AIOS/projects/xxx/pitfalls/` | 只影响某个项目的坑 |

AI 在做任务之前会自动扫描这些踩坑记录，避免你重复踩坑。

### 如何记录一个坑？

每条踩坑记录需要写明以下信息：

```markdown
# 踩坑：[标题]
- **记录人：** 你的名字
- **项目：** 项目名
- **日期：** YYYY-MM-DD
- **范围：** project 或 platform
- **影响模块：** 哪个模块
- **症状：** 出了什么问题
- **根因：** 为什么会这样
- **修复：** 怎么解决的
- **预防：** 以后怎么避免
```

---

## 反馈报告是什么？

每个 TM 执行结束后，AI 会自动生成一份反馈报告：

| 结果 | 意思 |
|------|------|
| **SUCCESS** | 所有要求都完成了，测试通过 ✅ |
| **PARTIAL** | 做了一部分，有些没完成 |
| **BLOCKED** | 被什么东西卡住了，无法继续 |

报告存在 `AIOS/projects/你的项目/feedback/你的名字/` 下面。

---

## GitLab 协作（重要！）

所有工程师通过 **GitLab** 共享代码。你必须在完成任务后把代码 push 上去。

### 第一次？先 Clone 仓库

**macOS / Linux（推荐 SSH）：**
```bash
git clone git@192.168.0.92:feature-phone/fp-aios-kz.git
```

**Windows（如果 SSH 没配好，用 HTTP）：**
```bash
git clone http://192.168.0.92/feature-phone/fp-aios-kz.git
```

### SSH 设置（macOS / Linux）

```bash
# 1. 生成密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. 启动 agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 3. 查看公钥，复制内容
cat ~/.ssh/id_ed25519.pub

# 4. 去 GitLab 添加：Settings → SSH Keys → Add Key

# 5. 测试连接
ssh -T git@192.168.0.92
# 期望输出：Welcome to GitLab, @你的用户名!
```

### SSH 设置（Windows）

**方式 A：Git Bash（推荐）**
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

**方式 B：用 HTTP（更简单）**
不需要配 SSH，直接用 HTTP clone 就行。

### 配置 Git 身份

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

### 创建你的分支

每个工程师+项目对应一个分支，格式是 `eng/你的名字/项目名`：

```bash
git checkout -B eng/KaiwenZheng/featurephone_secure
```

> 📌 如果你同时参与两个项目，就有两个分支。

### 日常提交和推送

```bash
# 1. 先 commit
git add -A
git commit -m "TM-41 实现音频桥接

Memo: TM-41
Author: KaiwenZheng
Project: featurephone_secure"

# 2. 再 push
git push -u origin eng/KaiwenZheng/featurephone_secure
```

> ❗ AI **永远不会**自动执行 git 命令。你必须自己在终端敲。

### GitLab 不可用怎么办？

如果内网断了或 GitLab 服务器宕机：
- **继续在本地工作**，正常 commit
- 等 GitLab 恢复后再 push
- 你的工作不会丢失

---

## 常见问题

**Q：我能不能跳过 Memo 直接让 AI 改代码？**
不行。这是核心规则。没有 Memo = 没有实施。但你可以让 GPT/Gemini等AI帮你**起草** Memo。

**Q：Memo 模板在哪？**
`AIOS/workflow/templates/technical_memo_template.md`

**Q：我发现了一个坑但不在做任务，怎么记？**
直接在 `AIOS/docs/pitfalls/`（全局）或 `AIOS/projects/你的项目/pitfalls/`（项目级）下新建 markdown 文件。

**Q：我怎么知道 AI 有哪些能力（技能、代理）？**
看 `AIOS/workflow/manifest.yaml`，里面列出了所有 AI 组件。

**Q：我忘记登录就开始干活了怎么办？**
AI 会阻止你。它会提示你先运行 `/aios-login`。

---

## 需要更多信息？

- [AIOS_WORKFLOW.md](AIOS_WORKFLOW.md) — 工作流规则详细定义
- [AI_CONTEXT.md](AI_CONTEXT.md) — 项目架构和技术上下文
- [MEMORY.md](MEMORY.md) — 项目记忆、踩坑记录、关键决策
- [workflow/manifest.yaml](workflow/manifest.yaml) — AI 组件完整清单
