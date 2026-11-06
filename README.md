# 个人常用浓缩的 Skills

个人日常使用的一组 Codex / Agent 技能与提示词模板。内容来自真实任务中的反复踩坑，每个条目都尽量压缩到"能直接执行、不啰嗦"的程度，不为模板完整而堆砌内容。

## 目录结构

```text
skills/
├── codex/
│   └── AGENTS.md                    Codex 全局协作约定
├── codex-session-namer/             技能：会话标题规范化
├── opencodex-install-win/           技能：Windows 上安装配置 OpenCodex
├── remote-device-coding/            技能：在 WSL / 远端 Linux 上改代码
├── prompts/                         提示词模板（非技能）
└── README.md
```

## 目录说明

| 路径 | 类型 | 内容 |
|---|---|---|
| `codex/AGENTS.md` | 全局配置 | 放置到 Codex 全局配置目录后生效的协作约定：默认中文、最小必要变更、Ponytail 实现原则、Bug 修复优先定位根因、验证与注释要求、会话命名规则 |
| `codex-session-namer/` | 技能 | 把会话标题统一成 `真实项目简称 \| 动作+核心对象`。重点在区分「Codex 项目（工作区容器）」与「真实代码项目」，要求用 git remote、项目清单文件等证据判定，禁止用路径名、IP 或 `src`/`backend` 之类通用名当项目名 |
| `opencodex-install-win/` | 技能 | 在 Windows 上安装/修复 OpenCodex：npm 全局安装、计划任务后台启动、代理注入服务包装脚本、替换 CC-Switch 路由并保留回滚备份、健康检查。区分监听端口 `10100` 与出口代理端口 `7890` |
| `remote-device-coding/` | 技能 | 在本机 WSL、局域网服务器、嵌入式设备上改代码，且不修改本地 Windows 工作区。包含目标模式判定、连接后的 Ready Gate 检查清单、跳板机拓扑处理、远端补丁应用与就地验证 |
| `prompts/` | 提示词 | 面向人使用的提示词模板，复制给 Agent 即可，不具备 SKILL.md 结构与自动触发能力 |

## 技能结构约定

带 `SKILL.md` 的目录即为一个技能，遵循 Agent Skills 的通用布局：

```text
<skill-name>/
├── SKILL.md              技能本体：YAML frontmatter（name、description）+ 主工作流
├── agents/openai.yaml    UI 展示信息：display_name、short_description、default_prompt
├── references/           按需加载的深度资料，不进主流程
└── scripts/              可复用脚本（按需，非必需）
```

约定：

- `description` 写明**触发条件**，让 Agent 能判断何时使用。
- `SKILL.md` 只放主流程与验收条件，长细则下沉到 `references/`，避免每次加载都占满上下文。
- 正文中文，目录名与代码标识符用英文 kebab-case。

## 提示词模板

`prompts/` 下的文件是给人看的，不参与技能自动加载：

| 文件 | 用途 |
|---|---|
| `skill-self-iteration.md` | Skill 自迭代改造指南。复制给能读写 Skill 文件的 Agent，并告知目标路径，让它先诊断、再确认验收标准、最后改造 |

## 使用方式

- **技能**：把需要的技能目录放到 Codex / Agent 的技能搜索路径下；或直接把 `SKILL.md` 的路径告知 Agent。
- **全局约定**：将 `codex/AGENTS.md` 的内容合并进全局 `AGENTS.md`。
- **提示词**：打开对应 `.md`，整段复制到对话中。

## 维护约定

- 只收录自己实际用过、验证有效的条目，不写未落地的设计。
- 优先修工具与检查项，而不是不断加提示词。
- 任何密码、私钥、Token、`auth.json` 都不进入本仓库、脚本或日志。
