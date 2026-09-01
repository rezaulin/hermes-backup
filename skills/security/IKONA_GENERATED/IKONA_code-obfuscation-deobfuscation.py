#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/code-obfuscation-deobfuscation

Skill: SKILL: Code Obfuscation & Deobfuscation — Expert Analysis Playbook
Desc : >-

Run:  python hack-skills-code-obfuscation-deobfuscation.py --help
      python hack-skills-code-obfuscation-deobfuscation.py --list
      python hack-skills-code-obfuscation-deobfuscation.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/code-obfuscation-deobfuscation'
TITLE = 'SKILL: Code Obfuscation & Deobfuscation — Expert Analysis Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: code-obfuscation-deobfuscation", "description: >-", "Code obfuscation analysis and deobfuscation playbook. Use when reversing", "binaries protected by junk code, opaque predicates, self-modifying code,", "control flow flattening, VM protection, or string encryption."],
    'skill-code-obfuscation-deobfuscation-expert-analysis-playbook': [],
    '0-related-routing': ["- [anti-debugging-techniques](../anti-debugging-techniques/SKILL.md) when the obfuscated binary also has anti-debug layers", "- [symbolic-execution-tools](../symbolic-execution-tools/SKILL.md) when using angr/Z3 for automated deobfuscation", "- [vm-and-bytecode-reverse](../vm-and-bytecode-reverse/SKILL.md) for deep VM protector bytecode analysis"],
    'quick-identification-picks': [],
    '1-junk-code-opaque-predicates': [],
    '1-1-junk-code-insertion': ["Dead code that never affects program output, added to increase analysis time.", "**Identification**:", "- Instructions that write to registers/memory never read afterward", "- Function calls whose return values are discarded and have no side effects", "- Loops with invariant bounds that compute unused results", "**Removal strategy**:", "1. Compute def-use chains (IDA/Ghidra data flow analysis)", "2. Mark instructions with no downstream use as dead", "3. Verify removal doesn't change program behavior (trace comparison)"],
    '1-2-opaque-predicates': ["Conditional branches where the condition is always true or always false, but this is non-obvious.", "**Deobfuscation**:", "- Abstract interpretation: prove the condition is constant", "- Symbolic execution: Z3 proves `\u2200x: predicate(x) = True`", "- Pattern matching: recognize known opaque predicate families", "- Dynamic: trace and observe the branch is never taken / always taken", "```python", "import z3", "x = z3.BitVec('x', 32)", "s = z3.Solver()", "s.add(x * (x + 1) % 2 != 0)", "print(s.check())  # unsat \u2192 always true"],
    '2-self-modifying-code-smc': ["Runtime code patching: encrypted code is decrypted just before execution."],
    '2-1-xor-decryption-loop-most-common': ["```asm", "lea esi, [encrypted_code]", "mov ecx, code_length", "mov al, xor_key", "decrypt_loop:", "xor byte [esi], al", "inc esi", "loop decrypt_loop", "jmp encrypted_code  ; now decrypted"],
    '2-2-analysis-strategy': ["1. Identify the decryption routine (look for XOR/ADD/SUB in loops writing to .text)", "2. Set breakpoint AFTER the loop completes", "3. At breakpoint: dump the decrypted memory region", "4. Re-analyze the dumped code in IDA/Ghidra", "5. For multi-layer: repeat for each decryption stage"],
    '2-3-automated-unpacking-via-emulation': ["```python", "from unicorn import *", "from unicorn.x86_const import *", "mu = Uc(UC_ARCH_X86, UC_MODE_32)", "mu.mem_map(0x400000, 0x10000)", "mu.mem_write(0x400000, binary_code)", "mu.emu_start(decrypt_entry, decrypt_end)", "decrypted = mu.mem_read(code_start, code_length)"],
    '3-control-flow-flattening-cff': [],
    '3-1-structure': ["Original sequential blocks are transformed into a dispatcher loop:", "Original:      A \u2192 B \u2192 C \u2192 D", "Flattened:     \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510", "\u2502   dispatcher     \u2502", "\u2502   switch(state)  \u2502\u25c4\u2500\u2500\u2500\u2500\u2500\u2510", "\u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524      \u2502", "\u2502 case 1: block A  \u2502\u2500\u2500\u2500\u2500\u2500\u2500\u2524", "\u2502 case 2: block B  \u2502\u2500\u2500\u2500\u2500\u2500\u2500\u2524", "\u2502 case 3: block C  \u2502\u2500\u2500\u2500\u2500\u2500\u2500\u2524", "\u2502 case 4: block D  \u2502\u2500\u2500\u2500\u2500\u2500\u2500\u2518", "\u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518", "Each block sets `state = next_state` before jumping back to the dispatcher."],
    '3-2-recovery-techniques': [],
    '3-3-symbolic-deflattening-angr-approach': ["```python", "import angr, claripy", "proj = angr.Project('./obfuscated')", "cfg = proj.analyses.CFGFast()"],
    'find-dispatcher-block-highest-in-degree-basic-block': ["dispatcher = max(cfg.graph.nodes(), key=lambda n: cfg.graph.in_degree(n))"],
    'for-each-case-block-symbolically-determine-successor': ["for block in case_blocks:", "state = proj.factory.blank_state(addr=block.addr)"],
    '4-movfuscator': [],
    '4-1-concept': ["All computation reduced to `mov` instructions only (Turing-complete via memory-mapped computation tables). Created by Christopher Domas."],
    '4-2-identification': ["- Function contains only `mov` instructions (no add, sub, xor, jmp, call)", "- Large lookup tables in data section", "- Memory-mapped flag registers"],
    '4-3-demovfuscation': [],
    '5-vm-protection-vmprotect-themida-code-virtualizer': [],
    '5-1-vm-architecture': ["Protected code \u2192 bytecode compiler \u2192 custom bytecode", "Runtime: VM entry (pushad/pushfd) \u2192 fetch \u2192 decode \u2192 execute \u2192 VM exit (popad/popfd)"],
    '5-2-vm-entry-point-identification': ["```asm", "; Typical VMProtect entry", "pushad                    ; save all registers", "pushfd                    ; save flags", "mov ebp, esp              ; VM stack frame", "sub esp, VM_LOCALS_SIZE   ; allocate VM context", "mov esi, bytecode_addr    ; bytecode instruction pointer", "jmp vm_dispatcher         ; enter VM loop"],
    '5-3-handler-table-extraction': ["1. Find dispatcher (large switch or indirect jump via table)", "2. Each case/entry = one VM handler (implements one VM opcode)", "3. Map handler addresses to operations by analyzing each handler:", "- Handler reads operand from bytecode stream (esi)", "- Performs operation on VM registers/stack", "- Advances bytecode pointer", "- Returns to dispatcher"],
    '5-4-devirtualization-approaches': [],
    '5-5-vmprotect-specifics': ["- Uses opaque predicates in dispatcher", "- Handler mutation: same opcode, different handler code per build", "- Multiple VM layers (VM inside VM)", "- Integrates anti-debug and integrity checks"],
    '6-string-encryption': [],
    '6-1-common-patterns': [],
    '6-2-automated-string-decryption': ["```python"],
    'ghidra-script-find-xor-decryption-calls-emulate-them': ["from ghidra.program.model.symbol import SourceType", "decrypt_func = getFunction(\"decrypt_string\")", "refs = getReferencesTo(decrypt_func.getEntryPoint())", "for ref in refs:", "call_addr = ref.getFromAddress()"],
    '7-import-hiding': [],
    '7-1-getprocaddress-hash-lookup': ["FARPROC resolve(DWORD hash) {", "// Walk PEB \u2192 LDR \u2192 InMemoryOrderModuleList", "// For each DLL, walk export table", "// Hash each export name, compare with target hash", "// Return matching function pointer"],
    '7-2-recovery': ["1. Identify the hash algorithm (common: CRC32, djb2, ROR13+ADD)", "2. Compute hashes for all known API names", "3. Build hash \u2192 API name lookup table", "4. Annotate resolved calls in IDA/Ghidra"],
    '7-3-common-hash-algorithms': [],
    '8-anti-disassembly-tricks': [],
    '8-1-techniques': [],
    '8-2-ida-fixes': ["Right-click \u2192 Undefine (U)", "Right-click \u2192 Code (C) at correct offset", "Edit \u2192 Patch \u2192 Assemble (for permanent fix)"],
    '9-decision-tree': ["Obfuscated binary \u2014 how to approach?", "\u251c\u2500 Can you run it?", "\u2502  \u251c\u2500 Yes \u2192 Dynamic analysis first", "\u2502  \u2502  \u251c\u2500 Set BP on interesting APIs (file, network, crypto)", "\u2502  \u2502  \u251c\u2500 Trace execution to understand real behavior", "\u2502  \u2502  \u2514\u2500 Dump decrypted code/strings at runtime", "\u2502  \u2514\u2500 No (embedded/firmware/exotic arch) \u2192 Static only", "\u2502     \u2514\u2500 Identify obfuscation type from patterns below", "\u251c\u2500 What does the code look like?", "\u2502  \u251c\u2500 Giant flat switch/dispatcher loop?", "\u2502  \u2502  \u251c\u2500 State variable drives control flow \u2192 CFF", "\u2502  \u2502  \u2502  \u2514\u2500 Use D-810 or symbolic deflattening", "\u2502  \u2502  \u2514\u2500 Bytecode fetch-decode-execute \u2192 VM protection", "\u2502  \u2502     \u2514\u2500 Extract handlers, build disassembler", "\u2502  \u251c\u2500 Only mov instructions?", "\u2502  \u2502  \u2514\u2500 movfuscator \u2192 demovfuscator tool", "\u2502  \u251c\u2500 XOR/ADD loop writing to .text section?", "\u2502  \u2502  \u2514\u2500 SMC \u2192 breakpoint after decode, dump", "\u2502  \u251c\u2500 Impossible conditions in branches?", "\u2502  \u2502  \u2514\u2500 Opaque predicates \u2192 Z3 proving or pattern removal", "\u2502  \u251c\u2500 Disassembly looks wrong / functions overlap?", "\u2502  \u2502  \u2514\u2500 Anti-disassembly \u2192 manual re-analysis at correct offsets", "\u2502  \u251c\u2500 No readable strings?", "\u2502  \u2502  \u2514\u2500 String encryption \u2192 hook decrypt function or emulate", "\u2502  \u251c\u2500 No imports in IAT?", "\u2502  \u2502  \u2514\u2500 Import hiding \u2192 identify hash, build lookup table", "\u2502  \u2514\u2500 pushad/pushfd \u2192 complex code \u2192 popad/popfd?", "\u2502     \u2514\u2500 VM protector entry/exit \u2192 full VM analysis", "\u2514\u2500 What tool to use?", "\u251c\u2500 Known protector (VMProtect/Themida) \u2192 specific deprotection guide", "\u251c\u2500 Custom obfuscation \u2192 combine: IDA scripting + Triton + manual", "\u251c\u2500 CTF challenge \u2192 angr symbolic execution often fastest", "\u2514\u2500 Malware analysis \u2192 dynamic (debugger + API monitor) first"],
    '10-toolbox': [],
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