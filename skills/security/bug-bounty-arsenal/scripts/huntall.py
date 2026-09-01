#!/usr/bin/env python3
"""huntall.py — full pipeline orchestrator (v2.5.0).

Runs the complete hunt pipeline in one command:
  recon -> (har2scan) -> hunter -> nuclei -> ffuf

Usage:
  python3 huntall.py target.com
  python3 huntall.py target.com --full --nuclei --ffuf --har capture.har
  python3 huntall.py target.com --skip-recon --slow
"""
import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))

def run(label, cmd):
    print(f"\n{'='*60}\n[{label}] {' '.join(cmd)}\n{'='*60}")
    r = subprocess.run(cmd)
    print(f"[{label}] exit={r.returncode}")
    return r.returncode

def main():
    ap = argparse.ArgumentParser(description="Full hunt pipeline")
    ap.add_argument("target")
    ap.add_argument("--full", action="store_true", help="run every stage")
    ap.add_argument("--nuclei", action="store_true")
    ap.add_argument("--ffuf", action="store_true")
    ap.add_argument("--har", help="HAR file to extract endpoints from")
    ap.add_argument("--slow", action="store_true", help="hunter --slow")
    ap.add_argument("--skip-recon", action="store_true")
    ap.add_argument("--outdir", default=f"hunt_{datetime.now():%Y%m%d_%H%M%S}")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    print(f"[*] huntall v2.5.0 — target: {args.target}")
    print(f"[*] artifacts -> {args.outdir}/")

    stages = []

    # 1. recon
    if not args.skip_recon:
        rc = run("recon", [sys.executable, os.path.join(HERE, "recon.py"),
                           args.target, "--out", os.path.join(args.outdir, "recon.json")])
        stages.append(("recon", rc))

    # 2. har endpoints
    endpoints_file = None
    if args.har and os.path.isfile(args.har):
        endpoints_file = os.path.join(args.outdir, "endpoints.txt")
        rc = run("har2scan", [sys.executable, os.path.join(HERE, "har2scan.py"),
                              args.har, "--out", endpoints_file])
        stages.append(("har2scan", rc))
    elif args.har:
        print(f"[!] HAR file not found: {args.har} — skipping")

    # 3. hunter
    hcmd = [sys.executable, os.path.join(HERE, "hunter.py"), args.target,
            "--json", os.path.join(args.outdir, "findings.json")]
    if args.slow or args.full:
        hcmd.append("--slow")
    if endpoints_file:
        hcmd += ["--endpoints", endpoints_file]
    rc = run("hunter", hcmd)
    stages.append(("hunter", rc))

    # 4. nuclei
    if args.nuclei or args.full:
        if shutil.which("nuclei"):
            rc = run("nuclei", [sys.executable, os.path.join(HERE, "scanner-nuclei.py"),
                                args.target, "--tags", "cve,xss,sqli,exposure",
                                "--out", os.path.join(args.outdir, "nuclei.json")])
            stages.append(("nuclei", rc))
        else:
            print("[!] nuclei not installed — skipping (install: install-repos.py --tools)")

    # 5. ffuf
    if args.ffuf or args.full:
        if shutil.which("ffuf"):
            rc = run("ffuf", [sys.executable, os.path.join(HERE, "ffuf-wrapper.py"),
                              args.target, "--filter", "404,403",
                              "--out", os.path.join(args.outdir, "ffuf.json")])
            stages.append(("ffuf", rc))
        else:
            print("[!] ffuf not installed — skipping (install: install-repos.py --tools)")

    # summary
    print(f"\n{'='*60}\nPIPELINE SUMMARY\n{'='*60}")
    for name, rc in stages:
        print(f"  {name:<12} exit={rc}")
    print(f"\n[done] artifacts in {args.outdir}/")
    print("[hint] review findings.json, log submissions: python3 tracker.py add ...")

if __name__ == "__main__":
    main()
