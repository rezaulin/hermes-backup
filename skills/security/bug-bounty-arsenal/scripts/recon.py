#!/usr/bin/env python3
"""recon.py — Bug Bounty Arsenal reconnaissance engine (v2.5.0).

Passive + active recon on a target domain:
  1. crt.sh certificate-transparency subdomain enumeration
  2. DNS A-record resolution (stdlib socket)
  3. TCP port scan (top common ports)
  4. HTTP(S) alive probe + tech fingerprinting

Usage:
  python3 recon.py target.com
  python3 recon.py target.com --skip-crtsh --ports top100
  python3 recon.py target.com --out report.json
"""
import argparse
import json
import socket
import ssl
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = "Mozilla/5.0 (BugBountyArsenal/2.5)"

TOP_PORTS = {
    21: "ftp", 22: "ssh", 25: "smtp", 53: "dns", 80: "http",
    110: "pop3", 143: "imap", 443: "https", 465: "smtps", 587: "smtp-sub",
    993: "imaps", 995: "pop3s", 3306: "mysql", 5432: "postgres",
    6379: "redis", 8080: "http-alt", 8443: "https-alt", 27017: "mongodb",
}

def crtsh_subdomains(domain, timeout=30):
    """Query crt.sh CT logs for subdomains. Returns set of names."""
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode())
    except Exception as e:
        print(f"[!] crt.sh query failed: {e}")
        return set()
    subs = set()
    for entry in data:
        for name in str(entry.get("name_value", "")).split("\n"):
            name = name.strip().lower().lstrip("*.")
            if name.endswith(domain) and name != domain:
                subs.add(name)
    return subs

def resolve(name):
    try:
        return socket.gethostbyname(name)
    except Exception:
        return None

def port_scan(host, ports, timeout=1.5):
    open_ports = []
    def check(p):
        try:
            with socket.create_connection((host, p), timeout=timeout):
                return p
        except Exception:
            return None
    with ThreadPoolExecutor(max_workers=24) as ex:
        futs = {ex.submit(check, p): p for p in ports}
        for f in as_completed(futs):
            p = f.result()
            if p:
                open_ports.append(p)
    return sorted(open_ports)

def http_probe(host, scheme="https"):
    """Probe HTTP(S) and return basic fingerprint info."""
    url = f"{scheme}://{host}/"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    ctx = None
    if scheme == "https":
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    info = {"url": url, "status": None, "server": None, "tls": None}
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
            info["status"] = r.status
            info["server"] = r.headers.get("Server", "")
            body = r.read(20480).decode(errors="ignore")
            tech = []
            for sig, name in [
                ("wp-content", "WordPress"), ("__NEXT_DATA__", "Next.js"),
                ("react", "React"), ("vue", "Vue"), ("angular", "Angular"),
                ("Django", "Django"), ("laravel", "Laravel"),
                ("X-Powered-By", "X-Powered-By header"),
            ]:
                if sig.lower() in body.lower() or sig.lower() in (r.headers.get("X-Powered-By", "") or "").lower():
                    tech.append(name)
            info["tech"] = tech
            if scheme == "https":
                info["tls"] = "verified-disabled (probe mode)"
    except Exception as e:
        info["error"] = str(e)
    return info

def main():
    ap = argparse.ArgumentParser(description="Recon engine")
    ap.add_argument("domain")
    ap.add_argument("--skip-crtsh", action="store_true", help="skip certificate transparency lookup")
    ap.add_argument("--ports", default="top", choices=["top", "top100", "none"], help="port scan scope")
    ap.add_argument("--out", help="write JSON report to file")
    args = ap.parse_args()

    domain = args.domain.lower().rstrip(".")
    print(f"=== recon: {domain} ===")

    result = {"domain": domain, "subdomains": [], "resolved": {}, "ports": {}, "http": []}

    # 1. subdomains
    subs = set() if args.skip_crtsh else crtsh_subdomains(domain)
    subs.add(domain)
    result["subdomains"] = sorted(subs)
    print(f"[+] subdomains found: {len(subs)}")
    for s in sorted(subs)[:40]:
        print(f"    {s}")
    if len(subs) > 40:
        print(f"    ... and {len(subs)-40} more")

    # 2. resolve
    print("[*] resolving A records ...")
    for s in sorted(subs):
        ip = resolve(s)
        if ip:
            result["resolved"][s] = ip
    print(f"[+] resolved {len(result['resolved'])}/{len(subs)}")

    # 3. port scan (main domain only by default to stay fast)
    ports = list(TOP_PORTS) if args.ports != "none" else []
    if args.ports == "top":
        ports = [80, 443, 8080, 8443, 22, 3306, 5432]
    if ports:
        ip = result["resolved"].get(domain) or domain
        print(f"[*] port-scanning {ip} ({len(ports)} ports) ...")
        openp = port_scan(ip, ports)
        result["ports"][domain] = [{"port": p, "service": TOP_PORTS.get(p, "?")} for p in openp]
        oplist = [f"{p}({TOP_PORTS.get(p, '?')})" for p in openp]
        print(f"[+] open: {oplist}")

    # 4. http probes (domain + up to 5 subs)
    probe_hosts = [domain] + sorted(s for s in subs if s != domain)[:5]
    print("[*] probing HTTP(S) ...")
    for h in probe_hosts:
        for scheme in ("https", "http"):
            info = http_probe(h, scheme)
            result["http"].append(info)
            line = f"    {info['url']}: "
            line += f"status={info['status']}" if info["status"] else f"err={info.get('error','')[:50]}"
            if info.get("server"):
                line += f" server={info['server']}"
            if info.get("tech"):
                line += f" tech={info['tech']}"
            print(line)

    if args.out:
        with open(args.out, "w") as f:
            json.dump(result, f, indent=2)
        print(f"[+] report -> {args.out}")

    print("=== done ===")

if __name__ == "__main__":
    main()
