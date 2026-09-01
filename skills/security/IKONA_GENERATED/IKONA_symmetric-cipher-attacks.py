#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/symmetric-cipher-attacks

Skill: SKILL: Symmetric Cipher Attacks — Expert Cryptanalysis Playbook
Desc : >-

Run:  python hack-skills-symmetric-cipher-attacks.py --help
      python hack-skills-symmetric-cipher-attacks.py --list
      python hack-skills-symmetric-cipher-attacks.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/symmetric-cipher-attacks'
TITLE = 'SKILL: Symmetric Cipher Attacks — Expert Cryptanalysis Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: symmetric-cipher-attacks", "description: >-", "Symmetric cipher attack playbook. Use when exploiting block cipher mode", "weaknesses (CBC padding oracle, ECB cut-and-paste, bit flipping), stream", "cipher key reuse, or meet-in-the-middle attacks."],
    'skill-symmetric-cipher-attacks-expert-cryptanalysis-playbook': [],
    '0-related-routing': ["- [rsa-attack-techniques](../rsa-attack-techniques/SKILL.md) when symmetric key is protected by RSA", "- [hash-attack-techniques](../hash-attack-techniques/SKILL.md) when HMAC or hash-based authentication is involved", "- [lattice-crypto-attacks](../lattice-crypto-attacks/SKILL.md) for LCG/LFSR state recovery via lattice methods"],
    'advanced-reference': ["Also load [BLOCK_CIPHER_ATTACKS.md](./BLOCK_CIPHER_ATTACKS.md) when you need:", "- Detailed attack scripts with full Python implementations", "- Step-by-step byte-at-a-time ECB walkthrough", "- PadBuster usage and custom padding oracle scripts", "- LCG/LFSR recovery implementation"],
    'quick-attack-selection': [],
    '1-padding-oracle-attack-cbc-mode': [],
    '1-1-mechanism': ["CBC decryption: `P_i = D_K(C_i) \u2295 C_{i-1}`", "If the server reveals whether padding is valid (PKCS#7), we can decrypt any block by manipulating the previous ciphertext block."],
    '1-2-attack-steps': ["Target: decrypt block C_i (with unknown plaintext P_i)", "For byte position b = 15 down to 0 (last byte first):", "padding_value = 16 - b", "For guess = 0x00 to 0xFF:", "Construct modified C'_{i-1}:", "- Bytes 0..b-1: original C_{i-1} bytes", "- Byte b: guess", "- Bytes b+1..15: calculated to produce correct padding", "Send (C'_{i-1} || C_i) to oracle", "If oracle says \"valid padding\":", "intermediate_byte[b] = guess \u2295 padding_value", "plaintext_byte[b] = intermediate_byte[b] \u2295 original_C_{i-1}[b]"],
    '1-3-python-implementation': ["```python", "def padding_oracle_attack(ciphertext, block_size, oracle):", "oracle(ct) returns True if padding is valid, False otherwise.", "ciphertext includes IV as first block.", "blocks = [ciphertext[i:i+block_size] for i in range(0, len(ciphertext), block_size)]", "plaintext = b\"\"", "for block_idx in range(1, len(blocks)):", "prev_block = bytearray(blocks[block_idx - 1])", "curr_block = blocks[block_idx]", "intermediate = [0] * block_size", "decrypted = [0] * block_size", "for byte_pos in range(block_size - 1, -1, -1):", "padding_val = block_size - byte_pos", "for guess in range(256):", "modified = bytearray(block_size)", "modified[byte_pos] = guess", "for j in range(byte_pos + 1, block_size):", "modified[j] = intermediate[j] ^ padding_val", "test_ct = bytes(modified) + curr_block", "if oracle(test_ct):", "if byte_pos == block_size - 1:", "check = bytearray(modified)", "check[byte_pos - 1] ^= 1", "if not oracle(bytes(check) + curr_block):", "continue", "intermediate[byte_pos] = guess ^ padding_val", "decrypted[byte_pos] = intermediate[byte_pos] ^ prev_block[byte_pos]", "break", "plaintext += bytes(decrypted)", "return plaintext"],
    '1-4-tools': ["```bash"],
    'padbuster': ["padbuster http://target/decrypt?ct= CIPHERTEXT_HEX 16 -encoding 0", "padbuster http://target/decrypt?ct= CIPHERTEXT_HEX 16 -encoding 0 -plaintext \"admin=true\""],
    '2-cbc-bit-flipping': [],
    '2-1-concept': ["Flipping bit at position j in C_{i-1} flips the same bit at position j in P_i (and corrupts all of P_{i-1}).", "Original:  P_i[j] = D_K(C_i)[j] \u2295 C_{i-1}[j]", "Modified:  P'_i[j] = D_K(C_i)[j] \u2295 C'_{i-1}[j]", "= P_i[j] \u2295 (C_{i-1}[j] \u2295 C'_{i-1}[j])"],
    '2-2-practical-example': ["```python", "def cbc_bitflip(ciphertext, block_size, target_byte_pos, old_value, new_value):", "Flip byte in plaintext block N+1 by modifying ciphertext block N.", "target_byte_pos: absolute position in plaintext (0-indexed)", "ct = bytearray(ciphertext)", "block_num = target_byte_pos // block_size", "byte_in_block = target_byte_pos % block_size", "modify_pos = (block_num - 1) * block_size + byte_in_block", "ct[modify_pos] ^= old_value ^ new_value", "return bytes(ct)"],
    'example-flip-admin-0-to-admin-1': [],
    'if-admin-0-is-at-byte-position-22-block-1-byte-6': ["modified_ct = cbc_bitflip(ciphertext, 16, 22, ord('0'), ord('1'))"],
    '3-ecb-mode-attacks': [],
    '3-1-detection': ["```python", "def detect_ecb(ciphertext, block_size=16):", "\"\"\"ECB produces identical blocks for identical plaintext blocks.\"\"\"", "blocks = [ciphertext[i:i+block_size] for i in range(0, len(ciphertext), block_size)]", "return len(blocks) != len(set(blocks))"],
    'force-detection-send-repeated-plaintext': ["test_input = b\"A\" * 48  # at least 3 blocks of identical data"],
    'if-response-has-repeated-blocks-ecb': [],
    '3-2-ecb-cut-and-paste': ["Reorder ciphertext blocks to create new valid plaintexts.", "Original blocks:", "Block 0: \"email=foo@bar.c\"", "Block 1: \"om&role=user&uid\"", "Block 2: \"=10\\x0d\\x0d\\x0d...\"", "Attack: craft input so \"admin\" + padding lands in its own block,", "then swap it in place of \"user\" block.", "Step 1: Send email that aligns \"admin\" + PKCS7 to a block:", "email = \"foo@bar.coadmin\\x0b\\x0b\\x0b\\x0b\\x0b\\x0b\\x0b\\x0b\\x0b\\x0b\\x0b\"", "\u2192 Block 1 encrypts \"admin\\x0b\\x0b...\"  (save this block)", "Step 2: Send email that puts \"role=\" at end of block:", "email = \"foo@bar.co\"", "\u2192 Block 2 = \"=user&uid=10...\"  (but we replace this)", "Step 3: Replace last block with saved \"admin\\x0b...\" block"],
    '3-3-byte-at-a-time-ecb-decryption': ["Decrypt unknown appended secret one byte at a time.", "```python", "def ecb_byte_at_a_time(encrypt_oracle, block_size=16):", "encrypt_oracle(input_bytes) = AES_ECB(input || unknown_secret)", "Returns the unknown_secret.", "secret = b\"\"", "secret_len = len(encrypt_oracle(b\"\"))", "for i in range(secret_len):", "block_num = i // block_size", "pad_len = block_size - 1 - (i % block_size)", "padding = b\"A\" * pad_len", "target_ct = encrypt_oracle(padding)", "target_block = target_ct[block_num * block_size:(block_num + 1) * block_size]", "for byte_val in range(256):", "test_input = padding + secret + bytes([byte_val])", "test_ct = encrypt_oracle(test_input)", "test_block = test_ct[block_num * block_size:(block_num + 1) * block_size]", "if test_block == target_block:", "secret += bytes([byte_val])", "break", "return secret"],
    '4-stream-cipher-attacks': [],
    '4-1-known-plaintext-key-reuse-two-time-pad': ["```python", "def two_time_pad(c1, c2, known_crib=None):", "c1 = m1 \u2295 K, c2 = m2 \u2295 K (same key K)", "c1 \u2295 c2 = m1 \u2295 m2 (key cancels)", "xored = bytes(a ^ b for a, b in zip(c1, c2))", "if known_crib:", "results = []", "for offset in range(len(xored) - len(known_crib) + 1):", "candidate = bytes(", "xored[offset + i] ^ known_crib[i] for i in range(len(known_crib))", "if all(0x20 <= b <= 0x7e for b in candidate):", "results.append((offset, candidate))", "return results", "return xored"],
    '4-2-single-byte-xor-brute-force': ["```python", "def single_byte_xor_crack(ciphertext):", "\"\"\"Brute force single-byte XOR key using frequency analysis.\"\"\"", "english_freq = {", "'e': 12.7, 't': 9.1, 'a': 8.2, 'o': 7.5, 'i': 7.0,", "'n': 6.7, 's': 6.3, 'h': 6.1, 'r': 6.0, 'd': 4.3,", "best_score, best_key, best_plaintext = 0, 0, b\"\"", "for key in range(256):", "plaintext = bytes(b ^ key for b in ciphertext)", "score = sum(", "english_freq.get(chr(b).lower(), 0)", "for b in plaintext if 0x20 <= b <= 0x7e", "if score > best_score:", "best_score = score", "best_key = key", "best_plaintext = plaintext", "return best_key, best_plaintext"],
    '4-3-repeating-key-xor-kasiski-like': ["```python", "def repeating_xor_crack(ciphertext, max_keylen=40):", "\"\"\"Crack repeating-key XOR using Hamming distance for key length.\"\"\"", "def hamming(a, b):", "return sum(bin(x ^ y).count('1') for x, y in zip(a, b))", "scores = []", "for kl in range(2, max_keylen + 1):", "blocks = [ciphertext[i:i+kl] for i in range(0, len(ciphertext) - kl, kl)]", "if len(blocks) < 4:", "continue", "dist = sum(hamming(blocks[i], blocks[i+1]) for i in range(min(3, len(blocks)-1)))", "normalized = dist / (min(3, len(blocks)-1) * kl)", "scores.append((normalized, kl))", "best_keylen = sorted(scores)[0][1]", "key = b\"\"", "for i in range(best_keylen):", "column = bytes(ciphertext[j] for j in range(i, len(ciphertext), best_keylen))", "k, _ = single_byte_xor_crack(column)", "key += bytes([k])", "return key"],
    '4-4-lfsr-state-recovery-berlekamp-massey': ["```python", "def berlekamp_massey_gf2(output_bits):", "\"\"\"Recover LFSR feedback polynomial from output sequence over GF(2).\"\"\"", "n = len(output_bits)", "C = [0] * (n + 1)", "B = [0] * (n + 1)", "C[0] = B[0] = 1", "L = 0", "m = 1", "b = 1", "for N in range(n):", "d = output_bits[N]", "for i in range(1, L + 1):", "d ^= C[i] & output_bits[N - i]", "if d == 0:", "m += 1", "elif 2 * L <= N:", "T = C[:]", "for i in range(m, n + 1):", "C[i] ^= B[i - m]", "L = N + 1 - L", "B = T", "b = d", "m = 1", "else:", "for i in range(m, n + 1):", "C[i] ^= B[i - m]", "m += 1", "return C[:L + 1], L"],
    '4-5-rc4-biases': [],
    '5-meet-in-the-middle': [],
    '5-1-double-encryption-attack': ["Double encryption: C = E_K2(E_K1(P))", "Brute force: 2^(2n) expected", "MITM:        2^(n+1) + storage for 2^n entries", "Attack:", "1. Encrypt P with all possible K1 \u2192 store (E_K1(P), K1) in table", "2. Decrypt C with all possible K2 \u2192 check if D_K2(C) matches any entry", "3. Match found \u2192 (K1, K2) recovered", "```python", "from itertools import product", "def meet_in_the_middle(encrypt, decrypt, plaintext, ciphertext, keyspace_bits):", "\"\"\"MITM attack on double encryption.\"\"\"", "enc_table = {}", "for k1 in range(2**keyspace_bits):", "intermediate = encrypt(plaintext, k1)", "enc_table[intermediate] = k1", "for k2 in range(2**keyspace_bits):", "intermediate = decrypt(ciphertext, k2)", "if intermediate in enc_table:", "k1 = enc_table[intermediate]", "return k1, k2", "return None"],
    '6-decision-tree': ["Symmetric cipher challenge \u2014 what can you observe?", "\u251c\u2500 Can you detect the mode?", "\u2502  \u251c\u2500 Repeated input \u2192 repeated output blocks?", "\u2502  \u2502  \u2514\u2500 Yes \u2192 ECB mode", "\u2502  \u2502     \u251c\u2500 Can control prefix \u2192 byte-at-a-time decryption", "\u2502  \u2502     \u251c\u2500 Can reorder blocks \u2192 cut-and-paste", "\u2502  \u2502     \u2514\u2500 Can detect block boundaries \u2192 block alignment oracle", "\u2502  \u251c\u2500 Error message differs for bad padding?", "\u2502  \u2502  \u2514\u2500 Yes \u2192 Padding oracle (CBC)", "\u2502  \u2502     \u2514\u2500 PadBuster or custom script", "\u2502  \u2514\u2500 Can modify ciphertext and observe effect?", "\u2502     \u2514\u2500 Next-block plaintext changes \u2192 CBC bit flipping", "\u251c\u2500 Stream cipher or XOR?", "\u2502  \u251c\u2500 Key reused on different messages?", "\u2502  \u2502  \u2514\u2500 XOR ciphertexts \u2192 crib drag", "\u2502  \u251c\u2500 Known plaintext-ciphertext pair?", "\u2502  \u2502  \u2514\u2500 Recover keystream directly", "\u2502  \u251c\u2500 Single-byte XOR key?", "\u2502  \u2502  \u2514\u2500 Brute force 256 keys with frequency analysis", "\u2502  \u251c\u2500 Repeating-key XOR?", "\u2502  \u2502  \u2514\u2500 Hamming distance \u2192 key length \u2192 per-position crack", "\u2502  \u2514\u2500 LFSR-based?", "\u2502     \u2514\u2500 Berlekamp-Massey for state/polynomial recovery", "\u251c\u2500 PRNG-based cipher?", "\u2502  \u251c\u2500 LCG \u2192 truncated output lattice attack", "\u2502  \u251c\u2500 Mersenne Twister \u2192 624 outputs \u2192 full state recovery", "\u2502  \u2514\u2500 Custom PRNG \u2192 analyze period and state size", "\u251c\u2500 Double / triple encryption?", "\u2502  \u2514\u2500 Meet-in-the-middle", "\u2514\u2500 RC4 specifically?", "\u251c\u2500 Single encryption \u2192 initial byte bias", "\u251c\u2500 Many encryptions same key \u2192 statistical attack", "\u2514\u2500 IV prepended to key \u2192 FMS attack (WEP-like)"],
    '7-tools': [],
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