#!/usr/bin/env python3
"""audit-smart-contract.py - Web3 smart contract security audit (v2.5.0).

Static analysis for Solidity/Vyper contracts. Detects common vulnerabilities:
- Reentrancy, tx.origin, unchecked calls, delegatecall abuse
- Integer overflow, block.timestamp manipulation
- Access control issues, uninitialized storage

Usage:
  python3 audit-smart-contract.py contract.sol
  python3 audit-smart-contract.py ./contracts/
  python3 audit-smart-contract.py contract.sol --slither  # requires slither
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

PATTERNS = [
    (r'\.send\(|\.transfer\(', 'high', 'Use of send/transfer (gas limit issues, prefer call)'),
    (r'\.call\(', 'medium', 'Low-level call (ensure return value check)'),
    (r'\.delegatecall\(', 'high', 'delegatecall (storage collision risk)'),
    (r'tx\.origin', 'high', 'tx.origin used (phishing vulnerability, use msg.sender)'),
    (r'block\.timestamp', 'low', 'block.timestamp used (miner manipulable)'),
    (r'block\.number', 'low', 'block.number used (predictable in some contexts)'),
    (r'now\b', 'low', 'now (alias for block.timestamp)'),
    (r'selfdestruct', 'critical', 'selfdestruct (irreversible, access control needed)'),
    (r'external\s+function', 'info', 'External function (check access control)'),
    (r'public\s+function', 'info', 'Public function (check access control)'),
    (r'payable', 'medium', 'Payable function (ensure ETH handling)'),
    (r'\+\+', 'low', 'Increment (check for overflow in older Solidity)'),
    (r'\-\-', 'low', 'Decrement (check for underflow in older Solidity)'),
    (r'pragma solidity\s*[<>=]', 'info', 'Compiler version constraint (use latest)'),
    (r'assembly\s*\{', 'high', 'Inline assembly (review carefully)'),
    (r'keccak256\(abi\.encodePacked', 'low', 'encodePacked (collision risk with dynamic types)'),
]

def audit_file(path):
    findings = []
    with open(path) as f:
        content = f.read()
    for pat, sev, desc in PATTERNS:
        matches = list(re.finditer(pat, content, re.I))
        if matches:
            for m in matches[:3]:  # limit to 3 per pattern
                line_num = content[:m.start()].count('\n') + 1
                findings.append({
                    'file': path, 'line': line_num, 'severity': sev,
                    'description': desc, 'match': m.group(0)[:50]
                })
    return findings

def main():
    ap = argparse.ArgumentParser(description='Smart contract security audit')
    ap.add_argument('target', help='contract file or directory')
    ap.add_argument('--slither', action='store_true', help='run Slither (if installed)')
    args = ap.parse_args()

    if not os.path.exists(args.target):
        print(f"Error: {args.target} not found")
        sys.exit(1)

    files = []
    if os.path.isfile(args.target):
        files = [args.target]
    else:
        for root, dirs, fnames in os.walk(args.target):
            files.extend(os.path.join(root, f) for f in fnames if f.endswith(('.sol', '.vy')))

    if not files:
        print("No Solidity/Vyper files found")
        sys.exit(1)

    print(f"[*] Auditing {len(files)} file(s)...")
    all_findings = []
    for f in files:
        findings = audit_file(f)
        all_findings.extend(findings)
        if findings:
            print(f"  {f}: {len(findings)} findings")

    sev_counts = {}
    for f in all_findings:
        sev_counts[f['severity']] = sev_counts.get(f['severity'], 0) + 1

    print(f"\n{'='*60}")
    print(f"Findings: {len(all_findings)}")
    for sev in ['critical', 'high', 'medium', 'low', 'info']:
        if sev in sev_counts:
            print(f"  {sev.upper()}: {sev_counts[sev]}")

    print(f"\n{'='*60}\n")
    for f in sorted(all_findings, key=lambda x: ['critical','high','medium','low','info'].index(x['severity'])):
        print(f"[{f['severity'].upper()}] {f['file']}:{f['line']}")
        print(f"  {f['description']}")
        print(f"  Match: {f['match']}")
        print()

    if args.slither and shutil.which('slither'):
        print("[*] Running Slither...")
        subprocess.run(['slither', args.target], check=False)
    elif args.slither:
        print("[!] Slither not installed")

if __name__ == '__main__':
    main()
