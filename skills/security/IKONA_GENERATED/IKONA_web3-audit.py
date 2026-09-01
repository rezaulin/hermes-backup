#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/web3-audit

Skill: WEB3 SMART CONTRACT AUDIT
Desc : Smart contract security audit — 10 DeFi bug classes (accounting desync, access control, incomplete path, off-by-one, oracle, ERC4626, reentrancy, flash loan, signature replay, proxy), pre-dive kill signals (TVL < $500K etc), Foundry PoC template, grep patterns for each class, and real Immunefi paid examples. Use for any Solidity/Rust contract audit or when deciding whether a DeFi target is worth hunting.

Run:  python claude-bughunter-web3-audit.py --help
      python claude-bughunter-web3-audit.py --list
      python claude-bughunter-web3-audit.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/web3-audit'
TITLE = 'WEB3 SMART CONTRACT AUDIT'
DESCRIPTION = 'Smart contract security audit — 10 DeFi bug classes (accounting desync, access control, incomplete path, off-by-one, oracle, ERC4626, reentrancy, flash loan, signature replay, proxy), pre-dive kill signals (TVL < $500K etc), Foundry PoC template, grep patterns for each class, and real Immunefi paid examples. Use for any Solidity/Rust contract audit or when deciding whether a DeFi target is worth hunting.'

PAYLOADS = {
    'main': ["name: web3-audit", "description: Smart contract security audit \u2014 10 DeFi bug classes (accounting desync, access control, incomplete path, off-by-one, oracle, ERC4626, reentrancy, flash loan, signature replay, proxy), pre-dive kill signals (TVL < $500K etc), Foundry PoC template, grep patterns for each class, and real Immunefi paid examples. Use for any Solidity/Rust contract audit or when deciding whether a DeFi target is worth hunting."],
    'web3-smart-contract-audit': ["10 bug classes. Pre-dive kill signals. Foundry PoC template. Real paid examples."],
    'pre-dive-kill-signals-check-before-any-code-review': ["1. **TVL < $500K** \u2192 max payout capped too low for effort", "2. **2+ top-tier audits** (Halborn, ToB, Cyfrin, OpenZeppelin) on simple protocol \u2192 bugs already found", "3. **Protocol < 500 lines, single A\u2192B\u2192C flow** \u2192 minimal attack surface", "4. **Formula**: `max_realistic_payout = min(10% \u00d7 TVL, program_cap)` \u2014 if < $10K, skip", "**Soft kill:** OZ/ToB/Cyfrin audit on current version + codebase > 500K LOC \u2192 expect 40+ hours for maybe 1 finding. Only proceed if bounty floor > $50K AND you have protocol-specific expertise.", "**Target scoring (go if >= 6/10):**", "- TVL > $10M: +2", "- Immunefi program with Critical >= $50K: +2", "- No top-tier audit on current version: +2", "- < 30 days since deploy: +1", "- Protocol you've hunted before: +1", "- Source code + natspec comments: +1", "- Upgradeable proxies: +1"],
    'the-one-rule': ["This single rule explains 19% of all Critical findings."],
    '1-accounting-state-desynchronization': [],
    'what-it-is': ["Two state variables supposed to stay in sync. One code path updates A but forgets B. Later code reads both and makes decisions based on stale B.", "Real Value = A - B", "If A updated but B isn't \u2192 Real Value appears larger \u2192 phantom value"],
    'root-cause-patterns': ["**Variant 1: Phantom Yield** (Yeet protocol \u2014 35 duplicate reports)", "```solidity", "function startUnstake(uint256 amount) external {", "totalSupply -= amount;  // decremented BEFORE transfer", "// aToken.balanceOf(this) still reflects old value", "// yieldAmount = aToken.balanceOf - totalSupply = phantom yield", "**Variant 2: Fast Path Skips State Update** (Alchemix V3)", "```solidity", "function claimRedemption(uint256 tokenId) external {", "if (transmuter.balance >= amount) {", "transmuter.transfer(user, amount);", "_burn(tokenId);", "return;  // EARLY RETURN \u2014 cumulativeEarmarked, _redemptionWeight, totalDebt never updated", "// Slow path: updates all state vars correctly", "alchemist.redeem(...);", "**Variant 3: Update Happens in Wrong Order** (Alchemix)", "```solidity", "function deposit(uint256 amount) external {", "_shares = (amount * totalShares) / totalAssets;  // calculated BEFORE deposit", "totalAssets += amount;   // assets added AFTER shares calculated \u2192 wrong rate"],
    'grep-patterns': ["```bash"],
    'find-all-accounting-variables': ["grep -rn \"totalSupply\\|totalShares\\|totalAssets\\|totalDebt\\|cumulativeReward\\|rewardPerShare\" contracts/"],
    'find-all-early-returns-in-claim-redeem-functions': ["grep -rn \"\\breturn\\b\" contracts/ -B3 | grep -B3 \"if\\b\""],
    'for-each-early-return-which-state-updates-in-normal-path-are-skipped': [],
    '2-access-control': [],
    'variant-1-missing-modifier-on-sibling-function': ["```solidity", "function vote(uint256 tokenId) external onlyNewEpoch(tokenId) {  // guarded", "function reset(uint256 tokenId) external onlyNewEpoch(tokenId) { // guarded", "function poke(uint256 tokenId) external {                         // NO GUARD \u2192 infinite FLUX inflation"],
    'variant-2-wrong-check-existence-vs-ownership': ["```solidity", "function split(uint256 tokenId, uint256 amount) external {", "_requireOwned(tokenId);  // checks if token EXISTS, not if caller OWNS it", "_burn(tokenId);", "_mint(msg.sender, amount);  // attacker steals tokens they don't own"],
    'variant-3-silent-modifier-if-vs-require': ["```solidity", "// VULNERABLE \u2014 non-admin silently gets through:", "modifier onlyAdmin() {", "if (msg.sender == admin) {", "_;  // body only executes for admin, but non-admin doesn't revert", "// CORRECT: require(msg.sender == admin, \"Not admin\"); _;"],
    'variant-4-uninitialized-proxy': ["```solidity", "function initialize(address _owner) public {  // MISSING: initializer modifier", "owner = _owner;  // anyone can call \u2192 become owner", "// Fix: constructor() { _disableInitializers(); }"],
    'grep-patterns': ["```bash"],
    'find-sibling-function-families-do-all-have-the-same-modifier-set': ["grep -rn \"function vote\\|function poke\\|function reset\\|function update\\|function claim\\|function harvest\" contracts/ -A2"],
    'ownership-check-existence-vs-ownership': ["grep -rn \"_requireOwned\\|ownerOf\\|_isApprovedOrOwner\\|_checkAuthorized\" contracts/ -B5"],
    'silent-modifiers': ["grep -rn \"modifier\\b\" contracts/ -A8 | grep -B3 \"if (\" | grep -v \"require\\|revert\""],
    'uninitialized-initializer': ["grep -rn \"function initialize\\b\" contracts/ -A3", "grep -rn \"_disableInitializers()\" contracts/"],
    'real-paid-examples': [],
    '3-incomplete-code-path': [],
    'the-function-family-comparison-test': ["1. List all state changes in function A (deposit/place/create)", "2. List all state changes in function B (withdraw/update/cancel)", "3. For each state change in A: does B have the corresponding reverse?", "4. For each token transfer in A: does B have the corresponding refund?", "If A does X but B doesn't do the reverse of X \u2192 BUG."],
    'variant-1-update-function-missing-refund-thundernft': ["```solidity", "function place_order(OrderInput calldata order) external {", "token.safeTransferFrom(msg.sender, address(this), order.price);  // takes tokens", "orders[orderId] = order;", "function update_order(OrderInput calldata updatedOrder) external {", "// BUG: NO REFUND for sell orders when price decreases \u2192 tokens permanently stuck", "orders[orderId] = updatedOrder;"],
    'variant-2-partial-fill-token-stuck-plume': ["```solidity", "function swapForETH(uint256 amountIn) external {", "token.safeTransferFrom(msg.sender, address(this), amountIn);", "uint256 filled = dex.swap(amountIn);  // partial fill possible", "_refundExcessEth(amountIn - filled);  // BUG: refunds ETH only, not ERC20"],
    'variant-3-mint-bypasses-check-that-deposit-has-metapool': ["```solidity", "function deposit(uint256 assets, address receiver) public override {", "shares = _deposit(assets, receiver);  // includes receipt validation", "function mint(uint256 shares, address receiver) public override {", "assets = convertToAssets(shares);", "_mint(receiver, shares);  // MISSING: _deposit() validation \u2192 mints without receiving assets"],
    'grep-patterns': ["```bash", "grep -rn \"function place_\\|function create_\\|function add_\\|function open_\" contracts/ -A5", "grep -rn \"function update_\\|function modify_\\|function cancel_\" contracts/ -A5", "grep -rn \"safeApprove\\b\" contracts/    # safeApprove without zero-reset before", "grep -rn \"delete\\b\" contracts/ -B5 -A5  # delete before operation completes", "grep -rn \"function deposit\\|function mint\\|function withdraw\\|function redeem\" contracts/ -A10"],
    '4-off-by-one-boundary-conditions': [],
    'root-cause': ["```solidity", "// VeChain Stargate \u2014 post-exit reward drain:", "function _claimableDelegationPeriods(address delegator) internal view returns (uint256) {", "if (endPeriod > nextClaimablePeriod) {  // BUG: should be >=", "return 0;  // exited users get nothing", "return nextClaimablePeriod - lastClaimedPeriod;  // rewards for period AFTER exit"],
    'mental-test-for-every-comparison': [],
    '6-boundary-locations-to-check': ["1. Period/Epoch boundaries: `>` vs `>=` at period end", "2. Time-based locks: does `block.timestamp == deadline` lock or unlock?", "3. Loop break conditions: `break` with `>` vs `>=`", "4. Array index boundaries: `i <= array.length` (should be `i < array.length`)", "5. Amount/balance boundaries: `>= amount` allows exact full withdrawal?", "6. Rounding/precision: can any input produce 0 output that should be non-zero?"],
    'grep-patterns': ["```bash"],
    'boundaries-in-comparisons': ["grep -rn \"Period\\|Epoch\\|Round\\|Deadline\\|period\\|epoch\\|deadline\" contracts/ -A3 | grep \"[<>][^=]\""],
    'loop-breaks': ["grep -rn \"\\bbreak\\b\" contracts/ -B10"],
    'off-by-one-in-array-access': ["grep -rn \"\\.length\\s*-\\s*1\\|i\\s*<=\\s*.*\\.length\\b\" contracts/"],
    '5-oracle-price-manipulation': [],
    'bug-a-missing-staleness-check-most-common': ["```solidity", "// VULNERABLE:", "(, int256 price,,,) = priceFeed.latestRoundData();", "return uint256(price);  // If Chainlink node goes down, stale price returned indefinitely", "// CORRECT:", "(, int256 price,, uint256 updatedAt,) = priceFeed.latestRoundData();", "require(block.timestamp - updatedAt <= MAX_PRICE_AGE, \"Stale price\");", "require(price > 0, \"Invalid price\");"],
    'bug-b-missing-confidence-interval-pyth': ["```solidity", "// VULNERABLE:", "PythStructs.Price memory p = pyth.getPriceUnsafe(priceFeed);", "return p.price;  // ignores p.conf (confidence interval)", "// CORRECT:", "require(p.conf * 10 <= uint64(p.price), \"Price too uncertain\");", "// conf > 10% of price = untrustworthy"],
    'bug-c-twap-too-short-flash-loan-manipulatable': ["```solidity", "// VULNERABLE: 60-second TWAP", "uint32[] memory secondsAgos = new uint32[](2);", "secondsAgos[0] = 60; secondsAgos[1] = 0;", "// Flash loan can shift price for entire 60s window", "// CORRECT: 1800s minimum TWAP (30 min)"],
    'bug-d-single-source-oracle': ["```solidity", "// VULNERABLE: only Uniswap spot price", "uint price = getUniswapSpotPrice(token);  // flash loan manipulatable", "// CORRECT: Chainlink primary, Uniswap TWAP as fallback, require close agreement"],
    'grep-patterns': ["```bash"],
    'missing-staleness-check': ["grep -rn \"latestRoundData\" contracts/ -A5 | grep -v \"updatedAt\\|timestamp\""],
    'pyth-price-usage-confidence-interval-checked': ["grep -rn \"getPriceUnsafe\\|getPrice\\b\" contracts/ -A8 | grep -v \"conf\\|confidence\""],
    'twap-windows-short-twap-flag': ["grep -rn \"secondsAgo\\|TWAP\\|cardinality\" contracts/ -A5"],
    '6-erc4626-vault-attacks': [],
    'exchange-rate-manipulation-near-empty-vault': ["```solidity", "// VULNERABLE \u2014 first depositor attack:", "// 1. Attacker deposits 1 wei \u2192 gets 1 share", "// 2. Attacker donates large amount directly (transfer, not deposit)", "// 3. Exchange rate: 1 share = (1 + donation) assets", "// 4. Victim deposits \u2192 rounds down to 0 shares \u2192 free donation to attacker", "// CORRECT: virtual shares (OpenZeppelin v4.9+)", "function _decimalsOffset() internal view virtual override returns (uint8) {", "return 9;  // add 1e9 virtual shares + assets to prevent manipulation"],
    'erc4626-transfer-moves-shares-but-not-stake-lock-records': ["```solidity", "// VULNERABLE: shares transferred, but lock records stay with original owner", "// \u2192 shares stuck, can't redeem \u2192 permanent freeze (Belong pattern)", "function transfer(address to, uint256 amount) external override {", "_transfer(msg.sender, to, amount);  // moves shares", "// MISSING: transfer lock record from msg.sender to `to`"],
    'grep-patterns': ["```bash", "grep -rn \"function transfer\\|function transferFrom\" contracts/ -A15", "grep -rn \"function deposit\\|function mint\\|function withdraw\\|function redeem\" contracts/ -A10"],
    '7-reentrancy': [],
    'variants': ["- **Single-function**: attacker re-enters same function before state updated", "- **Cross-function**: re-enters a sibling function with stale state", "- **Cross-contract**: re-enters via a callback to another protocol", "- **Read-only**: re-enters a view function that returns stale data used by attacker"],
    'root-cause-pattern': ["```solidity", "// VULNERABLE (effects after interaction):", "function withdraw(uint256 amount) external {", "require(balances[msg.sender] >= amount);", "(bool success,) = msg.sender.call{value: amount}(\"\");  // INTERACTION first", "require(success);", "balances[msg.sender] -= amount;  // EFFECT after \u2192 reentrancy window", "// CORRECT (CEI \u2014 Checks, Effects, Interactions):", "function withdraw(uint256 amount) external {", "require(balances[msg.sender] >= amount);  // CHECK", "balances[msg.sender] -= amount;            // EFFECT", "(bool success,) = msg.sender.call{value: amount}(\"\");  // INTERACTION last", "require(success);"],
    'grep-patterns': ["```bash"],
    'external-calls-before-state-updates': ["grep -rn \"\\.call{value\\|safeTransfer\\|transfer(\" contracts/ -B10 | grep -v \"require\\|revert\""],
    'missing-nonreentrant-modifier-on-critical-functions': ["grep -rn \"function withdraw\\|function redeem\\|function claim\" contracts/ -A2 | grep -v \"nonReentrant\""],
    'storage-slot-for-reentrancy-guard': ["grep -rn \"nonReentrant\\|ReentrancyGuard\\|_notEntered\" contracts/"],
    '8-flash-loan-attacks': [],
    'oracle-manipulation-via-flash-loan': ["```solidity", "// Attack flow:", "// 1. Borrow $100M from Aave flash loan", "// 2. Dump token in Uniswap pool \u2192 crash spot price", "// 3. Protocol reads Uniswap spot \u2192 undercollateralized loans accepted", "// 4. Borrow max against cheap collateral", "// 5. Repay flash loan, keep profits"],
    'price-oracle-sanity-checks-what-to-look-for': ["```bash", "grep -rn \"getReserves\\|getAmountsOut\\|slot0\\b\" contracts/ -A5"],
    'spot-price-from-reserves-manipulatable-with-flash-loan': [],
    'slot0-uniswap-v3-spot-price-manipulatable': [],
    '9-signature-replay': [],
    'missing-nonce': ["```solidity", "// VULNERABLE:", "function permit(address owner, address spender, uint256 value,", "uint256 deadline, uint8 v, bytes32 r, bytes32 s) external {", "bytes32 hash = keccak256(abi.encodePacked(owner, spender, value, deadline));", "// MISSING: nonce not included \u2192 same signature usable multiple times", "require(ecrecover(hash, v, r, s) == owner);"],
    'missing-chain-id': ["```solidity", "// VULNERABLE: signature valid on mainnet AND testnet AND all forks", "bytes32 hash = keccak256(abi.encodePacked(params));", "// MISSING: block.chainid not in hash \u2192 works on any chain"],
    'grep-patterns': ["```bash", "grep -rn \"ecrecover\\|ECDSA\\.recover\" contracts/ -B20"],
    'check-does-the-signed-hash-include-nonce-chainid-contract-address': ["grep -rn \"nonce\\|_nonces\\|nonces\\[\" contracts/"],
    '10-proxy-upgrade-issues': [],
    'storage-collision': ["```solidity", "// Implementation and proxy share storage layout", "// Proxy slot 0: _owner", "// Implementation slot 0: _initialized", "// \u2192 writing to _initialized overwrites _owner"],
    'uninitialized-implementation': ["```solidity", "// If implementation can be initialized directly \u2192 anyone becomes owner of implementation", "// Attack: call initialize() on implementation contract \u2192 call upgradeTo() \u2192 replace logic"],
    'delegatecall-to-user-controlled-address': ["```solidity", "function execute(address target, bytes calldata data) external onlyOwner {", "target.delegatecall(data);  // target is validated, but what if owner is compromised?"],
    'grep-patterns': ["```bash"],
    'uups-initialization-protection': ["grep -rn \"function initialize\\b\\|_disableInitializers\\|initializer\" contracts/"],
    'delegate-call': ["grep -rn \"delegatecall\\b\" contracts/ -B3 -A5"],
    'storage-layout-proxy-uses-eip-1967-slots': ["grep -rn \"0x360894\\|EIP1967\\|_IMPLEMENTATION_SLOT\" contracts/"],
    'foundry-poc-template': ["```solidity", "// SPDX-License-Identifier: MIT", "pragma solidity ^0.8.0;", "import \"forge-std/Test.sol\";", "import \"../src/VulnerableContract.sol\";", "contract ExploitTest is Test {", "VulnerableContract target;", "address attacker = makeAddr(\"attacker\");", "address victim = makeAddr(\"victim\");", "function setUp() public {", "// Fork mainnet at specific block", "vm.createSelectFork(\"mainnet\", BLOCK_NUMBER);", "// Deploy or load target", "target = VulnerableContract(TARGET_ADDRESS);", "// Fund accounts", "deal(address(token), attacker, INITIAL_BALANCE);", "deal(address(token), victim, VICTIM_BALANCE);", "function test_exploit() public {", "console.log(\"Attacker balance before:\", token.balanceOf(attacker));", "vm.startPrank(attacker);", "// Step 1: Setup conditions", "// Step 2: Execute exploit", "// Step 3: Verify impact", "vm.stopPrank();", "console.log(\"Attacker balance after:\", token.balanceOf(attacker));", "assertGt(token.balanceOf(attacker), INITIAL_BALANCE, \"Exploit failed\");"],
    'key-foundry-cheatcodes': ["```solidity", "vm.prank(address)           // next call from address", "vm.startPrank(address)      // all calls from address until stopPrank()", "vm.deal(address, amount)    // set ETH balance", "deal(token, address, amount) // set ERC20 balance", "vm.warp(timestamp)          // set block.timestamp", "vm.roll(blockNumber)        // set block.number", "vm.createSelectFork(\"mainnet\", blockNumber)  // fork mainnet", "vm.expectRevert(bytes)      // next call should revert", "vm.label(address, \"name\")   // label for trace output", "vm.assume(condition)        // fuzz: discard inputs where false"],
    'running-tests': ["```bash"],
    'run-specific-test': ["forge test --match-test test_exploit -vvvv"],
    'run-with-fork': ["forge test --match-test test_exploit -vvvv --fork-url $MAINNET_RPC"],
    'gas-report': ["forge test --gas-report"],
    'coverage': ["forge coverage --report summary"],
    'related-skills-chains': ["- **`meme-coin-audit`** \u2014 When the target is a meme coin / SPL token rather than a DeFi protocol. Workflow primitive: pre-dive kill signals diverge \u2014 this skill's \"TVL < $500K skip\" doesn't apply to meme coins where the rug check (mint authority, freeze authority, LP lock) is the entire audit; route to `meme-coin-audit` instead.", "- **`triage-validation`** \u2014 When a contract finding is ready to be filed on Immunefi. Workflow primitive: Immunefi has its own report format, but the impact-validated, chain-end-to-end discipline of `triage-validation` still applies; run the 7Q gate against the Foundry PoC before submitting.", "- **`report-writing`** \u2014 When writing the Immunefi report body. Workflow primitive: `report-writing`'s Immunefi template (with Foundry PoC, root cause code snippet, quantified economic impact) is the body skeleton this skill's findings feed into.", "- **`offensive-osint`** \u2014 When auditing a protocol's off-chain attack surface (frontend, admin API, RPC gateways). Workflow primitive: on-chain audit is this skill's job; any web2 component of the protocol (web-frontend, admin panel, indexer API) routes to `offensive-osint` for recon.", "- **`bb-methodology`** \u2014 When deciding whether to dive at all. Workflow primitive: PART 0 of `bb-methodology` confirms engagement (web3 bug bounty / private audit / smart-contract review); this skill's pre-dive kill signals replace the standard scoring rubric for that engagement type."],
    'operator-notes-claude-bughunter': [],
    'bug-classes-still-paying-in-2026': ["Flash-loan attacks remain top-paid on Immunefi (top 5 in 2024-2026 by bounty). The economic primitive \u2014 borrow $50M, manipulate price oracle, drain pool, repay \u2014 keeps reappearing because new protocols keep shipping with composability assumptions that don't hold under flash-loaned imbalance.", "Reentrancy IS still paying because new protocols keep shipping with ERC-777 / hooks / callbacks. Don't assume the class is dead \u2014 the 2023-2025 paid corpus contains 40+ reentrancy bugs against post-Checks-Effects-Interactions codebases (cross-function reentrancy, read-only reentrancy via view functions called during state-mid-flight).", "Oracle manipulation: still paid heavily but harder. Most projects use Chainlink price feeds now; the attack target is the SECONDARY oracle most projects also use (TWAP from a low-liquidity Uniswap V2 pair, the protocol's own internal oracle, a stale fallback path). Audit the failover chain, not just the primary feed."],
    'what-s-new-since-the-vendored-content-was-written': ["- **EIP-1153 (transient storage)** \u2014 introduced in 2024. New reentrancy classes: transient-storage reads cached across the same transaction can desync from persistent storage. Audit any `tload`/`tstore` usage for read-after-external-call.", "- **EIP-7702 (Pectra hard fork 2025)** \u2014 added EOA-to-smart-account upgrades. New ATO-like primitives via re-delegation: an EOA signed-once can delegate to a contract that the attacker controls, then signature replay across delegations.", "- **Account abstraction (ERC-4337 bundlers)** \u2014 paymaster sponsorship abuse and bundler griefing. Paymaster contracts that don't enforce strict sender allowlists drain on first call.", "- **ZK-rollup bridge bugs** \u2014 proof-replay across rollups, off-chain prover compromise, sequencer censorship leading to forced-inclusion edge cases.", "- **LST/LRT depeg dynamics** \u2014 liquid-staking and liquid-restaking tokens that assume 1:1 peg under loss conditions; oracle assumes peg, market reflects depeg, liquidation logic breaks."],
    'tool-stack-for-2026': ["Foundry remains the test framework. `forge test --gas-report --debug` for invariant testing; `forge fuzz` for property-based testing; `forge inspect` for storage-layout audits. Slither + Echidna for static + fuzz. Mythril for symbolic execution on smaller contracts. tenderly.co for forking + simulation (best UX for replicating attacks against mainnet state).", "For Solana: anchor framework, sealevel-attacks corpus (curated PoCs by anchor maintainers), soteria-sec / sec3 scanner. For Move (Aptos, Sui): move-prover, aptos-cli `aptos move test`.", "For cross-chain: hyperlane and LayerZero each have audit-tooling repos; bridge bugs require simulating both endpoints, not just one."],
    'where-pre-dive-kill-signals-matter': ["TVL under $500K isn't worth the audit time unless the bounty floor is high. Audit firm already covered it = low ROI unless you find what they missed \u2014 look at the audit-report scope-exclusion section for what they EXPLICITLY didn't audit (oracles, governance, off-chain components, frontend, the admin path).", "Multisig signers > 5 + timelock > 48h = low rug-pull risk; if your finding requires team-malicious assumptions, it's low-impact and likely out of scope per Immunefi's \"centralization risk\" exclusion. Read the program brief \u2014 most Immunefi programs explicitly downgrade or reject findings that assume admin malice."],
    'reporting-discipline': ["Immunefi requires Foundry PoC. Submission without PoC is auto-rejected. Submission with a PoC that requires manual setup (\"first deploy this, then call that\") usually gets downgraded \u2014 the PoC should be a single `forge test` invocation that proves the impact, with explicit `assertEq` on the drained balance / minted token / corrupted state.", "Severity claims must use Immunefi's severity matrix exactly; don't invent severities. The matrix gates on direct economic loss percentage of TVL \u2014 a critical against a $500K protocol pays differently than a critical against a $500M one. Read the program's specific severity assignment before claiming Critical."],
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