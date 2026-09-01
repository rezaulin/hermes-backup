#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/lattice-crypto-attacks

Skill: SKILL: Lattice-Based Cryptanalysis — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-lattice-crypto-attacks.py --help
      python hack-skills-lattice-crypto-attacks.py --list
      python hack-skills-lattice-crypto-attacks.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/lattice-crypto-attacks'
TITLE = 'SKILL: Lattice-Based Cryptanalysis — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: lattice-crypto-attacks", "description: >-", "Lattice-based cryptanalysis playbook. Use when attacking RSA via Coppersmith", "small roots, recovering DSA/ECDSA nonces from bias, solving knapsack", "problems, or applying LLL/BKZ reduction to cryptographic constructions."],
    'skill-lattice-based-cryptanalysis-expert-attack-playbook': [],
    '0-related-routing': ["- [rsa-attack-techniques](../rsa-attack-techniques/SKILL.md) for RSA-specific attacks that use lattice methods (Coppersmith, Boneh-Durfee)", "- [symmetric-cipher-attacks](../symmetric-cipher-attacks/SKILL.md) for LCG state recovery via lattice", "- [classical-cipher-analysis](../classical-cipher-analysis/SKILL.md) when lattice methods apply to classical cipher analysis"],
    'quick-application-guide': [],
    '1-lattice-fundamentals': [],
    '1-1-definitions': ["A **lattice** L is the set of all integer linear combinations of basis vectors:", "L = { a\u2081\u00b7b\u2081 + a\u2082\u00b7b\u2082 + ... + a\u2099\u00b7b\u2099 | a\u1d62 \u2208 \u2124 }", "where b\u2081, ..., b\u2099 are linearly independent vectors in \u211d\u1d50.", "**Key problems**:", "- **SVP** (Shortest Vector Problem): Find the shortest non-zero vector in L", "- **CVP** (Closest Vector Problem): Given target t, find v \u2208 L closest to t", "- **SVP is NP-hard** in general, but LLL finds an approximately short vector in polynomial time"],
    '1-2-lattice-quality-metrics': ["Determinant: det(L) = |det(B)| where B is the basis matrix", "Gaussian heuristic: shortest vector \u2248 \u221a(n/(2\u03c0e)) \u00b7 det(L)^(1/n)"],
    '2-lll-algorithm': [],
    '2-1-what-lll-does': ["Takes a lattice basis B and produces a **reduced basis** B' where:", "- Vectors are nearly orthogonal", "- First vector is approximately short (within 2^((n-1)/2) factor of SVP)", "- Runs in polynomial time: O(n^5 \u00b7 d \u00b7 log\u00b3 B) where d = dimension, B = max entry size"],
    '2-2-sagemath-usage': ["```python"],
    'sagemath': ["M = matrix(ZZ, [", "[1, 0, 0, large_value_1],", "[0, 1, 0, large_value_2],", "[0, 0, 1, large_value_3],", "[0, 0, 0, modulus],", "L = M.LLL()"],
    'short-vectors-in-l-reveal-the-solution': ["short_vector = L[0]  # first row is typically shortest"],
    '2-3-python-fpylll': ["```python", "from fpylll import IntegerMatrix, LLL", "n = 4", "A = IntegerMatrix(n, n)"],
    'fill-matrix-a': ["A[0] = (1, 0, 0, large_value_1)", "A[1] = (0, 1, 0, large_value_2)", "A[2] = (0, 0, 1, large_value_3)", "A[3] = (0, 0, 0, modulus)", "LLL.reduction(A)", "print(A[0])  # shortest vector"],
    '3-bkz-block-korkine-zolotarev': [],
    '3-1-comparison-with-lll': [],
    '3-2-usage': ["```python"],
    'sagemath': ["M = matrix(ZZ, [...])", "L = M.BKZ(block_size=20)  # \u03b2 = 20"],
    'fpylll': ["from fpylll import BKZ", "BKZ.reduction(A, BKZ.Param(block_size=20))", "Rule of thumb: start with LLL, increase to BKZ if needed. BKZ block size 20-40 is usually sufficient for CTF."],
    '4-coppersmith-s-method': [],
    '4-1-univariate-case': ["Given f(x) \u2261 0 (mod N) with small root |x\u2080| < X, find x\u2080.", "**Bound**: X < N^(1/d) where d = degree of f.", "```python"],
    'sagemath-built-in-small-roots': ["N = ...", "R.<x> = PolynomialRing(Zmod(N))", "f = x^3 + a*x^2 + b*x + c  # known polynomial", "roots = f.small_roots(X=2^100, beta=1.0, epsilon=1/30)", "**Parameters**:", "- `X`: upper bound on the root", "- `beta`: N = p^beta (beta=1.0 for modular root of N itself; beta=0.5 for root mod unknown factor p \u2248 \u221aN)", "- `epsilon`: smaller = better results but slower (try 1/30 to 1/100)"],
    '4-2-stereotyped-message-attack-rsa': ["```python"],
    'sagemath': ["n, e, c = ...  # RSA parameters", "known_msb = ...  # known upper portion of message", "R.<x> = PolynomialRing(Zmod(n))", "f = (known_msb + x)^e - c"],
    'x-represents-the-unknown-lower-bits': ["X = 2^(unknown_bit_count)", "roots = f.small_roots(X=X, beta=1.0)", "if roots:", "m = known_msb + int(roots[0])"],
    '4-3-partial-key-exposure-factor-p': ["Known MSBs of p: `p = p_known + x` where x is small.", "```python"],
    'sagemath': ["n = ...", "p_known = ...  # known upper bits of p", "R.<x> = PolynomialRing(Zmod(n))", "f = p_known + x", "roots = f.small_roots(X=2^unknown_bits, beta=0.5)"],
    'beta-0-5-because-p-n': ["if roots:", "p = p_known + int(roots[0])", "q = n // p"],
    '4-4-multivariate-coppersmith-howgrave-graham': ["For f(x, y) \u2261 0 (mod N):", "- No polynomial-time algorithm guaranteed", "- Heuristic methods work in practice", "- Used in Boneh-Durfee for RSA small d", "```python"],
    'sagemath-boneh-durfee': [],
    'e-d-1-mod-phi-where-phi-p-1-q-1': [],
    'rewrite-e-d-1-k-n-1-p-q': [],
    'let-x-k-y-p-q-both-small-relative-to-n': ["R.<x, y> = PolynomialRing(ZZ)", "A = (n + 1) // 2", "f = 1 + x * (A + y)  # mod e"],
    'build-shift-polynomials-and-construct-lattice': [],
    'apply-lll-to-find-small-x-y': [],
    '5-hidden-number-problem-hnp-dsa-ecdsa-nonce-recovery': [],
    '5-1-problem-statement': ["Given: signatures (r\u1d62, s\u1d62) where nonces k\u1d62 have known bias (leaked MSBs or LSBs).", "DSA equation: `s = k\u207b\u00b9(H(m) + xr) mod q`", "Rearranged: `k = s\u207b\u00b9(H(m) + xr) mod q`", "If partial bits of k are known: reduces to CVP on a lattice."],
    '5-2-attack-setup': ["```python"],
    'sagemath': ["def ecdsa_nonce_attack(signatures, q, known_bits, bit_position='msb'):", "signatures: list of (r, s, hash, known_nonce_bits)", "q: curve order", "known_bits: number of known bits per nonce", "n = len(signatures)", "B = 2^(q.nbits() - known_bits)  # bound on unknown part", "M = matrix(QQ, n + 2, n + 2)", "for i in range(n):", "r_i, s_i, h_i, a_i = signatures[i]", "t_i = Integer(inverse_mod(s_i, q) * r_i % q)", "u_i = Integer(inverse_mod(s_i, q) * h_i % q)", "M[i, i] = q", "M[n, i] = t_i", "M[n+1, i] = u_i - a_i  # a_i = known nonce bits", "M[n, n] = B / q", "M[n+1, n+1] = B", "L = M.LLL()", "for row in L:", "x_candidate = Integer(row[n] * q / B) % q", "if verify_private_key(x_candidate, signatures[0], q):", "return x_candidate", "return None"],
    '5-3-practical-nonce-bias-sources': ["For **reused nonce** (simplest case):", "```python", "def ecdsa_reused_nonce(r, s1, s2, h1, h2, q):", "\"\"\"Recover private key when nonce k is reused.\"\"\"", "k = ((h1 - h2) * inverse_mod(s1 - s2, q)) % q", "x = ((s1 * k - h1) * inverse_mod(r, q)) % q", "return x, k"],
    '6-knapsack-subset-sum-attacks': [],
    '6-1-low-density-attack': ["Knapsack: given weights a\u2081,...,a\u2099 and target S, find x\u2081,...,x\u2099 \u2208 {0,1} such that \u03a3x\u1d62a\u1d62 = S.", "**Density** d = n / max(log\u2082 a\u1d62). If d < 0.9408, lattice attack works.", "```python"],
    'sagemath': ["def knapsack_lattice(weights, target):", "\"\"\"Solve subset sum via LLL lattice attack.\"\"\"", "n = len(weights)", "N = ceil(sqrt(n) / 2)  # scaling factor", "M = matrix(ZZ, n + 1, n + 1)", "for i in range(n):", "M[i, i] = 1", "M[i, n] = N * weights[i]", "M[n, n] = N * target", "M2 = matrix(ZZ, n + 1, n + 2)", "for i in range(n):", "M2[i, i] = 1", "M2[i, n + 1] = N * weights[i]", "M2[n, n] = 1", "M2[n, n + 1] = N * (-target)", "L = M2.LLL()", "for row in L:", "if all(v in (0, 1) for v in row[:n]):", "solution = list(row[:n])", "if sum(solution[i] * weights[i] for i in range(n)) == target:", "return solution", "return None"],
    '7-ntru-cryptanalysis': [],
    '7-1-ntru-lattice': ["```python"],
    'sagemath': ["def ntru_lattice_attack(h, q, N):", "Construct NTRU lattice for key recovery.", "h = public key polynomial (mod q)", "q = modulus", "N = dimension", "H = matrix(ZZ, N, N)", "for i in range(N):", "for j in range(N):", "H[i, j] = h[(j - i) % N]", "M = block_matrix([", "[q * identity_matrix(N), zero_matrix(N)],", "[H, identity_matrix(N)]", "L = M.LLL()", "for row in L:", "f = vector(row[:N])", "g = vector(row[N:])", "if f.norm() < q and g.norm() < q:", "return f, g", "return None"],
    '8-constructing-attack-lattices-methodology': [],
    '8-1-general-recipe': ["1. Express the cryptographic problem as:", "\"Find small x such that f(x) \u2261 0 (mod N)\"", "or \"Find x close to target t in some lattice L\"", "2. Choose lattice type:", "\u251c\u2500 Polynomial lattice \u2192 Coppersmith-style", "\u251c\u2500 Modular lattice \u2192 HNP-style CVP", "\u2514\u2500 Knapsack lattice \u2192 subset sum / CJLOSS", "3. Determine dimensions:", "\u2514\u2500 More dimensions = better approximation but slower", "4. Set scaling factors:", "\u2514\u2500 Balance the rows so short vector has roughly equal entries", "\u2514\u2500 Common: multiply by N/X where X is the root bound", "5. Apply reduction:", "\u251c\u2500 LLL first (fast, usually sufficient)", "\u2514\u2500 BKZ if LLL fails (increase block size: 20, 30, 40)", "6. Extract solution:", "\u2514\u2500 Check reduced basis rows for valid solutions"],
    '8-2-embedding-technique-cvp-svp': ["Transform CVP into SVP by embedding the target into the lattice:", "```python"],
    'sagemath': ["def cvp_to_svp(basis_matrix, target, scale=1):", "\"\"\"Convert CVP to SVP via Kannan's embedding.\"\"\"", "n = basis_matrix.nrows()", "m = basis_matrix.ncols()", "M = matrix(ZZ, n + 1, m + 1)", "for i in range(n):", "for j in range(m):", "M[i, j] = basis_matrix[i, j]", "M[i, m] = 0", "for j in range(m):", "M[n, j] = target[j]", "M[n, m] = scale  # scaling factor (try 1, then adjust)", "L = M.LLL()", "for row in L:", "if abs(row[m]) == scale:", "return vector(target) - vector(row[:m]) * (row[m] // abs(row[m]))", "return None"],
    '8-3-dimension-selection-guide': [],
    '9-decision-tree': ["Lattice approach needed \u2014 which construction?", "\u251c\u2500 RSA-related?", "\u2502  \u251c\u2500 Small unknown part of message \u2192 Coppersmith univariate", "\u2502  \u2502  \u2514\u2500 Check: unknown_bits < n_bits / e", "\u2502  \u251c\u2500 Partial factor knowledge \u2192 Coppersmith mod p", "\u2502  \u2502  \u2514\u2500 Use beta=0.5, X=2^unknown_bits", "\u2502  \u251c\u2500 Small private exponent d \u2192 Boneh-Durfee", "\u2502  \u2502  \u2514\u2500 Check: d < N^0.292", "\u2502  \u2514\u2500 Multiple related equations \u2192 multivariate Coppersmith", "\u251c\u2500 DSA/ECDSA-related?", "\u2502  \u251c\u2500 Reused nonce \u2192 direct algebraic recovery (no lattice needed)", "\u2502  \u251c\u2500 Partial nonce leakage \u2192 HNP \u2192 CVP lattice", "\u2502  \u2502  \u2514\u2500 Need enough signatures: n \u2265 q_bits / leaked_bits", "\u2502  \u2514\u2500 Nonce bias \u2192 statistical HNP \u2192 larger lattice", "\u251c\u2500 Knapsack / subset sum?", "\u2502  \u251c\u2500 Low density (d < 0.9408) \u2192 CJLOSS lattice attack", "\u2502  \u251c\u2500 High density \u2192 lattice attack unlikely to work", "\u2502  \u2514\u2500 Super-increasing \u2192 greedy algorithm (no lattice needed)", "\u251c\u2500 LCG / PRNG?", "\u2502  \u251c\u2500 Full outputs known \u2192 algebraic recovery (no lattice)", "\u2502  \u251c\u2500 Truncated outputs \u2192 CVP on recurrence lattice", "\u2502  \u2514\u2500 Unknown modulus \u2192 use GCD of output differences", "\u251c\u2500 NTRU?", "\u2502  \u2514\u2500 Build circulant lattice \u2192 LLL/BKZ for short key vector", "\u2514\u2500 Custom problem?", "\u251c\u2500 Express as \"find small root of polynomial mod N\" \u2192 Coppersmith", "\u251c\u2500 Express as \"find lattice point close to target\" \u2192 CVP", "\u251c\u2500 Express as \"find short vector in lattice\" \u2192 SVP / LLL", "\u2514\u2500 If none fit \u2192 probably not a lattice problem"],
    '10-common-pitfalls': [],
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