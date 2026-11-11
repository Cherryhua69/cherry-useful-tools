---
name: opencodex-install-win
description: Use when installing, migrating, repairing, or configuring OpenCodex on Windows with npm, Task Scheduler background startup, replacing CC-Switch routing, a local HTTP proxy such as 127.0.0.1:7890, or Codex device OAuth errors.
---

# Install OpenCodex on Windows

Install the official npm package, bake the requested outbound proxy into the Windows background service, and verify observable health. Keep OpenCodex's listener (normally `10100`) distinct from the outbound proxy port (commonly `7890`).

## Workflow

1. Confirm Windows, Node.js 18+, npm, and the requested proxy endpoint. If Node.js is absent, ask the user to install the current LTS or run `winget install --id OpenJS.NodeJS.LTS`, then reopen PowerShell. Port `7890` is the proxy tool's HTTP/Mixed outbound port; OpenCodex normally listens on `10100`.
2. Read the repository's current `AGENTS_INSTALL.md` when a source checkout is available. Never star the GitHub repository or answer a star prompt for the user.
3. Run `scripts/install-opencodex.ps1`. Override `-ProxyUrl` when needed; use `-NoProxy` only when the user explicitly wants direct egress.
4. Run `ocx service install` by default after setting the process proxy environment so the Task Scheduler wrapper receives `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY`; then restart the service to prove the running process uses the fresh definition.
5. Replace recognized CC-Switch routing after making a timestamped backup of `~/.codex/config.toml`: when the root selection is `model_provider = "openai-http"`, switch it to the built-in `openai`, keep the `[model_providers.openai-http]` table for rollback, then run `ocx sync`. Do not overwrite a different external provider automatically.
6. Verify `ocx --version`, `ocx service status`, `ocx health --json`, and that Codex contains `openai_base_url = "http://127.0.0.1:10100/v1"`. Do not call the installation complete from command output alone if health is false.
7. Always remind the user to set their proxy tool's **HTTP/Mixed port to `7890`** and keep that tool running. OpenCodex is configured for `http://127.0.0.1:7890`; a different or stopped proxy makes upstream requests fail.
8. Finish by returning this command to the user without running it:

```powershell
ocx account login codex --device
```

OAuth authorization, device-code entry, quota refresh, and account consent remain user actions. Do not wait for, capture, transfer, or store credentials, device codes, email addresses, `auth.json`, API tokens, or admin tokens.

## Troubleshooting

Read [references/troubleshooting.md](references/troubleshooting.md) when OAuth reports `OAuth authentication failed`, the service does not inherit the proxy, `ENAMETOOLONG` appears, or the health check fails.

## Quick reference

| Goal | Command |
|---|---|
| Install/upgrade CLI | `npm install -g @bitkyc08/opencodex` |
| Install background startup | `ocx service install` |
| Repair an existing service | `ocx service repair` |
| Inspect service | `ocx service status` |
| Check health | `ocx health --json` |
| Replace CC-Switch routing | Back up `config.toml`, select built-in `openai`, then `ocx sync` |
| User-run OAuth | `ocx account login codex --device` |
| Remove service | `ocx service uninstall` |

Do not persist machine-wide or user-wide proxy variables unless the user explicitly requests that broader change. The installer temporarily sets them in the calling process so OpenCodex can bake them into its own service definition, then restores the prior values.
