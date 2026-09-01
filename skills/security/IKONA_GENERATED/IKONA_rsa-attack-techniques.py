#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/rsa-attack-techniques

Skill: SKILL: RSA Attack Techniques — Expert Cryptanalysis Playbook
Desc : >-

Run:  python hack-skills-rsa-attack-techniques.py --help
      python hack-skills-rsa-attack-techniques.py --list
      python hack-skills-rsa-attack-techniques.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/rsa-attack-techniques'
TITLE = 'SKILL: RSA Attack Techniques — Expert Cryptanalysis Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: rsa-attack-techniques", "description: >-", "RSA attack playbook for CTF and real-world cryptanalysis. Use when given", "RSA parameters (n, e, c) and need to recover plaintext by exploiting", "weak keys, small exponents, shared factors, or padding oracles."],
    'skill-rsa-attack-techniques-expert-cryptanalysis-playbook': [],
    '0-related-routing': ["- [lattice-crypto-attacks](../lattice-crypto-attacks/SKILL.md) for deep lattice theory behind Coppersmith/Boneh-Durfee", "- [hash-attack-techniques](../hash-attack-techniques/SKILL.md) when RSA signature forgery involves hash weaknesses", "- [symmetric-cipher-attacks](../symmetric-cipher-attacks/SKILL.md) when RSA protects a symmetric key (hybrid encryption)"],
    'advanced-reference': ["Also load [RSA_ATTACK_CATALOG.md](./RSA_ATTACK_CATALOG.md) when you need:", "- Detailed SageMath/Python implementation for each attack", "- Step-by-step mathematical derivation", "- Edge cases and failure conditions per attack"],
    'quick-attack-selection': [],
    '1-factorization-attacks': [],
    '1-1-direct-factorization-small-n': ["```python", "from sympy import factorint", "n = 0x...  # small modulus", "factors = factorint(n)", "p, q = list(factors.keys())", "**When**: n < ~512 bits, or known to be in factordb."],
    '1-2-fermat-s-factorization': ["Works when p and q are close together: |p - q| is small.", "```python", "from gmpy2 import isqrt, is_square", "def fermat_factor(n):", "a = isqrt(n) + 1", "while True:", "b2 = a * a - n", "if is_square(b2):", "b = isqrt(b2)", "return (a + b, a - b)", "a += 1"],
    '1-3-pollard-s-p-1': ["Works when p-1 has only small prime factors (B-smooth).", "```python", "from gmpy2 import gcd", "def pollard_p1(n, B=2**20):", "a = 2", "for j in range(2, B):", "a = pow(a, j, n)", "d = gcd(a - 1, n)", "if 1 < d < n:", "return d", "return None"],
    '1-4-batch-gcd-multiple-n-share-a-factor': ["```python", "from math import gcd", "from functools import reduce", "def batch_gcd(moduli):", "\"\"\"Find shared factors among multiple RSA moduli.\"\"\"", "product = reduce(lambda a, b: a * b, moduli)", "results = {}", "for i, n in enumerate(moduli):", "remainder = product // n", "g = gcd(n, remainder)", "if g != 1 and g != n:", "results[i] = (g, n // g)", "return results"],
    '2-small-exponent-attacks': [],
    '2-1-cube-root-attack-e-3-small-m': ["If m^e < n (no modular reduction occurred), simply take the e-th root.", "```python", "from gmpy2 import iroot", "c = 0x...  # ciphertext", "e = 3", "m, exact = iroot(c, e)", "if exact:", "print(f\"Plaintext: {bytes.fromhex(hex(m)[2:])}\")"],
    '2-2-hastad-broadcast-attack': ["Same message encrypted with same small e under different moduli (n\u2081, n\u2082, ..., n\u2091).", "```python", "from sympy.ntheory.modular import crt", "from gmpy2 import iroot"],
    'e-3-three-ciphertexts-under-three-different-n': ["n_list = [n1, n2, n3]", "c_list = [c1, c2, c3]"],
    'crt-find-x-such-that-x-ci-mod-ni-for-all-i': ["r, M = crt(n_list, c_list)", "m, exact = iroot(r, 3)", "assert exact"],
    '2-3-related-message-attack-franklin-reiter': ["Two messages related by a known linear function: m\u2082 = a\u00b7m\u2081 + b. Same n and e.", "```python"],
    'sagemath': ["def franklin_reiter(n, e, c1, c2, a, b):", "R.<x> = PolynomialRing(Zmod(n))", "f1 = x^e - c1", "f2 = (a*x + b)^e - c2", "return Integer(n - gcd(f1, f2).coefficients()[0])"],
    '3-large-e-small-d-attacks': [],
    '3-1-wiener-s-attack-continued-fractions': ["When d < n^(1/4) / 3, the continued fraction expansion of e/n reveals d.", "```python", "def wiener_attack(e, n):", "\"\"\"Recover d when d is small via continued fractions.\"\"\"", "cf = continued_fraction(e, n)", "convergents = get_convergents(cf)", "for k, d in convergents:", "if k == 0:", "continue", "phi_candidate = (e * d - 1) // k", "s = n - phi_candidate + 1", "discriminant = s * s - 4 * n", "if discriminant >= 0:", "from gmpy2 import isqrt, is_square", "if is_square(discriminant):", "return d", "return None", "def continued_fraction(a, b):", "cf = []", "while b:", "cf.append(a // b)", "a, b = b, a % b", "return cf", "def get_convergents(cf):", "convergents = []", "h_prev, h_curr = 0, 1", "k_prev, k_curr = 1, 0", "for a in cf:", "h_prev, h_curr = h_curr, a * h_curr + h_prev", "k_prev, k_curr = k_curr, a * k_curr + k_prev", "convergents.append((h_curr, k_curr))", "return convergents"],
    '3-2-boneh-durfee-attack-lattice-based': ["Extends Wiener: works when d < n^0.292. Uses lattice reduction (LLL/BKZ).", "**Use SageMath implementation** \u2014 see [lattice-crypto-attacks](../lattice-crypto-attacks/SKILL.md) for theory."],
    '4-coppersmith-s-method': [],
    '4-1-stereotyped-message': ["Known portion of plaintext, unknown part is small.", "```python"],
    'sagemath': ["n = ...", "e = 3", "c = ...", "known_prefix = b\"flag{\" + b\"\\x00\" * 27  # known prefix, unknown suffix", "known_int = int.from_bytes(known_prefix, 'big')", "R.<x> = PolynomialRing(Zmod(n))", "f = (known_int + x)^e - c", "roots = f.small_roots(X=2^(27*8), beta=1.0)", "if roots:", "m = known_int + int(roots[0])", "print(bytes.fromhex(hex(m)[2:]))"],
    '4-2-partial-key-exposure': ["Known MSB or LSB of p \u2192 recover full p via Coppersmith.", "```python"],
    'sagemath-known-msb-of-p': ["p_msb = ...  # known upper bits of p", "R.<x> = PolynomialRing(Zmod(n))", "f = p_msb + x", "roots = f.small_roots(X=2^unknown_bits, beta=0.5)", "if roots:", "p = p_msb + int(roots[0])", "q = n // p"],
    '5-common-modulus-attack': ["Two ciphertexts of same message under same n but different e\u2081, e\u2082 where gcd(e\u2081, e\u2082) = 1.", "```python", "from gmpy2 import gcd, invert", "def common_modulus(n, e1, e2, c1, c2):", "\"\"\"Recover m when same message encrypted with two different e under same n.\"\"\"", "assert gcd(e1, e2) == 1", "_, s1, s2 = extended_gcd(e1, e2)  # s1*e1 + s2*e2 = 1", "if s1 < 0:", "c1 = invert(c1, n)", "s1 = -s1", "if s2 < 0:", "c2 = invert(c2, n)", "s2 = -s2", "m = (pow(c1, s1, n) * pow(c2, s2, n)) % n", "return m", "def extended_gcd(a, b):", "if a == 0:", "return b, 0, 1", "g, x, y = extended_gcd(b % a, a)", "return g, y - (b // a) * x, x"],
    '6-oracle-attacks': [],
    '6-1-lsb-oracle-parity-oracle': ["An oracle reveals whether decrypted message is even or odd.", "```python", "from gmpy2 import mpz", "def lsb_oracle_attack(n, e, c, oracle_func):", "\"\"\"Decrypt using LSB (parity) oracle. oracle_func(c) returns m%2.\"\"\"", "from fractions import Fraction", "lo, hi = Fraction(0), Fraction(n)", "for _ in range(n.bit_length()):", "c = (c * pow(2, e, n)) % n  # multiply plaintext by 2", "if oracle_func(c) == 0:", "hi = (lo + hi) / 2", "else:", "lo = (lo + hi) / 2", "return int(hi)"],
    '6-2-bleichenbacher-pkcs-1-v1-5-padding-oracle': ["Given a padding validity oracle (valid/invalid PKCS#1 v1.5), iteratively narrow down the plaintext range.", "**Complexity**: O(2^16) oracle queries per byte on average.", "**Target**: TLS implementations returning different errors for valid/invalid padding."],
    '6-3-manger-s-attack-pkcs-1-oaep': ["Similar to Bleichenbacher but for OAEP padding. Exploits oracle that distinguishes whether the first byte after unpadding is 0x00."],
    '7-rsa-crt-fault-attack': ["If RSA-CRT signing produces a faulty signature (fault in one CRT half):", "```python", "def rsa_crt_fault(n, e, correct_sig, faulty_sig, msg):", "\"\"\"Factor n from one correct and one faulty CRT signature.\"\"\"", "from math import gcd", "diff = pow(correct_sig, e, n) - pow(faulty_sig, e, n)", "p = gcd(diff % n, n)", "if 1 < p < n:", "q = n // p", "return p, q", "return None"],
    'even-simpler-only-faulty-signature-needed-if-message-is-known': ["def rsa_crt_fault_simple(n, e, faulty_sig, msg):", "p = gcd(pow(faulty_sig, e, n) - msg, n)", "if 1 < p < n:", "return p, n // p", "return None"],
    '8-decision-tree': ["RSA challenge \u2014 what information do you have?", "\u251c\u2500 Have n and it's small (< 512 bits)?", "\u2502  \u2514\u2500 Factor directly: factordb.com \u2192 yafu \u2192 msieve", "\u251c\u2500 Have multiple n values?", "\u2502  \u2514\u2500 Batch GCD \u2014 shared factors?", "\u2502     \u251c\u2500 Yes \u2192 factor all that share factors", "\u2502     \u2514\u2500 No \u2192 analyze each n individually", "\u251c\u2500 Know e?", "\u2502  \u251c\u2500 e = 3 (or small)?", "\u2502  \u2502  \u251c\u2500 Single ciphertext, small message \u2192 cube root", "\u2502  \u2502  \u251c\u2500 Multiple ciphertexts, different n \u2192 Hastad broadcast", "\u2502  \u2502  \u251c\u2500 Two related messages \u2192 Franklin-Reiter", "\u2502  \u2502  \u2514\u2500 Partial plaintext known \u2192 Coppersmith", "\u2502  \u251c\u2500 e is very large?", "\u2502  \u2502  \u2514\u2500 d is likely small \u2192 Wiener \u2192 Boneh-Durfee", "\u2502  \u2514\u2500 Same n, two different e values?", "\u2502     \u2514\u2500 Common modulus attack (Bezout coefficients)", "\u251c\u2500 Know partial factorization info?", "\u2502  \u251c\u2500 Know some bits of p \u2192 Coppersmith partial key", "\u2502  \u251c\u2500 p-1 is B-smooth \u2192 Pollard p-1", "\u2502  \u2514\u2500 p \u2248 q (close primes) \u2192 Fermat factorization", "\u251c\u2500 Have an oracle?", "\u2502  \u251c\u2500 Parity oracle (LSB) \u2192 LSB oracle attack", "\u2502  \u251c\u2500 Padding validity oracle (PKCS#1 v1.5) \u2192 Bleichenbacher", "\u2502  \u2514\u2500 OAEP oracle \u2192 Manger's attack", "\u251c\u2500 Have faulty signature?", "\u2502  \u2514\u2500 RSA-CRT fault \u2192 factor n from faulty sig", "\u251c\u2500 Know e\u00b7d relationship?", "\u2502  \u2514\u2500 e\u00b7d \u2261 1 mod \u03c6(n) \u2192 factor n from (e,d,n)", "\u2514\u2500 None of the above?", "\u251c\u2500 Check factordb for known factorization", "\u251c\u2500 Try Pollard rho for medium-size n", "\u251c\u2500 Look for implementation flaws (weak PRNG for key generation)", "\u2514\u2500 Consider side-channel if physical access available"],
    '9-tools': [],
    'rsactftool-quick-commands': ["```bash"],
    'from-public-key': ["python3 RsaCtfTool.py --publickey pub.pem -n --private"],
    'from-parameters': ["python3 RsaCtfTool.py -n $N -e $E --uncipher $C"],
    'try-all-attacks': ["python3 RsaCtfTool.py --publickey pub.pem --uncipherfile flag.enc --attack all"],
    'decrypt-after-factoring': ["```python", "from Crypto.PublicKey import RSA", "from gmpy2 import invert", "p, q = ...  # factored", "n = p * q", "e = 65537", "phi = (p - 1) * (q - 1)", "d = int(invert(e, phi))", "c = ...  # ciphertext as integer", "m = pow(c, d, n)", "plaintext = m.to_bytes((m.bit_length() + 7) // 8, 'big')", "print(plaintext)"],
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