#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-html-injection

Skill: Cybermes Skill
Desc : Hunt HTML Injection — user-supplied input is rendered as raw HTML in the response without sanitisation, allowing an attacker to inject arbitrary HTML tags (but not necessarily JavaScript). Lower severity than XSS but enables phishing, UI manipulation, and credential harvesting via injected forms. Use when testing text-display surfaces (search results, profile fields, comments, error messages, feedback forms). For markup that executes JavaScript, escalate to hunt-xss.

Run:  python claude-bughunter-hunt-html-injection.py --help
      python claude-bughunter-hunt-html-injection.py --list
      python claude-bughunter-hunt-html-injection.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-html-injection'
TITLE = 'Cybermes Skill'
DESCRIPTION = 'Hunt HTML Injection — user-supplied input is rendered as raw HTML in the response without sanitisation, allowing an attacker to inject arbitrary HTML tags (but not necessarily JavaScript). Lower severity than XSS but enables phishing, UI manipulation, and credential harvesting via injected forms. Use when testing text-display surfaces (search results, profile fields, comments, error messages, feedback forms). For markup that executes JavaScript, escalate to hunt-xss.'

PAYLOADS = {
    'main': ["name: hunt-html-injection", "description: \"Hunt HTML Injection \u2014 user-supplied input is rendered as raw HTML in the response without sanitisation, allowing an attacker to inject arbitrary HTML tags (but not necessarily JavaScript). Lower severity than XSS but enables phishing, UI manipulation, and credential harvesting via injected forms. Use when testing text-display surfaces (search results, profile fields, comments, error messages, feedback forms). For markup that executes JavaScript, escalate to hunt-xss.\""],
    'what-is-html-injection': ["HTML Injection occurs when user input is inserted into a page's HTML without escaping, so injected tags are rendered by the browser as markup rather than displayed as literal text. Unlike XSS, the injected content does not require JavaScript execution \u2014 injecting `<b>`, `<h1>`, `<a>`, `<img>`, or `<form>` tags is sufficient.", "**To PROVE impact unambiguously, escalate to an active vector carrying a unique numeric canary** \u2014 e.g. `\"><img src=x onerror=alert(91234)>` or `<svg onload=alert(91234)>`. A distinctive 4+ digit number (not `alert(1)`) distinguishes YOUR reflected injection from the example payloads practice pages embed in their own hint text. Proof = the raw, unescaped vector with your canary appears in the response.", "**Impact:**", "- Phishing via injected `<form>` or `<a href=\"attacker.com\">` tags", "- UI defacement \u2014 `<h1>HACKED</h1>` renders visually on the page", "- Credential harvesting via injected login forms", "- Redirect via `<meta http-equiv=\"refresh\">`", "- Stepping stone to XSS (may be blocked by WAF on `<script>` but not `<img onerror>`)"],
    'attack-surface': ["Any input that is reflected or stored and then displayed in an HTML context:", "- Search boxes (`?q=`)", "- Comments, feedback, reviews", "- Profile fields (name, bio, username)", "- Error messages (`?error=`, `?message=`)", "- Subject / body of contact forms", "- Admin-visible fields (ticket titles, usernames in logs)"],
    'autonomous-testing-priority': ["**Inject a recognisable HTML tag with a unique canary string. Unescaped angle brackets in the response = confirmed injection.**", "**Pattern 1 \u2014 Basic HTML tag injection:**", "<b>CANARY</b>", "\"><b>CANARY</b>", "Use a unique string as CANARY (something distinct to this test run). **Proof:** the response contains `<b>CANARY` with literal `<` angle brackets \u2014 not `&lt;b&gt;CANARY`. A properly encoded app would escape `<` to `&lt;`.", "**Try multiple tag types when `<b>` is filtered:**", "- `<h1>CANARY</h1>` \u2014 heading tag (often less filtered)", "- `<img src=x onerror=CANARY>` \u2014 attribute context", "- `<a href=\"https://attacker.com\">click</a>` \u2014 link injection (phishing proof)", "**For stored injection:** inject into the storage endpoint, then GET the page where the value is displayed and check for unescaped tags.", "**Escalate immediately:** if `<b>` injection works, try `<script>alert(1)</script>` \u2014 the same unsanitised input may allow full XSS."],
    'proof': ["Confirmed when your injected tag appears in the response body with literal `<` angle brackets (not HTML-encoded). A safe app renders `&lt;b&gt;CANARY&lt;/b&gt;`; a vulnerable app renders `<b>CANARY</b>`."],
    'distinguishing-html-injection-from-xss': ["- HTML injection: `<b>text</b>` renders as **text** in the browser \u2014 no JS execution needed.", "- XSS: `<script>alert(1)</script>` executes JavaScript.", "Some WAFs block `<script>` but pass `<b>` or `<img>` \u2014 start with non-script tags, then escalate."],
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