#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/saml-sso-assertion-attacks

Skill: SKILL: SAML SSO and Assertion Attacks — Signature Validation, Binding, and Trust Confusion
Desc : >-

Run:  python hack-skills-saml-sso-assertion-attacks.py --help
      python hack-skills-saml-sso-assertion-attacks.py --list
      python hack-skills-saml-sso-assertion-attacks.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/saml-sso-assertion-attacks'
TITLE = 'SKILL: SAML SSO and Assertion Attacks — Signature Validation, Binding, and Trust Confusion'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: saml-sso-assertion-attacks", "description: >-", "SAML SSO assertion attack playbook. Use when testing signature validation, assertion wrapping, audience restrictions, ACS handling, XML trust boundaries, and enterprise SSO flaws."],
    'skill-saml-sso-and-assertion-attacks-signature-validation-binding-and-trust-confusion': [],
    '1-when-to-load-this-skill': ["Load when:", "- Enterprise SSO uses SAML requests or responses", "- You see `SAMLRequest`, `SAMLResponse`, XML assertions, or ACS endpoints", "- Login flows involve an external IdP and browser POST/redirect binding"],
    '2-high-value-misconfiguration-checks': [],
    '3-quick-triage': ["1. Capture one full login round trip.", "2. Inspect which XML nodes are signed and which attributes drive account binding.", "3. Compare SP-initiated and IdP-initiated flows.", "4. Test replay, altered attributes, and assertion placement confusion."],
    '4-related-routes': ["- XML parser attack depth: [xxe xml external entity](../xxe-xml-external-entity/SKILL.md)", "- OAuth or OIDC SSO alternatives: [oauth oidc misconfiguration](../oauth-oidc-misconfiguration/SKILL.md)", "- Auth boundary issues after SSO: [authbypass authentication flaws](../authbypass-authentication-flaws/SKILL.md)"],
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