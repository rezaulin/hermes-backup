---
name: third-party-code-audit
description: Audit third-party code drops (zip/repo) before user runs or integrates them — inventory, full source read, syntax check, sandbox run with dummy creds, live endpoint probing, security & trust review (obfuscation, secrets, replay, ToS risk), verdict + hardening list.
tags: [security, code-review, audit, payment-gateway, reverse-engineering]
triggers:
  - analisa zip
  - analisa repo github
  - review script
  - cek script aman
  - bedah source code
  - evaluasi payment gateway
---

# Third-Party Code Audit

User regularly receives/buys/finds third-party scripts (payment gateways, bots, automation tools) and says "analisa" before using or integrating them. Goal: a trust verdict backed by ACTUAL execution, not just reading. Deliverable must be immediately actionable.

## Workflow

1. **Extract & inventory.** Unzip/clone to /tmp. `find <dir> -type f -not -path '*/node_modules/*' -not -path '*/.git/*'`, file sizes (`du -b`), entry points, deps (package.json / go.mod), LICENSE, README. Note zip-with-backslash-paths quirk (Windows-made zips) — unzip still works.
2. **Read everything.** Batch-read ALL sources in one execute_code script (print each file with a header). Never audit from README alone; README claims are hypotheses to verify.
3. **Static checks.** `node --check file.js` per JS file; `go build -o /dev/null ./...` for Go. Diff files claimed to be identical copies across package variants.
4. **Detect obfuscation early.** Signs: single minified server.js, `javascript-obfuscator` in package.json build script, missing "raw" source file. If obfuscated, README security claims ("creds never leave your machine", "zero third-party") are UNVERIFIABLE — that is itself a headline finding. Recover the surface API anyway: regex-extract all quoted strings from the bundle, filter for routes/keywords (`/api|token|qris|POST`...).
5. **Sandbox run with dummy creds.** Copy app to /tmp, write a dummy .env (NEVER user's real tokens), npm install, start via terminal(background=true). Many apps print their own endpoint list on startup — read the banner. Probe every endpoint with curl: with and without auth key, happy path and error path. Kill the process when done (process action=kill).
6. **Security review checklist:**
   - Secrets: hardcoded in source / config templates / examples? Real keys committed?
   - Trust anchor: who can forge a "paid"/success event — the payment network, or the gateway process itself?
   - Webhooks: raw-body HMAC + constant-time compare + timestamp window + dedupe by transaction ID? Missing any = finding.
   - Persistence: in-memory-only state (Maps) = transactions/dedup lost on restart.
   - Cancel semantics: does cancel actually void the payment instrument (QR still payable = orphan funds)?
   - Unofficial-API risk: scraped endpoints / internal session tokens = ToS violation, ban risk, breakage on any upstream change. Note how fragile detection is (regex user-id extraction, empty-field paid heuristic).
   - License: no-resale clauses, copyright headers the user must keep.
7. **Deliverable format** (user preference — embed, don't skip): what it is (1-2 sentences) → how it works (numbered flow) → endpoint/feature table → findings table with severity 🔴🟡🟢 → verdict + concrete hardening list. Casual Indonesian, markdown tables, direct, no hedging. End with a "mau gue apain ini" next-step offer.

## Pitfalls

- Never feed the user's real credentials/tokens into the audit sandbox — dummies only.
- Kill sandbox processes after probing; don't leave test servers listening.
- curl-piped-to-python trips the terminal security scanner — write responses to a file first or parse inside execute_code.
- Obfuscated ≠ malicious. Report as "unauditable/unverifiable" and offer network monitoring as the next verification step, don't accuse.
- Payment drops riding unofficial endpoints (donation APIs, partner-portal session tokens): always rate the ban/breakage risk in the verdict, and credit good anti-rate-limit design when present.

## Prior art

See `references/payment-gateway-patterns.md` for analyzed payment-gateway drops (PG Saweria, ShopeePay Partner gateway) and reusable payment-drop checklist.
