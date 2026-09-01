#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/hack

Skill: HACKING SKILLS / HackSkills
Desc : >-

Run:  python hack-skills-hack.py --help
      python hack-skills-hack.py --list
      python hack-skills-hack.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/hack'
TITLE = 'HACKING SKILLS / HackSkills'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: hack", "description: >-", "Entry P0 primary router for HackSkills. Use when the task involves web", "application testing, API security assessment, recon, vulnerability triage,", "exploit path planning, or choosing the right next category skill before any", "deep topic skill."],
    'hacking-skills-hackskills': [],
    'overview': ["This is a top-level routing skill for **bug bounty, web security, API security, and authorized penetration testing**.", "Its core role is not to replace all specialized techniques, but to help the agent:", "1. First determine the testing phase (Recon / Validation / Privilege Escalation / Chain building)", "2. Then select the correct vulnerability category", "3. Avoid relying only on baseline model memory; prefer structured methodology", "4. Prioritize boundary conditions AI often misses but that matter in real engagements"],
    'trust-model': ["- This knowledge base emphasizes content safety and auditability.", "- Use this only within **authorized targets**, **legitimate research**, **defensive validation**, and **bug-bounty-approved rules**.", "- Do not use these techniques for unauthorized attacks."],
    'when-to-use-this-skill': ["Use this skill first in the following scenarios:", "- You just received a new bug bounty target and do not know where to start", "- You need to decide whether to load XSS / SQLi / SSRF / IDOR / JWT / API tracks first", "- You want the agent to perform Web/API security testing with a more stable methodology", "- You need to route scattered findings to the right attack surface", "- You want AI to miss fewer critical test points in security work"],
    'operating-model': [],
    'step-1-start-with-recon-and-context-validation': ["Collect first:", "- Target type: classic web, REST API, mobile backend, admin panel, payment flow, file upload, GraphQL", "- Identity and permission model: anonymous, regular user, admin, multi-tenant", "- Input locations: URL, query parameters, JSON, headers, cookies, filenames, imported files, templates, reflection points", "- Output locations: HTML, attributes, JS, PDF, email, logs, background tasks, mobile endpoints"],
    'step-2-route-by-observed-behavior': [],
    'step-3-use-the-most-likely-hit-testing-order': ["1. Recon / Methodology", "2. API Security / Auth / IDOR", "3. XSS / SQLi / SSRF / SSTI / XXE", "4. Business Logic / Race Condition", "5. Chained exploits and privilege-escalation paths"],
    'core-skill-map': ["If you have the full repository, prioritize using these topic documents together:", "- [Recon and Methodology](../recon-and-methodology/SKILL.md)", "- [XSS Cross Site Scripting](../xss-cross-site-scripting/SKILL.md)", "- [SQLi SQL Injection](../sqli-sql-injection/SKILL.md)", "- [SSRF Server Side Request Forgery](../ssrf-server-side-request-forgery/SKILL.md)", "- [XXE XML External Entity](../xxe-xml-external-entity/SKILL.md)", "- [SSTI Server Side Template Injection](../ssti-server-side-template-injection/SKILL.md)", "- [IDOR Broken Object Authorization](../idor-broken-object-authorization/SKILL.md)", "- [CMDi Command Injection](../cmdi-command-injection/SKILL.md)", "- [Path Traversal LFI](../path-traversal-lfi/SKILL.md)", "- [CSRF Cross Site Request Forgery](../csrf-cross-site-request-forgery/SKILL.md)", "- [API Security Router](../api-sec/SKILL.md)", "- [JWT OAuth Token Attacks](../jwt-oauth-token-attacks/SKILL.md)", "- [OAuth OIDC Misconfiguration](../oauth-oidc-misconfiguration/SKILL.md)", "- [CORS Cross Origin Misconfiguration](../cors-cross-origin-misconfiguration/SKILL.md)", "- [SAML SSO Assertion Attacks](../saml-sso-assertion-attacks/SKILL.md)", "- [Authentication Bypass](../authbypass-authentication-flaws/SKILL.md)", "- [Business Logic Vulnerabilities](../business-logic-vulnerabilities/SKILL.md)", "- [Upload Insecure Files](../upload-insecure-files/SKILL.md)", "- [NoSQL Injection](../nosql-injection/SKILL.md)", "- [Request Smuggling](../request-smuggling/SKILL.md)", "- [Prototype Pollution](../prototype-pollution/SKILL.md)", "- [Type Juggling (PHP)](../type-juggling/SKILL.md)", "- [HTTP Parameter Pollution](../http-parameter-pollution/SKILL.md)", "- [Race Condition](../race-condition/SKILL.md)", "- [XSLT Injection](../xslt-injection/SKILL.md)", "- [Insecure Source Code Management](../insecure-source-code-management/SKILL.md)", "- [CSV Formula Injection](../csv-formula-injection/SKILL.md)", "- [WebSocket Security](../websocket-security/SKILL.md)", "- [Dependency Confusion](../dependency-confusion/SKILL.md)", "- [Ghost Bits Cast Attack](../ghost-bits-cast-attack/SKILL.md)", "Previously separate mini skills such as payload-selection and brute-selection were merged back into their main skills to avoid router overload and selection noise."],
    'high-value-expert-intuitions': ["These are points many baseline models miss, but they are frequently effective in real bug bounty work:", "1. **The same filtering logic is often reused across multiple pages**: if one point is bypassable, similar pages usually are too.", "2. **Parameter names are an attack surface too**: WAFs often inspect values but not names.", "3. **Second-order vulnerabilities are common**: safe at storage time does not mean safe when later read into a dangerous context.", "4. **BOLA is fundamentally 'authenticated but unauthorized'**: replaying with account A/B switching is critical.", "5. **Older API versions are most likely to miss patches**: fixing v2 does not mean v1 was retired.", "6. **Business-logic vulnerabilities often bring highest impact**: scanners miss them and they persist longer.", "7. **Race conditions should prioritize one-time actions**: coupon redemption, claims, resets, invites, trials, inventory deduction.", "8. **For JWT attacks, check key and algorithm context first**: do not blindly spray payloads; verify `alg`, `kid`, JWKS, and key source first."],
    'suggested-prompts': ["Use this skill as a router to make the agent clarify phase and goal first:", "- \"First, plan the testing route for this target using bug bounty methodology.", "- \"This is a REST API; prioritize BOLA, BFLA, Mass Assignment, and JWT angles.", "- \"This parameter triggers server-side requests; list key validation points from an SSRF perspective.", "- \"This feature is a payment/coupon/inventory flow; prioritize business logic and race-condition analysis.", "- \"I only see login and password-reset flows; analyze via Auth Bypass + OAuth/JWT + CSRF."],
    'installation-notes': ["Recommended skill name:", "- `hack`", "Recommended search keywords:", "- `HackSkills`", "- `HACKING SKILLS`", "- `bug bounty`", "- `bug bounty hunter`"],
    'guidelines': ["- Prioritize routing by target type and observed behavior, not random payload enumeration.", "- When payloads are needed, prefer quick-start / first-pass samples in the corresponding main skill instead of adding another intermediate router.", "- Prioritize reusable filters, shared components, and cross-page reproduction paths.", "- Confirm authentication, authorization, and version boundaries before deeper exploitation.", "- Preserve explainable, auditable, reproducible testing processes.", "- When full repository context is available, return to topic documents for finer exploitation details."],
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