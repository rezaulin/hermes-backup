#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-exceptional-conditions

Skill: HUNT-EXCEPTIONAL-CONDITIONS — Verbose Errors / Fail-Open (A10:2025)
Desc : Hunt mishandling of exceptional conditions — feed an endpoint malformed/unexpected input (wrong type, broken JSON, oversized field, null byte) and make it fail OPEN or leak internals: a verbose stack-trace / framework error page that discloses ORM internals, server file paths, library versions, or a language traceback. Use on any input-accepting endpoint (JSON APIs, forms, query params). Medium-High when the leak exposes internal structure that arms a deeper attack.

Run:  python claude-bughunter-hunt-exceptional-conditions.py --help
      python claude-bughunter-hunt-exceptional-conditions.py --list
      python claude-bughunter-hunt-exceptional-conditions.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-exceptional-conditions'
TITLE = 'HUNT-EXCEPTIONAL-CONDITIONS — Verbose Errors / Fail-Open (A10:2025)'
DESCRIPTION = 'Hunt mishandling of exceptional conditions — feed an endpoint malformed/unexpected input (wrong type, broken JSON, oversized field, null byte) and make it fail OPEN or leak internals: a verbose stack-trace / framework error page that discloses ORM internals, server file paths, library versions, or a language traceback. Use on any input-accepting endpoint (JSON APIs, forms, query params). Medium-High when the leak exposes internal structure that arms a deeper attack.'

PAYLOADS = {
    'main': ["name: hunt-exceptional-conditions", "description: \"Hunt mishandling of exceptional conditions \u2014 feed an endpoint malformed/unexpected input (wrong type, broken JSON, oversized field, null byte) and make it fail OPEN or leak internals: a verbose stack-trace / framework error page that discloses ORM internals, server file paths, library versions, or a language traceback. Use on any input-accepting endpoint (JSON APIs, forms, query params). Medium-High when the leak exposes internal structure that arms a deeper attack.\"", "sources: hackerone_public"],
    'hunt-exceptional-conditions-verbose-errors-fail-open-a10-2025': [],
    'what-actually-pays': ["Well-built apps catch errors and return a clean, generic message. A broken app,", "when handed input it didn't expect, throws an unhandled exception and renders a", "**developer error page** straight to the client \u2014 leaking the stack trace, the", "ORM/query internals, server-side file paths, and framework/library versions.", "That disclosure is the finding (and it arms SQLi/RCE/path attacks next)."],
    'recon': ["Any endpoint that parses input is a candidate; the richest are:", "JSON APIs that expect typed fields:  POST /api/* with {numbers, ids, enums}", "Endpoints with numeric/id path or query params:  /item/{id}, ?page=, ?quantity=", "Search / filter / sort params", "File or content-type sensitive uploads"],
    'attack-send-what-the-code-didn-t-anticipate': ["Take a known-good request and break ONE assumption at a time:", "- **Wrong type:** a field the app expects to be a number/string is sent as an", "array or object \u2014 `{\"rating\":\"x\",\"comment\":[1,2,3]}`, `{\"quantity\":{}}`.", "- **Malformed body:** truncated/!invalid JSON, an unterminated string, a stray", "brace, a wrong/missing Content-Type.", "- **Boundary/oversized:** a very long string, a huge/negative/overflow number.", "- **Null byte / control chars** embedded in a value.", "POST /api/Feedbacks   {\"rating\":\"notanumber\",\"comment\":[1,2,3]}", "GET  /item/' OR /item/%00   (also exercises the error path)", "Watch the RESPONSE BODY, not just the status: a 500 (or even a 200/400) whose", "body contains a stack trace or framework error page is the signal."],
    'what-counts-as-a-leak-the-success-signal': ["A finding is confirmed when the response body contains a cross-framework error-disclosure signature:", "- **Node/Express + Sequelize:** `SequelizeDatabaseError`, `node_modules/sequelize`,", "a JS stack with internal paths.", "- **PHP:** `<b>Warning</b> ... /var/www/.../file.php on line N`.", "- **Python:** `Traceback (most recent call last)`, `werkzeug.exceptions`.", "- **Java:** `at com.app.Foo(Foo.java:42)` stack frames.", "- **.NET:** `Server Error in '/' Application`, a `[System.XxxException: ...]` YSOD.", "A clean JSON error (`{\"error\":\"Invalid input\"}`) with no internals is NOT a", "finding \u2014 that's correct handling. Disclosure of internal structure is."],
    'validation-discipline': ["- Capture the exact leaked artifact (path, ORM class, version, stack frame) \u2014", "that's the evidence. \"It returned 500\" alone is not disclosure.", "- Note what the leak enables next (e.g. a disclosed SQL error \u2192 hunt-sqli; a", "disclosed absolute path \u2192 hunt-lfi)."],
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