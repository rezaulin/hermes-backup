---
name: bug-bounty-arsenal
description: Bug bounty arsenal v2.5.0 — web2/web3/API hunting toolkit. 11 stdlib-only Python scripts (recon, vulnerability scanner with 35 modules, HAR-to-endpoint parsing, Nuclei/FFUF/Slither/Echidna wrappers, submission tracker, PoC report generator, full pipeline orchestrator) + repo installer for PayloadsAllTheThings/SecLists/ProjectDiscovery/OWASP/DeFi labs. Load for any bug bounty, pentest-on-own-infra, smart contract audit, or recon task.
tags: [bug-bounty, security, pentest, web3, recon, nuclei, ffuf]
required_commands: [python3]
---

# Bug Bounty Arsenal v2.5.0

11 scripts, ~3,000 baris, **stdlib-only Python 3** (no pip installs needed).
External binaries (ffuf, nuclei, slither, echidna, git) are OPTIONAL — scripts
degrade gracefully and say exactly what to install.

**Scope rules (operator's own risk model):** use on programs with explicit
bounty/scope, or on the operator's own infrastructure. Never scan third-party
targets without authorization.

## Scripts (all under `scripts/`)

| Script | Purpose |
|---|---|
| `install-repos.py` | Clone/download PayloadsAllTheThings, SecLists, nuclei-templates, ProjectDiscovery tools, OWASP GenAI/LLM Top 10, DeFi labs (Damn Vulnerable DeFi, Ethernaut), Gitleaks/TruffleHog, etc. Flags: `--all --payloads --web3 --ai --cloud --training` |
| `hunter.py` | Core vulnerability scanner — 35 modules (headers, XSS/SQLi/open-redirect/CORS probes, exposed files, TLS, methods, GraphQL introspection, JS secret extraction, path traversal, SSTI canary, ...). `python3 hunter.py TARGET [--slow] [--modules list] [--endpoints file]` |
| `recon.py` | Recon engine: crt.sh subdomain enumeration, DNS resolve, top-port TCP scan, HTTP(S) alive probe + fingerprint. `python3 recon.py DOMAIN [--ports top100]` |
| `audit-smart-contract.py` | Solidity/Vyper audit: built-in pattern checks (reentrancy, tx.origin, unchecked calls, delegatecall, ...), wraps Slither/Echidna/Medusa when installed. `python3 audit-smart-contract.py FILE_OR_DIR [--slither] [--echidna]` |
| `scanner-nuclei.py` | Nuclei wrapper: tags/severity filter, JSON export, dedupe. `python3 scanner-nuclei.py TARGET --tags critical,high` |
| `ffuf-wrapper.py` | FFUF wrapper: SecLists wordlist selection, extension lists, output parsing. `python3 ffuf-wrapper.py TARGET --wordlist seclists_dir/discovery/...` |
| `har2scan.py` | Parse HAR (browser capture / har-capture) → unique API endpoints (method, params, headers) → optional `--scan` feed straight into hunter. `python3 har2scan.py capture.har [--scan]` |
| `tracker.py` | Local submission & bounty tracker (JSON store): add/update/list/stats findings across programs. `python3 tracker.py add|list|update|stats` |
| `programs.py` | List/search public bug bounty program sources (offline bundled + online fetch when possible). `python3 programs.py [--search keyword]` |
| `huntall.py` | Full pipeline orchestrator: recon → hunter → nuclei → ffuf in one command. `python3 huntall.py TARGET [--full] [--nuclei] [--ffuf] [--har capture.har]` |
| `pocgen.py` | PoC / vulnerability report generator (markdown): severity, steps, impact, remediation templates. `python3 pocgen.py --title "..." --severity high ...` |

## Master workflow

```bash
cd ~/.hermes/skills/security/bug-bounty-arsenal/scripts

# 0. One-time: pull repos & wordlists (needs git)
python3 install-repos.py --all

# 1. Web2 hunt
python3 recon.py target.com
python3 har2scan.py capture.har --scan        # endpoints from real traffic
python3 hunter.py target.com --slow           # deep scan, 35 modules
python3 scanner-nuclei.py target.com --tags critical,high
python3 ffuf-wrapper.py target.com --wordlist ../repos/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt

# 2. Web3 / smart contract audit
python3 audit-smart-contract.py Contract.sol --slither

# 3. One-shot full pipeline
python3 huntall.py target.com --full --nuclei --ffuf --har capture.har

# 4. Track & report
python3 tracker.py add --target target.com --title "Open redirect" --severity medium
python3 pocgen.py --title "Open redirect on target.com" --severity medium
```

**Next.js / React SPA target where `/api/*` probes all 404?** The real endpoint map lives in the JS bundles — recover the axios baseURL + call-site paths in 4 steps (grep chunk paths from rendered pages → download → find `/api/v1` wrapper → grep `.get("/path")` string args), then probe each. Use the **RSC payload trick** (`RSC: 1` header + `Next-Router-State-Tree`) to test if sensitive routes are server-side protected (307→/login) vs client-side-only. The **405→upload→SVG-XSS ladder** finds unauth file uploads (test with valid PNG, then SVG XSS). Full recipe: `references/nextjs-spa-api-extraction.md`.

## Integration points

- `har-capture` skill → produces the `.har` that `har2scan.py` consumes
- `advanced-bug-hunting` → manual exploitation techniques after scanner finds
- `forum-anti-hack` → defensive patching counterpart
- External binaries: ffuf, nuclei, slither, echidna, medusa (installed via `install-repos.py` where possible)

## Gotchas

- All scripts are stdlib-only; they call external tools via subprocess and
  print a clear "install X first" message when missing — never crash silently.
- `hunter.py` probes are NON-destructive canaries (no real payloads written);
  for exploitation use manual techniques from advanced-bug-hunting.
- Repo downloads are ~2GB total with `--all`; use category flags to grab less.
- crt.sh subdomain recon needs internet + can take 30s+; `--skip-crtsh` available.
- TLS checks use the system CA bundle; self-signed targets will show a warning,
  which is itself a finding.
- **SPA / Next.js catch-all returns 200 for EVERY path.** `hunter.py` reporting
  `/.env`, `/.git/config`, `/backup.sql` all "accessible (200)" is a FALSE POSITIVE
  on any SPA — it serves the same HTML shell for unknown routes. Always verify by
  comparing the body to the root page: `curl <target>/.env | head -c 200` — if it's
  the same HTML as `/`, the file is NOT exposed. Report only after body check.
- **Own-infra audit: check bind address, not just nginx routes.** A backend can
  listen on `0.0.0.0` (internet-reachable) while nginx proxies it on `127.0.0.1`
  (safe). On the server run `ss -tlnp` and compare: `0.0.0.0:8085` = exposed HIGH
  finding, `127.0.0.1:8080` = safe. WA gateway / backend API on `0.0.0.0` is a
  common HIGH — fix by binding to `127.0.0.1` so only nginx (public) reaches it.
