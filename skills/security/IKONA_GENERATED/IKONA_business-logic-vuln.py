#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/business-logic-vuln

Skill: Business Logic Router
Desc : >-

Run:  python hack-skills-business-logic-vuln.py --help
      python hack-skills-business-logic-vuln.py --list
      python hack-skills-business-logic-vuln.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/business-logic-vuln'
TITLE = 'Business Logic Router'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: business-logic-vuln", "description: >-", "Entry P1 category router for business logic testing. Use when workflow abuse,", "race conditions, pricing flaws, or multi-step state attacks matter more than", "parser-level input injection."],
    'business-logic-router': ["This is the routing entry point for business-logic and state-machine issues."],
    'when-to-use': ["- The target involves coupons, inventory, payment, approvals, quotas, invites, trials, or state transitions", "- The issue is not parser-level; it is about when checks happen and which business conditions are checked", "- You suspect race conditions, workflow bypass, price tampering, negative values, stacked discounts, or multi-step flaws"],
    'skill-map': ["- [Business Logic Vulnerabilities](../business-logic-vulnerabilities/SKILL.md)"],
    'recommended-flow': ["1. First map key business states and one-time actions", "2. Then check for check-then-act windows, sequence dependencies, or missing cross-step authorization", "3. If the chain depends on APIs, uploads, or object permissions, return to the corresponding router skill to complete the path"],
    'related-categories': ["- [api-sec](../api-sec/SKILL.md)", "- [auth-sec](../auth-sec/SKILL.md)", "- [file-access-vuln](../file-access-vuln/SKILL.md)"],
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