#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/subdomain-takeover

Skill: SKILL: Subdomain Takeover — Detection & Exploitation Playbook
Desc : >-

Run:  python hack-skills-subdomain-takeover.py --help
      python hack-skills-subdomain-takeover.py --list
      python hack-skills-subdomain-takeover.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/subdomain-takeover'
TITLE = 'SKILL: Subdomain Takeover — Detection & Exploitation Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: subdomain-takeover", "description: >-", "Subdomain takeover detection and exploitation playbook. Use when targets have", "dangling CNAME/NS/MX records pointing to deprovisioned cloud resources, expired", "third-party services, or unclaimed SaaS tenants that an attacker can register", "to serve content under the victim's domain."],
    'skill-subdomain-takeover-detection-exploitation-playbook': [],
    '0-related-routing': ["- [ssrf-server-side-request-forgery](../ssrf-server-side-request-forgery/SKILL.md) when a subdomain takeover is used to bypass SSRF allowlists trusting `*.target.com`", "- [cors-cross-origin-misconfiguration](../cors-cross-origin-misconfiguration/SKILL.md) when CORS trusts `*.target.com` \u2014 takeover \u2192 full cross-origin read", "- [xss-cross-site-scripting](../xss-cross-site-scripting/SKILL.md) takeover gives you script execution under target origin (cookie theft, OAuth redirect abuse)", "- [http-host-header-attacks](../http-host-header-attacks/SKILL.md) when Host routing leads to subdomain-scoped cache or auth issues", "- [web-cache-deception](../web-cache-deception/SKILL.md) when a taken-over subdomain shares cache with the main domain"],
    '1-core-concept': ["Subdomain takeover occurs when:", "1. `sub.target.com` has a DNS record (CNAME, NS, A) pointing to an external service", "2. The external resource is **no longer provisioned** (deleted S3 bucket, removed Heroku app, etc.)", "3. The attacker can **register/claim** that exact resource name on the provider", "4. The attacker now controls content served under `sub.target.com`", "**Impact**: cookie theft (parent domain cookies), OAuth token interception, phishing under trusted domain, CORS bypass, CSP bypass via whitelisted subdomain."],
    '2-detection-methodology': [],
    '2-1-cname-enumeration': ["1. Collect subdomains (amass, subfinder, assetfinder, crt.sh, SecurityTrails)", "2. Resolve DNS for each:", "dig CNAME sub.target.com +short", "3. For each CNAME \u2192 check if the CNAME target returns NXDOMAIN or a provider error", "4. Match error response against fingerprint table (Section 3)"],
    '2-2-key-signals': [],
    '2-3-automated-tools': [],
    '3-service-provider-fingerprint-table': [],
    '4-takeover-procedure-common-providers': [],
    '4-1-aws-s3': ["1. Confirm: curl -s http://sub.target.com \u2192 \"NoSuchBucket\"", "2. Extract bucket name from CNAME (e.g., sub.target.com.s3.amazonaws.com \u2192 bucket = \"sub.target.com\")", "3. aws s3 mb s3://sub.target.com --region <region>", "4. Upload index.html proving control", "5. Enable static website hosting"],
    '4-2-github-pages': ["1. Confirm: curl -s https://sub.target.com \u2192 \"There isn't a GitHub Pages site here\"", "2. Create GitHub repo (any name)", "3. Add CNAME file containing \"sub.target.com\"", "4. Enable GitHub Pages in repo settings", "5. Wait for DNS propagation (GitHub verifies CNAME match)"],
    '4-3-heroku': ["1. Confirm: curl -s http://sub.target.com \u2192 \"No such app\"", "2. heroku create <app-name-from-cname>", "3. heroku domains:add sub.target.com", "4. Deploy proof-of-concept page"],
    '5-ns-takeover-high-severity': ["NS takeover is **far more dangerous** than CNAME takeover: you control **all DNS resolution** for the zone."],
    'how-it-happens': ["target.com NS \u2192 ns1.expireddomain.com", "attacker registers expireddomain.com", "attacker now controls ALL DNS for target.com", "(A records, MX records, TXT records \u2014 everything)"],
    'detection': ["1. Enumerate NS records: dig NS target.com +short", "2. Check each NS domain: whois ns1.example.com \u2192 is the domain expired or available?", "3. Also check: dig A ns1.example.com \u2192 NXDOMAIN/SERVFAIL?", "4. Subdelegated zones: check NS for sub.target.com specifically"],
    'impact': ["- Full domain takeover (serve any content, intercept email, issue TLS certs via DNS-01)", "- Issue DV certificates from any CA using DNS challenge", "- Modify SPF/DKIM/DMARC \u2192 send authenticated email as target"],
    '6-mx-takeover-email-interception': ["When MX records point to deprovisioned mail services:", "target.com MX \u2192 mail.deadservice.com (service discontinued)", "If attacker can claim `mail.deadservice.com` or the mail tenant:", "- Receive password reset emails", "- Intercept sensitive communications", "- Potentially reset accounts that use email-based auth"],
    'common-scenario': ["Expired Google Workspace / Microsoft 365 tenant \u2192 MX still points to Google/Microsoft \u2192 attacker creates new tenant and claims the domain."],
    '7-wildcard-dns-risks': ["If `*.target.com` has a wildcard CNAME to a claimable service:", "- **Every** undefined subdomain is vulnerable", "- `anything.target.com` can be taken over", "- Massively increases attack surface", "Detection: `dig A random1234567.target.com` \u2014 if it resolves, wildcard exists."],
    '8-detection-exploitation-decision-tree': ["Subdomain discovered (sub.target.com)?", "\u251c\u2500\u2500 Resolve DNS records", "\u2502   \u251c\u2500\u2500 Has CNAME \u2192 external service?", "\u2502   \u2502   \u251c\u2500\u2500 HTTP response matches known fingerprint? (Section 3)", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 YES \u2192 Attempt claim on provider (Section 4)", "\u2502   \u2502   \u2502   \u2502   \u251c\u2500\u2500 Claim successful \u2192 TAKEOVER CONFIRMED", "\u2502   \u2502   \u2502   \u2502   \u2514\u2500\u2500 Claim blocked (name reserved, region locked) \u2192 document, try variations", "\u2502   \u2502   \u2502   \u2514\u2500\u2500 NO \u2192 Service active, no takeover", "\u2502   \u2502   \u2514\u2500\u2500 CNAME target NXDOMAIN?", "\u2502   \u2502       \u251c\u2500\u2500 Target is a registrable domain? \u2192 Register it \u2192 full control", "\u2502   \u2502       \u2514\u2500\u2500 Target is a subdomain of active provider \u2192 check provider claim process", "\u2502   \u2502", "\u2502   \u251c\u2500\u2500 Has NS records \u2192 external nameserver?", "\u2502   \u2502   \u251c\u2500\u2500 NS domain expired/available? \u2192 Register \u2192 FULL ZONE TAKEOVER", "\u2502   \u2502   \u2514\u2500\u2500 NS domain active \u2192 no takeover", "\u2502   \u2502", "\u2502   \u251c\u2500\u2500 Has MX \u2192 external mail service?", "\u2502   \u2502   \u251c\u2500\u2500 Mail service deprovisioned/claimable? \u2192 Claim tenant \u2192 EMAIL INTERCEPTION", "\u2502   \u2502   \u2514\u2500\u2500 Active mail service \u2192 no takeover", "\u2502   \u2502", "\u2502   \u2514\u2500\u2500 Has A record \u2192 IP address?", "\u2502       \u251c\u2500\u2500 IP belongs to elastic cloud (AWS EIP, Azure, GCP)?", "\u2502       \u2502   \u251c\u2500\u2500 IP unassigned? \u2192 Claim IP \u2192 serve content", "\u2502       \u2502   \u2514\u2500\u2500 IP assigned to another customer \u2192 no takeover", "\u2502       \u2514\u2500\u2500 IP belongs to dedicated server \u2192 no takeover", "\u2514\u2500\u2500 Post-takeover impact assessment", "\u251c\u2500\u2500 Shared cookies with parent domain? \u2192 Session hijacking", "\u251c\u2500\u2500 CORS trusts *.target.com? \u2192 Cross-origin data theft", "\u251c\u2500\u2500 CSP whitelists *.target.com? \u2192 XSS via taken-over subdomain", "\u251c\u2500\u2500 OAuth redirect_uri allows sub.target.com? \u2192 Token theft", "\u2514\u2500\u2500 Can issue TLS cert for sub.target.com? \u2192 Full MITM"],
    '9-defense-remediation': [],
    '10-trick-notes-what-ai-models-miss': ["1. **CNAME \u2260 takeover**: A CNAME to S3 that returns 403 (bucket exists, private) is NOT vulnerable. Only `NoSuchBucket` (404) is.", "2. **Region matters for S3**: Bucket names are global, but website endpoints are regional. Try matching the region from the CNAME.", "3. **GitHub Pages verification**: GitHub added domain verification \u2014 org-verified domains cannot be claimed by others. Check if target uses this.", "4. **Edge cases**: Some providers (e.g., Cloudfront) require specific distribution configuration, not just domain claiming.", "5. **Second-order takeover**: `sub.target.com CNAME \u2192 other.target.com CNAME \u2192 dead-service.com` \u2014 the chain must be followed fully.", "6. **SPF subdomain takeover**: If SPF includes `include:sub.target.com` and you take over `sub.target.com`, you can modify its SPF TXT record to authorize your mail server \u2192 send spoofed email as `target.com`."],
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