#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/vm-and-bytecode-reverse

Skill: SKILL: VM & Bytecode Reverse Engineering — Expert Analysis Playbook
Desc : >-

Run:  python hack-skills-vm-and-bytecode-reverse.py --help
      python hack-skills-vm-and-bytecode-reverse.py --list
      python hack-skills-vm-and-bytecode-reverse.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/vm-and-bytecode-reverse'
TITLE = 'SKILL: VM & Bytecode Reverse Engineering — Expert Analysis Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: vm-and-bytecode-reverse", "description: >-", "Custom VM and bytecode reverse engineering playbook. Use when CTF challenges", "or protected software implement custom virtual machines with proprietary", "bytecode, dispatcher loops, or maze-style challenges."],
    'skill-vm-bytecode-reverse-engineering-expert-analysis-playbook': [],
    '0-related-routing': ["- [code-obfuscation-deobfuscation](../code-obfuscation-deobfuscation/SKILL.md) when the VM is a commercial protector (VMProtect/Themida)", "- [symbolic-execution-tools](../symbolic-execution-tools/SKILL.md) when using angr to solve VM-based challenges", "- [anti-debugging-techniques](../anti-debugging-techniques/SKILL.md) when the VM includes anti-debug checks"],
    'quick-identification': [],
    '1-custom-vm-identification': [],
    '1-1-structural-indicators': ["VM Architecture Components:", "\u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510", "\u2502  Bytecode Program (data section)\u2502", "\u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524", "\u2502  Program Counter (pc/ip)        \u2502", "\u2502  Register File / Stack          \u2502", "\u2502  Memory / Data Area             \u2502", "\u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524", "\u2502  Dispatcher Loop                \u2502", "\u2502  \u251c\u2500 Fetch: opcode = code[pc]    \u2502", "\u2502  \u251c\u2500 Decode: lookup handler      \u2502", "\u2502  \u2514\u2500 Execute: run handler        \u2502", "\u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518"],
    '1-2-ida-ghidra-signatures': ["**Switch dispatcher** (most common in CTF):", "while (running) {", "unsigned char op = bytecode[pc++];", "switch (op) {", "case 0x00: /* nop */       break;", "case 0x01: /* push imm */  stack[sp++] = bytecode[pc++]; break;", "case 0x02: /* add */       stack[sp-2] += stack[sp-1]; sp--; break;", "// ...", "case 0xFF: /* halt */      running = 0; break;", "**Table dispatcher** (more optimized):", "typedef void (*handler_t)(vm_ctx_t*);", "handler_t handlers[256] = { handle_nop, handle_push, handle_add, ... };", "while (running) {", "handlers[bytecode[pc++]](&ctx);"],
    '2-analysis-methodology': [],
    'step-1-find-the-dispatcher': ["Look for:", "- Large switch statement (many cases) in a loop", "- Array of function pointers indexed by a byte from a data buffer", "- Single function with high cyclomatic complexity", "- Cross-references to a data buffer read byte-by-byte"],
    'step-2-map-opcodes-to-operations': ["For each case/handler, determine:"],
    'step-3-extract-bytecode-program': ["```python"],
    'typical-extraction-from-binary': ["import struct", "with open('challenge', 'rb') as f:", "f.seek(bytecode_offset)", "bytecode = f.read(bytecode_length)"],
    'or-from-ida': [],
    'bytecode-idc-get-bytes-bytecode-addr-bytecode-len': [],
    'step-4-write-custom-disassembler': ["```python", "OPCODES = {", "0x00: (\"nop\",  0),    # (mnemonic, operand_bytes)", "0x01: (\"push\", 1),    # push immediate byte", "0x02: (\"pop\",  0),", "0x03: (\"add\",  0),", "0x04: (\"sub\",  0),", "0x05: (\"xor\",  0),", "0x06: (\"cmp\",  0),", "0x07: (\"jmp\",  2),    # jump to 16-bit address", "0x08: (\"je\",   2),", "0x09: (\"jne\",  2),", "0x0A: (\"mov\",  2),    # mov reg, imm", "0x0B: (\"load\", 1),    # load from memory[operand]", "0x0C: (\"store\",1),    # store to memory[operand]", "0x0D: (\"print\",0),", "0x0E: (\"read\", 0),    # read input", "0xFF: (\"halt\", 0),", "def disassemble(bytecode):", "pc = 0", "while pc < len(bytecode):", "op = bytecode[pc]", "if op not in OPCODES:", "print(f\"  {pc:04x}: UNKNOWN {op:#04x}\")", "pc += 1", "continue", "mnemonic, operand_size = OPCODES[op]", "operands = bytecode[pc+1:pc+1+operand_size]", "operand_str = ' '.join(f'{b:#04x}' for b in operands)", "print(f\"  {pc:04x}: {mnemonic:8s} {operand_str}\")", "pc += 1 + operand_size", "disassemble(bytecode)"],
    'step-5-analyze-disassembled-program': ["With the custom disassembly, apply standard reverse engineering:", "- Identify input reading (read opcode)", "- Trace data flow from input to comparison", "- Determine success/failure conditions", "- Extract the check logic (often XOR/ADD transformations of input compared against constants)"],
    '3-common-vm-patterns-in-ctf': [],
    '3-1-stack-based-vm': ["Operations work on a stack (like JVM or Python bytecode)."],
    '3-2-register-based-vm': ["Operations use register indices (like x86, ARM)."],
    '3-3-brainfuck-like-esoteric-vms': [],
    '4-maze-challenges': [],
    '4-1-identification': ["- Binary reads directional input (WASD, arrow keys, UDLR)", "- 2D array in data section (walls, paths, start, end)", "- Position tracking with x,y coordinates", "- Win condition at specific coordinates"],
    '4-2-map-extraction': ["```python"],
    'extract-maze-grid-from-binary-data-section': ["MAZE_ADDR = 0x601060", "WIDTH = 20", "HEIGHT = 15"],
    'from-binary-dump': ["maze = []", "for row in range(HEIGHT):", "line = \"\"", "for col in range(WIDTH):", "cell = bytecode[MAZE_ADDR + row * WIDTH + col - base_addr]", "if cell == 0: line += \".\"    # path", "elif cell == 1: line += \"#\"  # wall", "elif cell == 2: line += \"S\"  # start", "elif cell == 3: line += \"E\"  # end", "else: line += \"?\"", "maze.append(line)", "print(line)"],
    '4-3-automated-solving': ["```python", "from collections import deque", "def solve_maze(maze, start, end):", "\"\"\"BFS solver returns direction string.\"\"\"", "rows, cols = len(maze), len(maze[0])", "directions = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}", "queue = deque([(start, \"\")])", "visited = {start}", "while queue:", "(r, c), path = queue.popleft()", "if (r, c) == end:", "return path", "for name, (dr, dc) in directions.items():", "nr, nc = r + dr, c + dc", "if (0 <= nr < rows and 0 <= nc < cols and", "maze[nr][nc] != '#' and (nr, nc) not in visited):", "visited.add((nr, nc))", "queue.append(((nr, nc), path + name))", "return None"],
    'find-start-and-end-positions': ["for r, row in enumerate(maze):", "for c, cell in enumerate(row):", "if cell == 'S': start = (r, c)", "if cell == 'E': end = (r, c)", "solution = solve_maze(maze, start, end)", "print(f\"Path: {solution}\")"],
    '4-4-direction-encoding': ["Different challenges encode directions differently:"],
    '5-real-world-vm-protectors': [],
    '5-1-vmprotect-analysis-approach': ["1. Find VM entry: search for pushad/pushfd sequence", "2. Identify VM context structure (registers, flags, bytecode pointer)", "3. Locate handler table (often obfuscated with opaque predicates)", "4. For each handler:", "a. Remove junk code / opaque predicates", "b. Identify the core operation", "c. Document handler semantics", "5. Trace bytecode execution (instruction-level trace)", "6. Reconstruct original code from trace"],
    '5-2-tigress-obfuscator': ["Academic VM obfuscator with configurable protection layers."],
    '5-3-common-vm-protector-patterns': [],
    '6-tools': [],
    'ghidra-sleigh-processor-module': ["For recurring VM architectures, write a Sleigh processor specification:", "define space ram      type=ram_space      size=2  default;", "define space register type=register_space  size=1;", "define register offset=0 size=1 [ R0 R1 R2 R3 FLAGS PC SP ];", "define token opcode(8)", "op = (0,7)", ":NOP    is op=0x00 { }", ":PUSH   imm is op=0x01; imm { SP = SP - 1; *[ram]:1 SP = imm; }", ":POP    is op=0x02 { SP = SP + 1; }", ":ADD    is op=0x03 { local a = *[ram]:1 (SP+1); *[ram]:1 (SP+1) = a + *[ram]:1 SP; SP = SP + 1; }"],
    '7-decision-tree': ["Binary contains custom bytecode interpreter?", "\u251c\u2500 Can you identify the dispatcher?", "\u2502  \u251c\u2500 Yes (switch/table/if-chain)", "\u2502  \u2502  \u251c\u2500 Few opcodes (< 20) \u2192 Simple CTF VM", "\u2502  \u2502  \u2502  \u251c\u2500 Stack-based \u2192 map push/pop/arithmetic ops", "\u2502  \u2502  \u2502  \u251c\u2500 Register-based \u2192 map mov/add/cmp ops", "\u2502  \u2502  \u2502  \u2514\u2500 Write disassembler \u2192 analyze program \u2192 solve", "\u2502  \u2502  \u2502", "\u2502  \u2502  \u2514\u2500 Many opcodes (50+) \u2192 Commercial protector", "\u2502  \u2502     \u251c\u2500 Known protector \u2192 use specific deprotection tools", "\u2502  \u2502     \u2514\u2500 Custom \u2192 trace execution, pattern-match handlers", "\u2502  \u2514\u2500 No clear dispatcher", "\u2502     \u251c\u2500 All-mov instructions \u2192 movfuscator", "\u2502     \u251c\u2500 Encrypted bytecode \u2192 find decryption, dump after decode", "\u2502     \u2514\u2500 Split/distributed handlers \u2192 trace execution to find them", "\u251c\u2500 Is it a maze challenge?", "\u2502  \u251c\u2500 Extract grid from data section", "\u2502  \u251c\u2500 Identify direction encoding", "\u2502  \u251c\u2500 BFS/DFS to find shortest path", "\u2502  \u2514\u2500 Convert path to expected input format", "\u251c\u2500 Is there input validation in VM?", "\u2502  \u251c\u2500 Small input space \u2192 brute-force via Unicorn emulation", "\u2502  \u251c\u2500 Known format \u2192 constrained angr solve", "\u2502  \u2514\u2500 Complex check \u2192 write disassembler, analyze check logic", "\u2514\u2500 Multiple VM layers (VM in VM)?", "\u251c\u2500 Analyze outer VM first", "\u251c\u2500 Extract inner bytecode", "\u251c\u2500 Repeat analysis for inner VM", "\u2514\u2500 Consider: symbolic execution may handle nested VMs directly"],
    '8-ctf-solving-workflow': ["1. Run the binary \u2014 understand I/O behavior", "\u2514\u2500 What input does it expect? What output on success/failure?", "2. Open in IDA/Ghidra \u2014 find the main loop", "\u2514\u2500 Look for while/for loop with switch or indirect jump", "3. Identify VM components:", "\u251c\u2500 Bytecode location (where is the program data?)", "\u251c\u2500 PC/IP variable (how is current position tracked?)", "\u251c\u2500 Registers/stack (where is VM state stored?)", "\u2514\u2500 I/O handlers (which opcodes read input / write output?)", "4. Map all opcodes (create the ISA specification)", "\u2514\u2500 For each case/handler: opcode number, operation, operands", "5. Write disassembler in Python", "\u2514\u2500 Output readable assembly for the bytecode", "6. Analyze the disassembled program:", "\u251c\u2500 Find input reading", "\u251c\u2500 Trace transformations applied to input", "\u251c\u2500 Find comparison against expected values", "\u2514\u2500 Reverse the transformation to find valid input", "7. Solve:", "\u251c\u2500 If simple transforms (XOR, ADD) \u2192 reverse manually", "\u251c\u2500 If complex \u2192 feed to Z3 as constraints", "\u2514\u2500 If maze \u2192 extract grid, run pathfinding"],
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