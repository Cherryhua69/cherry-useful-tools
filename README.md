# Cherry Useful Tools

个人在真实任务里沉淀的一套 Coding Agent 工作资产：全局协作约定、可复用技能、可复制提示词。

收录标准只有一条——**自己实际跑通过**。每条规则都对应一次具体的踩坑，所以文字尽量压缩到"能直接执行"的程度，不为模板完整而堆砌内容。

## 快速索引

| 我想…… | 去哪里 |
|---|---|
| 让 Agent 默认用中文、少改代码、先查根因 | [`coding-agents/codex/AGENTS.md`](coding-agents/codex/AGENTS.md) |
| 给会话起一个能检索的标题 | [`skills/codex-session-namer/`](skills/codex-session-namer/SKILL.md) |
| 在 Windows 上装/修 OpenCodex 或替换 CC-Switch 路由 | [`skills/opencodex-install-win/`](skills/opencodex-install-win/SKILL.md) |
| 改本机 WSL / 局域网服务器 / 嵌入式设备上的代码 | [`skills/remote-device-coding/`](skills/remote-device-coding/SKILL.md) |
| 给 X 文章配布偶猫封面和插图 | [`skills/x-article-cat-visual/`](skills/x-article-cat-visual/SKILL.md) |
| 把一份 Skill 改造成可验证、可迭代的系统 | [`prompts/skill-self-iteration.md`](prompts/skill-self-iteration.md) |

## 目录结构

```text
.
├── coding-agents/                        全局常驻约定
│   └── codex/
│       └── AGENTS.md                     中文、最小变更、Ponytail、验证、会话命名
├── skills/                               技能：带 SKILL.md，按需触发
│   ├── codex-session-namer/
│   │   ├── SKILL.md
│   │   ├── agents/openai.yaml
│   │   └── references/research.md        命名规则的官方资料依据
│   ├── opencodex-install-win/
│   │   ├── SKILL.md
│   │   ├── agents/openai.yaml
│   │   ├── references/troubleshooting.md OAuth / ENAMETOOLONG / 端口 / 回滚
│   │   └── scripts/install-opencodex.ps1 一键安装脚本
│   ├── remote-device-coding/
│   │   ├── SKILL.md                      规则较长，未拆分 references
│   │   └── agents/openai.yaml
│   └── x-article-cat-visual/
│       ├── SKILL.md
│       ├── README.md                     包内文件清单与安装说明
│       ├── assets/ragdoll-ip-reference.jfif
│       ├── references/visual-spec.md     角色、语义、色卡、质检
│       ├── references/session-history.md 已画主题，防重复
│       └── scripts/export_image.py       等比例导出 + 像素校验
├── prompts/                              给人复制的提示词，不参与自动加载
│   ├── skill-self-iteration.md
│   └── x-article-cat-visual.md
└── README.md
```

## 三类内容的分界

| 类别 | 生效方式 | 加载时机 | 判断依据 |
|---|---|---|---|
| `coding-agents/` | 放进 Agent 全局配置目录 | 每次会话常驻 | 不是技能，没有 `SKILL.md` |
| `skills/` | 放进技能搜索路径，或把路径告知 Agent | 由 `description` 命中触发，一次只加载一个 | 目录下有 `SKILL.md` |
| `prompts/` | 人工整段复制进对话 | 由人决定 | 没有 frontmatter 与自动触发能力 |

同一套规则可以有技能版和提示词版两份载体（`x-article-cat-visual` 就是如此）：技能版按需加载、能带脚本；提示词版单段可复制，适合没有 Skills 目录的纯对话环境。两边改动时需要手动同步。

## 技能详解

### codex-session-namer｜会话标题规范化

**解决的问题**：会话越积越多，标题全是"继续优化""处理一下"，事后无法检索。

**核心机制**：标题固定为 `真实项目简称 | 动作+核心对象`，半角竖线两侧各一个空格，整条约 28 字符。

真正的工作量不在格式，而在**识别项目身份**：

- 证据按优先级取：用户明说的名称 → `git remote get-url origin` → `package.json`/`pyproject.toml`/`go.mod` 等清单 → README、部署配置、命名空间 → 仓库根目录名（仅低置信度线索）。
- 明确排除：Codex 项目/工作区名、当前路径文件夹名、服务器 IP/主机名/SSH 别名、`backend`/`frontend`/`src`/`worktree` 这类通用目录名。
- 同一个 Codex 项目里可能有多个代码项目、也可能跨多台服务器，必须结合 `hostId` 与工作目录逐个判断，不能套用同一个项目名；仅当同名不同项目会产生歧义时才追加最短限定词。

**内容字段**：优先写已完成的结果而不是宽泛动作，动词从新增/修复/优化/重构/排查/设计/迁移/升级/审查/整理中取，核心对象要带可检索的业务名词（`退款回调`、`登录性能`）。反例也写在技能里：`修改代码`、`处理问题`、`继续开发`。

**边界**：只做命名，不做归档、删除、移动、分组；用户只要建议时不实际改名。

`references/research.md` 记录了规则来源：OpenAI 的 Projects and Chats（一个会话一个明确结果）、Codex App Server（重命名走产品能力而非改内部存储）、`git-remote` 文档（远端名比本地目录名稳定）。

### opencodex-install-win｜Windows 安装 OpenCodex

**解决的问题**：npm 装完 CLI 不等于能用——后台服务不继承代理环境变量，OAuth 直接失败；CC-Switch 的路由还会和 OpenCodex 抢 `config.toml`。

**核心机制**（`scripts/install-opencodex.ps1` 一次跑完）：

1. 校验 Windows、Node.js 18+、npm；确认代理端点可达（未监听只警告，不阻断）。
2. 代理变量**只写在当前进程**，让 `ocx service install` 把它们固化进计划任务包装器 `~/.opencodex/opencodex-service.cmd`，脚本结束前恢复原值——不污染机器级/用户级环境。
3. `ocx service restart` 强制用新定义重启，避免把旧进程的健康状态当成成功。
4. 校验包装器里确实含 `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY`，并检查 `ocx health --json` 的 `ok` 为真。
5. 仅当 root 是 `model_provider = "openai-http"`（CC-Switch 特征）时才迁移：备份 `config.toml.before-opencodex-<时间戳>.bak` → 切到内置 `openai` → 保留原 provider 表以便回滚 → `ocx sync` → 断言出现 `openai_base_url = "http://127.0.0.1:10100/v1"`，并还原用户原有的 `service_tier`。识别到其他外部 provider 时只警告，不动。

**最容易混的两个端口**：`10100` 是 OpenCodex 的监听端口，`7890` 是代理工具的 HTTP/Mixed **出口**端口。只开 SOCKS 端口不满足默认配置。

**OAuth 永远是用户动作**：脚本最后只打印 `ocx account login codex --device`，不等待、不捕获、不存储设备码、邮箱、`auth.json`、API token。

**排障**（`references/troubleshooting.md`）：交互 shell 有代理但包装器没有 → 进程级设变量后 `ocx service repair` + restart；`ENAMETOOLONG` 往往是假报错，先看 `service status`/`health`，必要时 `ocx stop` → 等 12 秒 → `Start-ScheduledTask`；用 `Get-NetTCPConnection` 确认端口归属，不懂的进程不杀、不建重复计划任务；回滚只恢复确切路径的单个 `.bak`，不用通配符批量删除。

> 这是本仓库唯一以英文正文编写的技能，便于直接分享给非中文环境。

### remote-device-coding｜在 WSL / 远端设备上改代码

**解决的问题**：用户要求"不要修改本地项目"，但 Agent 习惯在 Windows 工作区搜索、改文件、跑测试，最后把本地结果当成远端结果汇报。

**核心机制**：先把目标环境定为唯一工作区——Windows 侧只发命令、看输出、存草稿。

- **模式判定**：说"本机 WSL / Ubuntu 子系统"→ Local WSL，用 `wsl.exe -d <发行版>`，不索要 IP、SSH 用户或密码；给出 IP / 主机名 / 跳板机 → SSH Remote；两者同时出现时分别标明"代码环境"和"运行环境"。
- **Ready Gate**：网络可达只是第一步。必须同时确认发行版已启动与 `uname -a`/`whoami`/`pwd` 一致、SSH 已登录与 `hostname`/`whoami`/`pwd` 一致、项目与子目录存在、已看 `git status --short`、读写权限探测通过（`touch .codex_write_probe && rm -f`）、`/tmp` 可写且 `git apply --check` 可执行、已理解入口与调用链。全部满足才允许输出固定结论：`目标项目连接成功且代码理解完成。`
- **连接方式表**：免密 OpenSSH → 交互登录 → Paramiko（密码只在内存变量，脚本放系统临时目录用完即删）→ `SSH_ASKPASS` → `sshpass`/`plink` → 跳板机 → HTTP 只读检查（只能看健康/日志，不能声称看过代码）→ 公网握手失败先查安全组与 Fail2Ban。
- **跳板机拓扑**：先分清代码机、运行机、跳板机、本地目录四个角色；本机直连看到的目录与历史不一致时，不要继续部署，改从跳板机视角重新确认。
- **改法**：所有写入落在目标环境；远端优先 `/tmp/*.patch` + `git apply --check && git apply`，改完看 `git diff`；验证必须在同一环境跑，Windows 上的 SDK 和工具链不算数。
- **安全规则**：密码/私钥/token 不进技能、仓库、补丁、长期脚本；不创建本地镜像副本再改；先看目标 `git status` 避免覆盖他人未提交改动；刻意采用的最小实现用 `ponytail:` 注释标明原因、限制和升级路径。

技能里还带 Quick Reference 与 Common Mistakes 两张表，多数问题能在表里一行对上。

### x-article-cat-visual｜X 文章布偶猫 IP 配图

**解决的问题**：连续给 X 文章配图，最容易退化成"同一张蓝色科幻壁纸"——猫永远正面端坐、旁边堆发光卡片，且生图工具输出的尺寸从来不是标称值。

**核心机制**：同一只猫，不同动作，不同故事。

- **身份基准**：`assets/ragdoll-ip-reference.jfif` 是用户上传的原始参考图，优先级高于任何文字描述；历史生成图不能反过来当标准。蓝眼睛、奶油白长毛、浅灰棕重点色（耳、脸外侧、蓬松尾）、小粉鼻、圆润幼态脸。
- **先动作后场景**：把文章观点翻译成有因果的具体事件，先定"行为目的 + 身体动作 + 互动对象 + 情绪 + 镜头"，再搭场景。低动态主题也要有真实行为（伸爪翻页、歪头检查），不靠跳跃凑动感。
- **防重复是硬约束**：比对 `references/session-history.md`，新图至少改变行为、场景、机位、主体位置、互动对象、情绪中的三个维度；点名警惕云端跳跃、漂浮科技卡片、左暗右亮对比、桌前坐姿。
- **双模式尺寸**：封面 5:2 → 2000×800 PNG（备选 1920×768），宽幅电影构图，主体避开四周约 10%；内插图 16:9 → 1920×1080 PNG，聚焦一个知识点，不做封面缩小版。
- **文字默认关闭**：仅用户要求时加一行标题 + 每侧一个短标签，文案必须来自正文，不编造 Benchmark 和数字；模型写错字就改用排版工具叠字。
- **尺寸必须实测**：`scripts/export_image.py` 用 Pillow 做 EXIF 校正 + LANCZOS 等比例裁切，源图比例误差超过 8% 直接拒绝（要求重新构图/扩图），导出后重新打开断言宽高与 PNG 格式，打印 `VERIFIED: ... is 2000x800 PNG`，并提醒仍需人工视觉质检。禁止非等比例拉伸。
- **不许虚报**：没读过文件尺寸就不能说"已达标"；工具不支持导出就如实给原始像素；没访问到参考图就不能说"角色完全一致"。

`references/visual-spec.md` 存角色细则、语义→视觉对照表、五元组、画幅表、色卡（`#8FC9F5` 天空蓝、`#FFF7ED` 奶油白、`#B5A6A2` 浅灰棕、`#EFA7AC` 鼻尖粉等）与质检项；`session-history.md` 记录已画主题与"未来优先改变的元素"。该技能没有 `agents/openai.yaml`，靠 `SKILL.md` 的 `description` 触发。

## 提示词模板

| 文件 | 用途 | 怎么用 |
|---|---|---|
| `prompts/skill-self-iteration.md` | Skill 自迭代改造指南。四步：理解现有 Skill（工作地图 / 工具能力 / 验证机制 / 反馈机制）→ 与用户确认验收标准（每轮最多 3 问，优先从历史资料找答案）→ 实施改造（结构化 / 工具化 / 可验证 / 可改进）→ 测试与交付（回归对比，区分「自动验证 / AI 评估 / 人工确认 / 未验证」四类状态） | 复制给能读写 Skill 文件的 Agent，同时告诉它目标路径；要求先诊断再动手 |
| `prompts/x-article-cat-visual.md` | X 文章配图完整提示词 V4.0（A–J 十节：输入惯例、猫咪身份、语义分析、动作导演、防重复、双模式尺寸、文字策略、美术风格、内部质检、输出方式） | 粘贴到新会话的自定义指令或首条消息，上传布偶猫参考图后按文末模板发送文章 |

`skill-self-iteration.md` 的核心主张值得单独记一句：**优先修工具、检查项和好样例，而不是不断加提示词**；没有证据不宣称验证通过。

## 安装与使用

**全局约定**：把 `coding-agents/codex/AGENTS.md` 的内容合并进全局 `AGENTS.md`（通常 `~/.codex/AGENTS.md`）。它是常驻规则，合并前建议先看一遍，避免和现有约定冲突。

**技能**：把整个技能目录复制到对应 Agent 的技能搜索路径，或直接把 `SKILL.md` 路径告诉 Agent。技能只提供方法与流程，不打包依赖：

| 技能 | 需要的外部能力 |
|---|---|
| `codex-session-namer` | 能列出并重命名 Codex 会话（App Server / 会话管理能力） |
| `opencodex-install-win` | Windows + PowerShell 7 + Node.js 18+ + npm；代理工具（Clash/Mihomo/Vortex 等） |
| `remote-device-coding` | `wsl.exe` 或 OpenSSH；可选 Paramiko、`sshpass`/`plink`；目标环境自带构建链 |
| `x-article-cat-visual` | 生图工具；可选 Python + Pillow（做精确尺寸导出） |

**提示词**：打开对应 `.md` 整段复制。注意提示词不会携带图片像素，换会话要重新上传参考图。

## 结构与命名约定

```text
<skill-name>/
├── SKILL.md              必需：YAML frontmatter（name、description）+ 主工作流
├── README.md             可选：包内文件清单与安装说明
├── agents/openai.yaml    可选：display_name、short_description、default_prompt
├── references/           可选：按需加载的深度资料
├── assets/               可选：固定素材
└── scripts/              可选：可复用脚本
```

- `description` 必须写清**触发条件**，这是技能被选中的唯一依据。
- `SKILL.md` 只放主流程和验收条件；长表格、官方依据、排障细节下沉到 `references/`，避免每次加载都占满上下文。
- 有身份基准素材（参考图、样例）时放 `assets/`，并在 `SKILL.md` 里写明它是基准、历史产物不能反推为标准。
- 目录名与代码标识符用英文 kebab-case；正文默认中文（`opencodex-install-win` 例外）。

## 安全边界

- 密码、私钥、Token、`auth.json`、设备码不进入本仓库、脚本、补丁、提交说明或日志。
- OAuth 授权、设备码输入、配额刷新、账号同意始终由用户本人完成，Agent 只把命令交回去。
- 代理环境变量只做进程级注入并恢复，不擅自改成用户级或机器级。
- 远端操作先看目标 `git status`；改前改后都看 `git diff`；不覆盖他人未提交改动。
- 日志、账号文件按敏感数据处理，报告里不放未脱敏内容。

## 维护约定

- 只收录实际用过、验证有效的条目，不写未落地的设计。
- 优先修工具与检查项，其次修好样例，最后才加提示词。
- 新增或移动目录后同步本文件的目录树、索引表和依赖表。
- 同一规则存在技能版与提示词版双载体时，两边一起改。
- 技能正文变更后，连同 `agents/openai.yaml` 的展示文案一起校对，避免"说的"和"做的"不一致。
