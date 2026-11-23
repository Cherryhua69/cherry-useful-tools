---
name: opencodex-install-win
description: Use when installing, migrating, repairing, or configuring OpenCodex on Windows with npm, Task Scheduler background startup, replacing CC-Switch routing, a local HTTP proxy, or Codex device OAuth errors.
---

# Install OpenCodex on Windows

Install the official npm package, bake the requested outbound proxy into the Windows background service, and verify observable health. Keep OpenCodex's listener (normally `10100`) distinct from the outbound proxy port.

## Workflow

1. Ask the user for their HTTP/Mixed proxy port (1-65535) if they have not provided it. Wait for the port before installing, configuring, or repairing the service. Use the supplied port on `127.0.0.1` unless the user specifies another host. Confirm Windows, Node.js 18+, and npm.
2. Read the repository's current `AGENTS_INSTALL.md` when a source checkout is available. Never star the GitHub repository or answer a star prompt for the user.
3. Run `scripts/install-opencodex.ps1 -ProxyUrl "http://127.0.0.1:<port>"` with the confirmed endpoint and explicit port.
4. The installer writes the proxy to the Task Scheduler wrapper, restarts the service, and checks health and wrapper contents. For repair, follow the troubleshooting reference and use the same confirmed endpoint.
5. Replace recognized CC-Switch routing after making a timestamped backup of `~/.codex/config.toml`: when the root selection is `model_provider = "openai-http"`, switch it to the built-in `openai`, keep the `[model_providers.openai-http]` table for rollback, then run `ocx sync`. Do not overwrite a different external provider automatically.
6. Report separate evidence for the wrapper endpoint, service status and `ocx health --json`. If CC-Switch was migrated, also verify the active Codex route. A TCP listener check only verifies reachability. Report upstream requests or OAuth as unverified unless separately observed.
7. Report the configured proxy endpoint and remind the user to keep their proxy tool running on that HTTP/Mixed port.
8. Finish by returning this command to the user without running it:

```powershell
ocx account login codex --device
```

OAuth authorization, device-code entry, quota refresh, and account consent remain user actions. Do not wait for, capture, transfer, or store credentials, device codes, email addresses, `auth.json`, API tokens, or admin tokens.

## Troubleshooting

Read [references/troubleshooting.md](references/troubleshooting.md) when OAuth reports `OAuth authentication failed`, the service does not inherit the proxy, `ENAMETOOLONG` appears, or the health check fails. After changing the port or repairing the wrapper, recheck the endpoint, wrapper and service health. Record the failing stage and sanitized evidence when a check fails.

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
