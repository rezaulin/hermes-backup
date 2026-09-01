#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-clickjacking

Skill: Cybermes Skill
Desc : Hunt Clickjacking — missing X-Frame-Options / CSP frame-ancestors lets an attacker embed the target page in an invisible iframe and trick victims into clicking buttons they cannot see (UI redressing). Targets: login flows, money transfers, account settings, OAuth confirmation pages. Confirm by fetching the page, then PROVE it frames in a real browser and a sensitive state-changing action survives the cross-site context (SameSite cookies / framebusting JS can defeat it) — header-absence alone is not a finding.

Run:  python claude-bughunter-hunt-clickjacking.py --help
      python claude-bughunter-hunt-clickjacking.py --list
      python claude-bughunter-hunt-clickjacking.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-clickjacking'
TITLE = 'Cybermes Skill'
DESCRIPTION = 'Hunt Clickjacking — missing X-Frame-Options / CSP frame-ancestors lets an attacker embed the target page in an invisible iframe and trick victims into clicking buttons they cannot see (UI redressing). Targets: login flows, money transfers, account settings, OAuth confirmation pages. Confirm by fetching the page, then PROVE it frames in a real browser and a sensitive state-changing action survives the cross-site context (SameSite cookies / framebusting JS can defeat it) — header-absence alone is not a finding.'

PAYLOADS = {
    'main': ["name: hunt-clickjacking", "description: \"Hunt Clickjacking \u2014 missing X-Frame-Options / CSP frame-ancestors lets an attacker embed the target page in an invisible iframe and trick victims into clicking buttons they cannot see (UI redressing). Targets: login flows, money transfers, account settings, OAuth confirmation pages. Confirm by fetching the page, then PROVE it frames in a real browser and a sensitive state-changing action survives the cross-site context (SameSite cookies / framebusting JS can defeat it) \u2014 header-absence alone is not a finding.\""],
    'what-is-clickjacking': ["Clickjacking (UI Redressing) lets an attacker load a target page inside a transparent iframe on a malicious site. The victim sees the attacker's decoy UI but clicks the hidden target UI beneath it. No JavaScript on the target is required.", "**Highest-value targets:**", "- Login / authentication pages \u2014 force login with attacker credentials", "- Money transfer / checkout / \"confirm payment\" buttons", "- Account settings (email change, password change, 2FA disable)", "- OAuth / social-login \"Authorize app\" confirmation dialogs", "- Admin actions (delete, promote user, change role)"],
    'protection-headers': ["Two mechanisms prevent framing:", "X-Frame-Options: DENY              # strongest \u2014 blocks all framing", "X-Frame-Options: SAMEORIGIN        # allows same-origin frames only", "Content-Security-Policy: frame-ancestors 'none'     # CSP equivalent of DENY", "Content-Security-Policy: frame-ancestors 'self'     # CSP equivalent of SAMEORIGIN", "If NEITHER is present, the page is frameable from any origin."],
    'how-to-test': ["Header-absence is the **trigger for investigation, not the finding**. Two steps:", "**Step 1 \u2014 Header check (screening).** Fetch the target page and inspect the response headers:", "curl -sI https://target.example/account/transfer | grep -iE 'x-frame-options|content-security-policy'", "If BOTH `X-Frame-Options` and CSP `frame-ancestors` are absent, the page is a *candidate*. If either is present and restrictive (`DENY`/`SAMEORIGIN`/`frame-ancestors 'none'|'self'`), stop \u2014 it's protected.", "**Step 2 \u2014 Prove it actually frames and clicks (required for a real finding).** Build a minimal PoC and load it in a real browser:", "```html", "<!doctype html>", "<h1>Win a prize \u2014 click below</h1>", "<iframe src=\"https://target.example/account/transfer\"", "style=\"opacity:0.1;position:absolute;top:0;left:0;width:1000px;height:800px\"></iframe>", "Confirm ALL of the following, or it is not exploitable:", "- The page **actually renders inside the iframe** (no framebusting JS that blanks/redirects it \u2014 e.g. `if(top!==self)` breakout, or a `Sec-Fetch-Dest`/JS frame check).", "- The **sensitive action still works while framed** \u2014 critically, the action must succeed *cross-site*. If it relies on a session cookie set `SameSite=Lax` or `SameSite=Strict` (the modern default), the cookie is **not** sent on the cross-site framed request, and the clickjack fails. Verify the victim's authenticated state carries into the frame.", "- The target is a **state-changing action** (transfer, settings/email/password change, 2FA disable, OAuth authorize, admin action), not a read-only page.", "**Strategy:** target the most sensitive action pages first \u2014 severity scales directly with what the victim is tricked into doing."],
    'false-positives': ["- Public, read-only pages (home/marketing) lacking frame protection are low/informational \u2014 no sensitive action to redress.", "- APIs and non-HTML endpoints (JSON, images) are not clickjacking targets.", "- **Header-absence alone is NOT a finding.** SameSite cookies, framebusting JS, or the lack of any sensitive framed action can each fully defeat it \u2014 which is why Step 2 is mandatory."],
    'proof-requirements': ["A valid clickjacking report shows: (1) the target page rendered inside an attacker-controlled iframe in a real browser, (2) a sensitive state-changing action reachable by a framed click while the victim is authenticated (cookies survive the cross-site context), and (3) a screenshot/recording of the overlay. Reporting missing headers with no working frame PoC is a documentation-quality issue, not a vulnerability."],
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