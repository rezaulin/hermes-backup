#!/usr/bin/env python3
"""scanner-nuclei.py — Nuclei template scanner wrapper (v2.5.0).

Wraps ProjectDiscovery's nuclei binary. If nuclei isn't installed, prints
install instructions. Supports tags/severity filters and JSON export.

Usage:
  python3 scanner-nuclei.py target.com
  python3 scanner-nuclei.py target.com --tags critical,high
  python3 scanner-nuclei.py target.com --severity critical --out results.json
"""
import argparse
import json
import shutil
import subprocess
import sys

def main():
    ap = argparse.ArgumentParser(description="Nuclei wrapper")
    ap.add_argument("target")
    ap.add_argument("--tags", help="comma-separated tags (e.g. cve,xss,sqli)")
    ap.add_argument("--severity", help="comma-separated severities")
    ap.add_argument("--templates", help="custom templates dir/path")
    ap.add_argument("--out", help="JSON output file")
    ap.add_argument("--list", action="store_true", help="list templates only")
    args = ap.parse_args()

    nuclei = shutil.which("nuclei")
    if not nuclei:
        print("[!] nuclei not installed.")
        print("    install: go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest")
        print("    or grab binary: https://github.com/projectdiscovery/nuclei/releases")
        print("    templates: python3 install-repos.py --tools")
        sys.exit(1)

    cmd = [nuclei, "-u", args.target, "-silent"]
    if args.list:
        cmd += ["-tl"]
        subprocess.run(cmd)
        return
    if args.tags:
        cmd += ["-tags", args.tags]
    if args.severity:
        cmd += ["-severity", args.severity]
    if args.templates:
        cmd += ["-t", args.templates]
    if args.out:
        cmd += ["-jsonl", "-o", args.out]

    print(f"[*] running: {' '.join(cmd)}")
    r = subprocess.run(cmd)
    print(f"[done] exit={r.returncode}")
    if args.out:
        print(f"[+] results -> {args.out}")

if __name__ == "__main__":
    main()
