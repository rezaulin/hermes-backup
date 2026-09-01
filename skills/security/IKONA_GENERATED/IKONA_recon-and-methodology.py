#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/recon-and-methodology

Skill: SKILL: Recon and Methodology — Expert Bug Bounty Playbook
Desc : >-

Run:  python hack-skills-recon-and-methodology.py --help
      python hack-skills-recon-and-methodology.py --list
      python hack-skills-recon-and-methodology.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/recon-and-methodology'
TITLE = 'SKILL: Recon and Methodology — Expert Bug Bounty Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: recon-and-methodology", "description: >-", "Reconnaissance and methodology playbook. Use when mapping assets, discovering endpoints, fingerprinting technology, and building a structured testing plan for a new target."],
    'skill-recon-and-methodology-expert-bug-bounty-playbook': [],
    '1-recon-hierarchy': ["Target Selection", "\u2514\u2500\u2500 Scope Definition (in-scope assets)", "\u2514\u2500\u2500 Asset Discovery (subdomains, IPs, domains)", "\u2514\u2500\u2500 Tech Fingerprinting (what's running)", "\u2514\u2500\u2500 Endpoint Discovery (attack surface)", "\u2514\u2500\u2500 Vulnerability Testing (per vulnerability type)"],
    '2-subdomain-enumeration-critical-first-step': [],
    'passive-no-dns-queries-to-target': ["```bash"],
    'subfinder-aggregates-multiple-sources': ["subfinder -d target.com -o subdomains.txt"],
    'amass-passive': ["amass enum -passive -d target.com"],
    'certsh-certificate-transparency': ["curl -s \"https://crt.sh/?q=%.target.com&output=json\" | jq -r '.[].name_value' | sort -u"],
    'securitytrails-api-shodan': [],
    'web-https-securitytrails-com-list-apex-domain-target-com': [],
    'active-dns-brute-force-resolution': ["```bash"],
    'massdns-wordlist': ["massdns -r /path/to/resolvers.txt -t A -o S -w output.txt \\", "<(cat wordlist.txt | sed 's/$/.target.com/')"],
    'ffuf-for-subdomain-brute': ["ffuf -w subdomains-wordlist.txt -u https://FUZZ.target.com \\", "-mc 200,301,302,403 -H \"Host: FUZZ.target.com\""],
    'dnsx-for-bulk-resolution': ["cat subdomains.txt | dnsx -a -resp -o resolved.txt"],
    'recommended-wordlist-seclists-discovery-dns': [],
    'virtual-host-discovery': ["```bash"],
    'ffuf-vhost-mode': ["ffuf -w wordlist.txt -u https://target.com \\", "-H \"Host: FUZZ.target.com\" -mc 200,301,403"],
    'gobuster-vhost': ["gobuster vhost -u https://target.com -w wordlist.txt"],
    '3-service-and-port-discovery': ["```bash"],
    'fast-port-scan-common-ports': ["nmap -T4 -F target.com -oN ports.txt"],
    'comprehensive-scan-on-resolved-subdomains': ["cat resolved_ips.txt | nmap -iL - --open -p 80,443,8080,8443,8888,3000,5000 -oG scan.txt"],
    'httpx-for-http-probing': ["cat subdomains.txt | httpx -title -tech-detect -status-code -o live_hosts.txt"],
    'masscan-for-speed-on-large-ip-ranges': ["masscan -p 80,443,8080,8443 10.0.0.0/8 --rate=1000"],
    '4-web-technology-fingerprinting': ["```bash"],
    'wappalyzer-browser-extension-or': ["whatweb https://target.com"],
    'httpx-with-tech-detection': ["httpx -u https://target.com -tech-detect"],
    'check-headers-manually': ["curl -sI https://target.com | grep -i \"server\\|x-powered-by\\|x-generator\\|cf-ray\""],
    'fingerprint-from': ["- Server header: nginx/1.18, Apache/2.4, IIS/10.0", "- X-Powered-By: PHP/7.4, ASP.NET", "- Cookies: PHPSESSID (PHP), JSESSIONID (Java), _rails_session (Rails)", "- HTML comments: <!-- Drupal 9 -->", "- Meta generator: <meta name=\"generator\" content=\"WordPress 6.2\">", "- JS framework files: /static/js/angular.min.js"],
    '5-endpoint-discovery': [],
    'directory-brute-force': ["```bash"],
    'ffuf-fastest': ["ffuf -u https://target.com/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt \\", "-mc 200,301,302,403 -t 50 -o dirs.txt"],
    'gobuster': ["gobuster dir -u https://target.com -w wordlist.txt -x php,html,js,json"],
    'feroxbuster-recursive': ["feroxbuster -u https://target.com -w wordlist.txt -x php,html,txt -r"],
    'parameter-discovery': ["```bash"],
    'arjun-hidden-parameter-finder': ["arjun -u https://target.com/api/endpoint"],
    'x8': ["x8 -u https://target.com/api/endpoint -w params-wordlist.txt"],
    'javascript-source-mining': ["```bash"],
    'extract-endpoints-from-js-files': ["gau target.com | grep '\\.js$' | httpx -mc 200 | xargs -I{} curl -s {} | \\", "grep -oE '\"/[a-zA-Z0-9/_-]+\"' | sort -u"],
    'linkfinder': ["python3 linkfinder.py -i https://target.com -d -o output.html"],
    'getallurls-gau': ["gau target.com | sort -u > all_urls.txt"],
    'wayback-urls': ["waybackurls target.com | sort -u > wayback_urls.txt"],
    'api-endpoint-discovery': ["```bash"],
    'common-api-paths': ["ffuf -u https://target.com/FUZZ -w /SecLists/Discovery/Web-Content/api/api-endpoints.txt"],
    'swagger-openapi': ["test: /swagger.json /api-docs /openapi.json /v2/api-docs /.well-known/ /docs/"],
    'graphql': ["test: /graphql /gql /v1/graphql /api/graphql"],
    '6-source-code-recon': [],
    'github-gitlab-exposure': ["```bash"],
    'trufflehog-secret-scanner-in-git-history': ["trufflehog git https://github.com/target-org/target-repo"],
    'gitleaks': ["gitleaks detect --source /path/to/cloned/repo"],
    'manual-github-search': [],
    'site-github-com-target-com-api-key-or-secret-or-password': [],
    'site-github-com-target-com-env-or-config-php-or-db-password': [],
    'github-dorks': [],
    'target-com-extension-env': [],
    'target-com-filename-config-password': [],
    'org-target-org-secret-or-password-or-apikey': [],
    'exposed-environment-files': [],
    'check-common-paths': ["https://target.com/.env", "https://target.com/.git/config", "https://target.com/config.json", "https://target.com/config.yaml", "https://target.com/credentials.json", "https://target.com/secrets.json", "https://target.com/wp-config.php", "https://target.com/backup.sql", "https://target.com/backup.zip"],
    '7-zseano-s-testing-methodology': [],
    'core-philosophy': ["1. **Go deep on one program** rather than spread across many \u2014 learn the application thoroughly", "2. **Build a profile of the company** \u2014 tech stack, developers, processes", "3. **Look where others don't** \u2014 check error pages, admin paths, old versions, mobile API", "4. **Follow the filter** \u2014 if input is filtered somewhere, that functionality exists and may be bypassed"],
    'testing-sequence-one-page-feature': ["For each input point:", "1. Non-malicious HTML tags (<h2>, <img>) \u2192 are they reflected?", "2. Incomplete tags \u2192 what happens? (<iframe src=//evil.com )", "3. Encoding tests \u2192 %0d, %0a, %09, <%00", "4. Observe the OUTPUT too (not just response) \u2014 where does your input appear?", "5. Test same input in ALL similarly-structured pages (shared code \u2192 shared vuln)", "6. Check if the same parameter exists in mobile/API endpoint (less protected)"],
    'parameter-insights': ["- Each parameter tells a story: \"what does this do server-side?\"", "- Filename \u2192 OS interaction \u2192 Path Traversal / CMDi", "- URL/location \u2192 HTTP fetch \u2192 SSRF", "- Template/HTML parameter \u2192 render function \u2192 SSTI", "- XML field \u2192 parser \u2192 XXE", "- SQL filter \u2192 query \u2192 SQLi", "- User-content \u2192 storage \u2192 Stored XSS"],
    '8-bug-bounty-program-triage-where-to-spend-time': [],
    'high-value-target-selection': ["\u2713 Programs with large scope (*.target.com)", "\u2713 Programs that pay for P2/P3 (not just RCE)", "\u2713 Programs with recent tech changes (migrations = new bugs)", "\u2713 Programs with active development (new features = new attack surface)", "\u00d7 Avoid: frozen/old codebases with well-known CVEs (already claimed)", "\u00d7 Avoid: strict programs with narrow scope (less surface)"],
    'high-value-feature-focus-by-bug-probability': ["Priority 1: Authentication, password reset, 2FA \u2192 account takeover", "Priority 2: File upload, profile edit, API endpoints \u2192 stored XSS, IDOR", "Priority 3: Admin panels, user management \u2192 BFLA, privilege escalation", "Priority 4: Payment flows, subscription \u2192 business logic", "Priority 5: Import/export, template rendering \u2192 XXE, SSTI"],
    '9-nuclei-templates-automated-scanning': ["```bash"],
    'run-all-on-target': ["nuclei -u https://target.com -t /nuclei-templates/ -o nuclei-results.txt"],
    'specific-categories': ["nuclei -u https://target.com -t cves/ -severity critical,high", "nuclei -u https://target.com -t exposures/", "nuclei -u https://target.com -t misconfiguration/"],
    'on-subdomain-list': ["cat subdomains.txt | nuclei -t exposures/ -t misconfiguration/ -o exposed.txt"],
    '10-common-misconfigurations-quick-wins': ["\u25a1 CORS: Access-Control-Allow-Origin: * with credentials \u2192 CSRF + data theft", "\u25a1 S3 bucket public: curl https://target.s3.amazonaws.com/", "\u25a1 Directory listing: response contains \"Index of /\"", "\u25a1 .git exposed: curl https://target.com/.git/config", "\u25a1 .env exposed: curl https://target.com/.env", "\u25a1 Debug mode: stack traces in production (source code exposure)", "\u25a1 Default credentials: admin:admin, admin:password on admin panels", "\u25a1 phpinfo.php: curl https://target.com/phpinfo.php", "\u25a1 Backup files: config.bak, database.sql.gz, app.zip", "\u25a1 GraphQL introspection enabled: POST /graphql {\"query\":\"{__schema{types{name}}}\"}", "\u25a1 Admin panels: /admin /manager /console /phpmyadmin /wp-admin"],
    '11-quick-reference-tools': [],
    '12-java-middleware-fingerprint-matrix': [],
    'spring-boot-actuator-exploitation-priority': ["/actuator/env          \u2192 Leak environment variables (DB creds, API keys)", "/actuator/heapdump     \u2192 Download JVM heap \u2192 search for passwords in memory", "/actuator/jolokia      \u2192 JMX \u2192 possible RCE via MBean manipulation", "/actuator/gateway/routes \u2192 Spring Cloud Gateway \u2192 SpEL injection (CVE-2022-22947)", "/actuator/configprops  \u2192 All configuration properties", "/actuator/mappings     \u2192 All URL mappings (hidden endpoints)", "/actuator/beans        \u2192 All Spring beans", "/actuator/threaddump   \u2192 Thread dump (may leak session tokens / secrets in stack frames)"],
    '13-information-leak-detection-checklist': [],
    'version-control-backup-leaks': ["/.git/HEAD                    \u2192 Git repository exposed", "/.svn/entries                 \u2192 SVN metadata", "/.svn/wc.db                   \u2192 SVN SQLite database", "/.hg/requires                 \u2192 Mercurial", "/.bzr/README                  \u2192 Bazaar", "/.DS_Store                    \u2192 macOS directory listing"],
    'backup-file-patterns': ["/backup.zip    /backup.tar.gz    /backup.sql", "/wwwroot.rar   /www.zip          /web.zip", "/db.sql        /database.sql     /dump.sql", "/config.php.bak    /config.php~    /config.php.swp", "/.config.php.swp   /wp-config.php.bak", "/.env          /.env.bak         /.env.production"],
    'api-documentation-debug': ["/swagger-ui.html              \u2192 Swagger/OpenAPI", "/swagger-ui/                  \u2192 Swagger UI", "/api-docs                     \u2192 API documentation", "/graphql                      \u2192 GraphQL playground", "/graphiql                     \u2192 GraphQL IDE", "/debug/                       \u2192 Debug endpoints", "/phpinfo.php                  \u2192 PHP configuration", "/server-status                \u2192 Apache status", "/server-info                  \u2192 Apache info", "/nginx_status                 \u2192 Nginx status"],
    'cloud-infrastructure': ["/.aws/credentials             \u2192 AWS credentials", "/.docker/config.json          \u2192 Docker registry auth", "/robots.txt                   \u2192 Disallowed paths (hint list)", "/sitemap.xml                  \u2192 Full URL listing", "/crossdomain.xml              \u2192 Flash cross-domain policy", "/.well-known/                 \u2192 Various well-known URIs"],
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