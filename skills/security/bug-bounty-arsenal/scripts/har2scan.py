#!/usr/bin/env python3
"""har2scan.py — HAR capture parser -> endpoint list (v2.5.0).

Parses a browser HAR export into unique API endpoints (method, URL, params,
content-type). Optionally feeds the list straight into hunter.py via --scan.

Usage:
  python3 har2scan.py capture.har
  python3 har2scan.py capture.har --out endpoints.txt
  python3 har2scan.py capture.har --scan --slow   # pipe into hunter.py
"""
import argparse
import json
import subprocess
import sys
import urllib.parse

HERE = __file__

def parse_har(path):
    with open(path) as f:
        har = json.load(f)
    entries = har.get("log", {}).get("entries", [])
    endpoints = []
    seen = set()
    for e in entries:
        req = e.get("request", {})
        url = req.get("url", "")
        if not url.startswith("http"):
            continue
        p = urllib.parse.urlparse(url)
        # skip static assets
        if p.path.lower().endswith((".js", ".css", ".png", ".jpg", ".jpeg",
                                     ".gif", ".svg", ".woff", ".woff2", ".ico", ".map")):
            continue
        method = req.get("method", "GET")
        params = {q["name"]: q.get("value", "") for q in req.get("queryString", [])}
        ctype = next((h["value"] for h in req.get("headers", [])
                      if h["name"].lower() == "content-type"), "")
        key = (method, p.netloc, p.path, frozenset(params))
        if key in seen:
            continue
        seen.add(key)
        endpoints.append({
            "method": method, "url": url, "path": p.path,
            "host": p.netloc, "params": params, "content_type": ctype,
            "status": e.get("response", {}).get("status"),
            "size": e.get("response", {}).get("content", {}).get("size", 0),
        })
    return endpoints

def main():
    ap = argparse.ArgumentParser(description="HAR -> endpoint parser")
    ap.add_argument("har")
    ap.add_argument("--out", help="write endpoint URLs (one per line)")
    ap.add_argument("--scan", action="store_true", help="feed into hunter.py")
    ap.add_argument("--slow", action="store_true", help="hunter --slow")
    ap.add_argument("--json", action="store_true", help="full JSON dump")
    args = ap.parse_args()

    try:
        eps = parse_har(args.har)
    except Exception as e:
        print(f"[!] failed to parse HAR: {e}")
        sys.exit(1)

    print(f"[+] {len(eps)} unique endpoints from HAR")
    for e in eps[:30]:
        print(f"    {e['method']:<6} {e['url'][:100]}")
    if len(eps) > 30:
        print(f"    ... +{len(eps)-30} more")

    if args.json:
        print(json.dumps(eps, indent=2))
        return

    if args.out or args.scan:
        outfile = args.out or "/tmp/har_endpoints.txt"
        with open(outfile, "w") as f:
            for e in eps:
                f.write(e["url"] + "\n")
        print(f"[+] endpoints -> {outfile}")

    if args.scan:
        host = eps[0]["host"] if eps else "target"
        cmd = [sys.executable, "-c",
               "import os; os.chdir(os.path.dirname(%r)); "
               "import runpy, sys; sys.argv=['hunter.py','%s','--endpoints',%r%s]; "
               "runpy.run_path('hunter.py', run_name='__main__')"
               % (HERE, f"https://{host}", outfile, ",'--slow'" if args.slow else "")]
        print(f"[*] piping into hunter.py ...")
        subprocess.run(cmd)

if __name__ == "__main__":
    main()
