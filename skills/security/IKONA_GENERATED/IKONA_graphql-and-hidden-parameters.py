#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/graphql-and-hidden-parameters

Skill: SKILL: GraphQL and Hidden Parameters — Introspection, Batching, and Undocumented Fields
Desc : >-

Run:  python hack-skills-graphql-and-hidden-parameters.py --help
      python hack-skills-graphql-and-hidden-parameters.py --list
      python hack-skills-graphql-and-hidden-parameters.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/graphql-and-hidden-parameters'
TITLE = 'SKILL: GraphQL and Hidden Parameters — Introspection, Batching, and Undocumented Fields'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: graphql-and-hidden-parameters", "description: >-", "GraphQL and hidden parameter testing playbook. Use when exploring introspection, batching, undocumented fields, hidden parameters, schema abuse, and GraphQL authorization gaps."],
    'skill-graphql-and-hidden-parameters-introspection-batching-and-undocumented-fields': [],
    '1-graphql-first-pass': ["```graphql", "query { __typename }", "query {", "__schema {", "types { name }", "If introspection is restricted, continue with:", "- field suggestions and error-based discovery", "- known type probes like `__type(name: \"User\")`", "- JS and mobile bundle route extraction"],
    '2-high-value-graphql-tests': [],
    '3-hidden-parameter-discovery': ["Look for:", "- fields present in admin docs but not public docs", "- `additionalProperties` or permissive schemas", "- frontend code using richer request bodies than visible UI controls", "- mobile endpoints carrying role, org, feature-flag, or internal filter fields"],
    '4-next-routing': ["- If hidden fields affect privilege: [api authorization and bola](../api-authorization-and-bola/SKILL.md)", "- If GraphQL batching changes auth or rate behavior: [api auth and jwt abuse](../api-auth-and-jwt-abuse/SKILL.md)", "- If endpoint discovery is incomplete: [api recon and docs](../api-recon-and-docs/SKILL.md)"],
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