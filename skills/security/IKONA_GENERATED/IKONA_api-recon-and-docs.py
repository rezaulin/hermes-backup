#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/api-recon-and-docs

Skill: SKILL: API Recon and Docs — Endpoints, Schemas, and Version Surface
Desc : >-

Run:  python hack-skills-api-recon-and-docs.py --help
      python hack-skills-api-recon-and-docs.py --list
      python hack-skills-api-recon-and-docs.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/api-recon-and-docs'
TITLE = 'SKILL: API Recon and Docs — Endpoints, Schemas, and Version Surface'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: api-recon-and-docs", "description: >-", "API reconnaissance and documentation review playbook. Use when discovering endpoints, schemas, versions, OpenAPI specs, hidden docs, and surface area for API testing."],
    'skill-api-recon-and-docs-endpoints-schemas-and-version-surface': [],
    '1-primary-goals': ["1. Discover all reachable API entrypoints.", "2. Extract schemas, optional fields, and role differences.", "3. Identify old versions, mobile paths, GraphQL endpoints, and undocumented parameters."],
    '2-recon-checklist': [],
    'javascript-and-client-mining': ["```bash", "curl https://target/app.js | grep -oE '(/api|/rest|/graphql)[^\"'\\'' ]+' | sort -u"],
    'common-documentation-and-schema-paths': ["```text", "/swagger.json", "/openapi.json", "/api-docs", "/docs", "/.well-known/", "/graphql"],
    'version-and-product-drift': ["```text", "/api/v1/", "/api/v2/", "/api/mobile/v1/", "/legacy/"],
    '3-what-to-extract-from-docs': ["- optional and undocumented fields", "- admin-only request examples", "- deprecated endpoints that may still be active", "- schema hints like `additionalProperties: true`", "- parameter names tied to filtering, sorting, IDs, roles, or tenancy"],
    '4-next-routing': [],
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