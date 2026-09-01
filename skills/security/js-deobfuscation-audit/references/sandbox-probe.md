# Sandbox probe recipe (runtime verification of a deobfuscated script)

Static grep proves what the code CAN do; a sandbox run proves what it DOES.

## Setup

```bash
mkdir -p /tmp/<name>-run && cp <name>/server.js /tmp/<name>-run/
cd /tmp/<name>-run
printf 'KEY1=dummy\nAPI_KEY=testkey123\nPORT=4455\n' > .env
ln -sf /tmp/<name>/node_modules node_modules   # reuse installed deps, don't reinstall
```

Start via Hermes `terminal(background=true)` — NOT `nohup ... &` (the terminal tool blocks shell-level background wrappers; background=true gives a trackable session_id you can poll/kill).

## Probe sequence

1. **Boot banner** — poll process output. Express apps often print their own endpoint list on startup — free route documentation.
2. **Unauthenticated vs authenticated** — hit every endpoint twice: bare, and with the dummy API key header. Expect 401 without key; confirms the auth middleware actually gates.
3. **Dummy-token error paths** — endpoints that call the real upstream API (e.g. payment gateway) will return the upstream's "invalid token" error. That PROVES the request path without touching real data.
4. **State-mutating endpoints with dummy data** — POST to create/update endpoints; verify they return success shapes and log events.
5. **Watch the logs** — the sandbox run's own log lines reveal behavior the code hides (e.g. a Telegram send attempt failing = notification wiring exists even if docs don't mention it).

## Gotchas observed

- Epoch unit mismatch: if a log prints year 58609, the API expects seconds, not milliseconds (or vice versa). Note it as a bug for the report.
- `curl -X POST ... -d '{"startTime":'$(date +%s)'000"}'` — command substitution inside -d works fine for probing.
- Clean up: kill the background process, `rm -rf /tmp/<name>-run`. Never leave dummy servers listening.
