#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/defi-attack-patterns

Skill: SKILL: DeFi Attack Patterns — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-defi-attack-patterns.py --help
      python hack-skills-defi-attack-patterns.py --list
      python hack-skills-defi-attack-patterns.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/defi-attack-patterns'
TITLE = 'SKILL: DeFi Attack Patterns — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: defi-attack-patterns", "description: >-", "DeFi attack pattern playbook. Use when analyzing flash loan attacks, price oracle manipulation, MEV sandwich attacks, governance exploits, bridge vulnerabilities, and token standard edge cases in decentralized finance protocols."],
    'skill-defi-attack-patterns-expert-attack-playbook': [],
    '0-related-routing': ["- [smart-contract-vulnerabilities](../smart-contract-vulnerabilities/SKILL.md) for underlying Solidity vulnerability patterns (reentrancy, integer overflow, delegatecall)", "- [deserialization-insecure](../deserialization-insecure/SKILL.md) when targeting off-chain bridge relayer or indexer infrastructure"],
    '1-flash-loan-attacks': [],
    '1-1-mechanism': ["Flash loans provide uncollateralized borrowing within a single transaction. The entire borrow \u2192 use \u2192 repay cycle must complete atomically; if repayment fails, the transaction reverts as if nothing happened."],
    '1-2-price-oracle-manipulation': ["1. Flash borrow 100,000 WETH", "2. Swap 100,000 WETH \u2192 TOKEN on AMM_A", "\u2192 TOKEN spot price on AMM_A skyrockets", "3. On Lending_Protocol (reads AMM_A spot price as oracle):", "\u2192 Deposit small TOKEN collateral (valued at inflated price)", "\u2192 Borrow large amount of WETH against it", "4. Swap TOKEN back \u2192 WETH on AMM_A (restore price)", "5. Repay flash loan (100,000 WETH + fee)", "6. Keep borrowed WETH from Lending_Protocol minus collateral cost", "**Key insight**: protocols using AMM spot reserves (`getReserves()`) as price oracles are vulnerable. Must use TWAP or external oracle (Chainlink)."],
    '1-3-liquidity-pool-drain-via-reentrancy': ["Flash borrow \u2192 deposit into pool \u2192 trigger reentrancy during callback \u2192 withdraw more than deposited \u2192 repay loan.", "Exploits the combination of flash loan capital with reentrancy in pool accounting logic."],
    '1-4-governance-flash-borrow': ["1. Flash borrow governance tokens", "2. Create/vote on malicious proposal (if no snapshot or timelock)", "3. Proposal passes instantly", "4. Execute proposal (drain treasury, change admin, etc.)", "5. Return governance tokens", "Defense: snapshot-based voting (Compound Governor Bravo), timelocks, minimum proposal period."],
    '2-price-oracle-manipulation': [],
    '2-1-spot-price-vs-twap': [],
    '2-2-amm-manipulation-flow': ["Normal state: Pool has 1000 ETH + 1,000,000 USDC \u2192 price = 1000 USDC/ETH", "Attack:", "\u251c\u2500\u2500 Swap 9000 ETH into pool", "\u2502   Pool now: 10000 ETH + 100,000 USDC (constant product)", "\u2502   Spot price: 10 USDC/ETH (crashed 100x)", "\u251c\u2500\u2500 Dependent contract reads this price", "\u2502   \u2192 Liquidates positions at wrong price", "\u2502   \u2192 Or allows cheap borrowing against ETH collateral", "\u251c\u2500\u2500 Swap back: buy ETH with USDC", "\u2502   Price restores to ~1000 USDC/ETH", "\u2514\u2500\u2500 Net profit = value extracted from dependent contract - swap slippage - fees"],
    '2-3-chainlink-oracle-staleness': ["```solidity", "(, int price, , uint updatedAt, ) = priceFeed.latestRoundData();", "// Missing checks:", "// 1. price > 0", "// 2. updatedAt != 0", "// 3. block.timestamp - updatedAt < HEARTBEAT", "// 4. answeredInRound >= roundId", "If oracle is stale (network congestion, L2 sequencer down), price can be hours old \u2192 arbitrage against stale price.", "**L2 Sequencer Risk**: If Arbitrum/Optimism sequencer is down, Chainlink prices freeze. When it comes back, prices jump \u2192 mass liquidations at wrong prices."],
    '3-mev-maximal-extractable-value': [],
    '3-1-sandwich-attack': ["Mempool observation: victim submits swap TOKEN_A \u2192 TOKEN_B with slippage 1%", "Front-run:  Buy TOKEN_B (increase price)", "Victim tx:  Swap executes at worse price (within slippage tolerance)", "Back-run:   Sell TOKEN_B (profit from price impact)", "Profit = victim's price impact - gas costs \u00d7 2"],
    '3-2-jit-just-in-time-liquidity': ["1. Observe large pending swap in mempool", "2. Provide concentrated liquidity in the exact price range (Uniswap V3 tick)", "3. Victim's swap executes \u2192 JIT LP earns majority of fees", "4. Remove liquidity immediately after swap", "5. Profit = fee earned - gas - impermanent loss (minimal for single block)"],
    '3-3-liquidation-mev': ["1. Monitor lending protocols for positions approaching liquidation threshold", "2. When price oracle updates \u2192 position becomes liquidatable", "3. Front-run other liquidators \u2192 execute liquidation", "4. Receive liquidation bonus (typically 5-15% of collateral)", "5. Sell collateral for profit"],
    '3-4-mev-protection-mechanisms': [],
    '4-precision-loss-exploitation': [],
    '4-1-rounding-errors-in-token-calculations': ["Solidity has no floating point. Integer division truncates:", "shares = depositAmount * totalShares / totalAssets", "If `totalAssets` is very large relative to `depositAmount * totalShares`, result rounds to 0 \u2192 depositor gets no shares but pool keeps the deposit."],
    '4-2-first-depositor-vault-inflation-attack': ["1. Attacker deposits 1 wei \u2192 receives 1 share", "2. Attacker donates 1,000,000 tokens directly to vault (not via deposit)", "3. Vault state: 1,000,001 tokens, 1 share", "4. Victim deposits 999,999 tokens:", "shares = 999,999 * 1 / 1,000,001 = 0 (integer truncation)", "5. Victim gets 0 shares; attacker owns 100% of vault (now 2,000,000 tokens)", "6. Attacker withdraws all", "**Defenses:**", "- Mint dead shares on first deposit (OpenZeppelin ERC4626 offset)", "- Require minimum initial deposit", "- Internal accounting with virtual offset"],
    '4-3-dust-attack-via-precision-truncation': ["Repeated small operations where each truncation loses 1 wei. Accumulate across thousands of operations \u2192 material loss."],
    '5-governance-attacks': [],
    '5-1-flash-loan-governance': ["Borrow governance tokens \u2192 vote \u2192 return. Only works if protocol doesn't snapshot balances before voting."],
    '5-2-timelock-bypass': [],
    '5-3-quorum-manipulation': ["Protocol requires 10% quorum (10M tokens out of 100M supply)", "\u251c\u2500\u2500 Flash borrow 10M governance tokens", "\u251c\u2500\u2500 Create proposal: set admin = attacker", "\u251c\u2500\u2500 Vote with borrowed tokens \u2192 meets quorum", "\u251c\u2500\u2500 If no timelock: execute immediately", "\u2514\u2500\u2500 Return tokens"],
    '6-bridge-exploits': [],
    '6-1-common-bridge-attack-vectors': [],
    '6-2-cross-chain-message-verification': ["Secure pattern:", "\u251c\u2500\u2500 Source chain: emit event with (destination, amount, nonce, chainId)", "\u251c\u2500\u2500 Relayer: submit proof (Merkle proof of event inclusion)", "\u251c\u2500\u2500 Destination chain: verify proof against known source block header", "\u2502   \u251c\u2500\u2500 Check nonce not replayed", "\u2502   \u251c\u2500\u2500 Check chainId matches", "\u2502   \u251c\u2500\u2500 Verify Merkle proof against trusted root", "\u2502   \u2514\u2500\u2500 Mint/release tokens", "Vulnerable pattern:", "\u251c\u2500\u2500 Relayer: submit (destination, amount) signed by N-of-M validators", "\u2514\u2500\u2500 If M is small or keys are compromised \u2192 forge signatures"],
    '7-token-standard-edge-cases': [],
    '7-1-erc-20-approval-front-running': ["1. Alice approves Bob for 100 tokens", "2. Alice wants to change approval to 50 tokens", "3. Bob sees the approval change tx in mempool", "4. Bob front-runs: transferFrom(Alice, Bob, 100) \u2014 uses old approval", "5. Alice's approval change executes: approval = 50", "6. Bob calls transferFrom(Alice, Bob, 50) \u2014 uses new approval", "7. Bob extracted 150 tokens instead of 50", "Defense: `approve(0)` first, then `approve(newAmount)`. Or use `increaseAllowance/decreaseAllowance`."],
    '7-2-erc-777-reentrancy-via-hooks': ["ERC-777 tokens call `tokensReceived()` hook on the recipient before completing the transfer \u2192 classic reentrancy vector.", "transfer(attacker, amount)", "\u251c\u2500\u2500 _beforeTokenTransfer hook", "\u251c\u2500\u2500 Balance update", "\u251c\u2500\u2500 tokensReceived() callback to recipient  \u2190 reentrancy window", "\u2502   \u2514\u2500\u2500 attacker re-enters: transfer, swap, deposit, etc.", "\u2514\u2500\u2500 _afterTokenTransfer hook"],
    '7-3-fee-on-transfer-tokens': ["Tokens that deduct a fee on each transfer. Protocol receives less than `amount`:", "```solidity", "// Vulnerable: assumes received == amount", "token.transferFrom(msg.sender, address(this), amount);", "deposits[msg.sender] += amount; // overcredits by fee amount", "// Fixed: measure actual balance change", "uint before = token.balanceOf(address(this));", "token.transferFrom(msg.sender, address(this), amount);", "uint received = token.balanceOf(address(this)) - before;", "deposits[msg.sender] += received;"],
    '7-4-rebasing-tokens': ["Tokens that automatically adjust balances (e.g., Aave aTokens, stETH). Protocols holding rebasing tokens may have accounting mismatches if they cache balances."],
    '8-notable-defi-exploits-reference': [],
    '9-decision-tree': ["Analyzing a DeFi protocol?", "\u251c\u2500\u2500 Does it use price oracles?", "\u2502   \u251c\u2500\u2500 Spot price (AMM reserves)? \u2192 Flash loan manipulation (Section 1.2)", "\u2502   \u2502   \u2514\u2500\u2500 Can oracle be manipulated in single tx? \u2192 HIGH RISK", "\u2502   \u251c\u2500\u2500 TWAP? \u2192 Multi-block manipulation needed \u2192 MEDIUM RISK", "\u2502   \u251c\u2500\u2500 Chainlink? \u2192 Check staleness handling (Section 2.3)", "\u2502   \u2502   \u251c\u2500\u2500 Heartbeat check present? \u2192 OK", "\u2502   \u2502   \u2514\u2500\u2500 L2? \u2192 Check sequencer uptime oracle", "\u2502   \u2514\u2500\u2500 Multiple oracles with fallback? \u2192 Evaluate each", "\u251c\u2500\u2500 Does it accept external tokens?", "\u2502   \u251c\u2500\u2500 Yes \u2192 Check fee-on-transfer handling (Section 7.3)", "\u2502   \u251c\u2500\u2500 ERC-777 tokens accepted? \u2192 Reentrancy via hooks (Section 7.2)", "\u2502   \u2514\u2500\u2500 Rebasing tokens? \u2192 Accounting mismatch (Section 7.4)", "\u251c\u2500\u2500 Does it have governance?", "\u2502   \u251c\u2500\u2500 Yes \u2192 Flash loan governance possible? (Section 5.1)", "\u2502   \u2502   \u251c\u2500\u2500 Snapshot-based voting? \u2192 Safer", "\u2502   \u2502   \u2514\u2500\u2500 Live balance voting? \u2192 Flash borrow attack", "\u2502   \u251c\u2500\u2500 Timelock present? \u2192 Check for bypass (Section 5.2)", "\u2502   \u2514\u2500\u2500 Quorum threshold vs flash-loanable supply? (Section 5.3)", "\u251c\u2500\u2500 Is it a vault / yield aggregator?", "\u2502   \u251c\u2500\u2500 Yes \u2192 First depositor attack (Section 4.2)", "\u2502   \u2502   \u2514\u2500\u2500 Virtual offset or dead shares? \u2192 Mitigated", "\u2502   \u2514\u2500\u2500 Precision loss in share calculation? (Section 4.1)", "\u251c\u2500\u2500 Is it a bridge?", "\u2502   \u251c\u2500\u2500 Yes \u2192 Load bridge vectors (Section 6)", "\u2502   \u2502   \u251c\u2500\u2500 Validator set size and key management?", "\u2502   \u2502   \u251c\u2500\u2500 Replay protection (nonce + chainId)?", "\u2502   \u2502   \u2514\u2500\u2500 Upgradeable? \u2192 Who holds upgrade key?", "\u2502   \u2514\u2500\u2500 No \u2192 Continue", "\u251c\u2500\u2500 User-facing swap functionality?", "\u2502   \u251c\u2500\u2500 Yes \u2192 MEV exposure (Section 3)", "\u2502   \u2502   \u251c\u2500\u2500 Slippage protection enforced?", "\u2502   \u2502   \u2514\u2500\u2500 Private mempool integration?", "\u2502   \u2514\u2500\u2500 No \u2192 Continue", "\u2514\u2500\u2500 Load [smart-contract-vulnerabilities](../smart-contract-vulnerabilities/SKILL.md)", "for underlying Solidity-level bugs"],
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