#!/usr/bin/env python3
"""tracker.py — submission & bounty tracking (v2.5.0).

Local JSON store for findings/submissions across bug bounty programs.
Track status (draft/submitted/triaged/rewarded/duplicate/na), bounty amounts,
and get per-program stats.

Usage:
  python3 tracker.py add --target t.com --title "Open redirect" --severity medium
  python3 tracker.py list [--target t.com] [--status submitted]
  python3 tracker.py update <id> --status rewarded --bounty 500
  python3 tracker.py stats
  python3 tracker.py show <id>
"""
import argparse
import json
import os
import sys
import uuid
from datetime import datetime

STORE = os.path.expanduser("~/.bba_tracker.json")
STATUSES = ["draft", "submitted", "triaged", "rewarded", "duplicate", "na", "resolved"]

def load():
    if os.path.exists(STORE):
        with open(STORE) as f:
            return json.load(f)
    return {"findings": []}

def save(db):
    with open(STORE, "w") as f:
        json.dump(db, f, indent=2)

def main():
    ap = argparse.ArgumentParser(description="Bounty submission tracker")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("--target", required=True)
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--severity", default="info",
                       choices=["critical", "high", "medium", "low", "info"])
    p_add.add_argument("--program", default="")
    p_add.add_argument("--status", default="draft", choices=STATUSES)
    p_add.add_argument("--bounty", type=float, default=0)
    p_add.add_argument("--notes", default="")

    p_list = sub.add_parser("list")
    p_list.add_argument("--target")
    p_list.add_argument("--status", choices=STATUSES)

    p_upd = sub.add_parser("update")
    p_upd.add_argument("id")
    p_upd.add_argument("--status", choices=STATUSES)
    p_upd.add_argument("--bounty", type=float)
    p_upd.add_argument("--notes")

    sub.add_parser("stats")
    p_show = sub.add_parser("show")
    p_show.add_argument("id")

    args = ap.parse_args()
    db = load()

    if args.cmd == "add":
        f = {
            "id": uuid.uuid4().hex[:8],
            "created": datetime.now().isoformat(timespec="seconds"),
            "target": args.target, "title": args.title,
            "severity": args.severity, "program": args.program,
            "status": args.status, "bounty": args.bounty, "notes": args.notes,
        }
        db["findings"].append(f)
        save(db)
        print(f"[+] added finding {f['id']}: {f['title']}")
        return

    if args.cmd == "list":
        rows = db["findings"]
        if args.target:
            rows = [r for r in rows if args.target.lower() in r["target"].lower()]
        if args.status:
            rows = [r for r in rows if r["status"] == args.status]
        if not rows:
            print("(no findings)")
            return
        for r in rows:
            print(f"[{r['id']}] {r['severity'].upper():<8} {r['status']:<10} "
                  f"${r['bounty']:>8.0f}  {r['target']} — {r['title']}")
        return

    if args.cmd == "update":
        for r in db["findings"]:
            if r["id"] == args.id:
                if args.status: r["status"] = args.status
                if args.bounty is not None: r["bounty"] = args.bounty
                if args.notes: r["notes"] = args.notes
                r["updated"] = datetime.now().isoformat(timespec="seconds")
                save(db)
                print(f"[+] updated {r['id']}")
                return
        print(f"[!] finding {args.id} not found")
        sys.exit(1)

    if args.cmd == "show":
        for r in db["findings"]:
            if r["id"] == args.id:
                print(json.dumps(r, indent=2))
                return
        print(f"[!] finding {args.id} not found")
        sys.exit(1)

    if args.cmd == "stats":
        rows = db["findings"]
        if not rows:
            print("(no findings yet)")
            return
        print(f"total findings: {len(rows)}")
        by_sev, by_status, by_target = {}, {}, {}
        total_bounty = 0
        for r in rows:
            by_sev[r["severity"]] = by_sev.get(r["severity"], 0) + 1
            by_status[r["status"]] = by_status.get(r["status"], 0) + 1
            by_target[r["target"]] = by_target.get(r["target"], 0) + 1
            total_bounty += r.get("bounty", 0)
        print("\nby severity:")
        for s in ["critical", "high", "medium", "low", "info"]:
            if s in by_sev:
                print(f"  {s:<8}: {by_sev[s]}")
        print("\nby status:")
        for s, c in sorted(by_status.items()):
            print(f"  {s:<10}: {c}")
        print("\nby target:")
        for t, c in sorted(by_target.items(), key=lambda x: -x[1]):
            print(f"  {t:<30}: {c}")
        print(f"\ntotal bounty earned: ${total_bounty:,.0f}")

if __name__ == "__main__":
    main()
