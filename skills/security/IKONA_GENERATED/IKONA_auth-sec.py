#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/auth-sec

Skill: Authentication and Authorization Router
Desc : >-

Run:  python hack-skills-auth-sec.py --help
      python hack-skills-auth-sec.py --list
      python hack-skills-auth-sec.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/auth-sec'
TITLE = 'Authentication and Authorization Router'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: auth-sec", "description: >-", "Entry P1 category router for authentication and authorization. Use when", "testing login flows, sessions, object authorization, JWT, OAuth, CORS, CSRF,", "and enterprise SSO weaknesses before any deeper auth topic skill."],
    'authentication-and-authorization-router': ["This is the routing entry point for authentication, sessions, and authorization boundaries.", "Use it to decide whether the issue is mainly login mechanics, object-level authorization, browser trust boundaries, or identity protocols such as OAuth/JWT/SAML before going deeper."],
    'when-to-use': ["- The target includes login, registration, password reset, 2FA, sessions, JWT, OAuth, or SSO", "- You suspect object authorization flaws, cross-tenant access, cross-origin reads, CSRF, or protocol misconfiguration", "- You need to decide whether to test authentication or authorization first"],
    'skill-map': ["- [Authentication Bypass](../authbypass-authentication-flaws/SKILL.md): login bypass, password reset, 2FA, enumeration, brute-force protections", "- [IDOR Broken Object Authorization](../idor-broken-object-authorization/SKILL.md): IDOR, BOLA, BFLA, missing object permissions", "- [JWT OAuth Token Attacks](../jwt-oauth-token-attacks/SKILL.md): algorithm confusion, key trust issues, claim abuse, token forgery", "- [OAuth OIDC Misconfiguration](../oauth-oidc-misconfiguration/SKILL.md): redirect URI, state, nonce, PKCE, account binding", "- [CSRF Cross Site Request Forgery](../csrf-cross-site-request-forgery/SKILL.md): CSRF tokens, SameSite, JSON CSRF, login CSRF", "- [CORS Cross Origin Misconfiguration](../cors-cross-origin-misconfiguration/SKILL.md): reflected Origin, credentialed cross-origin reads, allowlist bypass", "- [SAML SSO Assertion Attacks](../saml-sso-assertion-attacks/SKILL.md): assertion wrapping, signature validation, audience, ACS boundaries"],
    'recommended-flow': ["1. First confirm the authentication model and session boundaries", "2. Then confirm object-level and function-level authorization", "3. Then move to token, cross-origin, and protocol details", "4. If enterprise federation exists, continue with OAuth, OIDC, or SAML topics"],
    'related-categories': ["- [api-sec](../api-sec/SKILL.md)", "- Default credentials, username variants, wordlist sizing, and port focus are consolidated in [authbypass-authentication-flaws](../authbypass-authentication-flaws/SKILL.md)"],
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