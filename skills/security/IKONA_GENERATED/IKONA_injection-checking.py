#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/injection-checking

Skill: Injection Testing Router
Desc : >-

Run:  python hack-skills-injection-checking.py --help
      python hack-skills-injection-checking.py --list
      python hack-skills-injection-checking.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/injection-checking'
TITLE = 'Injection Testing Router'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: injection-checking", "description: >-", "Entry P1 category router for injection testing. Use when routing between XSS,", "SQLi, SSRF, XXE, SSTI, command injection, and NoSQL injection workflows based", "on how attacker-controlled input is consumed."],
    'injection-testing-router': ["This is the routing entry point when input reaches a dangerous interpreter or execution environment.", "After confirming this is an injection-class issue, use it to decide whether it is mainly browser context, database, template engine, server-side requests, XML parsing, or system commands."],
    'when-to-use': ["- Input reaches HTML, JS, SQL, templates, URL fetchers, XML parsers, or shell", "- You have not yet decided whether to start with XSS, SQLi, SSRF, XXE, SSTI, CMDi, or NoSQL", "- You need to choose the correct deep-topic skill based on input flow"],
    'skill-map': ["- [XSS Cross Site Scripting](../xss-cross-site-scripting/SKILL.md)", "- [SQLi SQL Injection](../sqli-sql-injection/SKILL.md)", "- [SSRF Server Side Request Forgery](../ssrf-server-side-request-forgery/SKILL.md)", "- [XXE XML External Entity](../xxe-xml-external-entity/SKILL.md)", "- [SSTI Server Side Template Injection](../ssti-server-side-template-injection/SKILL.md)", "- [CMDi Command Injection](../cmdi-command-injection/SKILL.md)", "- [NoSQL Injection](../nosql-injection/SKILL.md)", "- [Deserialization Insecure](../deserialization-insecure/SKILL.md)", "- [JNDI Injection](../jndi-injection/SKILL.md)", "- [Expression Language Injection](../expression-language-injection/SKILL.md)", "- [CRLF Injection](../crlf-injection/SKILL.md)", "- [Extra Injection Types (SSI, LDAP, XPath)](./EXTRA_INJECTION_TYPES.md)", "- [Request Smuggling](../request-smuggling/SKILL.md)", "- [Prototype Pollution](../prototype-pollution/SKILL.md)", "- [Type Juggling](../type-juggling/SKILL.md)", "- [HTTP Parameter Pollution](../http-parameter-pollution/SKILL.md)", "- [XSLT Injection](../xslt-injection/SKILL.md)", "- [CSV Formula Injection](../csv-formula-injection/SKILL.md)"],
    'recommended-flow': ["1. First identify the final sink of the input", "2. Then choose the topic skill that best matches that interpreter", "3. Small payload samples and quick triage are merged into each main skill; no extra payload router is needed"],
    'related-categories': ["- [file-access-vuln](../file-access-vuln/SKILL.md)"],
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