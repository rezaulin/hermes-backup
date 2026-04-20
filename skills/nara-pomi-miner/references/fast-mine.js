// Fast Miner — Reference Implementation
// Parallel proof generation with batched relay submission
// Full file at ~/nara-miner/src/fast-mine.js
//
// Key design decisions:
// - MAX_PARALLEL_PROOFS=3 for 4vcpu VPS (ZK proof is CPU-intensive, ~2-5s each)
// - Proof+submit in same batch (don't wait for all proofs before submitting)
// - 30s timeout per round (quests last 20-45s)
// - Pre-load all wallets at startup (avoid disk I/O during time-critical rounds)
// - Skip round if answer unsolvable or quest expired
// - Poll every 1-2s for new rounds

const { solveQuestion } = require('/root/nara-miner/src/solver.js');
// Full implementation at ~/nara-miner/src/fast-mine.js
