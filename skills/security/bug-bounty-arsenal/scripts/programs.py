#!/usr/bin/env python3
"""programs.py — bug bounty program discovery (v2.5.0).

Lists well-known program platforms + a bundled offline index of popular
programs. Attempts online discovery via public program lists when possible.

Usage:
  python3 programs.py
  python3 programs.py --search crypto
  python3 programs.py --online   # fetch program lists (network)
"""
import argparse
import json
import sys
import urllib.request

UA = "Mozilla/5.0 (BugBountyArsenal/2.5)"

PLATFORMS = [
    ("HackerOne", "https://hackerone.com/directory/programs", "largest platform"),
    ("Bugcrowd", "https://bugcrowd.com/programs", "major platform, VDPs too"),
    ("Intigriti", "https://app.intigriti.com/programs", "EU-focused"),
    ("YesWeHack", "https://yeswehack.com/programs", "EU platform"),
    ("Open Bug Bounty", "https://www.openbugbounty.org", "coordinated disclosure"),
    ("Immunefi", "https://immunefi.com/explore/", "Web3/DeFi — biggest crypto payouts"),
    ("Code4rena", "https://code4rena.com", "competitive smart contract audits"),
    ("Sherlock", "https://audits.sherlock.xyz", "audit contests"),
    ("HackenProof", "https://hackenproof.com", "web3 + web2"),
]

# Bundled offline index of well-known programs (name, platform, scope hint)
PROGRAMS = [
    ("Google VRP", "self-hosted", "google.com properties"),
    ("Microsoft MSRC", "self-hosted", "windows, azure, office"),
    ("Meta", "self-hosted", "facebook, instagram, whatsapp"),
    ("GitHub", "HackerOne", "github.com, gh cli, actions"),
    ("GitLab", "HackerOne", "gitlab.com, self-managed"),
    ("Shopify", "HackerOne", "shopify.com, storefronts"),
    ("PayPal", "HackerOne", "paypal, venmo"),
    ("Stripe", "HackerOne", "payments api"),
    ("Coinbase", "HackerOne", "exchange, wallet"),
    ("Binance", "self-hosted", "binance.com, smart chain"),
    ("Ethereum Foundation", "Immunefi", "protocol, clients"),
    ("Uniswap", "Immunefi", "protocol contracts"),
    ("Aave", "Immunefi", "lending protocol"),
    ("OpenSea", "Immunefi", "marketplace"),
    ("Polygon", "Immunefi", "L2, bridge"),
    ("Internet Bug Bounty", "HackerOne", "open source ecosystem"),
]

def main():
    ap = argparse.ArgumentParser(description="Bug bounty program discovery")
    ap.add_argument("--search", help="filter programs by keyword")
    ap.add_argument("--online", action="store_true", help="fetch online program list")
    args = ap.parse_args()

    print("=== platforms ===")
    for name, url, desc in PLATFORMS:
        print(f"  {name:<16} {url}\n{'':<18}{desc}")

    print("\n=== known programs ===")
    rows = PROGRAMS
    if args.search:
        kw = args.search.lower()
        rows = [p for p in PROGRAMS if kw in " ".join(p).lower()]
    for name, plat, scope in rows:
        print(f"  {name:<22} [{plat}] {scope}")
    if not rows:
        print("  (no match)")

    if args.online:
        print("\n[*] attempting online discovery (hackerone directory API)...")
        try:
            req = urllib.request.Request(
                "https://hackerone.com/programs/search?page=1&sort=published_at:descending&limit=20",
                headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read().decode())
            items = data.get("results", [])
            print(f"[+] fetched {len(items)} programs:")
            for it in items[:20]:
                fields = it.get("fields", {})
                print(f"    {fields.get('name', '?')} — {fields.get('offers_bounties', False) and 'bounty' or 'VDP'}")
        except Exception as e:
            print(f"[!] online fetch failed: {e}")
            print("    browse manually: https://hackerone.com/directory/programs")

    print("\n[hint] Web3: Immunefi has the biggest payouts ($10k-$10M+).")
    print("[hint] Always read program scope/policy before scanning.")

if __name__ == "__main__":
    main()
