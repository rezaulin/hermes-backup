#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/file-access-vuln

Skill: File Access Router
Desc : >-

Run:  python hack-skills-file-access-vuln.py --help
      python hack-skills-file-access-vuln.py --list
      python hack-skills-file-access-vuln.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/file-access-vuln'
TITLE = 'File Access Router'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: file-access-vuln", "description: >-", "Entry P1 category router for file access and upload workflows. Use when", "testing download endpoints, file paths, local file inclusion, upload flows,", "preview pipelines, archive extraction, or storage and sharing boundaries."],
    'file-access-router': ["This is the routing entry point for filesystem paths, download endpoints, upload pipelines, and file preview handling."],
    'when-to-use': ["- Parameters, filenames, download endpoints, or import flows influence file paths", "- The target supports upload, preview, transcoding, extraction, sharing, download, or proxied file access", "- You need to decide whether this is path traversal/LFI or an upload-validation/processing-chain issue"],
    'skill-map': ["- [Path Traversal LFI](../path-traversal-lfi/SKILL.md): path traversal, file read, wrapper abuse, include chains", "- [Upload Insecure Files](../upload-insecure-files/SKILL.md): upload validation, storage paths, processing chains, overwrite risk, preview/share boundaries"],
    'recommended-flow': ["1. First identify whether the entry point is a path parameter, download endpoint, or upload workflow", "2. Then locate whether the issue appears in accept, store, process, or serve stages", "3. Small path-chain and upload-bypass samples are merged into the main topic skills; no separate payload entry is needed"],
    'related-categories': ["- [injection-checking](../injection-checking/SKILL.md)", "- [business-logic-vuln](../business-logic-vuln/SKILL.md)"],
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