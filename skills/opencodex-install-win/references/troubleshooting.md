# OpenCodex Windows troubleshooting

## `OAuth authentication failed`

Check whether the interactive shell has proxy variables while the Task Scheduler wrapper does not:

```powershell
Get-ChildItem Env: | Where-Object Name -Match '^(HTTP_PROXY|HTTPS_PROXY|ALL_PROXY|NO_PROXY)$'
Select-String -Path "$env:USERPROFILE\.opencodex\opencodex-service.cmd" -Pattern 'HTTP_PROXY|HTTPS_PROXY|NO_PROXY'
```

If the wrapper lacks them, use the endpoint explicitly confirmed by the user. Run the example in a disposable PowerShell session so the environment changes end when that session closes. Set the host to the confirmed host if it differs from loopback.

```powershell
$proxyPort = 0
if (-not [int]::TryParse((Read-Host "Enter your HTTP/Mixed proxy port"), [ref]$proxyPort) -or
    $proxyPort -lt 1 -or $proxyPort -gt 65535) {
    throw 'Enter an explicit HTTP/Mixed proxy port between 1 and 65535.'
}
$env:HTTP_PROXY = "http://127.0.0.1:${proxyPort}"
$env:HTTPS_PROXY = $env:HTTP_PROXY
$env:NO_PROXY='localhost,127.0.0.1,::1'
Remove-Item Env:ALL_PROXY -ErrorAction SilentlyContinue
ocx service repair
ocx service restart
```

Verify the wrapper contains the confirmed endpoint and run `ocx service status` and `ocx health --json`. Only the user runs `ocx account login codex --device`.

## `ENAMETOOLONG` during service repair/restart

First inspect actual state; OpenCodex can report the spawn error even when it rewrote the wrapper and the service is healthy:

```powershell
ocx service status
ocx health --json
Select-String -Path "$env:USERPROFILE\.opencodex\opencodex-service.cmd" -Pattern 'HTTP_PROXY|HTTPS_PROXY|NO_PROXY'
```

If the wrapper is correct but the running process is stale, use OpenCodex's supported stop, wait for its respawn guard to finish, then start the existing task:

```powershell
ocx stop
Start-Sleep -Seconds 12
Start-ScheduledTask -TaskName 'opencodex-proxy'
ocx health --json
```

Do not kill an unidentified process or create a duplicate scheduled task.

## Port confusion

The user-specified HTTP/Mixed port belongs to the outbound proxy tool. OpenCodex normally listens on `10100`. Inspect ownership before changing either:

```powershell
$proxyPort = [int](Read-Host "Enter your HTTP/Mixed proxy port")
Get-NetTCPConnection -State Listen -LocalPort $proxyPort,10100 -ErrorAction SilentlyContinue |
    Select-Object LocalAddress,LocalPort,OwningProcess
```

Keep the proxy tool running on the HTTP/Mixed port supplied during installation. A SOCKS-only port cannot serve the configured HTTP proxy URL.

## Replace or roll back CC-Switch

The installer recognizes CC-Switch when the root Codex setting is `model_provider = "openai-http"`. It creates `config.toml.before-opencodex-<timestamp>.bak`, switches Codex to the built-in `openai` provider, retains the old provider table, and runs `ocx sync`.

Verify the active route:

```powershell
Select-String -Path "$env:USERPROFILE\.codex\config.toml" -Pattern '^model_provider|^openai_base_url'
ocx health --json
```

To roll back, stop using OpenCodex first, then restore the timestamped backup only after confirming its exact path. Do not delete all `.bak` files by wildcard.

## Diagnostics

```powershell
ocx doctor
ocx service status
ocx health --json
Get-Content "$env:USERPROFILE\.opencodex\service.log" -Tail 200
```

Treat logs and account files as sensitive. Do not copy credentials or unredacted tokens into reports.
