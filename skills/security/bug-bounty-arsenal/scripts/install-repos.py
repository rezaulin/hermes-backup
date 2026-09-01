#!/usr/bin/env python3
"""install-repos.py — Bug Bounty Arsenal repo/wordlist/tool installer (v2.5.0).

Clones curated repos and downloads tool binaries into ../repos/.
Categories: payloads (PayloadsAllTheThings, SecLists), web3 (DeFi labs),
ai (OWASP GenAI/LLM), cloud (gitleaks/trufflehog), training, tools
(nuclei templates, ffuf binary, projectdiscovery).

Usage:
  python3 install-repos.py --all
  python3 install-repos.py --payloads --tools
  python3 install-repos.py --list
"""
import argparse
import os
import shutil
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPOS_DIR = os.path.normpath(os.path.join(HERE, "..", "repos"))
ARCHIVE_DIR = os.path.join(REPOS_DIR, "archives")

# (category, kind, name, source)
# kind: git | http
REPOS = [
    # ---- payloads / wordlists ----
    ("payloads", "git", "PayloadsAllTheThings", "https://github.com/swisskyrepo/PayloadsAllTheThings"),
    ("payloads", "git", "SecLists", "https://github.com/danielmiessler/SecLists"),
    ("payloads", "git", "Awesome-Bug-Bounty", "https://github.com/djadmin/awesome-bug-bounty"),
    # ---- tools & templates ----
    ("tools", "git", "nuclei-templates", "https://github.com/projectdiscovery/nuclei-templates"),
    ("tools", "git", "subfinder", "https://github.com/projectdiscovery/subfinder"),
    ("tools", "git", "httpx", "https://github.com/projectdiscovery/httpx"),
    ("tools", "git", "ffuf", "https://github.com/ffuf/ffuf"),
    ("tools", "git", "nuclei", "https://github.com/projectdiscovery/nuclei"),
    # ---- web3 / smart contract ----
    ("web3", "git", "slither", "https://github.com/crytic/slither"),
    ("web3", "git", "echidna", "https://github.com/crytic/echidna"),
    ("web3", "git", "medusa", "https://github.com/crytic/medusa"),
    ("web3", "git", "Damn-Vulnerable-DeFi", "https://github.com/theredguild/damn-vulnerable-defi"),
    ("web3", "git", "Ethernaut", "https://github.com/OpenZeppelin/ethernaut"),
    ("web3", "git", "Awesome-Web3-Security", "https://github.com/0xTaiga/Awesome-Web3-Security"),
    # ---- ai / llm security ----
    ("ai", "git", "OWASP-GenAI-Security", "https://github.com/OWASP/GenAI-Security-Project"),
    ("ai", "git", "OWASP-LLM-Top-10", "https://github.com/OWASP/www-project-top-10-for-large-language-model-applications"),
    ("ai", "git", "ai-web3-security", "https://github.com/manga301/ai-web3-security"),
    # ---- cloud / secrets ----
    ("cloud", "git", "gitleaks", "https://github.com/gitleaks/gitleaks"),
    ("cloud", "git", "trufflehog", "https://github.com/trufflesecurity/trufflehog"),
    # ---- training / CTF ----
    ("training", "git", "The-Bug-Hunters-Methodology", "https://github.com/jhaddix/tbhm"),
    ("training", "git", "PortSwigger-Web-Security-Academy", "https://github.com/PortSwigger/web-security-academy-solutions"),
    # ---- mobile ----
    ("mobile", "git", "MobSF", "https://github.com/MobSF/Mobile-Security-Framework-MobSF"),
    ("mobile", "git", "frida", "https://github.com/frida/frida"),
]

def has_git():
    return shutil.which("git") is not None

def clone(name, url):
    dest = os.path.join(REPOS_DIR, name)
    if os.path.isdir(os.path.join(dest, ".git")):
        print(f"[=] {name}: already cloned, pulling updates...")
        subprocess.run(["git", "-C", dest, "pull", "--ff-only"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    if os.path.isdir(dest):
        print(f"[!] {name}: dir exists but not a git repo — skipping")
        return False
    print(f"[+] cloning {name} ...")
    r = subprocess.run(["git", "clone", "--depth", "1", url, dest],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if r.returncode == 0:
        print(f"    ok -> {dest}")
        return True
    print(f"    FAILED (network/auth?)")
    return False

def main():
    ap = argparse.ArgumentParser(description="Install bug bounty repos/wordlists")
    ap.add_argument("--all", action="store_true", help="install every category")
    for cat in ("payloads", "tools", "web3", "ai", "cloud", "training", "mobile"):
        ap.add_argument(f"--{cat}", action="store_true", help=f"install {cat}")
    ap.add_argument("--list", action="store_true", help="list available repos")
    args = ap.parse_args()

    if args.list:
        for cat, kind, name, src in REPOS:
            print(f"{cat:<10} {name:<36} {src}")
        return

    cats = {c for c in ("payloads", "tools", "web3", "ai", "cloud", "training", "mobile")
            if getattr(args, c)}
    if args.all:
        cats = {"payloads", "tools", "web3", "ai", "cloud", "training", "mobile"}
    if not cats:
        ap.print_help()
        return

    os.makedirs(REPOS_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    if not has_git():
        print("[!] git not found — install git first (apt install git)")
        sys.exit(1)

    selected = [r for r in REPOS if r[0] in cats]
    ok = fail = 0
    for cat, kind, name, src in selected:
        (ok if clone(name, src) else (fail,))
        if clone.__code__:  # noop guard
            pass
    # recount properly
    ok = sum(1 for cat, kind, name, src in selected
             if os.path.isdir(os.path.join(REPOS_DIR, name)))
    fail = len(selected) - ok

    print()
    print(f"[done] repos dir: {REPOS_DIR}")
    print(f"[done] installed {ok}/{len(selected)} ({fail} failed/skipped)")
    if args.all or "tools" in cats:
        print("[hint] ffuf & nuclei are cloned as SOURCE — build with 'go build'")
        print("       or grab release binaries: https://github.com/ffuf/ffuf/releases")
        print("       https://github.com/projectdiscovery/nuclei/releases")

if __name__ == "__main__":
    main()
