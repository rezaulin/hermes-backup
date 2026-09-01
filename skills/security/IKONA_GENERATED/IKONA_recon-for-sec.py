#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/recon-for-sec

Skill: Recon and Methodology Router
Desc : >-

Run:  python hack-skills-recon-for-sec.py --help
      python hack-skills-recon-for-sec.py --list
      python hack-skills-recon-for-sec.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/recon-for-sec'
TITLE = 'Recon and Methodology Router'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: recon-for-sec", "description: >-", "Entry P1 category router for reconnaissance and methodology. Use when mapping", "scope, discovering assets, fingerprinting technology, building endpoint", "inventory, and choosing the first high-value security testing path."],
    'recon-and-methodology-router': ["This is the starting router for new targets and unknown attack surfaces."],
    'when-to-use': ["- You just received a new target and do not yet know what to test first", "- You need to begin with asset discovery, tech fingerprinting, endpoint inventory, and test-route planning", "- You want to build follow-up testing on structured methodology instead of random payload enumeration"],
    'skill-map': ["- [Recon and Methodology](../recon-and-methodology/SKILL.md)", "- [Insecure Source Code Management](../insecure-source-code-management/SKILL.md) \u2014 .git/.svn/.hg exposure detection", "- [Dependency Confusion](../dependency-confusion/SKILL.md) \u2014 Supply chain reconnaissance for internal package names"],
    'recommended-flow': ["1. First confirm in-scope assets and target type", "2. Then perform asset discovery, port/service identification, technology fingerprinting, and endpoint collection", "3. Route based on collected findings to [api-sec](../api-sec/SKILL.md), [auth-sec](../auth-sec/SKILL.md), [injection-checking](../injection-checking/SKILL.md), or [business-logic-vuln](../business-logic-vuln/SKILL.md)"],
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