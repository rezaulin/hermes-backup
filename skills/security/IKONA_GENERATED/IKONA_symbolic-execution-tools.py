#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/symbolic-execution-tools

Skill: SKILL: Symbolic Execution Tools — Expert Analysis Playbook
Desc : >-

Run:  python hack-skills-symbolic-execution-tools.py --help
      python hack-skills-symbolic-execution-tools.py --list
      python hack-skills-symbolic-execution-tools.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/symbolic-execution-tools'
TITLE = 'SKILL: Symbolic Execution Tools — Expert Analysis Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: symbolic-execution-tools", "description: >-", "Symbolic execution and constraint solving playbook. Use when solving CTF", "reversing challenges, recovering keys, bypassing checks, or automating", "binary analysis with angr, Z3, or Unicorn Engine."],
    'skill-symbolic-execution-tools-expert-analysis-playbook': [],
    '0-related-routing': ["- [anti-debugging-techniques](../anti-debugging-techniques/SKILL.md) when anti-debug checks need to be symbolically bypassed", "- [code-obfuscation-deobfuscation](../code-obfuscation-deobfuscation/SKILL.md) when using symbolic execution for deobfuscation", "- [vm-and-bytecode-reverse](../vm-and-bytecode-reverse/SKILL.md) when applying angr to custom VM challenges"],
    'advanced-reference': ["Also load [ANGR_COOKBOOK.md](./ANGR_COOKBOOK.md) when you need:", "- 15+ ready-to-use angr script patterns for common CTF challenges", "- Hook templates for scanf, printf, malloc, strcmp", "- Symbolic file input, stdin, argv patterns", "- Optimization tricks for path explosion management"],
    'when-to-use-which-tool': [],
    '1-angr-core-concepts': [],
    '1-1-pipeline': ["Project(binary)", "\u2192 Factory.entry_state() / blank_state(addr=)", "\u2192 SimulationManager(state)", "\u2192 explore(find=target, avoid=bad)", "\u2192 found[0].solver.eval(symbolic_var)"],
    '1-2-essential-setup': ["```python", "import angr", "import claripy", "proj = angr.Project('./challenge', auto_load_libs=False)"],
    'entry-state-start-from-program-entry-point': ["state = proj.factory.entry_state()"],
    'blank-state-start-from-arbitrary-address': ["state = proj.factory.blank_state(addr=0x401000)"],
    'full-init-state-with-command-line-args': ["state = proj.factory.full_init_state(args=['./challenge', arg1_sym])", "simgr = proj.factory.simulation_manager(state)", "simgr.explore(find=0x401234, avoid=[0x401300])", "if simgr.found:", "found = simgr.found[0]", "solution = found.solver.eval(symbolic_input, cast_to=bytes)", "print(f\"Solution: {solution}\")"],
    '1-3-symbolic-variables-claripy': ["```python"],
    'bitvector-fixed-size-integer': ["sym_input = claripy.BVS(\"input\", 64)        # 64-bit symbolic", "sym_byte = claripy.BVS(\"byte\", 8)           # 8-bit symbolic", "sym_buf = claripy.BVS(\"buffer\", 8 * 32)     # 32-byte buffer"],
    'concrete-bitvector': ["concrete = claripy.BVV(0x41, 8)             # concrete value 0x41"],
    'constraints': ["state.solver.add(sym_input > 0)", "state.solver.add(sym_input < 100)", "state.solver.add(sym_byte >= 0x20)           # printable ASCII", "state.solver.add(sym_byte <= 0x7e)"],
    'evaluate': ["value = state.solver.eval(sym_input)", "all_values = state.solver.eval_upto(sym_input, 10)  # up to 10 solutions"],
    '1-4-symbolic-stdin': ["```python", "flag_len = 32", "sym_stdin = claripy.BVS(\"stdin\", 8 * flag_len)", "state = proj.factory.entry_state(stdin=sym_stdin)"],
    'constrain-to-printable-ascii': ["for i in range(flag_len):", "byte = sym_stdin.get_byte(i)", "state.solver.add(byte >= 0x20)", "state.solver.add(byte <= 0x7e)"],
    '1-5-hooking-functions': ["```python"],
    'hook-by-address-skip-n-bytes-of-original-code': ["@proj.hook(0x401100, length=5)", "def skip_check(state):", "state.regs.eax = 1  # force success"],
    'simprocedure-replace-library-function': ["class MyStrcmp(angr.SimProcedure):", "def run(self, s1, s2):", "return claripy.If(", "self.state.memory.load(s1, 32) == self.state.memory.load(s2, 32),", "claripy.BVV(0, 32),", "claripy.BVV(1, 32)", "proj.hook_symbol('strcmp', MyStrcmp())"],
    'hook-common-problematic-functions': ["proj.hook_symbol('printf', angr.SIM_PROCEDURES['libc']['printf']())", "proj.hook_symbol('scanf', angr.SIM_PROCEDURES['libc']['scanf']())", "proj.hook_symbol('puts', angr.SIM_PROCEDURES['libc']['puts']())"],
    '1-6-memory-operations': ["```python"],
    'read-memory-symbolic-aware': ["data = state.memory.load(addr, size)          # returns BV", "data_concrete = state.solver.eval(data, cast_to=bytes)"],
    'write-memory': ["state.memory.store(addr, claripy.BVV(0x41, 8))", "state.memory.store(addr, sym_buf)"],
    'read-write-registers': ["rax = state.regs.rax", "state.regs.rdi = claripy.BVV(0x1000, 64)"],
    '2-z3-constraint-solving': [],
    '2-1-core-api': ["```python", "from z3 import *"],
    'sorts': ["x = BitVec('x', 32)    # 32-bit bitvector", "y = Int('y')             # arbitrary precision integer", "b = Bool('b')            # boolean"],
    'solver': ["s = Solver()", "s.add(x + y == 42)", "s.add(x > 0)", "s.add(y > 0)", "if s.check() == sat:", "m = s.model()", "print(f\"x = {m[x]}, y = {m[y]}\")"],
    '2-2-common-ctf-patterns': ["```python"],
    'serial-key-validation-each-char-satisfies-constraints': ["key = [BitVec(f'k{i}', 8) for i in range(16)]", "s = Solver()", "for k in key:", "s.add(k >= 0x30, k <= 0x7a)  # alphanumeric-ish"],
    'xor-key-recovery': ["plaintext = b\"known_plaintext\"", "ciphertext = b\"\\x12\\x34...\"", "key_byte = BitVec('key', 8)", "s = Solver()", "for p, c in zip(plaintext, ciphertext):", "s.add(p ^ key_byte == c)"],
    'system-of-linear-equations-modular': ["a, b, c = BitVecs('a b c', 32)", "s = Solver()", "s.add(3*a + 5*b + 7*c == 0x12345678)", "s.add(2*a + 4*b + 6*c == 0xDEADBEEF)", "s.add(a ^ b ^ c == 0xCAFEBABE)"],
    '2-3-optimization': ["```python", "from z3 import Optimize", "opt = Optimize()", "x = BitVec('x', 32)", "opt.add(x > 0)", "opt.add(x < 1000)", "opt.minimize(x)  # find smallest satisfying value", "opt.check()", "print(opt.model())"],
    '3-unicorn-engine-code-emulation': [],
    '3-1-basic-setup': ["```python", "from unicorn import *", "from unicorn.x86_const import *", "from capstone import Cs, CS_ARCH_X86, CS_MODE_64", "mu = Uc(UC_ARCH_X86, UC_MODE_64)", "CODE_ADDR = 0x400000", "STACK_ADDR = 0x7fff0000", "STACK_SIZE = 0x10000", "mu.mem_map(CODE_ADDR, 0x10000)", "mu.mem_map(STACK_ADDR, STACK_SIZE)", "mu.mem_write(CODE_ADDR, code_bytes)", "mu.reg_write(UC_X86_REG_RSP, STACK_ADDR + STACK_SIZE - 0x1000)", "mu.reg_write(UC_X86_REG_RBP, STACK_ADDR + STACK_SIZE - 0x1000)", "mu.emu_start(CODE_ADDR, CODE_ADDR + len(code_bytes))", "result = mu.reg_read(UC_X86_REG_RAX)"],
    '3-2-hooking-memory-instructions': ["```python"],
    'hook-memory-access': ["def hook_mem(uc, access, address, size, value, user_data):", "if access == UC_MEM_WRITE:", "print(f\"Write {value:#x} to {address:#x}\")", "elif access == UC_MEM_READ:", "print(f\"Read from {address:#x}\")", "mu.hook_add(UC_HOOK_MEM_READ | UC_HOOK_MEM_WRITE, hook_mem)"],
    'hook-specific-instruction-for-tracing': ["def hook_code(uc, address, size, user_data):", "code = uc.mem_read(address, size)", "md = Cs(CS_ARCH_X86, CS_MODE_64)", "for insn in md.disasm(bytes(code), address):", "print(f\"  {insn.address:#x}: {insn.mnemonic} {insn.op_str}\")", "mu.hook_add(UC_HOOK_CODE, hook_code)"],
    '3-3-use-cases': [],
    '4-angr-exploration-strategies': [],
    '4-1-find-avoid': ["```python", "simgr.explore(", "find=lambda s: b\"Correct\" in s.posix.dumps(1),   # stdout contains \"Correct\"", "avoid=lambda s: b\"Wrong\" in s.posix.dumps(1)      # avoid \"Wrong\" output"],
    '4-2-managing-path-explosion': [],
    '4-3-concrete-symbolic-hybrid': ["```python", "state = proj.factory.entry_state(", "add_options={angr.options.UNICORN}  # use Unicorn for concrete regions", "This dramatically speeds up execution: concrete code runs natively via Unicorn, switching to symbolic only when symbolic variables are involved."],
    '5-practical-workflow': [],
    '5-1-ctf-binary-solving-workflow': ["1. Static analysis: identify input method, success/fail conditions", "\u2514\u2500 Find \"Correct\" / \"Wrong\" strings \u2192 get their xref addresses", "2. Choose tool:", "\u251c\u2500 Pure math (no binary needed) \u2192 Z3", "\u251c\u2500 Small binary, clear success/fail \u2192 angr explore", "\u2514\u2500 Specific function to emulate \u2192 Unicorn", "3. Set up symbolic input:", "\u251c\u2500 stdin \u2192 claripy.BVS + entry_state(stdin=)", "\u251c\u2500 argv \u2192 full_init_state(args=[...])", "\u251c\u2500 file input \u2192 SimFile", "\u2514\u2500 specific memory \u2192 state.memory.store(addr, sym)", "4. Hook problematic functions:", "\u251c\u2500 printf/puts \u2192 SimProcedure or no-op", "\u251c\u2500 scanf \u2192 custom handler", "\u251c\u2500 time/random \u2192 return concrete value", "\u2514\u2500 anti-debug \u2192 skip entirely", "5. Explore and extract:", "\u2514\u2500 simgr.explore(find=, avoid=) \u2192 solver.eval()"],
    '6-decision-tree': ["Need to solve a reversing challenge?", "\u251c\u2500 Is the challenge pure math / equations?", "\u2502  \u2514\u2500 Yes \u2192 Z3", "\u2502     \u251c\u2500 Linear equations \u2192 BitVec + Solver", "\u2502     \u251c\u2500 Modular arithmetic \u2192 BitVec (natural mod 2^n)", "\u2502     \u251c\u2500 Boolean logic \u2192 Bool + Solver", "\u2502     \u2514\u2500 Optimization \u2192 Optimize + minimize/maximize", "\u251c\u2500 Is it a compiled binary with clear success/fail?", "\u2502  \u2514\u2500 Yes \u2192 angr", "\u2502     \u251c\u2500 Input via stdin \u2192 symbolic stdin", "\u2502     \u251c\u2500 Input via argv \u2192 full_init_state with symbolic args", "\u2502     \u251c\u2500 Input via file \u2192 SimFile", "\u2502     \u251c\u2500 Path explosion \u2192 add constraints, avoid paths, hook loops", "\u2502     \u2514\u2500 Complex library calls \u2192 hook with SimProcedure", "\u251c\u2500 Need to emulate a specific function/region?", "\u2502  \u2514\u2500 Yes \u2192 Unicorn Engine", "\u2502     \u251c\u2500 Decryption routine \u2192 map code + data, emulate, read result", "\u2502     \u251c\u2500 Shellcode analysis \u2192 map shellcode, hook syscalls", "\u2502     \u2514\u2500 Key schedule \u2192 emulate with different inputs", "\u251c\u2500 Need to analyze firmware / exotic arch?", "\u2502  \u2514\u2500 Yes \u2192 Qiling (full system emulation with OS support)", "\u251c\u2500 Binary has VM protection?", "\u2502  \u2514\u2500 angr for handler analysis + Z3 for bytecode constraints", "\u2514\u2500 None of the above working?", "\u251c\u2500 Combine: Unicorn for concrete regions + Z3 for constraints", "\u251c\u2500 Manual reverse engineering with debugger", "\u2514\u2500 Side-channel approach (timing, power analysis for hardware)"],
    '7-common-pitfalls-fixes': [],
    '8-tool-versions-installation': ["```bash"],
    'angr-python-3-8': ["pip install angr"],
    'z3': ["pip install z3-solver"],
    'unicorn-engine': ["pip install unicorn"],
    'capstone-disassembly-pairs-with-unicorn': ["pip install capstone"],
    'keystone-assembly': ["pip install keystone-engine"],
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