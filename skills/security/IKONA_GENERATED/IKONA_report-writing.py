#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/report-writing

Skill: REPORT WRITING
Desc : Bug bounty report writing for H1/Bugcrowd/Intigriti/Immunefi — report templates, human tone guidelines, impact-first writing, CVSS 3.1 scoring, title formula, impact statement formula, severity decision guide, downgrade counters, pre-submit checklist. Validation gates and the submittability/always-rejected decision are owned by triage-validation; this skill owns the written report itself (templates, tone, formulas). Use after validating a finding and before submitting. Never use "could potentially" — prove it or don't report.

Run:  python claude-bughunter-report-writing.py --help
      python claude-bughunter-report-writing.py --list
      python claude-bughunter-report-writing.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/report-writing'
TITLE = 'REPORT WRITING'
DESCRIPTION = 'Bug bounty report writing for H1/Bugcrowd/Intigriti/Immunefi — report templates, human tone guidelines, impact-first writing, CVSS 3.1 scoring, title formula, impact statement formula, severity decision guide, downgrade counters, pre-submit checklist. Validation gates and the submittability/always-rejected decision are owned by triage-validation; this skill owns the written report itself (templates, tone, formulas). Use after validating a finding and before submitting. Never use "could potentially" — prove it or don\'t report.'

PAYLOADS = {
    'main': ["name: report-writing", "description: Bug bounty report writing for H1/Bugcrowd/Intigriti/Immunefi \u2014 report templates, human tone guidelines, impact-first writing, CVSS 3.1 scoring, title formula, impact statement formula, severity decision guide, downgrade counters, pre-submit checklist. Validation gates and the submittability/always-rejected decision are owned by triage-validation; this skill owns the written report itself (templates, tone, formulas). Use after validating a finding and before submitting. Never use \"could potentially\" \u2014 prove it or don't report."],
    'report-writing': ["Impact-first. Human tone. No theoretical language. Triagers are people."],
    'the-most-important-rule': ["BAD:  \"This vulnerability could potentially allow an attacker to access user data.\"", "GOOD: \"An attacker can access any user's order history by changing the user_id", "parameter to the target user's ID. I confirmed this using two test accounts:", "attacker@test.com (ID 123) successfully retrieved victim@test.com (ID 456)", "orders, including their shipping address and payment method last 4 digits.\""],
    'title-formula': ["[Bug Class] in [Exact Endpoint/Feature] allows [attacker role] to [impact] [victim scope]", "**Good titles (specific, impact-first):**", "IDOR in /api/v2/invoices/{id} allows authenticated user to read any customer's invoice data", "Missing auth on POST /api/admin/users allows unauthenticated attacker to create admin accounts", "Stored XSS in profile bio field executes in admin panel \u2014 allows privilege escalation", "SSRF via image import URL parameter reaches AWS EC2 metadata service", "Race condition in coupon redemption allows same code to be used unlimited times", "**Bad titles (vague, useless to triager):**", "IDOR vulnerability found", "Broken access control", "XSS in user input", "Security issue in API", "Unauthorized access to user data"],
    'hackerone-report-template': ["```markdown"],
    'summary': ["[One paragraph: what the bug is, where it is, what an attacker can do. Be specific.", "Include: endpoint, method, parameter, data exposed, required access level.]", "Example: \"The `/api/users/{user_id}/orders` endpoint does not verify that the", "authenticated user owns the requested user_id. An attacker can enumerate any", "user's order history, including PII (email, address, phone) and purchase history,", "by incrementing the user_id parameter. No privileges beyond a standard free", "account are required.\""],
    'vulnerability-details': ["**Vulnerability Type:** IDOR / Broken Object Level Authorization", "**CVSS 3.1 Score:** 6.5 (Medium) \u2014 AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N", "**Affected Endpoint:** GET /api/users/{user_id}/orders"],
    'steps-to-reproduce': ["**Environment:**", "- Attacker account: attacker@test.com, user_id = 123", "- Victim account: victim@test.com, user_id = 456", "- Target: https://target.com", "**Steps:**", "1. Log in as attacker@test.com, obtain Bearer token", "2. Send the following request:", "GET /api/users/456/orders HTTP/1.1", "Host: target.com", "Authorization: Bearer ATTACKER_TOKEN_HERE", "3. Observe response:", "```json", "\"orders\": [", "{\"id\": 789, \"items\": [...], \"email\": \"victim@test.com\", \"address\": \"123 Main St...\"}", "The response contains victim's full order history and PII despite being requested", "by a different user."],
    'impact': ["An authenticated attacker can enumerate all user orders by iterating user_id values.", "This exposes: full name, email, shipping address, purchase history, and payment", "method (last 4). With ~100K users, this represents a mass PII breach affecting", "all registered users. Exploitation requires only a free account and takes minutes", "with a simple loop."],
    'recommended-fix': ["Add server-side ownership verification:", "```python", "if order.user_id != current_user.id:", "raise Forbidden()"],
    'supporting-materials': ["[Screenshot showing attacker's session returning victim's order data]", "[Video walkthrough if available]"],
    'bugcrowd-report-template': ["```markdown"],
    'idor-user-order-history-accessible-without-authorization-via-api-users-id-orders': ["**VRT Category:** Broken Access Control > IDOR > P2"],
    'description': ["[Same impact-first paragraph as HackerOne summary]"],
    'steps-to-reproduce': ["[Same structured steps \u2014 exact HTTP requests, exact responses]"],
    'proof-of-concept': ["[Screenshot/video showing the actual impact]"],
    'expected-vs-actual-behavior': ["**Expected:** 403 Forbidden when user_id does not match authenticated user", "**Actual:** 200 OK with victim's full order data"],
    'severity-justification': ["P2 (High) \u2014 Direct read access to other users' PII. Affects all user accounts.", "No user interaction required. Exploitable by any authenticated user.", "Automated enumeration could exfil all [N] user records in minutes."],
    'remediation': ["Add ownership verification: `if order.user_id != current_user.id: raise 403`"],
    'intigriti-report-template': ["```markdown"],
    'bug-class-exact-impact-in-endpoint-feature': [],
    'description': ["[Impact-first paragraph. Start with what an attacker can do, not with how you found it.", "Include: endpoint, method, parameter, data exposed, required privileges.]"],
    'steps-to-reproduce': ["**Environment:**", "- Attacker: email=attacker@test.com (standard account, no special role)", "- Victim: email=victim@test.com", "- Tested: [date]", "**Reproduction steps:**", "1. [Login as attacker / visit URL / send request]", "2. Send the following HTTP request:", "\\```http", "METHOD /endpoint HTTP/1.1", "Host: target.com", "Authorization: Bearer ATTACKER_TOKEN", "Content-Type: application/json", "{\"param\": \"victim_id_here\"}", "3. Observe response contains victim's private data:", "\\```json", "{\"email\": \"victim@test.com\", \"address\": \"123 Main St\", ...}"],
    'impact': ["[Specific, quantified impact. What data, how many users, what can attacker do.]", "CVSS 3.1 Score: X.X ([Severity]) \u2014 AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N"],
    'remediation': ["[1-3 sentence concrete fix. Include code if helpful.]"],
    'attachments': ["[Screenshot or Loom video showing the impact \u2014 Intigriti triagers prefer video for complex bugs]", "**Intigriti-specific notes:**", "- Title format: `[Bug Class]: [One-line impact]` (no formula required, but keep it specific)", "- Severity is set by you: Critical/High/Medium/Low/Exceptional", "- CVSS 3.1 is standard (CVSS 4.0 also accepted on newer programs)", "- PoC video is valued much more than screenshot alone \u2014 record with Loom", "- Safe harbor: Intigriti enforces it, be comfortable going slightly aggressive with testing"],
    'immunefi-report-template': ["```markdown"],
    'bug-class-protocol-name-severity': [],
    'summary': ["[One paragraph with: root cause, affected function, economic impact, attack cost.", "Include numbers where possible: \"attacker can drain $X in Y transactions.\"]"],
    'vulnerability-details': ["**Contract:** `VulnerableContract.sol`", "**Function:** `claimRedemption()`", "**Bug Class:** Accounting State Desynchronization", "**Severity:** Critical"],
    'root-cause': ["[Exact code snippet showing the vulnerable code with comments]"],
    'proof-of-concept': ["```solidity", "// SPDX-License-Identifier: MIT", "pragma solidity ^0.8.0;", "// Foundry PoC \u2014 run: forge test --match-test test_exploit -vvvv", "contract ExploitTest is Test {", "// ... full working exploit"],
    'impact': ["[Quantified: \"Attacker can drain X% of TVL = $Y at current rates.", "Requires $Z gas. Attack is repeatable.\"]"],
    'recommended-fix': ["[Specific code change with before/after]"],
    'cvss-3-1-quick-scoring': [],
    'formula': ["CVSS = f(AV, AC, PR, UI, S, C, I, A)"],
    'metric-quick-picks': [],
    'typical-scores-by-bug-class': [],
    'severity-decision-guide': [],
    'critical-p1': ["- Full account takeover of any user without interaction", "- Remote code execution", "- SQLi with ability to dump/modify entire DB", "- Auth bypass to admin panel", "- SSRF to cloud metadata \u2192 IAM credentials exfil"],
    'high-p2': ["- Mass PII exposure (email, phone, SSN, payment data)", "- Privilege escalation from user to admin", "- SSRF reaching internal services (data returned)", "- Stored XSS executing for all users of sensitive feature", "- Payment bypass / financial loss without limit"],
    'medium-p3': ["- IDOR on specific user's non-critical data", "- XSS on low-sensitivity page requiring victim interaction", "- CSRF on important but non-critical action", "- Rate limit bypass on OTP (with effort demonstrated)"],
    'low-p4': ["- Information disclosure (non-sensitive, no PII)", "- Clickjacking on sensitive action WITH working PoC", "- CORS on limited data"],
    'severity-self-assessment': ["Each YES raises severity:", "1. Exposes PII / health / financial data of other users?        \u2192 +1 severity", "2. Allows account takeover or privilege escalation?             \u2192 +2 severity", "3. Requires ZERO user interaction from victim?                  \u2192 +1 severity", "4. Affects ALL users (not specific condition)?                  \u2192 +1 severity", "5. Remotely exploitable with no internal network access?        \u2192 baseline for High+"],
    'downgrade-counters': [],
    'the-60-second-pre-submit-checklist': ["[ ] Title follows formula: [Class] in [endpoint] allows [actor] to [impact]", "[ ] First sentence states exact impact in plain English", "[ ] Steps to Reproduce has exact HTTP request (copy-paste ready)", "[ ] Response showing the bug is included (screenshot or JSON body)", "[ ] Two test accounts used \u2014 not just one account testing itself", "[ ] CVSS score calculated and included", "[ ] Recommended fix is 1-2 sentences (not a lecture)", "[ ] No typos in endpoint paths or parameter names", "[ ] Report is < 600 words \u2014 triagers skim long reports", "[ ] Severity claimed matches impact described \u2014 don't overclaim", "[ ] Never used \"could potentially\" or \"may allow\"", "[ ] PoC is reproducible by triager from a fresh state"],
    'cvss-4-0-quick-reference-newer-programs': ["CVSS 4.0 replaced CVSS 3.1 in November 2023. Some newer programs require it."],
    'key-differences-from-cvss-3-1': [],
    'cvss-4-0-score-examples': [],
    'quick-cvss-4-0-calculator': ["Use: https://www.first.org/cvss/calculator/4.0", "Key fields:", "VC/VI/VA = Vulnerable System Confidentiality/Integrity/Availability", "SC/SI/SA = Subsequent System (downstream impact)", "AT = None (no special condition) | Present (race/specific config needed)", "UI = None | Passive (victim visits URL) | Active (victim takes explicit action)", "**Practical rule**: If program uses CVSS 4.0 and you don't know the vector, use the calculator and include the full string starting with `CVSS:4.0/AV:...`. Programs cannot dispute a valid vector string."],
    'human-tone-guidelines': ["**Write to a person, not a system:**", "- Triagers are tired. Get to the impact in sentence 1.", "- Use \"I\" not \"the researcher\" \u2014 you found it, own it", "- Short paragraphs, bullet points for steps", "- Hyperlink relevant docs if needed", "**Escalation language (when payout is being downgraded):**", "\"This vulnerability does not require any special privileges \u2014 only a free account.\"", "\"The exposed data includes [PII type], which is subject to GDPR requirements.\"", "\"An attacker can automate this with a simple loop \u2014 all [N] records in minutes.\"", "\"This is exploitable externally without network access to any internal system.\"", "\"The impact is equivalent to a full data breach of [feature/data type].\"", "**Avoid:**", "- Jargon the triager might not know", "- 5-paragraph explanations of what IDOR is (they know)", "- Theoretical chains (\"could be combined with X to...\")", "- Passive voice (\"it was observed that...\")", "- Qualifying language (\"seems to,\" \"appears to\")"],
    'steps-to-reproduce-format-triager-optimized': ["```markdown", "**Setup:**", "- Account A (attacker): email=attacker@test.com, ID=111", "- Account B (victim): email=victim@test.com, ID=222", "- Both created via normal registration \u2014 no special access", "**Steps:**", "1. Log in as Account A", "2. Send this request (replace `111` with victim ID `222`):", "GET /api/v2/resource/222 HTTP/1.1", "Host: target.com", "Authorization: Bearer ACCOUNT_A_TOKEN", "3. Response contains Account B's private data:", "\\```json", "{\"id\": 222, \"email\": \"victim@test.com\", \"name\": \"Victim User\", \"address\": \"...\"}", "**Expected:** 403 Forbidden", "**Actual:** 200 OK with victim's private data"],
    'related-skills-chains': ["- **`triage-validation`** \u2014 When deciding whether to write a report at all. Workflow primitive: NEVER open this skill before `triage-validation`'s 7-Question Gate passes; a finding that fails the gate should be killed, not written up.", "- **`bugcrowd-reporting`** \u2014 When the target is a Bugcrowd program. Workflow primitive: this skill's body template is the foundation; `bugcrowd-reporting` overlays VRT selection, severity-request paragraph, OOS-clause rebuttals on top.", "- **`evidence-hygiene`** \u2014 When PoC screenshots / HARs are being attached to the report. Workflow primitive: every artifact referenced in the \"Supporting Materials\" / \"Proof of Concept\" section gets routed through `evidence-hygiene` for cookie + PII redaction before attachment.", "- **`redteam-report-template`** \u2014 When the engagement is an external red team (NOT bug bounty). Workflow primitive: confirm engagement mode via `bb-methodology` PART 0; if red-team, swap this skill out for `redteam-report-template` (different audience, different structure: Subject / Observations / Description / Impact / Recommendation / PoC)."],
    'operator-notes-claude-bughunter': [],
    'title-formula-in-practice': ["`<asset> | <bug class> | <impact>` \u2014 three components, no fluff. Triagers read titles in roughly three seconds and use them to order the queue.", "- BAD: \"Interesting finding on /api/users\"", "- BAD: \"IDOR vulnerability in API\"", "- GOOD: \"Authenticated IDOR on /api/users/{uid} -> admin email + role disclosure\"", "- GOOD: \"Unauthenticated SSRF on /preview?url= -> AWS metadata 169.254.169.254 reachable\"", "The bad titles get opened last. The good titles get opened first. Same finding, different queue position, different triage day, different payout speed."],
    'what-triagers-actually-read': ["Their reading sequence on a fresh report:", "1. **Title** (3 seconds)", "2. **First paragraph of impact / summary** (15 seconds)", "3. **The curl command or HTTP request block** (30 seconds)", "4. **Reproduction steps** (only if the first three were convincing)", "5. **Everything else** (only on follow-up review)", "Optimize the top of the report ruthlessly. Save narrative for the middle. Triagers who are convinced by step 3 will rubber-stamp the rest; triagers who aren't convinced by step 3 won't read step 5."],
    'cvss-3-1-vs-bugcrowd-vrt-vs-h1-default-severity': ["These three systems disagree about 30% of the time. The most common gap: a finding that scores CVSS 7.x (High) maps to Bugcrowd P4 (Low) or H1 Medium-default. When the platform default rates lower than CVSS:", "1. **File the severity-request paragraph as the first body section.** Bugcrowd respects this. (See `bugcrowd-reporting` for the canonical template.)", "2. **Anchor the request in CVSS vector string + business impact, not feelings.** \"CVSS 3.1 AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N = 7.5 High because Confidentiality:High applies to cross-tenant data exposure.\"", "3. **Cite the platform's own VRT entry** that matches your finding. Don't argue against the platform; route within it.", "An authorized bug-bounty engagement saw P4-default findings escalated to P3 via the severity-request paragraph. The escalation isn't automatic \u2014 you have to ask, with grounded reasoning, in the first body section."],
    'evidence-rotation': ["Everything in the submission body is logged forever by the platform. Operate accordingly:", "- Use throwaway test accounts created specifically for the engagement.", "- Rotate cookies / tokens after each submission (don't reuse the cookie that's pasted in the report).", "- Never paste production cookies, real user emails, or real PII into the report body \u2014 redact in the PoC step.", "- Screenshots of admin panels: blur the user list, blur the URL bar if it contains tokens.", "Cross-link `evidence-hygiene` for the full capture-and-redact protocol."],
    'templates-by-platform-when-they-differ': ["Picking the wrong template style costs validity. A narrative-heavy Bugcrowd report misses the VRT mapping the triager needs; a structured H1 report reads as terse and gets follow-up questions that delay payout."],
    'the-single-biggest-report-writing-mistake': ["Claiming an attack works \"in theory\" or \"could be chained to [bigger impact]\" without demonstrating it. Triage-validation Q6 (impact beyond technically possible) kills these on the validation side; report-writing has to mirror it on the writing side.", "Two valid paths:", "1. **Show concrete impact end-to-end.** Capture the chain on a test account. Paste the full request/response sequence. Done.", "2. **Downgrade the severity claim to match what you actually demonstrated.** \"IDOR on /api/users/{uid} reading email + role\" is real and reportable; \"IDOR chained to potential admin takeover\" is not until you demonstrate the takeover.", "Pick one. Never split the difference with \"could potentially\" or \"may allow\" \u2014 those phrases are the triager's signal that the report is theoretical, and theoretical reports get N/A.", "- **`bb-methodology`** \u2014 When Phase 5's report-writing step starts. Workflow primitive: Phase 5 calls `/report` which loads this skill for the platform-specific template (H1 / Bugcrowd / Intigriti / Immunefi)."],
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