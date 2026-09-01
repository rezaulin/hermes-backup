#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/traffic-analysis-pcap

Skill: SKILL: Traffic Analysis & PCAP — Expert Analysis Playbook
Desc : >-

Run:  python hack-skills-traffic-analysis-pcap.py --help
      python hack-skills-traffic-analysis-pcap.py --list
      python hack-skills-traffic-analysis-pcap.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/traffic-analysis-pcap'
TITLE = 'SKILL: Traffic Analysis & PCAP — Expert Analysis Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: traffic-analysis-pcap", "description: >-", "Traffic analysis and PCAP forensics playbook. Use when analyzing network captures including Wireshark filters, protocol analysis (HTTP/DNS/FTP/SMTP/USB/WiFi), data extraction, covert channel detection, PCAP repair, TLS decryption, and tshark command-line analysis."],
    'skill-traffic-analysis-pcap-expert-analysis-playbook': [],
    '0-related-routing': ["Before going deep, consider loading:", "- [memory-forensics-volatility](../memory-forensics-volatility/SKILL.md) for correlating memory artifacts with network traffic", "- [steganography-techniques](../steganography-techniques/SKILL.md) for analyzing files extracted from traffic captures", "- [network-protocol-attacks](../network-protocol-attacks/SKILL.md) for understanding attack patterns visible in captures", "- [reverse-shell-techniques](../reverse-shell-techniques/SKILL.md) for identifying shell traffic in captures"],
    '1-pcap-repair': ["```bash", "pcapfix corrupted.pcap -o fixed.pcap           # repair corrupted PCAP"],
    'magic-bytes-d4c3b2a1-pcap-le-a1b2c3d4-pcap-be-0a0d0d0a-pcapng': ["editcap -F pcap capture.pcapng capture.pcap    # convert pcapng\u2192pcap", "mergecap -w merged.pcap file1.pcap file2.pcap  # merge captures"],
    '2-wireshark-essential-filters': [],
    'ip-host-filters': ["ip.addr == 10.0.0.1                  # source or destination", "ip.src == 10.0.0.1                   # source only", "ip.dst == 10.0.0.1                   # destination only", "ip.addr == 10.0.0.0/24              # subnet", "!(ip.addr == 10.0.0.1)              # exclude host"],
    'protocol-filters': ["http                                  # all HTTP", "dns                                   # all DNS", "tcp                                   # all TCP", "ftp                                   # all FTP", "smtp                                  # all SMTP", "tls                                   # all TLS/SSL", "icmp                                  # all ICMP", "arp                                   # all ARP"],
    'tcp-stream': ["tcp.stream eq 5                       # follow specific TCP stream", "tcp.port == 80                        # traffic on port 80", "tcp.flags.syn == 1 && tcp.flags.ack == 0   # SYN packets (connection starts)", "tcp.analysis.retransmission           # retransmitted packets", "tcp.len > 0                           # packets with payload"],
    'http': ["http.request.method == \"POST\"         # POST requests", "http.request.method == \"GET\"          # GET requests", "http.response.code == 200             # successful responses", "http.response.code >= 400             # error responses", "http.request.uri contains \"login\"     # URI contains string", "http.host contains \"target.com\"       # specific host", "http.content_type contains \"json\"     # JSON responses", "http.cookie contains \"session\"        # session cookies", "http.request.full_uri                 # show full URIs (column)"],
    'dns': ["dns.qry.name contains \"evil.com\"     # specific domain queries", "dns.qry.type == 1                    # A records", "dns.qry.type == 28                   # AAAA records", "dns.qry.type == 16                   # TXT records", "dns.flags.response == 1              # DNS responses only", "dns.resp.len > 100                   # large DNS responses"],
    'tls': ["tls.handshake.type == 1              # Client Hello", "tls.handshake.type == 2              # Server Hello", "tls.handshake.extensions.server_name  # SNI (hostname)", "tls.handshake.type == 11             # Certificate"],
    'content-search': ["frame contains \"password\"             # search in raw bytes", "frame contains \"flag{\"                # CTF flag pattern", "tcp contains \"admin\"                  # search in TCP payload"],
    '3-protocol-analysis': [],
    'http-follow-stream-extract': ["Right-click packet \u2192 Follow \u2192 TCP Stream"],
    'shows-full-http-request-response-conversation': [],
    'file-extraction': [],
    'file-export-objects-http-save-all': [],
    'useful-filters-for-credential-hunting': ["http.request.method == \"POST\" && frame contains \"password\"", "http.request.method == \"POST\" && frame contains \"login\"", "http.authbasic                        # Basic auth (base64 encoded)"],
    'https-tls-decryption': ["```bash"],
    'method-1-sslkeylogfile-pre-master-secrets-from-browser': [],
    'set-environment-variable-before-opening-browser': ["export SSLKEYLOGFILE=/tmp/sslkeys.log", "firefox https://target.com"],
    'wireshark-edit-preferences-protocols-tls': [],
    'pre-master-secret-log-filename-tmp-sslkeys-log': [],
    'method-2-server-private-key-for-rsa-key-exchange-only': [],
    'wireshark-edit-preferences-protocols-tls-rsa-keys-list': [],
    'add-ip-port-protocol-key-file-pem': [],
    'dns-tunneling-detection': ["```bash"],
    'indicators-of-dns-tunneling': [],
    '1-unusually-long-subdomain-names-30-chars': [],
    '2-high-volume-of-txt-record-queries-responses': [],
    '3-consistent-query-patterns-to-same-domain': [],
    '4-base32-base64-like-subdomain-strings': [],
    '5-high-query-frequency-from-single-host': [],
    'wireshark-filter-for-suspicious-dns': ["dns.qry.name.len > 50                # long query names", "dns.qry.type == 16                   # TXT records (common for tunneling)", "dns.resp.len > 512                   # large DNS responses"],
    'tshark-extraction': ["tshark -r capture.pcap -Y \"dns.qry.type==16\" -T fields -e dns.qry.name"],
    'ftp-credential-file-extraction': ["```bash"],
    'ftp-credentials-plaintext': [],
    'filter-ftp-request-command-user-ftp-request-command-pass': [],
    'ftp-file-transfer-reconstruction': [],
    'ftp-uses-separate-data-channel-usually-port-20-or-dynamic': [],
    'follow-tcp-stream-of-data-connection-to-extract-file': [],
    'tshark': ["tshark -r capture.pcap -Y \"ftp.request.command==USER || ftp.request.command==PASS\" -T fields -e ftp.request.arg"],
    'smtp-email-content-extraction': ["```bash"],
    'follow-tcp-stream-mail-from-rcpt-to-data-sections': [],
    'attachments-base64-in-mime-decode-content-transfer-encoding-blocks': [],
    'filters': ["smtp.req.command == \"AUTH\"            # authentication (often base64)", "smtp contains \"Content-Disposition: attachment\"   # attachments"],
    'usb-keyboard-hid-capture-decode': ["```bash"],
    'usb-hid-keyboard-traffic-interrupt-transfers-with-8-byte-data': [],
    'filter-usb-transfer-type-0x01': [],
    'extract-keystrokes': ["tshark -r usb.pcap -Y \"usb.capdata && usb.data_len == 8\" -T fields -e usb.capdata > keystrokes.txt"],
    'hid-keycode-layout-byte-0-modifier-byte-2-keycode': [],
    '0x04-a-0x1d-z-0x1e-1-0x27-0-0x28-enter-0x2c-space': [],
    'use-python-online-hid-decoder-to-convert-keycodes-text': [],
    'wifi-wpa-handshake': ["```bash"],
    'capture-airodump-ng-bssid-ap-mac-w-capture-wlan0mon': [],
    'convert-crack-hcxpcapngtool-o-hash-hc22000-capture-pcap': ["hashcat -m 22000 hash.hc22000 wordlist.txt"],
    'deauth-detection-wlan-fc-type-subtype-0x0c': [],
    'icmp-data-exfiltration': ["```bash"],
    'icmp-payload-analysis': [],
    'normal-ping-32-or-64-bytes-of-pattern-data': [],
    'exfiltration-meaningful-data-in-icmp-payload': [],
    'filter': ["icmp && data.len > 48                 # unusual ICMP payload size", "icmp.type == 8                        # echo requests"],
    'extract-icmp-payloads': ["tshark -r capture.pcap -Y \"icmp.type==8\" -T fields -e data.data"],
    '4-data-extraction': [],
    'file-carving': ["```bash"],
    'wireshark-file-export-objects': [],
    'supported-http-smb-tftp-imf-email-dicom': [],
    'manual-from-reassembled-stream': [],
    'follow-tcp-stream-show-as-raw-save-as': [],
    'binwalk-on-exported-stream-data': ["binwalk -e exported_stream.bin", "foremost -i exported_stream.bin -o carved/"],
    'credential-harvesting': ["```bash"],
    'plaintext-ftp-telnet-http-authbasic-smtp-pop-imap': [],
    'ntlm-ntlmssp-auth-username-extract-challenge-response-from-ntlmssp-messages': [],
    'hash-format-user-domain-challenge-ntproofstr-blob-hashcat-m-5600': [],
    'covert-channel-detection': ["Indicators: DNS with long subdomains, ICMP with large payloads, HTTP with encoded headers, regular beacon intervals (C2). Use `tshark -q -z io,stat,1` and `-z conv,tcp` for statistical anomaly detection."],
    '5-networkminer': ["```bash"],
    'automated-pcap-analysis-sudo-apt-install-networkminer': [],
    'open-pcap-auto-extracts-files-images-credentials-sessions-dns': [],
    'files-tab-carved-from-http-smb-ftp-credentials-tab-plaintext-creds': [],
    '6-tshark-command-line-analysis': ["```bash", "tshark -r capture.pcap -Y \"http.request\" -T fields -e http.host -e http.request.uri", "tshark -r capture.pcap -Y \"dns.flags.response==0\" -T fields -e dns.qry.name | sort -u", "tshark -r capture.pcap -Y \"http.request.method==POST\" -T fields -e http.file_data", "tshark -r capture.pcap -q -z io,stat,1                # I/O graph", "tshark -r capture.pcap -q -z conv,tcp                  # TCP conversations", "tshark -r capture.pcap -q -z endpoints,ip              # IP endpoints", "tshark -r capture.pcap -q -z io,phs                    # protocol hierarchy", "tshark -r capture.pcap -q -z follow,tcp,ascii,0        # follow stream 0", "tshark -r capture.pcap --export-objects http,/tmp/exported/"],
    '7-decision-tree': ["PCAP file for analysis", "\u251c\u2500\u2500 File won't open?", "\u2502   \u251c\u2500\u2500 Check magic bytes: xxd | head (\u00a71)", "\u2502   \u251c\u2500\u2500 Repair: pcapfix (\u00a71)", "\u2502   \u2514\u2500\u2500 Convert: editcap pcapng\u2192pcap (\u00a71)", "\u251c\u2500\u2500 What's in the capture? (Quick overview)", "\u2502   \u251c\u2500\u2500 tshark -q -z io,phs (protocol hierarchy) (\u00a76)", "\u2502   \u251c\u2500\u2500 tshark -q -z conv,tcp (conversations) (\u00a76)", "\u2502   \u2514\u2500\u2500 tshark -q -z endpoints,ip (endpoints) (\u00a76)", "\u251c\u2500\u2500 HTTP traffic?", "\u2502   \u251c\u2500\u2500 Export objects: File \u2192 Export Objects \u2192 HTTP (\u00a74)", "\u2502   \u251c\u2500\u2500 Credential hunt: POST + password/login filters (\u00a73)", "\u2502   \u251c\u2500\u2500 Follow streams: interesting request/response pairs (\u00a73)", "\u2502   \u2514\u2500\u2500 Encrypted (HTTPS)? \u2192 need SSLKEYLOGFILE or RSA key (\u00a73)", "\u251c\u2500\u2500 DNS traffic?", "\u2502   \u251c\u2500\u2500 Long subdomains? \u2192 DNS tunneling (\u00a73)", "\u2502   \u251c\u2500\u2500 High TXT record volume? \u2192 DNS exfiltration (\u00a73)", "\u2502   \u251c\u2500\u2500 Extract all queries: tshark -Y dns -T fields -e dns.qry.name (\u00a76)", "\u2502   \u2514\u2500\u2500 DNS rebinding? \u2192 check for alternating A record responses", "\u251c\u2500\u2500 FTP / Telnet / SMTP?", "\u2502   \u251c\u2500\u2500 Extract credentials (plaintext) (\u00a73)", "\u2502   \u251c\u2500\u2500 Reconstruct file transfers (follow data stream) (\u00a73)", "\u2502   \u2514\u2500\u2500 Email content and attachments (base64 decode) (\u00a73)", "\u251c\u2500\u2500 USB traffic?", "\u2502   \u251c\u2500\u2500 Keyboard HID \u2192 decode keystrokes (\u00a73)", "\u2502   \u251c\u2500\u2500 Storage \u2192 extract transferred files", "\u2502   \u2514\u2500\u2500 Check transfer_type and data_len fields", "\u251c\u2500\u2500 WiFi traffic?", "\u2502   \u251c\u2500\u2500 WPA handshake \u2192 crack with hashcat (\u00a73)", "\u2502   \u251c\u2500\u2500 Deauth frames \u2192 detect attack (\u00a73)", "\u2502   \u2514\u2500\u2500 Probe requests \u2192 device fingerprinting", "\u251c\u2500\u2500 ICMP traffic?", "\u2502   \u251c\u2500\u2500 Large/variable payloads \u2192 data exfiltration (\u00a73)", "\u2502   \u251c\u2500\u2500 Regular pattern \u2192 ICMP tunnel (\u00a73)", "\u2502   \u2514\u2500\u2500 Extract payloads: tshark -Y icmp -T fields -e data.data", "\u251c\u2500\u2500 Suspicious patterns?", "\u2502   \u251c\u2500\u2500 Regular beacon interval \u2192 C2 communication (\u00a74)", "\u2502   \u251c\u2500\u2500 Unusual port/protocol combos \u2192 covert channel (\u00a74)", "\u2502   \u251c\u2500\u2500 High volume to single external IP \u2192 data exfil (\u00a74)", "\u2502   \u2514\u2500\u2500 Encrypted traffic without SNI \u2192 suspicious tunnel", "\u2514\u2500\u2500 Need automated extraction?", "\u251c\u2500\u2500 NetworkMiner for files/creds/images (\u00a75)", "\u251c\u2500\u2500 tshark --export-objects for HTTP/SMB files (\u00a76)", "\u2514\u2500\u2500 binwalk/foremost on exported streams (\u00a74)"],
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