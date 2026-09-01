#!/usr/bin/env python3
"""Per-key Freestyle status triage.

Usage: python3 freestyle-key-status.py <accounts.json>
accounts.json = [{"label": "...", "key": "..."}]  (same shape as
/root/freestyle-dashboard/accounts.json)

For each key: list its VMs via raw REST (source of truth — the npm SDK can
resolve to the wrong team) and probe write access with a POST start.
Classifies each team into: WRITE_OK / FRAUD_BLOCKED(403) / QUOTA_BURN(429).
"""
import json, sys, urllib.request, urllib.error


def api(key, path, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"https://beta-api.freestyle.sh/v5{path}",
        data=data,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]


def classify(err):
    e = str(err).lower()
    if "blocked" in e or "fraud" in e or "payment" in e:
        return "FRAUD_BLOCKED(403) — read-only, support-only fix"
    if "limit_exceeded" in e or "allowance" in e:
        return "QUOTA_BURN(429) — allowance used, usable after reset/upgrade"
    return f"OTHER: {str(err)[:120]}"


def main(path):
    with open(path) as f:
        accounts = json.load(f)
    for a in accounts:
        key, label = a["key"], a["label"]
        print(f"=== {label} ({key[:6]}...) ===")
        code, data = api(key, "/vms")
        if code != 200:
            print(f"  LIST FAIL HTTP {code}: {data}")
            continue
        vms = data.get("vms", []) if isinstance(data, dict) else data
        if not vms:
            print("  NO VMs visible")
        for v in vms:
            vid = v["id"]
            # write-probe: start with idleTimeout bump. 200=OK, 403=fraud, 429=quota.
            c2, d2 = api(key, f"/vms/{vid}/start", "POST", {"idleTimeoutSeconds": 86400})
            cls = "WRITE_OK(200)" if c2 == 200 else classify(d2)
            h = int(v.get("totalRunSeconds") or 0)
            print(f"  VM {vid[:20]} slug={v.get('slug')} state={v.get('state')} "
                  f"uptime~{h // 3600}h  -> {cls}")
        print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__file__ + " <accounts.json>")
    main(sys.argv[1])
