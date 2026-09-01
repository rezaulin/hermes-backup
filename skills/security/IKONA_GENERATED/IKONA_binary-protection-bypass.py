#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/binary-protection-bypass

Skill: SKILL: Binary Protection Bypass — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-binary-protection-bypass.py --help
      python hack-skills-binary-protection-bypass.py --list
      python hack-skills-binary-protection-bypass.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/binary-protection-bypass'
TITLE = 'SKILL: Binary Protection Bypass — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: binary-protection-bypass", "description: >-", "Binary protection bypass playbook. Use when identifying and bypassing ASLR, PIE, NX/DEP, stack canary, RELRO, FORTIFY_SOURCE, CET, and MTE protections in ELF binaries to enable exploitation."],
    'skill-binary-protection-bypass-expert-attack-playbook': [],
    '0-related-routing': ["- [stack-overflow-and-rop](../stack-overflow-and-rop/SKILL.md) \u2014 ROP chains to bypass NX, ret2libc for ASLR bypass", "- [format-string-exploitation](../format-string-exploitation/SKILL.md) \u2014 primary method for leaking canary, PIE, libc addresses", "- [heap-exploitation](../heap-exploitation/SKILL.md) \u2014 heap attacks for RELRO bypass (when GOT is read-only)", "- [arbitrary-write-to-rce](../arbitrary-write-to-rce/SKILL.md) \u2014 what to overwrite when GOT is protected by RELRO"],
    'advanced-reference': ["Load [PROTECTION_BYPASS_MATRIX.md](./PROTECTION_BYPASS_MATRIX.md) for comprehensive protection \u00d7 bypass \u00d7 primitive matrix."],
    '1-protection-identification': ["```bash", "$ checksec ./binary", "[*] '/path/to/binary'", "Arch:     amd64-64-little", "RELRO:    Full RELRO          \u2190 GOT read-only", "Stack:    Canary found        \u2190 stack canary enabled", "NX:       NX enabled          \u2190 stack not executable", "PIE:      PIE enabled         \u2190 position-independent code", "FORTIFY:  Enabled             \u2190 fortified libc functions"],
    'quick-identification-table': [],
    '2-aslr-bypass': ["ASLR randomizes base addresses of stack, heap, libc, and mmap regions at each execution."],
    'aslr-entropy-x86-64-linux': [],
    '3-pie-bypass': ["PIE (Position Independent Executable) randomizes the binary's own code/data base address."],
    'partial-overwrite-details': ["PIE binary loaded at: 0x555555554000 (example)", "Function at offset 0x1234: 0x555555555234", "Overwrite return address last 2 bytes: 0x?234 \u2192 0x?XXX", "Unknown: bits 12-15 (one nibble = 4 bits = 16 possibilities)", "Success rate: 1/16 per attempt"],
    '4-nx-dep-bypass': ["NX (No-eXecute) / DEP (Data Execution Prevention) prevents execution of code on the stack/heap."],
    'mprotect-chain': ["```python"],
    'make-stack-executable-then-jump-to-shellcode': ["rop = b'A' * offset", "rop += p64(pop_rdi) + p64(stack_page)     # page-aligned address", "rop += p64(pop_rsi) + p64(0x1000)         # size", "rop += p64(pop_rdx) + p64(7)              # PROT_READ|PROT_WRITE|PROT_EXEC", "rop += p64(mprotect_addr)", "rop += p64(shellcode_addr)                 # jump to shellcode on now-executable stack"],
    '5-relro-bypass': [],
    'full-relro-alternative-targets': ["See [arbitrary-write-to-rce](../arbitrary-write-to-rce/SKILL.md) for comprehensive target list."],
    '6-canary-bypass': [],
    'canary-format': ["x86:    0x00XXXXXX (4 bytes, leading null byte)", "x86-64: 0x00XXXXXXXXXXXXXX (8 bytes, leading null byte)", "The leading `\\x00` prevents string operations from accidentally reading the canary."],
    '7-fortify-source-bypass': ["`_FORTIFY_SOURCE=2` adds buffer size checking and restricts format string operations."],
    'format-string-with-fortify-source': ["```python"],
    '1-n-is-blocked-by-printf-chk': [],
    'but-sequential-non-positional-n-may-still-work': [],
    'print-exact-byte-count-then-hn-must-be-very-precise': [],
    'or-find-unfortified-printf-in-binary-libc-via-rop': [],
    '8-cet-control-flow-enforcement-technology': ["Intel CET adds two mechanisms:"],
    'shadow-stack': ["- Hardware-maintained copy of return addresses", "- On `ret`, CPU checks shadow stack matches actual stack", "- Mismatch \u2192 `#CP` fault (control protection exception)"],
    'indirect-branch-tracking-ibt': ["- Indirect `jmp`/`call` must land on `ENDBR64` instruction", "- Non-ENDBR landing \u2192 `#CP` fault", "**Bypass**:", "- Data-only attacks (don't change control flow)", "- Find valid ENDBR gadgets that chain into useful operations", "- JOP with ENDBR-prefixed gadgets", "- Target structures outside CFI scope (modprobe_path, function pointer arrays)"],
    '9-mte-memory-tagging-extension-arm': ["ARM MTE assigns 4-bit tags to memory pointers and allocations. Tag mismatch = fault."],
    'bypass-approaches': [],
    '10-decision-tree': ["Binary analysis: checksec output", "\u251c\u2500\u2500 NX disabled?", "\u2502   \u2514\u2500\u2500 Shellcode on stack/heap (simplest path)", "\u251c\u2500\u2500 NX enabled (standard modern binary)?", "\u2502   \u251c\u2500\u2500 Need code execution \u2192 ROP/ret2libc", "\u2502   \u2502", "\u2502   \u251c\u2500\u2500 Canary enabled?", "\u2502   \u2502   \u251c\u2500\u2500 fork server? \u2192 byte-by-byte brute-force", "\u2502   \u2502   \u251c\u2500\u2500 Format string? \u2192 leak canary via %p", "\u2502   \u2502   \u251c\u2500\u2500 Heap vuln? \u2192 canary doesn't protect heap", "\u2502   \u2502   \u2514\u2500\u2500 Partial RELRO? \u2192 overwrite __stack_chk_fail@GOT", "\u2502   \u2502", "\u2502   \u251c\u2500\u2500 PIE enabled?", "\u2502   \u2502   \u251c\u2500\u2500 Format string? \u2192 leak .text address \u2192 PIE base", "\u2502   \u2502   \u251c\u2500\u2500 Partial overwrite \u2192 last 12 bits fixed (1/16 brute-force)", "\u2502   \u2502   \u2514\u2500\u2500 OOB read? \u2192 leak code pointer", "\u2502   \u2502", "\u2502   \u251c\u2500\u2500 ASLR enabled?", "\u2502   \u2502   \u251c\u2500\u2500 Info leak available \u2192 leak libc base", "\u2502   \u2502   \u251c\u2500\u2500 No leak \u2192 ret2dlresolve or SROP", "\u2502   \u2502   \u251c\u2500\u2500 32-bit? \u2192 brute-force feasible (~4096 attempts)", "\u2502   \u2502   \u2514\u2500\u2500 Return-to-PLT (no libc base needed for PLT calls)", "\u2502   \u2502", "\u2502   \u251c\u2500\u2500 RELRO level?", "\u2502   \u2502   \u251c\u2500\u2500 None/Partial \u2192 GOT overwrite", "\u2502   \u2502   \u2514\u2500\u2500 Full \u2192 alternative targets:", "\u2502   \u2502       \u251c\u2500\u2500 glibc < 2.34 \u2192 __malloc_hook / __free_hook", "\u2502   \u2502       \u251c\u2500\u2500 glibc \u2265 2.34 \u2192 _IO_FILE / exit_funcs / TLS_dtor_list", "\u2502   \u2502       \u251c\u2500\u2500 .fini_array (if writable)", "\u2502   \u2502       \u2514\u2500\u2500 Stack return address", "\u2502   \u2502", "\u2502   \u2514\u2500\u2500 FORTIFY_SOURCE?", "\u2502       \u251c\u2500\u2500 Blocks positional %n \u2192 use sequential %n or heap exploit", "\u2502       \u2514\u2500\u2500 Blocks buffer overflows in fortified functions \u2192 use unfortified paths", "\u251c\u2500\u2500 CET (shadow stack)?", "\u2502   \u251c\u2500\u2500 ROP blocked \u2192 data-only attack or JOP", "\u2502   \u2514\u2500\u2500 ENDBR-gadget chaining", "\u2514\u2500\u2500 MTE (ARM)?", "\u251c\u2500\u2500 1/16 brute-force", "\u2514\u2500\u2500 Stay in-bounds for relative corruption"],
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