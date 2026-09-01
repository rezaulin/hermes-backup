#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/classical-cipher-analysis

Skill: SKILL: Classical Cipher Analysis — Expert Cryptanalysis Playbook
Desc : >-

Run:  python hack-skills-classical-cipher-analysis.py --help
      python hack-skills-classical-cipher-analysis.py --list
      python hack-skills-classical-cipher-analysis.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/classical-cipher-analysis'
TITLE = 'SKILL: Classical Cipher Analysis — Expert Cryptanalysis Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: classical-cipher-analysis", "description: >-", "Classical cipher analysis playbook. Use when encountering substitution", "ciphers, Vigenere, transposition, XOR, or encoded text in CTF challenges", "that requires frequency analysis, Kasiski examination, or known-plaintext", "cryptanalysis."],
    'skill-classical-cipher-analysis-expert-cryptanalysis-playbook': [],
    '0-related-routing': ["- [symmetric-cipher-attacks](../symmetric-cipher-attacks/SKILL.md) when dealing with modern symmetric ciphers (AES/DES) rather than classical", "- [hash-attack-techniques](../hash-attack-techniques/SKILL.md) when the challenge involves hash-based constructions", "- [lattice-crypto-attacks](../lattice-crypto-attacks/SKILL.md) when knapsack-based ciphers are encountered"],
    'quick-identification-guide': [],
    '1-cipher-identification-methodology': [],
    '1-1-step-1-character-set-analysis': ["```python", "def analyze_charset(ciphertext):", "\"\"\"Identify encoding/cipher by character set.\"\"\"", "chars = set(ciphertext.strip())", "if chars <= set('01 \\n'):", "return \"Binary encoding\"", "if chars <= set('.-/ \\n'):", "return \"Morse code\"", "if chars <= set('0123456789abcdef \\n'):", "return \"Hex encoding\"", "if chars <= set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\\n'):", "if '=' in ciphertext or len(ciphertext) % 4 == 0:", "return \"Base64 encoding\"", "if chars <= set('ABCDEFGHIJKLMNOPQRSTUVWXYZ \\n'):", "return \"Uppercase only \u2014 classical cipher\"", "if all(c in '12345' for c in ciphertext.replace(' ', '').replace('\\n', '')):", "return \"Polybius square (digits 1-5)\"", "return \"Mixed charset \u2014 needs further analysis\""],
    '1-2-step-2-frequency-analysis': ["```python", "from collections import Counter", "def frequency_analysis(text):", "\"\"\"Compute letter frequency distribution.\"\"\"", "text = text.upper()", "letters = [c for c in text if c.isalpha()]", "total = len(letters)", "freq = Counter(letters)", "print(\"Letter frequencies:\")", "for letter, count in freq.most_common():", "pct = count / total * 100", "bar = '#' * int(pct)", "print(f\"  {letter}: {pct:5.1f}% {bar}\")", "return freq"],
    'english-letter-frequency-for-comparison': [],
    'e-t-a-o-i-n-s-h-r-d-l-c-u-m-w-f-g-y-p-b-v-k-j-x-q-z': [],
    '12-7-9-1-8-2-7-5-7-0-6-7-6-3-6-1-6-0-4-3-4-0-2-8': [],
    '1-3-step-3-index-of-coincidence-ic': ["```python", "def index_of_coincidence(text):", "IC \u2248 0.065 \u2192 English / monoalphabetic substitution", "IC \u2248 0.038 \u2192 random / polyalphabetic cipher", "text = [c for c in text.upper() if c.isalpha()]", "N = len(text)", "freq = Counter(text)", "ic = sum(f * (f - 1) for f in freq.values()) / (N * (N - 1))", "return ic"],
    'interpretation': [],
    'ic-0-060-monoalphabetic-caesar-simple-substitution-playfair': [],
    'ic-0-045-0-055-polyalphabetic-with-short-key-vigenere-key-10': [],
    'ic-0-038-0-042-polyalphabetic-with-long-key-or-random': [],
    '1-4-step-4-kasiski-examination-for-polyalphabetic': ["```python", "from math import gcd", "from functools import reduce", "def kasiski(ciphertext, min_len=3):", "\"\"\"Find repeated sequences and their distances \u2192 key length.\"\"\"", "text = ''.join(c for c in ciphertext.upper() if c.isalpha())", "distances = []", "for length in range(min_len, min(20, len(text) // 3)):", "for i in range(len(text) - length):", "seq = text[i:i+length]", "j = text.find(seq, i + 1)", "while j != -1:", "distances.append(j - i)", "j = text.find(seq, j + 1)", "if not distances:", "return None", "common_gcds = Counter()", "for d in distances:", "for factor in range(2, min(d + 1, 30)):", "if d % factor == 0:", "common_gcds[factor] += 1", "print(\"Likely key lengths (by frequency):\")", "for length, count in common_gcds.most_common(5):", "print(f\"  Key length {length}: {count} occurrences\")", "return common_gcds.most_common(1)[0][0]"],
    '2-monoalphabetic-substitution': [],
    '2-1-frequency-analysis-attack': ["```python", "def solve_substitution(ciphertext, interactive=False):", "\"\"\"Solve monoalphabetic substitution via frequency analysis.\"\"\"", "freq = frequency_analysis(ciphertext)", "eng_order = \"ETAOINSRHLDCUMWFGYPBVKJXQZ\"", "cipher_order = ''.join(c for c, _ in freq.most_common())", "mapping = {}", "for i, c in enumerate(cipher_order):", "if i < len(eng_order):", "mapping[c] = eng_order[i]", "result = \"\"", "for c in ciphertext.upper():", "result += mapping.get(c, c)", "return result, mapping"],
    'better-approach-use-automated-solvers': [],
    'quipqiup-com-online-substitution-solver': [],
    'dcode-fr-monoalphabetic-substitution-with-word-pattern-matching': [],
    '2-2-known-plaintext-crib-dragging': ["If part of the plaintext is known (e.g., \"flag{\" prefix):", "```python", "def crib_drag_substitution(ciphertext, known_plain, known_cipher):", "\"\"\"Build partial mapping from known plaintext-ciphertext pair.\"\"\"", "mapping = {}", "for p, c in zip(known_plain.upper(), known_cipher.upper()):", "mapping[c] = p", "result = \"\"", "for c in ciphertext.upper():", "result += mapping.get(c, '?')", "return result, mapping"],
    '3-caesar-rot-ciphers': [],
    '3-1-brute-force': ["```python", "def caesar_bruteforce(ciphertext):", "\"\"\"Try all 25 shifts, score by English frequency.\"\"\"", "results = []", "for shift in range(26):", "decrypted = \"\"", "for c in ciphertext:", "if c.isalpha():", "base = ord('A') if c.isupper() else ord('a')", "decrypted += chr((ord(c) - base - shift) % 26 + base)", "else:", "decrypted += c", "score = chi_squared_score(decrypted)", "results.append((shift, score, decrypted))", "results.sort(key=lambda x: x[1])", "return results[0]  # best match", "def chi_squared_score(text):", "\"\"\"Lower score = closer to English.\"\"\"", "expected = {", "'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0,", "'N': 6.7, 'S': 6.3, 'H': 6.1, 'R': 6.0, 'D': 4.3,", "'L': 4.0, 'C': 2.8, 'U': 2.8, 'M': 2.4, 'W': 2.4,", "'F': 2.2, 'G': 2.0, 'Y': 2.0, 'P': 1.9, 'B': 1.5,", "'V': 1.0, 'K': 0.8, 'J': 0.2, 'X': 0.2, 'Q': 0.1, 'Z': 0.1,", "text = text.upper()", "letters = [c for c in text if c.isalpha()]", "total = len(letters)", "if total == 0:", "return float('inf')", "freq = Counter(letters)", "score = sum(", "(freq.get(c, 0) / total * 100 - expected.get(c, 0)) ** 2 / max(expected.get(c, 0.1), 0.1)", "for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'", "return score"],
    '3-2-rot13-and-rot47': ["```python", "import codecs"],
    'rot13-letters-only': ["rot13 = codecs.decode(ciphertext, 'rot_13')"],
    'rot47-ascii-33-126': ["def rot47(text):", "return ''.join(", "chr(33 + (ord(c) - 33 + 47) % 94) if 33 <= ord(c) <= 126 else c", "for c in text"],
    '4-vigenere-cipher': [],
    '4-1-full-attack-workflow': ["Step 1: Confirm polyalphabetic (IC \u2248 0.04-0.05)", "Step 2: Find key length (Kasiski + IC per period)", "Step 3: For each key position, solve as single Caesar cipher", "Step 4: Assemble key \u2192 decrypt"],
    '4-2-ic-based-key-length-detection': ["```python", "def find_vigenere_key_length(ciphertext, max_key=20):", "\"\"\"Use IC to find Vigenere key length.\"\"\"", "text = [c for c in ciphertext.upper() if c.isalpha()]", "results = []", "for kl in range(1, max_key + 1):", "columns = [[] for _ in range(kl)]", "for i, c in enumerate(text):", "columns[i % kl].append(c)", "avg_ic = sum(", "index_of_coincidence(''.join(col)) for col in columns", ") / kl", "results.append((kl, avg_ic))", "print(f\"  Key length {kl:2d}: IC = {avg_ic:.4f}\")", "best = max(results, key=lambda x: x[1])", "return best[0]"],
    '4-3-per-position-frequency-attack': ["```python", "def crack_vigenere(ciphertext, key_length):", "\"\"\"Crack Vigenere given known key length.\"\"\"", "text = [c for c in ciphertext.upper() if c.isalpha()]", "key = \"\"", "for pos in range(key_length):", "column = ''.join(text[i] for i in range(pos, len(text), key_length))", "shift, score, _ = caesar_bruteforce(column)", "key += chr(shift + ord('A'))", "plaintext = \"\"", "ki = 0", "for c in ciphertext:", "if c.isalpha():", "shift = ord(key[ki % key_length]) - ord('A')", "base = ord('A') if c.isupper() else ord('a')", "plaintext += chr((ord(c) - base - shift) % 26 + base)", "ki += 1", "else:", "plaintext += c", "return key, plaintext"],
    '5-affine-cipher': [],
    '5-1-definition': ["`E(x) = (a\u00b7x + b) mod 26` where gcd(a, 26) = 1.", "Valid a values: 1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25 (12 values)."],
    '5-2-brute-force-312-combinations': ["```python", "def crack_affine(ciphertext):", "\"\"\"Brute force affine cipher: 12 \u00d7 26 = 312 combinations.\"\"\"", "valid_a = [a for a in range(1, 26) if gcd(a, 26) == 1]", "for a in valid_a:", "a_inv = pow(a, -1, 26)", "for b in range(26):", "plaintext = \"\"", "for c in ciphertext.upper():", "if c.isalpha():", "y = ord(c) - ord('A')", "x = (a_inv * (y - b)) % 26", "plaintext += chr(x + ord('A'))", "else:", "plaintext += c", "score = chi_squared_score(plaintext)", "if score < 50:  # reasonable English", "print(f\"a={a}, b={b}: {plaintext[:50]}...\")"],
    '5-3-known-plaintext': ["```python", "def affine_from_known(plain1, cipher1, plain2, cipher2):", "\"\"\"Recover (a, b) from two known plaintext-ciphertext pairs.\"\"\"", "p1, c1 = ord(plain1) - ord('A'), ord(cipher1) - ord('A')", "p2, c2 = ord(plain2) - ord('A'), ord(cipher2) - ord('A')", "diff_p = (p1 - p2) % 26", "diff_c = (c1 - c2) % 26", "if gcd(diff_p, 26) != 1:", "return None", "a = (diff_c * pow(diff_p, -1, 26)) % 26", "b = (c1 - a * p1) % 26", "return a, b"],
    '6-hill-cipher': ["Matrix-based cipher: `C = K \u00b7 P mod 26` where K is an n\u00d7n key matrix."],
    '6-1-known-plaintext-attack': ["```python", "import numpy as np", "def crack_hill(known_plain, known_cipher, n=2):", "\"\"\"Recover Hill cipher key from known plaintext-ciphertext (mod 26).\"\"\"", "P = [ord(c) - ord('A') for c in known_plain.upper()]", "C = [ord(c) - ord('A') for c in known_cipher.upper()]", "P_matrix = np.array(P[:n*n]).reshape(n, n).T", "C_matrix = np.array(C[:n*n]).reshape(n, n).T", "from sympy import Matrix", "P_mat = Matrix(P_matrix.tolist())", "C_mat = Matrix(C_matrix.tolist())", "P_inv = P_mat.inv_mod(26)", "K = (C_mat * P_inv) % 26", "return K"],
    '7-transposition-ciphers': [],
    '7-1-rail-fence': ["```python", "def rail_fence_decrypt(ciphertext, rails):", "\"\"\"Decrypt rail fence cipher.\"\"\"", "n = len(ciphertext)", "pattern = []", "for i in range(n):", "row = 0", "cycle = 2 * (rails - 1)", "pos = i % cycle", "row = pos if pos < rails else cycle - pos", "pattern.append((row, i))", "pattern.sort()", "result = [''] * n", "ci = 0", "for _, orig_pos in pattern:", "result[orig_pos] = ciphertext[ci]", "ci += 1", "return ''.join(result)"],
    'brute-force-all-rail-counts': ["for rails in range(2, 20):", "print(f\"Rails {rails}: {rail_fence_decrypt(ct, rails)[:50]}\")"],
    '7-2-columnar-transposition': ["```python", "def columnar_decrypt(ciphertext, key):", "\"\"\"Decrypt columnar transposition given key word.\"\"\"", "n_cols = len(key)", "n_rows = -(-len(ciphertext) // n_cols)  # ceiling division", "order = sorted(range(n_cols), key=lambda i: key[i])", "full_cols = len(ciphertext) % n_cols", "if full_cols == 0:", "full_cols = n_cols", "columns = [''] * n_cols", "pos = 0", "for col_idx in order:", "col_len = n_rows if col_idx < full_cols else n_rows - 1", "columns[col_idx] = ciphertext[pos:pos + col_len]", "pos += col_len", "plaintext = ''", "for row in range(n_rows):", "for col in range(n_cols):", "if row < len(columns[col]):", "plaintext += columns[col][row]", "return plaintext"],
    '8-xor-cipher': [],
    '8-1-single-byte-xor': ["See [symmetric-cipher-attacks](../symmetric-cipher-attacks/SKILL.md) Section 4.2 for full implementation."],
    '8-2-multi-byte-xor-xortool': ["```bash"],
    'automatic-key-length-detection-and-cracking': ["xortool ciphertext.bin -l 5        # try key length 5", "xortool ciphertext.bin -b          # brute force key length", "xortool ciphertext.bin -c 20       # assume most common char is space (0x20)"],
    '8-3-known-plaintext-xor': ["```python", "def xor_known_plaintext(ciphertext, known_plain, offset=0):", "\"\"\"Recover XOR key from known plaintext at given offset.\"\"\"", "key_fragment = bytes(", "c ^ p for c, p in zip(ciphertext[offset:], known_plain)", "print(f\"Key fragment: {key_fragment}\")", "return key_fragment"],
    '9-special-ciphers': [],
    '9-1-bacon-cipher': ["Binary encoding using two typefaces (A=normal, B=bold/italic).", "```python", "BACON = {", "'AAAAA': 'A', 'AAAAB': 'B', 'AAABA': 'C', 'AAABB': 'D',", "'AABAA': 'E', 'AABAB': 'F', 'AABBA': 'G', 'AABBB': 'H',", "'ABAAA': 'I', 'ABAAB': 'J', 'ABABA': 'K', 'ABABB': 'L',", "'ABBAA': 'M', 'ABBAB': 'N', 'ABBBA': 'O', 'ABBBB': 'P',", "'BAAAA': 'Q', 'BAAAB': 'R', 'BAABA': 'S', 'BAABB': 'T',", "'BABAA': 'U', 'BABAB': 'V', 'BABBA': 'W', 'BABBB': 'X',", "'BAAAA': 'Y', 'BAAAB': 'Z',", "def decode_bacon(text):", "\"\"\"Decode Bacon cipher: uppercase=B, lowercase=A (or similar mapping).\"\"\"", "binary = ''.join('B' if c.isupper() else 'A' for c in text if c.isalpha())", "result = ''", "for i in range(0, len(binary) - 4, 5):", "chunk = binary[i:i+5]", "result += BACON.get(chunk, '?')", "return result"],
    '9-2-polybius-square': ["1 2 3 4 5", "\u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500", "1 \u2502 A B C D E", "2 \u2502 F G H I/J K", "3 \u2502 L M N O P", "4 \u2502 Q R S T U", "5 \u2502 V W X Y Z", "\"HELLO\" = \"23 15 31 31 34\""],
    '9-3-playfair': ["5\u00d75 grid cipher encrypting digraphs.", "Key: \"MONARCHY\" \u2192 grid:", "M O N A R", "C H Y B D", "E F G I/J K", "L P Q S T", "U V W X Z", "Rules:", "Same row \u2192 shift right: HE \u2192 FE \u2192 \"GF\"", "Same col \u2192 shift down", "Rectangle \u2192 swap columns"],
    '10-decision-tree': ["Unknown ciphertext \u2014 how to identify and break?", "\u251c\u2500 Step 1: Check encoding", "\u2502  \u251c\u2500 Base64 alphabet with padding? \u2192 Decode first, then re-analyze", "\u2502  \u251c\u2500 Hex string? \u2192 Convert to bytes, re-analyze", "\u2502  \u251c\u2500 Binary (01)? \u2192 Convert to ASCII", "\u2502  \u251c\u2500 Morse (.-/)? \u2192 Decode Morse", "\u2502  \u2514\u2500 Printable text? \u2192 Continue to Step 2", "\u251c\u2500 Step 2: Character set", "\u2502  \u251c\u2500 Only letters (A-Z)?", "\u2502  \u2502  \u251c\u2500 Compute IC", "\u2502  \u2502  \u2502  \u251c\u2500 IC \u2248 0.065 \u2192 Monoalphabetic", "\u2502  \u2502  \u2502  \u2502  \u251c\u2500 Uniform shift in freq? \u2192 Caesar \u2192 brute force 25", "\u2502  \u2502  \u2502  \u2502  \u251c\u2500 Random-looking mapping? \u2192 Simple substitution \u2192 frequency analysis", "\u2502  \u2502  \u2502  \u2502  \u2514\u2500 Digraph patterns? \u2192 Playfair \u2192 digraph analysis", "\u2502  \u2502  \u2502  \u2502", "\u2502  \u2502  \u2502  \u251c\u2500 IC \u2248 0.04-0.05 \u2192 Polyalphabetic", "\u2502  \u2502  \u2502  \u2502  \u251c\u2500 Kasiski \u2192 find key length", "\u2502  \u2502  \u2502  \u2502  \u2514\u2500 Per-position frequency \u2192 crack Vigenere", "\u2502  \u2502  \u2502  \u2502", "\u2502  \u2502  \u2502  \u2514\u2500 IC \u2248 0.038 \u2192 Very long key or one-time pad", "\u2502  \u2502  \u2502     \u2514\u2500 Look for key reuse or weak key generation", "\u2502  \u2502  \u2502", "\u2502  \u2502  \u2514\u2500 Letters appear scrambled (right freq, wrong order)?", "\u2502  \u2502     \u2514\u2500 Transposition", "\u2502  \u2502        \u251c\u2500 Rail fence \u2192 brute force rail count", "\u2502  \u2502        \u2514\u2500 Columnar \u2192 try common key lengths", "\u2502  \u251c\u2500 Numbers (digit pairs)?", "\u2502  \u2502  \u251c\u2500 Pairs in range 11-55 \u2192 Polybius square", "\u2502  \u2502  \u2514\u2500 Numbers mod 26 \u2192 numeric substitution", "\u2502  \u251c\u2500 Mixed case with pattern?", "\u2502  \u2502  \u2514\u2500 Upper/lower encodes binary \u2192 Bacon cipher", "\u2502  \u2514\u2500 Non-printable bytes?", "\u2502     \u2514\u2500 XOR cipher", "\u2502        \u251c\u2500 Single-byte key \u2192 brute force 256", "\u2502        \u251c\u2500 Repeating key \u2192 xortool / Hamming distance", "\u2502        \u2514\u2500 Known plaintext \u2192 direct key recovery", "\u2514\u2500 Step 3: Apply specific attack", "\u251c\u2500 Substitution \u2192 quipqiup.com / frequency analysis", "\u251c\u2500 Caesar \u2192 dcode.fr / brute force", "\u251c\u2500 Vigenere \u2192 Kasiski + per-column Caesar", "\u251c\u2500 Affine \u2192 brute force 312 combinations", "\u251c\u2500 Hill \u2192 known-plaintext matrix attack", "\u251c\u2500 Transposition \u2192 pattern analysis + brute force", "\u2514\u2500 XOR \u2192 xortool / crib dragging"],
    '11-tools': [],
    'cyberchef-recipes-common': ["ROT13:               ROT13", "Caesar brute force:   ROT13 (with offset slider)", "Base64 decode:        From Base64", "Hex decode:           From Hex", "XOR:                  XOR (key as hex/utf8)", "Vigenere:             Vigen\u00e8re Decode", "Morse:                From Morse Code"],
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