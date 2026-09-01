#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/api-auth-and-jwt-abuse

Skill: SKILL: API Auth and JWT Abuse — Token Trust, Header Tricks, and Rate Limits
Desc : >-

Run:  python hack-skills-api-auth-and-jwt-abuse.py --help
      python hack-skills-api-auth-and-jwt-abuse.py --list
      python hack-skills-api-auth-and-jwt-abuse.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/api-auth-and-jwt-abuse'
TITLE = 'SKILL: API Auth and JWT Abuse — Token Trust, Header Tricks, and Rate Limits'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: api-auth-and-jwt-abuse", "description: >-", "API authentication and JWT abuse playbook. Use when testing bearer tokens, API keys, claim trust, header spoofing, rate limits, and API auth boundary weaknesses."],
    'skill-api-auth-and-jwt-abuse-token-trust-header-tricks-and-rate-limits': [],
    '1-token-triage': ["Inspect:", "- `alg`, `kid`, `jku`, `x5u`", "- role, org, tenant, scope, or privilege claims", "- issuer and audience mismatches", "- reuse of mobile and web tokens across products"],
    '2-quick-attack-picks': [],
    '3-hidden-fields-and-batch-abuse': [],
    'mass-assignment-field-picks': ["```text", "isAdmin", "admin", "verified", "permissions", "owner"],
    'rate-limit-and-batch-abuse-picks': ["```text", "X-Forwarded-For: 1.2.3.4", "X-Real-IP: 5.6.7.8", "Forwarded: for=9.9.9.9", "GraphQL or JSON batch abuse candidates:", "- arrays of login mutations", "- bulk object fetches with varying IDs", "- repeated password reset or verification calls in one request"],
    '4-rate-limit-bypass-families': ["```text", "X-Forwarded-For", "X-Real-IP", "Forwarded", "User-Agent rotation", "Path case / slash variants"],
    '5-next-routing': ["- For GraphQL batching and hidden parameters: [graphql and hidden parameters](../graphql-and-hidden-parameters/SKILL.md)", "- For default credential and brute-force planning: [authentication bypass](../authbypass-authentication-flaws/SKILL.md)", "- For full JWT and OAuth depth: [jwt oauth token attacks](../jwt-oauth-token-attacks/SKILL.md)", "- For OAuth or OIDC configuration flaws in browser and SSO flows: [oauth oidc misconfiguration](../oauth-oidc-misconfiguration/SKILL.md)", "- For credentialed browser reads and origin trust bugs: [cors cross origin misconfiguration](../cors-cross-origin-misconfiguration/SKILL.md)"],
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