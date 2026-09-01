#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/smart-contract-vulnerabilities

Skill: SKILL: Smart Contract Vulnerabilities — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-smart-contract-vulnerabilities.py --help
      python hack-skills-smart-contract-vulnerabilities.py --list
      python hack-skills-smart-contract-vulnerabilities.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/smart-contract-vulnerabilities'
TITLE = 'SKILL: Smart Contract Vulnerabilities — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: smart-contract-vulnerabilities", "description: >-", "Smart contract vulnerability playbook. Use when auditing Solidity/EVM contracts for reentrancy, integer overflow, access control, delegatecall, flash loan, signature replay, and MEV-related attack patterns."],
    'skill-smart-contract-vulnerabilities-expert-attack-playbook': [],
    '0-related-routing': ["- [defi-attack-patterns](../defi-attack-patterns/SKILL.md) when the vulnerability is part of a DeFi protocol exploit (flash loans, oracle manipulation, governance attacks)", "- [deserialization-insecure](../deserialization-insecure/SKILL.md) when the target is off-chain infrastructure deserializing blockchain data"],
    'advanced-reference': ["Also load [SOLIDITY_VULN_PATTERNS.md](./SOLIDITY_VULN_PATTERNS.md) when you need:", "- Side-by-side vulnerable vs fixed code patterns for each vulnerability class", "- Gas optimization traps that introduce vulnerabilities", "- Proxy pattern storage collision examples with slot calculations"],
    '1-reentrancy': ["The most iconic smart contract vulnerability. External calls transfer execution control; if state is not updated before the call, the callee can re-enter."],
    '1-1-classic-reentrancy-single-function': ["Victim.withdraw()", "\u251c\u2500\u2500 checks balance[msg.sender] > 0          \u2713", "\u251c\u2500\u2500 msg.sender.call{value: balance}(\"\")     \u2190 external call", "\u2502   \u2514\u2500\u2500 Attacker.receive()", "\u2502       \u2514\u2500\u2500 Victim.withdraw()               \u2190 re-enters before state update", "\u2502           \u251c\u2500\u2500 checks balance[msg.sender]   \u2190 still > 0!", "\u2502           \u2514\u2500\u2500 sends ETH again", "\u2514\u2500\u2500 balance[msg.sender] = 0                 \u2190 too late"],
    '1-2-cross-function-reentrancy': ["Two functions share state; attacker re-enters a different function during callback:"],
    '1-3-cross-contract-reentrancy': ["Contract A calls Contract B, which calls back into Contract A (or Contract C that reads A's stale state). Especially dangerous in DeFi protocols where multiple contracts share state."],
    '1-4-read-only-reentrancy': ["The re-entered function is a `view` function used by a third-party contract for price calculation. No state modification in the victim, but the stale intermediate state misleads the reader.", "**Real-world**: Curve pool `get_virtual_price()` read during `remove_liquidity()` callback \u2192 inflated price \u2192 profit on dependent lending protocol."],
    'mitigations': [],
    '2-integer-overflow-underflow': [],
    'pre-solidity-0-8': ["Arithmetic silently wraps: `uint8(255) + 1 == 0`, `uint8(0) - 1 == 255`."],
    'post-solidity-0-8': ["Default checked arithmetic reverts on overflow. But `unchecked{}` blocks reintroduce risk:", "```solidity", "unchecked {", "// \"gas optimization\" \u2014 but if i can be influenced by user input, overflow returns", "for (uint i = start; i < end; i++) { ... }"],
    'safemath-bypass-scenarios': ["- Casting: `uint256` \u2192 `uint128` truncation before SafeMath check", "- Assembly blocks: `mstore` / `add` bypass Solidity-level checks", "- Intermediate multiplication overflow before division: `(a * b) / c` where `a * b` overflows"],
    '3-access-control': [],
    'tx-origin-vs-msg-sender': ["Attack: trick owner into calling attacker contract \u2192 attacker contract calls victim with owner's `tx.origin`."],
    'common-patterns': [],
    '4-randomness-manipulation': ["On-chain randomness sources are predictable to miners/validators:", "**Commit-reveal bypass**: If reveal phase doesn't enforce timeout or bond, attacker can choose not to reveal unfavorable outcomes (selective abort attack)."],
    '5-delegatecall-vulnerabilities': ["`delegatecall` executes callee's code in caller's storage context. Storage slot layout must match exactly."],
    'storage-layout-collision': ["Proxy (storage):         Implementation (code):", "slot 0: owner            slot 0: someVariable", "slot 1: implementation   slot 1: anotherVariable", "Implementation writes to `someVariable` (slot 0) \u2192 overwrites proxy's `owner`. Attacker calls implementation function that writes slot 0 \u2192 becomes proxy owner."],
    'function-selector-collision': ["4-byte function selectors can collide. If proxy's `admin()` selector collides with implementation's `transfer()`, calling `admin()` on the proxy executes `transfer()` logic.", "Tool: `cast selectors <bytecode>` (Foundry) to enumerate selectors."],
    '6-front-running-mev': [],
    'transaction-ordering-manipulation': ["Victim submits DEX swap tx (visible in mempool)", "\u251c\u2500\u2500 Front-runner: buy token before victim (raise price)", "\u251c\u2500\u2500 Victim tx executes at worse price", "\u2514\u2500\u2500 Back-runner: sell token after victim (profit from spread)", "= Sandwich attack"],
    'protection-patterns': [],
    '7-signature-replay': [],
    'missing-nonce': ["Reuse a valid signature to repeat the action (e.g., transfer) multiple times."],
    'cross-chain-replay': ["Same contract deployed on multiple chains with same address \u2192 signature valid on all chains. Must include `block.chainid` in signed message."],
    'eip-712-implementation-errors': [],
    '8-self-destruct-force-send-eth': ["`selfdestruct(recipient)` force-sends all contract ETH to recipient \u2014 bypasses `receive()` and `fallback()`, cannot be rejected.", "Breaks contracts that rely on `address(this).balance` for logic (e.g., `require(balance == expected)`).", "Post-EIP-6780 (Dencun): `selfdestruct` only sends ETH; code/storage deletion only if called in same tx as creation."],
    '9-create2-deterministic-address-exploitation': ["`CREATE2` address = `keccak256(0xff ++ deployer ++ salt ++ keccak256(initCode))`."],
    '10-flash-loan-attack-patterns': ["Single transaction:", "\u251c\u2500\u2500 Borrow large amount (no collateral)", "\u251c\u2500\u2500 Manipulate state (price oracle, governance, etc.)", "\u251c\u2500\u2500 Extract profit from manipulated state", "\u251c\u2500\u2500 Repay loan + fee", "\u2514\u2500\u2500 Keep profit", "Key: entire sequence must succeed atomically or the whole tx reverts."],
    '11-short-address-attack': ["EVM pads missing bytes in ABI-encoded calldata with zeros. If `transfer(address, uint256)` is called with a 19-byte address, the uint256 amount shifts left by 8 bits \u2192 multiplied by 256.", "Mitigation: validate calldata length; modern Solidity compilers add checks."],
    '12-tools': [],
    '13-decision-tree': ["Auditing a smart contract?", "\u251c\u2500\u2500 Is it a proxy pattern?", "\u2502   \u251c\u2500\u2500 Yes \u2192 Check storage layout collision (Section 5)", "\u2502   \u2502   \u251c\u2500\u2500 Compare slot assignments between proxy and implementation", "\u2502   \u2502   \u251c\u2500\u2500 Check for function selector collision", "\u2502   \u2502   \u2514\u2500\u2500 Verify initializer cannot be called twice", "\u2502   \u2514\u2500\u2500 No \u2192 Continue", "\u251c\u2500\u2500 Does it make external calls?", "\u2502   \u251c\u2500\u2500 Yes \u2192 Check reentrancy (Section 1)", "\u2502   \u2502   \u251c\u2500\u2500 State updated before call? \u2192 CEI pattern OK", "\u2502   \u2502   \u251c\u2500\u2500 ReentrancyGuard present? \u2192 Check all entry points", "\u2502   \u2502   \u251c\u2500\u2500 Cross-function state sharing? \u2192 Cross-function reentrancy risk", "\u2502   \u2502   \u2514\u2500\u2500 View functions read during callback? \u2192 Read-only reentrancy", "\u2502   \u2514\u2500\u2500 No \u2192 Continue", "\u251c\u2500\u2500 Does it handle tokens/ETH?", "\u2502   \u251c\u2500\u2500 Yes \u2192 Check integer overflow (Section 2)", "\u2502   \u2502   \u251c\u2500\u2500 Solidity < 0.8? \u2192 All arithmetic suspect", "\u2502   \u2502   \u251c\u2500\u2500 unchecked{} blocks? \u2192 Verify no user-influenced values", "\u2502   \u2502   \u2514\u2500\u2500 Casting between uint sizes? \u2192 Truncation risk", "\u2502   \u2514\u2500\u2500 Also check self-destruct force-send (Section 8)", "\u251c\u2500\u2500 Does it use signatures?", "\u2502   \u251c\u2500\u2500 Yes \u2192 Check replay (Section 7)", "\u2502   \u2502   \u251c\u2500\u2500 Nonce included? \u2192 Verify incremented", "\u2502   \u2502   \u251c\u2500\u2500 ChainId included? \u2192 Cross-chain safe", "\u2502   \u2502   \u2514\u2500\u2500 ecrecover result checked for address(0)? \u2192 OK", "\u2502   \u2514\u2500\u2500 No \u2192 Continue", "\u251c\u2500\u2500 Does it use on-chain randomness?", "\u2502   \u251c\u2500\u2500 Yes \u2192 Predictable (Section 4)", "\u2502   \u2502   \u2514\u2500\u2500 Recommend Chainlink VRF or commit-reveal with bond", "\u2502   \u2514\u2500\u2500 No \u2192 Continue", "\u251c\u2500\u2500 Does it interact with DeFi protocols?", "\u2502   \u251c\u2500\u2500 Yes \u2192 Load [defi-attack-patterns](../defi-attack-patterns/SKILL.md)", "\u2502   \u2502   \u251c\u2500\u2500 Flash loan vectors", "\u2502   \u2502   \u251c\u2500\u2500 Oracle manipulation", "\u2502   \u2502   \u2514\u2500\u2500 MEV exposure", "\u2502   \u2514\u2500\u2500 No \u2192 Continue", "\u251c\u2500\u2500 Does it use CREATE2?", "\u2502   \u251c\u2500\u2500 Yes \u2192 Check deterministic address exploitation (Section 9)", "\u2502   \u2514\u2500\u2500 No \u2192 Continue", "\u2514\u2500\u2500 Run automated tools (Section 12)", "\u251c\u2500\u2500 Slither for static analysis", "\u251c\u2500\u2500 Mythril for symbolic execution", "\u2514\u2500\u2500 Echidna for fuzzing invariants"],
}

def main():
    ap = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="list sections")
    ap.add_argument("--dump", metavar="SECTION", help="dump payloads for a section")
    ap.add_argument("--search", metavar="KEYWORD", help="search payloads")
    args = ap.parse_args()
    if args.list or not (args.dump or args.search):
        print("=== %s ===" % TITLE)
        print(DESCRIPTION)
        print()
        print("Sections (%d):" % len(PAYLOADS))
        for k in PAYLOADS:
            print("  -", k, "(%d payloads)" % len(PAYLOADS[k]))
        if args.list:
            return
    if args.dump:
        if args.dump not in PAYLOADS:
            print("Section not found. Available:", list(PAYLOADS.keys()))
            sys.exit(1)
        for p in PAYLOADS[args.dump]:
            print(p)
        return
    if args.search:
        q = args.search.lower()
        hits = 0
        for k, v in PAYLOADS.items():
            for p in v:
                if q in p.lower():
                    print("[%s] %s" % (k, p))
                    hits += 1
        print("\n%d hits" % hits)
        return

if __name__ == "__main__":
    main()