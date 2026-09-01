#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/memory-forensics-volatility

Skill: SKILL: Memory Forensics — Expert Analysis Playbook
Desc : >-

Run:  python hack-skills-memory-forensics-volatility.py --help
      python hack-skills-memory-forensics-volatility.py --list
      python hack-skills-memory-forensics-volatility.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/memory-forensics-volatility'
TITLE = 'SKILL: Memory Forensics — Expert Analysis Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: memory-forensics-volatility", "description: >-", "Memory forensics playbook using Volatility 2/3. Use when analyzing memory dumps for malware analysis, credential extraction, process investigation, code injection detection, and incident response timeline reconstruction."],
    'skill-memory-forensics-expert-analysis-playbook': [],
    '0-related-routing': ["Before going deep, consider loading:", "- [traffic-analysis-pcap](../traffic-analysis-pcap/SKILL.md) for correlating network artifacts with memory findings", "- [steganography-techniques](../steganography-techniques/SKILL.md) if hidden data suspected in extracted files", "- [windows-privilege-escalation](../windows-privilege-escalation/SKILL.md) for understanding post-exploitation artifacts in memory"],
    'quick-reference': ["Also load [VOLATILITY_CHEATSHEET.md](./VOLATILITY_CHEATSHEET.md) when you need:", "- Vol2 vs Vol3 command comparison table", "- Common plugin sequences for specific investigation types"],
    '1-memory-acquisition': [],
    'linux': ["```bash"],
    'lime-linux-memory-extractor-kernel-module': ["insmod lime.ko \"path=/tmp/mem.lime format=lime\""],
    'proc-kcore-if-available': ["dd if=/proc/kcore of=/tmp/mem.raw bs=1M"],
    'avml-microsoft-s-open-source': ["./avml /tmp/mem.lime"],
    'windows': ["```bash"],
    'winpmem': ["winpmem_mini_x64.exe memdump.raw"],
    'ftk-imager-gui-capture-memory-to-file': [],
    'dumpit-single-click-memory-dump': ["DumpIt.exe"],
    'comae-magnetram': ["MagnetRAMCapture.exe /output memdump.raw"],
    'virtual-machines': ["```bash"],
    'vmware-vmem-file-in-vm-directory-suspend-vm-first': [],
    'virtualbox-vboxmanage-debugvm-vm-name-dumpvmcore-filename-mem-raw': [],
    'kvm-qemu-virsh-dump-domain-memdump-memory-only': [],
    'hyper-v-checkpoint-vm-inspect-bin-files': [],
    '2-volatility-2-vs-3': [],
    '3-analysis-methodology': [],
    'step-1-identify-os': ["```bash"],
    'vol2': ["vol.py -f mem.raw imageinfo", "vol.py -f mem.raw kdbgscan"],
    'vol3': ["vol -f mem.raw windows.info", "vol -f mem.raw banners.Banners"],
    'step-2-process-listing-hidden-process-detection': ["```bash"],
    'vol2': ["vol.py -f mem.raw --profile=PROFILE pslist       # EPROCESS linked list", "vol.py -f mem.raw --profile=PROFILE psscan       # pool tag scan (finds unlinked)", "vol.py -f mem.raw --profile=PROFILE pstree       # parent-child hierarchy"],
    'vol3': ["vol -f mem.raw windows.pslist", "vol -f mem.raw windows.psscan", "vol -f mem.raw windows.pstree", "**Red flags**: Process in `psscan` but not `pslist` = DKOM (Direct Kernel Object Manipulation) hiding."],
    'step-3-network-connections': ["```bash"],
    'vol2': ["vol.py -f mem.raw --profile=PROFILE netscan      # TCP/UDP endpoints", "vol.py -f mem.raw --profile=PROFILE connections   # XP/2003 only", "vol.py -f mem.raw --profile=PROFILE connscan      # closed connections"],
    'vol3': ["vol -f mem.raw windows.netscan", "vol -f mem.raw windows.netstat"],
    'step-4-dll-module-analysis': ["```bash"],
    'vol2': ["vol.py -f mem.raw --profile=PROFILE dlllist -p PID", "vol.py -f mem.raw --profile=PROFILE ldrmodules -p PID   # find unlinked DLLs"],
    'vol3': ["vol -f mem.raw windows.dlllist --pid PID", "**Red flags**: DLL in `dlllist` but `False` in all three `ldrmodules` columns = reflective DLL injection."],
    'step-5-code-injection-detection-malfind': ["```bash"],
    'vol2': ["vol.py -f mem.raw --profile=PROFILE malfind -p PID", "vol.py -f mem.raw --profile=PROFILE malfind -D /tmp/dump/   # dump injected sections"],
    'vol3': ["vol -f mem.raw windows.malfind --pid PID", "**What malfind detects**: Memory regions with `PAGE_EXECUTE_READWRITE` that don't map to a file on disk \u2014 classic shellcode/injection indicator."],
    'step-6-credential-extraction': ["```bash"],
    'vol2': ["vol.py -f mem.raw --profile=PROFILE hashdump      # SAM hashes", "vol.py -f mem.raw --profile=PROFILE lsadump       # LSA secrets", "vol.py -f mem.raw --profile=PROFILE cachedump     # domain cached creds", "vol.py -f mem.raw --profile=PROFILE mimikatz      # (plugin) plaintext creds"],
    'vol3': ["vol -f mem.raw windows.hashdump", "vol -f mem.raw windows.lsadump", "vol -f mem.raw windows.cachedump"],
    'step-7-file-extraction': ["```bash"],
    'vol2': ["vol.py -f mem.raw --profile=PROFILE filescan | grep -i \"password\\|secret\\|flag\"", "vol.py -f mem.raw --profile=PROFILE dumpfiles -Q OFFSET -D /tmp/dump/"],
    'vol3': ["vol -f mem.raw windows.filescan", "vol -f mem.raw windows.dumpfiles --virtaddr OFFSET"],
    'step-8-registry-analysis': ["```bash"],
    'vol2': ["vol.py -f mem.raw --profile=PROFILE hivelist", "vol.py -f mem.raw --profile=PROFILE printkey -K \"Software\\Microsoft\\Windows\\CurrentVersion\\Run\"", "vol.py -f mem.raw --profile=PROFILE userassist    # program execution evidence"],
    'vol3': ["vol -f mem.raw windows.registry.hivelist", "vol -f mem.raw windows.registry.printkey --key \"Software\\Microsoft\\Windows\\CurrentVersion\\Run\""],
    'step-9-command-history': ["```bash"],
    'vol2': ["vol.py -f mem.raw --profile=PROFILE cmdscan       # cmd.exe history", "vol.py -f mem.raw --profile=PROFILE consoles       # full console output"],
    'vol3': ["vol -f mem.raw windows.cmdline"],
    'step-10-timeline-generation': ["```bash"],
    'vol2': ["vol.py -f mem.raw --profile=PROFILE timeliner --output=body --output-file=timeline.body", "mactime -b timeline.body -d > timeline.csv"],
    'vol3': ["vol -f mem.raw timeliner.Timeliner"],
    '4-linux-memory-analysis': ["```bash"],
    'vol2-requires-linux-profile': ["vol.py -f mem.lime --profile=LinuxProfile linux_pslist", "vol.py -f mem.lime --profile=LinuxProfile linux_pstree", "vol.py -f mem.lime --profile=LinuxProfile linux_netstat", "vol.py -f mem.lime --profile=LinuxProfile linux_bash        # bash history", "vol.py -f mem.lime --profile=LinuxProfile linux_enumerate_files", "vol.py -f mem.lime --profile=LinuxProfile linux_proc_maps -p PID", "vol.py -f mem.lime --profile=LinuxProfile linux_malfind"],
    'vol3': ["vol -f mem.lime linux.pslist", "vol -f mem.lime linux.pstree", "vol -f mem.lime linux.bash", "vol -f mem.lime linux.check_afinfo     # rootkit detection", "vol -f mem.lime linux.check_syscall    # syscall hooking", "vol -f mem.lime linux.tty_check        # TTY hooking"],
    'building-linux-profiles-vol2': ["```bash", "cd volatility/tools/linux"],
    'creates-module-dwarf-system-map-zip-as-profile': ["zip LinuxProfile.zip module.dwarf /boot/System.map-$(uname -r)"],
    'place-in-volatility-plugins-overlays-linux': [],
    '5-malware-indicators-in-memory': [],
    'normal-parent-child-relationships-windows': ["System (4)", "\u2514\u2500\u2500 smss.exe", "\u2514\u2500\u2500 csrss.exe", "\u2514\u2500\u2500 wininit.exe", "\u2514\u2500\u2500 services.exe", "\u2514\u2500\u2500 svchost.exe (multiple)", "\u2514\u2500\u2500 spoolsv.exe", "\u2514\u2500\u2500 lsass.exe", "\u2514\u2500\u2500 winlogon.exe", "\u2514\u2500\u2500 explorer.exe", "\u2514\u2500\u2500 user applications"],
    '6-decision-tree': ["Memory dump acquired \u2014 need to analyze", "\u251c\u2500\u2500 What OS?", "\u2502   \u251c\u2500\u2500 Windows \u2192 vol imageinfo / windows.info (\u00a73 Step 1)", "\u2502   \u2514\u2500\u2500 Linux \u2192 build profile or use Vol3 auto-detect (\u00a74)", "\u251c\u2500\u2500 Malware investigation?", "\u2502   \u251c\u2500\u2500 Check processes: pslist vs psscan (hidden?) (\u00a73 Step 2)", "\u2502   \u251c\u2500\u2500 Check parent-child: pstree (suspicious spawning?) (\u00a75)", "\u2502   \u251c\u2500\u2500 Check injections: malfind (RWX memory?) (\u00a73 Step 5)", "\u2502   \u251c\u2500\u2500 Check DLLs: ldrmodules (unlinked?) (\u00a73 Step 4)", "\u2502   \u251c\u2500\u2500 Check network: netscan (C2 connections?) (\u00a73 Step 3)", "\u2502   \u2514\u2500\u2500 Extract suspicious files: dumpfiles (\u00a73 Step 7)", "\u251c\u2500\u2500 Credential recovery?", "\u2502   \u251c\u2500\u2500 SAM hashes \u2192 hashdump (\u00a73 Step 6)", "\u2502   \u251c\u2500\u2500 LSA secrets \u2192 lsadump (\u00a73 Step 6)", "\u2502   \u251c\u2500\u2500 Cached domain creds \u2192 cachedump (\u00a73 Step 6)", "\u2502   \u2514\u2500\u2500 Plaintext passwords \u2192 mimikatz plugin (\u00a73 Step 6)", "\u251c\u2500\u2500 Incident timeline?", "\u2502   \u251c\u2500\u2500 timeliner for comprehensive timeline (\u00a73 Step 10)", "\u2502   \u251c\u2500\u2500 cmdscan / consoles for command history (\u00a73 Step 9)", "\u2502   \u251c\u2500\u2500 userassist for program execution (\u00a73 Step 8)", "\u2502   \u2514\u2500\u2500 Cross-reference with PCAP timeline (\u2192 traffic-analysis-pcap)", "\u251c\u2500\u2500 CTF / flag hunting?", "\u2502   \u251c\u2500\u2500 filescan + grep for flag patterns (\u00a73 Step 7)", "\u2502   \u251c\u2500\u2500 cmdscan for typed flags/passwords (\u00a73 Step 9)", "\u2502   \u251c\u2500\u2500 Clipboard: clipboard plugin", "\u2502   \u251c\u2500\u2500 Screenshots: screenshot plugin", "\u2502   \u2514\u2500\u2500 Environment vars: envars plugin", "\u2514\u2500\u2500 Linux-specific?", "\u251c\u2500\u2500 linux_bash for shell history (\u00a74)", "\u251c\u2500\u2500 linux_check_syscall for rootkit (\u00a74)", "\u2514\u2500\u2500 linux_netstat for connections (\u00a74)"],
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