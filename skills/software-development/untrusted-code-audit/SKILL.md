---
name: untrusted-code-audit
description: "Audit untrusted/obfuscated code (JS packages, PyInstaller .exe binaries, payment scripts, third-party repos/zips) before deployment: deobfuscate with webcrack, extract PyInstaller archives with pyinstxtractor, pattern-scan for exfiltration, sandbox-run and probe endpoints. Includes evaluation checklist for unofficial payment gateways."
tags: [security, audit, deobfuscation, payment-gateway, due-diligence, pyinstaller, binary-analysis]
triggers:
  - audit code
  - is this safe
  - obfuscated
  - deobfuscate
  - review before deploy
  - unofficial payment gateway
  - analisa script
  - cek exe
  - check exe
  - exe-only repo
---

# Untrusted Code Audit

Use when the operator shares code from an unknown author that will touch credentials or money (payment gateways, WA bots, scrapers), especially when source is obfuscated. Goal: verify each safety claim in the README against actual code, then verdict.

**Repo ships ONLY an .exe (no source)? That is a PyInstaller/PE audit, not a JS audit — branch at step 2 to the binary path below.** Full recipe: `references/pyinstaller-exe-audit.md`.

## Workflow

1. **Clone/extract + inventory.** Find entry points, note obfuscation. One huge single `server.js` with `_0x` identifiers + RC4 string arrays = javascript-obfuscator output; original `*-raw.js` usually NOT published. For repos: record `sha256sum` of every binary, `git log --oneline --all`, author identity, commit count, stars/forks — an exe-only repo with 1 commit / 0 forks / pushed_at before created_at is a red flag worth saying out loud (repackage risk).
2. **Deobfuscate / unpack, per artifact type:**
   - **JS:** `npm i -g webcrack && webcrack server.js -o out/` — handles control-flow flattening, string-array RC4, self-defending wrappers (real case: 901 transforms → 596 readable lines). If webcrack struggles: extract the string array with regex and map call sites, or run the code once and dump decoded strings.
   - **PyInstaller .exe:** NEVER run it. `git clone https://github.com/extremecoders-re/pyinstxtractor && python3 pyinstxtractor.py target.exe` → extracts `*_extracted/` with the entry-point `.pyc` + bundled libs. Audit statically: `strings -n 6 <entrypoint>.pyc | grep -oE "https?://..."` (every outbound URL), `strings | grep -iE "subprocess|powershell|schtasks|reg add|webhook|discord|pastebin|ngrok|base64"` (exec sinks & exfil channels). Cross-check each `subprocess` hit against its context — bundling webdriver-manager/selenium makes `subprocess` appear legitimately (chromedriver extract). PYZ decompilation needs the EXACT Python version the exe was built with (e.g. python3.13) — without it, string-table audit is still strong evidence; say so explicitly in the verdict rather than blocking on the version.
3. **Read ALL deobfuscated output** — full read-through is the audit. Don't conclude from greps alone. (For binaries where full decompile is unavailable, the string sweep + dependency inventory is the substitute — list exactly what was NOT verifiable.)
4. **Static pattern sweep:**
   - Execution sinks: `eval|Function(|child_process|exec|spawn` (JS) / `subprocess|os.system|ctypes|win32` (Python)
   - File access (exfil from disk): `fs.|writeFile|readFile|createWriteStream`
   - Hidden payloads: `atob|base64`
   - **Every outbound URL:** `grep -oE "https?://[a-zA-Z0-9._/-]+" | sort -u` — cross-check against README claims; exfil tells: discord webhooks, pastebin, ngrok, interact.sh, .onion
   - **Every env var read:** `grep -oE "process\\.env\\.[A-Z_]+" | sort -u`
   - Cross-check: each secret must flow ONLY to its legitimate destination. (E.g. a "Gmail creator" asking for a 5SIM API key is consistent; the SAME tool also needing Telegram/webhook endpoints is not.)
5. **Sandbox-run it** (skip for EXEs you can't unpack — static verdict only). Dummy `.env`, isolated port, run with real deps, probe every endpoint (with and without auth) and record actual responses — behavior must match README claims. Check **redirects (302)** too: a clean codebase can still leak data via redirect to a third-party renderer (e.g. `api.qrserver.com` receiving full QRIS strings).
6. **Verdict report**, claim-by-claim: exfiltration (found/not), hidden ops, write/file/shell ops, "does X as claimed". Note obfuscation ≠ malware — vendors do it for IP protection; the audit decides trust, not the presence of obfuscation. For a "conditionally usable" verdict on a binary, spell out the deployment protocol: disposable machine (never the main VPS), egress allowlist to only the legit domains, fresh API keys, never run where other credentials live.

## Pitfalls

- Obfuscated code that fails to deobfuscate fully → do NOT bless it; fall back to network-level egress firewall as the trust mechanism and say so.
- API-key-only auth + `CORS origin:*` is a finding to report, not a backdoor.
- State held only in RAM (dedupe maps, logs) → report as operational risk (restart wipes it), separate from security.
- When recommending deployment of audited obfuscated code: deploy the DEOBFUSCATED source you reviewed, not the vendor's blob. For exe-only tools with no source, the deployment protocol (sandbox + egress) IS the trust mechanism — offer "write our own from scratch" as the alternative, but a working audited tool often beats a rewrite.
- `pyinstxtractor` run under a different Python version than the build → it warns and SKIPS PYZ extraction; the entry-point `.pyc` string audit still works (it's a separate archive entry). Don't treat the warning as failure.

## Skill-pack drops (zip of SKILL.md directories) — audit-then-install

A zip named like an "EXPLOIT"/"ARSENAL" pack is usually a **skill library**, not a runnable tool: many dirs each with `SKILL.md` (YAML frontmatter `name:` + `scripts/`/`references/`). Verified 2026-08-30 on the operator's `IKONA EXPLOIT.zip` (1,158 files, 22 skills):

1. **Inventory first**: `unzip -l` — a tree of `SKILL.md` per dir = skill pack, not malware to run.
2. **Static sweep before installing** (same greps as workflow step 4, over `--include="*.py" --include="*.sh"`): outbound URLs (SSRF-payload addresses like `http://0x7f000001` are NORMAL in pentest toolkits — filter them; real exfil = discord/pastebin/ngrok/webhook), `os.environ|process.env` reads, `subprocess|os.system|eval\(` exec sinks. Exec sinks are expected when scripts wrap nuclei/ffuf; file-writes are expected for PoC generators. Clean sweep → safe to install.
3. **Install = `cp -r` the dirs into `~/.hermes/skills/<category>/`**, NOT 22 skill_manage calls (folder tree with scripts/references copies in one shot).
4. **Verify via `skills_list`**; then check each `SKILL.md` frontmatter `name:` — **folder name ≠ skill name** (`IKONA_ARSENAL` → `name: bug-bounty-arsenal`). Same-name skills in the pack **overwrite** earlier same-name skills in the registry (frontmatter `name:` is the key, folder name is cosmetic). Tell the operator which existing skills were replaced.

## Payment-gateway specifics

For unofficial payment gateway scripts, apply `references/payment-gateway-eval.md` — trust anchor, replay/dedup, cancel semantics, ToS risk.
