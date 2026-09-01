#!/usr/bin/env python3
"""ffuf-wrapper.py — FFUF directory/wordlist bruteforce wrapper (v2.5.0).

Wraps ffuf binary. Selects SecLists wordlists from ../repos/SecLists.

Usage:
  python3 ffuf-wrapper.py target.com
  python3 ffuf-wrapper.py target.com --wordlist ../repos/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt
  python3 ffuf-wrapper.py target.com --ext php,html --filter 404
"""
import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WL = os.path.normpath(os.path.join(HERE, "..", "repos", "SecLists",
    "Discovery", "Web-Content", "directory-list-2.3-medium.txt"))

def main():
    ap = argparse.ArgumentParser(description="FFUF wrapper")
    ap.add_argument("target", help="target URL (use FUZZ keyword or /auto-appends)")
    ap.add_argument("--wordlist", default=DEFAULT_WL)
    ap.add_argument("--ext", help="comma extensions e.g. php,html,txt")
    ap.add_argument("--filter", dest="filters", help="comma filter codes e.g. 404,403")
    ap.add_argument("--threads", type=int, default=40)
    ap.add_argument("--out", help="output file")
    args = ap.parse_args()

    ffuf = shutil.which("ffuf")
    if not ffuf:
        print("[!] ffuf not installed.")
        print("    install: go install github.com/ffuf/ffuf/v2@latest")
        print("    or binary: https://github.com/ffuf/ffuf/releases")
        sys.exit(1)

    if not os.path.isfile(args.wordlist):
        print(f"[!] wordlist not found: {args.wordlist}")
        print("    get SecLists: python3 install-repos.py --payloads")
        sys.exit(1)

    url = args.target.rstrip("/")
    if "FUZZ" not in url:
        url += "/FUZZ"

    cmd = [ffuf, "-u", url, "-w", args.wordlist, "-t", str(args.threads)]
    if args.ext:
        cmd += ["-e", args.ext]
    if args.filters:
        cmd += ["-fc", args.filters]
    if args.out:
        cmd += ["-o", args.out, "-of", "json"]

    print(f"[*] running: {' '.join(cmd)}")
    r = subprocess.run(cmd)
    print(f"[done] exit={r.returncode}")

if __name__ == "__main__":
    main()
