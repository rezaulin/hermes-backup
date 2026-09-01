#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/anti-debugging-techniques

Skill: SKILL: Anti-Debugging Techniques — Detection & Bypass Playbook
Desc : >-

Run:  python hack-skills-anti-debugging-techniques.py --help
      python hack-skills-anti-debugging-techniques.py --list
      python hack-skills-anti-debugging-techniques.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/anti-debugging-techniques'
TITLE = 'SKILL: Anti-Debugging Techniques — Detection & Bypass Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: anti-debugging-techniques", "description: >-", "Anti-debugging detection and bypass playbook. Use when reversing protected", "binaries that detect debuggers via ptrace, PEB flags, timing checks, or", "signal/exception handlers on Linux and Windows."],
    'skill-anti-debugging-techniques-detection-bypass-playbook': [],
    '0-related-routing': ["- [code-obfuscation-deobfuscation](../code-obfuscation-deobfuscation/SKILL.md) when the binary also uses control flow flattening, VM protection, or string encryption", "- [vm-and-bytecode-reverse](../vm-and-bytecode-reverse/SKILL.md) when the anti-debug sits inside a custom VM dispatcher", "- [symbolic-execution-tools](../symbolic-execution-tools/SKILL.md) when you want to symbolically skip anti-debug checks entirely"],
    'advanced-reference': ["Also load [ANTI_DEBUG_MATRIX.md](./ANTI_DEBUG_MATRIX.md) when you need:", "- Complete cross-reference matrix of technique \u00d7 OS \u00d7 detection method \u00d7 bypass method", "- Per-technique reliability ratings and false-positive notes", "- Tool compatibility chart (GDB, x64dbg, WinDbg, Frida, ScyllaHide)"],
    'quick-bypass-picks': [],
    '1-linux-anti-debug-techniques': [],
    '1-1-ptrace-ptrace-traceme': ["The classic self-attach: a process calls `ptrace(PTRACE_TRACEME, 0, 0, 0)`. If a debugger is already attached, the call fails (returns -1).", "if (ptrace(PTRACE_TRACEME, 0, 0, 0) == -1) {", "exit(1); // debugger detected", "**Bypass methods**:"],
    '1-2-proc-self-status-tracerpid': ["FILE *f = fopen(\"/proc/self/status\", \"r\");", "// parse TracerPid: if non-zero \u2192 debugger attached", "**Bypass**: Mount a FUSE filesystem over `/proc/self`, or `LD_PRELOAD` hook `fopen`/`fread` to filter `TracerPid` to 0."],
    '1-3-timing-checks-rdtsc-clock-gettime': ["Measures elapsed time between two points; debugger single-stepping causes noticeable delay.", "```asm", "rdtsc", "mov ebx, eax       ; save low 32 bits", "; ... protected code ...", "rdtsc", "sub eax, ebx", "cmp eax, 0x1000    ; threshold", "ja  debugger_detected", "**Bypass**: Set hardware breakpoint after second `rdtsc`, modify `eax` to pass the comparison. Or use Frida to replace the timing function."],
    '1-4-signal-based-detection-sigtrap': ["volatile int caught = 0;", "void handler(int sig) { caught = 1; }", "signal(SIGTRAP, handler);", "raise(SIGTRAP);", "if (!caught) exit(1); // debugger swallowed the signal", "When a debugger is attached, `SIGTRAP` is consumed by the debugger rather than delivered to the handler. **Bypass**: In GDB, use `handle SIGTRAP nostop pass` to forward the signal."],
    '1-5-proc-self-maps-ld-preload-detection': ["Checks for injected libraries or memory regions characteristic of debuggers/instrumentation.", "FILE *f = fopen(\"/proc/self/maps\", \"r\");", "while (fgets(buf, sizeof(buf), f)) {", "if (strstr(buf, \"frida\") || strstr(buf, \"LD_PRELOAD\"))", "exit(1);", "**Bypass**: Hook `fopen(\"/proc/self/maps\")` to return a filtered version, or rename Frida's agent library."],
    '1-6-environment-variable-checks': ["Some protections check for `LD_PRELOAD`, `LINES`, `COLUMNS` (set by GDB's terminal), or debugger-specific env vars.", "**Bypass**: Unset suspicious env vars before launch, or hook `getenv()`."],
    '2-windows-anti-debug-techniques': [],
    '2-1-isdebuggerpresent-checkremotedebuggerpresent': ["if (IsDebuggerPresent()) ExitProcess(1);", "BOOL debugged = FALSE;", "CheckRemoteDebuggerPresent(GetCurrentProcess(), &debugged);", "if (debugged) ExitProcess(1);", "**Bypass**: Hook `kernel32!IsDebuggerPresent` to return 0, or patch PEB directly."],
    '2-2-peb-flags': ["```asm", "mov rax, gs:[0x60]    ; PEB", "movzx eax, byte [rax+0x02]  ; BeingDebugged", "test eax, eax", "jnz debugger_detected", "**Bypass**: Zero all four fields. ScyllaHide does this automatically."],
    '2-3-ntqueryinformationprocess': ["**Bypass**: Hook `ntdll!NtQueryInformationProcess` to return clean values per info class."],
    '2-4-hardware-breakpoint-detection': ["CONTEXT ctx;", "ctx.ContextFlags = CONTEXT_DEBUG_REGISTERS;", "GetThreadContext(GetCurrentThread(), &ctx);", "if (ctx.Dr0 || ctx.Dr1 || ctx.Dr2 || ctx.Dr3)", "ExitProcess(1);", "**Bypass**: Hook `GetThreadContext` to zero DR0\u2013DR3, or use `NtSetInformationThread(ThreadHideFromDebugger)` preemptively (ironically, the anti-debug technique itself)."],
    '2-5-int-2d-int-3-ud2-exception-tricks': ["`INT 2D` is the kernel debug service interrupt. Without a debugger, it raises `STATUS_BREAKPOINT`; with a debugger, behavior differs (byte skipping).", "```asm", "xor eax, eax", "int 2dh", "nop          ; debugger may skip this byte", "; ... divergent execution path ...", "**Bypass**: Handle in VEH or patch the interrupt instruction."],
    '2-6-tls-callbacks': ["TLS callbacks execute before `main()` / `WinMain()`. Anti-debug checks placed here run before the debugger's initial break.", "**Bypass**: In x64dbg, set \"Break on TLS Callbacks\" option. In WinDbg, use `sxe ld` to break on module load."],
    '2-7-ntsetinformationthread-threadhidefromdebugger': ["NtSetInformationThread(GetCurrentThread(), ThreadHideFromDebugger, NULL, 0);", "After this call, the thread becomes invisible to the debugger \u2014 breakpoints and single-stepping stop working silently.", "**Bypass**: Hook `NtSetInformationThread` to NOP when `ThreadInfoClass == 0x11`."],
    '2-8-veh-based-detection': ["Registers a Vectored Exception Handler that checks `EXCEPTION_RECORD` for debugger-specific behavior (single-step flag, guard page violations with debugger semantics).", "**Bypass**: Understand the VEH logic and ensure the exception chain behaves identically to non-debugged execution."],
    '3-advanced-multi-layer-techniques': [],
    '3-1-self-debugging-fork-ptrace': ["The process forks a child that attaches to the parent via ptrace. If an external debugger is already attached, the child's ptrace fails.", "pid_t child = fork();", "if (child == 0) {", "if (ptrace(PTRACE_ATTACH, getppid(), 0, 0) == -1)", "kill(getppid(), SIGKILL);", "ptrace(PTRACE_DETACH, getppid(), 0, 0);", "_exit(0);", "wait(NULL);", "**Bypass**: Patch the `fork()` return or kill/detach the watchdog child."],
    '3-2-multi-process-debugging-detection': ["Parent and child cooperatively check each other's debug state, creating a mutual-watch pattern.", "**Bypass**: Attach to both processes (GDB `follow-fork-mode`, or two debugger instances)."],
    '3-3-timing-based-with-multiple-checkpoints': ["Distributes timing checks across multiple functions, comparing cumulative drift. Single patches fail because the total still exceeds threshold.", "**Bypass**: Frida `Interceptor.replace` all timing sources (`rdtsc`, `clock_gettime`, `QueryPerformanceCounter`) to return controlled values."],
    '3-4-nanomite-int3-patching': ["Original conditional jumps are replaced with `INT3` (0xCC). A parent debugger process handles each `INT3`, evaluates the condition, and sets the child's EIP accordingly.", "**Bypass**: Reconstruct the original jump table by tracing all `INT3` handlers, then patch the binary."],
    '4-countermeasure-tools': [],
    '5-systematic-bypass-methodology': ["Step 1: Static analysis \u2014 identify anti-debug calls", "\u2514\u2500 Search for: ptrace, IsDebuggerPresent, NtQuery, rdtsc,", "GetTickCount, SIGTRAP, INT 2D, TLS directory entries", "Step 2: Classify each check", "\u251c\u2500 API-based \u2192 hook or patch the call", "\u251c\u2500 Flag-based \u2192 patch PEB/proc fields", "\u251c\u2500 Timing-based \u2192 spoof time source", "\u251c\u2500 Exception-based \u2192 forward/handle exception correctly", "\u2514\u2500 Multi-process \u2192 handle both processes", "Step 3: Apply bypass (order matters)", "1. Load ScyllaHide / set LD_PRELOAD (covers 80% of checks)", "2. Handle TLS callbacks (break before main)", "3. Patch remaining custom checks (Frida or binary patch)", "4. Verify: run with breakpoints, confirm no premature exit", "Step 4: Validate bypass completeness", "\u2514\u2500 Set BP on ExitProcess/exit/_exit \u2014 if hit unexpectedly,", "a check was missed \u2192 trace back from exit call"],
    '6-decision-tree': ["Binary exits/crashes under debugger?", "\u251c\u2500 Crashes immediately before main?", "\u2502  \u2514\u2500 TLS callback anti-debug", "\u2502     \u2514\u2500 Enable TLS callback breaking in debugger", "\u251c\u2500 Crashes at startup?", "\u2502  \u251c\u2500 Linux: check for ptrace(TRACEME)", "\u2502  \u2502  \u2514\u2500 LD_PRELOAD hook or NOP patch", "\u2502  \u2514\u2500 Windows: check IsDebuggerPresent / PEB", "\u2502     \u2514\u2500 ScyllaHide or manual PEB patch", "\u251c\u2500 Crashes after some execution?", "\u2502  \u251c\u2500 Consistent crash point \u2192 API-based check", "\u2502  \u2502  \u251c\u2500 NtQueryInformationProcess \u2192 hook return values", "\u2502  \u2502  \u251c\u2500 /proc/self/status \u2192 filter TracerPid", "\u2502  \u2502  \u2514\u2500 Hardware BP detection \u2192 hook GetThreadContext", "\u2502  \u251c\u2500 Variable crash point \u2192 timing-based check", "\u2502  \u2502  \u2514\u2500 Hook rdtsc / QueryPerformanceCounter", "\u2502  \u2514\u2500 Crash on breakpoint hit \u2192 exception-based check", "\u2502     \u251c\u2500 INT 2D / INT 3 trick \u2192 handle in VEH", "\u2502     \u2514\u2500 SIGTRAP handler \u2192 GDB: handle SIGTRAP pass", "\u251c\u2500 Debugger loses control silently?", "\u2502  \u2514\u2500 ThreadHideFromDebugger", "\u2502     \u2514\u2500 Hook NtSetInformationThread", "\u251c\u2500 Child process detects and kills parent?", "\u2502  \u2514\u2500 Self-debugging (fork+ptrace)", "\u2502     \u2514\u2500 Patch fork() or handle both processes", "\u2514\u2500 All basic bypasses applied but still detected?", "\u2514\u2500 Multi-layer / custom checks", "\u251c\u2500 Use Frida for comprehensive API hooking", "\u251c\u2500 Full emulation with Qiling", "\u2514\u2500 Trace all calls to exit/abort to find remaining checks"],
    '7-ctf-real-world-patterns': [],
    'common-ctf-anti-debug-patterns': [],
    'real-world-protections': [],
    '8-quick-reference-bypass-cheat-sheet': [],
    'linux-one-liners': ["```bash"],
    'ld-preload-anti-ptrace': ["echo 'long ptrace(int r, ...) { return 0; }' > /tmp/ap.c", "gcc -shared -o /tmp/ap.so /tmp/ap.c", "LD_PRELOAD=/tmp/ap.so ./target"],
    'gdb-catch-and-bypass-ptrace': ["(gdb) catch syscall ptrace", "(gdb) commands"],
    'frida-anti-debug-bypass-cross-platform': ["```javascript", "// Hook IsDebuggerPresent (Windows)", "Interceptor.replace(", "Module.getExportByName('kernel32.dll', 'IsDebuggerPresent'),", "new NativeCallback(() => 0, 'int', [])", "// Hook ptrace (Linux)", "Interceptor.replace(", "Module.getExportByName(null, 'ptrace'),", "new NativeCallback(() => 0, 'long', ['int', 'int', 'pointer', 'pointer'])", "// Timing spoof", "Interceptor.attach(Module.getExportByName(null, 'clock_gettime'), {", "onLeave(retval) {", "// manipulate timespec to hide debugger delay"],
    'x64dbg-scyllahide-quick-setup': ["1. Plugins \u2192 ScyllaHide \u2192 Options", "2. Check: PEB BeingDebugged, NtGlobalFlag, HeapFlags", "3. Check: NtQueryInformationProcess (all classes)", "4. Check: NtSetInformationThread (HideFromDebugger)", "5. Check: GetTickCount, QueryPerformanceCounter", "6. Apply \u2192 restart debugging session"],
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