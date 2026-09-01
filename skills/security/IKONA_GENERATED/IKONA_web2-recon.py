#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/web2-recon

Skill: WEB2 RECON PIPELINE
Desc : Web2 recon pipeline — subdomain enumeration (subfinder, Chaos API, assetfinder), live host discovery (dnsx, httpx), URL crawling (katana, waybackurls, gau), directory fuzzing (ffuf), JS analysis (LinkFinder, SecretFinder), continuous monitoring (new subdomain alerts, JS change detection, GitHub commit watch). Use when starting recon on any web2 target or when asked about asset discovery, subdomain enum, or attack surface mapping.

Run:  python claude-bughunter-web2-recon.py --help
      python claude-bughunter-web2-recon.py --list
      python claude-bughunter-web2-recon.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/web2-recon'
TITLE = 'WEB2 RECON PIPELINE'
DESCRIPTION = 'Web2 recon pipeline — subdomain enumeration (subfinder, Chaos API, assetfinder), live host discovery (dnsx, httpx), URL crawling (katana, waybackurls, gau), directory fuzzing (ffuf), JS analysis (LinkFinder, SecretFinder), continuous monitoring (new subdomain alerts, JS change detection, GitHub commit watch). Use when starting recon on any web2 target or when asked about asset discovery, subdomain enum, or attack surface mapping.'

PAYLOADS = {
    'main': ["name: web2-recon", "description: Web2 recon pipeline \u2014 subdomain enumeration (subfinder, Chaos API, assetfinder), live host discovery (dnsx, httpx), URL crawling (katana, waybackurls, gau), directory fuzzing (ffuf), JS analysis (LinkFinder, SecretFinder), continuous monitoring (new subdomain alerts, JS change detection, GitHub commit watch). Use when starting recon on any web2 target or when asked about asset discovery, subdomain enum, or attack surface mapping."],
    'web2-recon-pipeline': ["Full asset discovery from nothing to a prioritized URL list ready for hunting."],
    'setup-one-time': ["```bash"],
    '1-set-your-chaos-api-key-get-free-key-at-chaos-projectdiscovery-io': ["export CHAOS_API_KEY=\"your-key-here\""],
    'add-to-zshrc-or-bashrc-for-persistence': ["echo 'export CHAOS_API_KEY=\"your-key-here\"' >> ~/.zshrc"],
    '2-update-nuclei-templates-run-weekly': ["nuclei -update-templates"],
    '3-configure-subfinder-with-api-keys-for-more-sources': ["mkdir -p ~/.config/subfinder", "cat > ~/.config/subfinder/config.yaml << 'EOF'"],
    'get-free-keys-at-virustotal-com-securitytrails-com-censys-io-shodan-io': ["virustotal: [YOUR_VT_KEY]", "securitytrails: [YOUR_ST_KEY]", "censys_apiid: YOUR_CENSYS_ID", "censys_secret: YOUR_CENSYS_SECRET", "shodan: [YOUR_SHODAN_KEY]"],
    '4-verify-all-tools-installed': ["which subfinder httpx dnsx nuclei katana waybackurls gau dalfox ffuf anew gf interactsh-client"],
    'the-5-minute-rule': ["**5-minute kill signals:**", "- All subdomains return 403 or static marketing pages", "- No API endpoints visible in URLs", "- No JavaScript bundles with interesting endpoint paths", "- nuclei returns 0 medium/high findings", "- No forms, no authentication, no user data"],
    'standard-recon-pipeline': [],
    'pre-hunt-always-run-first': ["```bash", "TARGET=\"target.com\""],
    'step-0-passive-crt-sh-certificate-transparency-no-api-key-needed': ["curl -s \"https://crt.sh/?q=%.${TARGET}&output=json\" \\", "echo \"[+] crt.sh: $(wc -l < /tmp/subs.txt) subdomains\""],
    'step-1-chaos-api-projectdiscovery-most-comprehensive-source': ["curl -s \"https://dns.projectdiscovery.io/dns/$TARGET/subdomains\" \\", "-H \"Authorization: $CHAOS_API_KEY\" \\", "echo \"[+] Chaos returned $(wc -l < /tmp/subs.txt) subdomains\""],
    'step-2-subfinder-passive-multi-source': ["subfinder -d $TARGET -silent | anew /tmp/subs.txt", "assetfinder --subs-only $TARGET | anew /tmp/subs.txt", "echo \"[+] Total subdomains after all sources: $(wc -l < /tmp/subs.txt)\""],
    'step-3-dns-resolution-live-host-check': ["cat /tmp/subs.txt | dnsx -silent | httpx -silent -status-code -title -tech-detect | tee /tmp/live.txt", "echo \"[+] Live hosts: $(wc -l < /tmp/live.txt)\""],
    'step-4-url-crawl': ["cat /tmp/live.txt | awk '{print $1}' | katana -d 3 -jc -kf all -silent | anew /tmp/urls.txt"],
    'step-5-historical-urls': ["echo $TARGET | waybackurls | anew /tmp/urls.txt", "gau $TARGET --subs | anew /tmp/urls.txt", "echo \"[+] Total URLs: $(wc -l < /tmp/urls.txt)\""],
    'step-6-nuclei-scan': ["nuclei -l /tmp/live.txt -t ~/nuclei-templates/ -severity critical,high,medium -o /tmp/nuclei.txt"],
    'output-to-organized-directory': ["```bash", "TARGET=\"target.com\"", "RECON_DIR=\"recon/$TARGET\"", "mkdir -p $RECON_DIR"],
    'all-outputs-go-here': ["/tmp/subs.txt         \u2192 $RECON_DIR/subdomains.txt", "/tmp/live.txt         \u2192 $RECON_DIR/live-hosts.txt", "/tmp/urls.txt         \u2192 $RECON_DIR/urls.txt", "/tmp/nuclei.txt       \u2192 $RECON_DIR/nuclei.txt"],
    'attack-surface-triage': [],
    'find-interesting-targets-in-url-list': ["```bash"],
    'parameters-worth-testing': ["cat /tmp/urls.txt | grep -E \"[?&](id|user|file|path|url|redirect|next|src|token|key|api_key)=\" | tee /tmp/interesting-params.txt"],
    'api-endpoints': ["cat /tmp/urls.txt | grep -E \"/api/|/v1/|/v2/|/v3/|/graphql|/rest/|/gql\" | tee /tmp/api-endpoints.txt"],
    'file-upload-endpoints': ["cat /tmp/urls.txt | grep -E \"upload|file|attachment|document|image|avatar|photo|media\" | tee /tmp/uploads.txt"],
    'admin-internal-paths': ["cat /tmp/urls.txt | grep -E \"/admin|/internal|/debug|/test|/staging|/dev|/management|/console\" | tee /tmp/admin-paths.txt"],
    'authentication-endpoints': ["cat /tmp/urls.txt | grep -E \"/oauth|/login|/auth|/sso|/saml|/oidc|/callback|/token\" | tee /tmp/auth-paths.txt"],
    'gf-patterns-quick-classification': ["```bash"],
    'install-gf-patterns-https-github-com-tomnomnom-gf': ["cat /tmp/urls.txt | gf xss | tee /tmp/xss-candidates.txt", "cat /tmp/urls.txt | gf ssrf | tee /tmp/ssrf-candidates.txt", "cat /tmp/urls.txt | gf idor | tee /tmp/idor-candidates.txt", "cat /tmp/urls.txt | gf sqli | tee /tmp/sqli-candidates.txt", "cat /tmp/urls.txt | gf redirect | tee /tmp/redirect-candidates.txt", "cat /tmp/urls.txt | gf lfi | tee /tmp/lfi-candidates.txt", "cat /tmp/urls.txt | gf rce | tee /tmp/rce-candidates.txt"],
    'js-analysis': [],
    'secretfinder-api-keys-tokens-in-js-bundles': ["```bash"],
    'activate-venv': ["source ~/tools/SecretFinder/.venv/bin/activate"],
    'scan-a-single-js-file': ["python3 ~/tools/SecretFinder/SecretFinder.py -i \"https://target.com/static/js/main.js\" -o cli"],
    'scan-all-js-urls-found-in-recon': ["cat /tmp/urls.txt | grep \"\\.js$\" | head -50 | while read url; do", "echo \"=== $url ===\"", "python3 ~/tools/SecretFinder/SecretFinder.py -i \"$url\" -o cli 2>/dev/null", "deactivate"],
    'linkfinder-endpoints-hidden-in-js': ["```bash", "source ~/tools/LinkFinder/.venv/bin/activate"],
    'single-js-file': ["python3 ~/tools/LinkFinder/linkfinder.py -i \"https://target.com/app.js\" -o cli"],
    'all-pages-crawls-js-from-html': ["python3 ~/tools/LinkFinder/linkfinder.py -i \"https://target.com\" -d -o cli", "deactivate"],
    'directory-fuzzing': [],
    'ffuf-standard-fuzzing': ["```bash"],
    'directory-discovery-on-a-live-host': ["ffuf -u \"https://target.com/FUZZ\" \\", "-w ~/wordlists/common.txt \\", "-mc 200,201,204,301,302,307,401,403 \\", "-ac \\", "-t 40 \\", "-o /tmp/ffuf-dirs.json"],
    'api-endpoint-discovery': ["ffuf -u \"https://target.com/api/FUZZ\" \\", "-w ~/wordlists/api-endpoints.txt \\", "-mc 200,201,204,301,302 \\", "-ac \\", "-t 20"],
    'idor-fuzzing-with-authenticated-request': [],
    'create-req-txt-with-authorization-bearer-token': ["ffuf -request /tmp/req.txt \\", "-request-proto https \\", "-w <(seq 1 10000) \\", "-fc 404 \\", "-ac \\", "-t 10"],
    'target-scoring-go-no-go': ["Score before spending time. Skip if score < 4.", "**< 4:** Skip", "**4-5:** Only if nothing better available", "**6-8:** Good \u2014 spend 1-3 days", "**>= 9:** Excellent \u2014 spend up to 1 week"],
    'pre-dive-hard-kill-signals': ["1. Max bounty < $500 \u2192 not worth your time", "2. All recent reports are N/A or duplicate \u2192 hunters saturated it", "3. Scope is only a static marketing page \u2192 no attack surface", "4. Company < 5 employees with no revenue \u2192 won't pay", "5. Explicitly excludes your planned bug class in rules"],
    'tech-stack-detection-2-min': ["```bash"],
    'response-headers-reveal-backend': ["curl -sI https://target.com | grep -iE \"server|x-powered-by|x-aspnet|x-runtime|x-generator\""],
    'common-signals': [],
    'server-nginx-x-powered-by-php-7-4-php-backend': [],
    'server-gunicorn-or-x-powered-by-express-python-node-js': [],
    'x-powered-by-asp-net-net': [],
    'server-apache-tomcat-java': [],
    'x-runtime-ruby-ruby-on-rails': [],
    'framework-from-js-bundle-paths': [],
    'next-static-next-js': [],
    'static-js-main-chunk-js-cra-react': [],
    'packs-ruby-on-rails-webpacker': [],
    'nuxt-nuxt-js-vue': [],
    'stack-primary-bug-class-map': [],
    'continuous-monitoring-setup': ["Set up once per target. Alerts you before other hunters."],
    'new-subdomain-alerts-daily-cron': ["```bash", "TARGET=\"target.com\"", "KNOWN=\"/tmp/$TARGET-subs-known.txt\"", "subfinder -d $TARGET -silent > /tmp/$TARGET-subs-fresh.txt", "curl -s \"https://dns.projectdiscovery.io/dns/$TARGET/subdomains\" \\", "-H \"Authorization: $CHAOS_API_KEY\" \\"],
    'diff-against-known': ["NEW=$(comm -23 <(sort /tmp/$TARGET-subs-fresh.txt) <(sort $KNOWN 2>/dev/null))", "if [ -n \"$NEW\" ]; then", "echo \"NEW SUBDOMAINS: $NEW\"", "echo \"$NEW\" >> $KNOWN"],
    'schedule-crontab-e-0-8-bin-bash-monitors-subs-watch-sh': [],
    'github-commit-watch': ["```bash", "REPO=\"TargetOrg/target-app\"", "LAST_SHA=\"/tmp/$REPO-last-sha.txt\"", "CURRENT=$(curl -s \"https://api.github.com/repos/$REPO/commits?per_page=1\" | jq -r '.[0].sha')", "KNOWN=$(cat $LAST_SHA 2>/dev/null)", "if [ \"$CURRENT\" != \"$KNOWN\" ]; then", "echo \"New commit on $REPO: $CURRENT\"", "echo $CURRENT > $LAST_SHA", "curl -s \"https://api.github.com/repos/$REPO/commits/$CURRENT\" \\"],
    'schedule-30-bin-bash-monitors-github-watch-sh': [],
    'port-scanning-often-skipped-don-t-skip': ["```bash"],
    'naabu-fast-port-scanner-from-projectdiscovery': [],
    'finds-non-standard-ports-8080-8443-3000-8888-9000-etc': ["cat /tmp/live.txt | awk '{print $1}' | naabu -port 80,443,8080,8443,3000,4000,5000,8000,8888,9000,9090,9200,6379 -silent | tee /tmp/open-ports.txt"],
    'why-this-matters-admin-panels-debug-services-internal-apis-often-run-on-alt-ports': [],
    'example-wins-8080-actuator-env-spring-boot-9200-cat-indices-elasticsearch-6379-redis': [],
    'secret-scanning-in-js-bundles': ["```bash"],
    'trufflehog-high-signal-secret-detection-with-entropy-analysis': [],
    'scans-js-files-and-git-repos': ["pip install trufflehog3 2>/dev/null || true", "trufflehog filesystem --only-verified recon/$TARGET/ 2>/dev/null"],
    'secretfinder-manual-js-bundle-scan-already-in-tools': ["source ~/tools/SecretFinder/.venv/bin/activate", "cat /tmp/urls.txt | grep \"\\.js$\" | head -100 | while read url; do", "python3 ~/tools/SecretFinder/SecretFinder.py -i \"$url\" -o cli 2>/dev/null", "deactivate"],
    'quick-grep-for-common-patterns-in-downloaded-js': ["wget -q -r -l 1 -A \"*.js\" -P /tmp/js-files/ \"https://$TARGET\" 2>/dev/null", "grep -rn \"api_key\\|apiKey\\|client_secret\\|access_token\\|private_key\\|AWS_SECRET\\|AKIA\" /tmp/js-files/ 2>/dev/null"],
    'github-dorking-for-target': ["```bash"],
    'search-github-for-hardcoded-secrets-before-hunting-the-app': ["TARGET_ORG=\"TargetOrgName\"  # Check their GitHub org"],
    'useful-dorks-search-on-github-com': [],
    'org-target-org-password': [],
    'org-target-org-api-key': [],
    'org-target-org-authorization-bearer': [],
    'org-target-org-env': [],
    'org-target-org-begin-rsa-private-key': [],
    'cli-with-gh-github-cli': ["gh search code \"api_key\" --owner \"$TARGET_ORG\" --json path,repository 2>/dev/null | jq '.'", "gh search code \"password\" --owner \"$TARGET_ORG\" --json path,repository 2>/dev/null | head -20"],
    'gitdorker-if-installed': ["python3 ~/tools/GitDorker/GitDorker.py -t GITHUB_TOKEN -d ~/tools/GitDorker/Dorks/alldorksv3 -q \"$TARGET\" -org"],
    '30-minute-recon-protocol': [],
    'minutes-0-5-read-program-page': ["Note:", "- ALL in-scope assets (every domain listed)", "- Out-of-scope list (read carefully \u2014 common trap)", "- Safe harbor statement", "- Impact types accepted (some exclude \"low\")", "- Average bounty amount (signals program generosity)"],
    'minutes-5-15-asset-discovery': ["Run the standard pipeline above. Focus on live.txt output."],
    'minutes-15-25-surface-map': ["Run gf patterns and the interesting-params grep above."],
    'minutes-25-30-manual-exploration': ["Open Burp Suite. Browse the app with proxy on:", "1. Register an account", "2. Perform main user actions (create/read/update/delete resources)", "3. Note all API calls in Burp history", "4. Look for endpoints not in your URL list"],
    'after-30-min-prioritize': ["Priority 1: API endpoints with ID parameters \u2192 IDOR candidates", "Priority 2: File upload features \u2192 XSS/RCE candidates", "Priority 3: OAuth/SSO flows \u2192 auth bypass candidates", "Priority 4: Search/filter with user input \u2192 SQLi/SSRF/SSTI candidates", "Priority 5: Admin/debug endpoints \u2192 auth bypass candidates"],
    'toolchain-fallback-when-dnsx-httpx-crash': ["The projectdiscovery Go binaries (`dnsx`, `httpx`, `naabu`) occasionally `SIGSEGV` on macOS arm64 due to a cgo / system-resolver interaction. The crash signature is identical regardless of install method \u2014 both `brew install` and `go install github.com/projectdiscovery/<tool>@latest` produce binaries that segfault at the same address. Smoke-test once before relying on them in a real engagement:", "```bash", "dnsx -version   # if SIGSEGV: use the dig fallback below", "httpx -version  # if SIGSEGV: use the curl fallback below"],
    'dnsx-dig-fallback': ["```bash"],
    'replaces-dnsx-l-subs-txt-a-resp-silent': ["while read s; do", "ips=$(dig +short +tries=1 +time=3 \"$s\" \\", "[ -n \"$ips\" ] && echo \"$s|$ips\"", "done < subs.txt"],
    'httpx-curl-fallback': ["```bash"],
    'replaces-httpx-l-subs-txt-silent-status-code-title-tech-detect': ["while read s; do", "resp=$(curl -s -L -m 5 -o /tmp/body \\", "-w \"%{http_code}|%{url_effective}|%{header_server}\" \\", "\"https://$s\")", "code=$(echo \"$resp\" | cut -d'|' -f1)", "if [ \"$code\" != \"000\" ]; then", "title=$(grep -oE '<title[^>]*>[^<]*</title>' /tmp/body | head -1 | sed 's/<[^>]*>//g')", "echo \"$s|$resp|$title\"", "done < subs.txt", "**Trade-off:** Serial vs. concurrent. The fallback handles ~24 subdomains in 14 seconds; the same workload on `httpx` with default 50 threads finishes in 2-3 seconds. For VDP-scale recon (< 100 subdomains) the fallback is fine. For mass recon (1000+) fix the toolchain first.", "Verified against HackerOne's own VDP in `docs/verification/recon-hackerone-vdp.md`."],
    'api-spec-swagger-openapi-discovery-2024-2026-surface': ["API spec endpoints are the single highest-leverage recon target on any modern .NET / Node / Python / Java backend. The spec discloses every endpoint, HTTP methods, parameter names + types + formats, models, validation rules \u2014 a complete attack-map in JSON. Default routes are commonly left enabled in production. **Add this wordlist to the directory-fuzzing phase** (after the standard `common.txt` pass)."],
    'default-discovery-path-wordlist-paste-into-swagger-paths-txt': [],
    'nswag-swashbuckle-asp-net-core': ["/swagger", "/swagger/", "/swagger/index.html", "/swagger/ui/index.html", "/swagger/v1/swagger.json", "/swagger/v2/swagger.json", "/swagger/v3/swagger.json", "/swagger/docs/v1", "/swagger/docs/v2", "/swagger-ui", "/swagger-ui/", "/swagger-ui.html", "/swagger-resources", "/swagger-resources/configuration/ui", "/nswag", "/nswag/index.html", "/api/swagger", "/api/swagger.json", "/api/swagger/v1/swagger.json", "/api/openapi", "/api/openapi.json", "/api/v1/swagger.json", "/api/v2/swagger.json", "/api-docs", "/api-docs/swagger.json"],
    'openapi-generic': ["/openapi", "/openapi.json", "/openapi.yaml", "/openapi.yml", "/openapi/v1.json", "/openapi/v2.json", "/openapi/v3.json", "/.well-known/openapi.json"],
    'java-spring-springfox-springdoc': ["/v2/api-docs", "/v3/api-docs", "/v3/api-docs.yaml", "/v3/api-docs/swagger-config", "/swagger-ui/index.html"],
    'python-fastapi-flask-restplus-connexion-drf': ["/docs", "/docs/", "/redoc", "/redoc/", "/openapi.json", "/swagger.json", "/swagger/?format=openapi", "/swagger.yaml"],
    'express-node-hapi': ["/api-docs", "/api-docs.json", "/swagger.json", "/swagger-stats", "/graphql-docs"],
    'graphql-adjacent-often-co-located': ["/graphql", "/graphiql", "/playground", "/altair", "/voyager", "/graphql/console", "/graphql-explorer"],
    'redoc-rapidoc-stoplight-alt-uis': ["/redoc", "/redoc.html", "/redoc-ui.html", "/rapidoc", "/rapidoc.html", "/stoplight", "/elements"],
    'misc-dev-leftover': ["/actuator", "/actuator/openapi", "/actuator/mappings", "/q/openapi", "/q/swagger-ui", "/docs/swagger.json", "/api/v1/docs", "/api/v2/docs", "/internal/swagger", "/admin/swagger", "/management/swagger"],
    'integration-with-the-standard-pipeline': ["```bash"],
    'after-live-hosts-txt-is-built-phase-1-2-run': ["ffuf -w swagger-paths.txt -u \"https://FUZZ.target.com\" -mc 200,302 -fs 0 -t 50 -o swagger-hits.json"],
    'or-with-httpx-for-content-aware-filtering': ["httpx -l live-hosts.txt -path swagger-paths.txt -mc 200 -mr \"swagger|openapi\" -json | tee swagger-hits.jsonl"],
    'for-every-hit': ["jq '.paths | keys' swagger.json > endpoints.txt", "jq '.components.schemas' swagger.json > schemas.json   # mass-assignment field candidates"],
    'why-this-matters-for-recon-to-hunting-handoff': ["- **Spec \u2192 mass IDOR/BOLA** \u2014 `jq '.paths | keys' swagger.json` becomes the input list for `Autorize`/`ffuf` per-user testing.", "- **Spec \u2192 mass-assignment payload construction** \u2014 `components.schemas.UserUpdateDto` enumerates `isAdmin`, `emailVerified`, `tenantId`, `role`.", "- **Spec \u2192 hidden endpoint discovery** \u2014 `/internal/*`, `/debug/*`, `/v0/*`, `/legacy/*` routes documented but never auth-gated.", "- **Spec \u2192 injection-class seeding** \u2014 every parameter's type + format + enum + max-length means payloads pass validation before reaching the sink. Especially valuable against ASP.NET Core where the model binder rejects malformed input before any controller logic."],
    'tools': ["- `kiterunner` \u2014 natively ingests OpenAPI spec, generates requests against the API.", "- `sj` (Swagger Jacker) \u2014 purpose-built for Swagger spec exploitation.", "- `apidetector` (brinhosa) \u2014 Swagger-UI mass scanner.", "- `XSSwagger` (vavkamil) \u2014 detects vulnerable Swagger UI versions (CVE-2018-25031 family).", "- `nuclei -t http/exposures/apis/` \u2014 built-in templates for default spec paths."],
    'anti-pattern-reminder': ["A 404/403 on `/swagger` does NOT mean no spec is exposed. Many .NET projects route the spec under `/api/swagger/v1/swagger.json` rather than `/swagger`. Always test the full path list, not just the root.", "Full attack-chain analysis is in `hunt-api-misconfig` \u2192 `NSwag / Swagger / OpenAPI Spec Exposure`."],
    'related-skills-chains': ["- **`offensive-osint`** \u2014 When recon needs concrete probes / wordlists / regexes beyond the basic pipeline. Workflow primitive: this skill produces the URL set; `offensive-osint` provides the secret regexes, GraphQL/Swagger paths, and identity-fabric probes you apply to that URL set.", "- **`osint-methodology`** \u2014 When you need a severity rubric for what you discovered. Workflow primitive: after recon outputs `subdomains.txt` / `live-hosts.txt` / `urls.txt`, score each asset against `osint-methodology`'s findings rubric to decide what gets a finding versus what stays in the asset graph.", "- **`hunt-subdomain`** \u2014 When recon surfaces stale CNAMEs / dangling DNS. Workflow primitive: any subdomain in `subdomains.txt` whose CNAME points to S3 / GitHub Pages / Heroku / Shopify / Azure should auto-route to `hunt-subdomain` for takeover validation.", "- **`security-arsenal`** \u2014 When the URL set is classified by `gf` and ready for active testing. Workflow primitive: `gf xss/ssrf/sqli/idor` output names become payload-class queries against `security-arsenal`'s payload library.", "- **`bb-methodology`** \u2014 When recon completes and Phase 1 transitions to Phase 2 (Mapping). Workflow primitive: hand the live host + URL set back to `bb-methodology` Phase 2 for endpoint mapping and Phase 3 vulnerability discovery routing."],
    'operator-notes-claude-bughunter': [],
    'cross-tld-pivot-discipline': ["Phase 2C's HackerOne VDP recon walked from `hackerone.com` (24 subdomains) into a sister TLD `hacker.one` (12 more subdomains found in JS bundle references). Operators who only enumerate `*.target.com` miss attack surface that the target legitimately operates on a different domain.", "Always grep JS bundles for plausible sibling TLDs:", "```bash"],
    'pull-all-js-grep-for-sibling-tld-candidates': ["for url in $(cat live-hosts.txt); do", "curl -s \"$url\" | grep -oE 'src=\"[^\"]+\\.js\"' | sed 's/src=\"//;s/\"//'", "done | sort -u > js-urls.txt"],
    'then-on-each-js-file': ["for j in $(cat js-urls.txt); do", "curl -s \"$j\" | grep -oE '[a-z0-9.-]+\\.(io|app|one|dev|test|cloud|ai|co)' | sort -u", "done | sort -u > sibling-tld-candidates.txt", "Common sibling-TLD patterns: `target.com \u2192 target.io / target.app / target.one / target.dev / target.test / target-corp.com / target-cdn.net`. Always validate via WHOIS or by checking if the cert chain trusts the same internal CA before treating the sister TLD as in-scope."],
    'subdomain-wordlist-priorities-by-2026': ["Top discovery prefixes by hit rate against enterprise VDPs in our 2024-2026 corpus:", "mta-sts.*          api.*              docs.*", "dev-*              staging-*          *-qa", "*-stage            *-uat              events.*", "portal.*           customer.*         partner.*", "vendor.*           internal-*         admin-*", "employee-*         hr.*               jobs.*", "sso.*              auth.*             id.*", "Internal-looking subdomains often expose more surface than the marketing site \u2014 `partner.target.com` and `vendor-portal.target.com` frequently have weaker auth than the main app because they're scoped for \"trusted\" external users. Always send a probe to the long-tail wordlist after the standard subfinder run completes."],
    'live-host-probe-how-to-fingerprint-stack-quickly': ["`curl -sI <host>` headers are 80% of the fingerprint:", "- `Server:` \u2014 apache / nginx / cloudflare / kestrel (= .NET Core) / openresty / envoy", "- `X-Powered-By:` \u2014 PHP version, ASP.NET version, Express.js", "- `X-Drupal-Cache`, `X-Generator: Drupal 9` \u2014 Drupal", "- `X-Generator: WordPress` \u2014 WordPress", "- `Via:` \u2014 CDN chain (1.1 varnish, 1.1 cloudfront)", "- `Set-Cookie:` names \u2014 `JSESSIONID` (Java), `PHPSESSID` (PHP), `ASP.NET_SessionId` (.NET), `connect.sid` (Express), `laravel_session` (Laravel)", "JS bundle filename patterns:", "- `/_next/static/` = Next.js", "- `/_nuxt/` = Nuxt", "- `/assets/static/` with hash filenames = Vite", "- `/static/js/main.*.chunk.js` = Create React App", "- `runtime.*.js + polyfills.*.js + main.*.js` = Angular CLI", "The first 10s of recon should yield a stack guess; the rest is targeting. If your fingerprint contradicts itself (Server says nginx, Set-Cookie says ASP.NET) you've found a reverse proxy front-end \u2014 note the origin app for later smuggling/cache attacks."],
    'github-pages-404-vs-takeover-signal': ["Critical distinction operators get wrong:", "- **\"Page not found \u00b7 GitHub Pages\"** with HTTP 404 means the repo EXISTS \u2014 NOT a takeover.", "- **\"There isn't a GitHub Pages site here\"** means the repo was deleted \u2014 TAKEOVER candidate.", "Same distinction for CloudFront:", "- **\"Error - 404\"** with `Server: CloudFront` = distribution exists, origin returned 404 \u2014 NOT a takeover.", "- **\"The request could not be satisfied\"** with `X-Cache: Error from cloudfront` = origin missing entirely \u2014 potential takeover.", "Phase 2C verified both patterns live. Always check the EXACT response body string before filing a takeover finding \u2014 the takeover-scanner tools (subzy, subjack) match on multiple fingerprints and frequently false-positive on the \"still owned, just empty\" case."],
    'toolchain-fallback': ["Already covered in this file's Phase 2C addition. Quick reminder: dnsx/httpx may segfault on macOS arm64; the dig+curl fallback works for < 100-host runs in ~14 seconds. Don't burn an hour debugging Go binary panics when the fallback gets you to the same URL set."],
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