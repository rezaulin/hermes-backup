---
name: nara-pomi-miner
description: |
  Nara Chain PoMI (Proof of Machine Intelligence) multi-wallet automated mining skill.
  Use this skill when the user asks to mine NARA tokens, set up Nara Chain automation,
  generate Nara wallets, answer PoMI quests, consolidate NARA rewards, or build bots
  for the Nara blockchain. Covers: wallet generation, quest fetching, question solving,
  ZK proof generation, gasless relay submission, multi-wallet orchestration, and
  auto-consolidation of rewards to a main wallet.
version: 1.0.0
author: nara-miner-skill
tags: [nara, blockchain, mining, pomi, web3, solana, zk-proof, automation]
---

# Nara PoMI Miner Skill

## What is This

This skill enables AI agents to automate **PoMI (Proof of Machine Intelligence) mining** on Nara Chain — a Solana-compatible L1 blockchain where agents earn NARA tokens by solving on-chain quiz challenges verified with zero-knowledge proofs.

## When to Use

Trigger this skill when the user mentions any of:
- "mine NARA" / "nara mining" / "PoMI mining"
- "nara wallet" / "generate nara wallets"
- "nara quest" / "answer quest" / "solve quest"
- "consolidate NARA" / "transfer NARA"
- "nara bot" / "nara automation"
- "naracli" / "nara-sdk"
- Multi-wallet farming on Nara Chain

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    NARA PoMI MINER                        │
│                                                          │
│  ┌─────────┐   ┌──────────┐   ┌──────────┐   ┌───────┐ │
│  │ Wallet  │──▶│  Quest   │──▶│  ZK      │──▶│Submit │ │
│  │Generator│   │  Solver  │   │  Prover  │   │(Relay)│ │
│  └─────────┘   └──────────┘   └──────────┘   └───────┘ │
│       │                                          │       │
│       │              ┌───────────┐               │       │
│       └─────────────▶│Consolidate│◀──────────────┘       │
│                      │ → Main    │                       │
│                      └───────────┘                       │
└──────────────────────────────────────────────────────────┘
```

**Flow per round:**
1. Fetch quest (soal quiz on-chain)
2. Solve question (arithmetic, string manipulation, etc.)
3. Generate Groth16 ZK proof per wallet
4. Submit via relay (gasless) for each wallet
5. Periodically consolidate all rewards → main wallet

---

## Core Concepts

### Nara Chain
- Layer 1 blockchain, **forked from Solana**
- Native token: **NARA**
- Wallet standard: BIP39 mnemonic + Ed25519 (same as Solana)
- RPC Devnet: `https://devnet-api.nara.build/`
- RPC Mainnet: `https://mainnet-api.nara.build/`

### PoMI Mining
- System publishes quiz questions on-chain (math, string, logic)
- Agents compute the answer, generate a **Groth16 ZK proof**
- Proof is verified on-chain → NARA tokens rewarded instantly
- **First come, first served** — limited reward slots per round
- Contract: `Quest11111111111111111111111111111111111111`

### Gasless Relay
- Wallets with < 0.1 NARA can submit via relay (free)
- Relay URL: `https://quest-api.nara.build/`
- Reward still goes to the submitting wallet

### Staking (Competitive Mode)
- When reward slots hit system cap → staking required
- Stake requirement uses **parabolic decay**: high at start, drops over time
- Formula: `effective = stakeHigh - (stakeHigh - stakeLow) * (elapsed / decay)^2`

---

## Dependencies

```json
{
  "nara-sdk": "latest",
  "@solana/web3.js": "^1.95.0",
  "bip39": "^3.1.0",
  "ed25519-hd-key": "^1.3.0",
  "tweetnacl": "^1.0.3"
}
```

Required: **Node.js 20+**

---

## Key SDK Functions

All imports from `nara-sdk`:

### Wallet

```javascript
import { Keypair } from 'nara-sdk';
import * as bip39 from 'bip39';
import { derivePath } from 'ed25519-hd-key';

// Generate new wallet
const mnemonic = bip39.generateMnemonic();
const seed = await bip39.mnemonicToSeed(mnemonic);
const derived = derivePath("m/44'/501'/0'/0'", seed.toString('hex')).key;
const keypair = Keypair.fromSeed(derived);

// Save keypair
fs.writeFileSync('wallet.json', JSON.stringify(Array.from(keypair.secretKey)));

// Load keypair
const data = JSON.parse(fs.readFileSync('wallet.json', 'utf-8'));
const keypair = Keypair.fromSecretKey(new Uint8Array(data));

// Address
console.log(keypair.publicKey.toBase58());
```

### Quest Info

```javascript
import { getQuestInfo } from 'nara-sdk';
import { Connection } from '@solana/web3.js';

const connection = new Connection('https://devnet-api.nara.build/', 'confirmed');
const quest = await getQuestInfo(connection);

// quest.active        — boolean, is quest active
// quest.question      — string, question text
// quest.answerHash    — number[], on-chain answer hash
// quest.round         — string, round identifier
// quest.rewardPerWinner — number, reward per winner
// quest.remainingSlots  — number, remaining reward slots
// quest.timeRemaining   — number, seconds remaining
// quest.effectiveStakeRequirement — number, current stake needed
```

### Check Already Answered

```javascript
import { hasAnswered } from 'nara-sdk';

const answered = await hasAnswered(connection, keypair);
// true/false — whether this wallet has answered current round
```

### Generate ZK Proof

```javascript
import { generateProof } from 'nara-sdk';

const proof = await generateProof(
  answer,                    // string answer
  quest.answerHash,          // hash from quest info
  keypair.publicKey,         // wallet pubkey
  quest.round                // round (anti-replay)
);
// proof.solana — for on-chain submit
// proof.hex   — for relay submit
// THROWS if answer is wrong!
```

### Submit (Direct / On-chain)

```javascript
import { submitAnswer } from 'nara-sdk';

const { signature } = await submitAnswer(
  connection,
  keypair,
  proof.solana,
  'agent-name',    // optional
  'model-name'     // optional
);
```

### Submit (Relay / Gasless)

```javascript
import { submitAnswerViaRelay } from 'nara-sdk';

const { txHash } = await submitAnswerViaRelay(
  'https://quest-api.nara.build/',
  keypair.publicKey,
  proof.hex,
  'agent-name',    // optional
  'model-name'     // optional
);
```

### Check Reward

```javascript
import { parseQuestReward } from 'nara-sdk';

const reward = await parseQuestReward(connection, signature);
// reward.rewarded   — boolean
// reward.rewardNso  — reward amount
// reward.winner     — winner number
```

### Transfer NARA

```javascript
import {
  Connection, PublicKey, SystemProgram, Transaction,
  sendAndConfirmTransaction, LAMPORTS_PER_SOL
} from '@solana/web3.js';

const tx = new Transaction().add(
  SystemProgram.transfer({
    fromPubkey: keypair.publicKey,
    toPubkey: new PublicKey('DESTINATION_ADDRESS'),
    lamports: Math.floor(amount * LAMPORTS_PER_SOL),
  })
);
const sig = await sendAndConfirmTransaction(connection, tx, [keypair]);
```

### Staking

```javascript
import { stake, unstake, getStakeInfo } from 'nara-sdk';

await stake(connection, keypair, 5);         // stake 5 NARA
await unstake(connection, keypair, 5);       // unstake 5 NARA
const info = await getStakeInfo(connection, keypair.publicKey);
// info.amount, info.stakeRound
```

---

## CLI Reference (naracli)

Alternative to SDK — use CLI directly:

```bash
# Install
npm install -g naracli

# Wallet
npx naracli wallet create
npx naracli wallet import -m "mnemonic words..."
npx naracli address
npx naracli balance

# Config
npx naracli config set rpc-url https://devnet-api.nara.build/
npx naracli config set wallet /path/to/keypair.json

# Quest / Mining
npx naracli quest get                         # view question
npx naracli quest get --json                  # JSON format
npx naracli quest answer "answer"             # submit (direct)
npx naracli quest answer "answer" --relay     # submit (gasless)
npx naracli quest answer "answer" --stake     # auto-stake

# Transfer
npx naracli transfer <address> <amount>

# Staking
npx naracli quest stake <amount>
npx naracli quest unstake <amount>
npx naracli quest stake-info
```

---

## Question Solver Patterns

PoMI quest questions are quiz challenges that need to be answered. Support these patterns:

### Arithmetic
```
"What is 42 + 58?"           → "100"
"Calculate 15 * 3 - 7"       → "38"
"Compute 100 / 4"            → "25"
"Result of (5 + 3) * 2"      → "16"
```

### String Manipulation
```
"Reverse the string 'hello'"              → "olleh"
"'abc' repeated 3 times"                  → "abcabcabc"
"Convert 'hello' to uppercase"            → "HELLO"
"Length of 'nara chain'"                   → "10"
"Concatenate 'foo' and 'bar'"             → "foobar"
"Sort characters of 'dcba'"               → "abcd"
"Character at position 2 of 'hello'"      → "l"
"Substring of 'hello' from 1 to 3"        → "el"
"Replace 'a' with 'o' in 'banana'"        → "bonono"
"Count 'a' in 'banana'"                   → "3"
```

### Math Functions
```
"10th Fibonacci number"       → "55"
"Factorial of 6"              → "720"
"Convert 255 to hexadecimal"  → "ff"
"Convert 10 to binary"        → "1010"
"15 mod 4"                    → "3"
"2 to the power of 10"        → "1024"
"GCD of 12 and 8"             → "4"
"Absolute value of -42"       → "42"
"Sum of 1, 2, 3, 4, 5"       → "15"
"Maximum of 3, 7, 1, 9"      → "9"
```

### Logic / Boolean
```
"Is 'racecar' a palindrome?"  → "true"
"Is 'hello' a palindrome?"    → "false"
```

### Additional Quest Patterns (discovered through live testing on devnet, April 2026)

**⚠️ CRITICAL: Sort array answers must NOT include brackets!**
`"Sort [41, 57, 2, 28] in ascending order."` → `"2, 28, 41, 57"` (NOT `"[2, 28, 41, 57]"`)
Verified by comparing `computeAnswerHash()` with on-chain `quest.answerHash`.

```
"Sort the digits of 419 in ascending order."              → "149"
"Sort the digits of 419 in descending order."             → "941"
"Sort [41, 57, 2, 28] in ascending order."               → "2, 28, 41, 57"   ← NO BRACKETS
"Sort [50, 57, 2, 22] in descending order."              → "57, 50, 22, 2"   ← NO BRACKETS
"What is the LCM of 13 and 20?"                            → "260"
"Extract all letters from 'u0gh26'."                       → "ugh"
"Extract all digits from 'cr2yptocurren1cy'."              → "21"
"Count vowels in 'hello'"                                  → "2"
"Count consonants in 'hello'"                              → "3"
"Number of words in 'hello world'"                         → "2"
"Does 'piano' end with 'o'? Answer yes or no."             → "yes/no"
"Does string 'nara' end with 'ra'? Answer yes or no."      → "yes/no"   (matches with or without "the string")
"Does 'piano' start with 'pi'? Answer yes or no."          → "yes/no"
"Does string 'nara' start with 'na'? Answer yes or no."    → "yes/no"   (matches with or without "the string")
"Is 'hello' contained in 'say hello world'?"               → "yes/no"
"Does 'apple' contain 'krq'? Answer yes or no."            → "yes/no"   ← REVERSED syntax (subject/object flipped)
"What is the integer average (floor) of 70, 29, 59?"       → "52"
"Replace every 'i' in 'light' with 'a'."                   → "laght"
"Pad 'nfr' on the left with '0' to length 6."             → "000nfr"
"Pad 'nfr' on the right with '*' to length 6."            → "nfr***"
"Remove consecutive duplicate characters from 'qqfffrrr'." → "qfr"
"Remove all duplicate characters from 'abcabc'."           → "abc"
"What are the first 3 characters of 'whale'?"              → "wha"
"What are the last 3 characters of 'whale'?"               → "ale"
"What is the product of [1, 12, 9, 12]?"                   → "1296"
"Median of [37, 29, 25, 20, 23]"                           → "25"
"Sum of [49, 15, 29, 11, 72]" (array format)              → "176"
"Difference between 100 and 37"                            → "63"
"Square of 15" / "15 squared"                              → "225"
"Square root of 144"                                       → "12"
"Cube of 3" / "3 cubed"                                    → "27"
"Is 7 prime? Answer yes or no."                            → "yes/no"
"Is 4 even? Answer yes or no."                             → "yes/no"
"Is 5 odd? Answer yes or no."                              → "yes/no"
"What is 11 OR 2 (bitwise)?"                               → "11"
"What is 11 AND 2 (bitwise)?"                              → "2"
"What is 11 XOR 2 (bitwise)?"                              → "9"
"What is C(7, 2)? (combination)"                           → "21"
"What is P(7, 2)? (permutation)"                           → "42"
"Run-length encode 'fffdffffcc' (e.g., 'aabbc' -> 'a2b2c')." → "f3df4c2"
"Shift each letter in 'storm' forward by 13 positions (wrap around z to a)." → "fgbez"
"How many bits are needed to represent 682 in binary?"      → "10"
"Convert octal '2016' to decimal."                         → "1038"
"Convert decimal 1736 to octal."                           → "3310"
"Convert hexadecimal 'ff' to decimal."                     → "255"
"Convert binary '1010' to decimal."                        → "10"
"What is the maximum of [47, -65, -88, -31, -61, 49]?"    → "49"  ← handles negatives
"What is the minimum of [47, -65, -88, -31, -61, 49]?"    → "-88"
```

### Solver Implementation Strategy

```javascript
function solveQuestion(question) {
  // Higher priority = checked first. Most specific patterns before generic.
  const solvers = [
    // Arithmetic (most common)
    solveArithmetic,
    solveModulo,
    solvePower,
    solveFactorial,
    solveSquare,
    solveSquareRoot,
    solveCube,
    solveBitwise,

    // Array operations
    solveProduct,
    solveMedian,
    solveSumArray,
    solveSortArray,
    solveMinMax,
    solveSum,
    solveDifference,

    // Number theory
    solveGCD,
    solveLCM,
    solveFibonacci,
    solveIsPrime,
    solveEvenOdd,
    solveAbs,

    // String — sorting
    solveSortDigits,
    solveSortChars,

    // String — extraction
    solveExtractLetters,
    solveExtractDigits,
    solveFirstNChars,
    solveLastNChars,
    solveCharAt,
    solveSubstring,

    // String — transformation
    solveReverse,
    solveRepeat,
    solveUpperLower,
    solveReplace,
    solveReplaceEvery,
    solvePadLeft,
    solvePadRight,
    solveRemoveConsecutiveDups,
    solveRemoveAllDups,

    // String — queries
    solveLength,
    solveConcatenate,
    solveCountChars,
    solveCountVowels,
    solveCountConsonants,
    solveWordCount,

    // Yes/No questions
    solveEndsWith,
    solveStartsWith,
    solveContains,
    solvePalindrome,

    // Average
    solveFloorAverage,

    // Conversion
    solveHexConvert,
    solveBinaryConvert,

    // Fallback
    solveEvalExpression,
  ];

  for (const solver of solvers) {
    try {
      const result = solver(question);
      if (result !== null && result !== undefined) return String(result);
    } catch { /* next */ }
  }
  return null;
}
```

---

## Multi-Wallet Mining Pattern

### Generate N Wallets

```javascript
const wallets = [];
for (let i = 0; i < N; i++) {
  const mnemonic = bip39.generateMnemonic();
  const seed = await bip39.mnemonicToSeed(mnemonic);
  const derived = derivePath("m/44'/501'/0'/0'", seed.toString('hex')).key;
  const keypair = Keypair.fromSeed(derived);

  fs.writeFileSync(
    `wallets/wallet_${String(i).padStart(3,'0')}.json`,
    JSON.stringify(Array.from(keypair.secretKey))
  );

  wallets.push({
    index: i,
    keypair,
    address: keypair.publicKey.toBase58(),
    mnemonic,
  });
}

// Save index
fs.writeFileSync('wallets/index.json', JSON.stringify(
  wallets.map(w => ({
    index: w.index,
    address: w.address,
    mnemonic: w.mnemonic,
    file: `wallet_${String(w.index).padStart(3,'0')}.json`,
  })),
  null, 2
));
```

### Mining Loop — Critical Timing Pattern

**Quests last only 20-45 seconds.** The entire fetch→solve→proof→submit cycle must complete within this window. ZK proof generation is CPU-intensive (~2-5 seconds per proof on 4vcpu).

**Optimal strategy:** Process wallets in small batches (MAX_PARALLEL_PROOFS=3 on 4vcpu/8GB VPS). Each batch: generate proofs in parallel → submit immediately. Skip if 30s elapsed.

```javascript
const MAX_PARALLEL_PROOFS = 3; // tune based on CPU cores

while (true) {
  const quest = await getQuestInfo(connection);
  if (!quest.active || quest.expired || quest.round === lastRound) {
    await sleep(2000);
    continue;
  }
  lastRound = quest.round;
  const startTime = Date.now();

  const answer = solveQuestion(quest.question);
  if (!answer) { await sleep(2000); continue; }

  // Process in batches — each batch does proof+submit together
  for (let i = 0; i < wallets.length; i += MAX_PARALLEL_PROOFS) {
    const batch = wallets.slice(i, i + MAX_PARALLEL_PROOFS);
    const results = await Promise.allSettled(
      batch.map(async (w) => {
        const proof = await generateProof(
          String(answer), quest.answerHash, w.keypair.publicKey, quest.round
        );
        // proof.hex is ZkProofHex {proofA: string, proofB: string, proofC: string}
        // Pass directly to submitAnswerViaRelay — SDK handles serialization
        return submitAnswerViaRelay(RELAY_URL, w.keypair.publicKey, proof.hex, agentName, modelName);
      })
    );
    // Check elapsed — don't submit to expired quest
    if (Date.now() - startTime > 30000) break;
  }
}
```

### Consolidation Pattern

```javascript
async function consolidateAll(wallets, mainAddress) {
  const mainPubkey = new PublicKey(mainAddress);

  for (const w of wallets) {
    const balance = await connection.getBalance(w.keypair.publicKey);
    const naraBal = balance / LAMPORTS_PER_SOL;

    if (naraBal < 0.01) continue;

    const lamports = Math.floor((naraBal - 0.001) * LAMPORTS_PER_SOL);
    const tx = new Transaction().add(
      SystemProgram.transfer({
        fromPubkey: w.keypair.publicKey,
        toPubkey: mainPubkey,
        lamports,
      })
    );
    await sendAndConfirmTransaction(connection, tx, [w.keypair]);
  }
}
```

---

## Configuration Reference

| Key | Default | Description |
|-----|---------|-------------|
| `MAIN_WALLET` | (required) | Main wallet address for consolidation |
| `RPC_URL` | `https://devnet-api.nara.build/` | RPC endpoint |
| `RELAY_URL` | `https://quest-api.nara.build/` | Gasless relay endpoint |
| `TOTAL_WALLETS` | 300 | Number of wallets to generate |
| `CONCURRENCY` | 10 | Parallel wallet submissions |
| `USE_RELAY` | true | Use gasless relay mode |
| `POLL_INTERVAL_MS` | 5000 | Quest poll interval (ms) |
| `CONSOLIDATE_AFTER_ROUNDS` | 5 | Auto-consolidate every N rounds |
| `CONSOLIDATE_THRESHOLD` | 0.01 | Min balance to trigger transfer |

---

## Actual Setup (Verified)

```bash
# 1. Create project
mkdir -p ~/nara-miner/wallets && cd ~/nara-miner
npm init -y

# 2. Install dependencies — tsx is REQUIRED because nara-sdk ships raw TypeScript
npm install nara-sdk @solana/web3.js bip39 ed25519-hd-key tweetnacl p-limit@3
npm install tsx --save-dev

# 3. Create source files (src/config.js, src/solver.js, src/generate.js, src/miner.js, src/consolidate.js)
#    — see project at ~/nara-miner/ for reference implementation

# 4. All scripts MUST use tsx, not node (nara-sdk is .ts ESM)
# package.json scripts:
#   "generate": "tsx src/generate.js"
#   "mine": "tsx src/miner.js"
#   "consolidate": "tsx src/consolidate.js"

# 5. Generate wallets
npx tsx src/generate.js 5

# 6. Test mine one round
npx tsx src/test-mine.js

# 7. Run in background
screen -S nara
npx tsx src/miner.js
# Ctrl+A D to detach

# Or use pm2:
pm2 start tsx --name nara -- src/miner.js
pm2 logs nara
```

---

## Error Handling Best Practices

1. **Proof generation fails** → answer is wrong, skip wallet this round
2. **Relay timeout** → retry 1x, then skip wallet
3. **RPC error** → exponential backoff, retry
4. **No active quest** → poll every 5 seconds
5. **All slots filled** → skip round, wait for next
6. **Consolidation fails** → log error, continue to next wallet
7. **Already answered** → skip wallet (checked via `hasAnswered`)

---

## Pitfalls

### nara-sdk is TypeScript ESM — Cannot use plain `node`
**nara-sdk** ships as raw `.ts` files (not pre-compiled JS). Node.js v22's experimental `--experimental-strip-types` explicitly refuses to strip types from `node_modules/`. You MUST use **tsx** as the runtime:
```bash
npm install tsx --save-dev
npx tsx src/miner.js    # NOT: node src/miner.js
```
Error if you forget: `ERR_UNSUPPORTED_NODE_MODULES_TYPE_STRIPPING`

### nara-sdk imports from `@solana/web3.js` internally
The SDK re-exports `Keypair`, `PublicKey`, `Transaction` from `@solana/web3.js`. You can import from either location, but `@solana/web3.js` must be installed as a direct dependency (it's a peer dep of nara-sdk).

### `generateProof()` throws if answer is wrong
Always wrap in try/catch. If it throws with "Assert Failed. Error in template AnswerProof", the answer doesn't match the on-chain hash. The answer might be correct but the quest may have changed rounds between fetch and proof generation.

### `proof.hex` is an OBJECT, not a string
`proof.hex` returns `ZkProofHex = { proofA: string, proofB: string, proofC: string }` — three hex strings (proofA=128chars, proofB=256chars, proofC=128chars). Pass it directly to `submitAnswerViaRelay` — the SDK extracts `proofA`/`proofB`/`proofC` internally. Do NOT serialize to JSON or convert to a single hex string.

### Answer format verification with `computeAnswerHash`
Always verify answer format BEFORE attempting proof generation:
```javascript
import { computeAnswerHash } from 'nara-sdk';
const ourHash = await computeAnswerHash(answer);
const match = JSON.stringify(quest.answerHash) === JSON.stringify(ourHash);
if (!match) {
  // Try format variants: without brackets, without spaces, lowercase, etc.
  // See "Sort array" pitfall below
}
```
This prevents wasted ZK proof computation (~2-5s) on wrong-format answers.

### Sort array answers: NO brackets, NO square brackets
The on-chain answerHash for array-sorting questions uses format `"2, 28, 41, 57"` NOT `"[2, 28, 41, 57]"`. The solver must return `nums.join(', ')` not `[${nums.join(', ')}]`. Verified by comparing `computeAnswerHash()` against `quest.answerHash`. Other array operations (product, sum, median, min/max) may use the bracket format — verify each.

### Regex patterns must handle negative numbers
Quest arrays can contain negatives: `"maximum of [47, -65, -88, -31, -61, 49]"`. Regex `[\d,\s]+` won't match negative signs. Use `[-?\d,\s]+` instead.

### Relay verification failures — possible upstream issue (April 2026)
As of April 2026, the devnet relay (`https://quest-api.nara.build/submit-answer`) returns `"ZK proof verification failed"` (code: `InvalidProof`) consistently — even when using the official `naracli` tool. This is NOT a code bug. Possible causes:
- On-chain verification key mismatch with SDK circuit
- Relay service configuration issue
- The relay may be undergoing maintenance

**Workaround:** Use on-chain direct submission (requires NARA for gas) or wait for relay fix. Always verify with `naracli quest answer "X" --relay` before deploying automated miner.

### naracli defaults to MAINNET RPC
The official `naracli` defaults to `https://mainnet-api.nara.build/`. When using naracli for testing, always pass `--rpc-url https://devnet-api.nara.build/` explicitly. Mainnet quests have staking requirements (700+ NARA) and are trivia-based (not math/string).

### Each wallet can only answer ONCE per round
Check `hasAnswered()` before generating a proof. Missing this wastes ZK proof computation time.

### Quest timing is the #1 failure mode
Quests last 20-45 seconds. If "ZK proof verification failed" appears from the relay, the quest likely expired between proof generation and relay submission — NOT because the answer is wrong. Verify answer correctness with `computeAnswerHash(answer)` matching `quest.answerHash`. Use small parallel batches (3 on 4vcpu) for speed.

### Parallel ZK proofs are CPU-bound
Each `generateProof()` call runs a Groth16 prover (~2-5s on 4vcpu). Running 10+ in parallel will cause timeouts. Optimal batch size: CPU cores / 2. For 4vcpu → MAX_PARALLEL_PROOFS=2-3.

### DeP0040 punycode warning
Node.js 22 shows `(node:xxx) [DEP0040] DeprecationWarning: The 'punycode' module is deprecated`. This is harmless — comes from `@solana/web3.js` dependency chain. Can be suppressed with `--no-deprecation` flag if running as daemon.

### pm2 with tsx
Don't use `pm2 start tsx --name nara -- src/miner.js`. Instead use:
```bash
pm2 start --name nara -- npx tsx src/miner.js
```
Or install tsx globally: `npm install -g tsx` then `pm2 start --name nara -- tsx src/miner.js`

## Important Notes

- PoMI is currently live on **Devnet** only
- First come, first served — speed is critical
- Relay mode = gasless, new wallets can submit immediately
- ZK proof `generateProof()` THROWS if answer is wrong
- `round` parameter in proof prevents cross-round replay
- Each wallet can only answer ONCE per round
- Mnemonic backup is critical — lost = funds gone forever
- Reserve 0.001 NARA per wallet for tx fees during consolidation
