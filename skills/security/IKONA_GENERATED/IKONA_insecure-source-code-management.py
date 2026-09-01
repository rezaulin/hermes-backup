#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/insecure-source-code-management

Skill: SKILL: Insecure Source Code Management
Desc : >-

Run:  python hack-skills-insecure-source-code-management.py --help
      python hack-skills-insecure-source-code-management.py --list
      python hack-skills-insecure-source-code-management.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/insecure-source-code-management'
TITLE = 'SKILL: Insecure Source Code Management'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: insecure-source-code-management", "description: >-", "Source control and artifact exposure (.git, .svn, .hg, backups, .env). Use when recon finds VCS paths, 403 on hidden dirs, or backup/config leaks during authorized testing."],
    'skill-insecure-source-code-management': [],
    '0-quick-start': ["High-value paths to probe first (GET or HEAD, respect rate limits):", "```http", "/.git/HEAD", "/.git/config", "/.svn/entries", "/.svn/wc.db", "/.hg/requires", "/.bzr/README", "/.DS_Store", "/.env", "**Routing note**: quickly probe these paths first; for full recon workflow, load methodology from `recon-for-sec` and `recon-and-methodology` before deeper testing."],
    '1-git-exposure': [],
    'detection': ["- **`/.git/HEAD`** \u2014 valid repo often returns plain text like:", "```text", "ref: refs/heads/main", "- **`/.git/config`** \u2014 may expose `remote.origin.url`, user identity, or embedded credentials.", "- **`/.git/index`**, **`/.git/objects/`** \u2014 partial object store access enables reconstruction with the right tools."],
    '403-vs-404': ["- **`404`** \u2014 path likely absent or fully blocked at the edge.", "- **`403` on `/.git/`** \u2014 directory may **exist** but listing is denied; still try direct file URLs:", "```http", "/.git/HEAD", "/.git/config", "/.git/logs/HEAD", "/.git/refs/heads/main", "A **403 on the directory** plus **200 on `HEAD`** strongly indicates exposure."],
    'recovery-tools-open-source': ["- **`arthaud/git-dumper`** \u2014 dumps reachable `.git` tree when individual files are fetchable.", "- **`internetwache/GitTools`** \u2014 Dumper, Extractor, Finder modules for partial/corrupt dumps.", "- **`WangYihang/GitHacker`** \u2014 alternative recovery when standard dumpers miss edge cases."],
    'key-files-to-prioritize': [],
    '2-svn-exposure': [],
    'detection': ["- **SVN before 1.7**: **`/.svn/entries`** \u2014 XML or text metadata listing paths and revisions.", "- **SVN \u2265 1.7**: **`/.svn/wc.db`** \u2014 SQLite working copy database (`PRAGMA table_info` after download).", "Example probe:", "```http", "GET /.svn/entries HTTP/1.1", "GET /.svn/wc.db HTTP/1.1"],
    'recovery': ["- **`anantshri/svn-extractor`** \u2014 automated extraction from exposed `.svn`.", "- **Manual**: download `wc.db`, query with `sqlite3` for file paths and checksums, then request **`/.svn/pristine/`** blobs if exposed."],
    '3-mercurial-exposure': [],
    'detection': ["- **`/.hg/requires`** \u2014 small text file listing repository features; confirms Mercurial metadata.", "```http", "GET /.hg/requires HTTP/1.1", "GET /.hg/store/ HTTP/1.1"],
    'recovery': ["- **`sahildhar/mercurial_source_code_dumper`** \u2014 dumps repository when store paths are reachable."],
    '4-other-leaks': [],
    'bazaar-bzr': ["- Probe **`/.bzr/README`** and **`/.bzr/branch-format`** for Bazaar metadata."],
    'macos-ds-store': ["- **`/.DS_Store`** can encode directory and filename listings.", "- Tools: **`gehaxelt/ds-store`**, **`lijiejie/ds_store_exp`** \u2014 parse `.DS_Store` offline."],
    'backup-and-config-artifacts': ["Probe (adjust for app root and naming conventions):", "```text", "/.env", "/backup.zip", "/backup.tar.gz", "/wwwroot.rar", "/backup.sql", "/config.php.bak", "/.config.php.swp"],
    'web-server-misconfiguration-signal-example-nginx': ["- **`location /.git { deny all; }`** \u2014 may return **403** for `/.git/` while still allowing or denying specific subpaths depending on rules.", "- **403 on a protected location** can **confirm the route exists**; always distinguish from **404** on non-existent paths."],
    '5-decision-tree': ["1. **Probe `/.git/HEAD`** \u2192 `ref: refs/heads/` pattern? \u2192 run **git-dumper / GitTools / GitHacker**; review `config` and `logs/HEAD` for secrets.", "2. **Else probe `/.svn/wc.db` or `entries`** \u2192 success? \u2192 **svn-extractor** or manual `wc.db` + pristine recovery.", "3. **Else probe `/.hg/requires`** \u2192 success? \u2192 **mercurial dumper**.", "4. **Else probe `/.bzr/README`** \u2192 Bazaar tooling or manual path walk.", "5. **Parallel**: fetch **`/.DS_Store`**, **`/.env`**, common **backup extensions** on app root and parent paths.", "6. **Interpret status codes**: **403 on directory** + **200 on specific files** \u2192 treat as **high priority** for file-by-file extraction."],
    '6-related-routing': ["- From **[recon-for-sec](../recon-for-sec/SKILL.md)** \u2014 scope-safe discovery, crawling, and fingerprinting before deep VCS tests.", "- From **[recon-and-methodology](../recon-and-methodology/SKILL.md)** \u2014 structured methodology and evidence handling.", "**Note**: coordinate with recon skills\u2014set scope and request rate first, then run targeted VCS/backup validation."],
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