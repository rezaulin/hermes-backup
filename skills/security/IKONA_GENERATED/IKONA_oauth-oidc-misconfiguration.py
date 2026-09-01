#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/oauth-oidc-misconfiguration

Skill: SKILL: OAuth and OIDC Misconfiguration — Redirects, PKCE, Scopes, and Token Binding
Desc : >-

Run:  python hack-skills-oauth-oidc-misconfiguration.py --help
      python hack-skills-oauth-oidc-misconfiguration.py --list
      python hack-skills-oauth-oidc-misconfiguration.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/oauth-oidc-misconfiguration'
TITLE = 'SKILL: OAuth and OIDC Misconfiguration — Redirects, PKCE, Scopes, and Token Binding'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: oauth-oidc-misconfiguration", "description: >-", "OAuth and OIDC misconfiguration testing playbook. Use when reviewing redirect URI handling, state and nonce validation, PKCE, token audience, callback binding, and identity-provider trust flaws."],
    'skill-oauth-and-oidc-misconfiguration-redirects-pkce-scopes-and-token-binding': [],
    '1-when-to-load-this-skill': ["Load when:", "- The app supports `Login with Google`, GitHub, Microsoft, Okta, or other IdPs", "- You see `authorize`, `callback`, `redirect_uri`, `code`, `state`, `nonce`, or `code_challenge`", "- Mobile or SPA clients rely on OAuth or OIDC flows", "For token cryptography and JWT header abuse, also load:", "- [jwt oauth token attacks](../jwt-oauth-token-attacks/SKILL.md)"],
    '2-high-value-misconfiguration-checks': [],
    '3-quick-triage': ["1. Map the full flow: authorize, callback, token exchange, logout.", "2. Replay callback flows with altered `state`, `nonce`, and `redirect_uri`.", "3. Compare SPA, mobile, and web clients for weaker validation.", "4. Check whether one provider account can be rebound to another local account."],
    '4-related-routes': ["- CORS or cross-origin token exposure: [cors cross origin misconfiguration](../cors-cross-origin-misconfiguration/SKILL.md)", "- XML federation or enterprise SSO: [saml sso assertion attacks](../saml-sso-assertion-attacks/SKILL.md)", "- CSRF-heavy login or binding bugs: [csrf cross site request forgery](../csrf-cross-site-request-forgery/SKILL.md)"],
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