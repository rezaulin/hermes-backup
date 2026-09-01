# PyInstaller / PE .exe audit recipe (static, never-run)

For repos that ship ONLY a compiled Windows `.exe` (classic mass-account-creator /
trial-farmer / "tool with proprietary UI" pattern). Goal: verdict WITHOUT executing
the binary. Proven 2026-08 on a 52MB PyInstaller Gmail-creator exe.

## 0. Repo & file inventory (5 min)

```bash
git clone --depth 1 <repo> && cd <repo>
sha256sum *.exe                          # record; enables VirusTotal lookup later
git log --oneline --all                  # 1 commit = repackage risk
git log -1 --format='%an <%ae> %ad'      # author identity
file *.exe                               # PE32+ console? PyInstaller?
```

GitHub API reputation check (no auth needed for public data):
```bash
curl -s https://api.github.com/users/<owner>        # created_at, public_repos, followers
curl -s https://api.github.com/repos/<owner>/<repo> # stars/forks/issues, created vs pushed_at
```
Red flags: exe-only repo + requirements.txt claiming "Python source", 1 commit,
0 forks, `pushed_at` earlier than `created_at`, no issues/PRs ever.

## 1. Confirm & extract the PyInstaller archive

```bash
# Magic check (tail of file):
python3 -c "f=open('X.exe','rb').read(); print(b'MEI\x0c\x0b\x0a\x0b\x0e' in f, f[-64:])"
# Last bytes show the bundled pythonNNN.dll → tells you the build Python version.

git clone --depth 1 https://github.com/extremecoders-re/pyinstxtractor.git
cd pyinstxtractor
python3 pyinstxtractor.py /path/to/X.exe
```

Output: `X.exe_extracted/` containing:
- **`<entrypoint>.pyc`** ← the app code. THIS is the audit target.
- `PYZ.pyz` (11MB+ typical) — bundled stdlib/third-party libs; extractable only with the EXACT build Python version (skip; note it).
- `pyi_rth_*.pyc`, `pyimod*.pyc`, `struct.pyc` — PyInstaller boilerplate, ignore.
- `.pyd`/`.dll` and dist-info dirs — dependency inventory.

## 2. String-table audit of the entry point

```bash
cd X.exe_extracted
strings -n 6 <entrypoint>.pyc | head -200        # imports, config keys, UI text
strings -n 6 <entrypoint>.pyc | grep -oE "https?://[^ \"']+" | sort -u   # ALL outbound URLs
strings -n 5 <entrypoint>.pyc | grep -iE \
  "subprocess|os\.system|powershell|cmd\.exe|schtasks|reg add|startup|curl|wget|socket|exec\(" | sort -u
strings -n 5 <entrypoint>.pyc | grep -iE \
  "discord|webhook|telegram|pastebin|ngrok|burpcollab|oast|interact\.sh|\.onion|upload|exfil" | sort -u
```

Interpretation:
- URL list must match README claims (e.g. signup target + phone-verification API +
  browsing "warm-up" sites). Exfil tells: webhooks, paste sites, tunnel domains.
- `subprocess` appearing is NOT automatically malicious: bundled `webdriver-manager`
  uses it to extract chromedriver (`webdriver_manager.core.os_manager` context string
  near the hit). Check the 2-3 strings around each hit.
- Hidden second payload: `find . -maxdepth 2 -name "*.pyc"` — anything besides the
  entrypoint + pyimod/pyi_rth/struct is suspicious; also `ls` the extracted root for
  non-Python blobs.

## 3. What you can & can't conclude

CAN conclude: outbound-URL inventory, exec-sink presence, persistence mechanisms
absent/present, dependency set, config-file surface (what secrets it reads).
CAN'T conclude without the build Python: full control-flow of the `.pyc`, PYZ
contents, runtime behavior. Say this explicitly in the verdict ("static audit —
string-table level, not full decompile") rather than blocking on it.

If the build Python version IS available: `pip install decompyle3/uncompyle6` (version-
dependent — 3.9+ support is spotty; `pycdc` (Decompyle++) works on newer versions).

## 4. Conditional-use deployment protocol

For a "clean static, unrunnable dynamically" verdict, the trust mechanism is the
sandbox, not the code:
- Run ONLY on a disposable machine (never the main VPS; a Freestyle/cloud VM or
  dedicated Windows box).
- Egress allowlist: only the legitimate domains from the URL inventory.
- Feed ONLY fresh/rotatable API keys; output artifacts (accounts.json etc.) are
  treated as untrusted data.
- Offer the operator the alternative of a from-scratch rewrite, but don't push it —
  an audited working tool usually wins for heavy automation (signup flows encode
  many edge cases).

## Observed case (2026-08): pood1e/gmail-account-creator

52MB PyInstaller (Python 3.13) Gmail creator, author "ShadowHackr" (Jordan), repo
repackage (1 commit, no source). Static verdict: clean — URLs only google-signup +
5sim.net + warm-up sites, no webhook/persistence, subprocess = webdriver-manager
only. Conditional-use: disposable Windows + egress allowlist. Feeds a Qoder-Pro
trial-farming pipeline (Gmail supply → device-code OAuth login → token manager).
