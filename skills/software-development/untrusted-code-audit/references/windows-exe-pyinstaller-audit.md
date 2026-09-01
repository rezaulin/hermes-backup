# Auditing Windows EXE "tools" that ship without source

Common in farming/utility tool repos: a big `.exe` + config files + README claiming it's a
Python script, but no `.py` in the repo. Do NOT run it. Extract and read instead.

## Triage recipe

1. **Repo red-flag sweep first** (cheap, often conclusive):
   - `git log --oneline --all` — single commit, one author, no issues/CI = repack.
   - `git log -1 --format='%an <%ae>'` — note author; check `https://api.github.com/users/<login>` + `/repos/<owner>/<repo>` for stars/forks/pushed_at anomalies.
   - File inventory: EXE present but no matching source? `requirements.txt` describing code that isn't published? Classic malware-distribution shape.

2. **Identify packer:** `file tool.exe` + check PyInstaller magic:
   ```python
   f = open('tool.exe','rb').read()
   print(b'MEI\x0c\x0b\x0a\x0b\x0e' in f)      # PyInstaller
   print(f[-64:])                                # trailing names often show pythonXY.dll
   ```

3. **Extract:** `git clone extremecoders-re/pyinstxtractor && python3 pyinstxtractor.py tool.exe`
   - Creates `tool.exe_extracted/` with the entry-point `*.pyc` beside the bootstrap pycs.
   - PYZ archive skips extraction when your Python version ≠ build version (note the build
     version from the banner, e.g. "Python version: 3.13"). String analysis still works.

4. **Static sweep of the entry-point pyc** (no execution needed):
   ```bash
   strings -n 6 tool.pyc | head -200                                  # imports, UI text, config keys
   strings -n 6 tool.pyc | grep -oE "https?://[^ \"']+" | sort -u     # ALL outbound URLs
   strings -n 5 tool.pyc | grep -iE "subprocess|os\.system|powershell|cmd\.exe|schtasks|reg add|startup|socket|base64|exec\("
   strings -n 6 tool.pyc | grep -iE "discord|webhook|telegram|pastebin|ngrok|interact\.sh|upload|send_"
   ```
   Cross-check every URL against README claims. `subprocess` appearing only next to
   `webdriver_manager.core.os_manager` = chromedriver extraction, legitimate.

5. **Hidden-payload check:** list extracted contents; legitimate bundles contain only known
   libs (selenium, requests, PIL, numpy...). Flag: extra .pyc beyond entry+bootstrap,
   unexpected `.py`/`.pyd`, random-looking dirs.

6. **Full decompile (optional, version-sensitive):** unmarshal 3.13 pycs needs a 3.13
   interpreter (`uv python install 3.13` then run decompyle tooling against the main pyc).
   If the sandbox blocks installs, string-table analysis is usually enough for a verdict —
   say so explicitly and recommend network egress allowlisting if the user still wants to run it.

## Verdict template

Report claim-by-claim: exfiltration endpoints (found/not), persistence (registry/startup/schtasks),
exec sinks and their context, URL list vs README claims, repo trust signals. Obfuscated ≠ malware,
but "EXE-only repo repacked by an unknown author" is always a run-under-restriction verdict:
disposable machine + egress allowlist + never feed it real credentials before the sweep passes.

## Case log

- 2026-08-23 `pood1e/gmail-account-creator` (Gmail Creator Pro, 52 MB PyInstaller 3.13 EXE,
  sha256 daef0372…): clean — URLs only accounts.google.com signup + 5sim.net API + warming
  sites; subprocess only via webdriver-manager; no webhook/persistence. Verdict: usable in a
  disposable Windows sandbox with egress allowlist; repo is a repack of ShadowHackr's tool.
