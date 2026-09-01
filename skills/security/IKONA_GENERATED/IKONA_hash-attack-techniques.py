#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/hash-attack-techniques

Skill: SKILL: Hash Attack Techniques — Expert Cryptanalysis Playbook
Desc : >-

Run:  python hack-skills-hash-attack-techniques.py --help
      python hack-skills-hash-attack-techniques.py --list
      python hack-skills-hash-attack-techniques.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/hash-attack-techniques'
TITLE = 'SKILL: Hash Attack Techniques — Expert Cryptanalysis Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: hash-attack-techniques", "description: >-", "Hash attack playbook. Use when exploiting length extension, MD5/SHA1", "collisions, HMAC timing leaks, birthday attacks, or hash-based proof", "of work in CTF and authorized testing scenarios."],
    'skill-hash-attack-techniques-expert-cryptanalysis-playbook': [],
    '0-related-routing': ["- [rsa-attack-techniques](../rsa-attack-techniques/SKILL.md) when hash weaknesses affect RSA signature schemes", "- [symmetric-cipher-attacks](../symmetric-cipher-attacks/SKILL.md) when hash is used in key derivation", "- [classical-cipher-analysis](../classical-cipher-analysis/SKILL.md) when analyzing hash-like constructions in classical ciphers"],
    'quick-attack-selection': [],
    '1-length-extension-attack': [],
    '1-1-vulnerable-vs-non-vulnerable': [],
    '1-2-attack-mechanism': ["Given:   MAC = H(secret || original_message)", "Known:   original_message, len(secret), MAC value", "Compute: H(secret || original_message || padding || extension)", "WITHOUT knowing the secret!", "How: The MAC value IS the internal hash state after processing", "(secret || original_message || padding).", "Initialize hash with this state, continue hashing extension."],
    '1-3-padding-calculation-md5-sha': ["```python", "def md5_padding(message_len_bytes):", "\"\"\"Calculate MD5/SHA padding for given message length.\"\"\"", "bit_len = message_len_bytes * 8", "padding = b'\\x80'", "padding += b'\\x00' * ((55 - message_len_bytes) % 64)", "padding += bit_len.to_bytes(8, 'little')  # MD5", "return padding"],
    '1-4-tool-usage': ["```bash"],
    'hashpump': ["hashpump -s \"known_mac_hex\" \\", "-d \"original_data\" \\", "-k 16 \\            # secret length", "-a \"extension_data\""],
    'output-new-mac-new-data-original-padding-extension': [],
    'hash-extender': ["hash_extender --data \"original\" \\", "--secret 16 \\", "--append \"extension\" \\", "--signature \"known_mac_hex\" \\", "--format md5"],
    '1-5-python-implementation': ["```python", "import struct", "def md5_extend(original_mac, original_data_len, secret_len, extension):", "Perform MD5 length extension attack.", "original_mac: hex string of H(secret || original_data)", "h = struct.unpack('<4I', bytes.fromhex(original_mac))", "total_original = secret_len + original_data_len", "padding = md5_padding(total_original)", "forged_len = total_original + len(padding) + len(extension)", "from hashlib import md5", "import hlextend", "sha = hlextend.new('md5')", "new_hash = sha.extend(extension, original_data, secret_len,", "original_mac)", "new_data = sha.payload  # includes original + padding + extension", "return new_hash, new_data"],
    '2-md5-collision-attacks': [],
    '2-1-identical-prefix-collision-fastcoll': ["Two messages with same prefix but different content, producing identical MD5.", "```bash"],
    'generate-collision-pair': ["fastcoll -p prefix_file -o collision1.bin collision2.bin"],
    'result-md5-collision1-bin-md5-collision2-bin': [],
    'files-differ-in-exactly-128-bytes-two-md5-blocks': [],
    '2-2-chosen-prefix-collision-hashclash': ["Two messages with different chosen prefixes, appended with computed suffixes to collide.", "```bash"],
    'hashclash-marc-stevens': ["./hashclash prefix1.bin prefix2.bin"],
    'result-md5-prefix1-suffix1-md5-prefix2-suffix2': [],
    '2-3-unicoll-single-block-near-collision': ["Produces two messages differing in a single byte within one MD5 block, with same hash.", "Application: forge two PDF/PE files with same MD5", "- File 1: benign content", "- File 2: malicious content", "- Same MD5 hash"],
    '2-4-collision-applications': [],
    '2-5-ctf-md5-collision-tricks': ["```php", "// PHP: md5($_GET['a']) == md5($_GET['b']) && $_GET['a'] != $_GET['b']", "// Method 1: Array trick (not real collision)", "?a[]=1&b[]=2  // md5(array) returns NULL, NULL == NULL", "// Method 2: Real collision (fastcoll output, URL-encoded binary)", "?a=<collision1_urlencoded>&b=<collision2_urlencoded>", "// Method 3: 0e magic hashes (loose comparison ==)", "// md5(\"240610708\") = \"0e462097431906509019562988736854\"", "// md5(\"QNKCDZO\")   = \"0e830400451993494058024219903391\"", "// PHP: \"0e...\" == \"0e...\" is TRUE (both evaluate to 0 as floats)"],
    '3-sha-1-collision': [],
    '3-1-shattered-attack-2017': ["First practical SHA-1 collision: two PDF files with same SHA-1.", "- Complexity: ~2^63 SHA-1 computations", "- Cost: ~$110K on GPU clusters (2017 prices)", "- Tool: shattered.io provides the collision PDFs"],
    '3-2-sha-1-chosen-prefix-collision-2020': ["- Complexity: ~2^63.4 computations", "- Practical for attacking PGP/GnuPG key servers", "- Demonstrates SHA-1 is broken for collision resistance"],
    '3-3-impact': ["SHA-1 should NOT be used for:", "\u2717 Digital signatures", "\u2717 Certificate fingerprints", "\u2717 Git commit integrity (migration to SHA-256 in progress)", "\u2717 Deduplication based on hash", "SHA-1 is still OK for:", "\u2713 HMAC-SHA1 (collision resistance not required)", "\u2713 HKDF-SHA1 (PRF security suffices)", "\u2713 Non-adversarial checksums"],
    '4-birthday-attack': [],
    '4-1-generic-birthday-bound': ["For n-bit hash: expected collisions after ~2^(n/2) hashes", "Hash     Bits    Birthday bound", "MD5      128     2^64", "SHA-1    160     2^80", "SHA-256  256     2^128", "CTF application: if hash is truncated to k bits,", "collision in ~2^(k/2) attempts"],
    '4-2-birthday-attack-implementation': ["```python", "import hashlib", "import os", "def birthday_attack(hash_func, output_bits, max_attempts=2**28):", "\"\"\"Find collision for truncated hash.\"\"\"", "mask = (1 << output_bits) - 1", "seen = {}", "for _ in range(max_attempts):", "msg = os.urandom(16)", "h = int(hash_func(msg).hexdigest(), 16) & mask", "if h in seen and seen[h] != msg:", "return seen[h], msg  # collision!", "seen[h] = msg", "return None"],
    'example-find-collision-for-first-32-bits-of-sha-256': ["result = birthday_attack(hashlib.sha256, 32)"],
    '5-hmac-timing-attack': [],
    '5-1-vulnerable-comparison': ["```python"],
    'vulnerable-early-exit-string-comparison': ["def verify_hmac(received, expected):", "return received == expected  # Python == compares left to right"],
    'the-comparison-may-short-circuit-on-first-differing-byte': [],
    'leaking-timing-information': [],
    '5-2-attack-strategy': ["```python", "import requests", "import time", "def hmac_timing_attack(url, data, hmac_len=32):", "\"\"\"Byte-by-byte HMAC recovery via timing.\"\"\"", "known = \"\"", "for pos in range(hmac_len * 2):  # hex chars", "best_char = \"\"", "best_time = 0", "for c in \"0123456789abcdef\":", "candidate = known + c + \"0\" * (hmac_len * 2 - len(known) - 1)", "times = []", "for _ in range(50):  # multiple samples for accuracy", "start = time.perf_counter_ns()", "requests.get(url, params={**data, \"mac\": candidate})", "elapsed = time.perf_counter_ns() - start", "times.append(elapsed)", "avg_time = sorted(times)[len(times)//2]  # median", "if avg_time > best_time:", "best_time = avg_time", "best_char = c", "known += best_char", "print(f\"Position {pos}: {known}\")", "return known"],
    '5-3-constant-time-comparison-defense': ["```python", "import hmac"],
    'secure-constant-time-comparison': ["def verify_hmac_secure(received, expected):", "return hmac.compare_digest(received, expected)"],
    '6-meet-in-the-middle-hash': [],
    '6-1-concept': ["Split hash computation into two halves, precompute one, match against the other.", "Hash computation: H = f(g(x\u2081), h(x\u2082))", "Precompute: table[g(x\u2081)] = x\u2081  for all x\u2081 in space\u2081", "Search:     for each x\u2082 in space\u2082:", "if h(x\u2082) in table:", "found! (x\u2081, x\u2082)", "Time:  O(2^(n/2)) instead of O(2^n)", "Space: O(2^(n/2))"],
    '7-hash-proof-of-work': [],
    '7-1-common-ctf-pow-formats': ["```python"],
    'format-1-find-x-such-that-sha256-prefix-x-starts-with-n-zero-bits': ["import hashlib", "def solve_pow_prefix(prefix, zero_bits):", "target = '0' * (zero_bits // 4)", "i = 0", "while True:", "candidate = prefix + str(i)", "h = hashlib.sha256(candidate.encode()).hexdigest()", "if h.startswith(target):", "return str(i)", "i += 1"],
    'format-2-find-x-such-that-sha256-x-ends-with-specific-suffix': ["def solve_pow_suffix(suffix_hex, hash_func=hashlib.sha256):", "i = 0", "while True:", "h = hash_func(str(i).encode()).hexdigest()", "if h.endswith(suffix_hex):", "return str(i)", "i += 1"],
    '7-2-gpu-accelerated-pow': ["```bash"],
    'hashcat-for-sha256-pow': ["hashcat -a 3 -m 1400 --hex-charset \\", "\"0000000000000000000000000000000000000000000000000000000000000000:prefix\" \\", "\"?a?a?a?a?a?a?a?a\""],
    '8-rainbow-tables-salting': [],
    '8-1-rainbow-table-attack': ["Precomputed chain: password \u2192 hash \u2192 reduce \u2192 password\u2082 \u2192 hash\u2082 \u2192 ...", "Lookup: given hash h, check if h appears in any chain", "Time-memory tradeoff: less space than full table, more time than direct lookup"],
    '8-2-salt-defeats-rainbow-tables': ["Without salt: H(password) \u2014 same password always produces same hash", "With salt:    H(salt || password) \u2014 different salt per user", "Rainbow tables are password-specific, not (salt+password)-specific", "Each unique salt requires a separate table \u2192 infeasible"],
    '8-3-modern-password-hashing': [],
    '9-decision-tree': ["Hash-related challenge \u2014 what's the scenario?", "\u251c\u2500 Have H(secret || message), need to extend?", "\u2502  \u251c\u2500 Hash is MD5/SHA1/SHA256/SHA512?", "\u2502  \u2502  \u2514\u2500 Yes \u2192 Length extension attack", "\u2502  \u2502     \u2514\u2500 Need: MAC value, original message, secret length", "\u2502  \u2502        \u2514\u2500 Tool: HashPump or hash_extender", "\u2502  \u2514\u2500 Hash is SHA3/HMAC/BLAKE2?", "\u2502     \u2514\u2500 Length extension doesn't work", "\u2502        \u2514\u2500 Look for other vulnerabilities", "\u251c\u2500 Need two inputs with same hash?", "\u2502  \u251c\u2500 MD5?", "\u2502  \u2502  \u251c\u2500 Same prefix \u2192 fastcoll (seconds)", "\u2502  \u2502  \u251c\u2500 Different prefixes \u2192 hashclash (hours)", "\u2502  \u2502  \u2514\u2500 CTF PHP loose comparison \u2192 0e magic hashes", "\u2502  \u251c\u2500 SHA-1?", "\u2502  \u2502  \u2514\u2500 SHAttered (expensive, use precomputed if possible)", "\u2502  \u2514\u2500 SHA-256+?", "\u2502     \u2514\u2500 No practical collision attack", "\u2502        \u2514\u2500 Look for logic flaws instead", "\u251c\u2500 Need to forge HMAC?", "\u2502  \u251c\u2500 Timing side channel available?", "\u2502  \u2502  \u2514\u2500 Byte-by-byte timing attack", "\u2502  \u251c\u2500 Key is short/weak?", "\u2502  \u2502  \u2514\u2500 Brute force key with hashcat", "\u2502  \u2514\u2500 No weakness?", "\u2502     \u2514\u2500 HMAC is secure \u2014 look elsewhere", "\u251c\u2500 Hash is truncated (short output)?", "\u2502  \u2514\u2500 Birthday attack \u2014 collision in 2^(bits/2)", "\u251c\u2500 Proof of work?", "\u2502  \u2514\u2500 Brute force with parallel computation", "\u2502     \u251c\u2500 Python multiprocessing for < 28 bits", "\u2502     \u251c\u2500 hashcat/GPU for > 28 bits", "\u2502     \u2514\u2500 Optimize: pre-increment string, avoid re-encoding", "\u2514\u2500 Password hash cracking?", "\u251c\u2500 No salt \u2192 rainbow tables (pre-computed)", "\u251c\u2500 Known salt \u2192 hashcat / John the Ripper", "\u2514\u2500 Memory-hard (Argon2/scrypt) \u2192 limited by memory, slow brute force"],
    '10-tools': [],
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