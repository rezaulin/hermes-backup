---
name: js-deobfuscation-audit
description: "Deobfuscate and security-audit obfuscated/minified JavaScript sources — javascript-obfuscator output, packed bundles, closed-source scripts you must trust or run. Verify exfiltration claims, inventory all outbound URLs, detect eval/shell/fs backdoors."
tags: [security, deobfuscation, audit, javascript, malware-triage, webcrack, obfuscator]
triggers:
  - audit code
  - deobfuscate
  - obfuscated source
  - is this script safe
  - audit obfuscated
  - backdoor check
  - cek aman nggak kodenya
  - review closed-source script
---

# JS Deobfuscation & Security Audit

For analyzing third-party / obfuscated JS before trusting or running it (payment scripts, miners, bot frameworks, closed-source tools a user wants to deploy).

## 1. Deobfuscate

```bash
npm i -g webcrack
webcrack obfuscated.js -o deobf/    # produces deobf/deobfuscated.js
```

- Handles javascript-obfuscator: control-flow flattening, string-array + RC4 encoding, self-defending wrappers, debug protection.
- Check result: `wc -l deobf/deobfuscated.js` — obfuscator output collapses to surprisingly readable, small files (a 66KB obfuscated file became ~600 clean lines).
- If webcrack partially fails, `npx js-deobfuscator` or `npx synchrony` are fallbacks. For multi-layer obfuscation, run webcrack twice.

## 2. Static sweep (the audit checklist)

Run on the DEOBFUSCATED file:

```bash
# Code execution / dynamic payloads — all must be ABSENT
grep -nE "eval|Function\(|child_process|exec|spawn|atob|base64" file.js

# File access — absence means it can't steal .env/keys from disk
grep -nE "writeFile|readFile|unlink|fs\.|createWriteStream" file.js

# COMPLETE outbound URL inventory — this is the core of the audit
grep -oE "https?://[a-zA-Z0-9._/-]+" file.js | sort | uniq -c

# Every secret/env var it reads — then trace each one: where does the value flow?
grep -oE "process\.env\.[A-Z_]+" file.js | sort -u
```

Verdict criteria for "safe":
1. Every secret read from env flows ONLY to its legitimate destination (e.g. merchant token only in requests to the official vendor API).
2. No dynamic code execution primitives.
3. No fs/shell access (can't touch other files even if compromised).
4. URL inventory contains only expected hosts. Flag any "harmless-looking" third party (QR renderers, analytics, image CDNs) — data still transits there.

## 3. Dynamic probe (sandbox run)

Static audit + runtime behavior together are the proof. See `references/sandbox-probe.md` for the exact recipe. Key idea: run it with dummy credentials on a high port, then `curl` every endpoint — well-behaved Express apps print their own route list on boot, and dummy-token errors confirm the auth path without touching real data.

## Pitfalls

- ⚠️ Obfuscation is NOT automatically malware. Commercial scripts obfuscate for IP protection. Report the verdict factually: "obfuscated for IP protection, clean after deobfuscation" — don't FUD.
- ⚠️ Audit the exact commit/file the user will run, not the README's claims. README says "zero third-party"? Verify with the URL grep.
- ⚠️ `curl | grep -oE` for URL extraction from OBFUSCATED source misses RC4-encoded strings — deobfuscate first, then grep.
- ⚠️ Before running a downloaded script: check `package.json` deps too (supply chain), and run with a throwaway `.env`, never real credentials.
- ⚠️ Kill sandbox processes with the process tool, not `kill` from terminal, when Hermes started them via background=true.
