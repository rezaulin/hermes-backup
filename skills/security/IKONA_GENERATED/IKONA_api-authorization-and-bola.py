#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/api-authorization-and-bola

Skill: SKILL: API Authorization and BOLA — Object Access, Function Access, and Mass Assignment
Desc : >-

Run:  python hack-skills-api-authorization-and-bola.py --help
      python hack-skills-api-authorization-and-bola.py --list
      python hack-skills-api-authorization-and-bola.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/api-authorization-and-bola'
TITLE = 'SKILL: API Authorization and BOLA — Object Access, Function Access, and Mass Assignment'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: api-authorization-and-bola", "description: >-", "API authorization and BOLA testing playbook. Use when APIs expose object identifiers, nested resources, hidden writable fields, or weak function-level authorization."],
    'skill-api-authorization-and-bola-object-access-function-access-and-mass-assignment': [],
    '1-core-test-loop': ["1. Create Account A and Account B.", "2. As Account A, capture create, read, update, and delete flows.", "3. Replay with Account B's token.", "4. Test sibling endpoints, nested endpoints, and alternate HTTP verbs."],
    '2-test-surfaces': [],
    '3-quick-payloads': ["```json", "{\"role\":\"admin\"}", "{\"isAdmin\":true}", "{\"org\":\"target-company\"}", "{\"verified\":true}"],
    '4-what-testers-miss': ["- object IDs in headers, cookies, GraphQL args, and nested objects", "- alternate methods sharing the same route but weaker authz", "- parent check present, child resource check missing", "- admin docs revealing extra writable fields"],
    '5-next-routing': ["- For JWT or token-layer abuse: [api auth and jwt abuse](../api-auth-and-jwt-abuse/SKILL.md)", "- For GraphQL and hidden parameter discovery: [graphql and hidden parameters](../graphql-and-hidden-parameters/SKILL.md)", "- For broader IDOR patterns outside APIs: [idor broken object authorization](../idor-broken-object-authorization/SKILL.md)"],
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