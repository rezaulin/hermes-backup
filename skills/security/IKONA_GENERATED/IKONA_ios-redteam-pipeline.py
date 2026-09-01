#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/ios-redteam-pipeline

Skill: App Store search API (no auth, no scraping needed)
Desc : End-to-end iOS red-team pipeline — IPA acquisition (App Store extraction, TestFlight, enterprise/ad-hoc sideload), class-dump/Hopper/Ghidra static analysis, Info.plist + entitlements + Keychain secret extraction, App Transport Security (ATS) misconfig + certificate-pinning bypass (frida-ios-dump, objection, SSL Kill Switch 2), URL-scheme / Universal Link hijack, exported-service enumeration, Frida runtime instrumentation. Companion to apk-redteam-pipeline for the iOS side of a mobile app catalogue. Use when target has an iOS app (App Store listing, TestFlight link, enterprise MDM distribution), when an IPA URL is found hosted on a web server, or when post-recon mentions "iOS app" / "mobile app" in scope alongside an Apple developer account.

Run:  python claude-bughunter-ios-redteam-pipeline.py --help
      python claude-bughunter-ios-redteam-pipeline.py --list
      python claude-bughunter-ios-redteam-pipeline.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/ios-redteam-pipeline'
TITLE = 'App Store search API (no auth, no scraping needed)'
DESCRIPTION = 'End-to-end iOS red-team pipeline — IPA acquisition (App Store extraction, TestFlight, enterprise/ad-hoc sideload), class-dump/Hopper/Ghidra static analysis, Info.plist + entitlements + Keychain secret extraction, App Transport Security (ATS) misconfig + certificate-pinning bypass (frida-ios-dump, objection, SSL Kill Switch 2), URL-scheme / Universal Link hijack, exported-service enumeration, Frida runtime instrumentation. Companion to apk-redteam-pipeline for the iOS side of a mobile app catalogue. Use when target has an iOS app (App Store listing, TestFlight link, enterprise MDM distribution), when an IPA URL is found hosted on a web server, or when post-recon mentions "iOS app" / "mobile app" in scope alongside an Apple developer account.'

PAYLOADS = {
    'main': ["name: ios-redteam-pipeline", "description: End-to-end iOS red-team pipeline \u2014 IPA acquisition (App Store extraction, TestFlight, enterprise/ad-hoc sideload), class-dump/Hopper/Ghidra static analysis, Info.plist + entitlements + Keychain secret extraction, App Transport Security (ATS) misconfig + certificate-pinning bypass (frida-ios-dump, objection, SSL Kill Switch 2), URL-scheme / Universal Link hijack, exported-service enumeration, Frida runtime instrumentation. Companion to apk-redteam-pipeline for the iOS side of a mobile app catalogue. Use when target has an iOS app (App Store listing, TestFlight link, enterprise MDM distribution), when an IPA URL is found hosted on a web server, or when post-recon mentions \"iOS app\" / \"mobile app\" in scope alongside an Apple developer account.", "sources: public_research, frida_docs, objection_docs, owasp_mastg", "report_count: 0"],
    'when-to-use-this-skill': ["Trigger when:", "- Recon surfaces 1+ apps under the target's Apple Developer / App Store publisher page", "- A TestFlight public link or enterprise/ad-hoc `.ipa`/`manifest.plist` (OTA install) is found", "- Customer-facing app, dealer/partner portal, or employee mobile companion app ships on iOS", "- Bug bounty program lists iOS in scope", "- `apk-redteam-pipeline` already found Android endpoints/secrets \u2014 the iOS build often ships a *different* backend version worth diffing (see `hunt-shadow-api`)", "DO NOT use for:", "- Android-only targets \u2014 that's `apk-redteam-pipeline`", "- React Native / Flutter apps already fully covered by JS-bundle analysis on the web side", "- Server-side only assessments with no mobile client in scope"],
    'stage-0-inventory-all-org-owned-ios-apps': ["```bash"],
    'app-store-search-api-no-auth-no-scraping-needed': ["curl -s \"https://itunes.apple.com/search?term=<brand>&country=us&entity=software&limit=50\" | python3 -m json.tool"],
    'pull-the-full-metadata-for-a-known-bundle-id-once-you-have-one': ["curl -s \"https://itunes.apple.com/lookup?bundleId=com.<brand>.app&country=us\"", "Extract: `trackId`, `bundleId`, `sellerName` (developer account \u2014 pivot to find sibling apps), `version`,", "`releaseNotes` (changelogs often reference deprecated/removed API behavior \u2014 feeds `hunt-shadow-api`).", "Cross-reference sibling-app bundle IDs surfaced from Android APK inventories (same", "multi-brand conglomerate usually reuses `com.<corp>.<sub-brand>` naming on both platforms)."],
    'stage-1-ipa-acquisition': [],
    'primary-from-a-real-device-you-control-no-jailbreak-needed-for-a-purchased-free-app': ["```bash"],
    'install-the-app-on-a-real-device-via-apple-configurator-2-or-xcode-then-pull-the-ipa': [],
    'apple-configurator-2-macos-devices-select-device-right-click-installed-app-save-to': [],
    'or-via-libimobiledevice': ["brew install libimobiledevice ideviceinstaller", "ideviceinstaller -l              # list installed apps + bundle IDs"],
    'secondary-testflight-if-the-program-distributes-betas-publicly': ["Open the public TestFlight link, install via the TestFlight app, then extract as above.", "TestFlight builds are frequently LESS hardened than App Store releases (debug logging left on,", "staging API hosts hardcoded) \u2014 always prefer a TestFlight build over the Store build if both exist."],
    'tertiary-enterprise-ad-hoc-distribution-ota-install': ["```bash"],
    'itms-services-links-embed-a-manifest-plist-with-a-direct-ipa-url': ["curl -s \"https://<target>/manifest.plist\" | plutil -convert xml1 -o - -"],
    'look-for-key-software-package-key-that-url-is-a-directly-downloadable-unencrypted-ipa': ["curl -sk -L \"<software-package-url>\" -o target.ipa", "Enterprise/ad-hoc IPAs are **not FairPlay-encrypted** \u2014 no jailbreak or decryption tooling needed,", "unlike an App Store binary pulled from a device."],
    'decrypting-an-app-store-sourced-binary-only-if-extracted-from-a-jailbroken-device': ["App Store binaries are FairPlay-encrypted at rest; a binary copied off a jailbroken device", "needs runtime decryption (`frida-ios-dump`, `bagbak`, or `flexdecrypt`) before static tools can", "read it meaningfully:", "```bash", "pip install --break-system-packages frida-tools"],
    'with-frida-server-running-on-the-jailbroken-device-and-the-app-in-foreground': ["python3 dump.py <bundle_id>          # frida-ios-dump \u2014 outputs a decrypted .ipa"],
    'stage-2-unpack-and-static-analysis': ["```bash"],
    'an-ipa-is-just-a-zip': ["unzip -o target.ipa -d extracted_target/", "cd extracted_target/Payload/*.app"],
    'info-plist-bundle-id-url-schemes-ats-config-entitlements-hint': ["plutil -convert xml1 -o - Info.plist"],
    'entitlements-codesign-reads-the-app-bundle-or-the-mach-o-binary-not-info-plist': ["codesign -d --entitlements :- Payload/<AppName>.app 2>/dev/null || \\", "security cms -D -i embedded.mobileprovision | plutil -convert xml1 -o - -"],
    'class-dump-for-objective-c-symbol-class-recovery-compiled-binary-not-the-app-bundle': ["brew install class-dump", "class-dump -H <AppBinaryName> -o headers/"],
    'swift-binaries-class-dump-won-t-show-much-use-hopper-ghidra-or-nm-strings-instead': ["nm -a <AppBinaryName> | grep -i swift | head -50", "strings -a <AppBinaryName> > strings_target.txt", "For a fast triage pass without a disassembler, the strings dump alone usually surfaces most of", "what Stage 3 is looking for."],
    'stage-3-secret-grep-same-catalog-as-apk-redteam-pipeline-ios-specific-sources-added': ["```bash"],
    'url-grep-owned-domain-references': ["grep -oE 'https?://[a-zA-Z0-9.-]+\\.(target1|target2|target3)\\.(com|io|net)[a-zA-Z0-9./_?=&%-]*' strings_target.txt | sort -u"],
    'cloud-credentials-same-60-pattern-catalog-as-android-reuse-verbatim': ["grep -oE 'AKIA[A-Z0-9]{16}'                             # AWS Access Key", "grep -oE 'AIza[A-Za-z0-9_-]{35}'                        # Google API key", "grep -oE 'eyJ[A-Za-z0-9_-]+\\.eyJ[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]*' strings_target.txt   # JWT"],
    'ios-specific-googleservice-info-plist-firebase-config-bundled-per-platform': ["find extracted_target -iname \"GoogleService-Info.plist\" -exec plutil -convert xml1 -o - {} \\;"],
    'look-for-api-key-project-id-storage-bucket-gcm-sender-id-google-app-id-same-firebase': [],
    'public-read-tests-as-apk-redteam-pipeline-stage-6': [],
    'ios-specific-hardcoded-config-plists-shipped-in-the-bundle': ["find extracted_target -iname \"*.plist\" ! -iname \"Info.plist\" -exec sh -c 'echo \"=== {} ===\"; plutil -convert xml1 -o - \"{}\"' \\;"],
    'app-transport-security-exceptions-info-plist-tells-you-if-arbitrary-insecure-loads-are-allowed': ["plutil -extract NSAppTransportSecurity xml1 -o - Info.plist 2>/dev/null"],
    'keychain-items-left-in-a-backup-if-you-have-a-device-backup-encrypted-or-not': ["```bash", "pip install --break-system-packages iphone_backup_decrypt   # for encrypted local backups"],
    'keychain-dumper-run-on-a-jailbroken-device-for-live-keychain-contents': ["./keychain-dumper -e   # -e also decodes entitlements per item, showing which app owns which secret"],
    'stage-4-app-transport-security-ats-misconfig-certificate-pinning-bypass': [],
    'check-for-blanket-ats-disablement-the-single-most-common-ios-network-misconfig': ["```bash", "plutil -extract NSAppTransportSecurity xml1 -o - Info.plist", "Red flags in the output:", "- `NSAllowsArbitraryLoads = true` at the top level \u2014 HTTP (cleartext) allowed anywhere, app-wide.", "- Per-domain `NSExceptionAllowsInsecureHTTPLoads = true` for a domain that carries auth tokens.", "- `NSAllowsArbitraryLoadsInWebContent = true` \u2014 WKWebView traffic exempted, common blind spot.", "A blanket ATS exception + a network position (rogue AP, ARP spoof, malicious VPN profile) =", "plaintext credential/token interception without touching pinning at all."],
    'certificate-pinning-bypass-when-pinning-is-present-and-correctly-configured': ["```bash", "pip install --break-system-packages frida-tools objection", "objection --gadget <bundle_id> explore"],
    'inside-objection': ["ios sslpinning disable", "If you want a Frida script instead, don't hand-roll one \u2014 use a maintained universal bypass", "(e.g. the widely-used `frida-ios-pinning`/`ios-ssl-bypass` community scripts). Modern iOS TLS goes", "through **BoringSSL**, so a reliable universal hook targets `SSL_CTX_set_custom_verify` /", "`SSL_get_psk_identity` at the native layer and forces the verify callback to return \"OK\" \u2014 this", "catches `URLSession`, `AFNetworking`, `Alamofire`, and `TrustKit` at once, which per-delegate", "Objective-C hooks (like the deprecated `NSURLConnection` delegate) miss:", "```bash"],
    'pull-a-maintained-universal-boringssl-layer-bypass-and-run-it': ["frida -U -f <bundle_id> -l ios-ssl-bypass.js --no-pause", "In practice, prefer **SSL Kill Switch 2** (jailbroken device, installs as a tweak) or", "**objection's `ios sslpinning disable`** over any hand-rolled script \u2014 both cover the common", "pinning implementations (`NSURLSession`, `AFNetworking`, `TrustKit`) without per-app tuning."],
    'stage-5-url-scheme-universal-link-enumeration': ["```bash"],
    'custom-url-schemes-cfbundleurltypes-anything-can-invoke-these-via-safari-another-app': ["plutil -extract CFBundleURLTypes xml1 -o - Info.plist"],
    'universal-links-associated-domains-applinks-requires-a-matching-apple-app-site-association': ["plutil -extract com.apple.developer.associated-domains xml1 -o - Info.plist 2>/dev/null", "curl -s \"https://<domain>/.well-known/apple-app-site-association\" | python3 -m json.tool", "For each custom scheme found (e.g. `myapp://`):", "- Trigger it from Safari/Notes and observe what the app does with parameters:", "`myapp://reset-password?token=x&redirect=https://evil.com` \u2014 does the app trust an", "attacker-supplied `redirect`/`url`/`callback` param and load it in a WebView (open-redirect \u2192", "WebView-XSS chain) or use it to bypass an auth screen?", "- If the scheme is also registered by another app on the device (scheme squatting), a malicious", "app can intercept traffic intended for the legitimate app \u2014 check `CFBundleURLName` uniqueness.", "- Universal Links degrade to the custom scheme when the AASA validation fails or is absent \u2014", "test both paths for the same parameter-injection surface."],
    'stage-6-runtime-instrumentation-frida-objection': ["Requires a jailbroken device (checkra1n/palera1n for older iOS, or a Corellium virtual device) \u2014", "unlike Android, there is no practical rooted-emulator equivalent for iOS.", "```bash"],
    'setup': ["pip install --break-system-packages frida-tools objection"],
    'install-frida-server-on-the-jailbroken-device-via-cydia-sileo-frida-repo-matching-the': [],
    'host-frida-tools-version-exactly-version-skew-is-the-1-cause-of-failed-to-attach-errors': [],
    'full-interactive-exploration': ["objection --gadget <bundle_id> explore"],
    'inside-objection': ["ios hooking watch class <ClassName>", "ios hooking watch class_method <Class>.<method> --dump-args --dump-return", "ios keychain dump", "ios plist dump", "ios cookies get"],
    'network-traffic-capture-once-pinning-is-bypassed': ["```bash", "mitmproxy --listen-port 8080"],
    'set-the-device-wi-fi-proxy-to-host-8080-install-the-mitmproxy-ca-via-http-mitm-it-on-device': [],
    'settings-general-vpn-device-management-trust-the-cert-then-enable-full-trust-under': [],
    'certificate-trust-settings-ios-requires-this-second-step-unlike-android': [],
    'decision-tree-what-to-do-with-what-you-find': [],
    'anti-patterns': ["- **Don't assume App Store = FairPlay-encrypted requires jailbreak** \u2014 TestFlight and enterprise/ad-hoc", "builds are frequently NOT encrypted and need no decryption step at all. Always check distribution", "channel before reaching for `frida-ios-dump`.", "- **Don't skip Swift binaries because class-dump shows nothing** \u2014 `strings` and `nm` still work; a", "proper Swift-aware disassembler (Hopper, Ghidra with Swift demangling) recovers the rest.", "- **Don't stop at \"pinning is present\" as a finding** \u2014 pinning is a mitigation, not a vulnerability;", "the finding is what you can do once it's bypassed (or the ATS misconfig that makes it moot).", "- **Don't ignore WKWebView-loaded content** \u2014 `NSAllowsArbitraryLoadsInWebContent` is a distinct,", "frequently-overlooked exception from the top-level ATS setting.", "- **Don't run Frida instrumentation against a personal/production Apple ID device** \u2014 use a", "dedicated jailbroken test device or Corellium instance."],
    'tooling-install-one-time': ["```bash", "brew install libimobiledevice ideviceinstaller class-dump", "pip install --break-system-packages frida-tools objection iphone_backup_decrypt"],
    'jailbroken-test-device-checkra1n-palera1n-or-a-corellium-virtual-ios-device-for-runtime-work': [],
    'frida-server-installed-on-device-via-the-frida-cydia-sileo-repo': [],
    'related-skills-chains': ["- **`apk-redteam-pipeline`** \u2014 the Android counterpart; run both when a target ships on both", "platforms. Sibling bundle IDs and shared backend endpoints frequently surface cross-platform.", "- **`hunt-shadow-api`** \u2014 mobile builds (iOS and Android alike) often hardcode an older API", "version than the current web app. Chain: IPA reveals `/v1/*` endpoints \u2192 `hunt-shadow-api`", "diffs `/v1/` against the current `/v3/` for auth/validation regressions.", "- **`cloud-iam-deep`** \u2014 IPA secret extraction frequently yields live AWS/GCP/Azure credentials", "or Firebase configs. Chain: strings-grep produces an AWS key \u2192 `cloud-iam-deep` privilege", "analysis.", "- **`hunt-api-misconfig`** \u2014 hardcoded JWTs/API keys extracted here feed directly into JWT", "algorithm-confusion and mass-assignment testing there.", "- **`evidence-hygiene`** \u2014 extracted Keychain items and secrets need redaction before report", "inclusion.", "- **`offensive-osint`** \u2014 App Store developer-page enumeration is part of the broader org recon", "graph; pair with certificate-transparency lookups for the same brand."],
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