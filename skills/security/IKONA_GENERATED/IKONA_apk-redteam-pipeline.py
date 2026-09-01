#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/apk-redteam-pipeline

Skill: Find developer page from the target's brand name
Desc : End-to-end Android APK red-team pipeline — automated APK acquisition (Play Store + apkpure + apkmirror fallback), jadx decompilation, secret/URL/JWT/Firebase grep, pinned-cert extraction, exported-component enumeration, Frida runtime instrumentation templates, intent-injection probes. Built from an authorized external red-team engagement where 7 APKs were pulled manually, 4 download attempts truncated, and a hardcoded JWT + 30 internal API endpoints were recovered from one of the apps. Use when target has a mobile app catalogue (Play Store developer page), when you find an APK URL hosted on a web server, or when post-recon mentions "mobile app" in scope.

Run:  python claude-bughunter-apk-redteam-pipeline.py --help
      python claude-bughunter-apk-redteam-pipeline.py --list
      python claude-bughunter-apk-redteam-pipeline.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/apk-redteam-pipeline'
TITLE = "Find developer page from the target's brand name"
DESCRIPTION = 'End-to-end Android APK red-team pipeline — automated APK acquisition (Play Store + apkpure + apkmirror fallback), jadx decompilation, secret/URL/JWT/Firebase grep, pinned-cert extraction, exported-component enumeration, Frida runtime instrumentation templates, intent-injection probes. Built from an authorized external red-team engagement where 7 APKs were pulled manually, 4 download attempts truncated, and a hardcoded JWT + 30 internal API endpoints were recovered from one of the apps. Use when target has a mobile app catalogue (Play Store developer page), when you find an APK URL hosted on a web server, or when post-recon mentions "mobile app" in scope.'

PAYLOADS = {
    'main': ["name: apk-redteam-pipeline", "description: End-to-end Android APK red-team pipeline \u2014 automated APK acquisition (Play Store + apkpure + apkmirror fallback), jadx decompilation, secret/URL/JWT/Firebase grep, pinned-cert extraction, exported-component enumeration, Frida runtime instrumentation templates, intent-injection probes. Built from an authorized external red-team engagement where 7 APKs were pulled manually, 4 download attempts truncated, and a hardcoded JWT + 30 internal API endpoints were recovered from one of the apps. Use when target has a mobile app catalogue (Play Store developer page), when you find an APK URL hosted on a web server, or when post-recon mentions \"mobile app\" in scope.", "sources: authorized-engagement", "report_count: 1"],
    'when-to-use-this-skill': ["Trigger when:", "- Recon surfaces 1+ mobile apps under the target's developer name (Play Store dev page)", "- A web app hosts `*.apk` files directly (e.g. `Recruitz.apk` found on a subdomain during one engagement)", "- APK package IDs leaked via stealer logs (e.g. `com.<brand>.app`, `com.<brand>.<sub-brand>` patterns in stealer dump format)", "- Customer-facing app, dealer/partner portal, or employee mobile companion app is in scope", "- Bug bounty program lists Android in scope", "DO NOT use for:", "- iOS-only targets (different pipeline \u2014 IPA reverse, MobSF, frida-ios-dump)", "- React Native / Flutter web apps already covered by JS bundle analysis", "- Server-side only assessments"],
    'stage-0-inventory-all-org-owned-apps': [],
    'play-store-developer-page-scrape': ["```bash"],
    'find-developer-page-from-the-target-s-brand-name': ["curl -sk -A \"Mozilla/5.0\" \"https://play.google.com/store/apps/developer?id=<Brand+Name>\" -o /tmp/dev.html"],
    'extract-package-ids': ["grep -oE 'id=[a-zA-Z0-9._]+' /tmp/dev.html | sort -u", "Example output (anonymized \u2014 7 packages typical for a multi-brand conglomerate):", "com.events.<brand>build", "com.<corp>.<sub-brand-1>", "com.<corp>.<sub-brand-2>", "com.<corp>.<flagship>", "com.<corp>.<product-line-1>", "com.<corp>.<product-line-2>", "com.<corp>.<sub-brand-3>"],
    'cross-reference-with-stealer-logs': ["Stealer-log format includes package names like `*@com.<corp>.<app>` \u2014 extract these from `creds_userpass.txt` if you have a leaked dump."],
    'brand-permutation-guesses-multi-brand-conglomerate-patterns': ["com.<brand>.app", "com.<brand>.mobile", "com.<brand>.android", "com.<brand>connect.app", "in.<brand>.dealer", "in.co.<brand>.app"],
    'stage-1-apk-acquisition': [],
    'primary-apkpure-direct-no-auth-required': ["```bash"],
    'follow-302-redirects-to-actual-download': ["curl -sk -L --max-time 60 \\", "\"https://d.apkpure.net/b/APK/<package_id>?version=latest\" \\", "-o \"<package_id>.apk\""],
    'or-via-the-legacy-d-xx-winudf-com-mirror-chain-we-saw-this-work': [],
    'secondary-apkmirror-search': ["```bash", "curl -sk -A \"Mozilla/5.0\" \"https://www.apkmirror.com/?post_type=app_release&searchtype=apk&s=<brand>\" \\"],
    'tertiary-apkpure-web-search': ["```bash", "curl -sk \"https://apkpure.com/search?q=<brand>\" | grep -oE 'data-dt-app=\"[^\"]+\"'"],
    'xapk-vs-apk': ["- `.xapk` = a zip containing multiple split APKs (base + config.armeabi-v7a + config.en + etc.)", "- Unzip outer first, then unzip the inner `base.apk` or `<package>.apk`", "- Some apkpure downloads return truncated XAPK with missing EOCD signature \u2014 symptom of CDN rate-limiting; rotate IP and retry, OR use `7z x` which is more lenient than `unzip`", "```bash"],
    'standard-unzip-works-for-clean-apk': ["unzip -o <package>.apk -d extracted_<package>/"],
    'for-truncated-repaired-xapk': ["7z x -y <package>.apk -o\"extracted_<package>\""],
    'for-nested-xapk': ["for inner in extracted_<package>/*.apk; do", "mkdir -p \"extracted_<package>/$(basename \"$inner\" .apk)\"", "unzip -o \"$inner\" -d \"extracted_<package>/$(basename \"$inner\" .apk)\""],
    'stage-2-dex-decompilation-jadx': ["```bash"],
    'install': ["brew install jadx          # macOS"],
    'or': ["wget https://github.com/skylot/jadx/releases/latest/download/jadx-1.5.x.zip"],
    'decompile': ["jadx -d decompiled_<package>/ <package>.apk"],
    'for-xapk-that-contains-multiple-apks': ["for inner in extracted_<package>/*.apk; do", "jadx -d decompiled_<package>_$(basename \"$inner\" .apk)/ \"$inner\"", "For a fast \"strings only\" pass without full decompilation:", "```bash", "find extracted_<package> -name \"classes*.dex\" -exec strings -8 {} \\; > strings_<package>.txt"],
    'stage-3-secret-grep-the-60-pattern-catalog': ["```bash"],
    'url-grep-owned-domain-references': ["grep -oE 'https?://[a-zA-Z0-9.-]+\\.(target1|target2|target3)\\.(com|io|net|in)[a-zA-Z0-9./_?=&%-]*' strings_<package>.txt | sort -u"],
    'internal-ip-port-urls': ["grep -oE 'https?://(10\\.|172\\.(1[6-9]|2[0-9]|3[01])\\.|192\\.168\\.|127\\.)[0-9.]+(:[0-9]+)?[a-zA-Z0-9./_?=&-]*' strings_<package>.txt"],
    'cloud-credentials': ["grep -oE 'AKIA[A-Z0-9]{16}'                            # AWS Access Key", "grep -oE 'aws_secret_access_key[\\s:=]+[A-Za-z0-9/+=]{40}' # AWS Secret", "grep -oE 'AIza[A-Za-z0-9_-]{35}'                       # Google API key", "grep -oE 'ya29\\.[A-Za-z0-9_-]+'                        # Google OAuth refresh token", "grep -oE 'gh[ps]_[A-Za-z0-9]{36}'                      # GitHub PAT", "grep -oE 'glpat-[A-Za-z0-9_-]{20}'                     # GitLab PAT", "grep -oE 'xox[pbar]-[A-Za-z0-9-]+'                     # Slack token", "grep -oE 'sk-[A-Za-z0-9]{48}'                          # OpenAI API key", "grep -oE 'sk-ant-[A-Za-z0-9_-]{90,}'                   # Anthropic API key", "grep -oE 'AC[a-f0-9]{32}'                              # Twilio Account SID", "grep -oE 'sk_live_[A-Za-z0-9]{24}'                     # Stripe live key", "grep -oE 'pk_live_[A-Za-z0-9]{24}'                     # Stripe publishable", "grep -oE 'mailgun-[A-Za-z0-9-]{40}'                    # Mailgun", "grep -oE 'SG\\.[A-Za-z0-9_-]{22}\\.[A-Za-z0-9_-]{43}'    # SendGrid"],
    'jwt-any-algorithm': ["grep -oE 'eyJ[A-Za-z0-9_-]+\\.eyJ[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]*' strings_<package>.txt"],
    'firebase': ["grep -oE '\"(api_key|project_id|database_url|storage_bucket|client_id|mobilesdk_app_id|google_app_id|gcm_defaultSenderId)\"\\s*:\\s*\"[^\"]+\"' \\", "extracted_<package>/res/values/strings.xml \\", "extracted_<package>/google-services.json \\", "decompiled_<package>/resources/AndroidManifest.xml 2>/dev/null"],
    'oauth-client-secrets': ["grep -oE 'client_secret[\"\\s:=]+[A-Za-z0-9_-]{24,}' strings_<package>.txt"],
    'hardcoded-passwords-heuristic-many-false-positives-manual-review': ["grep -oE '\"password\"\\s*:\\s*\"[^\"]+\"|password\\s*=\\s*\"[^\"]+\"' decompiled_<package>/sources/**/*.java 2>/dev/null"],
    'real-world-example-finding-anonymized-from-an-authorized-engagement': [],
    'customer-facing-apk-shipped-a-hardcoded-url-of-this-shape': ["https://api.<client>.example/<path-token>/<resource-token>?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.<payload>.<sig>"],
    'decoded-jwt-payload-sid-int-iat-unix-ts-exp-unix-ts': [],
    'expired-8-years-earlier-but-path-tokens-30-v1-endpoints-still-useful-intel': [],
    'stage-4-pinned-certificate-extraction': ["```bash"],
    'find-cer-der-pem-files-in-assets': ["find extracted_<package>/assets -iname \"*.cer\" -o -iname \"*.der\" -o -iname \"*.pem\" -o -iname \"*.crt\" 2>/dev/null"],
    'or-in-network-security-config-xml': ["find extracted_<package> -name \"network_security_config.xml\" -exec cat {} \\;"],
    'for-each-cert-extract-subject-san-might-reveal-new-internal-api-hosts': ["for cert in $(find extracted_<package>/assets -iname \"*.cer\"); do", "echo \"=== $cert ===\"", "openssl x509 -in \"$cert\" -noout -subject -issuer -dates 2>/dev/null", "openssl x509 -in \"$cert\" -noout -text 2>/dev/null | grep -E 'Subject:|DNS:|Issuer:|Validity'"],
    'real-world-example': ["A customer-facing APK from an authorized engagement contained `assets/api_<service>_<domain>_com.cer` \u2014 revealed the existence of an `api.<service>.<domain>.example` asset that had NOT surfaced in passive recon."],
    'stage-5-exported-component-enumeration': ["AndroidManifest.xml lists components. Exported ones (especially with `android:exported=\"true\"` or implicit-export via intent-filter) can be triggered by other apps \u2014 potential intent-injection attack surface.", "```bash"],
    'decode-binary-androidmanifest-if-needed': ["apktool d <package>.apk -o decoded_<package>/    # apktool decodes binary manifest"],
    'or-read-directly-from-jadx-output': ["cat decompiled_<package>/resources/AndroidManifest.xml | grep -E '<(activity|service|receiver|provider)' | head -50"],
    'filter-exported': ["grep -E 'android:exported=\"true\"' decompiled_<package>/resources/AndroidManifest.xml", "For each exported component, check:", "- Does it accept extras that flow into a WebView (intent \u2192 WebView \u2192 XSS / file://)", "- Does it accept URI extras (potential SSRF via deep link)", "- Does it pass extras to other Activities (intent redirection)"],
    'stage-6-firebase-cloud-service-config-inspection': ["```bash"],
    'google-services-json-full-firebase-config': ["find extracted_<package> -name \"google-services.json\" -exec cat {} \\; | python3 -m json.tool"],
    'look-for': [],
    'project-id-can-guess-firestore-rtdb-url-https-project-id-firebaseio-com-json': [],
    'storage-bucket-can-guess-gcs-bucket-gs-bucket': [],
    'web-api-key-can-use-to-enumerate-firebase-tenant-config': [],
    'test-if-firestore-is-publicly-readable': ["curl -s \"https://firestore.googleapis.com/v1/projects/<project_id>/databases/(default)/documents/users\""],
    'test-if-realtime-db-is-publicly-readable': ["curl -s \"https://<project_id>.firebaseio.com/.json\""],
    'test-if-storage-bucket-is-publicly-listable': ["curl -s \"https://firebasestorage.googleapis.com/v0/b/<bucket>/o\""],
    'stage-7-runtime-instrumentation-frida': ["For when static analysis isn't enough \u2014 you want to dump tokens at runtime, bypass cert pinning, or trace API calls."],
    'setup': ["```bash", "pip install --break-system-packages frida-tools objection", "adb devices  # ensure device/emulator connected"],
    'push-frida-server-to-device-root-required-or-use-rooted-emulator-like-genymotion-x86-64-avd': [],
    'cert-pinning-bypass-universal': ["```javascript", "// frida-script-pinning-bypass.js", "Java.perform(function() {", "// OkHttp", "try {", "var CertificatePinner = Java.use('okhttp3.CertificatePinner');", "CertificatePinner.check.overload('java.lang.String', 'java.util.List').implementation = function() {", "console.log('[+] OkHttp pinning bypassed for: ' + arguments[0]);", "return;", "} catch (e) {}", "// HttpsURLConnection", "try {", "var TrustManagerImpl = Java.use('com.android.org.conscrypt.TrustManagerImpl');", "TrustManagerImpl.verifyChain.implementation = function(chain) {", "console.log('[+] TrustManagerImpl verifyChain bypassed');", "return chain;", "} catch (e) {}", "```bash", "frida -U -l frida-script-pinning-bypass.js -f <package_id> --no-pause"],
    'hook-http-requests': ["```javascript", "Java.perform(function() {", "var OkHttpClient = Java.use('okhttp3.OkHttpClient');", "var Request = Java.use('okhttp3.Request');", "var Call = Java.use('okhttp3.Call');", "OkHttpClient.newCall.implementation = function(req) {", "var url = req.url().toString();", "var headers = req.headers().toString();", "console.log('[REQ] ' + url);", "console.log('[HDRS] ' + headers);", "return this.newCall(req);"],
    'quick-token-extraction-via-objection': ["```bash", "objection --gadget com.target.app explore"],
    'inside': ["android hooking watch class_method <class>.<method> --dump-args --dump-return"],
    'stage-8-network-traffic-capture-via-mitmproxy': ["For deeper API discovery once pinning is bypassed.", "```bash"],
    'run-mitmproxy-on-host': ["mitmproxy --listen-port 8080"],
    'configure-android-device-proxy-to-host-8080': [],
    'install-mitmproxy-ca-cert-on-device': [],
    'pull-from-http-mitm-it-on-the-device-or': [],
    'push-to-system-etc-security-cacerts-on-rooted-device': [],
    'use-the-frida-pinning-bypass-script-while-traffic-flows-through-mitmproxy': [],
    'all-api-calls-visible-in-mitmproxy-ui': [],
    'decision-tree-what-to-do-with-what-you-find': [],
    'anti-patterns': ["- **Don't grep only for \"password\"** \u2014 most secrets have specific high-signal patterns (AKIA, AIza, eyJ, etc.). Generic word grep produces too much noise.", "- **Don't skip XAPK split APKs** \u2014 config.armeabi splits and config.<lang> splits sometimes contain different code paths.", "- **Don't trust expired JWTs as \"dead intel\"** \u2014 the path structure, endpoint list, and signing algorithm are still useful. The 8-year-expired-JWT example above shows this.", "- **Don't reverse only the latest version** \u2014 older APK versions (via APKMirror version history) sometimes have secrets removed in newer versions but still active server-side.", "- **Don't ignore Firebase even if app looks \"simple\"** \u2014 Firebase rules misconfigurations (public read on Firestore) are extremely common.", "- **Don't run Frida on a production device** \u2014 use rooted emulator or test device only."],
    'tooling-install-one-time': ["```bash", "brew install jadx p7zip", "pip install --break-system-packages frida-tools objection"],
    'genymotion-or-avd-for-rooted-android-emulator': ["For APK download convenience, can add a `download-apk` shell function:", "```bash", "download-apk() {", "local pkg=\"$1\"", "curl -sk -L --max-time 60 \"https://d.apkpure.net/b/APK/$pkg?version=latest\" -o \"$pkg.apk\"", "echo \"Downloaded $(wc -c < \"$pkg.apk\") bytes\"", "file \"$pkg.apk\""],
    'bridge-to-neighboring-skills': ["- `offensive-osint` \u2014 Play Store / APKMirror enum is part of broader OSINT", "- `hunt-cloud-misconfig` \u2014 Firebase public-read is exactly this skill's specialty post-discovery", "- `hunt-api-misconfig` \u2014 JWT manipulation once you have the algorithm + sample token", "- `evidence-hygiene` \u2014 extracted secrets need redaction before report inclusion", "- `redteam-mindset` \u2014 APK reverse on day-1 of an engagement, not as an afterthought"],
    'real-world-finding-template-anonymized-authorized-engagement': ["**Finding: Hardcoded JWT + 30+ Internal API Endpoints in a customer-facing APK**", "- Subject: Hardcoded artifacts in legacy mobile build reveal internal API surface", "- Observations: Decompilation of `com.<client>.<app>` revealed embedded JWT (expired ~8 years earlier) and 30+ `/v1/*` endpoint paths against `api2.<client>.example` (internal-only externally)", "- Description: APK ships with developer build artifacts. Path tokens are security-by-obscurity; API endpoint inventory is reconnaissance-grade.", "- Impact: Post-VPN-foothold (via cred compromise), attacker has full API surface map without binary reverse. HS256 secret recovery (via SSRF/LFI) would yield arbitrary token forging.", "- Recommendation: rotate HS256 secret, migrate to RS256, remove hardcoded URLs from builds, audit all org APKs.", "- Evidence: extracted strings, decoded JWT, endpoint inventory"],
    'related-skills-chains': ["- **`cloud-iam-deep`** \u2014 APK secret extraction frequently yields live AWS/GCP/Azure credentials. Chain primitive: jadx string-grep produces AWS Access Key ID + Secret \u2192 `cloud-iam-deep` `aws sts get-caller-identity` \u2192 role/policy enumeration \u2192 IAM privilege-escalation path (one of 24 documented AWS escalation patterns) \u2192 cloud-plane takeover. Same flow applies to GCP service-account JSON and Azure shared-access-signature tokens extracted from APK resources.", "- **`hunt-api-misconfig`** \u2014 APK endpoint inventory hands you the API surface for free; mass-assignment, JWT, and CORS bugs are typical. Chain primitive: APK reveals `/v1/users/me` and `/v1/admin/users` \u2192 `hunt-api-misconfig` mass-assignment probes (`{is_admin:true}`) against `/v1/users/me` \u2192 admin role escalation \u2192 access to `/v1/admin/users`.", "- **`hunt-rce`** \u2014 Hardcoded JWT signing secrets (HS256) extracted from APK enable arbitrary token forging. Chain primitive: APK strings yield HS256 secret \u2192 forge admin token \u2192 access admin API \u2192 if API has eval/template/sink \u2192 `hunt-rce` to server. Also: exported components with intent-injection sinks can reach `Runtime.exec` if app is local-installed.", "- **`offensive-osint`** \u2014 APK is one node in the broader org recon graph; pair with breach corpora and cert transparency. Chain primitive: APK reveals internal API hostname `api2.example.com` \u2192 `offensive-osint` certificate-transparency lookup \u2192 discover sibling subdomains \u2192 expanded attack surface.", "- **`redteam-report-template`** \u2014 APK findings need clear \"what the binary leaks\" framing because client engineers often dismiss mobile-static findings as \"obfuscation problem.\" Chain primitive: validated finding (token/URL/secret extracted) \u2192 `triage-validation` 7-Question Gate (specifically: \"does this credential still authenticate today?\") \u2192 `redteam-report-template` packaging with explicit binary version + extraction reproduction steps."],
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