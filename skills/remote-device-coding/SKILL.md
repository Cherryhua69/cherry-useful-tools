---
name: remote-device-coding
description: Use when modifying code in local WSL projects, LAN servers, embedded Linux devices, SSH-only build machines, or remote project directories while explicitly avoiding edits to the Windows/local workspace.
---

# Remote Device Coding

## Overview

在本机 WSL、局域网服务器或嵌入式设备上改代码时，把用户指定的目标环境和项目目录当成唯一工作区：Windows 本地只用于发起命令、记录输出和临时草稿，不修改本地项目代码。

核心原则：先识别目标模式，再连通和定位项目，然后理解目标环境中的代码、最小改动并在同一环境验证。

## Target Mode

先根据用户表述选择模式，不要把本机 WSL 当成 SSH 服务器：

- 用户说“本机 WSL”“WSL 里的项目”“Ubuntu 子系统”或给出 WSL 发行版/路径时，使用 **Local WSL** 模式，通过 Windows 的 `wsl.exe` 在指定发行版内执行操作；不索要 `host`、SSH 用户名或 SSH 密码。
- 用户给出 IP、主机名、SSH 用户、跳板机或远端设备路径时，使用 **SSH Remote** 模式，遵循后文 SSH 流程。
- 两种信息同时出现时，以用户明确指定的代码所在环境为准；代码在 WSL、服务运行在远端时，要分别标明“代码环境”和“运行环境”，不能把两边的路径或验证结果混为一谈。

## Workflow

1. 明确目标：确认目标模式、发行版或远端连接信息、目标环境内的项目路径、具体子目录、需求和“不修改 Windows/本地项目”的边界。
2. 连通性检查：Local WSL 用 `wsl.exe --list --quiet` 和目标发行版内的无副作用命令；SSH Remote 用 `ping` / `Test-NetConnection` / `ssh -o BatchMode=yes`。不要把密码写入技能、仓库、脚本或日志文件。
3. 进入目标项目：在选定环境内执行 `pwd`、`ls`、`git status --short`、`git branch --show-current`，确认实际路径和工作区状态。
4. 理解代码：在目标环境内使用 `rg`、`find`、`grep`、构建脚本和测试配置定位调用链；不要在 Windows 本地项目目录复制或改写同名文件。
5. 修改代码：所有写入必须发生在目标环境的项目路径内。SSH Remote 优先生成远端补丁并用 `git apply --check && git apply`；Local WSL 直接调用发行版内已有的编辑/补丁工具，小改动前后都查看 diff。
6. 验证结果：在同一目标环境运行最小可行验证，例如单测、编译、lint、目标模块构建或命令行自检。
7. 汇报交付：说明目标模式、发行版或远端主机、实际项目路径、改了什么、执行了哪些验证、是否有未提交改动，以及无法验证的原因。

## Ready Gate

发现 WSL 发行版或目标服务器网络可达只代表第一步成功。调用本技能后，只有同时满足下面条件，才可以继续代码修改或回复“连接成功”：

- Local WSL：目标发行版能启动，并确认发行版名称、`uname -a`、`whoami`、`pwd` 与用户目标一致。用户未指定发行版时，可以使用默认发行版；存在多个发行版且默认项无法确定对应项目时，先通过只读检查定位，仍有歧义再询问用户。
- SSH Remote：SSH 登录成功，并确认 `hostname`、`whoami`、`pwd` 与用户给定目标一致。
- 目标项目路径存在，目标子目录存在，能执行 `ls` / `find` / `rg` 等只读代码检索。
- 已检查项目工作区状态，例如 `git status --short`；如果不是 Git 项目，要说明用什么方式追踪改动。
- 已确认目标项目具有必要读写权限：能读取关键源码，能在项目目录或允许的临时目录创建和删除探测文件。
- 已确认补丁写入路径可用：能写入目标环境的 `/tmp` 或项目允许的临时补丁文件，并能执行 `git apply --check` 或等价检查。
- 已理解目标代码结构：至少确认入口文件、相关模块、调用链、构建/运行脚本、验证方式，以及本次需求可能影响的文件范围。
- 如果权限不足、路径不一致、代码理解不完整或只能 HTTP 访问，只能回复具体阻塞原因，不能说“目标项目连接成功且代码理解完成”。

权限探测要使用无害文件名，并立即清理：

```bash
cd /path/to/project
touch .codex_write_probe && rm -f .codex_write_probe
tmp_patch="/tmp/codex_patch_probe_$$.patch"
printf '' > "$tmp_patch" && rm -f "$tmp_patch"
```

完成 Ready Gate 后，回复必须包含这句话：

```text
目标项目连接成功且代码理解完成。
```

## Local WSL Mode

当用户要求连接本机 WSL 及其中的项目时，直接通过 `wsl.exe` 操作，不走 SSH，不在当前 Windows 工作区执行项目命令。优先使用用户给出的 Linux 绝对路径；如果只给项目名，先在发行版的常用项目根目录中做有限深度只读查找，再用 Git 元数据和项目配置确认，不要扫描整个文件系统。

PowerShell 示例：

```powershell
$Distro = "Ubuntu"
$Project = "/home/cherryhua/projects/example"
wsl.exe --list --quiet
wsl.exe -d $Distro -- bash -lc "uname -a && whoami && cd '$Project' && pwd && git status --short && git branch --show-current"
```

执行规则：

- 用户明确给出发行版时始终使用 `wsl.exe -d <发行版> -- ...`，避免命令落到另一个默认发行版。
- 用户只说“本机 WSL”且只有一个可用发行版时，可直接使用该发行版；有多个发行版时，先只读检查默认发行版和候选项目位置，不凭发行版名称猜项目归属。
- 用户给出 `/home/...`、`/opt/...` 等 Linux 路径时按原路径进入；给出 `C:\...` 等 Windows 路径时，只有用户明确表示目标项目位于挂载盘时才转换为 `/mnt/c/...`。
- 项目位于 WSL 的 Linux 文件系统时，不要通过 `\\wsl$\...` 或 Windows 编辑器路径修改，统一在发行版内执行读写命令，保持权限、符号链接和换行规则一致。
- 需要应用补丁时，可从 Windows 通过标准输入传给 WSL 内的 `git apply --check` / `git apply`，或在 WSL 的 `/tmp` 创建临时补丁；不要先修改 Windows 同名项目再复制覆盖。
- 所有搜索、修改、测试和 Git 检查都必须显式绑定同一发行版和同一项目路径。每次独立命令都重新 `cd` 到目标项目，不依赖前一条命令保留工作目录。

如果用户只提供项目名，可按实际用户名和常见根目录缩小查找范围，例如：

```powershell
$Distro = "Ubuntu"
$ProjectName = "example"
wsl.exe -d $Distro -- bash -lc "find ~/projects ~/work ~/src -maxdepth 3 -type d -name '$ProjectName' 2>/dev/null"
```

找到多个候选目录时，比较 `git remote -v`、仓库根目录和项目清单；无法唯一确认时再请用户指定，不在多个候选项目中同时执行写操作。

## Command Pattern

PowerShell 本地发起远端只读检查：

```powershell
$HostName = "192.168.1.132"
$UserName = "ztl"
$Project = "/home/ztl/ks_face_recognition"
Test-Connection -ComputerName $HostName -Count 2 -Quiet
ssh "$UserName@$HostName" "cd '$Project' && pwd && git status --short"
```

如果环境没有可非交互输入密码的 SSH 工具，说明限制并请用户在交互终端完成登录、配置 SSH key，或提供可用的安全连接方式。不要假装已经登录成功。

## Connection Methods

根据历史任务，按下面顺序选择连接方式。每一种方式都只用于本次任务，不把密码写入仓库、技能或长期脚本。

| 方式 | 适用场景 | 做法 |
| --- | --- | --- |
| OpenSSH 免密 | 用户已配置 SSH key，或已在服务器授权公钥 | `ssh -o BatchMode=yes user@host "hostname && pwd"`，成功后继续远端操作 |
| OpenSSH 交互登录 | 用户愿意在终端手动输入密码 | 让用户执行 `ssh user@host` 完成首次登录或授权公钥；Codex 不能接管另一个已登录的 cmd 会话 |
| Paramiko 密码登录 | 本机没有 `sshpass/plink`，但 Python 有 `paramiko` | 用临时 Python 脚本建立 SSH/SFTP，只在内存变量里使用用户当次提供的密码；脚本放系统临时目录，用完删除 |
| `SSH_ASKPASS` 临时授权 | Windows OpenSSH 可用，需自动执行一次密码认证或写入公钥 | 创建临时 askpass 脚本，通过环境变量喂本次密码，执行完立即删除；不要把脚本放项目目录 |
| `sshpass` / `plink` | 机器已安装这些工具，用户允许本次自动密码登录 | 仅在临时命令或临时脚本中使用，避免进入长期文件；优先禁用公钥误试：`PreferredAuthentications=password` |
| 跳板机 / 构建机 | 目标设备只能从另一台服务器访问，或本机直连看到的文件系统不对 | 先登录跳板机，再从跳板机 SSH 到目标机；必要时用 `ProxyCommand` / `nc`，并明确区分“代码机”“运行机”“日志机” |
| HTTP 只读检查 | SSH 凭据不对，但服务端口可访问 | 只做健康接口、日志接口或页面状态检查；不能据此宣称已检查远端代码 |
| 公网服务器握手失败 | 22 端口可连但 `kex_exchange_identification` 或 `ssh-keyscan` 失败 | 先让用户通过云控制台检查安全组、防火墙、Fail2Ban、`sshd` 状态，再授权公钥 |

### Paramiko 临时脚本模式

当用户明确提供账号密码、且本机没有 `sshpass/plink` 时，可以用 Paramiko 做只读检查或 SFTP 补丁写入。脚本必须放在系统临时目录，执行后删除。

```python
import paramiko

host = "192.168.x.x"
user = "user"
password = "use-runtime-secret-only"
project = "/path/to/project"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password, timeout=10)
stdin, stdout, stderr = client.exec_command(f"cd {project!r} && pwd && git status --short")
print(stdout.read().decode("utf-8", "replace"))
print(stderr.read().decode("utf-8", "replace"))
client.close()
```

实际执行时不要把真实密码写入技能或项目文件；如果需要临时脚本，脚本结束后清理。

### Jump Host Pattern

历史任务里常见这种拓扑：

```text
本机 -> 1.155 测试/代理机 -> 2.133 构建机 -> 目标运行目录
```

处理这类任务时先画清楚角色：

- 代码机：真正修改和编译代码的位置。
- 运行机：服务实际运行、日志和数据库所在位置。
- 跳板机：只负责连通，不默认等于代码机。
- 本地目录：只用于查看上下文，除非用户明确要求，否则不修改。

如果本机直连某个 IP 看到的目录和历史记录不一致，不要继续部署；改从已知跳板机视角重新确认 `hostname`、`ip addr`、`pwd`、目标目录和进程。

## Remote Edit Pattern

在远端应用补丁时使用可回滚路径：

```bash
cd /home/ztl/ks_face_recognition
git status --short
cat >/tmp/change.patch <<'PATCH'
diff --git a/path/file.c b/path/file.c
--- a/path/file.c
+++ b/path/file.c
@@
 old line
+new line
PATCH
git apply --check /tmp/change.patch && git apply /tmp/change.patch
git diff -- path/file.c
```

复杂改动可以先把补丁写到远端 `/tmp`，检查通过后再应用。避免用本地 `apply_patch` 修改工作区文件，因为那会改到本机，不是目标服务器。

## Safety Rules

- 不把密码、私钥、token 写入技能、仓库、提交说明、补丁或长期文件。
- 不在本地项目目录创建镜像副本后修改；如需临时下载只读文件，放到系统临时目录并标明仅供分析。
- 目标项目已有未提交改动时先汇报；只改任务相关文件，不覆盖他人改动。
- 修改前后都看 `git diff`；涉及生成物、SDK、交叉编译产物时先确认项目约定。
- Bug 修复先定位根因；新功能先做最小可运行实现。
- 在目标环境新增或改动的方法、函数、类、复杂逻辑块要写中文注释；简单 getter、常量或一眼可懂的一行逻辑不强行注释。
- 如果刻意采用最小实现且有已知上限，在代码注释里用 `ponytail:` 标明原因、限制和未来升级路径。

## Quick Reference

| 场景 | 做法 |
| --- | --- |
| 连接本机 WSL 项目 | `wsl.exe -d <发行版> -- bash -lc "cd '<项目路径>' && pwd && git status --short"` |
| 只给 WSL 项目名 | 在 `~/projects`、`~/work`、`~/src` 等有限范围查找，再用 Git 和项目元数据确认 |
| 只确认设备在线 | `ping` / `Test-Connection`，再测 22 端口 |
| 确认远端项目 | `ssh user@host "cd /path && pwd && ls"` |
| 确认读写权限 | `touch .codex_write_probe && rm -f .codex_write_probe` |
| 确认代码理解 | 找到入口、模块、调用链、构建脚本和验证方式 |
| 查代码 | `ssh user@host "cd /path && rg 'keyword' subdir"` |
| 看远端改动 | `ssh user@host "cd /path && git diff --stat && git diff"` |
| 应用改动 | 远端 `/tmp/*.patch` + `git apply --check` |
| 验证 | 在目标环境运行项目已有测试、构建或最小复现命令 |
| 密码自动登录 | 优先 Paramiko / 临时 `SSH_ASKPASS`，用完删除临时脚本 |
| 经跳板机访问 | 先确认跳板机和目标机角色，再用 `ProxyCommand` 或跳板机侧临时脚本 |

## Current Request Shape

当用户给出类似信息时触发本技能：

```text
服务器：192.168.1.132
用户名：ztl
远端项目：/home/ztl/ks_face_recognition
目标子目录：Hisi3516DV500_COMC.870.990.V2.0.3.sdk200.DevKit_glibc_shandong
要求：不要修改本地项目代码
```

把这些值视为本次任务参数，不要固化到技能之外；尤其不要保存密码。

本机 WSL 示例：

```text
连接本机 WSL 的 Ubuntu
项目：/home/cherryhua/projects/AI_generated
要求：后续搜索、修改和验证都在这个 WSL 项目中执行
```

## Common Mistakes

- 用户说本机 WSL 后仍索要 IP、SSH 用户名或密码：应切换到 Local WSL 模式并使用 `wsl.exe`。
- 在 Windows 当前目录执行搜索、修改或测试，再把结果当成 WSL 项目结果：所有项目操作必须在指定发行版和项目路径内执行。
- 多个 WSL 发行版时默认选一个并写入：先确认发行版与项目目录的对应关系。
- 把 Windows 路径机械转换为 `/mnt/<盘符>`：先确认项目确实位于挂载盘，而不是 WSL Linux 文件系统中的同名项目。
- 在本地仓库搜索到同名目录后直接改本地文件：应改远端项目。
- 只 ping 通就说“已连接”：必须区分网络在线、SSH 端口可达、登录成功、项目路径存在。
- 只确认服务器可达就开始改：必须先确认目标项目读写权限、文件操作权限和代码理解完成。
- 只看了目录树就说理解代码：至少要确认入口、调用链、构建/运行脚本和可验证方式。
- 为了方便把密码写进脚本：改用交互登录、SSH key、会话缓存或用户确认的安全工具。
- 未查看远端 `git status` 就应用补丁：可能覆盖别人的未提交改动。
- 验证只在 Windows 当前目录运行：WSL 或远端中的 SDK、工具链和系统库才是目标环境。
