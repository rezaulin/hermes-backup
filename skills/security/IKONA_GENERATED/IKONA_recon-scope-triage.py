#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/recon-scope-triage

Skill: the "finding"
Desc : Triage ASM/recon output for ownership before testing — separate the target's real assets from namespace-collision noise. Automated recon keyword-matches on the brand name, so for any target whose name is a common/dictionary word, the output is dominated by assets belonging to UNRELATED same-named companies (repos, cloud buckets, mobile apps, breach corpora, typosquats). Built from an authorized engagement where an ASM report's "Criticals" were overwhelmingly false positives and the combo/repos/mobile/bucket lists were polluted with unrelated same-named orgs. Use at the START of any engagement, immediately on receiving any ASM/recon/OSINT dataset, BEFORE testing anything.

Run:  python claude-bughunter-recon-scope-triage.py --help
      python claude-bughunter-recon-scope-triage.py --list
      python claude-bughunter-recon-scope-triage.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/recon-scope-triage'
TITLE = 'the "finding"'
DESCRIPTION = 'Triage ASM/recon output for ownership before testing — separate the target\'s real assets from namespace-collision noise. Automated recon keyword-matches on the brand name, so for any target whose name is a common/dictionary word, the output is dominated by assets belonging to UNRELATED same-named companies (repos, cloud buckets, mobile apps, breach corpora, typosquats). Built from an authorized engagement where an ASM report\'s "Criticals" were overwhelmingly false positives and the combo/repos/mobile/bucket lists were polluted with unrelated same-named orgs. Use at the START of any engagement, immediately on receiving any ASM/recon/OSINT dataset, BEFORE testing anything.'

PAYLOADS = {
    'main': ["name: recon-scope-triage", "description: Triage ASM/recon output for ownership before testing \u2014 separate the target's real assets from namespace-collision noise. Automated recon keyword-matches on the brand name, so for any target whose name is a common/dictionary word, the output is dominated by assets belonging to UNRELATED same-named companies (repos, cloud buckets, mobile apps, breach corpora, typosquats). Built from an authorized engagement where an ASM report's \"Criticals\" were overwhelmingly false positives and the combo/repos/mobile/bucket lists were polluted with unrelated same-named orgs. Use at the START of any engagement, immediately on receiving any ASM/recon/OSINT dataset, BEFORE testing anything.", "sources: authorized-engagement", "report_count: 1"],
    'when-to-use-this-skill': ["Trigger when:", "- The target brand is a common/dictionary word or shared term (e.g. `apex`, `summit`, `vertex`, `nova`, `core`, `orbit`, `pulse`, `unity`\u2026)", "- You receive an ASM report, recon export, breach combo, repo list, bucket list, or mobile-app list to act on", "- A \"Critical\" count looks implausibly high (hundreds) for the org's size", "- Any asset's ownership is asserted by the tool but not *proven*", "The two failure modes this skill prevents:", "1. **Wasting the engagement** testing/triaging assets that aren't the target's.", "2. **Attacking an innocent third party** that merely shares the name \u2014 out of scope, and real harm.", "**Rule: ownership is guilty-until-proven. An asset is the target's only when a concrete ownership signal ties it to the target \u2014 never because a scanner's keyword matched.**"],
    'the-collision-sources-where-keyword-matching-lies': [],
    'web-critical-triage-the-soft-404-control': ["Automated `.env` / `.git` / `actuator` / admin-panel \"Criticals\" are overwhelmingly **soft-404s**: SPA/framework catch-alls returning HTTP 200 (or 403) for *every* path. Verify EACH before believing it:", "```bash"],
    'the-finding': ["curl -s -o /tmp/a -w \"%{http_code} %{size_download}\\n\" https://host.target.com/.env"],
    'a-junk-control-on-the-same-host': ["curl -s -o /tmp/b -w \"%{http_code} %{size_download}\\n\" https://host.target.com/zzz-nonsense-$RANDOM"],
    'identical-byte-length-body-false-positive-catch-all-discard': ["cmp -s /tmp/a /tmp/b && echo \"SOFT-404 false positive\" || echo \"differs \u2014 investigate\"", "Real exposures have a content-type + signature that differs from the catch-all (`.git/config` starts `[core]`; `.env` has `KEY=value`; phpinfo has the XHTML-transitional doctype + `PHP Version`). A physical `.php`/`phpinfo.php` that returns a *bigger/different* body than the junk control is the real-vs-soft-404 tell."],
    'the-triage-workflow': ["1. **Confirm the canonical owned-domain set first** (the SOW/program domain + its verified subdomains + the verified Entra/Okta/Google tenant brand name). This is your ownership anchor.", "2. **For each asset class, apply the verify-by column above.** No signal \u2192 quarantine, don't test.", "3. **Re-baseline the severity counts** against only-owned assets. Report the *delta* \u2014 \"N Criticals \u2192 M after ownership + soft-404 triage\" is itself a finding about the ASM program.", "4. **Quarantine collisions explicitly** (a `loot/quarantined_<source>.txt`) so it's auditable that you saw them and chose not to target them.", "5. **Surface the meta-finding:** if the supplied ASM/recon feed is mostly false-positive, that misallocates the owner's remediation budget and buries real risk \u2014 write it up (Medium/Strategic)."],
    'anti-patterns': ["- **Trusting the tool's \"owned\" label.** Tools keyword-match; they don't prove ownership. Verify.", "- **Targeting a same-named third party** because it was \"in the report.\" Out of scope + real harm. A combo line `user@<word>company.com` is a different company's employee.", "- **Reporting soft-404s as exposures.** Always run the junk-path control.", "- **Counting typosquats / missing-headers / brand-collision repos as offensive findings.** They're defensive/hygiene/noise \u2014 they pad the report and erode credibility.", "- **Skipping triage \"to save time.\"** Untriaged, you spend the whole engagement on other people's assets and find nothing real."],
    'why-this-matters-calibration': ["For a target whose brand is a common word, expect the bulk of automated \"owned\" assets to be collisions:", "- **Repos** that are unrelated open-source projects (ad-block lists, scrapers, student projects, a different company's SDK) merely containing the word.", "- **Mobile apps** published by entirely different companies that share the name \u2014 banks, credit unions, dating apps, dispensaries, home-care services are all real-world collision categories. (Good ASM tooling will tell you it accepted *zero* as owned.)", "- **Cloud buckets** in the global namespace holding some unrelated org's content (other-language documents, demo/sample data, another industry's files).", "- **Breach combos** full of emails from sibling-named-but-different companies (`<word>group.com`, `<region><word>.com`).", "On a real engagement against a dictionary-word brand, after clearing this noise the only genuinely-owned high-severity finding was discoverable solely by manual tradecraft (a JS-bundle \u2192 API discovery, see `hunt-spa-api`) \u2014 it was nowhere in the hundreds of scanner \"Criticals.\" Triage-first is what made the engagement productive instead of a goose chase."],
    'related-skills-chains': ["- **`triage-validation`** \u2014 asset-ownership triage (this skill) precedes finding-validity triage (the 7-Question Gate). Ownership first, then validity.", "- **`redteam-mindset`** \u2014 \"aggressive default\" means probe every *owned* live surface; this skill defines which surfaces are owned so persistence isn't wasted on collisions.", "- **`hunt-spa-api`** \u2014 once an API host passes ownership triage, this is how you test it.", "- **`offensive-osint` / `osint-methodology`** \u2014 feed ownership anchors (verified domains, tenant brand, dev accounts) from OSINT into this triage."],
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