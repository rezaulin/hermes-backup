#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/api-sec

Skill: API Security Router
Desc : >-

Run:  python hack-skills-api-sec.py --help
      python hack-skills-api-sec.py --list
      python hack-skills-api-sec.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/api-sec'
TITLE = 'API Security Router'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: api-sec", "description: >-", "Entry P1 category router for API security. Use when choosing between API", "recon, authorization, token abuse, and hidden-parameter workflows before any", "deeper API topic skill."],
    'api-security-router': ["This is the routing entry point for API security testing.", "Use this skill first to decide whether the API issue is mostly recon/docs, object authorization, token trust, or GraphQL/hidden parameters, then route to a deeper topic skill."],
    'when-to-use': ["- The target exposes REST APIs, mobile backends, or GraphQL endpoints", "- You need to define API testing order before going into specific topics", "- You want to handle object authorization, JWT, GraphQL, and hidden fields as separate tracks"],
    'skill-map': ["- [API Recon and Docs](../api-recon-and-docs/SKILL.md): OpenAPI, Swagger, version drift, hidden documentation", "- [API Authorization and BOLA](../api-authorization-and-bola/SKILL.md): BOLA, BFLA, method abuse, hidden writable fields", "- [API Auth and JWT Abuse](../api-auth-and-jwt-abuse/SKILL.md): bearer token, header trust, claim abuse, rate-limit bypass", "- [GraphQL and Hidden Parameters](../graphql-and-hidden-parameters/SKILL.md): introspection, batching, undocumented fields, hidden parameters"],
    'quick-triage': [],
    'recommended-flow': ["1. Start with exposed endpoints and documentation assets", "2. Then evaluate object-level and function-level authorization", "3. Then evaluate token, header, signature, and rate-limit boundaries", "4. If GraphQL or complex JSON is present, continue with hidden fields and schema abuse"],
    'related-categories': ["- [auth-sec](../auth-sec/SKILL.md)", "- [business-logic-vuln](../business-logic-vuln/SKILL.md)", "- [recon-for-sec](../recon-for-sec/SKILL.md)"],
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